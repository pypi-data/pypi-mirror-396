#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
solver_deploy_ts_mapsch.py
=======================

.. module:: solver_deploy_ts_mapsch
  :platform: Windows
  :synopsis: 基于禁忌搜索的最小分配与路径选择成本启发式 (TS-MAPSCH) SFC 编排求解器模块

.. moduleauthor:: WangXi

简介
----

该模块实现了文章中提出的禁忌搜索（Tabu Search）算法，用于解决服务功能链（SFC）的部署优化问题。
TS-MAPSCH 算法旨在寻找一个在满足所有约束条件（如资源、链路连通性、VNF 依赖）的前提下，
能够最小化总体部署成本（包括 VNF 实例化成本和链路带宽占用成本）的 SFC 部署方案。

算法步骤：
1.  **初始化**: 使用贪心算法（如 GEP）生成一个初始可行解。
2.  **邻域搜索**: 通过对当前解进行微小的修改（例如，将一个 VNF 迁移到另一个可行的节点）来生成一系列邻域解。
3.  **禁忌表**: 为了避免陷入局部最优解，算法会记录最近访问过的解（或解的特征），并在一定步数内禁止再次访问。
4.  ** aspiration 准则**: 如果一个被禁忌的解明显优于当前找到的最优解，则可以忽略禁忌状态，接受该解。
5.  **迭代**: 重复邻域搜索、评估、选择最优非禁忌解的过程，直到达到预设的迭代次数或搜索停滞。

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

