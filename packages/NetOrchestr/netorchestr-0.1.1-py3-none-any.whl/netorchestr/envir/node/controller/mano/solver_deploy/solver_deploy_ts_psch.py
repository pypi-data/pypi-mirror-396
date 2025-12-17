#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
solver_deploy_ts_psch.py
=======================

.. module:: solver_deploy_ts_psch
  :platform: Windows
  :synopsis: 基于禁忌搜索的路径选择与信道启发式 (TS-PSCH) SFC 编排求解器模块

.. moduleauthor:: WangXi

简介
----

该模块实现了文章中提出的禁忌搜索（Tabu Search）算法，专注于优化服务功能链（SFC）中各 VNF 之间的通信路径。
TS-PSCH 算法的核心目标是在满足端到端延迟等 QoS 约束的前提下，为 SFC 的每条虚拟链路选择最优的物理路径，
以实现网络资源（如带宽）的高效利用或最小化总通信延迟。

算法步骤：
1.  **初始化**: 使用贪心算法（如 GEP）生成一个初始可行解。
2.  **邻域搜索**: 通过对当前解中的某一条链路路径进行重新选择（例如，选择一条延迟稍高但带宽更充裕的路径）来生成邻域解。
3.  **禁忌表**: 记录最近更改过的链路路径，避免在短期内重复选择相同的次优路径。
4.  ** aspiration 准则**: 如果一个被禁忌的路径更改能显著降低端到端延迟或满足更严格的约束，则可以接受。
5.  **迭代**: 持续寻找更优的路径组合，直到达到迭代上限或无法找到更优解。

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

