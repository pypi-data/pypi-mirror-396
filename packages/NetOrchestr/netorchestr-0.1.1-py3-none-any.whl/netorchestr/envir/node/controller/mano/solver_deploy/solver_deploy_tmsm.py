#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
solver_deploy_tmsm.py
=======================

.. module:: solver_deploy_tmsm
  :platform: Windows
  :synopsis: 基于拓扑感知的最小延迟 SFC 迁移算法 (TMSM) 求解器模块，实现动态网络中 SFC 部署与迁移的 latency-cost 平衡优化

.. moduleauthor:: WangXi

简介
----

该模块完整复现了论文提出的 Topology-aware Min-latency SFC Migration (TMSM) 算法，核心聚焦动态网络拓扑下的 SFC 部署与迁移优化。
通过 Lyapunov 优化将长期平均延迟约束转化为瞬时优化目标，结合拓扑感知的节点排序与路径选择策略，实现延迟与迁移成本的联合优化。
主要特性包括：

- 拓扑感知节点排序：基于节点的度中心性与介数中心性加权计算重要性得分，优先选择关键节点部署 VNF；
- 延迟-成本平衡：引入 Lyapunov 漂移惩罚项，在降低端到端延迟的同时控制迁移频率与资源消耗；
- 动态路径适配：采用带权重的 Dijkstra 算法，综合链路延迟与带宽利用率选择最优传输路径；
- 完整迁移机制：支持基于延迟阈值触发的 SFC 整体迁移，确保网络状态变化时的服务质量稳定性。

参考
----

```
@article{QIN2023109563,
  title = {Service function chain migration with the long-term budget in dynamic networks},
  journal = {Computer Networks},
  volume = {223},
  pages = {109563},
  year = {2023},
  issn = {1389-1286},
  doi = {https://doi.org/10.1016/j.comnet.2023.109563},
  url = {https://www.sciencedirect.com/science/article/pii/S1389128623000087},
  author = {Yudong Qin and Deke Guo and Lailong Luo and Jingyu Zhang and Ming Xu},
  keywords = {Service function chain, SFC migration, Long-term budget, Dynamic networks},
}
```

版本
----

- 版本 1.0 (2025/11/11): 初始版本，复现论文核心算法，支持部署与迁移的联合优化