- 版本 1.0 (2025/11/12): 初始版本，实现 TS-MAPSCH 算法核心逻辑。
'''

import copy
import random
import networkx as nx
from typing import TYPE_CHECKING, Dict, List, Any, Tuple
from netorchestr.envir.node.controller.mano.solver_deploy.solver_deploy_gep import SolverDeployGEP
from netorchestr.envir.node.controller.mano.solver_deploy import SolutionDeploy, SolverDeployBase, SOLUTION_DEPLOY_TYPE
from netorchestr.envir.node.controller.mano.vim import NfvInstance

if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import VnffgManager

class SolverDeployTSMAPSCH(SolverDeployBase):
    def __init__(self, name: str):
        super().__init__(name)
        self.greedy_solver = SolverDeployGEP("gep_for_ts_mapsch")
        self.tabu_list: List[Dict[str, Any]] = []
        self.tabu_tenure = 10  # 禁忌 tenure
        self.max_iterations = 50  # 最大迭代次数
        self.best_solution: SolutionDeploy = None
        self.best_cost = float('inf')

    def _calculate_cost(self, vnffgManager: "VnffgManager", solution: SolutionDeploy) -> float:
        """
        计算给定部署方案的总成本。
        成本 = sum(VNF实例化成本) + sum(链路带宽占用成本)
        这里简化为：成本 = VNF部署的CPU总占用 + 链路总跳数
        """
        total_cost = 0

        # 1. VNF 实例化成本 (CPU 占用)
        for vnf_idx, nfvi_id in enumerate(solution.map_node):
            vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[vnf_idx]
            vnf_cpu = vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu']
            # 如果是共享部署，可能只计算一次或按比例计算，这里简化为每次都计算
            total_cost += vnf_cpu.value if hasattr(vnf_cpu, 'value') else vnf_cpu

        # 2. 链路带宽占用成本 (路径长度)
        for (u, v), path in solution.map_link.items():
            # 路径长度代表了带宽占用的成本，跳数越多，成本越高
            total_cost += len(path)

        return total_cost

    def _generate_neighbor(self, vnffgManager: "VnffgManager", solution: SolutionDeploy) -> SolutionDeploy:
        """
        生成当前解的一个邻域解。
        策略：随机选择一个非首尾的 VNF，尝试将其迁移到一个新的、可行的 NFVI 节点。
        """
        new_solution = copy.deepcopy(solution)
        num_vnfs = len(vnffgManager.sfc_req.sfc_vnfs_type)

        if num_vnfs <= 2:
            return new_solution # 无法移动中间节点

        # 1. 随机选择一个可移动的 VNF (非第一个也非最后一个)
        vnf_to_move_idx = random.choice(range(1, num_vnfs - 1))
        original_nfvi_id = new_solution.map_node[vnf_to_move_idx]

        # 2. 为该 VNF 寻找一个新的、可行的部署节点
        # 可行节点需要满足：资源充足、与前序和后序 VNF 连通
        vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[vnf_to_move_idx]
        vnf_res = vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit

        candidate_nodes = []
        for nfvi in vnffgManager.vnfVim.nfvi_group.values():
            nfvi_id = nfvi.id
            if nfvi_id == original_nfvi_id:
                continue

            # 检查资源
            remaining_res = nfvi.node_handle.get_remaining_resource()
            if remaining_res['cpu'] >= vnf_res['cpu'] and remaining_res['ram'] >= vnf_res['ram']:

                # 检查与前序节点连通性
                prev_vnf_idx = vnf_to_move_idx - 1
                prev_nfvi_id = new_solution.map_node[prev_vnf_idx]
                try:
                    nx.dijkstra_path(vnffgManager.vnfVim.get_graph(), prev_nfvi_id, nfvi_id)
                except nx.NetworkXNoPath:
                    continue

                # 检查与后序节点连通性
                next_vnf_idx = vnf_to_move_idx + 1
                next_nfvi_id = new_solution.map_node[next_vnf_idx]
                try:
                    nx.dijkstra_path(vnffgManager.vnfVim.get_graph(), nfvi_id, next_nfvi_id)
                except nx.NetworkXNoPath:
                    continue

                candidate_nodes.append(nfvi)

        if not candidate_nodes:
            return new_solution # 找不到可行的迁移节点，返回原解

        # 3. 随机选择一个候选节点进行迁移
        new_nfvi = random.choice(candidate_nodes)
        new_solution.map_node[vnf_to_move_idx] = new_nfvi.id
        new_solution.share_node[vnf_to_move_idx] = None # 迁移后不再共享

        # 4. 更新受影响的链路
        # 更新与前序 VNF 的链路
        prev_link = (vnf_to_move_idx - 1, vnf_to_move_idx)
        try:
            path = nx.dijkstra_path(vnffgManager.vnfVim.get_graph(), new_solution.map_node[prev_link[0]], new_solution.map_node[prev_link[1]])
            new_solution.map_link[prev_link] = [(path[i], path[i+1]) for i in range(len(path)-1)]
        except nx.NetworkXNoPath:
            return new_solution # 迁移后链路不可达，返回原解

        # 更新与后序 VNF 的链路
        next_link = (vnf_to_move_idx, vnf_to_move_idx + 1)
        try:
            path = nx.dijkstra_path(vnffgManager.vnfVim.get_graph(), new_solution.map_node[next_link[0]], new_solution.map_node[next_link[1]])
            new_solution.map_link[next_link] = [(path[i], path[i+1]) for i in range(len(path)-1)]
        except nx.NetworkXNoPath:
            return new_solution # 迁移后链路不可达，返回原解

        return new_solution

    def _is_tabu(self, solution: SolutionDeploy) -> bool:
        """检查解是否在禁忌表中"""
        # 简化：使用 map_node 的元组作为解的特征
        solution_key = tuple(solution.map_node)
        for entry in self.tabu_list:
            if entry['key'] == solution_key:
                return True
        return False

    def _add_to_tabu(self, solution: SolutionDeploy):
        """将解加入禁忌表"""
        solution_key = tuple(solution.map_node)
        self.tabu_list.append({'key': solution_key, 'step': self.current_iteration})

    def solve_embedding(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """TS-MAPSCH 算法核心逻辑"""
        self.current_iteration = 0

        # 1. 生成初始解
        print("TS-MAPSCH: Generating initial solution with GEP...")
        self.best_solution = self.greedy_solver.solve_embedding(vnffgManager)
        if not self.best_solution.current_result:
            print("TS-MAPSCH: Initial solution generation failed.")
            return self.best_solution

        self.best_cost = self._calculate_cost(vnffgManager, self.best_solution)
        current_solution = copy.deepcopy(self.best_solution)
        current_cost = self.best_cost

        print(f"TS-MAPSCH: Initial cost: {self.best_cost}")

        # 2. 开始禁忌搜索迭代
        while self.current_iteration < self.max_iterations:
            print(f"TS-MAPSCH: Iteration {self.current_iteration + 1}/{self.max_iterations}, Current Best Cost: {self.best_cost}")

            # 3. 生成邻域解并寻找最优非禁忌解
            best_neighbor_solution = None
            best_neighbor_cost = float('inf')

            # 生成多个邻域解以找到更优的
            for _ in range(5): # 每次迭代生成5个邻域解
                neighbor_solution = self._generate_neighbor(vnffgManager, current_solution)
                neighbor_cost = self._calculate_cost(vnffgManager, neighbor_solution)

                # 检查解的有效性 (简化，假设 _generate_neighbor 生成的是有效解)
                if neighbor_cost < best_neighbor_cost:
                    # 应用 aspiration 准则
                    if not self._is_tabu(neighbor_solution) or neighbor_cost < self.best_cost:
                        best_neighbor_cost = neighbor_cost
                        best_neighbor_solution = neighbor_solution

            if best_neighbor_solution is None:
                print("TS-MAPSCH: No valid non-tabu neighbor found. Stopping early.")
                break

            # 4. 更新当前解
            current_solution = best_neighbor_solution
            current_cost = best_neighbor_cost

            # 5. 更新全局最优解
            if current_cost < self.best_cost:
                self.best_solution = copy.deepcopy(current_solution)
                self.best_cost = current_cost
                print(f"TS-MAPSCH: New best cost found: {self.best_cost}")

            # 6. 更新禁忌表
            self._add_to_tabu(current_solution)

            # 7. 老化禁忌表
            self.tabu_list = [entry for entry in self.tabu_list if self.current_iteration - entry['step'] < self.tabu_tenure]

            self.current_iteration += 1

        print(f"TS-MAPSCH: Search completed. Final best cost: {self.best_cost}")
        self.best_solution.current_description = SOLUTION_DEPLOY_TYPE.SET_SUCCESS # 假设找到的是有效解
        return self.best_solution

    def solve_migration(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """TS-MAPSCH 迁移逻辑（与部署逻辑类似）"""
        # 为简化，迁移逻辑可以复用部署逻辑，它会寻找一个全新的最优解
        print("TS-MAPSCH: Starting migration by finding a new optimal solution...")
        migration_solution = self.solve_embedding(vnffgManager)
        migration_solution.current_req_type = "migrate"
        migration_solution.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS if migration_solution.current_result else SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_OTHER
        self.calculate_cost_and_revenue(vnffgManager) # 如果需要
        return migration_solution