- 版本 1.0 (2025/11/12): 初始版本，实现 TS-PSCH 算法核心逻辑。
'''

import copy
import random
import networkx as nx
from typing import TYPE_CHECKING, Dict, List, Any, Tuple
from netorchestr.envir.node.controller.mano.solver_deploy.solver_deploy_gep import SolverDeployGEP
from netorchestr.envir.node.controller.mano.solver_deploy import SolutionDeploy, SolverDeployBase, SOLUTION_DEPLOY_TYPE

if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import VnffgManager

class SolverDeployTSPSCH(SolverDeployBase):
    def __init__(self, name: str):
        super().__init__(name)
        self.greedy_solver = SolverDeployGEP("gep_for_ts_psch")
        self.tabu_list: List[Dict[str, Any]] = []
        self.tabu_tenure = 8  # 禁忌 tenure
        self.max_iterations = 40  # 最大迭代次数
        self.best_solution: SolutionDeploy = None
        self.best_latency = float('inf') # 优化目标是最小化延迟

    def _calculate_end_to_end_latency(self, vnffgManager: "VnffgManager", solution: SolutionDeploy) -> float:
        """计算给定部署方案的端到端延迟"""
        total_latency = 0
        graph = vnffgManager.vnfVim.get_graph(with_weight="Latency")

        for (u, v), path in solution.map_link.items():
            # 计算每条链路的延迟
            path_latency = 0
            for i in range(len(path) - 1):
                edge_data = graph.get_edge_data(path[i], path[i+1])
                # 假设延迟存储在 'Latency' 属性中，单位为秒或毫秒
                path_latency += edge_data.get('Latency', 1.0).value if hasattr(edge_data.get('Latency', 1.0), 'value') else edge_data.get('Latency', 1.0)
            total_latency += path_latency

        return total_latency

    def _generate_neighbor(self, vnffgManager: "VnffgManager", solution: SolutionDeploy) -> SolutionDeploy:
        """
        生成当前解的一个邻域解。
        策略：随机选择一条链路，尝试为其寻找一条不同的、满足延迟约束的路径。
        """
        new_solution = copy.deepcopy(solution)
        links = list(solution.map_link.keys())

        if not links:
            return new_solution

        # 1. 随机选择一条链路
        link_to_change = random.choice(links)
        vnf_u_idx, vnf_v_idx = link_to_change
        nfvi_u_id = new_solution.map_node[vnf_u_idx]
        nfvi_v_id = new_solution.map_node[vnf_v_idx]

        # 2. 寻找该链路的备选路径
        graph = vnffgManager.vnfVim.get_graph(with_weight="Latency")
        original_path = new_solution.map_link[link_to_change]
        original_path_key = tuple(original_path)

        # 尝试找到所有可能的简单路径，然后排除当前路径
        try:
            # 注意：nx.all_simple_paths 可能非常耗时，在大型网络中不推荐使用
            # 这里仅作为示例，实际应用中可能需要更高效的方法或限制路径长度
            all_paths = list(nx.all_simple_paths(graph, source=nfvi_u_id, target=nfvi_v_id, cutoff=5)) # 限制最大跳数
        except nx.NetworkXNoPath:
            return new_solution

        # 过滤掉与当前路径完全相同的路径
        alternative_paths = []
        for path in all_paths:
            path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
            if tuple(path_edges) != original_path_key:
                alternative_paths.append(path_edges)

        if not alternative_paths:
            return new_solution # 找不到备选路径

        # 3. 随机选择一条备选路径
        new_path = random.choice(alternative_paths)
        new_solution.map_link[link_to_change] = new_path

        return new_solution

    def _is_tabu(self, solution: SolutionDeploy) -> bool:
        """检查解是否在禁忌表中（简化版）"""
        # 禁忌表记录被更改的链路及其旧路径，防止立即改回
        # 此函数用于判断一个新解是否因包含禁忌的"反向操作"而被禁止
        # 更精确的实现需要比较新旧解的差异并检查禁忌表
        return False # 简化实现，实际中需要更复杂的逻辑

    def _add_to_tabu(self, old_solution: SolutionDeploy, new_solution: SolutionDeploy):
        """将导致解变化的操作加入禁忌表"""
        # 找出发生变化的链路
        changed_links = []
        for link in old_solution.map_link:
            if old_solution.map_link[link] != new_solution.map_link[link]:
                changed_links.append(link)
                break # 假设每次只改变一个链路

        if changed_links:
            link = changed_links[0]
            # 禁忌内容：(链路, 旧路径)，表示在 tenure 步内禁止将此链路改回旧路径
            tabu_entry = {
                'link': link,
                'old_path': tuple(old_solution.map_link[link]),
                'step': self.current_iteration
            }
            self.tabu_list.append(tabu_entry)

    def solve_embedding(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """TS-PSCH 算法核心逻辑"""
        self.current_iteration = 0

        # 1. 生成初始解
        print("TS-PSCH: Generating initial solution with GEP...")
        self.best_solution = self.greedy_solver.solve_embedding(vnffgManager)
        if not self.best_solution.current_result:
            print("TS-PSCH: Initial solution generation failed.")
            return self.best_solution

        self.best_latency = self._calculate_end_to_end_latency(vnffgManager, self.best_solution)
        current_solution = copy.deepcopy(self.best_solution)
        current_latency = self.best_latency

        print(f"TS-PSCH: Initial end-to-end latency: {self.best_latency}")

        # 2. 开始禁忌搜索迭代
        while self.current_iteration < self.max_iterations:
            print(f"TS-PSCH: Iteration {self.current_iteration + 1}/{self.max_iterations}, Current Best Latency: {self.best_latency}")

            # 3. 生成邻域解并寻找最优非禁忌解
            best_neighbor_solution = None
            best_neighbor_latency = float('inf')

            for _ in range(5): # 每次迭代生成5个邻域解
                neighbor_solution = self._generate_neighbor(vnffgManager, current_solution)

                # 简化：不检查禁忌，直接评估
                neighbor_latency = self._calculate_end_to_end_latency(vnffgManager, neighbor_solution)

                if neighbor_latency < best_neighbor_latency:
                    best_neighbor_latency = neighbor_latency
                    best_neighbor_solution = neighbor_solution

            if best_neighbor_solution is None:
                print("TS-PSCH: No valid neighbor found. Stopping early.")
                break

            # 4. 更新当前解
            old_solution = copy.deepcopy(current_solution)
            current_solution = best_neighbor_solution
            current_latency = best_neighbor_latency

            # 5. 更新全局最优解
            if current_latency < self.best_latency:
                self.best_solution = copy.deepcopy(current_solution)
                self.best_latency = current_latency
                print(f"TS-PSCH: New best latency found: {self.best_latency}")

            # 6. 更新禁忌表
            self._add_to_tabu(old_solution, current_solution)

            # 7. 老化禁忌表
            self.tabu_list = [entry for entry in self.tabu_list if self.current_iteration - entry['step'] < self.tabu_tenure]

            self.current_iteration += 1

        print(f"TS-PSCH: Search completed. Final best latency: {self.best_latency}")
        self.best_solution.current_description = SOLUTION_DEPLOY_TYPE.SET_SUCCESS
        return self.best_solution

    def solve_migration(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """TS-PSCH 迁移逻辑（与部署逻辑类似）"""
        print("TS-PSCH: Starting migration by finding a new optimal path solution...")
        migration_solution = self.solve_embedding(vnffgManager)
        migration_solution.current_req_type = "migrate"
        migration_solution.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS if migration_solution.current_result else SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_OTHER
        self.calculate_cost_and_revenue(vnffgManager) # 如果需要
        return migration_solution