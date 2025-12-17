#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
solver_deploy_pposfc.py
=======================

.. module:: solver_deploy_pposfc
  :platform: Windows
  :synopsis: 基于近端策略优化 (PPO) 的动态 SFC 编排求解器模块，适配 LEO 卫星网络拓扑动态性，实现部署与调整联合优化

.. moduleauthor:: WangXi

简介
----

该模块实现了文章提出的 PPOSFC 算法，基于深度强化学习中的 PPO 框架，针对 LEO 卫星网络拓扑动态变化和资源约束特性，
以服务提供商利润最大化为目标，融合未来拓扑预测信息，实现 SFC 部署与调整的智能决策。核心特性包括：

- 动态拓扑感知：集成未来网络拓扑预测信息，通过时间片快照建模网络状态变化，提升决策前瞻性；
- PPO 强化学习框架：采用 actor-critic 架构，通过剪辑替代目标函数保证训练稳定性，结合广义优势估计 (GAE) 优化奖励计算；
- 双目标优化：同时考虑 SFC 部署成功率与调整成本，通过自定义奖励函数平衡服务质量与运营效率；
- K 短路路径优化：将虚拟链路映射限制在 K 短路集合内，解决动作空间爆炸问题，提升计算效率；
- 完整部署与调整流程：支持 SFC 接入时的初始部署 (solve_embedding) 与运行时的动态调整 (solve_migration)，适配卫星网络拓扑动态性。

参考
----

```
@Article{electronics14010056,
  AUTHOR = {Zhang, Ziyi and Hu, Hefei and Wu, You},
  TITLE = {DRL-Based Dynamic SFC Orchestration Algorithm for LEO Satellite Networks},
  JOURNAL = {Electronics},
  VOLUME = {14},
  YEAR = {2025},
  NUMBER = {1},
  ARTICLE-NUMBER = {56},
  URL = {https://www.mdpi.com/2079-9292/14/1/56},
  ISSN = {2079-9292},
  DOI = {10.3390/electronics14010056}
}
```


版本
----

