#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
solver_deploy_dvine.py
=======================

.. module:: solver_deploy_dvine
  :platform: Windows
  :synopsis: 基于线性松弛贪心策略的动态虚拟网络嵌入 (D-ViNE) 模块，适用于非地面网络 (NTNs) 中服务功能链 (SFC) 部署与重映射

.. moduleauthor:: WangXi

简介
----

该模块复现了 2022 IEEE WCNC 论文提出的 D-ViNE 算法，针对非地面网络（卫星/空天地一体化网络）的动态
网络环境，实现服务功能链（SFC）的高效部署与重映射。算法核心特点如下：

- 采用线性松弛技术将整数规划问题转化为连续域优化，通过贪心策略快速求解近似最优解
- 引入动态权重调整机制，联合优化链路带宽、端到端时延和节点资源利用率
- 支持虚拟网络功能（VNF）共享部署，通过资源预留策略减少服务中断概率
- 设计分层映射策略：先完成VNF节点映射，再基于最短路径算法优化链路映射
- 具备重映射触发机制，当网络状态变化（如卫星切换、链路故障）时自动调整部署方案

参考
----

```
@INPROCEEDINGS{9771560,
  author={Maity, Ilora and Vu, Thang X. and Chatzinotas, Symeon and Minardi, Mario},
  booktitle={2022 IEEE Wireless Communications and Networking Conference (WCNC)}, 
  title={D-ViNE: Dynamic Virtual Network Embedding in Non-Terrestrial Networks}, 
  year={2022},
  volume={},
  number={},
  pages={166-171},
  keywords={Satellites;Costs;Network topology;Heuristic algorithms;Conferences;Benchmark testing;Dynamic scheduling;Software-Defined Networking (SDN);Network Function Virtualization (NFV);Virtual Network Embedding (VNE);VNF Mapping;Virtual Link;Satellite Networks},
  doi={10.1109/WCNC51071.2022.9771560}
}
```

版本
----

- 版本 1.0 (2025/11/11): 初始版本，复现论文核心算法，支持NTN场景下SFC部署与重映射

