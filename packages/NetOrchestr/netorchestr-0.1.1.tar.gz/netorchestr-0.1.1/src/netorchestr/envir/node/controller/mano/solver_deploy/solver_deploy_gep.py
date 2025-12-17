#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
solver_deploy_gep.py
=======================

.. module:: solver_deploy_gep
  :platform: Windows
  :synopsis: 基于贪心最早处理 (GEP) 策略的 SFC 编排求解器模块，适配 SDN/NFV 赋能的空天地一体化网络，支持 IoV 服务动态部署

.. moduleauthor:: WangXi

简介
----

该模块实现了文章中提出的贪心最早处理（Greedy Earliest Processing, GEP）算法，作为 TS-MAPSCH 和 TS-PSCH 算法的初始解生成器。
核心逻辑遵循“最早处理就绪的 VNF 优先部署”原则，同时考虑：
1. VNF 部署的时间约束（就绪时间）
2. 节点资源容量限制（CPU/内存）
3. 链路带宽约束
4. VNF 依赖关系（按 SFC 顺序部署）
5. 物理节点负载均衡

算法步骤：
1. 初始化：解析 SFC 请求，获取 VNF 类型、资源需求、就绪时间、依赖关系
2. 构建候选节点集：筛选满足 VNF 资源需求且与前序节点连通的物理节点
3. 贪心选择：对每个就绪的 VNF，选择“最早完成部署”的节点（综合考虑节点剩余资源、链路延迟）
4. 部署执行：更新节点资源占用，记录部署路径
5. 迭代：直至所有 VNF 部署完成或因资源不足部署失败

参考
----

```
@ARTICLE{9351537,
  author={Li, Junling and Shi, Weisen and Wu, Huaqing and Zhang, Shan and Shen, Xuemin},
  journal={IEEE Internet of Things Journal}, 
  title={Cost-Aware Dynamic SFC Mapping and Scheduling in SDN/NFV-Enabled Space–Air–Ground-Integrated Networks for Internet of Vehicles}, 
  year={2022},
  volume={9},
  number={8},
  pages={5824-5838},
  keywords={Dynamic scheduling;Heuristic algorithms;Vehicle dynamics;Resource management;Quality of service;Delays;Satellites;Internet of Vehicles (IoV);network function virtualization (NFV);resource allocation;software-defined networking (SDN);space–air–ground-integrated networks (SAGINs);virtual network function (VNF) mapping;VNF scheduling},
  doi={10.1109/JIOT.2021.3058250}
}
```

版本
----

- 版本 1.0 (2025/11/11): 初始版本，实现 GEP 算法核心逻辑，支持基本约束检查
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


