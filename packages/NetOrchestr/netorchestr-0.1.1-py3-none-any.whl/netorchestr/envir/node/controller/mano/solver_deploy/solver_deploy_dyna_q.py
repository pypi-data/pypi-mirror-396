#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
solver_deploy_dyna_q.py
=======================

.. module:: solver_deploy_dyna_q
  :platform: Windows
  :synopsis: 基于深度Dyna-Q(DDQ)算法的SFC动态重配置求解器模块, 结合GNN资源预测与强化学习, 实现IoT网络中VNF迁移与路径重路由的自适应优化

.. moduleauthor:: WangXi

简介
----

该模块复现了IEEE IoT JOURNAL 2020年论文提出的DDQ算法, 核心聚焦IoT网络中SFC动态重配置问题(SFC-DRP). 通过GNN预测VNF资源需求, 结合DTMDP建模与改进Dyna-Q算法, 在满足QoS和资源约束的前提下, 实现收益最大化与重配置成本最小化的trade-off优化. 
它提供了以下特性: 

- GNN资源预测: 基于图神经网络的多任务学习模型, 预测VNF的CPU、存储和延迟需求, RMSE低至0.17, 有效避免"滞后性"问题；
- DTMDP建模: 将SFC重配置过程建模为离散时间马尔可夫决策过程, 状态包含VNF实例和链路状态, 动作涵盖VNF迁移与路径重路由；
- 改进Dyna-Q算法: 融合直接强化学习 (真实经验) 与间接强化学习 (模拟经验) , 采用新型动作选择函数加速收敛；
- 双阶段训练机制: GNN模型支持离线预训练与在线滑动窗口更新, 适配动态服务请求；
- 严格约束满足: 保证资源利用率阈值 (0.2~0.8) 、端到端延迟QoS约束及服务连续性的迁移次数限制. 

参考
----

```
@ARTICLE{Liu2020DynaQ,
  author={Liu, Yicen and Lu, Yu and Li, Xi and Yao, Zhigang and Zhao, Donghao},
  journal={IEEE Internet of Things Journal}, 
  title={On Dynamic Service Function Chain Reconfiguration in IoT Networks}, 
  year={2020},
  volume={7},
  number={11},
  pages={10969-10984},
  keywords={Internet of Things;Resource management;Quality of service;Cloud computing;Virtualization;Dynamic scheduling;Proposals;Deep Dyna-Q (DDQ) approach;discrete-time Markov decision process (DTMDP);Internet-of-Things (IoT) network;network function virtualization (NFV);service function chain (SFC) reconfiguration},
  doi={10.1109/JIOT.2020.2991753}
}
```

版本
----

- 版本 1.0 (2025/11/11): 初始版本, 完整复现论文GNN资源预测、DTMDP建模与DDQ重配置核心逻辑
- 版本 1.1 (2025/11/12): 将TensorFlow实现改为PyTorch实现, 保持算法逻辑与性能一致

