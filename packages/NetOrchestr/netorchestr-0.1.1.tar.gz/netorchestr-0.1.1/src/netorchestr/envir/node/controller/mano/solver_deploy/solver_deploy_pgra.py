#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
solver_deploy_pgra.py
======================

.. module:: solver_deploy_pgra
  :platform: Windows
  :synopsis: 基于势博弈的卫星边缘计算VNF部署求解器模块, 实现分布式资源分配与纳什均衡优化

.. moduleauthor:: WangXi

简介
----

该模块复现了IEEE TNSM 2022论文中提出的PGRA (Potential Game-based Resource Allocation) 算法, 
针对卫星边缘计算场景下的虚拟网络功能 (VNF) 部署问题, 通过势博弈建模与Viterbi算法结合, 实现分布式资源优化. 
核心目标是最小化部署成本 (能耗、带宽、时延) 并最大化服务用户请求数量, 具备以下特性: 

- 势博弈建模: 将VNF部署问题转化为精确势博弈, 用户请求作为博弈参与者, 网络总收益为势函数; 
- 分布式决策: 无需集中式控制, 各参与者通过竞争资源迭代优化策略, 最终收敛至纳什均衡; 
- Viterbi路径优化: 针对每个用户请求的服务功能链 (SFC) , 通过Viterbi算法搜索最优部署路径; 
- 多目标成本优化: 联合考虑卫星节点能耗、星间链路带宽占用及服务端到端时延; 
- 动态拓扑适配: 适配低轨卫星网络拓扑时变特性, 支持时隙化资源更新与重分配. 

参考
----

```
@ARTICLE{9674029,
  author={Gao, Xiangqiang and Liu, Rongke and Kaushik, Aryan},
  journal={IEEE Transactions on Network and Service Management}, 
  title={Virtual Network Function Placement in Satellite Edge Computing With a Potential Game Approach}, 
  year={2022},
  volume={19},
  number={2},
  pages={1243-1259},
  keywords={Satellites;Edge computing;Resource management;Costs;Low earth orbit satellites;Games;Delays;Network function virtualization (NFV);satellite edge computing;virtual network function (VNF);resource allocation;potential game},
  doi={10.1109/TNSM.2022.3141165}
}
```

版本
----

- 版本 1.0 (2025/11/11): 初始版本, 复现论文核心算法, 包含势博弈建模、Viterbi部署优化、分布式迭代收敛逻辑

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