class SolverDeployGEP(SolverDeployBase):
    def __init__(self, name: str):
        super().__init__(name)
        self.temp_nfvi_group_resouce: Dict[int, Dict[str, Union[int, u.Quantity]]] = {}
        self.vnf_ready_time: List[float] = []  # 每个 VNF 的就绪时间
        self.vnf_deploy_time: List[float] = []  # 每个 VNF 的部署完成时间
        self.vnf_dependencies: List[List[int]] = []  # VNF 依赖关系（前序 VNF 索引）

    def _init_vnf_metadata(self, vnffgManager: "VnffgManager") -> None:
        """初始化 VNF 元数据（就绪时间、部署时间、依赖关系）"""
        sfc_vnfs = vnffgManager.sfc_req.sfc_vnfs_type
        num_vnfs = len(sfc_vnfs)
        
        # 初始化就绪时间（默认按 SFC 顺序，第一个 VNF 就绪时间为 0）
        self.vnf_ready_time = [0.0] * num_vnfs
        for i in range(1, num_vnfs):
            # 后续 VNF 就绪时间 = 前序 VNF 部署完成时间（简化依赖，实际可根据文章调整）
            self.vnf_ready_time[i] = self.vnf_deploy_time[i-1] if i > 0 else 0.0
        
        # 初始化部署时间（默认 0，部署时计算）
        self.vnf_deploy_time = [0.0] * num_vnfs
        
        # 初始化依赖关系（SFC 顺序依赖，每个 VNF 依赖前一个 VNF）
        self.vnf_dependencies = [[i-1] for i in range(num_vnfs)]
        self.vnf_dependencies[0] = []  # 第一个 VNF 无依赖

    def _get_candidate_nodes(self, vnffgManager: "VnffgManager", vnf_idx: int) -> List[NfvInstance]:
        """获取 VNF 的候选部署节点：满足资源需求 + 与前序节点连通"""
        sfc_req = vnffgManager.sfc_req
        vnf_type = sfc_req.sfc_vnfs_type[vnf_idx]
        vnf_resource = vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit
        
        # 1. 筛选满足资源需求的节点
        candidate_nodes = []
        for nfvi in vnffgManager.vnfVim.nfvi_group.values():
            remaining_res = self.temp_nfvi_group_resouce[nfvi.id]
            # 检查 CPU、内存资源是否充足
            if (remaining_res['cpu'] >= vnf_resource['cpu'] and
                remaining_res['ram'] >= vnf_resource['ram'] and
                remaining_res['rom'] >= vnf_resource['rom']):
                candidate_nodes.append(nfvi)
        
        # 2. 筛选与前序节点连通的节点（第一个 VNF 无此约束）
        if vnf_idx > 0:
            prev_nfvi_id = self.solution_deploy.map_node[vnffgManager.sfc_req.sfc_vnfs_dep[vnf_idx][0]]
            prev_nfvi = vnffgManager.vnfVim.nfvi_group[prev_nfvi_id]
            connected_nodes = []
            for nfvi in candidate_nodes:
                try:
                    # 检查是否存在路径（使用 Dijkstra 算法验证连通性）
                    nx.dijkstra_path(self.adjacent_topo, prev_nfvi.id, nfvi.id)
                    connected_nodes.append(nfvi)
                except nx.NetworkXNoPath:
                    continue
            candidate_nodes = connected_nodes
        
        # 3. 特殊约束：起始/终止 VNF 需部署在 UE 可接入节点
        if vnf_idx == 0:
            can_access = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_start)
            candidate_nodes = [n for n in candidate_nodes if n in can_access]
        elif vnf_idx == len(sfc_req.sfc_vnfs_type) - 1:
            can_access = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_end)
            candidate_nodes = [n for n in candidate_nodes if n in can_access]
        
        return candidate_nodes

    def _select_best_node(self, vnffgManager: "VnffgManager", vnf_idx: int, candidate_nodes: List[NfvInstance]) -> NfvInstance:
        """选择最优部署节点：最早完成部署（综合资源、链路延迟）"""
        best_node = None
        earliest_finish_time = float('inf')
        vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[vnf_idx]
        vnf_resource = vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit
        
        for nfvi in candidate_nodes:
            # 计算部署时间：资源占用时间 + 链路传输时间（简化模型）
            # 1. 资源占用时间 = 资源需求 / 节点剩余资源（模拟部署效率）
            cpu_ratio = vnf_resource['cpu'] / self.temp_nfvi_group_resouce[nfvi.id]['cpu']
            ram_ratio = vnf_resource['ram'] / self.temp_nfvi_group_resouce[nfvi.id]['ram']
            resource_time = max(cpu_ratio, ram_ratio) * 10  # 放大系数，单位：秒
            
            # 2. 链路传输时间（仅非第一个 VNF）
            link_time = 0.0
            if vnf_idx > 0:
                prev_nfvi_id = self.solution_deploy.map_node[vnffgManager.sfc_req.sfc_vnfs_dep[vnf_idx][0]]
                try:
                    path = nx.dijkstra_path(self.adjacent_topo, prev_nfvi_id, nfvi.id)
                    # 链路时间 = 路径长度 * 单位延迟（假设单位延迟为 1 秒/跳）
                    link_time = len(path) - 1
                except nx.NetworkXNoPath:
                    link_time = float('inf')
            
            # 3. 总完成时间 = 就绪时间 + 资源时间 + 链路时间
            finish_time = self.vnf_ready_time[vnf_idx] + resource_time + link_time
            
            # 4. 选择最早完成的节点（负载均衡：资源占用率越低越优先）
            if (finish_time < earliest_finish_time) or \
               (finish_time == earliest_finish_time and 
                self.temp_nfvi_group_resouce[nfvi.id]['cpu'] > self.temp_nfvi_group_resouce[best_node.id]['cpu']):
                earliest_finish_time = finish_time
                best_node = nfvi
        
        return best_node

    def solve_embedding(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """GEP 算法核心：部署 SFC 请求"""
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "arrive"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        
        # 初始化
        self._init_vnf_metadata(vnffgManager)
        self.adjacent_topo = vnffgManager.vnfVim.get_graph(with_weight="Latency")
        self.solution_deploy.current_topo = self.adjacent_topo
        self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos
        self.solution_deploy.share_node = [None] * len(self.current_vnfs_index_list)
        
        # 深拷贝资源，用于临时计算
        self.temp_nfvi_group_resouce = {
            nvfi.id: copy.deepcopy(nvfi.node_handle.get_remaining_resource()) 
            for nvfi in vnffgManager.vnfVim.nfvi_group.values()
        }
        
        # 按就绪时间顺序部署 VNF
        deployed_vnfs = set()
        while len(deployed_vnfs) < len(self.current_vnfs_index_list):
            # 找到所有已就绪的 VNF（依赖已满足 + 未部署）
            ready_vnfs = []
            for vnf_idx in self.current_vnfs_index_list:
                if vnf_idx in deployed_vnfs:
                    continue
                # 检查依赖是否全部部署完成
                dependencies_met = all(dep in deployed_vnfs for dep in self.vnf_dependencies[vnf_idx])
                if dependencies_met:
                    ready_vnfs.append(vnf_idx)
            
            if not ready_vnfs:
                # 无就绪 VNF 且未部署完成，部署失败
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_RESOURCE_INSUFFICIENT
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            # 选择就绪时间最早的 VNF 进行部署
            vnf_idx = min(ready_vnfs, key=lambda x: self.vnf_ready_time[x])
            
            # 获取候选节点
            candidate_nodes = self._get_candidate_nodes(vnffgManager, vnf_idx)
            if not candidate_nodes:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_CANDIDATE_NODE
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            # 选择最优节点
            best_node = self._select_best_node(vnffgManager, vnf_idx, candidate_nodes)
            if not best_node:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_BEST_NODE
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            # 执行部署：更新资源、记录部署信息
            vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[vnf_idx]
            vnf_resource = vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit
            self.temp_nfvi_group_resouce[best_node.id]['cpu'] -= vnf_resource['cpu']
            self.temp_nfvi_group_resouce[best_node.id]['ram'] -= vnf_resource['ram']
            self.temp_nfvi_group_resouce[best_node.id]['rom'] -= vnf_resource['rom']
            
            self.solution_deploy.map_node[vnf_idx] = best_node.id
            
            # 计算部署完成时间（用于后续 VNF 就绪时间计算）
            if vnf_idx > 0:
                prev_nfvi_id = self.solution_deploy.map_node[self.vnf_dependencies[vnf_idx][0]]
                try:
                    path = nx.dijkstra_path(self.adjacent_topo, prev_nfvi_id, best_node.id)
                    link_time = len(path) - 1
                except nx.NetworkXNoPath:
                    link_time = 0.0
            else:
                link_time = 0.0
            
            self.vnf_deploy_time[vnf_idx] = self.vnf_ready_time[vnf_idx] + link_time + 1  # +1 为部署耗时基数
            deployed_vnfs.add(vnf_idx)
        
        # 计算链路路径
        v_links = [(v_node, v_node+1) for v_node in self.current_vnfs_index_list[:-1]]
        for v_link in v_links:
            try:
                map_path = nx.dijkstra_path(self.adjacent_topo, self.solution_deploy.map_node[v_link[0]], self.solution_deploy.map_node[v_link[1]])
                self.solution_deploy.map_link[v_link] = [(map_path[i], map_path[i+1]) for i in range(len(map_path)-1)]
            except nx.NetworkXNoPath:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
                self.solution_deploy.current_result = False
                return self.solution_deploy
        
        # 验证部署结果
        self.solution_deploy.current_description = self.check_solution(vnffgManager)
        self.solution_deploy.current_result = (self.solution_deploy.current_description == SOLUTION_DEPLOY_TYPE.SET_SUCCESS)
        
        return self.solution_deploy

    def solve_migration(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """GEP 算法迁移逻辑（简化版：按部署逻辑重新选择节点）"""
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "migrate"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        
        # 初始化（与部署逻辑类似）
        self._init_vnf_metadata(vnffgManager)
        self.adjacent_topo = vnffgManager.vnfVim.get_graph(with_weight="Latency")
        self.solution_deploy.current_topo = self.adjacent_topo
        self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos
        self.solution_deploy.share_node = [None] * len(self.current_vnfs_index_list)
        
        # 深拷贝资源
        self.temp_nfvi_group_resouce = {
            nvfi.id: copy.deepcopy(nvfi.node_handle.get_remaining_resource()) 
            for nvfi in vnffgManager.vnfVim.nfvi_group.values()
        }
        
        # 按就绪时间重新部署（迁移逻辑：不考虑历史部署，直接选择最优节点）
        deployed_vnfs = set()
        while len(deployed_vnfs) < len(self.current_vnfs_index_list):
            ready_vnfs = []
            for vnf_idx in self.current_vnfs_index_list:
                if vnf_idx in deployed_vnfs:
                    continue
                dependencies_met = all(dep in deployed_vnfs for dep in self.vnf_dependencies[vnf_idx])
                if dependencies_met:
                    ready_vnfs.append(vnf_idx)
            
            if not ready_vnfs:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_RESOURCE_INSUFFICIENT
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            vnf_idx = min(ready_vnfs, key=lambda x: self.vnf_ready_time[x])
            candidate_nodes = self._get_candidate_nodes(vnffgManager, vnf_idx)
            
            if not candidate_nodes:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_CANDIDATE_NODE
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            best_node = self._select_best_node(vnffgManager, vnf_idx, candidate_nodes)
            if not best_node:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_BEST_NODE
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            # 更新资源和部署信息
            vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[vnf_idx]
            vnf_resource = vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit
            self.temp_nfvi_group_resouce[best_node.id]['cpu'] -= vnf_resource['cpu']
            self.temp_nfvi_group_resouce[best_node.id]['ram'] -= vnf_resource['ram']
            self.temp_nfvi_group_resouce[best_node.id]['rom'] -= vnf_resource['rom']
            
            self.solution_deploy.map_node[vnf_idx] = best_node.id
            self.vnf_deploy_time[vnf_idx] = self.vnf_ready_time[vnf_idx] + 1  # 简化迁移耗时
            deployed_vnfs.add(vnf_idx)
        
        # 计算迁移链路路径
        v_links = [(v_node, v_node+1) for v_node in self.current_vnfs_index_list[:-1]]
        for v_link in v_links:
            try:
                map_path = nx.dijkstra_path(self.adjacent_topo, self.solution_deploy.map_node[v_link[0]], self.solution_deploy.map_node[v_link[1]])
                self.solution_deploy.map_link[v_link] = [(map_path[i], map_path[i+1]) for i in range(len(map_path)-1)]
            except nx.NetworkXNoPath:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_PATH
                self.solution_deploy.current_result = False
                return self.solution_deploy
        
        # 验证迁移结果
        self.solution_deploy.current_description = self.check_solution(vnffgManager)
        self.solution_deploy.current_result = (self.solution_deploy.current_description == SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS)
        
        self.calculate_cost_and_revenue(vnffgManager)
        
        return self.solution_deploy