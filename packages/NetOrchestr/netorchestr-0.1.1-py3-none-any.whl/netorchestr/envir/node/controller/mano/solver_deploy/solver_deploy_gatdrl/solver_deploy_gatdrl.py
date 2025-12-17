#Anaconda/envs/pyqtenv python
# -*- coding: utf-8 -*-
'''
solver_deploy_gatdrl.py
=======================

.. module:: solver_deploy_gatdrl
  :platform: Windows
  :synopsis: 基于 GAT (图注意力网络) 的 SFC 编排求解器模块, 用于在支持 VNF 共享的网络环境中, 实现虚拟网络功能 (VNF) 向物理设施节点 (NFVI) 的智能嵌入部署

.. moduleauthor:: WangXi

简介
----

该模块实现了融合 Encoder-Decoder 架构的 Actor-Critic 强化学习模型, 专门用于服务功能链 (SFC) 的微服务实例部署优化。
核心逻辑是通过 GAT 网络深度挖掘物理网络 (p_net) 的空间结构特征与虚拟网络 (v_net) 的请求特征，结合时序建模与注意力机制，实现高效、前瞻性的 VNF 嵌入决策。
它提供了以下特性：

- 使用 GAT 网络提取物理网络节点特征，适配含时间聚合链路（未来时延序列）的动态拓扑，同时支持 VNF 共享状态感知；
- 采用 Encoder-Decoder 架构, Encoder 通过 GRU 与注意力机制捕捉虚拟网络请求的时序关联与关键信息, Decoder 结合 GRU 时序建模与 MLP 输出部署决策；
- 支持动态维度边特征处理，通过补全机制适配不同时间聚合链路的采样点数量，确保批量训练的兼容性；
- 融入物理节点资源状态 (最大 / 剩余 CPU、内存、带宽) 与 VNF 共享信息 (共享标记), 提升决策的合理性与资源利用率；
- 基于 Actor-Critic 框架, Actor 输出 VNF 嵌入位置的概率分布, Critic 评估当前部署状态价值，实现稳定高效的强化学习训练.

版本
----

- 版本 1.0 (2025/11/11): 初始版本，集成 GAT 特征提取、时序注意力机制、VNF 共享支持与动态边特征适配功能

'''


import os
import networkx as nx
import numpy as np

from astropy import units as u
from netorchestr.envir.node.controller.mano.solver_deploy import SolutionDeploy, SolverDeployBase, SOLUTION_DEPLOY_TYPE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import VnffgManager

from netorchestr.envir.node.controller.mano.solver_deploy.solver_deploy_gatdrl.train_env import TrainEnv, TrainSolution
from netorchestr.envir.node.controller.mano.solver_deploy.solver_deploy_gatdrl.train_net import ActorCritic, apply_mask_to_logit
from netorchestr.envir.node.controller.mano.solver_deploy.solver_deploy_gatdrl.buffer import RolloutBuffer
from netorchestr.envir.node.controller.mano.solver_deploy.solver_deploy_gatdrl.train_tracer import SolverTracer

import torch
import torch.nn.functional as F
from torch.distributions import Categorical
import networkx as nx