class SolverDeployPGRA(SolverDeployBase):
    def __init__(self, name: str):
        super().__init__(name)
        # 算法核心参数 (论文推荐配置) 
        self.max_iterations = 50  # 最大迭代次数K_max
        self.shortest_path_num = 8  # 候选最短路径数d
        self.viterbi_beam_width = 4  # Viterbi搜索树宽度B
        
        # 临时变量
        self.current_sfc_strategy: Dict[int, int] = {}  # 存储当前VNF到NFVI的映射

    def calculate_deployment_cost(self, vnffgManager: "VnffgManager", vnf_index: int, nfvi_id: int) -> float:
        """
        基于新模型计算单个VNF部署的综合成本
        整合资源成本与潜在迁移成本
        """
        # 1. 计算当前VNF的资源成本因子
        vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[vnf_index]
        nfvi_type = vnffgManager.vnfVim.nfvi_group[nfvi_id].node_type
        cost_factor = vnffgManager.vnfManager.vnfTemplates[vnf_type].cost_with_loc[nfvi_type]
        
        # 2. 基础资源成本计算
        vnf_resource = vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit
        cpu_cost = vnf_resource['cpu'] * cost_factor
        ram_cost = vnf_resource['ram'].to(u.GB).value * cost_factor
        
        # 非共享节点需计算ROM成本
        if self.solution_deploy.share_node[vnf_index] is None:
            rom_cost = vnf_resource['rom'].to(u.GB).value * cost_factor
        else:
            rom_cost = 1  # 避免乘法因子为0
        
        node_cost = cpu_cost * ram_cost * rom_cost
        
        # 3. 链路成本计算（与前序VNF的连接）
        if vnf_index > 0:
            prev_nfvi_id = self.current_sfc_strategy[vnf_index - 1]
            try:
                path = nx.dijkstra_path(self.adjacent_topo, prev_nfvi_id, nfvi_id)
                band_need = (vnffgManager.sfc_req.sfc_trans_model["payload_size"].to(u.Mbit) / 
                            vnffgManager.sfc_req.sfc_trans_model["interval"].to(u.s)).value
                link_cost = len(path) * band_need
            except nx.NetworkXNoPath:
                link_cost = float('inf')  # 无路径时成本无穷大
        else:
            link_cost = 1  # 第一个VNF无链路成本
        
        # 4. 综合成本（节点成本 × 链路成本）
        total_cost = node_cost * link_cost
        return total_cost

    def calculate_user_payoff(self, vnffgManager: "VnffgManager", vnf_mapping: List[int]) -> float:
        """
        基于新模型计算用户收益
        整合服务满意度、可靠性与资源需求
        """
        self.current_sfc_strategy = {i: vnf_mapping[i] for i in range(len(vnf_mapping))}
        
        # 1. 计算总资源成本（用于归一化）
        total_resource_cost = 0.0
        for i in range(len(vnf_mapping)):
            total_resource_cost += self.calculate_deployment_cost(vnffgManager, i, vnf_mapping[i])
        
        if total_resource_cost == 0:
            return 0.0  # 避免除零错误
        
        # 2. 服务满意度（基于时延）
        try:
            # 计算当前部署的实际时延
            total_latency = 0.0
            for i in range(1, len(vnf_mapping)):
                path = nx.dijkstra_path(self.adjacent_topo, vnf_mapping[i-1], vnf_mapping[i])
                total_latency += sum(self.adjacent_topo[path[j]][path[j+1]]['weight'] 
                                for j in range(len(path)-1))
            
            ue_access_start = vnffgManager.ue_access_start
            nfvi_access_start = vnffgManager.vnfVim.nfvi_group[vnf_mapping[0]]
            
            _, _, latency_ue_access_start = vnffgManager.vnfVim.net.radio_medium.is_in_communication_range_with_RadioPhySimpleSDR(ue_access_start.node_handle.radioPhy,
                                                                                                                                    nfvi_access_start.node_handle.duAau.radioPhy)
            total_latency += latency_ue_access_start.to(u.ms).value
                
            ue_access_end = vnffgManager.ue_access_end
            nfvi_access_end = vnffgManager.vnfVim.nfvi_group[vnf_mapping[-1]]
            
            _, _, latency_ue_access_end = vnffgManager.vnfVim.net.radio_medium.is_in_communication_range_with_RadioPhySimpleSDR(ue_access_end.node_handle.radioPhy,
                                                                                                                                nfvi_access_end.node_handle.duAau.radioPhy)
            
            total_latency += latency_ue_access_end.to(u.ms).value
            
            sfc_satisfaction = 1 - (total_latency / vnffgManager.sfc_req.sfc_qos["latency"].to(u.ms).value)
            sfc_satisfaction = max(0.0, min(sfc_satisfaction, 1.0))  # 限制在[0,1]区间
        except nx.NetworkXNoPath:
            sfc_satisfaction = 0.0  # 无路径时满意度为0
        
        # 3. 服务可靠性
        packet_over_rate = vnffgManager.sfc_req.sfc_qos["overrate"]
        sfc_reliability = np.exp(-packet_over_rate / vnffgManager.sfc_req.sfc_qos["overrate"])
        
        # 4. 用户流量需求
        traffic = (vnffgManager.sfc_req.sfc_trans_model["payload_size"].to(u.Mbit) / 
                vnffgManager.sfc_req.sfc_trans_model["interval"].to(u.s)).value
        traffic *= (len(vnf_mapping) - 1)  # 链路数量
        
        # 5. 收益计算：(满意度 × 可靠性 × 流量) / 资源成本
        # 加入资源成本倒数作为优化目标（成本越低收益越高）
        payoff = (sfc_satisfaction * sfc_reliability * traffic) / total_resource_cost
        return max(payoff, 0.0)  # 确保非负收益

    def viterbi_vnf_placement(self, vnffgManager: "VnffgManager", path: List[int]) -> List[int]:
        """Viterbi算法求解单路径上的最优VNF部署"""
        sfc_length = len(vnffgManager.sfc_req.sfc_vnfs_type)
        # 拓扑排序获取VNF部署顺序 (SFC顺序) 
        vnf_order = list(range(sfc_length))
        
        # 初始化动态规划表: [阶段][卫星ID] = (累计收益, 前序卫星ID)
        dp = [{} for _ in range(sfc_length)]
        beam_width = self.viterbi_beam_width
        
        # 阶段0: 第一个VNF部署 (起始节点) 
        start_nfvi_ids = [nfvi.id for nfvi in vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_start) 
                         if nfvi.id in path]
        for nfvi_id in start_nfvi_ids:
            temp_mapping = [nfvi_id] + [0]*(sfc_length-1)
            payoff = self.calculate_user_payoff(vnffgManager, temp_mapping)
            dp[0][nfvi_id] = (payoff, None)
        
        # 剪枝: 保留收益最高的B个状态
        dp[0] = dict(sorted(dp[0].items(), key=lambda x: x[1][0], reverse=True)[:beam_width])
        
        # 多阶段迭代
        for stage in range(1, sfc_length):
            for prev_nfvi_id, (prev_payoff, _) in dp[stage-1].items():
                # 获取当前阶段可用卫星 (路径中后续节点, 避免重复路由) 
                prev_idx = path.index(prev_nfvi_id)
                available_nfvi_ids = path[prev_idx:]
                
                for curr_nfvi_id in available_nfvi_ids:
                    # 检查资源是否充足
                    vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[stage]
                    vnf_resource = vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit
                    remaining_res = self.temp_nfvi_group_resouce[curr_nfvi_id]
                    
                    if (remaining_res['cpu'] >= vnf_resource['cpu'] and
                        remaining_res['ram'] >= vnf_resource['ram'] and
                        remaining_res['rom'] >= vnf_resource['rom']):
                        # 构建临时部署映射
                        temp_mapping = [0]*sfc_length
                        temp_mapping[stage] = curr_nfvi_id
                        temp_mapping[stage-1] = prev_nfvi_id
                        
                        self.temp_nfvi_group_resouce[curr_nfvi_id] = {
                            'cpu': remaining_res['cpu'] - vnf_resource['cpu'],
                            'ram': remaining_res['ram'] - vnf_resource['ram'],
                            'rom': remaining_res['rom'] - vnf_resource['rom']
                        }
                        
                        # 计算当前阶段收益
                        curr_payoff = self.calculate_user_payoff(vnffgManager, temp_mapping)
                        total_payoff = prev_payoff + curr_payoff
                        
                        # 更新DP表
                        if curr_nfvi_id not in dp[stage] or total_payoff > dp[stage][curr_nfvi_id][0]:
                            dp[stage][curr_nfvi_id] = (total_payoff, prev_nfvi_id)
            
            # 剪枝: 保留收益最高的B个状态
            dp[stage] = dict(sorted(dp[stage].items(), key=lambda x: x[1][0], reverse=True)[:beam_width])
        
        # 回溯获取最优部署路径
        if not dp[-1]:
            return []  # 无可行部署
        best_nfvi_id = max(dp[-1].keys(), key=lambda x: dp[-1][x][0])
        best_mapping = [0]*sfc_length
        best_mapping[-1] = best_nfvi_id
        
        for stage in range(sfc_length-2, -1, -1):
            best_nfvi_id = dp[stage+1][best_nfvi_id][1]
            best_mapping[stage] = best_nfvi_id
        
        return best_mapping

    def get_candidate_paths(self, vnffgManager: "VnffgManager") -> List[List[int]]:
        """
        候选路径生成算法
        增加路径多样性, 避免VNF过度集中部署在单一节点
        """
        start_node = vnffgManager.vnfVim.get_closest_nfvi_node(vnffgManager.ue_access_start).id
        end_node = vnffgManager.vnfVim.get_closest_nfvi_node(vnffgManager.ue_access_end).id
        
        # 如果源目节点相同，强制生成包含其他节点的路径
        if start_node == end_node:
            return self._generate_diverse_paths(start_node, end_node, vnffgManager)
        
        try:
            from itertools import islice
            # 1. 先获取基础最短路径集（基于时延）
            shortest_paths = list(islice(
                nx.shortest_simple_paths(self.adjacent_topo, start_node, end_node, weight="Latency"),
                self.shortest_path_num // 2  # 取一半配额给最短路径
            ))
            
            # 2. 补充多样化路径（基于节点多样性）
            diverse_paths = self._generate_diverse_paths(start_node, end_node, vnffgManager)
            
            # 3. 合并去重并保持路径数量
            all_paths = shortest_paths + diverse_paths
            unique_paths = []
            seen = set()
            for path in all_paths:
                path_tuple = tuple(path)
                if path_tuple not in seen:
                    seen.add(path_tuple)
                    unique_paths.append(path)
                    if len(unique_paths) >= self.shortest_path_num:
                        break
            
            return unique_paths
        
        except (nx.NetworkXNoPath, StopIteration):
            return []
    
    def _generate_diverse_paths(self, start: int, end: int, vnffgManager: "VnffgManager") -> List[List[int]]:
        """辅助方法：生成多样化路径，优先包含不同中间节点"""
        diverse_paths = []
        topo = self.adjacent_topo
        all_nodes = list(topo.nodes)
        # 排除源目节点的其他候选节点
        candidate_middles = [n for n in all_nodes if n != start and n != end]
        
        # 按节点资源余量排序（优先选择资源充足的节点作为中间节点）
        candidate_middles.sort(key=lambda n: (
            vnffgManager.vnfVim.nfvi_group[n].node_handle.get_remaining_resource()['cpu'],
            vnffgManager.vnfVim.nfvi_group[n].node_handle.get_remaining_resource()['ram']
        ), reverse=True)
        
        # 尝试生成经过不同中间节点的路径
        for middle in candidate_middles:
            try:
                # 生成"起点->中间节点->终点"的两段式路径
                path1 = nx.shortest_path(topo, start, middle, weight="Latency")
                path2 = nx.shortest_path(topo, middle, end, weight="Latency")
                full_path = path1 + path2[1:]  # 合并去重中间节点
                diverse_paths.append(full_path)
                
                # 达到所需数量则停止
                if len(diverse_paths) >= self.shortest_path_num // 2:
                    break
            except nx.NetworkXNoPath:
                continue
        
        return diverse_paths

    def solve_embedding(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """PGRA算法主流程 分布式VNF部署"""
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "arrive"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        self.current_nfvi_index_list = list(self.nfvOrchestrator.vnfVim.nfvi_group.keys())
        
        # region 准备算法所需数据 ---------------------------------------------
        sfc_length = len(self.current_vnfs_index_list)
        self.solution_deploy.current_time = vnffgManager.scheduler.now
        self.solution_deploy.resource['cpu'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu'] 
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['ram'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['ram'] 
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['rom'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['rom']
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        
        self.adjacent_topo = vnffgManager.vnfVim.get_graph(with_weight="Latency")
        self.solution_deploy.current_topo = self.adjacent_topo
        self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos
        self.solution_deploy.share_node = [None] * sfc_length

        # region 算法做出部署决策 ---------------------------------------------
        # 获取候选路径集
        candidate_paths = self.get_candidate_paths(vnffgManager)
        if not candidate_paths:
            self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
            self.solution_deploy.current_result = False
            return self.solution_deploy
        
        # 初始化当前策略和收益
        current_strategy = [random.choice(self.current_nfvi_index_list) for _ in range(sfc_length)]
        current_strategy[0] = vnffgManager.vnfVim.get_closest_nfvi_node(vnffgManager.ue_access_start).id
        current_strategy[-1] = vnffgManager.vnfVim.get_closest_nfvi_node(vnffgManager.ue_access_end).id
        current_payoff = self.calculate_user_payoff(vnffgManager, current_strategy)
        
        # 迭代优化 (势博弈收敛过程) 
        for iter_idx in range(self.max_iterations):
            best_new_strategy = None
            best_new_payoff = current_payoff
            
            # 遍历所有候选路径寻找最优策略
            for path in candidate_paths:
                self.temp_nfvi_group_resouce:dict[int,dict[str,Union[int,u.Quantity]]] = \
                    {nvfi.id : copy.deepcopy(nvfi.node_handle.get_remaining_resource()) 
                    for nvfi in vnffgManager.vnfVim.nfvi_group.values()}
                
                # Viterbi算法获取该路径上的最优部署
                path_strategy = self.viterbi_vnf_placement(vnffgManager, path)
                if not path_strategy:
                    continue
                
                # 计算该策略的收益
                path_payoff = self.calculate_user_payoff(vnffgManager, path_strategy)
                
                # 更新全局最优策略
                if path_payoff > best_new_payoff:
                    best_new_payoff = path_payoff
                    best_new_strategy = path_strategy
            
            # 收敛判断: 收益提升小于阈值
            if best_new_payoff - current_payoff < 1e-6:
                break
            
            # 更新策略和资源状态
            current_strategy = best_new_strategy
            current_payoff = best_new_payoff
        
        # 构建部署结果
        self.solution_deploy.map_node = {i: current_strategy[i] for i in range(sfc_length)}
        
        v_links = [(i, i+1) for i in range(sfc_length-1)]
        for v_link in v_links:
            try:
                map_path = nx.dijkstra_path(self.adjacent_topo, 
                                          current_strategy[v_link[0]], 
                                          current_strategy[v_link[1]])
                if len(map_path) == 1:
                    self.solution_deploy.map_link[v_link] = [(map_path[0], map_path[0])]
                else:
                    self.solution_deploy.map_link[v_link] = [(map_path[i], map_path[i+1]) for i in range(len(map_path)-1)]
            except nx.NetworkXNoPath:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
                self.solution_deploy.current_result = False
                return self.solution_deploy
        
        # region 检查算法决策结果 ---------------------------------------------
        
        self.solution_deploy.current_description = self.check_solution(vnffgManager)
        self.solution_deploy.current_result = (self.solution_deploy.current_description == SOLUTION_DEPLOY_TYPE.SET_SUCCESS)
        
        return self.solution_deploy

    def solve_migration(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """迁移场景下的PGRA算法适配"""
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "migrate"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        self.current_nfvi_index_list = list(self.nfvOrchestrator.vnfVim.nfvi_group.keys())
        
        # region 准备算法所需数据 ---------------------------------------------
        sfc_length = len(self.current_vnfs_index_list)
        self.solution_deploy.current_time = vnffgManager.scheduler.now
        self.solution_deploy.resource['cpu'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu'] 
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['ram'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['ram'] 
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['rom'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['rom']
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        
        self.adjacent_topo = vnffgManager.vnfVim.get_graph(with_weight="Latency")
        
        self.solution_deploy.current_topo = self.adjacent_topo
        self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos
        
        self.solution_deploy.share_node = [None] * sfc_length
        
        # region 算法做出部署决策 ---------------------------------------------
        # 获取候选路径集
        candidate_paths = self.get_candidate_paths(vnffgManager)
        if not candidate_paths:
            self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_PATH
            self.solution_deploy.current_result = False
            self.calculate_cost_and_revenue(vnffgManager)
            return self.solution_deploy
        
        # 初始化当前策略和收益
        current_strategy = [random.choice(self.current_nfvi_index_list) for _ in range(sfc_length)]
        current_strategy[0] = vnffgManager.vnfVim.get_closest_nfvi_node(vnffgManager.ue_access_start).id
        current_strategy[-1] = vnffgManager.vnfVim.get_closest_nfvi_node(vnffgManager.ue_access_end).id
        current_payoff = self.calculate_user_payoff(vnffgManager, current_strategy)
        
        for iter_idx in range(self.max_iterations):
            best_new_strategy = None
            best_new_payoff = current_payoff
            
            for path in candidate_paths:
                self.temp_nfvi_group_resouce:dict[int,dict[str,Union[int,u.Quantity]]] = \
                    {nvfi.id : copy.deepcopy(nvfi.node_handle.get_remaining_resource()) 
                    for nvfi in vnffgManager.vnfVim.nfvi_group.values()}
                    
                path_strategy = self.viterbi_vnf_placement(vnffgManager, path)
                if not path_strategy:
                    continue
                
                path_payoff = self.calculate_user_payoff(vnffgManager, path_strategy)
                if path_payoff > best_new_payoff:
                    best_new_payoff = path_payoff
                    best_new_strategy = path_strategy
            
            if best_new_payoff - current_payoff < 1e-6:
                break
            
            current_strategy = best_new_strategy
            current_payoff = best_new_payoff
            
            # 更新资源状态
            for i, nfvi_id in enumerate(current_strategy):
                vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[i]
                vnf_resource = vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit
                self.temp_nfvi_group_resouce[nfvi_id]['cpu'] -= vnf_resource['cpu']
                self.temp_nfvi_group_resouce[nfvi_id]['ram'] -= vnf_resource['ram']
                self.temp_nfvi_group_resouce[nfvi_id]['rom'] -= vnf_resource['rom']
        
        # 构建部署结果
        self.solution_deploy.map_node = {i: current_strategy[i] for i in range(sfc_length)}
        
        v_links = [(i, i+1) for i in range(sfc_length-1)]
        for v_link in v_links:
            try:
                map_path = nx.dijkstra_path(self.adjacent_topo, 
                                          current_strategy[v_link[0]], 
                                          current_strategy[v_link[1]])
                if len(map_path) == 1:
                    self.solution_deploy.map_link[v_link] = [(map_path[0], map_path[0])]
                else:
                    self.solution_deploy.map_link[v_link] = [(map_path[i], map_path[i+1]) for i in range(len(map_path)-1)]
            except nx.NetworkXNoPath:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_PATH
                self.solution_deploy.current_result = False
                return self.solution_deploy
        
        # 检查迁移结果
        self.solution_deploy.current_description = self.check_solution(vnffgManager)
        self.solution_deploy.current_result = (self.solution_deploy.current_description == SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS)
        
        self.calculate_cost_and_revenue(vnffgManager)
        
        return self.solution_deploy
    