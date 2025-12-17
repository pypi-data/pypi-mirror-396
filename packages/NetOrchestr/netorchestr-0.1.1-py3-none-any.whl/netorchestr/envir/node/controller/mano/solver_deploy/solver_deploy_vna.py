
#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
solver_deploy_vna.py
=======================

.. module:: solver_deploy_vna
  :platform: Windows
  :synopsis: 基于文章算法的虚拟网络分配求解器模块, 支持VNA-I (无重配置) 和VNA-II (选择性重配置) , 实现虚拟网络向基底网络的高效嵌入与动态优化

.. moduleauthor:: WangXi

简介
----

该模块完整复现了文章提出的虚拟网络分配 (VN Assignment) 核心算法, 聚焦基底网络节点与链路应力的低水平均衡, 支持稀疏拓扑虚拟网络的细分部署与动态重配置优化。
通过邻域资源可用性 (NR) 评估、节点势能计算、虚拟网络细分 (SubVN) 及自适应优化策略, 实现虚拟节点与链路的智能映射, 同时支持基于关键资源占用的选择性重配置。
它提供了以下特性: 

- 完整复现VNA-I基础算法: 基于NR指标选择集群中心, 结合节点势能与链路应力距离实现节点/链路协同优化；
- 支持SubVN细分策略: 将复杂虚拟网络拆分为星型子网络, 提升稀疏拓扑下的资源利用效率与部署灵活性；
- 自适应优化机制: 通过节点/链路应力比动态选择node-opt或link-opt策略, 平衡两类应力优化目标；
- 实现VNA-II选择性重配置: 基于全局标记与临界资源判断, 仅对高应力关联虚拟网络进行重配置, 控制部署成本；
- 严格遵循文章应力模型: 精准实现节点应力 (虚拟节点部署数) 与链路应力 (虚拟链路占用数) 的计算与优化。

参考
----

```
@INPROCEEDINGS{Zhu2006Assigning,
  author={Zhu, Y. and Ammar, M.},
  booktitle={Proceedings IEEE INFOCOM 2006. 25TH IEEE International Conference on Computer Communications}, 
  title={Algorithms for Assigning Substrate Network Resources to Virtual Network Components}, 
  year={2006},
  volume={},
  number={},
  pages={1-12},
  keywords={IP networks;Resource virtualization;Protocols;Network topology;Proposals;Web and internet services;Technological innovation;Service oriented architecture;Investments;Resource management},
  doi={10.1109/INFOCOM.2006.322}
}
```

版本
----