class SolverDeployGatDrl(SolverDeployBase):
    """基于 GAT (图注意力网络) 的 SFC 编排求解器模块"""
    def __init__(self, name:str, **kwargs) -> None:
        super().__init__(name)

        self.use_cuda = kwargs.get('use_cuda', True)
        if self.use_cuda and torch.cuda.is_available():
            print(f'INFO: {self.__class__.__name__} is using CUDA GPU')
            self.device = torch.device('cuda:0')
        else:
            print(f'INFO: {self.__class__.__name__} is using CPU')
            self.device = torch.device('cpu')
            
        self.policy = None
        self.optimizer = None
        
        self.work_mode:str = kwargs.get('work_mode', 'train')
        """工作模式设置, 可选 'train' 或 'validate', 决定了智能体处于训练模式或验证模式"""
        
    def ready_for_controller(self, nfvOrchestrator):
        super().ready_for_controller(nfvOrchestrator)
        
        self.buffer = RolloutBuffer()
        
        p_net_num_nodes = len(nfvOrchestrator.vnfVim.nfvi_group)

        self.policy = ActorCritic(p_net_num_nodes=p_net_num_nodes, 
                                  p_net_feature_dim=7, 
                                  v_net_feature_dim=3, 
                                  embedding_dim=64).to(self.device)
        
        self.optimizer = torch.optim.Adam([
                {'params': self.policy.actor.parameters(), 'lr': 0.005},
                {'params': self.policy.critic.parameters(), 'lr': 0.001},
            ],
        )
        
        print(f"INFO: {self.__class__.__name__} 处于工作模式 {self.work_mode}")

        self.tracer = SolverTracer(save_dir=nfvOrchestrator.vnfVim.net.logger.log_dir,
                                   save_id=nfvOrchestrator.vnfVim.net.logger.sim_id,
                                   solver_name=self.name)
        
    def select_action(self, observation, mask=None, sample=True):
        """策略网络 Policy Network 的核心执行函数, 根据当前的观测 observation 和可选动作掩码 mask, 生成一个动作 action 并计算该动作的对数概率 action_logprob

        Args:
            observation (dict): 环境的当前观测，包含了智能体做出决策所需的所有信息
            
                {
                    'p_net': p_net_obs, # PyTorch Geometric 单图数据结构, 类型为 Batch, 包含节点特征、边索引、边属性等信息, 类型为 Data
                    'p_net_node': p_net_node, # 节点个数, 类型为 LongTensor, 形状为 (1,)
                    'hidden_state': hidden_state, # 循环神经网络 GRU 输出的隐藏状态, 类型为 FloatTensor, 形状为 (1, 1, embedding_dim)
                    'encoder_outputs': encoder_outputs # 编码器输出, 类型为 FloatTensor, 形状为 (1, v_node_num, embedding_dim)
                }
            
            mask (torch.Tensor, optional): 动作掩码, 是一个布尔型或浮点型的张量, 屏蔽掉在当前状态下不可行的动作. Defaults to None.
            
            sample (bool, optional): 一个布尔值，决定了动作的选择方式. Defaults to True.
            
                sample=True: 从概率分布中采样一个动作, 保证探索 Exploration
                
                sample=False: 选择概率最高的动作 argmax, 让智能体执行一个 “贪婪” 策略，在测试或评估时使用

        Returns:
            tuple: 包含动作 action 和动作的对数概率 action_logprob 的元组:     
            action (numpy.ndarray): 动作, 类型为 numpy.ndarray, 形状为 (1,)
            action_logprob (numpy.ndarray): 动作的对数概率, 类型为 numpy.ndarray, 形状为 (1,)
        """
        
        with torch.no_grad():
            # 一个上下文管理器，它会临时关闭 PyTorch 的自动求导机制。
            # select_action 是在与环境交互时执行的，只需要前向传播来得到动作，不需要计算梯度，这样可以大大节省计算资源和时间。
            action_logits = self.policy.act(observation)

        if mask is not None:
            candicate_action_logits = apply_mask_to_logit(action_logits, mask) 
            # 激活函数将 candicate_action_logits（经过掩码处理的对数几率）转换为概率分布 candicate_action_probs
            # dim=-1 表示在最后一个维度（即动作维度）上进行归一化，确保所有动作的概率之和为 1
            candicate_action_probs = F.softmax(candicate_action_logits, dim=-1)
            #  PyTorch torch.distributions 模块中的类, 创建了一个分类分布的实例。权重由 candicate_action_probs 决定。
            # 这个分布对象提供了 .sample() 和 .log_prob() 等方法。
            candicate_action_dist = Categorical(probs=candicate_action_probs)
        else:
            candicate_action_logits = action_logits
            candicate_action_probs = F.softmax(action_logits, dim=-1)
            candicate_action_dist = Categorical(probs=candicate_action_probs)

        if sample:
            # 根据概率分布随机采样一个动作
            action = candicate_action_dist.sample()
        else:
            # 选择概率最高的动作
            action = candicate_action_logits.argmax(-1)

        # 计算动作的对数概率
        # 无论动作是采样得到的还是贪婪选择的，都需要计算这个具体动作在当前策略下发生的对数概率
        # 这个值在强化学习的策略梯度（Policy Gradient）算法中至关重要，用作更新策略网络参数的权重。
        # 使得回报（Reward）高的动作的对数概率增大，使得回报低的动作的对数概率减小。
        action_logprob = candicate_action_dist.log_prob(action)
        
        # 格式化输出
        # 将动作张量展平成一个一维向量，以统一输出格式，无论 batch_size 是多少
        action = action.reshape(-1, )
        
        # 将张量从计算图中分离出来, 将张量从 GPU 移动到 CPU, 将其转换为 NumPy 数组
        return action.cpu().detach().numpy(), action_logprob.cpu().detach().numpy()
    

    def merge_experience(self,train_solution:TrainSolution,subbuffer:RolloutBuffer):
        if train_solution.result == True:
            subbuffer.compute_mc_returns(gamma=0.95)
            self.buffer.merge(subbuffer)
        else:
            pass
    
    def update(self):
        """智能体训练与参数更新

        Returns:
            loss: 训练过程中的损失函数值, 类型为 float
        """
        # 1. 数据预处理：将缓冲区数据转为模型可训练的张量
        
        # 观测数据：调用 p_net_obs_to_tensor 转为 PyTorch 张量（适配图网络格式）
        observations = TrainEnv.p_net_obs_to_tensor(self.buffer.observations, self.device)
        # 动作：拼接所有动作并转为长整型张量（LongTensor 适配分类任务）
        actions = torch.LongTensor(np.concatenate(self.buffer.actions, axis=0)).to(self.device)
        # 折扣回报：转为浮点张量（作为 Critic 的目标值）
        returns = torch.FloatTensor(self.buffer.returns).to(self.device)
        # 动作掩码：拼接掩码（若有），用于过滤不可行动作
        if len(self.buffer.action_mask) != 0:
            masks = torch.IntTensor(np.concatenate(self.buffer.action_mask, axis=0)).to(self.device)
        else:
            masks = None


        # 2. 模型前向计算：评估动作价值与概率
        
        values, action_logprobs, dist_entropy, other = self.evaluate_actions(observations, actions, masks=masks, return_others=True)

        # 3. 损失函数计算：分别优化 Actor、Critic 和探索性
        
        # 优势函数（Advantage）计算, 衡量 “动作实际回报比预期好多少”——returns 是真实折扣回报，values.detach() 是 Critic 预测的价值（detach() 避免更新 Critic 时影响 Actor）
        advantages = returns - values.detach()
        # 标准化处理：减去均值、除以标准差（+1e-8 避免除零），让优势函数分布更稳定，加速训练收敛。
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        # Actor 损失（策略损失）, 最大化优势大的动作的概率，最小化优势小的动作的概率
        #   若 advantages > 0（动作比预期好）：-logprob * 正数 → 损失减小，模型会增加该动作的概率
        #   若 advantages < 0（动作比预期差）：-logprob * 负数 → 损失增加，模型会减少该动作的概率
        actor_loss = - (action_logprobs * advantages).mean()
        # Critic 损失（价值预测损失）,训练 Critic 让预测价值 values 尽可能接近真实折扣回报 returns, 用 MSE（均方误差）作为损失函数，符合回归任务的优化目标（价值预测是连续值回归）
        critic_loss = F.mse_loss(returns, values)
        # 熵损失（探索鼓励项）, 熵越大，动作分布越均匀（智能体更愿意探索）；熵越小，动作分布越集中（智能体越贪婪）。加入熵损失是为了平衡探索和利用，避免智能体过早陷入局部最优。
        entropy_loss = dist_entropy.mean()
        # 总损失, 加权求和通过系数（0.5、0.01）调节各损失的重要性
        loss = actor_loss + 0.5 * critic_loss + 0.01 * entropy_loss

        # 4. 梯度下降更新模型参数
        
        # 清空之前的梯度（避免梯度累积）
        self.optimizer.zero_grad()
        # 反向传播：计算所有参数的梯度
        loss.backward()
        # 梯度裁剪：限制梯度最大范数为 1（防止梯度爆炸，稳定训练）
        torch.nn.utils.clip_grad_norm_(self.policy.parameters(), max_norm=1)
        # 执行梯度下降：更新 Actor 和 Critic 的所有参数
        self.optimizer.step()

        # 5. 训练信息记录与缓冲区清空
        
        # 记录训练过程信息（损失、学习率、回报等），用于后续可视化或日志
        learning_info = {
            'lr': self.optimizer.defaults['lr'],
            'loss/loss': loss.detach().cpu().numpy(),
            'loss/actor_loss': actor_loss.detach().cpu().numpy(),
            'loss/critic_loss': critic_loss.detach().cpu().numpy(),
            'loss/entropy_loss': entropy_loss.detach().cpu().numpy(),
            'value/logprob': action_logprobs.detach().mean().cpu().numpy(),
            'value/return': returns.detach().mean().cpu().numpy()
        }
        # 清空缓冲区，为下一轮数据存储做准备
        self.buffer.clear()
        # 记录训练过程信息
        self.tracer.handle_data(None,learning_info)

        return loss
    
    def evaluate_actions(self, old_observations, old_actions, masks=None, return_others=False):
        """

        Args:
            old_observations (_type_): 观测数据
            old_actions (_type_): 动作
            masks (_type_, optional): 折扣回报. Defaults to None.
            return_others (bool, optional): 动作掩码. Defaults to False.

        Returns:
            values: Critic 预测的状态价值，维度 (batch_size, 1)（每个时间步的预测价值）

            action_logprobs: Actor 输出的、智能体实际选择动作的对数概率，维度 (batch_size, 1)（衡量动作的 “置信度”）
            
            dist_entropy: 动作概率分布的熵，维度 (batch_size, 1)（熵越大，动作选择越随机，用于鼓励探索）
            
            other: 其他信息，包括掩码掩盖的动作概率、预测掩码的损失、预测掩码的准确率
        """
        
        
        actions_logits = self.policy.act(old_observations)
        actions_probs = F.softmax(actions_logits / 1, dim=-1)

        if masks is not None:
            candicate_actions_logits = apply_mask_to_logit(actions_logits, masks)
        else:
            candicate_actions_logits = actions_logits

        candicate_actions_probs = F.softmax(candicate_actions_logits, dim=-1)

        dist = Categorical(actions_probs)
        candicate_dist = Categorical(candicate_actions_probs)
        policy_dist = candicate_dist

        action_logprobs = policy_dist.log_prob(old_actions)
        dist_entropy = policy_dist.entropy()

        values = self.policy.evaluate(old_observations).squeeze(-1) if hasattr(self.policy, 'evaluate') else None

        if return_others:
            other = {}
            if masks is not None:
                mask_actions_probs = actions_probs * (~masks.bool())
                other['mask_actions_probs'] = mask_actions_probs.sum(-1).mean()
                if hasattr(self.policy, 'predictor'):
                    predicted_masks_logits = self.policy.predict(old_observations)
                    print(predicted_masks_logits)
                    prediction_loss = F.binary_cross_entropy(predicted_masks_logits, masks.float())
                    other['prediction_loss'] = prediction_loss
                    predicted_masks = torch.where(predicted_masks_logits > 0.5, 1., 0.)
                    correct_count = torch.eq(predicted_masks.bool(), masks.bool()).sum(-1).float().mean(0)
                    acc = correct_count / predicted_masks.shape[-1]
                    print(prediction_loss, correct_count, acc)
            return values, action_logprobs, dist_entropy, other

        return values, action_logprobs, dist_entropy
    
    def learn(self, 
              vnffgManager:"VnffgManager", solution_deploy:SolutionDeploy, 
              nfvi_access_start_mask:list[bool], nfvi_access_end_mask:list[bool], 
              time_aggregated_graph:nx.Graph, shared_node_array_mask:np.ndarray):
        
        self.subbuffer = RolloutBuffer()
    
        self.train_env = TrainEnv(vnffgManager,solution_deploy,time_aggregated_graph,shared_node_array_mask)
        train_env_obs = self.train_env.get_observation()
        train_env_done = False

        v_net_obs_tensor = TrainEnv.v_net_obs_to_tensor(train_env_obs,self.device)
        encoder_outputs = self.policy.encode(v_net_obs_tensor)
        # 移除张量中维度为 1 的第 1 维 batch_size 维得到 (v_node_num, embedding_dim), 将张量移动到 CPU 内存 (NumPy 要求)
        # 将张量从计算图中分离出来不再跟踪其梯度信息, 将 PyTorch 张量转换为 NumPy 数组 (不需要反向传播计算梯度, 节省内存并提高效率)
        encoder_outputs = encoder_outputs.squeeze(1).cpu().detach().numpy()

        train_env_obs = {
            'p_net_x': train_env_obs['p_net_x'], # dim = (p_node_num, p_node_feature_dim)
            'p_net_edge': train_env_obs['p_net_edge'], # dim = (2, p_edge_num)
            'p_net_edge_x': train_env_obs['p_net_edge_x'], # dim = (p_edge_num, p_edge_feature_dim)
            'p_net_node': nfvi_access_start_mask.index(True), # dim = 1 为当前关注的节点，默认从nfvi_access_start_mask中为 True 的节点开始选择
            'hidden_state': self.policy.get_last_rnn_state().squeeze(0).cpu().detach().numpy(), # dim = (1, embedding_dim)
            'encoder_outputs': encoder_outputs # dim = (v_node_num, embedding_dim)
        }

        while not train_env_done:
            
            if self.train_env.curr_v_node_id == 0:
                access_p_node_mask = np.array(nfvi_access_start_mask)
            elif self.train_env.curr_v_node_id == len(self.train_env.v_net.nodes)-1:
                access_p_node_mask = np.array(nfvi_access_end_mask)
            else:
                access_p_node_mask = np.ones(len(self.train_env.p_net.nodes), dtype=bool)
            
            mask = np.expand_dims(self.train_env.mix_action_mask(self.train_env.get_action_mask(),
                                                                 access_p_node_mask), 
                                  axis=0) # dim = (1, p_node_num)
            p_net_obs_tensor = TrainEnv.p_net_obs_to_tensor(train_env_obs,self.device)
            
            action, action_logprob = self.select_action(p_net_obs_tensor, mask=mask, sample=True)
            
            next_train_env_obs, train_env_reward, train_env_done, train_env_info, train_step_result = self.train_env.step(action[0], mask)

            p_node_id = action[0].item() # 更新当前关注的节点（即记录上一个动作作为下一次决策时的状态）
            
            if train_step_result == True and access_p_node_mask[p_node_id] == False:
                print(f'WARNING: action {p_node_id} is not allowed by access_p_node_mask')
    
            value = self.policy.evaluate(p_net_obs_tensor).squeeze(-1).detach().cpu()
            
            self.subbuffer.add(train_env_obs,action,train_env_reward,train_env_done,action_logprob,value=value)
            self.subbuffer.action_mask.append(mask)

            hidden_state = self.policy.get_last_rnn_state()
            next_train_env_obs = {
                'p_net_x': next_train_env_obs['p_net_x'],
                'p_net_edge': next_train_env_obs['p_net_edge'],
                'p_net_edge_x': next_train_env_obs['p_net_edge_x'],
                'p_net_node': p_node_id,
                'hidden_state': hidden_state.squeeze(0).cpu().detach().numpy(),
                'encoder_outputs': encoder_outputs
            }

            if train_env_done:
                break

            train_env_obs = next_train_env_obs


        self.tracer.handle_data(self.train_env,None)

        p_net_obs_tensor = TrainEnv.p_net_obs_to_tensor(train_env_obs,self.device)
        last_value = self.policy.evaluate(p_net_obs_tensor).squeeze(-1).detach().cpu()

        return self.train_env.train_solution, self.subbuffer, last_value
    
    
    def validate(self, 
                 vnffgManager:"VnffgManager", solution_deploy:SolutionDeploy,
                 nfvi_access_start_mask:list[bool], nfvi_access_end_mask:list[bool], 
                 time_aggregated_graph:nx.Graph, shared_node_array_mask:np.ndarray):
        
        self.val_env = TrainEnv(vnffgManager, solution_deploy, time_aggregated_graph, shared_node_array_mask)
        val_env_obs = self.val_env.get_observation()
        val_env_done = False
        
        v_net_obs_tensor = TrainEnv.v_net_obs_to_tensor(val_env_obs,self.device)
        with torch.no_grad():
            encoder_outputs = self.policy.encode(v_net_obs_tensor)
        # 移除张量中维度为 1 的第 1 维 batch_size 维得到 (v_node_num, embedding_dim), 将张量移动到 CPU 内存 (NumPy 要求)
        # 将张量从计算图中分离出来不再跟踪其梯度信息, 将 PyTorch 张量转换为 NumPy 数组 (不需要反向传播计算梯度, 节省内存并提高效率)
        encoder_outputs = encoder_outputs.squeeze(1).cpu().numpy()
    
        val_env_obs = {
            'p_net_x': val_env_obs['p_net_x'],
            'p_net_edge': val_env_obs['p_net_edge'],
            'p_net_edge_x': val_env_obs['p_net_edge_x'],
            'p_net_node': nfvi_access_start_mask.index(True),
            'hidden_state': self.policy.get_last_rnn_state().squeeze(0).cpu().numpy(),
            'encoder_outputs': encoder_outputs
        }
    
        while not val_env_done:
            # 一. 获取掩码并对当前环境状态预处理
            if self.val_env.curr_v_node_id == 0:
                access_p_node_mask = np.array(nfvi_access_start_mask)
            elif self.val_env.curr_v_node_id == len(self.val_env.v_net.nodes)-1:
                access_p_node_mask = np.array(nfvi_access_end_mask)
            else:
                access_p_node_mask = np.ones(len(self.val_env.p_net.nodes), dtype=bool)
                
            mask = np.expand_dims(self.val_env.mix_action_mask(self.val_env.get_action_mask(),
                                                               access_p_node_mask), 
                              axis=0)
            
            p_net_obs_tensor = TrainEnv.p_net_obs_to_tensor(val_env_obs, self.device)
            
            # 二. 获取模型输出动作
            with torch.no_grad():
                train_action, _ = self.select_action(p_net_obs_tensor, mask=mask, sample=True)
            action = train_action
            
            # 三. 执行动作, 环境状态转移, 得到下一个状态
            next_val_env_obs, _, val_env_done, _, val_step_result = self.val_env.step(action[0], mask)
            
            p_node_id = action[0].item() # 更新当前关注的节点 (即记录上一个动作作为下一次决策时的状态) 
            
            if val_step_result == True and access_p_node_mask[p_node_id] == False:
                print(f'WARNING: action {p_node_id} is not allowed by access_p_node_mask')

            if val_env_done:
                break
    
            # 四. 更新环境状态为智能体下一次决策做准备
            hidden_state = self.policy.get_last_rnn_state()
            next_val_env_obs = {
                'p_net_x': next_val_env_obs['p_net_x'],
                'p_net_edge': next_val_env_obs['p_net_edge'],
                'p_net_edge_x': next_val_env_obs['p_net_edge_x'],
                'p_net_node': p_node_id,
                'hidden_state': hidden_state.squeeze(0).cpu().numpy(),
                'encoder_outputs': encoder_outputs
            }
            val_env_obs = next_val_env_obs
        
        self.tracer.handle_data(self.val_env,None)
        
        return self.val_env.train_solution, None, None
    
    
    def get_predict_topo_graphs(self, vnffgManager:"VnffgManager", time_step:u.Quantity = 5*u.min):
        sfc_curr_time = vnffgManager.scheduler.now
        sfc_end_time = vnffgManager.sfc_req.end_time.to(u.ms).value
        sfc_predict_topo_time_list = np.arange(sfc_curr_time, sfc_end_time+(time_step).to(u.ms).value, (time_step).to(u.ms).value)
        sfc_predict_topo_time_list = sfc_predict_topo_time_list * u.ms
        predict_topo_graphs = []
        for time in sfc_predict_topo_time_list:
            predict_topo_graphs.append(vnffgManager.vnfVim.get_graph(time=time, with_weight="Latency"))
        return predict_topo_graphs
    
    def get_time_aggregated_graph(self, vnffgManager:"VnffgManager", time_step:int=5*u.min):
        predict_topo_graphs = self.get_predict_topo_graphs(vnffgManager, time_step)
        
        if predict_topo_graphs == []:
            return None
        
        # 1. 确定全连接图的所有节点
        all_nodes = list(predict_topo_graphs[0].nodes())
        num_nodes = len(all_nodes)
        num_graphs = len(predict_topo_graphs)
        
        # 2. 创建全连接图
        time_aggregated_graph = nx.Graph()
        time_aggregated_graph.add_nodes_from(all_nodes)
        
        # 3. 为新图添加全连接的边，并设置权重列表
        for i in range(num_nodes):
            for j in range(i, num_nodes):
                u = all_nodes[i]
                v = all_nodes[j]

                # 为这对节点创建一个权重列表
                weight_list = []
                for g in predict_topo_graphs:
                    if g.has_edge(u, v):
                        # 边 (u, v) 存在，获取边的权重
                        weight = g[u][v].get('weight')
                        weight_list.append(weight)
                    else:
                        # 边 (u, v) 不存在，添加无穷大
                        weight_list.append(np.inf)

                # 在新图中添加边 (u, v)，并将权重列表作为其属性
                time_aggregated_graph.add_edge(u, v, weight=weight_list)        
        
        return time_aggregated_graph
    
    def get_shared_node_array_mask(self, vnffgManager:"VnffgManager"):
        """得到对于 SFC 请求中的每种类型的 VNF 存在可被共享的 NFVI 的掩码矩阵

        Args:
            vnffgManager (VnffgManager): vnffg 管理器
            
        Returns:
            np.array: 维度为 (vnf_num, nfvi_num) 的掩码矩阵，表示对于每种类型的 VNF 存在可被共享的 NFVI
        """
        shared_node_array_mask = []
        sfc_need_type_list = vnffgManager.sfc_req.sfc_vnfs_type
        for i,vnf_type in enumerate(sfc_need_type_list):
            shared_node_with_type_mask = [0] * len(vnffgManager.vnfVim.nfvi_group)
            if vnffgManager.sfc_req.sfc_vnfs_shared[i] == True:
                for nfvi in vnffgManager.vnfVim.who_has_vnf_with_type(vnf_type):
                    shared_node_with_type_mask[nfvi.id] = 1
            shared_node_array_mask.append(shared_node_with_type_mask)
            
        return np.array(shared_node_array_mask)
    
    def solve_embedding(self,vnffgManager:"VnffgManager") -> SolutionDeploy:
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "arrive"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        self.current_nfvi_index_list = list(self.nfvOrchestrator.vnfVim.nfvi_group.keys())

        # algorithm begin ---------------------------------------------
        self.solution_deploy.current_time = vnffgManager.scheduler.now
        self.solution_deploy.resource['cpu'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu'] 
                                    for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['ram'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['ram'] 
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['rom'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['rom']
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]

        self.adjacent_topo = vnffgManager.vnfVim.get_graph(time=vnffgManager.scheduler.now*u.ms, with_weight="Latency")
        adjacent_topo_with_ue = vnffgManager.vnfVim.get_graph_to_ue(vnffgManager.ue_access_start, self.adjacent_topo, with_weight="Latency")
        adjacent_topo_with_ue = vnffgManager.vnfVim.get_graph_to_ue(vnffgManager.ue_access_end, adjacent_topo_with_ue, with_weight="Latency")
        
        self.solution_deploy.current_topo = self.adjacent_topo
        self.solution_deploy.current_topo_with_ue = adjacent_topo_with_ue
        self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos

        self.solution_deploy.share_node = [None] * len(self.current_vnfs_index_list)

        can_access_nfvi_list = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_start)
        nfvi_access_start_mask = [True if nfvi in can_access_nfvi_list else False 
                                  for nfvi in self.nfvOrchestrator.vnfVim.nfvi_group.values()]
        can_access_nfvi_list = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_end)
        nfvi_access_end_mask = [True if nfvi in can_access_nfvi_list else False 
                                for nfvi in self.nfvOrchestrator.vnfVim.nfvi_group.values()]

        if self.work_mode == "train":
            train_solution, subbuffer, _ = self.learn(self.vnffgManager, 
                                                      self.solution_deploy,
                                                      nfvi_access_start_mask,
                                                      nfvi_access_end_mask,
                                                      self.get_time_aggregated_graph(vnffgManager),
                                                      self.get_shared_node_array_mask(vnffgManager))
            self.merge_experience(train_solution,subbuffer)
            if self.buffer.size() >= 32:
                self.update()
        
        elif self.work_mode == "validate":
            train_solution, _, _ = self.validate(self.vnffgManager, 
                                                self.solution_deploy,
                                                nfvi_access_start_mask,
                                                nfvi_access_end_mask,
                                                self.get_time_aggregated_graph(vnffgManager),
                                                self.get_shared_node_array_mask(vnffgManager))
        else:
            raise ValueError(f"{self.__class__.__name__} reported: Invalid work_mode")

        if train_solution.result == True:
            # 从智能体中得到了可行解
            for i,node in enumerate(self.current_vnfs_index_list):
                aim_deploy_nfvi_id = train_solution.selected_actions[i]
                self.solution_deploy.map_node[node] = aim_deploy_nfvi_id
                
                # 寻找可共享的 NFVI 上的部署 VNF
                if vnffgManager.sfc_req.sfc_vnfs_shared[i] == True:
                    vnf_type_need = vnffgManager.sfc_req.sfc_vnfs_type[i]
                    vnfs_list = vnffgManager.vnfVim.nfvi_group[aim_deploy_nfvi_id].get_deployed_vnf_with_type(vnf_type_need)
                    if vnfs_list != []:
                        self.solution_deploy.share_node[i] = vnfs_list[0].id
        else:
            # 从智能体中未能得到可行解
            self.solution_deploy.current_latency = train_solution.sfc_actual_latency * u.ms
            self.solution_deploy.current_description = train_solution.reason
            self.solution_deploy.current_result = False
            return self.solution_deploy

        v_links = [(v_node, v_node+1) for v_node in self.current_vnfs_index_list[:-1]]
        for v_link in v_links:
            try:
                map_path = nx.dijkstra_path(self.adjacent_topo, self.solution_deploy.map_node[v_link[0]], self.solution_deploy.map_node[v_link[1]])
            except:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            if len(map_path) == 1:
                self.solution_deploy.map_link[v_link] = [(map_path[0], map_path[0])]
            else:
                self.solution_deploy.map_link[v_link] = [(map_path[i],map_path[i+1]) for i in range(len(map_path)-1)]
        # algorithm end ---------------------------------------------

        self.solution_deploy.current_description = self.check_solution(vnffgManager)

        if self.solution_deploy.current_description != SOLUTION_DEPLOY_TYPE.SET_SUCCESS:
            self.solution_deploy.current_result = False
        else:
            self.solution_deploy.current_result = True

        return self.solution_deploy
    
    def solve_migration(self, vnffgManager:"VnffgManager") -> SolutionDeploy:
        self.vnffgManager = vnffgManager
        self.solution_deploy = SolutionDeploy()
        self.solution_deploy.current_req_type = "migrate"
        self.current_vnfs_index_list = list(range(len(vnffgManager.sfc_req.sfc_vnfs_type)))
        self.current_nfvi_index_list = list(vnffgManager.vnfVim.nfvi_group.keys())        

        # algorithm begin ---------------------------------------------
        self.solution_deploy.current_time = vnffgManager.scheduler.now
        self.solution_deploy.resource['cpu'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['cpu'] 
                                    for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['ram'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['ram'] 
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]
        self.solution_deploy.resource['rom'] = [vnffgManager.vnfManager.vnfTemplates[vnf_type].resource_limit['rom']
                                        for vnf_type in vnffgManager.sfc_req.sfc_vnfs_type]

        self.adjacent_topo = vnffgManager.vnfVim.get_graph(with_weight="Latency")
        adjacent_topo_with_ue = vnffgManager.vnfVim.get_graph_to_ue(vnffgManager.ue_access_start, self.adjacent_topo, with_weight="Latency")
        adjacent_topo_with_ue = vnffgManager.vnfVim.get_graph_to_ue(vnffgManager.ue_access_end, adjacent_topo_with_ue, with_weight="Latency")
        
        self.solution_deploy.current_topo = self.adjacent_topo
        self.solution_deploy.current_topo_with_ue = adjacent_topo_with_ue
        self.solution_deploy.current_qos = vnffgManager.sfc_req.sfc_qos

        self.solution_deploy.share_node = [None] * len(self.current_vnfs_index_list)

        can_access_nfvi_list = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_start)
        nfvi_access_start_mask = [True if nfvi in can_access_nfvi_list else False 
                                  for nfvi in self.nfvOrchestrator.vnfVim.nfvi_group.values()]
        can_access_nfvi_list = vnffgManager.vnfVim.get_can_access_nfvi_node(vnffgManager.ue_access_end)
        nfvi_access_end_mask = [True if nfvi in can_access_nfvi_list else False 
                                for nfvi in self.nfvOrchestrator.vnfVim.nfvi_group.values()]

        if self.work_mode == "train":
            train_solution, subbuffer, _ = self.learn(self.vnffgManager, 
                                                      self.solution_deploy,
                                                      nfvi_access_start_mask,
                                                      nfvi_access_end_mask,
                                                      self.get_time_aggregated_graph(vnffgManager),
                                                      self.get_shared_node_array_mask(vnffgManager))
            self.merge_experience(train_solution,subbuffer)
            if self.buffer.size() >= 32:
                self.update()
        
        elif self.work_mode == "validate":
            train_solution, _, _ = self.validate(self.vnffgManager, 
                                                self.solution_deploy,
                                                nfvi_access_start_mask,
                                                nfvi_access_end_mask,
                                                self.get_time_aggregated_graph(vnffgManager),
                                                self.get_shared_node_array_mask(vnffgManager))
        else:
            raise ValueError(f"{self.__class__.__name__} reported: Invalid work_mode")

        if train_solution.result == True:
            # 从智能体中得到了可行解
            for i,node in enumerate(self.current_vnfs_index_list):
                aim_deploy_nfvi_id = train_solution.selected_actions[i]
                self.solution_deploy.map_node[node] = aim_deploy_nfvi_id
                
                # 寻找可共享的 NFVI 上的部署 VNF
                if vnffgManager.sfc_req.sfc_vnfs_shared[i] == True:
                    vnf_type_need = vnffgManager.sfc_req.sfc_vnfs_type[i]
                    vnfs_list = vnffgManager.vnfVim.nfvi_group[aim_deploy_nfvi_id].get_deployed_vnf_with_type(vnf_type_need)
                    if vnfs_list != []:
                        self.solution_deploy.share_node[i] = vnfs_list[0].id
        else:
            # 从智能体中未能得到可行解
            self.solution_deploy.current_latency = train_solution.sfc_actual_latency * u.ms
            self.solution_deploy.current_description = train_solution.reason
            self.solution_deploy.current_result = False
            self.calculate_cost_and_revenue(vnffgManager)
            return self.solution_deploy

        v_links = [(v_node, v_node+1) for v_node in self.current_vnfs_index_list[:-1]]
        for v_link in v_links:
            try:
                map_path = nx.dijkstra_path(self.adjacent_topo, self.solution_deploy.map_node[v_link[0]], self.solution_deploy.map_node[v_link[1]])
            except:
                self.solution_deploy.current_description = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_PATH
                self.solution_deploy.current_result = False
                return self.solution_deploy
            
            if len(map_path) == 1:
                self.solution_deploy.map_link[v_link] = [(map_path[0], map_path[0])]
            else:
                self.solution_deploy.map_link[v_link] = [(map_path[i],map_path[i+1]) for i in range(len(map_path)-1)]
        
        # algorithm end ---------------------------------------------

        self.solution_deploy.current_description = self.check_solution(vnffgManager)

        if self.solution_deploy.current_description != SOLUTION_DEPLOY_TYPE.CHANGE_SUCCESS:
            self.solution_deploy.current_result = False
        else:
            self.solution_deploy.current_result = True

        self.calculate_cost_and_revenue(vnffgManager)

        return self.solution_deploy
    

    def save_param(self):
        self.tracer.save_model(**{'policy': self.policy.state_dict(),'optimizer': self.optimizer.state_dict()})
        print(f'INFO: {self.name} 保存求解器参数至 {self.tracer.model_file}')


    def load_param(self, param_file_path):
        if param_file_path is None:
            print(f'INFO: {self.name} 没有指定求解器参数文件路径，将使用随机初始化参数')
        elif not os.path.exists(param_file_path):
            print(f'INFO: {self.name} 没有找到求解器参数文件 {param_file_path} 将使用随机初始化参数')
        else:
            print(f'INFO: {self.name} 加载求解器参数 {param_file_path}')
            policy_param, optimizer_param = self.tracer.load_model(param_file_path)
            self.policy.load_state_dict(policy_param)
            self.optimizer.load_state_dict(optimizer_param)

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
        
        
        