'''

import copy
import random
import networkx as nx
import numpy as np
from typing import TYPE_CHECKING, Union, List, Dict, Tuple
from astropy import units as u

# 导入框架核心模块
from netorchestr.envir.node.controller.mano.solver_deploy import SolutionDeploy, SolverDeployBase, SOLUTION_DEPLOY_TYPE
from netorchestr.envir.node.controller.mano.vim import NfvInstance

if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import VnffgManager


class SolverDeployDVine(SolverDeployBase):
    '''
    基于D-ViNE算法的SFC部署与重映射求解器
    复现2022 IEEE WCNC论文"Dynamic Virtual Network Embedding in Non-Terrestrial Networks"
    '''
    
    def __init__(self, name: str):
        super().__init__(name)
        # 算法参数配置（基于论文建议值）
        self.alpha = 0.4  # 带宽权重系数
        self.beta = 0.3   # 时延权重系数
        self.gamma = 0.3  # 资源利用率权重系数
        self.resource_threshold = 0.7  # 资源预留阈值（触发重映射）
        self.temp_nfvi_resources = {}  # 临时资源记录
        self.vnf_mapping_priority = []  # VNF映射优先级列表
    
    def _calculate_node_score(self, nfvi: NfvInstance, vnf_type: str) -> float:
        '''
        计算NFVI节点对目标VNF的映射得分（论文公式3）
        综合考虑资源剩余量、资源利用率和网络位置
        
        Args:
            nfvi: 待评估的NFVI节点
            vnf_type: VNF类型
            
        Returns:
            节点映射得分（越高越优先）
        '''
        # 获取VNF资源需求
        vnf_cpu = self.vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu']
        vnf_ram = self.vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['ram']
        
        # 获取NFVI剩余资源
        remaining_cpu = self.temp_nfvi_resources[nfvi.id]['cpu']
        remaining_ram = self.temp_nfvi_resources[nfvi.id]['ram']
        
        # 计算资源满足度（避免除零）
        cpu_satisfaction = remaining_cpu / vnf_cpu if vnf_cpu > 0 else 1.0
        ram_satisfaction = remaining_ram / vnf_ram if vnf_ram > 0 else 1.0
        
        # 计算资源利用率（论文公式4）
        total_cpu = nfvi.node_handle.get_total_resource()['cpu']
        total_ram = nfvi.node_handle.get_total_resource()['ram']
        cpu_util = (total_cpu - remaining_cpu) / total_cpu if total_cpu > 0 else 0.0
        ram_util = (total_ram - remaining_ram) / total_ram if total_ram > 0 else 0.0
        avg_util = (cpu_util + ram_util) / 2
        
        # 计算节点得分（论文公式3）
        resource_score = 0.5 * cpu_satisfaction + 0.5 * ram_satisfaction
        utilization_score = 1 - avg_util  # 利用率越低得分越高
        node_score = self.gamma * resource_score + (1 - self.gamma) * utilization_score
        
        return node_score
    
    def _calculate_link_score(self, path: List[int], bandwidth_demand: float) -> float:
        '''
        计算链路映射路径得分（论文公式5）
        综合考虑带宽剩余量、链路时延和路径长度
        
        Args:
            path: 候选路径（节点ID列表）
            bandwidth_demand: 带宽需求
            
        Returns:
            路径映射得分（越高越优先）
        '''
        if len(path) < 2:
            return 0.0
            
        total_bandwidth_score = 0.0
        total_latency = 0.0
        
        # 计算路径上各链路的得分
        for i in range(len(path) - 1):
            u_node = path[i]
            v_node = path[i + 1]
            
            # 获取链路剩余带宽和时延
            link_data = self.adjacent_topo.get_edge_data(u_node, v_node)
            remaining_bw = link_data.get('bandwidth', 0.0)
            latency = link_data.get('latency', 0.0)
            
            # 带宽得分（归一化）
            bw_score = remaining_bw / bandwidth_demand if bandwidth_demand > 0 else 1.0
            total_bandwidth_score += bw_score
            
            # 累计时延
            total_latency += latency
        
        # 计算平均带宽得分和路径长度惩罚
        avg_bw_score = total_bandwidth_score / (len(path) - 1)
        path_length_penalty = 1 / len(path)  # 路径越短惩罚越小
        
        # 计算链路得分（论文公式5）
        latency_score = 1 / (1 + total_latency)  # 时延越小得分越高
        link_score = (self.alpha * avg_bw_score + 
                     self.beta * latency_score) * path_length_penalty
        
        return link_score
    
    def _determine_vnf_priority(self) -> List[int]:
        '''
        确定VNF映射优先级（论文第IV-B节）
        基于VNF类型重要性、资源需求和位置约束
        
        Returns:
            VNF索引的优先级列表（0为最高优先级）
        '''
        priority_list = []
        
        for idx, vnf_type in enumerate(self.vnffgManager.sfc_req.sfc_vnfs_type):
            # 位置约束权重（起始和终止VNF优先级更高）
            if idx == 0 or idx == len(self.vnffgManager.sfc_req.sfc_vnfs_type) - 1:
                location_weight = 0.4
            else:
                location_weight = 0.1
            
            # 资源需求权重（资源需求越高优先级越高）
            cpu_demand = self.vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu']
            ram_demand = self.vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['ram']
            resource_weight = (cpu_demand + ram_demand) / (1e9 + 1e9)  # 归一化到[0,1]
            
            # 共享属性权重（可共享VNF优先级略低）
            if self.vnffgManager.sfc_req.sfc_vnfs_shared[idx]:
                share_weight = 0.1
            else:
                share_weight = 0.2
            
            # 计算总优先级得分
            priority_score = location_weight + resource_weight + share_weight
            priority_list.append((idx, priority_score))
        
        # 按得分降序排序，返回VNF索引
        priority_list.sort(key=lambda x: x[1], reverse=True)
        return [idx for idx, _ in priority_list]
    
    def _check_remapping_trigger(self) -> bool:
        '''
        检查是否需要触发重映射（论文第IV-C节）
        当节点资源利用率超过阈值或链路带宽不足时触发
        
        Returns:
            是否需要重映射
        '''
        # 检查节点资源利用率
        for nfvi in self.vnffgManager.vnfVim.nfvi_group.values():
            total_cpu = nfvi.node_handle.get_total_resource()['cpu']
            used_cpu = total_cpu - nfvi.node_handle.get_remaining_resource()['cpu']
            cpu_util = used_cpu / total_cpu if total_cpu > 0 else 0.0
            
            total_ram = nfvi.node_handle.get_total_resource()['ram']
            used_ram = total_ram - nfvi.node_handle.get_remaining_resource()['ram']
            ram_util = used_ram / total_ram if total_ram > 0 else 0.0
            
            if cpu_util > self.resource_threshold or ram_util > self.resource_threshold:
                return True
        
        # 检查链路带宽利用率
        for u, v, data in self.adjacent_topo.edges(data=True):
            total_bw = data.get('bandwidth_total', data.get('bandwidth', 0.0))
            used_bw = total_bw - data.get('bandwidth', 0.0)
            bw_util = used_bw / total_bw if total_bw > 0 else 0.0
            
            if bw_util > self.resource_threshold:
                return True
        
        return False
    
    def _perform_node_mapping(self) -> bool:
        '''
        执行VNF节点映射（论文第IV-B节）
        基于优先级和节点得分选择最优NFVI节点
        
        Returns:
            节点映射是否成功
        '''
        # 初始化临时资源记录
        self.temp_nfvi_resources = {
            nfvi.id: copy.deepcopy(nfvi.node_handle.get_remaining_resource())
            for nfvi in self.vnffgManager.vnfVim.nfvi_group.values()
        }
        
        # 确定VNF映射优先级
        self.vnf_mapping_priority = self._determine_vnf_priority()
        
        for vnf_idx in self.vnf_mapping_priority:
            vnf_type = self.vnffgManager.sfc_req.sfc_vnfs_type[vnf_idx]
            is_shared = self.vnffgManager.sfc_req.sfc_vnfs_shared[vnf_idx]
            
            # 筛选候选NFVI节点
            if vnf_idx == 0:
                # 起始VNF：必须部署在UE起始端点可接入的NFVI
                candidate_nfvis = self.vnffgManager.vnfVim.get_can_access_nfvi_node(
                    self.vnffgManager.ue_access_start
                )
            elif vnf_idx == len(self.vnffgManager.sfc_req.sfc_vnfs_type) - 1:
                # 终止VNF：必须部署在UE终止端点可接入的NFVI
                candidate_nfvis = self.vnffgManager.vnfVim.get_can_access_nfvi_node(
                    self.vnffgManager.ue_access_end
                )
            elif is_shared:
                # 可共享VNF：优先选择已部署同类型VNF的NFVI
                candidate_nfvis = self.vnffgManager.vnfVim.who_has_vnf_with_type(vnf_type)
                # 如果没有则选择所有可路由的NFVI
                if not candidate_nfvis:
                    start_nfvi = self.vnffgManager.vnfVim.nfvi_group[self.solution_deploy.map_node[0]]
                    candidate_nfvis = self.vnffgManager.vnfVim.who_can_route_to_nfvi(
                        start_nfvi, self.adjacent_topo
                    )
            else:
                # 不可共享VNF：选择所有可路由的NFVI
                start_nfvi = self.vnffgManager.vnfVim.nfvi_group[self.solution_deploy.map_node[0]]
                candidate_nfvis = self.vnffgManager.vnfVim.who_can_route_to_nfvi(
                    start_nfvi, self.adjacent_topo
                )
            
            # 过滤掉资源不足的NFVI
            valid_nfvis = []
            vnf_cpu = self.vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu']
            vnf_ram = self.vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['ram']
            
            for nfvi in candidate_nfvis:
                if (self.temp_nfvi_resources[nfvi.id]['cpu'] >= vnf_cpu and
                    self.temp_nfvi_resources[nfvi.id]['ram'] >= vnf_ram):
                    valid_nfvis.append(nfvi)
            
            if not valid_nfvis:
                # 没有可用的NFVI节点
                if vnf_idx == 0:
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_UE_ACCESS_START
                elif vnf_idx == len(self.vnffgManager.sfc_req.sfc_vnfs_type) - 1:
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_UE_ACCESS_END
                else:
                    self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_RESOURCE_INSUFFICIENT
                return False
            
            # 选择得分最高的NFVI节点
            best_nfvi = max(valid_nfvis, key=lambda n: self._calculate_node_score(n, vnf_type))
            
            # 更新资源和映射关系
            self.temp_nfvi_resources[best_nfvi.id]['cpu'] -= vnf_cpu
            self.temp_nfvi_resources[best_nfvi.id]['ram'] -= vnf_ram
            self.solution_deploy.map_node[vnf_idx] = best_nfvi.id
            
            # 处理共享VNF
            if is_shared:
                shared_vnfems = best_nfvi.get_deployed_vnf_with_type(vnf_type)
                self.solution_deploy.share_node[vnf_idx] = shared_vnfems[0].id if shared_vnfems else None
            else:
                self.solution_deploy.share_node[vnf_idx] = None
        
        return True
    
    def _perform_link_mapping(self) -> bool:
        '''
        执行VNF链路映射（论文第IV-B节）
        基于最短路径和链路得分选择最优路径
        
        Returns:
            链路映射是否成功
        '''
        vnf_count = len(self.vnffgManager.sfc_req.sfc_vnfs_type)
        
        for i in range(vnf_count - 1):
            # 获取源和目标NFVI节点
            src_nfvi_id = self.solution_deploy.map_node[i]
            dst_nfvi_id = self.solution_deploy.map_node[i + 1]
            
            # 获取链路带宽需求
            vnf_link = (i, i + 1)
            bandwidth_demand = self.vnffgManager.sfc_req.sfc_links_bandwidth.get(vnf_link, 0.0)
            
            # 查找所有可能的路径
            try:
                all_paths = list(nx.all_simple_paths(self.adjacent_topo, src_nfvi_id, dst_nfvi_id))
            except nx.NetworkXNoPath:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
                return False
            
            # 过滤掉带宽不足的路径
            valid_paths = []
            for path in all_paths:
                path_valid = True
                for j in range(len(path) - 1):
                    u = path[j]
                    v = path[j + 1]
                    remaining_bw = self.adjacent_topo.get_edge_data(u, v).get('bandwidth', 0.0)
                    if remaining_bw < bandwidth_demand:
                        path_valid = False
                        break
                if path_valid:
                    valid_paths.append(path)
            
            if not valid_paths:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_BANDWIDTH_INSUFFICIENT
                return False
            
            # 选择得分最高的路径
            best_path = max(valid_paths, key=lambda p: self._calculate_link_score(p, bandwidth_demand))
            
            # 更新链路映射和资源
            self.solution_deploy.map_link[(i, i + 1)] = [
                (best_path[j], best_path[j + 1]) for j in range(len(best_path) - 1)
            ]
            
            # 占用链路带宽资源
            for u, v in self.solution_deploy.map_link[(i, i + 1)]:
                self.adjacent_topo[u][v]['bandwidth'] -= bandwidth_demand
        
        return True
    
    def solve_embedding(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        '''
        初始部署SFC（论文第IV-B节）
        执行节点映射和链路映射，返回部署方案
        
        Args:
            vnffgManager: VNF转发图管理器
            
        Returns:
            部署方案
        '''
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "arrive"
        
        # 初始化映射关系
        vnf_count = len(vnffgManager.sfc_req.sfc_vnfs_type)
        self.solution_deploy.map_node = [None] * vnf_count
        self.solution_deploy.share_node = [None] * vnf_count
        self.solution_deploy.map_link = {}
        
        # 获取网络拓扑和QoS需求
        self.adjacent_topo = vnffgManager.vnfVim.get_graph(with_weight="Latency")
        self.solution_deploy.current_topo = copy.deepcopy(self.adjacent_topo)
        self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos
        
        # 记录资源需求
        self.solution_deploy.resource['cpu'] = [
            vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu']
            for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type
        ]
        self.solution_deploy.resource['ram'] = [
            vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['ram']
            for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type
        ]
        self.solution_deploy.resource['rom'] = [
            vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['rom']
            for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type
        ]
        
        # 执行节点映射
        if not self._perform_node_mapping():
            self.solution_deploy.current_result = False
            return self.solution_deploy
        
        # 执行链路映射
        if not self._perform_link_mapping():
            self.solution_deploy.current_result = False
            return self.solution_deploy
        
        # 验证部署方案
        self.solution_deploy.current_description = self.check_solution(vnffgManager)
        self.solution_deploy.current_result = (self.solution_deploy.current_description == SOLUTION_DEPLOY_TYPE.SET_SUCCESS)
        
        return self.solution_deploy
    
    def solve_migration(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        '''
        重映射SFC（论文第IV-C节）
        当网络状态变化时，调整VNF部署以维持服务质量
        
        Args:
            vnffgManager: VNF转发图管理器
            
        Returns:
            重映射方案
        '''
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "migrate"
        
        # 检查是否需要触发重映射
        if not self._check_remapping_trigger():
            self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_TRIGGER
            self.solution_deploy.current_result = False
            return self.solution_deploy
        
        # 初始化映射关系（继承原有映射作为基础）
        vnf_count = len(vnffgManager.sfc_req.sfc_vnfs_type)
        original_solution = vnffgManager.current_solution
        self.solution_deploy.map_node = copy.deepcopy(original_solution.map_node)
        self.solution_deploy.share_node = copy.deepcopy(original_solution.share_node)
        self.solution_deploy.map_link = copy.deepcopy(original_solution.map_link)
        
        # 获取更新后的网络拓扑
        self.adjacent_topo = vnffgManager.vnfVim.get_graph(with_weight="Latency")
        self.solution_deploy.current_topo = copy.deepcopy(self.adjacent_topo)
        self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos
        
        # 记录资源需求（与初始部署相同）
        self.solution_deploy.resource = copy.deepcopy(original_solution.resource)
        
        # 执行节点重映射（优先调整受影响的VNF）
        if not self._perform_node_mapping():
            self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_RESOURCE_INSUFFICIENT
            self.solution_deploy.current_result = False
            return self.solution_deploy
        
        # 执行链路重映射
        if not self._perform_link_mapping():
            self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_BANDWIDTH_INSUFFICIENT
            self.solution_deploy.current_result = False
            return self.solution_deploy
        
        # 验证重映射方案
        self.solution_deploy.current_description = self.check_solution(vnffgManager)
        self.solution_deploy.current_result = (self.solution_deploy.current_description == SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS)
        
        # 计算迁移成本和收益
        self.calculate_cost_and_revenue(vnffgManager)
        
        return self.solution_deploy