- 版本 1.0 (2025/11/11): 初始版本，复现文章 PPOSFC 核心逻辑, 集成拓扑预测、PPO 决策、K 短路优化等关键特性
'''

import os
import copy
import random
import networkx as nx
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical

from astropy import units as u
from netorchestr.envir.node.controller.mano.solver_deploy import SolutionDeploy, SolverDeployBase, SOLUTION_DEPLOY_TYPE
from netorchestr.envir.node.controller.mano.vim import NfvInstance

from typing import TYPE_CHECKING, Union, List, Tuple, Dict
if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import VnffgManager

# PPO 算法超参数（参考文章仿真配置）
PPO_HYPERPARAMS = {
    'gamma': 0.99,        # 折扣因子
    'lambda': 0.95,       # GAE 参数
    'epsilon': 0.2,       # 剪辑参数
    'c1': 0.5,            # 价值函数损失系数
    'c2': 0.01,           # 熵正则化系数
    'lr': 1e-4,           # 学习率
    'batch_size': 256,    # 批次大小
    'epochs': 10,         # 每轮更新次数
    'k_shortest': 5       # K 短路数量
}

# 奖励函数参数（参考文章问题建模）
REWARD_PARAMS = {
    'zeta': 0.003,        # 部署成功即时奖励系数
    'eta': 10.0,          # 部署失败惩罚
    'theta': 0.002,       # 调整成功惩罚系数
    'vartheta': 20.0      # 调整失败惩罚
}

class PolicyNetwork(nn.Module):
    """PPO Actor 网络：状态到动作分布的映射"""
    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        self.fc1 = nn.Linear(state_dim, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, action_dim)
        self.activation = nn.Tanh()
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.activation(self.fc1(x))
        x = self.activation(self.fc2(x))
        logits = self.fc3(x)
        return torch.softmax(logits, dim=-1)

class ValueNetwork(nn.Module):
    """PPO Critic 网络：状态价值估计"""
    def __init__(self, state_dim: int):
        super().__init__()
        self.fc1 = nn.Linear(state_dim, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 1)
        self.activation = nn.Tanh()
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.activation(self.fc1(x))
        x = self.activation(self.fc2(x))
        return self.fc3(x)

class SolverDeployPPOSFC(SolverDeployBase):
    def __init__(self, name: str):
        super().__init__(name)
        
        # 网络状态缓存
        self.temp_nfvi_resources: Dict[int, Dict[str, Union[int, u.Quantity]]] = {}
        self.current_topo: nx.Graph = None
        self.future_topos: List[nx.Graph] = []  # 未来 K 个时间片拓扑预测
        self.k_shortest_paths: Dict[Tuple[int, int], List[List[int]]] = {}  # (起点,终点) -> 路径列表
        
        # PPO 相关初始化
        self.state_dim = None
        self.action_dim = None
        self.policy_net = None
        self.value_net = None
        self.optimizer = None
        
        # 训练数据缓存
        self.trajectories = []
        self.trajectory_count = 0

    def ready_for_controller(self, nfvOrchestrator):
        super().ready_for_controller(nfvOrchestrator)
        
        self._init_ppo_networks()
        
    def _init_ppo_networks(self):
        """初始化 PPO 网络和优化器"""
        # 动态计算状态维度：每个 NFVI 的 CPU/内存/存储剩余资源 + 链路带宽 + 延迟约束
        self.state_dim = 3 * len(self.nfvOrchestrator.vnfVim.nfvi_group) + 2
        # 动作维度：K 短路路径选择 * NFVI 节点选择（简化为路径选择主导）
        self.action_dim = PPO_HYPERPARAMS['k_shortest']
        
        self.policy_net = PolicyNetwork(self.state_dim, self.action_dim)
        self.value_net = ValueNetwork(self.state_dim)
        self.optimizer = optim.Adam(
            list(self.policy_net.parameters()) + list(self.value_net.parameters()),
            lr=PPO_HYPERPARAMS['lr']
        )

    def _get_k_shortest_paths(self, start_nfvi_id: int, end_nfvi_id: int) -> List[List[int]]:
        """
        获取起点到终点的 K 条最短路径（基于延迟权重）
        如果路径总数少于 K 则复制最后一条路径来凑齐 K 条
        """
        cache_key = (start_nfvi_id, end_nfvi_id)
        if cache_key in self.k_shortest_paths:
            return self.k_shortest_paths[cache_key]
        
        k = PPO_HYPERPARAMS['k_shortest']
        paths = []
        
        try:
            path_generator = nx.shortest_simple_paths(
                self.current_topo, 
                start_nfvi_id, 
                end_nfvi_id
            )
            
            # 手动迭代生成器，获取尽可能多的路径
            for path in path_generator:
                paths.append(path)
                # 如果已经获取了 k 条，就停止
                if len(paths) == k:
                    break
                
        except nx.NetworkXNoPath:
            # 如果根本不存在任何路径，返回空列表或根据业务决定如何处理
            self.k_shortest_paths[cache_key] = []
            return []

        if len(paths) > 0:
            while len(paths) < k:
                paths.append(paths[-1].copy())

        self.k_shortest_paths[cache_key] = paths
        return paths

    def _encode_state(self, vnffgManager: "VnffgManager") -> torch.Tensor:
        """编码网络状态: 包含当前资源、未来拓扑趋势、SFC 需求"""
        # 1. NFVI 资源状态（CPU、内存、存储剩余量归一化）
        nfvi_resources = []
        for nfvi in vnffgManager.vnfVim.nfvi_group.values():
            res = self.temp_nfvi_resources[nfvi.id]
            nfvi_resources.extend([
                res['cpu'],
                res['ram'].to(u.GB).value,
                res['rom'].to(u.GB).value
            ])
        nfvi_resources = np.array(nfvi_resources)
        nfvi_resources = (nfvi_resources - nfvi_resources.min(axis=0)) / (nfvi_resources.max(axis=0) - nfvi_resources.min(axis=0))

        # 2. SFC 需求特征（流量需求、延迟约束归一化）
        traffic_demand = (vnffgManager.sfc_req.sfc_trans_model['payload_size']/vnffgManager.sfc_req.sfc_trans_model['interval']).to(u.Mb/u.s).value  
        delay_constraint = vnffgManager.sfc_req.sfc_qos['latency'].to(u.ms).value / 500  
        
        # 3. 状态拼接与张量转换
        state_np = np.concatenate([nfvi_resources, np.array([traffic_demand, delay_constraint])])
        
        return torch.tensor(state_np, dtype=torch.float32).unsqueeze(0)

    def _calculate_reward(self, solution: SolutionDeploy, vnffgManager: "VnffgManager", is_migration: bool) -> float:
        """计算即时奖励"""
        if not solution.current_result:
            return -REWARD_PARAMS['eta'] if not is_migration else -REWARD_PARAMS['vartheta']
        
        if not is_migration:
            # 部署成功奖励：流量 * 生命周期
            traffic_demand = vnffgManager.sfc_req.sfc_trans_model['payload_size']/vnffgManager.sfc_req.sfc_trans_model['interval'].to(u.Mb/u.s).value
            lifecycle = (vnffgManager.sfc_req.end_time - vnffgManager.sfc_req.start_time).to(u.min).value
            reward = REWARD_PARAMS['zeta'] * traffic_demand * lifecycle
        else:
            # 调整成功惩罚：流量 * 迁移跳数
            traffic_demand = vnffgManager.sfc_req.sfc_trans_model['payload_size']/vnffgManager.sfc_req.sfc_trans_model['interval'].to(u.Mb/u.s).value
            migration_hops = self._calculate_migration_hops(solution, vnffgManager)
            reward = -REWARD_PARAMS['theta'] * traffic_demand * migration_hops
        
        return reward

    def _calculate_migration_hops(self, solution: SolutionDeploy, vnffgManager: "VnffgManager") -> float:
        """计算 VNF 迁移跳数（基于最短路径跳数）"""
        total_hops = 0.0
        # 获取历史部署节点
        history_map = vnffgManager.solutions_deploy[-1].map_node
        for v_node in range(len(solution.map_node)):
            old_nfvi_id = history_map.get(v_node, None)
            new_nfvi_id = solution.map_node[v_node]
            if old_nfvi_id and old_nfvi_id != new_nfvi_id:
                try:
                    # 计算新旧节点间最短路径跳数
                    path = nx.shortest_path(self.current_topo, old_nfvi_id, new_nfvi_id)
                    total_hops += len(path) - 1
                except nx.NetworkXNoPath:
                    total_hops += PPO_HYPERPARAMS['k_shortest']  # 不可达时赋予最大跳数惩罚
        return total_hops

    def _update_ppo_networks(self):
        """更新 PPO 网络（剪辑目标 + 价值损失 + 熵正则化）"""
        # 1. 检查是否有足够的数据进行一次更新
        if len(self.trajectories) < PPO_HYPERPARAMS['batch_size']:
            return
        
        # -------------------------- 数据采样与预处理 --------------------------
        # 对应 PPO 的 "经验收集" 环节，但这里是从已收集的轨迹中采样一个批次
        # PPO 是一种 On-Policy 算法，意味着它只能使用当前策略收集的数据进行更新
        batch = random.sample(self.trajectories, PPO_HYPERPARAMS['batch_size'])
        
        # 将批次数据转换为 PyTorch 张量，方便计算
        states = torch.cat([t['state'] for t in batch])           # 状态 s
        actions = torch.tensor([t['action'] for t in batch], dtype=torch.long).unsqueeze(1) # 动作 a
        old_probs = torch.tensor([t['prob'] for t in batch], dtype=torch.float32).unsqueeze(1) # 旧策略的动作概率 π_old(a|s)
        rewards = torch.tensor([t['reward'] for t in batch], dtype=torch.float32).unsqueeze(1) # 即时奖励 r
        next_states = torch.cat([t['next_state'] for t in batch]) # 下一个状态 s'
        dones = torch.tensor([t['done'] for t in batch], dtype=torch.float32).unsqueeze(1) # 结束标志 (1表示回合结束)

        # -------------------------- 计算 GAE 优势估计 --------------------------
        # 重要的一步用于稳定训练。
        # 优势函数 A(s,a) 衡量在状态 s 下采取动作 a 比平均动作好多少。
        # GAE 通过加权平均的方式结合了 TD-error，在偏差和方差之间取得了更好的平衡。
        
        # 使用 Critic 网络（价值网络）估计当前状态和下一个状态的价值 V(s) 和 V(s')
        values = self.value_net(states)
        next_values = self.value_net(next_states)
        
        # 计算 TD-error (Temporal Difference error)
        # δ_t = r_t + γ * V(s_{t+1}) * (1 - done_t) - V(s_t)
        deltas = rewards + PPO_HYPERPARAMS['gamma'] * next_values * (1 - dones) - values
        
        # 从后往前计算 GAE
        advantages = torch.zeros_like(deltas)
        advantage = 0.0
        # 逆序遍历是为了让每个时刻的优势都能包含未来的折扣奖励信息
        for t in reversed(range(len(deltas))):
            # A_t = δ_t + γλ * A_{t+1}
            advantage = deltas[t] + PPO_HYPERPARAMS['gamma'] * PPO_HYPERPARAMS['lambda'] * advantage
            advantages[t] = advantage
        
        # 计算目标回报 G_t，它等于优势函数加上状态价值 V(s_t)
        # G_t = A_t + V(s_t)
        returns = advantages + values
        
        # -------------------------- 标准化优势函数 --------------------------
        # 对优势函数进行标准化可以显著提升训练的稳定性和收敛速度。
        # 这使得优势的均值为0，标准差为1，避免了梯度爆炸或消失的问题。
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        advantages_detached = advantages.detach()
        old_probs_detached = old_probs.detach()

        # -------------------------- 多轮更新 (Policy Epochs) --------------------------
        # PPO 的一个关键优势是 "样本高效"。它会多次（epochs）使用同一个批次的数据来更新网络。
        # 这与传统的策略梯度方法（如 REINFORCE）每次更新只用一次数据形成对比。
        for _ in range(PPO_HYPERPARAMS['epochs']):
            # -------------------------- 策略网络前向传播 --------------------------
            # 使用当前的 Actor 网络（策略网络）计算在给定状态下采取动作的概率 π_θ(a|s)
            current_probs = self.policy_net(states).gather(1, actions)
            
            # -------------------------- 计算剪辑目标 (Clipped Surrogate Objective) --------------------------
            # 这是 PPO 算法最核心的部分，也是其名字 "Proximal Policy Optimization" 的由来。
            # 它通过限制新旧策略的更新幅度（即概率比）来防止策略更新过于激进导致训练崩溃。
            
            # 计算新旧策略的概率比 r_t(θ) = π_θ(a_t|s_t) / π_old(a_t|s_t)
            ratio = current_probs / (old_probs_detached + 1e-8) # 加一个小epsilon防止除以零
            
            # 计算未经剪辑的目标项：r_t * A_t
            surr1 = ratio * advantages_detached
            
            # 计算经过剪辑的目标项：clip(r_t, 1-ε, 1+ε) * A_t
            # 如果 r_t 超出 [1-ε, 1+ε] 的范围，就将其 "剪辑" 到边界上。
            clip_ratio = torch.clamp(ratio, 1 - PPO_HYPERPARAMS['epsilon'], 1 + PPO_HYPERPARAMS['epsilon'])
            surr2 = clip_ratio * advantages_detached
            
            # PPO 的目标函数是取这两个目标项中的较小值：min(r_t * A_t, clip(r_t, 1-ε, 1+ε) * A_t)
            # 这样做的目的是，当 r_t * A_t 很大时（例如，一个好的动作被过度放大），
            # 我们用剪辑后的版本来限制它，从而保证策略更新在一个 "安全" 的范围内。
            policy_loss = -torch.min(surr1, surr2).mean()
            
            # -------------------------- 价值函数损失 --------------------------
            # 同时更新 Critic 网络。Critic 的目标是让其预测的状态价值 V(s_t) 尽可能接近真实的目标回报 G_t。
            # 使用 MSE (Mean Squared Error) 损失来优化。
            # .detach() 是为了切断梯度流，不让 Critic 的更新影响到之前计算的优势函数和 returns。
            value_loss = nn.MSELoss()(self.value_net(states), returns.detach())
            
            # -------------------------- 熵正则化 --------------------------
            # 为了鼓励策略保持一定的随机性（探索），而不是过早地收敛到一个确定性策略，
            # PPO 通常会在总损失中加入一个熵正则项。
            # 熵越大，策略的随机性越高。我们减去熵损失（即加上负熵），
            # 这样优化器在最小化总损失时会倾向于选择熵更大的策略。
            dist = Categorical(self.policy_net(states))
            entropy_loss = -dist.entropy().mean()
            
            # -------------------------- 计算总损失 --------------------------
            # 总损失 = 策略损失 + c1 * 价值损失 - c2 * 熵损失
            # c1 和 c2 是超参数，用来平衡这三个部分的权重。
            total_loss = policy_loss + PPO_HYPERPARAMS['c1'] * value_loss - PPO_HYPERPARAMS['c2'] * entropy_loss
            
            # -------------------------- 反向传播与优化 --------------------------
            # 清空之前的梯度
            self.optimizer.zero_grad()
            # 反向传播计算梯度
            total_loss.backward()
            # 根据梯度更新网络参数
            self.optimizer.step()
        
        # 更新完成后，清空轨迹缓存，为下一轮收集数据做准备
        self.trajectories.clear()

    def get_predict_topo_graphs(self, vnffgManager:"VnffgManager", time_step:u.Quantity = 1*u.min, n=3):
        sfc_curr_time = vnffgManager.scheduler.now
        sfc_end_time = sfc_curr_time + (time_step * n).to(u.ms).value
        sfc_predict_topo_time_list = np.arange(sfc_curr_time, sfc_end_time+(time_step).to(u.ms).value, (time_step).to(u.ms).value)
        sfc_predict_topo_time_list = sfc_predict_topo_time_list * u.ms
        predict_topo_graphs = []
        for time in sfc_predict_topo_time_list:
            predict_topo_graphs.append(vnffgManager.vnfVim.get_graph(time=time, with_weight="Latency"))
        return predict_topo_graphs
    
    def _calculate_node_stability(self, nfvi_id: int) -> float:
        """计算节点稳定性：基于未来拓扑中链路存续时间"""
        stability_score = 0.0
        for future_topo in self.future_topos:
            if nfvi_id in future_topo.nodes:
                # 节点存在则计算连接度稳定性
                current_degree = self.current_topo.degree(nfvi_id)
                future_degree = future_topo.degree(nfvi_id)
                stability_score += 1 - abs(current_degree - future_degree) / max(current_degree, future_degree, 1)
        return stability_score / len(self.future_topos) if self.future_topos else 0.0

    def solve_embedding(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """
        PPOSFC 初始部署逻辑：基于 PPO 决策选择最优部署方案
        
        Args:
            vnffgManager (VnffgManager): SFC 编排管理器
            
        Returns:
            SolutionDeploy: 部署结果（包含节点映射、链路映射、部署状态）
        """
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "arrive"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        
        
        # region 准备算法输入数据 ---------------------------------------------
        self.solution_deploy.current_time = vnffgManager.scheduler.now
        self.solution_deploy.resource['cpu'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu']
                                                for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['ram'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['ram']
                                                for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['rom'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['rom']
                                                for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        
        self.current_topo = vnffgManager.vnfVim.get_graph(time=vnffgManager.scheduler.now*u.ms, with_weight="Latency")
        adjacent_topo_with_ue = vnffgManager.vnfVim.get_graph_to_ue(vnffgManager.ue_access_start, self.current_topo, with_weight="Latency")
        adjacent_topo_with_ue = vnffgManager.vnfVim.get_graph_to_ue(vnffgManager.ue_access_end, adjacent_topo_with_ue, with_weight="Latency")

        self.solution_deploy.current_topo = self.current_topo
        self.solution_deploy.current_topo_with_ue = adjacent_topo_with_ue
        self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos
        
        self.future_topos = self.get_predict_topo_graphs(vnffgManager, time_step=1*u.min, n=3)  # 获取未来 3 个时间片拓扑
        
        # 深拷贝资源状态（避免影响实际网络）
        self.temp_nfvi_resources = {
            nfvi.id: copy.deepcopy(nfvi.node_handle.get_remaining_resource())
            for nfvi in vnffgManager.vnfVim.nfvi_group.values()
        }
        
        self.solution_deploy.share_node = [None] * len(self.current_vnfs_index_list)
        self.solution_deploy.map_node = {vnf_index: None for vnf_index in self.current_vnfs_index_list}
        self.solution_deploy.map_link = {}
        
        # region 执行算法主要逻辑 ---------------------------------------------
        # 1. 起始 VNF 部署（UE 接入点约束）
        start_access_nfvis = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_start)
        if not start_access_nfvis:
            self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_UE_ACCESS_START
            self.solution_deploy.current_result = False
            return self.solution_deploy
        
        # 2. 终止 VNF 部署（UE 接入点约束）
        end_access_nfvis = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_end)
        if not end_access_nfvis:
            self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_UE_ACCESS_END
            self.solution_deploy.current_result = False
            return self.solution_deploy
        
        # 3. 基于未来拓扑选择稳定起始-终止节点间 K 短路路径
        start_nfvi = max(start_access_nfvis, key=lambda x: self._calculate_node_stability(x.id))
        end_nfvi = max(end_access_nfvis, key=lambda x: self._calculate_node_stability(x.id))
        self.solution_deploy.map_node[self.current_vnfs_index_list[0]] = start_nfvi.id
        self.solution_deploy.map_node[self.current_vnfs_index_list[-1]] = end_nfvi.id
        
        k_paths = self._get_k_shortest_paths(start_nfvi.id, end_nfvi.id)
        if not k_paths:
            self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
            self.solution_deploy.current_result = False
            return self.solution_deploy
        
        # 4. PPO 策略选择最优路径
        state = self._encode_state(vnffgManager)
        action_probs = self.policy_net(state)
        dist = Categorical(action_probs)
        action = dist.sample()
        action_idx = action.item()
        selected_path = k_paths[action_idx % len(k_paths)]
        
        # 5. 中间 VNF 部署（路径上节点选择）
        path_nfvi_ids = selected_path[1:-1]  # 排除起始和终止节点
        path_nfvis = [vnffgManager.vnfVim.nfvi_group[pid] for pid in path_nfvi_ids]
        
        for v_node in self.current_vnfs_index_list[1:-1]:
            if not path_nfvis:
                # 路径节点不足时选择资源最充足节点
                all_nfvis = list(vnffgManager.vnfVim.nfvi_group.values())
                choosen_nfvi = max(all_nfvis, key=lambda x: self.temp_nfvi_resources[x.id]['cpu'])
            else:
                # 路径上选择资源最充足节点
                choosen_nfvi = max(path_nfvis, key=lambda x: self.temp_nfvi_resources[x.id]['cpu'])
            
            # 资源检查与扣减
            cpu_need = self.solution_deploy.resource['cpu'][v_node]
            ram_need = self.solution_deploy.resource['ram'][v_node]
            rom_need = self.solution_deploy.resource['rom'][v_node]
            
            if self.temp_nfvi_resources[choosen_nfvi.id]['cpu'] < cpu_need:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_CPU
                self.solution_deploy.current_result = False
                return self.solution_deploy
            elif self.temp_nfvi_resources[choosen_nfvi.id]['ram'] < ram_need:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_RAM
                self.solution_deploy.current_result = False
                return self.solution_deploy
            elif self.temp_nfvi_resources[choosen_nfvi.id]['rom'] < rom_need:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_ROM
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            # 更新资源与映射
            self.temp_nfvi_resources[choosen_nfvi.id]['cpu'] -= cpu_need
            self.temp_nfvi_resources[choosen_nfvi.id]['ram'] -= ram_need
            self.temp_nfvi_resources[choosen_nfvi.id]['rom'] -= rom_need
            self.solution_deploy.map_node[v_node] = choosen_nfvi.id
            
            # 共享 VNF 处理
            vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
            if vnffgManager.sfc_req.sfc_vnfs_shared[v_node]:
                shared_vnfems = choosen_nfvi.get_deployed_vnf_with_type(vnf_type)
                self.solution_deploy.share_node[v_node] = shared_vnfems[0].id if shared_vnfems else None
        
        # 6. 虚拟链路映射（基于选定路径）
        v_links = [(v_node, v_node+1) for v_node in self.current_vnfs_index_list[:-1]]
        for v_link in v_links:
            try:
                map_path = nx.dijkstra_path(self.current_topo, self.solution_deploy.map_node[v_link[0]], self.solution_deploy.map_node[v_link[1]])
            except:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            if len(map_path) == 1:
                self.solution_deploy.map_link[v_link] = [(map_path[0], map_path[0])]
            else:
                self.solution_deploy.map_link[v_link] = [(map_path[i],map_path[i+1]) for i in range(len(map_path)-1)]
                
        # 7. 记录轨迹用于训练
        next_state = self._encode_state(vnffgManager)
        reward = self._calculate_reward(self.solution_deploy, vnffgManager, is_migration=False)
        self.trajectories.append({
            'state': state,
            'action': action_idx,
            'prob': action_probs[0][action_idx].item(),
            'reward': reward,
            'next_state': next_state,
            'done': True
        })
        
        # 8. 定期更新 PPO 网络
        self.trajectory_count += 1
        if self.trajectory_count % 10 == 0:
            self._update_ppo_networks()
        
        # region 检查算法解可行性 ---------------------------------------------
        
        self.solution_deploy.current_description = self.check_solution(vnffgManager)
        self.solution_deploy.current_result = (self.solution_deploy.current_description == SOLUTION_DEPLOY_TYPE.SET_SUCCESS)

        return self.solution_deploy

    def solve_migration(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """
        PPOSFC 动态调整逻辑：基于拓扑变化和 PPO 决策优化调整方案
        
        Args:
            vnffgManager (VnffgManager): SFC 编排管理器
            
        Returns:
            SolutionDeploy: 调整结果（包含节点映射、链路映射、调整状态）
        """
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "migrate"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        
        
        # region 准备算法输入数据 ---------------------------------------------
        self.solution_deploy.current_time = vnffgManager.scheduler.now
        self.solution_deploy.resource['cpu'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu']
                                                for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['ram'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['ram']
                                                for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['rom'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['rom']
                                                for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        
        self.current_topo = vnffgManager.vnfVim.get_graph(time=vnffgManager.scheduler.now*u.ms, with_weight="Latency")
        adjacent_topo_with_ue = vnffgManager.vnfVim.get_graph_to_ue(vnffgManager.ue_access_start, self.current_topo, with_weight="Latency")
        adjacent_topo_with_ue = vnffgManager.vnfVim.get_graph_to_ue(vnffgManager.ue_access_end, adjacent_topo_with_ue, with_weight="Latency")

        self.solution_deploy.current_topo = self.current_topo
        self.solution_deploy.current_topo_with_ue = adjacent_topo_with_ue
        self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos
        
        self.future_topos = self.get_predict_topo_graphs(vnffgManager, time_step=1*u.min, n=3)  # 获取未来 3 个时间片拓扑
        
        # 深拷贝资源状态（避免影响实际网络）
        self.temp_nfvi_resources = {
            nfvi.id: copy.deepcopy(nfvi.node_handle.get_remaining_resource())
            for nfvi in vnffgManager.vnfVim.nfvi_group.values()
        }
        
        self.solution_deploy.share_node = [None] * len(self.current_vnfs_index_list)
        self.solution_deploy.map_node = {vnf_index: None for vnf_index in self.current_vnfs_index_list}
        self.solution_deploy.map_link = {}

        # region 执行算法主要逻辑 ---------------------------------------------
        # 1. 重新验证起始 VNF 部署（UE 接入点约束）
        start_access_nfvis = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_start)
        if not start_access_nfvis:
            self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_UE_ACCESS_START
            self.solution_deploy.current_result = False
            return self.solution_deploy
        
        # 2. 重新验证终止 VNF 部署（UE 接入点约束）
        end_access_nfvis = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_end)
        if not end_access_nfvis:
            self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_UE_ACCESS_END
            self.solution_deploy.current_result = False
            return self.solution_deploy
        
        # 3. 基于未来拓扑选择稳定起始-终止节点间 K 短路路径
        start_nfvi = max(start_access_nfvis, key=lambda x: self._calculate_node_stability(x.id))
        end_nfvi = max(end_access_nfvis, key=lambda x: self._calculate_node_stability(x.id))
        self.solution_deploy.map_node[self.current_vnfs_index_list[0]] = start_nfvi.id
        self.solution_deploy.map_node[self.current_vnfs_index_list[-1]] = end_nfvi.id
        
        k_paths = self._get_k_shortest_paths(start_nfvi.id, end_nfvi.id)
        if not k_paths:
            self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_PATH
            self.solution_deploy.current_result = False
            return self.solution_deploy
        
        # 4. PPO 策略选择最优路径
        state = self._encode_state(vnffgManager)
        action_probs = self.policy_net(state)
        dist = Categorical(action_probs)
        action = dist.sample()
        action_idx = action.item()
        selected_path = k_paths[action_idx % len(k_paths)]
        
        # 5. 中间 VNF 调整部署
        path_nfvi_ids = selected_path[1:-1]
        path_nfvis = [vnffgManager.vnfVim.nfvi_group[pid] for pid in path_nfvi_ids]
        
        history_map = vnffgManager.solutions_deploy[-1].map_node
        for v_node in self.current_vnfs_index_list[1:-1]:
            # 优先选择历史节点（减少迁移成本）
            old_nfvi_id = history_map.get(v_node, None)
            if old_nfvi_id and old_nfvi_id in path_nfvi_ids:
                choosen_nfvi = vnffgManager.vnfVim.nfvi_group[old_nfvi_id]
                # 检查资源是否充足
                vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
                cpu_need = vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu']
                if self.temp_nfvi_resources[choosen_nfvi.id]['cpu'] >= cpu_need:
                    self.solution_deploy.map_node[v_node] = old_nfvi_id
                    self.temp_nfvi_resources[choosen_nfvi.id]['cpu'] -= cpu_need
                    continue
            
            # 路径上选择资源充足且稳定的节点
            if path_nfvis:
                choosen_nfvi = max(path_nfvis, key=lambda x: (
                    self.temp_nfvi_resources[x.id]['cpu'],
                    self._calculate_node_stability(x.id)
                ))
            else:
                choosen_nfvi = max(vnffgManager.vnfVim.nfvi_group.values(), key=lambda x: self.temp_nfvi_resources[x.id]['cpu'])
            
            # 资源检查
            cpu_need = self.solution_deploy.resource['cpu'][v_node]
            ram_need = self.solution_deploy.resource['ram'][v_node]
            rom_need = self.solution_deploy.resource['rom'][v_node]
            
            if self.temp_nfvi_resources[choosen_nfvi.id]['cpu'] < cpu_need:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_CPU
                self.solution_deploy.current_result = False
                return self.solution_deploy
            elif self.temp_nfvi_resources[choosen_nfvi.id]['ram'] < ram_need:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_RAM
                self.solution_deploy.current_result = False
                return self.solution_deploy
            elif self.temp_nfvi_resources[choosen_nfvi.id]['rom'] < rom_need:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_ROM
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            # 更新资源与映射
            self.temp_nfvi_resources[choosen_nfvi.id]['cpu'] -= cpu_need
            self.temp_nfvi_resources[choosen_nfvi.id]['ram'] -= ram_need
            self.temp_nfvi_resources[choosen_nfvi.id]['rom'] -= rom_need
            self.solution_deploy.map_node[v_node] = choosen_nfvi.id
            
            # 共享 VNF 处理
            vnf_type = vnffgManager.sfc_req.sfc_vnfs_type[v_node]
            if vnffgManager.sfc_req.sfc_vnfs_shared[v_node]:
                shared_vnfems = choosen_nfvi.get_deployed_vnf_with_type(vnf_type)
                self.solution_deploy.share_node[v_node] = shared_vnfems[0].id if shared_vnfems else None
        
        # 6. 虚拟链路重新映射
        v_links = [(v_node, v_node+1) for v_node in self.current_vnfs_index_list[:-1]]
        for v_link in v_links:
            try:
                map_path = nx.dijkstra_path(self.current_topo, self.solution_deploy.map_node[v_link[0]], self.solution_deploy.map_node[v_link[1]])
            except:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_PATH
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            if len(map_path) == 1:
                self.solution_deploy.map_link[v_link] = [(map_path[0], map_path[0])]
            else:
                self.solution_deploy.map_link[v_link] = [(map_path[i],map_path[i+1]) for i in range(len(map_path)-1)]
        
        # 7. 记录轨迹用于训练
        next_state = self._encode_state(vnffgManager)
        reward = self._calculate_reward(self.solution_deploy, vnffgManager, is_migration=True)
        self.trajectories.append({
            'state': state,
            'action': action_idx,
            'prob': action_probs[0][action_idx].item(),
            'reward': reward,
            'next_state': next_state,
            'done': True
        })
        
        # 8. 定期更新 PPO 网络
        self.trajectory_count += 1
        if self.trajectory_count % 10 == 0:
            self._update_ppo_networks()
        
        # region 检查算法解可行性 ---------------------------------------------
        
        self.solution_deploy.current_description = self.check_solution(vnffgManager)
        self.solution_deploy.current_result = (self.solution_deploy.current_description == SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS)
        
        self.calculate_cost_and_revenue(vnffgManager)
        
        return self.solution_deploy

    def save_param(self, param_file_path: str = None):
        """
        保存 PPO 网络模型
        
        Args:
            save_path (str): 模型保存路径
            
        Notes:
            参数内容包括
            - policy_net_param
            - value_net_param
            - optimizer_param
        """
        if param_file_path is None:
            param_file_path = os.path.join(self.vnffgManager.vnfVim.net.logger.log_dir, f'{self.name}_model.pt')
        
        torch.save({
            'policy_net_param': self.policy_net.state_dict(),
            'value_net_param': self.value_net.state_dict(),
            'optimizer_param': self.optimizer.state_dict(),
        }, param_file_path)
    
    def load_param(self, param_file_path: str = None):
        """
        加载 PPO 网络模型
        
        Args:
            load_path (str): 模型加载路径
        """
        
        if param_file_path is None:
            print(f'INFO: {self.name} 没有指定求解器参数文件路径，将使用随机初始化参数')
        elif not os.path.exists(param_file_path):
            print(f'INFO: {self.name} 没有找到求解器参数文件 {param_file_path} 将使用随机初始化参数')
        else:
            print(f'INFO: {self.name} 加载求解器参数 {param_file_path}')
            checkpoint = torch.load(param_file_path, weights_only=True)
            self.policy_net.load_state_dict(checkpoint['policy_net_param'])
            self.value_net.load_state_dict(checkpoint['value_net_param'])
            self.optimizer.load_state_dict(checkpoint['optimizer_param'])
        
    def get_newest_model_file(self, dirs_path:str):
        dir_has_model_file: list[str] = []
        for dir_path in os.listdir(dirs_path):
            if os.path.isdir(os.path.join(dirs_path, dir_path)):
                # 判断该目录下是否有以 .pt 结尾的文件
                if os.path.exists(os.path.join(dirs_path, dir_path, f'{self.name}_model.pt')):
                    dir_has_model_file.append(dir_path)
        if len(dir_has_model_file) == 0:
            return None
        else:
            dir_has_model_file.sort()
            return os.path.join(dirs_path, dir_has_model_file[-1], f'{self.name}_model.pt')    
    
    