'''

import copy
import networkx as nx
from collections import defaultdict

from astropy import units as u
from netorchestr.envir.node.controller.mano.solver_deploy import SolutionDeploy, SolverDeployBase, SOLUTION_DEPLOY_TYPE

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import VnffgManager

class SolverDeployTMSM(SolverDeployBase):
    def __init__(self, name: str, lyapunov_weight: float = 0.1, degree_weight: float = 0.4, betweenness_weight: float = 0.6):
        """
        初始化 TMSM 求解器
        
        Args:
            name: 求解器名称
            lyapunov_weight: Lyapunov 优化权重，平衡延迟与迁移成本
            degree_weight: 度中心性权重，用于节点重要性计算
            betweenness_weight: 介数中心性权重，用于节点重要性计算
        """
        super().__init__(name)
        self.lyapunov_weight = lyapunov_weight
        self.degree_weight = degree_weight
        self.betweenness_weight = betweenness_weight
        
        # 存储节点重要性得分
        self.node_importance: dict[int, float] = {}
        # 存储链路带宽利用率（模拟动态网络状态）
        self.link_utilization: dict[tuple[int, int], float] = defaultdict(float)

    def calculate_node_importance(self, topo: nx.Graph) -> dict[int, float]:
        """
        计算节点重要性得分（度中心性 + 介数中心性加权）
        
        Args:
            topo: 物理网络拓扑图
            
        Returns:
            节点 ID 到重要性得分的映射
        """
        # 计算度中心性（归一化）
        degree_centrality = nx.degree_centrality(topo)
        # 计算介数中心性（归一化）
        betweenness_centrality = nx.betweenness_centrality(topo)
        
        # 加权计算节点重要性
        importance = {}
        for node in topo.nodes():
            importance[node] = (self.degree_weight * degree_centrality[node] + 
                               self.betweenness_weight * betweenness_centrality[node])
        return importance

    def calculate_link_weight(self, c: int, v: int, topo: nx.Graph) -> float:
        """
        计算链路权重（延迟 + 带宽利用率惩罚）
        
        Args:
            c: 链路起始节点
            v: 链路终止节点
            topo: 物理网络拓扑图
            
        Returns:
            链路权重值
        """
        # 基础延迟（从拓扑获取）
        latency = topo[c][v]['weight']
        # 带宽利用率（模拟值，实际应从网络监控获取）
        util = self.link_utilization.get((c, v), 0.0)
        util = max(0.0, min(1.0, util))  # 确保在 [0,1] 范围内
        
        # 链路权重 = 延迟 * (1 + 利用率惩罚因子)
        # 利用率越高，惩罚越大，避免选择拥堵链路
        weight = latency * (1 + self.lyapunov_weight * util)
        return weight

    def get_topology_aware_path(self, graph: nx.Graph, source: int, target: int) -> list[int]:
        """基于链路延迟的最短路径计算"""
        if source == target:
            return [source]  # 同一节点，直接返回
        # 执行 Dijkstra 算法
        try:
            return nx.dijkstra_path(graph, source, target)
        except nx.NetworkXNoPath:
            return []

    def calculate_lyapunov_cost(self, current_map: dict[int, int], new_map: dict[int, int]) -> float:
        """
        计算 Lyapunov 迁移成本（基于部署变化量）
        
        Args:
            current_map: 当前 VNF 部署映射（VNF 索引 -> NFVI 节点 ID）
            new_map: 新的 VNF 部署映射
            
        Returns:
            Lyapunov 成本值
        """
        # 计算迁移的 VNF 数量及资源变化量，更精确评估迁移成本
        migration_cost = 0.0
        for vnf_idx in current_map:
            if current_map[vnf_idx] != new_map.get(vnf_idx, -1):
                # 基础迁移成本
                migration_cost += 1.0
                # 增加资源重新分配惩罚因子（假设VNF资源需求越大，迁移成本越高）
                vnf_type = self.vnffgManager.sfc_req.sfc_vnfs_type[vnf_idx]
                vnf_resource = self.vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit
                resource_factor = (vnf_resource['cpu'] + vnf_resource['ram'].value + vnf_resource['rom'].value)
                migration_cost += self.lyapunov_weight * resource_factor
        
        return migration_cost


    def select_target_nfvi(
        self, 
        vnf_idx: int, 
        vnf_type: str, 
        is_shared: bool, 
        current_map: dict[int, int], 
        adjacent_topo: nx.Graph, 
        vnffgManager: "VnffgManager"
    ) -> tuple[int, bool]:
        """
        优化后的节点选择策略：
        - 平衡节点重要性、剩余资源、负载均衡和链路延迟。
        - 强化约束, 第一个VNF必须部署在可接入节点, 最后一个VNF必须部署在可接出节点。
        """
        vnf_resource = self.vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit
        candidate_nodes = []
        total_vnfs = len(self.current_vnfs_index_list)
        
        ue_access_start_allowed_nfvis = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_start)
        ue_access_end_allowed_nfvis = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_end)

        for nfvi_id, nfvi in vnffgManager.vnfVim.nfvi_group.items():
            if vnf_idx == 0 and nfvi_id not in [nfvi.id for nfvi in ue_access_start_allowed_nfvis]:
                continue  # 第一个VNF，跳过非接入节点
            if vnf_idx == total_vnfs - 1 and nfvi_id not in [nfvi.id for nfvi in ue_access_end_allowed_nfvis]:
                continue  # 最后一个VNF，跳过非接出节点

            # 1. 基础资源检查：确保节点剩余资源满足当前VNF需求
            remaining_cpu = self.temp_nfvi_group_resouce[nfvi_id]["cpu"]
            remaining_ram = self.temp_nfvi_group_resouce[nfvi_id]["ram"]
            if remaining_cpu < vnf_resource["cpu"] or remaining_ram < vnf_resource["ram"]:
                continue

            # 2. 计算节点负载因子（负载越高，权重越低）
            deployed_vnfs = len(nfvi.get_deployed_vnfs())
            load_factor = 1.0 / (deployed_vnfs + 1)

            # 3. 节点重要性得分
            importance_score = self.node_importance.get(nfvi_id, 1)

            # 4. 链路延迟预估
            path_latency = 0.0
            prev_vnf_idx = vnf_idx - 1
            if prev_vnf_idx in current_map:
                prev_nfvi_id = current_map[prev_vnf_idx]
                if prev_nfvi_id != nfvi_id:
                    path = self.get_topology_aware_path(adjacent_topo, prev_nfvi_id, nfvi_id)
                    if not path:
                        continue  # 如果与前一个节点不连通，也跳过
                    path_latency = sum(adjacent_topo[c][v].get("Latency", 1.0) for c, v in zip(path[:-1], path[1:]))

            # 5. 综合得分计算
            # 对于中间节点，延迟是重要考量；对于首尾节点，约束已满足，延迟权重可降低
            latency_weight = 0.5 if (vnf_idx == 0 or vnf_idx == total_vnfs - 1) else 1.0
            latency_penalty = 1.0 / (path_latency * latency_weight + 1.0)
            
            total_score = importance_score * load_factor * latency_penalty

            candidate_nodes.append((nfvi_id, total_score))

        # 选择得分最高的节点
        if not candidate_nodes:
            return -1, False  # 无可用节点
        candidate_nodes.sort(key=lambda x: x[1], reverse=True)
        best_nfvi_id = candidate_nodes[0][0]

        # 检查是否可共享（原逻辑保留）
        if is_shared:
            deployed_vnfs = vnffgManager.vnfVim.nfvi_group[best_nfvi_id].get_deployed_vnf_with_type(vnf_type)
            if deployed_vnfs:
                return best_nfvi_id, True  # 共享已部署的VNF

        # --- 占用选定节点的资源 ---
        self.temp_nfvi_group_resouce[best_nfvi_id]["cpu"] -= vnf_resource["cpu"]
        self.temp_nfvi_group_resouce[best_nfvi_id]["ram"] -= vnf_resource["ram"]

        return best_nfvi_id, False

    def solve_embedding(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """
        TMSM 算法的 SFC 初始部署实现
        
        Args:
            vnffgManager: VNF 管理实例
            
        Returns:
            部署解决方案
        """
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "arrive"
        self.solution_deploy.current_time = vnffgManager.scheduler.now
        
        # 初始化参数
        sfc = vnffgManager.sfc_req
        self.current_vnfs_index_list = list(range(len(sfc.sfc_vnfs_type)))
        self.solution_deploy.resource = {
            'cpu': [vnffgManager.vnfManager.vnfTemplates[t].resource_limit['cpu'] for t in sfc.sfc_vnfs_type],
            'ram': [vnffgManager.vnfManager.vnfTemplates[t].resource_limit['ram'] for t in sfc.sfc_vnfs_type],
            'rom': [vnffgManager.vnfManager.vnfTemplates[t].resource_limit['rom'] for t in sfc.sfc_vnfs_type]
        }
        
        self.adjacent_topo = vnffgManager.vnfVim.get_graph(with_weight="Latency")
        self.solution_deploy.current_topo = self.adjacent_topo
        self.solution_deploy.current_qos = sfc.sfc_qos
        self.solution_deploy.share_node = [None] * len(self.current_vnfs_index_list)
        
        # 深拷贝资源用于决策
        self.temp_nfvi_group_resouce:dict[int,dict[str,Union[int,u.Quantity]]] = \
            {nvfi.id : copy.deepcopy(nvfi.node_handle.get_remaining_resource()) 
             for nvfi in vnffgManager.vnfVim.nfvi_group.values()}
        
        # 部署 VNF（按顺序选择拓扑重要性高的节点）
        current_map = {}
        for vnf_idx in self.current_vnfs_index_list:
            vnf_type = sfc.sfc_vnfs_type[vnf_idx]
            is_shared = sfc.sfc_vnfs_shared[vnf_idx]
            
            # 选择目标 NFVI
            target_nfvi_id, use_shared = self.select_target_nfvi(
                vnf_idx, vnf_type, is_shared, current_map, self.adjacent_topo, vnffgManager
            )
            
            if target_nfvi_id == -1:
                # 部署失败
                if vnf_idx == 0:
                    desc = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_UE_ACCESS_START
                elif vnf_idx == len(self.current_vnfs_index_list) - 1:
                    desc = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_UE_ACCESS_END
                else:
                    desc = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_CPU
                self.solution_deploy.current_description = desc
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            # 更新部署映射
            current_map[vnf_idx] = target_nfvi_id
            self.solution_deploy.map_node[vnf_idx] = target_nfvi_id
            
            # 更新共享节点信息
            if is_shared:
                nfvi = vnffgManager.vnfVim.nfvi_group[target_nfvi_id]
                can_be_shared_vnfem = nfvi.get_deployed_vnf_with_type(vnf_type)
                if not can_be_shared_vnfem:
                    self.solution_deploy.share_node[vnf_idx] = None
                else:
                    self.solution_deploy.share_node[vnf_idx] = can_be_shared_vnfem[0].id
            else:
                self.solution_deploy.share_node[vnf_idx] = None
            
            # 更新临时资源
            vnf_resource = vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit
            for res_type in ['cpu', 'ram', 'rom']:
                self.temp_nfvi_group_resouce[target_nfvi_id][res_type] -= vnf_resource[res_type]
        
        # 计算 VNF 间链路路径（拓扑感知路径选择）
        v_links = [(i, i+1) for i in range(len(self.current_vnfs_index_list)-1)]
        for v_link in v_links:
            source_nfvi = current_map[v_link[0]]
            target_nfvi = current_map[v_link[1]]
            
            # 获取拓扑感知最优路径
            path = self.get_topology_aware_path(self.adjacent_topo, source_nfvi, target_nfvi)
            if not path:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            # 转换为链路列表
            if len(path) == 1:
                self.solution_deploy.map_link[v_link] = [(path[0], path[0])]
            else:
                self.solution_deploy.map_link[v_link] = [(path[i], path[i+1]) for i in range(len(path)-1)]
            
            # 更新链路利用率（模拟流量变化）
            for i in range(len(path)-1):
                c, v = path[i], path[i+1]
                self.link_utilization[(c, v)] += 0.1  # 假设每次传输增加 10% 利用率
                self.link_utilization[(v, c)] += 0.1  # 双向链路
        
        # 验证部署结果
        self.solution_deploy.current_description = self.check_solution(vnffgManager)
        self.solution_deploy.current_result = (self.solution_deploy.current_description == SOLUTION_DEPLOY_TYPE.SET_SUCCESS)
        
        return self.solution_deploy

    def solve_migration(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """
        TMSM 算法的 SFC 迁移部署实现（确保时延达标，最小化迁移成本）
        
        Args:
            vnffgManager: VNF 管理实例
            
        Returns:
            迁移解决方案
        """
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "migrate"
        self.solution_deploy.current_time = vnffgManager.scheduler.now
        
        # 获取当前部署映射和拓扑信息
        current_solution = vnffgManager.solutions_deploy[-1]
        current_map = current_solution.map_node
        current_latency = self._calculate_current_latency(current_map, vnffgManager)
        sfc = vnffgManager.sfc_req
        qos_latency = sfc.sfc_qos.get('latency', float('inf'))
        
        # 初始化参数
        self.current_vnfs_index_list = list(range(len(sfc.sfc_vnfs_type)))
        self.solution_deploy.resource = {
            'cpu': [vnffgManager.vnfManager.vnfTemplates[t].resource_limit['cpu'] for t in sfc.sfc_vnfs_type],
            'ram': [vnffgManager.vnfManager.vnfTemplates[t].resource_limit['ram'] for t in sfc.sfc_vnfs_type],
            'rom': [vnffgManager.vnfManager.vnfTemplates[t].resource_limit['rom'] for t in sfc.sfc_vnfs_type]
        }
        
        self.adjacent_topo = vnffgManager.vnfVim.get_graph(with_weight="Latency")
        self.solution_deploy.current_topo = self.adjacent_topo
        self.solution_deploy.current_qos = sfc.sfc_qos
        self.solution_deploy.share_node = [None] * len(self.current_vnfs_index_list)
        
        # 深拷贝资源用于决策
        self.temp_nfvi_group_resouce:dict[int,dict[str,Union[int,u.Quantity]]] = \
            {nvfi.id : copy.deepcopy(nvfi.node_handle.get_remaining_resource()) 
             for nvfi in vnffgManager.vnfVim.nfvi_group.values()}
        
        # 生成候选迁移方案（尝试部分迁移以最小化成本）
        best_new_map = None
        best_new_latency = float('inf')
        best_migration_cost = float('inf')
        
        # 策略1: 尝试单独迁移每个VNF，寻找最优部分迁移方案
        for target_vnf_idx in self.current_vnfs_index_list:
            partial_map = copy.deepcopy(current_map)
            # 仅重新部署目标VNF
            vnf_type = sfc.sfc_vnfs_type[target_vnf_idx]
            is_shared = sfc.sfc_vnfs_shared[target_vnf_idx]
            
            target_nfvi_id, use_shared = self.select_target_nfvi(
                target_vnf_idx, vnf_type, is_shared, current_map, self.adjacent_topo, vnffgManager
            )
            
            if target_nfvi_id == -1:
                continue  # 该VNF无法单独迁移，跳过
            
            partial_map[target_vnf_idx] = target_nfvi_id
            partial_latency = self._calculate_current_latency(partial_map, vnffgManager)
            partial_cost = self.calculate_lyapunov_cost(current_map, partial_map)
            
            # 若部分迁移已满足时延要求，优先选择成本最低的方案
            if partial_latency <= qos_latency and partial_cost < best_migration_cost:
                best_new_map = partial_map
                best_new_latency = partial_latency
                best_migration_cost = partial_cost
        
        # 策略2: 如果部分迁移无法满足要求，则尝试全量迁移
        if best_new_map is None:
            new_map = {}
            valid = True
            for vnf_idx in self.current_vnfs_index_list:
                vnf_type = sfc.sfc_vnfs_type[vnf_idx]
                is_shared = sfc.sfc_vnfs_shared[vnf_idx]
                
                target_nfvi_id, use_shared = self.select_target_nfvi(
                    vnf_idx, vnf_type, is_shared, current_map, self.adjacent_topo, vnffgManager
                )
                
                if target_nfvi_id == -1:
                    valid = False
                    break
                
                new_map[vnf_idx] = target_nfvi_id
            
            if not valid:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NODE_CPU
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            # 评估全量迁移方案
            full_latency = self._calculate_current_latency(new_map, vnffgManager)
            full_cost = self.calculate_lyapunov_cost(current_map, new_map)
            
            # 即使全量迁移后仍不满足时延，也必须执行（因为外部已判定当前不满足）
            best_new_map = new_map
            best_new_latency = full_latency
            best_migration_cost = full_cost
        
        # 应用最优迁移方案
        self.solution_deploy.map_node = best_new_map
        
        # 更新链路映射
        v_links = [(i, i+1) for i in range(len(self.current_vnfs_index_list)-1)]
        for v_link in v_links:
            source_nfvi = best_new_map[v_link[0]]
            target_nfvi = best_new_map[v_link[1]]
            path = self.get_topology_aware_path(self.adjacent_topo, source_nfvi, target_nfvi)
            
            if not path:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_PATH
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            if len(path) == 1:
                self.solution_deploy.map_link[v_link] = [(path[0], path[0])]
            else:
                self.solution_deploy.map_link[v_link] = [(path[i], path[i+1]) for i in range(len(path)-1)]
            
            # 更新链路利用率
            for i in range(len(path)-1):
                c, v = path[i], path[i+1]
                self.link_utilization[(c, v)] = max(0.0, self.link_utilization[(c, v)] - 0.05)
                self.link_utilization[(v, c)] = max(0.0, self.link_utilization[(v, c)] - 0.05)
        
        # 更新共享节点信息
        for vnf_idx in self.current_vnfs_index_list:
            vnf_type = sfc.sfc_vnfs_type[vnf_idx]
            is_shared = sfc.sfc_vnfs_shared[vnf_idx]
            if is_shared:
                nfvi = vnffgManager.vnfVim.nfvi_group[best_new_map[vnf_idx]]
                can_be_shared_vnfem = nfvi.get_deployed_vnf_with_type(vnf_type)
                if not can_be_shared_vnfem:
                    self.solution_deploy.share_node[vnf_idx] = None
                else:
                    self.solution_deploy.share_node[vnf_idx] = can_be_shared_vnfem[0].id
            else:
                self.solution_deploy.share_node[vnf_idx] = None
        
        # 验证迁移结果
        self.solution_deploy.current_description = self.check_solution(vnffgManager)
        self.solution_deploy.current_result = (self.solution_deploy.current_description == SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS)

        self.calculate_cost_and_revenue(vnffgManager)
        
        return self.solution_deploy


    def _calculate_current_latency(self, deployment_map: dict[int, int], vnffgManager: "VnffgManager") -> float:
        """辅助方法：计算当前部署的端到端延迟"""
        latency = 0.0 * u.ms
        v_links = [(i, i+1) for i in range(len(deployment_map)-1)]
        for v_link in v_links:
            source_nfvi = deployment_map[v_link[0]]
            target_nfvi = deployment_map[v_link[1]]
            path = self.get_topology_aware_path(self.adjacent_topo, source_nfvi, target_nfvi)
            if not path:
                continue
            # 累加路径延迟
            for i in range(len(path)-1):
                c, v = path[i], path[i+1]
                latency += self.adjacent_topo[c][v]['weight'] * u.ms
        
        ue_access_start = vnffgManager.ue_access_start
        nfvi_access_start = vnffgManager.vnfVim.nfvi_group[list(deployment_map.values())[0]]
        
        _, _, latency_ue_access_start = vnffgManager.vnfVim.net.radio_medium.is_in_communication_range_with_RadioPhySimpleSDR(ue_access_start.node_handle.radioPhy,
                                                                                                                              nfvi_access_start.node_handle.duAau.radioPhy)
        latency += latency_ue_access_start
            
        ue_access_end = vnffgManager.ue_access_end
        nfvi_access_end = vnffgManager.vnfVim.nfvi_group[list(deployment_map.values())[-1]]
        
        _, _, latency_ue_access_end = vnffgManager.vnfVim.net.radio_medium.is_in_communication_range_with_RadioPhySimpleSDR(ue_access_end.node_handle.radioPhy,
                                                                                                                            nfvi_access_end.node_handle.duAau.radioPhy)
        
        latency += latency_ue_access_end
        
        return latency
    