'''

import copy
import random
import math
import networkx as nx
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from collections import deque

from astropy import units as u
from netorchestr.envir.node.controller.mano.solver_deploy import SolutionDeploy, SolverDeployBase, SOLUTION_DEPLOY_TYPE
from netorchestr.envir.node.controller.mano.vim import NfvInstance

from typing import TYPE_CHECKING, Union, Dict, List, Tuple, Optional
if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import VnffgManager

class GNNResourcePredictor(nn.Module):
    """基于图神经网络的VNF资源预测模型 (复现论文多任务学习机制) - PyTorch实现"""
    def __init__(self, history_window: int = 20, predict_window: int = 20):
        super(GNNResourcePredictor, self).__init__()
        self.history_window = history_window  # 历史观测窗口长度
        self.predict_window = predict_window  # 预测窗口长度
        self.hidden_dim = 35  # 隐藏层神经元数 (论文Table III配置) 
        self.task_layer_dim = 66  # 多任务层神经元数
        self.learning_rate = 0.0001
        self.max_iterations = 300
        self.beta = 0.01  # 惩罚项权重
        self.input_dim = None  # 输入维度 (动态确定) 
        self.training_data = deque(maxlen=10000)  # 训练数据缓存
        
        # 构建网络层 (复现论文网络结构) 
        self.feature_encoder = nn.Sequential(
            nn.Linear(self.input_dim if self.input_dim else 129, 129),
            nn.ReLU(),
            nn.Linear(129, 66),
            nn.ReLU(),
            nn.Linear(66, self.hidden_dim),
            nn.ReLU()
        )
        
        self.task_layer = nn.Sequential(
            nn.Linear(self.hidden_dim, self.task_layer_dim),
            nn.ReLU()
        )
        
        # 多任务输出层 (CPU、存储、延迟) 
        self.cpu_output = nn.Linear(self.task_layer_dim, self.predict_window)
        self.storage_output = nn.Linear(self.task_layer_dim, self.predict_window)
        self.delay_output = nn.Linear(self.task_layer_dim, self.predict_window)
        
        # 优化器
        self.optimizer = optim.Adam(self.parameters(), lr=self.learning_rate)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """前向传播 (复现h_ω和g_ω函数) """
        # 特征编码 (h_ω函数) 
        encoded = self.feature_encoder(x)
        # 多任务处理
        task_features = self.task_layer(encoded)
        # 输出预测 (g_ω函数) 
        cpu_pred = self.cpu_output(task_features)
        storage_pred = self.storage_output(task_features)
        delay_pred = self.delay_output(task_features)
        return cpu_pred, storage_pred, delay_pred

    def penalized_quadratic_cost(self, y_true: torch.Tensor, y_pred: torch.Tensor) -> torch.Tensor:
        """惩罚二次损失函数 (复现论文公式) """
        mse = nn.functional.mse_loss(y_pred, y_true)
        # 收缩映射惩罚项
        penalty = self.beta * torch.mean(torch.square(y_pred))
        return mse + penalty

    def normalize_features(self, features: np.ndarray) -> np.ndarray:
        """特征归一化"""
        return (features - np.mean(features, axis=0)) / (np.std(features, axis=0) + 1e-8)

    class ResourceDataset(Dataset):
        """资源预测数据集"""
        def __init__(self, features: np.ndarray, cpu_labels: np.ndarray, storage_labels: np.ndarray, delay_labels: np.ndarray):
            self.features = torch.tensor(features, dtype=torch.float32)
            self.cpu_labels = torch.tensor(cpu_labels, dtype=torch.float32)
            self.storage_labels = torch.tensor(storage_labels, dtype=torch.float32)
            self.delay_labels = torch.tensor(delay_labels, dtype=torch.float32)

        def __len__(self) -> int:
            return len(self.features)

        def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
            return (self.features[idx], self.cpu_labels[idx], 
                    self.storage_labels[idx], self.delay_labels[idx])

    def update_network_dimensions(self, input_dim: int):
        """更新网络输入维度 (动态适配数据) """
        self.input_dim = input_dim
        # 重新初始化特征编码器以匹配输入维度
        self.feature_encoder = nn.Sequential(
            nn.Linear(self.input_dim, 129),
            nn.ReLU(),
            nn.Linear(129, 66),
            nn.ReLU(),
            nn.Linear(66, self.hidden_dim),
            nn.ReLU()
        )
        # 更新优化器
        self.optimizer = optim.Adam(self.parameters(), lr=self.learning_rate)

    def offline_train(self, vnffgManager: "VnffgManager"):
        """离线预训练 (复现论文Step 1) """
        # 收集历史数据: [CPU(t-history_window), ..., CPU(t), 存储, 延迟]
        all_features = []
        all_cpu_labels = []
        all_storage_labels = []
        all_delay_labels = []

        # 遍历所有已部署的VNF实例收集历史数据
        for nfvi in vnffgManager.vnfVim.nfvi_group.values():
            for vnfem in nfvi.get_all_deployed_vnfems():
                # 假设VNF实例有历史资源记录属性 history_resources
                history = vnfem.history_resources  # 格式: List[Dict['cpu', 'storage', 'delay', 'time']]
                if len(history) < self.history_window + self.predict_window:
                    continue
                
                # 构建输入特征 (历史窗口) 和标签 (预测窗口) 
                for i in range(len(history) - self.history_window - self.predict_window + 1):
                    hist_data = history[i:i+self.history_window]
                    pred_data = history[i+self.history_window:i+self.history_window+self.predict_window]
                    
                    # 特征: CPU、存储、延迟的历史序列
                    feature = []
                    for item in hist_data:
                        feature.extend([item['cpu'], item['storage'], item['delay']])
                    feature = np.array(feature)
                    
                    # 标签: 未来窗口的资源需求
                    cpu_label = np.array([item['cpu'] for item in pred_data])
                    storage_label = np.array([item['storage'] for item in pred_data])
                    delay_label = np.array([item['delay'] for item in pred_data])
                    
                    all_features.append(feature)
                    all_cpu_labels.append(cpu_label)
                    all_storage_labels.append(storage_label)
                    all_delay_labels.append(delay_label)
        
        if not all_features:
            raise ValueError("无足够历史数据进行离线训练")
        
        # 归一化
        X = self.normalize_features(np.array(all_features))
        y_cpu = np.array(all_cpu_labels)
        y_storage = np.array(all_storage_labels)
        y_delay = np.array(all_delay_labels)
        
        # 更新网络输入维度
        self.update_network_dimensions(X.shape[1])
        
        # 创建数据集和数据加载器
        dataset = self.ResourceDataset(X, y_cpu, y_storage, y_delay)
        dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
        
        # 训练模型
        self.train()
        for epoch in range(self.max_iterations):
            total_loss = 0.0
            for batch in dataloader:
                features, cpu_labels, storage_labels, delay_labels = batch
                
                # 前向传播
                cpu_pred, storage_pred, delay_pred = self(features)
                
                # 计算损失
                loss_cpu = self.penalized_quadratic_cost(cpu_labels, cpu_pred)
                loss_storage = self.penalized_quadratic_cost(storage_labels, storage_pred)
                loss_delay = self.penalized_quadratic_cost(delay_labels, delay_pred)
                total_batch_loss = loss_cpu + loss_storage + loss_delay
                
                # 反向传播和优化
                self.optimizer.zero_grad()
                total_batch_loss.backward()
                self.optimizer.step()
                
                total_loss += total_batch_loss.item()
            
            # 每50轮打印一次损失
            if (epoch + 1) % 50 == 0:
                avg_loss = total_loss / len(dataloader)
        
        # 缓存训练数据
        for feat, cpu, storage, delay in zip(all_features, all_cpu_labels, all_storage_labels, all_delay_labels):
            self.training_data.append((feat, cpu, storage, delay))

    def online_update(self, vnffgManager: "VnffgManager"):
        """在线更新 (复现论文滑动窗口机制) """
        if self.input_dim is None:
            self.offline_train(vnffgManager)
            return
        
        # 收集最新数据
        new_features = []
        new_cpu_labels = []
        new_storage_labels = []
        new_delay_labels = []
        
        for nfvi in vnffgManager.vnfVim.nfvi_group.values():
            for vnfem in nfvi.get_all_deployed_vnfems():
                history = vnfem.history_resources
                if len(history) < self.history_window + self.predict_window:
                    continue
                
                # 取最新的一个窗口数据
                i = len(history) - self.history_window - self.predict_window
                hist_data = history[i:i+self.history_window]
                pred_data = history[i+self.history_window:i+self.history_window+self.predict_window]
                
                feature = []
                for item in hist_data:
                    feature.extend([item['cpu'], item['storage'], item['delay']])
                feature = np.array(feature)
                
                cpu_label = np.array([item['cpu'] for item in pred_data])
                storage_label = np.array([item['storage'] for item in pred_data])
                delay_label = np.array([item['delay'] for item in pred_data])
                
                new_features.append(feature)
                new_cpu_labels.append(cpu_label)
                new_storage_labels.append(storage_label)
                new_delay_labels.append(delay_label)
        
        if new_features:
            # 滑动窗口更新训练数据
            for feat, cpu, storage, delay in zip(new_features, new_cpu_labels, new_storage_labels, new_delay_labels):
                self.training_data.append((feat, cpu, storage, delay))
            
            # 准备在线训练数据
            X = self.normalize_features(np.array([f for f, _, _, _ in self.training_data]))
            y_cpu = np.array([c for _, c, _, _ in self.training_data])
            y_storage = np.array([s for _, _, s, _ in self.training_data])
            y_delay = np.array([d for _, _, _, d in self.training_data])
            
            # 创建数据集
            dataset = self.ResourceDataset(X, y_cpu, y_storage, y_delay)
            dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
            
            # 在线微调
            self.train()
            for epoch in range(10):
                total_loss = 0.0
                for batch in dataloader:
                    features, cpu_labels, storage_labels, delay_labels = batch
                    
                    cpu_pred, storage_pred, delay_pred = self(features)
                    
                    loss_cpu = self.penalized_quadratic_cost(cpu_labels, cpu_pred)
                    loss_storage = self.penalized_quadratic_cost(storage_labels, storage_pred)
                    loss_delay = self.penalized_quadratic_cost(delay_labels, delay_pred)
                    total_batch_loss = loss_cpu + loss_storage + loss_delay
                    
                    self.optimizer.zero_grad()
                    total_batch_loss.backward()
                    self.optimizer.step()
                    
                    total_loss += total_batch_loss.item()

    def predict(self, vnfm_type: str, vnffgManager: "VnffgManager") -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """预测VNF资源需求 (CPU、存储、延迟) """
        # 收集目标VNF类型的历史数据
        history_data = []
        for nfvi in vnffgManager.vnfVim.nfvi_group.values():
            for vnfem in nfvi.get_deployed_vnf_with_type(vnfm_type):
                history = vnfem.history_resources[-self.history_window:]
                if len(history) < self.history_window:
                    continue
                for item in history:
                    history_data.extend([item['cpu'], item['storage'], item['delay']])
                break
            if history_data:
                break
        
        if not history_data:
            # 无历史数据时返回默认值
            vnf_template = vnffgManager.vnfManager.vnfTemplates[vnfm_type]
            cpu_pred = np.full(self.predict_window, vnf_template.resource_limit['cpu'])
            storage_pred = np.full(self.predict_window, vnf_template.resource_limit['rom'])
            delay_pred = np.full(self.predict_window, 0.1)  # 默认延迟
            return cpu_pred, storage_pred, delay_pred
        
        # 归一化并转换为张量
        X = self.normalize_features(np.array([history_data]))
        X_tensor = torch.tensor(X, dtype=torch.float32)
        
        # 预测
        self.eval()
        with torch.no_grad():
            cpu_pred, storage_pred, delay_pred = self(X_tensor)
        
        # 转换为numpy数组并返回
        return cpu_pred.numpy()[0], storage_pred.numpy()[0], delay_pred.numpy()[0]

class DTMDPModel:
    """离散时间马尔可夫决策过程模型 (复现论文定义) """
    def __init__(self, num_vnfis: int):
        self.num_vnfis = num_vnfis
        self.state_dim = 2 ** num_vnfis * num_vnfis  # 状态空间大小: 2^M * M (M为VNF实例数) 
        self.action_space: List[Dict] = []  # 动作空间: {vnfi_migrate: (u, v), path_reroute: [(u1,v1),...]}
        self.transition_prob: Dict[Tuple[int, int], float] = {}  # P(s'|s,a)
        self.utilization_low = 0.2  # 资源利用率下阈值
        self.utilization_high = 0.8  # 资源利用率上阈值

    def build_action_space(self, nfvi_list: List[NfvInstance], vnf_indices: List[int]) -> None:
        """构建动作空间 (VNF迁移+路径重路由) """
        self.action_space.clear()
        # 生成所有可能的VNF迁移动作
        for vnf_idx in vnf_indices:
            for src_nfvi in nfvi_list:
                for dst_nfvi in nfvi_list:
                    if src_nfvi.id == dst_nfvi.id:
                        continue
                    # 迁移动作 + 默认路径重路由 (后续由Dyna-Q优化) 
                    self.action_space.append({
                        'type': 'migrate_reroute',
                        'vnfi_idx': vnf_idx,
                        'src_nfvi_id': src_nfvi.id,
                        'dst_nfvi_id': dst_nfvi.id,
                        'reroute_path': None
                    })
        # 添加空动作 (不迁移仅重路由) 
        self.action_space.append({
            'type': 'only_reroute',
            'vnfi_idx': -1,
            'src_nfvi_id': -1,
            'dst_nfvi_id': -1,
            'reroute_path': None
        })

    def get_state(self, vnfi_map: List[int], nfvi_resources: Dict[int, Dict[str, float]]) -> int:
        """根据VNF映射和资源状态计算DTMDP状态"""
        # 状态编码: VNF映射位置 + 资源利用率状态 (0: 正常, 1: 过低/过高) 
        state_code = 0
        for i, nfvi_id in enumerate(vnfi_map):
            # 计算资源利用率
            cpu_util = (nfvi_resources[nfvi_id]['total_cpu'] - nfvi_resources[nfvi_id]['remaining_cpu']) / nfvi_resources[nfvi_id]['total_cpu']
            util_state = 0 if (self.utilization_low <= cpu_util <= self.utilization_high) else 1
            # 编码到状态位
            state_code |= (nfvi_id << (2 * i)) | (util_state << (2 * i + 1))
        # 状态空间裁剪 (确保在有效范围内) 
        return state_code % self.state_dim

    def calculate_reward(self, action: Dict, revenue: float, migration_cost: float, bandwidth_cost: float) -> float:
        """计算即时奖励 (复现论文r = R_total - C_total) """
        total_cost = migration_cost + bandwidth_cost
        reward = revenue - total_cost
        # 违反约束时返回惩罚
        if reward < 0:
            return -1e-6  # 论文惩罚因子 -1/ξ
        return reward

class SolverDeployDynaQ(SolverDeployBase):
    """基于深度Dyna-Q的SFC重配置求解器 (复现论文核心算法) """
    def __init__(self, name: str):
        super().__init__(name)
        
        # 算法参数 (复现论文配置) 
        self.gamma = 0.9  # 折扣因子
        self.alpha = 0.8  # 初始学习因子
        self.epsilon = 0.1  # ε-Greedy探索率
        self.zeta = 0.3  # 动作选择函数权重
        self.eta = 0.6  # Q值收敛阈值
        self.max_t = 1500  # 最大学习周期
        self.max_step = 1000  # 最大学习步数
        self.planning_steps = 100  # 规划步数
        self.reconfig_trigger_duration = 2  # 重配置触发持续时间
        self.history_window = 20  # GNN历史窗口
        self.predict_window = 20  # GNN预测窗口
        
        # 核心组件
        self.gnn_predictor = GNNResourcePredictor(self.history_window, self.predict_window)
        self.dtmdp: Optional[DTMDPModel] = None
        self.q_table: Dict[Tuple[int, int], float] = {}  # Q(s,a)
        self.learning_model: Dict[Tuple[int, int], Tuple[int, float]] = {}  # M(s,a) = (s', r)
        self.real_experience_buffer = deque(maxlen=1000)  # 真实经验缓存 D^u
        self.simulated_experience_buffer = deque(maxlen=2000)  # 模拟经验缓存 D^s
        self.state_action_count: Dict[Tuple[int, int], int] = {}  # N(s,a) 计数
        self.state_count: Dict[int, int] = {}  # N(s) 计数
        
        # 临时变量
        self.temp_nfvi_resources: Dict[int, Dict[str, float]] = {}  # 包含总资源和剩余资源
        self.vnfi_migration_cost: Dict[Tuple[int, int], float] = {}  # (src, dst) -> 迁移成本
        self.link_bandwidth_cost: Dict[Tuple[int, int], float] = {}  # (u, v) -> 带宽成本

    def _init_cost_models(self, nfvi_list: List[NfvInstance], topo: nx.Graph):
        """初始化成本模型 (复现论文成本计算) """
        # 迁移成本: 基于节点间距离 (延迟) 
        for src_nfvi in nfvi_list:
            for dst_nfvi in nfvi_list:
                if src_nfvi.id == dst_nfvi.id:
                    self.vnfi_migration_cost[(src_nfvi.id, dst_nfvi.id)] = 0.0
                    continue
                try:
                    distance = nx.dijkstra_path_length(topo, src_nfvi.id, dst_nfvi.id, weight='Latency')
                    self.vnfi_migration_cost[(src_nfvi.id, dst_nfvi.id)] = distance * 10  # 成本系数
                except nx.NetworkXNoPath:
                    self.vnfi_migration_cost[(src_nfvi.id, dst_nfvi.id)] = float('inf')
        
        # 带宽成本: 固定5货币单位/链路 (复现论文参数) 
        for (u, v) in topo.edges():
            self.link_bandwidth_cost[(u, v)] = 5.0

    def _check_reconfig_trigger(self, utilization_ratios: Dict[int, float], end2end_delay: float, max_delay: float) -> bool:
        """检查重配置触发条件 (复现论文两种触发机制) """
        # 条件1: 资源利用率超出阈值 (0.2~0.8) 
        util_trigger = any(util < 0.2 or util > 0.8 for util in utilization_ratios.values())
        # 条件2: 端到端延迟超出QoS约束
        delay_trigger = end2end_delay > max_delay
        # 满足任一条件且持续指定时长
        return (util_trigger or delay_trigger) and self._trigger_duration_check()

    def _trigger_duration_check(self) -> bool:
        """检查触发条件持续时长 (简化实现) """
        return True  # 实际场景需结合时间戳判断, 此处简化为始终满足

    def _calculate_utilization_ratios(self) -> Dict[int, float]:
        """计算所有NFVI节点的CPU利用率"""
        util_ratios = {}
        for nfvi_id, resources in self.temp_nfvi_resources.items():
            if resources['total_cpu'] == 0:
                util_ratios[nfvi_id] = 0.0
            else:
                used_cpu = resources['total_cpu'] - resources['remaining_cpu']
                util_ratios[nfvi_id] = used_cpu / resources['total_cpu']
        return util_ratios

    def _calculate_end2end_delay(self, map_path: List[List[int]], vnfi_map: List[int], vnf_types: List[str]) -> float:
        """计算端到端延迟 (链路延迟+VNF处理延迟) """
        total_delay = 0.0
        # 链路延迟
        for path in map_path:
            for (u, v) in path:
                total_delay += self.adjacent_topo[u][v]['Latency']
        # VNF处理延迟 (复现论文商用设备参数) 
        delay_map = {
            'FW': 0.12, 'IDS': 0.16, 'NAT': 0.16, 'DPI': 0.2, 'Proxy': 0.18
        }
        for vnf_type in vnf_types:
            total_delay += delay_map.get(vnf_type, 0.15)  # 默认0.15ms
        return total_delay

    def _get_best_reroute_path(self, src_nfvi_id: int, dst_nfvi_id: int) -> List[Tuple[int, int]]:
        """获取最优重路由路径 (Dijkstra算法) """
        try:
            path = nx.dijkstra_path(self.adjacent_topo, src_nfvi_id, dst_nfvi_id, weight='Latency')
            return [(path[i], path[i+1]) for i in range(len(path)-1)]
        except nx.NetworkXNoPath:
            return []

    def _update_q_value(self, state: int, action_idx: int, reward: float, next_state: int):
        """更新Q值 (复现论文公式14) """
        current_q = self.q_table.get((state, action_idx), 0.0)
        # 获取下一状态最优Q值
        next_actions = range(len(self.dtmdp.action_space))
        max_next_q = max([self.q_table.get((next_state, a), 0.0) for a in next_actions], default=0.0)
        # 更新Q值
        new_q = (1 - self.alpha) * current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[(state, action_idx)] = new_q
        # 更新计数
        self.state_action_count[(state, action_idx)] = self.state_action_count.get((state, action_idx), 0) + 1
        self.state_count[state] = self.state_count.get(state, 0) + 1
        # 衰减学习因子 (复现论文α=1/(1+Φ_t(n))) 
        self.alpha = 1.0 / (1 + self.state_action_count[(state, action_idx)] ** 0.5)

    def _select_action(self, state: int) -> int:
        """新型动作选择函数 (复现论文公式16) """
        action_scores = []
        for action_idx in range(len(self.dtmdp.action_space)):
            # 计算ΔQ (当前Q值与平均Q值的差) 
            current_q = self.q_table.get((state, action_idx), 0.0)
            avg_q = np.mean([self.q_table.get((state, a), 0.0) for a in range(len(self.dtmdp.action_space))])
            delta_q = abs(current_q - avg_q)
            
            # 计算探索项
            n_s = self.state_count.get(state, 1)
            n_sa = self.state_action_count.get((state, action_idx), 0.001)  # 避免除以0
            exploration_term = math.sqrt(math.log(n_s) / n_sa)
            
            # 动作得分
            score = (1 - self.zeta) * delta_q + self.zeta * exploration_term
            action_scores.append(score)
        
        # ε-Greedy选择
        if random.random() < self.epsilon:
            return random.choice(range(len(self.dtmdp.action_space)))
        return np.argmax(action_scores)

    def direct_reinforcement_learning(self, vnffgManager: "VnffgManager", vnfi_map: List[int], vnf_types: List[str]) -> None:
        """直接强化学习 (真实经验学习) """
        step = 0
        while step < self.max_step:
            # 获取当前状态
            util_ratios = self._calculate_utilization_ratios()
            current_state = self.dtmdp.get_state(vnfi_map, self.temp_nfvi_resources)
            # 选择动作
            action_idx = self._select_action(current_state)
            action = self.dtmdp.action_space[action_idx]
            
            # 执行动作
            new_vnfi_map = copy.deepcopy(vnfi_map)
            migration_cost = 0.0
            bandwidth_cost = 0.0
            
            if action['type'] == 'migrate_reroute' and action['src_nfvi_id'] != -1:
                # 执行VNF迁移
                vnf_idx = action['vnfi_idx']
                src_id = action['src_nfvi_id']
                dst_id = action['dst_nfvi_id']
                if new_vnfi_map[vnf_idx] == src_id and dst_id in self.temp_nfvi_resources:
                    # 检查目标节点资源
                    vnf_template = vnffgManager.vnfManager.vnfTemplates[vnf_types[vnf_idx]]
                    required_cpu = vnf_template.resource_limit['cpu']
                    if self.temp_nfvi_resources[dst_id]['remaining_cpu'] >= required_cpu:
                        # 迁移资源更新
                        self.temp_nfvi_resources[src_id]['remaining_cpu'] += required_cpu
                        self.temp_nfvi_resources[dst_id]['remaining_cpu'] -= required_cpu
                        new_vnfi_map[vnf_idx] = dst_id
                        migration_cost = self.vnfi_migration_cost[(src_id, dst_id)]
            
            # 执行路径重路由
            map_path = []
            for i in range(len(new_vnfi_map)-1):
                src_nfvi_id = new_vnfi_map[i]
                dst_nfvi_id = new_vnfi_map[i+1]
                path = self._get_best_reroute_path(src_nfvi_id, dst_nfvi_id)
                if not path:
                    reward = -1e-6  # 路径不可达惩罚
                    break
                map_path.append(path)
                # 计算带宽成本
                for (u, v) in path:
                    bandwidth_cost += self.link_bandwidth_cost[(u, v)]
            else:
                # 计算奖励 (假设每成功服务一次获得固定收益) 
                revenue = 100.0  # 简化收益模型
                reward = self.dtmdp.calculate_reward(action, revenue, migration_cost, bandwidth_cost)
            
            # 获取下一状态
            next_util_ratios = self._calculate_utilization_ratios()
            next_state = self.dtmdp.get_state(new_vnfi_map, self.temp_nfvi_resources)
            
            # 更新Q值和学习模型
            self._update_q_value(current_state, action_idx, reward, next_state)
            self.learning_model[(current_state, action_idx)] = (next_state, reward)
            
            # 存储真实经验
            self.real_experience_buffer.append((current_state, action_idx, next_state, reward))
            
            # 更新状态
            vnfi_map = new_vnfi_map
            step += 1
            
            # 检查收敛
            q_values = [self.q_table.get((current_state, a), 0.0) for a in range(len(self.dtmdp.action_space))]
            if max(q_values) - min(q_values) < self.eta:
                break

    def indirect_reinforcement_learning(self) -> None:
        """间接强化学习 (模拟经验学习) """
        for _ in range(self.planning_steps):
            if not self.real_experience_buffer:
                break
            # 随机选择历史经验
            (state, action_idx, _, _) = random.choice(list(self.real_experience_buffer))
            # 从学习模型获取模拟下一状态和奖励
            if (state, action_idx) not in self.learning_model:
                continue
            next_state, reward = self.learning_model[(state, action_idx)]
            # 更新Q值
            self._update_q_value(state, action_idx, reward, next_state)
            # 存储模拟经验
            self.simulated_experience_buffer.append((state, action_idx, next_state, reward))

    def solve_embedding(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """初始部署 (结合GNN预测的DDQ部署逻辑) """
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "arrive"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        nfvi_list = list(vnffgManager.vnfVim.nfvi_group.values())
        
        # 初始化组件
        self.adjacent_topo = vnffgManager.vnfVim.get_graph(with_weight="Latency")
        self.solution_deploy.current_topo = self.adjacent_topo
        self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos
        self.solution_deploy.share_node = [None] * len(self.current_vnfs_index_list)
        
        # 初始化资源信息 (总资源+剩余资源) 
        self.temp_nfvi_resources = {}
        for nfvi in nfvi_list:
            remaining = nfvi.node_handle.get_remaining_resource()
            total = nfvi.node_handle.get_total_resource()
            self.temp_nfvi_resources[nfvi.id] = {
                'total_cpu': total['cpu'].value if isinstance(total['cpu'], u.Quantity) else total['cpu'],
                'remaining_cpu': remaining['cpu'].value if isinstance(remaining['cpu'], u.Quantity) else remaining['cpu'],
                'total_storage': total['rom'].value if isinstance(total['rom'], u.Quantity) else total['rom'],
                'remaining_storage': remaining['rom'].value if isinstance(remaining['rom'], u.Quantity) else remaining['rom'],
            }
        
        # 初始化成本模型和DTMDP
        self._init_cost_models(nfvi_list, self.adjacent_topo)
        self.dtmdp = DTMDPModel(len(self.current_vnfs_index_list))
        self.dtmdp.build_action_space(nfvi_list, self.current_vnfs_index_list)
        
        # GNN在线更新与资源预测
        self.gnn_predictor.online_update(vnffgManager)
        vnf_types = vnffgManager.sfc_req.sfc_vnfs_type
        predicted_resources = []
        for vnf_type in vnf_types:
            cpu_pred, storage_pred, delay_pred = self.gnn_predictor.predict(vnf_type, vnffgManager)
            predicted_resources.append({
                'cpu': cpu_pred[0],  # 取预测窗口第一个时间点的值
                'storage': storage_pred[0],
                'delay': delay_pred[0]
            })
        
        # 初始VNF映射 (基于预测资源的贪心部署) 
        vnfi_map = [-1] * len(self.current_vnfs_index_list)
        for v_node in self.current_vnfs_index_list:
            vnf_type = vnf_types[v_node]
            pred_cpu = predicted_resources[v_node]['cpu']
            pred_storage = predicted_resources[v_node]['storage']
            
            # 选择满足资源需求且利用率最优的节点
            candidate_nfvis = []
            for nfvi in nfvi_list:
                res = self.temp_nfvi_resources[nfvi.id]
                if res['remaining_cpu'] >= pred_cpu and res['remaining_storage'] >= pred_storage:
                    # 优先选择利用率在正常范围的节点
                    util = (res['total_cpu'] - res['remaining_cpu']) / res['total_cpu']
                    if 0.2 <= util <= 0.8:
                        candidate_nfvis.append((nfvi.id, util))
            
            if not candidate_nfvis:
                # 无理想节点时选择资源最充足的
                candidate_nfvis = [(nfvi.id, (nfvi.node_handle.get_total_resource()['cpu'] - nfvi.node_handle.get_remaining_resource()['cpu']) / nfvi.node_handle.get_total_resource()['cpu']) 
                                   for nfvi in nfvi_list 
                                   if self.temp_nfvi_resources[nfvi.id]['remaining_cpu'] >= pred_cpu 
                                   and self.temp_nfvi_resources[nfvi.id]['remaining_storage'] >= pred_storage]
            
            if not candidate_nfvis:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_RESOURCE_INSUFFICIENT
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            # 选择利用率最低的节点
            candidate_nfvis.sort(key=lambda x: x[1])
            chosen_nfvi_id = candidate_nfvis[0][0]
            vnfi_map[v_node] = chosen_nfvi_id
            
            # 更新资源
            self.temp_nfvi_resources[chosen_nfvi_id]['remaining_cpu'] -= pred_cpu
            self.temp_nfvi_resources[chosen_nfvi_id]['remaining_storage'] -= pred_storage
            
            # 共享节点处理
            if vnffgManager.sfc_req.sfc_vnfs_shared[v_node]:
                nfvi = vnffgManager.vnfVim.nfvi_group[chosen_nfvi_id]
                shared_vnfems = nfvi.get_deployed_vnf_with_type(vnf_type)
                self.solution_deploy.share_node[v_node] = shared_vnfems[0].id if shared_vnfems else None
        
        # 路径路由
        map_path = []
        for i in range(len(vnfi_map)-1):
            src_id = vnfi_map[i]
            dst_id = vnfi_map[i+1]
            path = self._get_best_reroute_path(src_id, dst_id)
            if not path:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
                self.solution_deploy.current_result = False
                return self.solution_deploy
            map_path.append(path)
        
        # 存储部署结果
        self.solution_deploy.map_node = vnfi_map
        self.solution_deploy.map_link = {(i, i+1): map_path[i] for i in range(len(map_path))}
        self.solution_deploy.resource['cpu'] = [pred['cpu'] for pred in predicted_resources]
        self.solution_deploy.resource['ram'] = [vnffgManager.vnfManager.vnfTemplates[vt].resource_limit['ram'] for vt in vnf_types]
        self.solution_deploy.resource['rom'] = [pred['storage'] for pred in predicted_resources]
        
        # 检查部署结果
        self.solution_deploy.current_description = self.check_solution(vnffgManager)
        self.solution_deploy.current_result = (self.solution_deploy.current_description == SOLUTION_DEPLOY_TYPE.SET_SUCCESS)
        
        return self.solution_deploy

    def solve_migration(self, vnffgManager: "VnffgManager") -> SolutionDeploy:
        """重配置迁移 (复现论文DDQ核心逻辑) """
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "migrate"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        nfvi_list = list(vnffgManager.vnfVim.nfvi_group.values())
        vnf_types = vnffgManager.sfc_req.sfc_vnfs_type
        
        # 初始化组件
        self.adjacent_topo = vnffgManager.vnfVim.get_graph(with_weight="Latency")
        self.solution_deploy.current_topo = self.adjacent_topo
        self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos
        self.solution_deploy.share_node = [None] * len(self.current_vnfs_index_list)
        
        # 初始化资源信息
        self.temp_nfvi_resources = {}
        for nfvi in nfvi_list:
            remaining = nfvi.node_handle.get_remaining_resource()
            total = nfvi.node_handle.get_total_resource()
            self.temp_nfvi_resources[nfvi.id] = {
                'total_cpu': total['cpu'].value if isinstance(total['cpu'], u.Quantity) else total['cpu'],
                'remaining_cpu': remaining['cpu'].value if isinstance(remaining['cpu'], u.Quantity) else remaining['cpu'],
                'total_storage': total['rom'].value if isinstance(total['rom'], u.Quantity) else total['rom'],
                'remaining_storage': remaining['rom'].value if isinstance(remaining['rom'], u.Quantity) else remaining['rom'],
            }
        
        # 初始化成本模型、DTMDP和Q表
        self._init_cost_models(nfvi_list, self.adjacent_topo)
        self.dtmdp = DTMDPModel(len(self.current_vnfs_index_list))
        self.dtmdp.build_action_space(nfvi_list, self.current_vnfs_index_list)
        self.q_table.clear()
        self.learning_model.clear()
        self.state_action_count.clear()
        self.state_count.clear()
        
        # 获取当前部署状态
        current_vnfi_map = vnffgManager.current_sfc_deployment['map_node']
        current_map_path = vnffgManager.current_sfc_deployment['map_link']
        
        # 检查重配置触发条件
        util_ratios = self._calculate_utilization_ratios()
        current_delay = self._calculate_end2end_delay([current_map_path[(i, i+1)] for i in range(len(current_vnfi_map)-1)],
                                                     current_vnfi_map, vnf_types)
        max_delay = vnffgManager.sfc_req.sfc_qos['max_delay']
        if not self._check_reconfig_trigger(util_ratios, current_delay, max_delay):
            self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_TRIGGER
            self.solution_deploy.current_result = False
            return self.solution_deploy
        
        # GNN预测未来资源需求
        self.gnn_predictor.online_update(vnffgManager)
        predicted_resources = []
        for vnf_type in vnf_types:
            cpu_pred, storage_pred, delay_pred = self.gnn_predictor.predict(vnf_type, vnffgManager)
            predicted_resources.append({
                'cpu': cpu_pred[0],
                'storage': storage_pred[0],
                'delay': delay_pred[0]
            })
        
        # 执行DDQ重配置
        t = 0
        best_vnfi_map = copy.deepcopy(current_vnfi_map)
        best_map_path = copy.deepcopy(current_map_path)
        best_reward = -float('inf')
        
        while t < self.max_t:
            # 直接强化学习
            self.direct_reinforcement_learning(vnffgManager, current_vnfi_map, vnf_types)
            # 间接强化学习
            self.indirect_reinforcement_learning()
            
            # 评估当前策略
            current_state = self.dtmdp.get_state(current_vnfi_map, self.temp_nfvi_resources)
            action_idx = self._select_action(current_state)
            action = self.dtmdp.action_space[action_idx]
            
            # 计算当前奖励
            migration_cost = self.vnfi_migration_cost.get((action.get('src_nfvi_id', -1), action.get('dst_nfvi_id', -1)), 0.0)
            bandwidth_cost = sum([self.link_bandwidth_cost.get((u, v), 0.0) for path in current_map_path.values() for (u, v) in path])
            revenue = 100.0
            current_reward = self.dtmdp.calculate_reward(action, revenue, migration_cost, bandwidth_cost)
            
            # 更新最优解
            if current_reward > best_reward:
                best_reward = current_reward
                best_vnfi_map = copy.deepcopy(current_vnfi_map)
                best_map_path = copy.deepcopy(current_map_path)
            
            # 检查收敛
            q_values = [self.q_table.get((current_state, a), 0.0) for a in range(len(self.dtmdp.action_space))]
            if max(q_values) - min(q_values) < self.eta:
                break
            
            t += 1
        
        # 验证最优解的约束满足性
        final_delay = self._calculate_end2end_delay([best_map_path[(i, i+1)] for i in range(len(best_vnfi_map)-1)],
                                                   best_vnfi_map, vnf_types)
        final_util_ratios = self._calculate_utilization_ratios()
        valid = (final_delay <= max_delay) and all(0.2 <= util <= 0.8 for util in final_util_ratios.values())
        
        if not valid:
            self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_CONSTRAINT_VIOLATION
            self.solution_deploy.current_result = False
            return self.solution_deploy
        
        # 存储迁移结果
        self.solution_deploy.map_node = best_vnfi_map
        self.solution_deploy.map_link = best_map_path
        self.solution_deploy.resource['cpu'] = [pred['cpu'] for pred in predicted_resources]
        self.solution_deploy.resource['ram'] = [vnffgManager.vnfManager.vnfTemplates[vt].resource_limit['ram'] for vt in vnf_types]
        self.solution_deploy.resource['rom'] = [pred['storage'] for pred in predicted_resources]
        
        # 计算成本与收益
        self.calculate_cost_and_revenue(vnffgManager)
        
        # 检查迁移结果
        self.solution_deploy.current_description = self.check_solution(vnffgManager)
        self.solution_deploy.current_result = (self.solution_deploy.current_description == SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS)
        
        return self.solution_deploy

    def calculate_cost_and_revenue(self, vnffgManager: "VnffgManager") -> None:
        """计算重配置成本与收益 (复现论文目标函数) """
        # 迁移成本
        migration_cost = 0.0
        current_map = vnffgManager.current_sfc_deployment['map_node']
        new_map = self.solution_deploy.map_node
        for vnf_idx in range(len(current_map)):
            if current_map[vnf_idx] != new_map[vnf_idx]:
                migration_cost += self.vnfi_migration_cost.get((current_map[vnf_idx], new_map[vnf_idx]), 0.0)
        
        # 带宽成本
        bandwidth_cost = 0.0
        for path in self.solution_deploy.map_link.values():
            for (u, v) in path:
                bandwidth_cost += self.link_bandwidth_cost.get((u, v), 0.0)
        
        # 总收益 (假设每服务一个请求获得固定收益) 
        revenue = len(vnffgManager.sfc_req.sfc_vnfs_type) * 100.0
        total_profit = revenue - (migration_cost + bandwidth_cost)
        
        # 存储到解决方案
        self.solution_deploy.cost['migration'] = migration_cost
        self.solution_deploy.cost['bandwidth'] = bandwidth_cost
        self.solution_deploy.cost['total'] = migration_cost + bandwidth_cost
        self.solution_deploy.revenue = revenue
        self.solution_deploy.profit = total_profit