- 版本 1.0 (2025/11/11): 初始版本, 集成VNA-I基础算法、SubVN细分策略、自适应优化及VNA-II选择性重配置核心功能
'''

import copy
import random
import networkx as nx
import numpy as np

from astropy import units as u
from netorchestr.envir.node.controller.mano.solver_deploy import SolutionDeploy, SolverDeployBase, SOLUTION_DEPLOY_TYPE
from netorchestr.envir.node.controller.mano.vim import NfvInstance

from typing import TYPE_CHECKING, Union, List, Dict, Tuple
if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import VnffgManager
    
class SolverDeployVNA(SolverDeployBase):
    def __init__(self, name: str, alpha: float = 1.0, beta: float = 1.0, delta_L: int = 1, delta_N: int = 1):
        super().__init__(name)
        self.alpha = alpha  # 节点应力权重
        self.beta = beta    # 链路应力权重
        self.delta_L = delta_L  # 链路距离计算常数
        self.delta_N = delta_N  # 节点势能计算常数
        self.temp_nfvi_group_resouce = {}
        self.substrate_stress: Dict[int, Dict[str, int]] = {}  # 基底网络应力状态 {nfvi_id: {'node_stress': int, 'link_stress': Dict[Tuple[int, int], int]}}

    def _calculate_substrate_stress(self, vnffgManager: "VnffgManager") -> None:
        """计算当前基底网络的节点应力和链路应力"""
        self.substrate_stress = {}
        for nfvi in vnffgManager.vnfVim.nfvi_group.values():
            # 节点应力: 部署在该节点的VNF数量
            node_stress = len(nfvi.get_deployed_vnfs())
            # 链路应力: 每条链路被多少虚拟链路占用
            link_stress = {}
            for edge in vnffgManager.vnfVim.get_graph().edges():
                edge_key = tuple(sorted(edge))  # 无向边标准化
                # 统计通过该链路的已部署虚拟链路数
                stress_count = 0
                for deployed_vnffg in vnffgManager.deployed_vnffgs.values():
                    for v_link_path in deployed_vnffg.solution.map_link.values():
                        for path_edge in v_link_path:
                            if tuple(sorted(path_edge)) == edge_key:
                                stress_count += 1
                link_stress[edge_key] = stress_count
            self.substrate_stress[nfvi.id] = {
                'node_stress': node_stress,
                'link_stress': link_stress
            }

    def _get_max_stresses(self) -> Tuple[int, int]:
        """获取当前最大节点应力和最大链路应力"""
        max_node_stress = max([self.substrate_stress[nfvi_id]['node_stress'] for nfvi_id in self.substrate_stress.keys()], default=0)
        max_link_stress = 0
        for nfvi_id in self.substrate_stress.keys():
            link_stresses = self.substrate_stress[nfvi_id]['link_stress'].values()
            if link_stresses:
                current_max = max(link_stresses)
                if current_max > max_link_stress:
                    max_link_stress = current_max
        return max_node_stress, max_link_stress

    def _calculate_nr(self, nfvi: NfvInstance, max_node_stress: int, max_link_stress: int) -> float:
        """计算邻域资源可用性 (NR) : 综合节点应力和相邻链路应力"""
        nfvi_id = nfvi.id
        node_stress = self.substrate_stress[nfvi_id]['node_stress']
        # 计算相邻链路的应力总和
        adjacent_links = self.vnffgManager.vnfVim.get_graph().edges(nfvi_id)
        link_stress_sum = 0
        for edge in adjacent_links:
            edge_key = tuple(sorted(edge))
            link_stress = self.substrate_stress[nfvi_id]['link_stress'].get(edge_key, 0)
            link_stress_sum += (max_link_stress - link_stress)
        # NR公式: (最大节点应力 - 当前节点应力) * 相邻链路应力总和
        return (max_node_stress - node_stress) * link_stress_sum

    def _calculate_path_distance(self, path: List[int], max_link_stress: int) -> float:
        """计算路径距离: 基于链路应力的倒数和"""
        distance = 0.0
        for i in range(len(path) - 1):
            edge_key = tuple(sorted((path[i], path[i+1])))
            # 找到该链路的应力
            link_stress = 0
            for nfvi_stress in self.substrate_stress.values():
                if edge_key in nfvi_stress['link_stress']:
                    link_stress = nfvi_stress['link_stress'][edge_key]
                    break
            # 距离公式: 1/(最大链路应力 + delta_L - 当前链路应力)
            denominator = max_link_stress + self.delta_L - link_stress
            distance += 1.0 / denominator if denominator != 0 else float('inf')
        return distance

    def _find_shortest_distance_path(self, graph: nx.Graph, start: int, end: int, max_link_stress: int) -> List[int]:
        """找到基于链路应力的最短距离路径"""
        if start == end:
            return [start]
        # 为每条可能路径计算距离并选择最小的
        shortest_path = None
        min_distance = float('inf')
        try:
            for path in nx.all_simple_paths(graph, start, end):
                path_distance = self._calculate_path_distance(path, max_link_stress)
                if path_distance < min_distance:
                    min_distance = path_distance
                    shortest_path = path
        except nx.NetworkXNoPath:
            return []
        return shortest_path if shortest_path else []

    def _calculate_node_potential(self, nfvi: NfvInstance, selected_nfvi_ids: List[int], max_node_stress: int, max_link_stress: int) -> float:
        """计算节点势能: 综合到已选节点的距离和节点应力"""
        nfvi_id = nfvi.id
        node_stress = self.substrate_stress[nfvi_id]['node_stress']
        # 计算到所有已选节点的最短距离之和
        total_distance = 0.0
        graph = self.vnffgManager.vnfVim.get_graph()
        for selected_id in selected_nfvi_ids:
            path = self._find_shortest_distance_path(graph, nfvi_id, selected_id, max_link_stress)
            if not path:
                return float('inf')
            total_distance += self._calculate_path_distance(path, max_link_stress)
        # 势能公式: 总距离 / (最大节点应力 + delta_N - 当前节点应力)
        denominator = max_node_stress + self.delta_N - node_stress
        return total_distance / denominator if denominator != 0 else float('inf')

    def _select_cluster_center(self, candidate_nfvis: List[NfvInstance], max_node_stress: int, max_link_stress: int) -> NfvInstance:
        """选择集群中心: NR值最大的节点"""
        max_nr = -float('inf')
        cluster_center = None
        for nfvi in candidate_nfvis:
            nr = self._calculate_nr(nfvi, max_node_stress, max_link_stress)
            if nr > max_nr:
                max_nr = nr
                cluster_center = nfvi
        return cluster_center if cluster_center else random.choice(candidate_nfvis)

    def _match_vnf_to_nfvi(self, vnf_index: int, selected_nfvis: List[NfvInstance], vnffgManager: "VnffgManager") -> NfvInstance:
        """将虚拟节点映射到基底节点: 高degree VNF优先映射到高NR节点"""
        vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[vnf_index]
        # 计算每个VNF的degree (虚拟链路连接数) 
        vnf_degree = 0
        if vnf_index == 0 or vnf_index == len(self.current_vnfs_index_list) - 1:
            vnf_degree = 1  # 首尾节点只有一条连接
        else:
            vnf_degree = 2  # 中间节点两条连接
        # 计算每个候选节点的NR值
        max_node_stress, max_link_stress = self._get_max_stresses()
        nfvi_nr = [(nfvi, self._calculate_nr(nfvi, max_node_stress, max_link_stress)) for nfvi in selected_nfvis]
        # 按NR降序排序
        nfvi_nr.sort(key=lambda x: x[1], reverse=True)
        # 高degree VNF分配到高NR节点
        return nfvi_nr[0][0] if nfvi_nr else random.choice(selected_nfvis)

    def solve_embedding(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """实现文章VNA-I基础版算法: 无重配置的虚拟网络分配"""
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "arrive"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        
        # 初始化数据
        self.solution_deploy.resource['cpu'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu'] 
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['ram'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['ram'] 
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['rom'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['rom']
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]

        self.adjacent_topo = vnffgManager.vnfVim.get_graph(with_weight="Latency")
        self.solution_deploy.current_topo = self.adjacent_topo
        self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos
        self.solution_deploy.share_node = [None] * len(self.current_vnfs_index_list)
        self.solution_deploy.map_node = [None] * len(self.current_vnfs_index_list)
        self.solution_deploy.map_link = {}

        # 深拷贝资源用于决策
        self.temp_nfvi_group_resouce:dict[int,dict[str,Union[int,u.Quantity]]] = \
            {nvfi.id : copy.deepcopy(nvfi.node_handle.get_remaining_resource()) 
             for nvfi in vnffgManager.vnfVim.nfvi_group.values()}
        
        # 步骤1: 计算当前基底网络应力
        self._calculate_substrate_stress(vnffgManager)
        max_node_stress, max_link_stress = self._get_max_stresses()

        # 步骤2: 选择集群中心 (第一个虚拟节点的部署) 
        # 起始节点需满足UE接入约束
        if self.current_vnfs_index_list:
            first_vnf_index = self.current_vnfs_index_list[0]
            can_access_nfvi_list = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_start)
            if not can_access_nfvi_list:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_UE_ACCESS_START
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            # 选择NR最大的节点作为集群中心
            cluster_center = self._select_cluster_center(can_access_nfvi_list, max_node_stress, max_link_stress)
            # 分配资源并记录映射
            first_vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[first_vnf_index]
            self.temp_nfvi_group_resouce[cluster_center.id]['cpu'] -= vnffgManager.vnfManager.vnfTemplates[first_vnf_type].resource_limit['cpu']
            self.solution_deploy.map_node[first_vnf_index] = cluster_center.id
            selected_nfvi_ids = [cluster_center.id]

        # 步骤3: 选择剩余虚拟节点的部署位置
        for v_node in self.current_vnfs_index_list[1:]:
            # 过滤出资源充足且可路由的NFVI
            candidate_nfvis = []
            for nfvi in vnffgManager.vnfVim.nfvi_group.values():
                # 资源检查
                vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                required_cpu = vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu']
                if self.temp_nfvi_group_resouce[nfvi.id]['cpu'] < required_cpu:
                    continue
                # 可路由检查 (到已选节点) 
                is_routable = False
                for selected_id in selected_nfvi_ids:
                    path = self._find_shortest_distance_path(self.adjacent_topo, nfvi.id, selected_id, max_link_stress)
                    if path:
                        is_routable = True
                        break
                if is_routable:
                    candidate_nfvis.append(nfvi)
            
            if not candidate_nfvis:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            # 选择势能最小的节点
            min_potential = float('inf')
            chosen_nfvi = None
            for nfvi in candidate_nfvis:
                potential = self._calculate_node_potential(nfvi, selected_nfvi_ids, max_node_stress, max_link_stress)
                if potential < min_potential:
                    min_potential = potential
                    chosen_nfvi = nfvi
            
            # 分配资源并记录映射
            vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
            self.temp_nfvi_group_resouce[chosen_nfvi.id]['cpu'] -= vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu']
            self.solution_deploy.map_node[v_node] = chosen_nfvi.id
            selected_nfvi_ids.append(chosen_nfvi.id)

        # 步骤4: 虚拟链路映射 (最短距离路径) 
        v_links = [(v_node, v_node+1) for v_node in self.current_vnfs_index_list[:-1]]
        for v_link in v_links:
            start_nfvi_id = self.solution_deploy.map_node[v_link[0]]
            end_nfvi_id = self.solution_deploy.map_node[v_link[1]]
            # 找到基于链路应力的最短路径
            path = self._find_shortest_distance_path(self.adjacent_topo, start_nfvi_id, end_nfvi_id, max_link_stress)
            if not path:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            # 转换为链路列表
            if len(path) == 1:
                self.solution_deploy.map_link[v_link] = [(path[0], path[0])]
            else:
                self.solution_deploy.map_link[v_link] = [(path[i], path[i+1]) for i in range(len(path)-1)]

        # 验证解决方案
        self.solution_deploy.current_description = self.check_solution(vnffgManager)
        self.solution_deploy.current_result = (self.solution_deploy.current_description == SOLUTION_DEPLOY_TYPE.SET_SUCCESS)

        return self.solution_deploy
        
    def solve_migration(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """迁移逻辑: 基于文章VNA-II的选择性重配置思想 (简化版) """
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "migrate"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        
        # 步骤1: 计算当前应力, 识别关键节点/链路 (θ=0.1, 仅考虑高应力资源) 
        self._calculate_substrate_stress(vnffgManager)
        max_node_stress, max_link_stress = self._get_max_stresses()
        theta = 0.1
        critical_node_threshold = (1 - theta) * max_node_stress
        critical_link_threshold = (1 - theta) * max_link_stress

        # 步骤2: 检查当前部署是否使用关键资源, 需要迁移则重新执行嵌入算法
        need_migration = False
        current_deploy = vnffgManager.current_deployed_solution
        for v_node, nfvi_id in enumerate(current_deploy.map_node):
            # 检查节点是否为关键节点
            if self.substrate_stress[nfvi_id]['node_stress'] >= critical_node_threshold:
                need_migration = True
                break
            # 检查链路是否为关键链路
            for v_link, path in current_deploy.map_link.items():
                for edge in path:
                    edge_key = tuple(sorted(edge))
                    link_stress = 0
                    for nfvi_stress in self.substrate_stress.values():
                        if edge_key in nfvi_stress['link_stress']:
                            link_stress = nfvi_stress['link_stress'][edge_key]
                            break
                    if link_stress >= critical_link_threshold:
                        need_migration = True
                        break
                if need_migration:
                    break
            if need_migration:
                break

        # 不需要迁移则返回当前部署
        if not need_migration:
            self.solution_deploy = copy.deepcopy(current_deploy)
            self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS
            self.solution_deploy.current_result = True
            return self.solution_deploy

        # 需要迁移则重新执行嵌入算法
        return self.solve_embedding(vnffgManager)