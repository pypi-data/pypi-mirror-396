
import torch
from torch_geometric.data import Data, Batch
import networkx as nx
import numpy as np
from astropy import units as u

from netorchestr.envir.node.controller.mano.solver_deploy import SolutionDeploy, SOLUTION_DEPLOY_TYPE
from netorchestr.envir.node.controller.mano.solver_deploy.solver_deploy_gatdrl_melt_gat.train_env_net import TrainEnvPNet, TrainEnvVNet

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import VnffgManager

class TrainSolution:
    def __init__(self) -> None:
        self.sfc_req_type:str = ""
        self.sfc_req_latency:float = 0.0
        self.sfc_actual_latency:float = 0.0
        self.try_times:int = 0
        self.max_try_times:int = 0
        self.selected_actions:list[int] = []
        self.result:bool = False
        self.place_result:bool = False
        self.route_result:bool = False
        self.rejection:bool = False
        self.reason:str = ""
        self.reward:float = 0.0
        self.vnf_fail_count = []  # 每个 VNF 的失败次数计数器
        self.max_fail_per_vnf = 0  # 每个 VNF 最多失败次数
        

class TrainEnv:
    def __init__(self,vnffgManager:"VnffgManager", solution_deploy:SolutionDeploy, 
                 time_aggregated_graph:nx.Graph, shared_node_array_mask:np.ndarray) -> None:
        self.time = solution_deploy.current_time
        self.p_net = TrainEnvPNet(vnffgManager, solution_deploy)
        self.v_net = TrainEnvVNet(vnffgManager, solution_deploy)
        self.c_net = solution_deploy.current_topo_with_ue           # 当前连接UE的拓扑
        self.curr_v_node_id = 0
        
        self.train_solution = TrainSolution()
        self.train_solution.sfc_req_latency = solution_deploy.current_qos["latency"].to(u.ms).value
        self.train_solution.sfc_req_type = solution_deploy.current_req_type
        self.train_solution.max_try_times = 10 * len(self.v_net.nodes)
        self.vnf_fail_count = [0] * len(self.v_net.nodes)
        self.max_fail_per_vnf = 5

        self.p_net_time_aggregated = time_aggregated_graph
        self.p_net_shared_node_array_mask = shared_node_array_mask
        
    def get_observation(self):
        """get_observation

        Args:
            event (Event)

        Returns:
            dict[
                
                'p_net_x':NDArray[float32] dim = p_net_node_num * node_features,
                
                当前参与计算的 p_net 的节点特征类型为 [remain_cpu, capacity_cpu, remain_ram, capacity_ram, aggr_remain_band, aggr_capacity_band]
            
                'p_net_edge':NDArray[int] dim = 2 * edge_num
                 
                'v_net_x':NDArray[float32] dim = v_net_node_num * node_features
                
                当前参与计算的 v_net 的特征类型为 [request_cpu, request_ram, request_band]
                
                ] 
        """
        p_net_obs,p_net_edge,p_net_edge_features = self.__get_p_net_obs()
        v_net_obs = self.__get_v_net_obs()
        
        return {'p_net_x': p_net_obs,
                'p_net_edge': p_net_edge,
                'p_net_edge_x': p_net_edge_features,
                'v_net_x': v_net_obs}
    
    def __get_p_net_obs(self):
        """得到 p_net 的状态量

        Returns:
            tuple: (node_features, edge_index, edge_features)
            
            node_features: NDArray[float32] dim = p_net_node_num * node_features
            
            当前参与计算的 p_net 的节点特征类型为 [remain_cpu, capacity_cpu, remain_ram, capacity_ram, aggr_remain_band, aggr_capacity_band]
            
            edge_index: NDArray[int] dim = 2 * edge_num
            
            edge_features: NDArray[float32] dim = edge_num * time_aggregated_features
            
            当前参与计算的 p_net 的边特征类型为 [weight at each time]
            
        """
        node_features = []
        
        node_attrs = [
            'remain_cpu',       # 1
            'capacity_cpu',     # 2
            'remain_ram',       # 3
            'capacity_ram',     # 4
            # 'remain_rom',       # 5
            # 'capacity_rom'      # 6
        ]
        
        aggr_attrs = ['remain_band',      # 7
                      'capacity_band'     # 8
                      ]
        
        # 处理普通节点特征（单独归一化）
        for attr in node_attrs:
            feat = np.array(self.p_net.get_all_nodes_attrs_values(attr))
            feat_min = feat.min()
            feat_max = feat.max()
            # 避免除零（若特征全相同，归一化为 0）
            if feat_max - feat_min < 1e-8:
                norm_feat = np.zeros_like(feat, dtype=np.float32)
            else:
                norm_feat = (feat - feat_min) / (feat_max - feat_min)
            node_features.append(norm_feat)
        
        # 处理聚合边特征（单独归一化）
        for attr in aggr_attrs:
            feat = np.array(self.p_net.get_all_nodes_aggrlinks_attrs_values(attr))
            feat_min = feat.min()
            feat_max = feat.max()
            if feat_max - feat_min < 1e-8:
                norm_feat = np.zeros_like(feat, dtype=np.float32)
            else:
                norm_feat = (feat - feat_min) / (feat_max - feat_min)
            node_features.append(norm_feat)

        # 处理共享节点特征（单独归一化）
        if self.curr_v_node_id >= len(self.v_net.nodes):
            node_features.append(np.zeros(len(self.p_net.nodes)))                               #9
        else:
            node_features.append(self.p_net_shared_node_array_mask[self.curr_v_node_id])        #9
        
        # 转换为 (node_num, feat_dim) 的格式（特征维度在最后一维）
        node_features = np.stack(node_features, axis=1).astype(np.float32)
        
        edge_index = np.array(list(self.p_net.edges)).T
    
        edge_features = []
        for edge in self.p_net.edges:
            edge_features.append(self.p_net_time_aggregated.edges[edge]['weight'])
        edge_features = np.array(edge_features)
        # 无穷值替换：将 np.inf 替换为1e10（代表链路断开）
        edge_features = np.where(np.isinf(edge_features), 1e10, edge_features)
        # 全局 Min-Max 归一化：将所有边的所有时序特征缩放到[0,1], 计算全局最小值和最大值（排除1e10，避免其影响归一化范围）
        valid_mask = (edge_features < 1e10)  # 标记有效时延（非断开的边）
        if valid_mask.any():  # 确保存在有效时延（避免全是断开边导致的除零错误）
            global_min = edge_features[valid_mask].min()
            global_max = edge_features[valid_mask].max()
            # 归一化公式：norm = (x - min) / (max - min)，断开边（1e10）归一化后为1
            edge_features[valid_mask] = (edge_features[valid_mask] - global_min) / (global_max - global_min)
            edge_features[~valid_mask] = 1.0  # 断开边的归一化值设为1（最大值，代表不可用）
        else:
            # 极端情况：所有边都是断开的，直接设为1.0
            edge_features = np.ones_like(edge_features)

        return node_features,edge_index,edge_features

    def __get_v_net_obs(self):
        """得到 v_net 的状态量

        Returns:
            NDArray[float32] dim = v_net_node_num * node_features
            
            当前参与计算的 v_net 的特征类型为 [request_cpu, request_ram, request_band]
        """
        node_features = []
    
        node_attrs = ['request_cpu', # 1
                      'request_ram', # 2
                    #   'request_rom'  # 3
                      ]
        aggr_attrs = ['request_band' # 4
                      ]
        
        for attr in node_attrs:
            feat = np.array(self.v_net.get_all_nodes_attrs_values(attr))
            feat_min = feat.min()
            feat_max = feat.max()
            if feat_max - feat_min < 1e-8:
                norm_feat = np.zeros_like(feat, dtype=np.float32)
            else:
                norm_feat = (feat - feat_min) / (feat_max - feat_min)
            node_features.append(norm_feat)

        for attr in aggr_attrs:
            feat = np.array(self.v_net.get_all_nodes_aggrlinks_attrs_values(attr))
            feat_min = feat.min()
            feat_max = feat.max()
            if feat_max - feat_min < 1e-8:
                norm_feat = np.zeros_like(feat, dtype=np.float32)
            else:
                norm_feat = (feat - feat_min) / (feat_max - feat_min)
            node_features.append(norm_feat)
        
        node_features = np.array(node_features, dtype=np.float32).T

        return node_features
    
    @staticmethod
    def v_net_obs_to_tensor(obs:Union[dict,list], device) -> dict:
        """v_net_obs_to_tensor

        Args:
            obs (dict): _description_
            device (_type_): _description_

        Returns:
            dict: {'v_net_x': obs_v_net_x}
        """
        if isinstance(obs, dict):
            v_net_x = obs['v_net_x']
            # 提取的 v_net_x 转换为 PyTorch 的浮点张量，在第 0 维增加一个维度，张量移动到指定的计算设备
            obs_v_net_x = torch.FloatTensor(v_net_x).unsqueeze(dim=0).to(device)
            return {'v_net_x': obs_v_net_x}
        elif isinstance(obs, list):
            obs_batch = obs
            v_net_x_list = []
            for observation in obs:
                v_net_x = obs['v_net_x']
                v_net_x_list.append(v_net_x)
            obs_v_net_x = torch.FloatTensor(np.array(v_net_x_list)).to(device)
            return {'v_net_x': obs_v_net_x}
        else:
            raise Exception(f"Unrecognized type of observation {type(obs)}")
    
    @staticmethod
    def p_net_obs_to_tensor(obs:Union[dict,list], device) -> dict:
        """将输入的与 p_net 相关的观测数据转换为 PyTorch 张量格式, 并适配 PyTorch Geometric 图神经网络库的数据结构

        Args:
            obs (dict): p_net 观测数据字典, 键值包含 
            
                "p_net_x": dim = p_node_num * p_node_features
                
                "p_net_edge": dim = 2 * p_edge_num
                
                "p_net_edge_x": dim = p_edge_num * time_aggregated_features
                
                "p_net_node": dim = 1 # 当前关注的节点
                
                "hidden_state": dim = (1, embedding_dim)
                
                "encoder_outputs": dim = (v_node_num, embedding_dim)
            
            device: 指定的计算设备, 如 torch.device('cuda') 或 cpu

        Returns:
            dict: { 
            
                'p_net': p_net_obs, # PyTorch Geometric 单图数据结构, 类型为 Batch, 包含节点特征、边索引、边属性等信息, 类型为 Data
            
                'p_net_node': p_net_node, #  当前关注的节点, 类型为 LongTensor, 形状为 (1,)
                    
                'hidden_state': hidden_state, # 循环神经网络 GRU 输出的隐藏状态, 类型为 FloatTensor, 形状为 (1, 1, embedding_dim)
                    
                'encoder_outputs': encoder_outputs # 编码器输出, 类型为 FloatTensor, 形状为 (1, v_node_num, embedding_dim)
                
                }
        """
        if isinstance(obs, dict):
            # p_net 的节点特征矩阵, 维度为 p_node_num * p_node_features
            p_net_x = torch.tensor(obs['p_net_x']) 
            # p_net 的边索引，PyTorch Geometric 中边索引格式为 (2, edge_num)（第一行是起点，第二行是终点），转为 long 类型（图神经网络常用类型）
            p_net_edge = torch.tensor(obs['p_net_edge']).long() 
            # p_net 的边属性，PyTorch Geometric 中边属性格式为 (edge_num, time_aggregated_features)
            p_net_edge_attr = torch.tensor(obs['p_net_edge_x']).float()
            # Data 是 PyTorch Geometric 中表示单个图的数据结构，包含节点特征（x）、边索引（edge_index）、边属性（edge_attr）等。
            data = Data(x=p_net_x, edge_index=p_net_edge, edge_attr=p_net_edge_attr) # 构建 PyTorch Geometric 图数据结构, 
            # 将单个图数据包装成批次（batch）格式（即使只有一个图），符合图神经网络输入的标准格式
            p_net_obs = Batch.from_data_list([data]).to(device)
            
            # 当前关注的节点, 转换为 LongTensor（整数类型张量），并用 [obs['p_net_node']] 增加一个维度(1,)，移动到指定设备
            p_net_node = torch.LongTensor([obs['p_net_node']]).to(device)
            
            # 循环神经网络 GRU 输出的隐藏状态, 转换为浮点张量后，增加 batch 维度 (1, 1, embedding_dim)，移动到指定设备
            hidden_state = torch.FloatTensor(obs['hidden_state']).unsqueeze(dim=0).to(device)
            
            # 编码器输出, 转换为浮点张量后，增加 batch 维度 (1, v_node_num, embedding_dim)，移动到指定设备
            encoder_outputs = torch.FloatTensor(obs['encoder_outputs']).unsqueeze(dim=0).to(device)

            return {'p_net': p_net_obs, 'p_net_node': p_net_node, 
                    'hidden_state': hidden_state, 'encoder_outputs': encoder_outputs}
            
        elif isinstance(obs, list):
            obs_batch = obs
            p_net_data_list, p_net_node_list, hidden_state_list, encoder_outputs_list = [], [], [], []
            
            # 第一步：找到所有观测中edge_attr的最大维度（即最大采样点数量）
            max_edge_attr_dim = 0
            for observation in obs_batch:
                edge_x = np.array(observation['p_net_edge_x'])
                current_dim = edge_x.shape[1] if edge_x.ndim == 2 else 1
                if current_dim > max_edge_attr_dim:
                    max_edge_attr_dim = current_dim            
            
            # 第二步：批量处理每个观测，补全edge_attr的维度
            for observation in obs_batch:
                p_net_x = torch.tensor(observation['p_net_x'])
                
                p_net_edge = torch.tensor(observation['p_net_edge']).long()
                
                p_net_edge_attr = torch.tensor(observation['p_net_edge_x']).float()
                # 确保edge_attr是2D张量（edge_num, current_dim）
                if p_net_edge_attr.ndim == 1:
                    p_net_edge_attr = p_net_edge_attr.unsqueeze(1)
                current_dim = p_net_edge_attr.shape[1]
                if current_dim < max_edge_attr_dim:
                    pad_num = max_edge_attr_dim - current_dim
                    # 生成补全张量
                    pad_tensor = torch.ones(
                        (p_net_edge_attr.shape[0], pad_num),  # 形状：(边数, 需补维度)
                        dtype=p_net_edge_attr.dtype,          # 与原张量同类型（float32）
                        device=p_net_edge_attr.device         # 与原张量同设备（CPU/GPU）
                    )
                    p_net_edge_attr = torch.cat([p_net_edge_attr, pad_tensor], dim=1)
                
                p_net_data = Data(x=p_net_x, edge_index=p_net_edge, edge_attr=p_net_edge_attr)
                p_net_node = observation['p_net_node']
                hidden_state = observation['hidden_state']
                encoder_outputs = observation['encoder_outputs']
                p_net_data_list.append(p_net_data)
                p_net_node_list.append(p_net_node)
                hidden_state_list.append(hidden_state)
                encoder_outputs_list.append(encoder_outputs)
            obs_p_net_node = torch.LongTensor(np.array(p_net_node_list)).to(device)
            obs_hidden_state = torch.FloatTensor(np.array(hidden_state_list)).to(device)
            obs_p_net = Batch.from_data_list(p_net_data_list).to(device)
            # Pad sequences with zeros and get the mask of padded elements
            sequences = encoder_outputs_list
            max_length = max([seq.shape[0] for seq in sequences])
            padded_sequences = np.zeros((len(sequences), max_length, sequences[0].shape[1]))
            mask = np.zeros((len(sequences), max_length), dtype=np.bool_)
            for i, seq in enumerate(sequences):
                seq_len = seq.shape[0]
                padded_sequences[i, :seq_len, :] = seq
                mask[i, :seq_len] = 1
            obs_encoder_outputs = torch.FloatTensor(np.array(padded_sequences)).to(device)
            obs_mask = torch.FloatTensor(mask).to(device)

            return {'p_net': obs_p_net, 'p_net_node': obs_p_net_node, 
                    'hidden_state': obs_hidden_state, 'encoder_outputs': obs_encoder_outputs}
        else:
            raise ValueError('obs type error')
    
    
    def get_latency_delay_to_ue(self, ue_access:str, action:int):
        """得到如果执行当前动作与接入用户之间的时延

        Args:
            ue_access (str): 接入用户位置, start表示UE在开始节点, end表示UE在结束节点.
            action (int): 动作编号, 即 vnf 部署位置
        """
        if ue_access == "start":
            ue_node_id = len(self.c_net.nodes) - 2
        elif ue_access == "end":
            ue_node_id = len(self.c_net.nodes) - 1
        
        edge_attrs = self.c_net.edges.get((ue_node_id,action),None)
        if edge_attrs is None:
            return np.inf
        else:
            return edge_attrs['weight']    
    
    
    def get_action_mask(self):
        mask = np.zeros(len(self.p_net.nodes), dtype=bool)
        
        for node in self.p_net.nodes:
            mask[node] = self.check_action(node)
            
        return mask
        
        # 资源约束条件
        request_cpu = self.v_net.nodes[self.curr_v_node_id]['request_cpu']
        request_ram = self.v_net.nodes[self.curr_v_node_id]['request_ram']
        cpu_values = self.p_net.get_all_nodes_attrs_values('remain_cpu')
        ram_values = self.p_net.get_all_nodes_attrs_values('remain_ram')
        cadidate_nodes = []
        for node in self.p_net.nodes:
            if request_cpu <= cpu_values[node] and request_ram <= ram_values[node]:
                cadidate_nodes.append(node)
        mask[cadidate_nodes] = True
        
        # 路由约束条件
        if len(self.train_solution.selected_actions) >= 1:
            last_action = self.train_solution.selected_actions[-1]
            v_link_rq_band = self.v_net.edges[(self.curr_v_node_id,self.curr_v_node_id-1)]['request_band']

            for action in self.p_net.nodes:
                if action == last_action: # 动作为自身节点时，不做限制
                    continue
                map_path = self.p_net.get_djikstra_path(last_action,action)
                if len(map_path) == 0: # 动作对应的节点没有路由，不能被执行
                    mask[action] = False
                elif len(map_path) == 1: # 动作对应的节点只有一个路由，需要判断是否满足带宽约束
                    map_link = [(map_path[0],map_path[0])]
                else: # 动作对应的节点有多个路由，需要判断是否满足带宽约束
                    map_link = [(map_path[i],map_path[i+1]) for i in range(len(map_path)-1)]

                p_link_rm_band = [self.p_net.opt_link_attrs_value((link[0],link[1]),'remain_band','get') for link in map_link]
                link_check_flag = [v_link_rq_band <= band for band in p_link_rm_band]
                if False in link_check_flag:
                    mask[action] = False

        return mask
    
    def mix_action_mask(self, mask_1, mask_2):
        mask = np.logical_and(mask_1, mask_2)
        return mask

    def step(self, action:int, mask:np.ndarray):
        """sub env step

        Args:
            action (int): 

        Returns:
            self.get_observation (dict): \\
            self.__compute_reward (float): \\
            done (bool): \\
            self.train_solution (object): \\ 
        """
        self.train_solution.try_times += 1

        if self.train_solution.try_times > self.train_solution.max_try_times:
            return self.reject()
        
        assert action in list(self.p_net.nodes)
        check_result = self.check_action(action)

        if check_result and mask[0][action]:
            self.do_action(action)
            self.train_solution.selected_actions.append(action)
            self.curr_v_node_id += 1
            done = False
            
            if self.curr_v_node_id >= len(self.v_net.nodes):
                done = True
        else:
            check_result = False
            done = False
        
        next_train_env_obs = self.get_observation()
        train_env_reward = self.compute_reward(self.train_solution)
        train_env_done = done
        train_env_info = self.train_solution
        train_step_result = check_result
        
        self.train_solution.reward += train_env_reward
        
        if self.train_solution.sfc_req_latency - self.train_solution.sfc_actual_latency < 10:
            # 当前部署已经完全不可能满足最后接入的时延需求，提前结束本 SFC 的部署
            self.train_solution.try_times = self.train_solution.max_try_times
        
        return next_train_env_obs, train_env_reward, train_env_done, train_env_info, train_step_result


    def reject(self):
        """智能体尝试次数达到上限未能得到满足约束的动作, 主动终止尝试

        Returns:
            self.get_observation (dict): \\
            self.__compute_reward (float): \\
            done (bool): \\
            self.train_solution (object): \\ 
            
        Note:
            这里的尝试次数达到上限大多都是因为在给定的时延约束条件下实在未能找到满足要求的解.
            
            因为网络的资源总量是足够的, 该智能体无法得到满足约束的解很大概率不太可能是因为资源不足, 而是因为网络结构本身的限制.
            
            因此这里返回一个失败原因的总结为时延不足导致.
        """
        self.train_solution.rejection = True
        self.train_solution.result = False
    
        if self.train_solution.reason == SOLUTION_DEPLOY_TYPE.NOTHING:
            if self.train_solution.sfc_req_type == "arrive":
                self.train_solution.reason = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_LATENCY
            elif self.train_solution.sfc_req_type == "migrate":
                self.train_solution.reason = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_LATENCY
    
        next_train_env_obs = self.get_observation()
        train_env_reward = self.compute_reward(self.train_solution)
        train_env_done = True
        train_env_info = self.train_solution
        train_step_result = False
        
        self.train_solution.reward += train_env_reward
        
        return next_train_env_obs, train_env_reward, train_env_done, train_env_info, train_step_result


    def get_deploy_reward(self) -> float:
        action_curr = self.train_solution.selected_actions[-1]
        deploy_index = len(self.train_solution.selected_actions) - 1
        deploy_cost = 1
        
        # 1. 节点类型系数（保留原有逻辑）
        node_type_coeff = {
            "Ground": 1.0,
            "Uav": 1.1,
            "Sat": 1.2
        }.get(self.p_net.nodes[action_curr]["type"], 1.0)
        
        # 2. 资源需求（改为加权和，避免连乘导致数值过小）
        v_node = self.v_net.nodes[deploy_index]
        if self.p_net_shared_node_array_mask[deploy_index, action_curr] == 0:
            # 非共享节点：CPU+RAM+ROM加权（权重按资源重要性设置）
            resource_demand = (
                0.4 * v_node["request_cpu"] + 
                0.4 * v_node["request_ram"] + 
                0.2 * v_node["request_rom"]  # ROM权重较低，因通常不稀缺
            )
        else:
            # 共享节点：仅ROM（保留原有逻辑）
            resource_demand = v_node["request_rom"]
        
        # 3. 部署成本（系数*需求，数值范围更合理）
        deploy_cost = max(node_type_coeff * resource_demand, 0.1)
        
        # 4. 新增“资源充足奖励”：若当前节点剩余资源充足，额外加分
        remain_resource_ratio = (
            min(self.p_net.nodes[action_curr]["remain_cpu"] / v_node["request_cpu"],
                self.p_net.nodes[action_curr]["remain_ram"] / v_node["request_ram"],
                self.p_net.nodes[action_curr]["remain_rom"] / v_node["request_rom"])
            if self.p_net_shared_node_array_mask[deploy_index, action_curr] == 0
            else 1.0  # 共享节点不检查CPU/RAM
        )
        resource_sufficient_bonus = 1.0 + min(remain_resource_ratio - 1.0, 0.5)  # 资源充足最多加0.5分
        
        # 5. 最终部署奖励（基础奖励*资源充足系数，范围0.5-5）
        base_deploy_reward = 2.0 / deploy_cost  # 基础奖励，需求越低奖励越高
        deploy_reward = min(base_deploy_reward * resource_sufficient_bonus, 5.0)  # 上限5，避免极端值

        return deploy_reward
    
    
    def get_balance_reward(self) -> float:
        action_curr = self.train_solution.selected_actions[-1]
        deploy_index = len(self.train_solution.selected_actions) - 1
        v_node = self.v_net.nodes[deploy_index]
        
        # 1. 部署后的资源使用率
        deploy_used_ratio = self.p_net.get_resource_used_ratio(action_curr)
        
        # 2. 网络平均资源使用率
        net_average_used_ratio = self.p_net.get_average_resource_used_ratio()
        
        # 3. 资源平衡奖励：使用率与平均差异越小，奖励越高（范围0-2）
        balance_score = np.exp(-5 * (deploy_used_ratio - net_average_used_ratio)**2)
        balance_reward = 2.0 * balance_score
        
        # 4. 资源过载风险惩罚：若部署后使用率超80%，扣减奖励
        if deploy_used_ratio > 0.8:
            overload_penalty = 0.5 * (deploy_used_ratio - 0.8) / 0.2  # 超80%后，每超10%扣0.25分
            balance_reward = max(balance_reward - overload_penalty, 0.0)
        
        return balance_reward
    
    
    def get_stable_reward(self) -> float:
        """
        根据链路稳定度计算奖励（允许链路断开但施加惩罚）
        - 根据断开概率计算一个惩罚因子
        - 奖励由“时延稳定性”、“平均时延”和“断开惩罚因子”共同决定
        """
        def _calc_link_down_probability(latency_samples: list[float]) -> float:
            """
            计算链路在未来的断开概率（基于采样数据）。
            :param latency_samples: 链路未来时延的采样列表。
            :return: 断开概率 (0.0 到 1.0)。
            """
            if not latency_samples:
                return 1.0  # 如果没有数据，默认链路是断开的。
            
            # 统计采样中出现 'inf' 的次数
            down_count = sum(1 for sample in latency_samples if np.isinf(sample))
            
            # 计算断开概率
            down_prob = down_count / len(latency_samples)
            return down_prob
        
        def _get_downlink_penalty(down_prob: float) -> float:
            """
            根据链路断开概率计算惩罚因子。
            - 断开概率为0时, 惩罚因子为1.0 (无惩罚)。
            - 断开概率越高，惩罚因子越低。
            - 使用指数函数来实现惩罚的非线性增长。
            :param down_prob: 链路断开概率。
            :return: 惩罚因子 (0.0 到 1.0)。
            """
            # 当 down_prob = 0 时, penalty = 1.0
            # 当 down_prob = 0.5 时, penalty ≈ 0.368
            # 当 down_prob = 1.0 时, penalty ≈ 0.018
            # 你可以调整指数的系数来改变惩罚的严厉程度。
            penalty_factor = np.exp(-3 * down_prob)
            return penalty_factor
        
        if len(self.train_solution.selected_actions) < 2:
            return 0.0
        action_curr = self.train_solution.selected_actions[-1]
        action_last = self.train_solution.selected_actions[-2]
        
        map_path = self.p_net.get_djikstra_path(action_curr,action_last)
        if len(map_path) == 1: 
            return 4.0  # 只有一个节点的链路，奖励固定为4.0
        
        map_links = [(map_path[i], map_path[i+1]) for i in range(len(map_path)-1)]
        total_stable_reward = 0.0
        
        for map_link in map_links:
            if "weight" not in self.p_net_time_aggregated.edges[map_link]:
                # 如果没有采样数据，视为高断开风险，给予最低奖励
                total_stable_reward += 0.01
                continue
                
            link_lat_samples = self.p_net_time_aggregated.edges[map_link]["weight"]
            
            # 1. 计算链路断开概率和惩罚因子
            down_prob = _calc_link_down_probability(link_lat_samples)
            down_penalty = _get_downlink_penalty(down_prob)

            # 2. 计算链路时延稳定性得分 (仅基于有效样本)
            valid_latencies = [lat for lat in link_lat_samples if not np.isinf(lat)]
            if len(valid_latencies) < 2:
                # 如果有效样本太少，稳定性得分为1.0（最稳定）或0.5（少量样本）
                stability_score = 0.5 if len(valid_latencies) == 1 else 1.0
            else:
                var_lat = np.var(valid_latencies)
                max_acceptable_var = 100.0
                stability_score = np.exp(-var_lat / max_acceptable_var)
            
            # 3. 计算链路平均时延得分 (仅基于有效样本)
            if not valid_latencies:
                # 如果所有样本都是断开的，平均时延得分最低
                avg_lat_score = 0.01
            else:
                avg_lat = np.mean(valid_latencies)
                max_acceptable_avg_lat = 200.0
                avg_lat_score = np.exp(-avg_lat / max_acceptable_avg_lat) if avg_lat > 0 else 0.0
            
            # 4. 单链路稳定度奖励 = (稳定性得分 * 权重 + 平均时延得分 * 权重) * 断开惩罚因子
            single_link_reward = (0.3 * stability_score + 0.7 * avg_lat_score) * down_penalty
            
            # 将单链路奖励贡献到总奖励中（乘以一个基础系数以调整奖励范围）
            total_stable_reward += single_link_reward * 2.0        
        
        # 5. 计算所有链路的平均奖励，并设置上限
        final_stable_reward = min(total_stable_reward / len(map_links), 4.0) if map_links else 0.0
        
        return final_stable_reward
    
    def get_latency_compliance_reward(self) -> float:
        """
        独立判断SFC累计延迟合规性
        - 累计延迟 ≤ 最大允许延迟: 奖励2-5
        - 累计延迟 > 最大允许延迟: 奖励0 (仅惩罚，无奖励)
        """
        # 1. 获取SFC的最大允许累计延迟, 计算分段推荐最大时延值
        segment_suggessted_latency = self.train_solution.sfc_req_latency/len(self.v_net.nodes)
        
        # 2. 计算当前SFC的累计延迟
        if len(self.train_solution.selected_actions) < 2:
            return 1.0  # 仅部署1个节点，无累计延迟，给予基础合规奖励
        segment_current_latency = self.train_solution.sfc_actual_latency/len(self.train_solution.selected_actions)
        
        # 3. 根据超时比例计算合规性奖励
        latency_redundancy = (segment_suggessted_latency - segment_current_latency) / segment_suggessted_latency
        compliance_reward = 1.0 + 2.0 * latency_redundancy  # 基础2分+冗余度加分，上限5分
        
        return min(compliance_reward, 3.0)

    def compute_reward(self, train_solution:TrainSolution) -> float:
        """Calculate deserved reward according to the result of current solution

        Args:
            train_solution (TrainSolution)

        Returns:
            float: reward
        """
        if len(self.train_solution.selected_actions) == 0:
            current_vnf_id = 0
        else:
            current_vnf_id = len(self.train_solution.selected_actions)-1
        
        if self.train_solution.try_times > self.train_solution.max_try_times:
            deployed_ratio = current_vnf_id / len(self.v_net.nodes)
            reward = -2 * len(self.v_net.nodes) * (1 - deployed_ratio)  # 已部署越多，惩罚越小
            return reward
        
        if train_solution.result == True:
            # 部署成功
            self.vnf_fail_count[current_vnf_id] = 0
            
            reward_deploy = self.get_deploy_reward()
            reward_balance = self.get_balance_reward()
            reward_stable = self.get_stable_reward()
            reward_latency_compliance = self.get_latency_compliance_reward()
            
            # 奖励权重
            reward = (0.1 * reward_deploy + 
                      0.1 * reward_balance + 
                      0.3 * reward_stable + 
                      0.5 * reward_latency_compliance)
            
            # 所有VNF部署完成的额外奖励
            if self.curr_v_node_id >= len(self.v_net.nodes):
                reward += 5.0
        else:
            # 部署失败
            self.vnf_fail_count[current_vnf_id] += 1
            
            # 若单个 VNF 部署超过最大失败次数, 固定惩罚，避免无限叠加
            if self.vnf_fail_count[current_vnf_id] >= self.max_fail_per_vnf:
                return self.train_solution.reward
            
            if self.train_solution.place_result == False:
                fail_reason = "resource_insufficient"
            elif self.train_solution.route_result == False:
                fail_reason = "link_unavailable"
                
            reason_penalty = {
                "link_unavailable": -1.0,
                "resource_insufficient": -0.5,
            }[fail_reason]
 
            try_penalty_coeff = min(self.train_solution.try_times /self.train_solution.max_try_times, 1.0)
                
            reward = reason_penalty * try_penalty_coeff
        
        return reward
        
    def check_action(self, action:int):
        self.train_solution.reason = SOLUTION_DEPLOY_TYPE.NOTHING
        self.train_solution.place_result = False
        self.train_solution.route_result = False
        self.train_solution.result = False
        
        # region 开始节点检查
        v_node_rq_cpu = self.v_net.nodes[self.curr_v_node_id]['request_cpu']
        p_node_rm_cpu = self.p_net.opt_node_attrs_value(action,'remain_cpu','get')
        node_check_flag = [v_node_rq_cpu <= p_node_rm_cpu]
        if False in node_check_flag:
            self.train_solution.place_result = False
            self.train_solution.result = False
            if self.train_solution.sfc_req_type == "arrive":
                self.train_solution.reason = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_CPU
            elif self.train_solution.sfc_req_type == "migrate":
                self.train_solution.reason = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NODE_CPU
            return False

        v_node_rq_ram = self.v_net.nodes[self.curr_v_node_id]['request_ram']
        p_node_rm_ram = self.p_net.opt_node_attrs_value(action,'remain_ram','get')
        node_check_flag = [v_node_rq_ram <= p_node_rm_ram]
        if False in node_check_flag:
            self.train_solution.place_result = False
            self.train_solution.result = False
            if self.train_solution.sfc_req_type == "arrive":
                self.train_solution.reason = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_RAM
            elif self.train_solution.sfc_req_type == "migrate":
                self.train_solution.reason = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NODE_RAM
            return False
        
        v_node_rq_rom = self.v_net.nodes[self.curr_v_node_id]['request_rom']
        p_node_rm_rom = self.p_net.opt_node_attrs_value(action,'remain_rom','get')
        node_check_flag = [v_node_rq_rom <= p_node_rm_rom]
        if False in node_check_flag:
            self.train_solution.place_result = False
            self.train_solution.result = False
            if self.train_solution.sfc_req_type == "arrive":
                self.train_solution.reason = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NODE_ROM
            elif self.train_solution.sfc_req_type == "migrate":
                self.train_solution.reason = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NODE_ROM
            return False

        # endregion 节点检查通过
        self.train_solution.place_result = True

        # region 开始路由检查  ### 缺少对接入用户后的时延检查 ********************** todo
        if len(self.train_solution.selected_actions) == 0:
            # 开始节点的路由，强制设定上一个动作为自身节点以使得后续计算正确
            last_action = action
            v_link_rq_band = 0 # 开始用户到接入节点的路由，不考虑带宽
        else:
            last_action = self.train_solution.selected_actions[-1]
            v_link_rq_band = self.v_net.edges[(self.curr_v_node_id,self.curr_v_node_id-1)]['request_band']

        # step 1: 检查路由是否存在
        map_path = self.p_net.get_djikstra_path(last_action,action)
        if len(map_path) == 0:
            self.train_solution.route_result = False
            self.train_solution.result = False
            if self.train_solution.sfc_req_type == "arrive":
                self.train_solution.reason = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_NO_PATH
            elif self.train_solution.sfc_req_type == "migrate":
                self.train_solution.reason = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_NO_PATH
            return False
        elif len(map_path) == 1: 
            map_link = [(map_path[0],map_path[0])]
            if len(self.train_solution.selected_actions) == 0:
                # 开始节点的路由，计入用户接入时延
                map_path_weight =  self.get_latency_delay_to_ue("start",action)
            else:
                # 中间节点之间的路由，且两个节点相同，此时不计入时延
                map_path_weight = 0
        else:
            map_link = [(map_path[i],map_path[i+1]) for i in range(len(map_path)-1)]
            map_path_weight = self.p_net.get_path_weight(map_path)
            
            if len(self.train_solution.selected_actions) == len(self.v_net.nodes) - 1:
                # 结束节点的路由，计入用户接入时延
                map_path_weight += self.get_latency_delay_to_ue("end",action)
        
        # step 2: 检查路由是否满足带宽约束
        p_link_rm_band = [self.p_net.opt_link_attrs_value((link[0],link[1]),'remain_band','get') for link in map_link]
        link_check_flag = [v_link_rq_band <= band for band in p_link_rm_band]
        if False in link_check_flag:
            self.train_solution.route_result = False
            self.train_solution.result = False
            if self.train_solution.sfc_req_type == "arrive":
                self.train_solution.reason = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_LINK_BAND
            elif self.train_solution.sfc_req_type == "migrate":
                self.train_solution.reason = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_LINK_BAND
            return False
        
        # step 3: 检查路由是否满足时延约束
        if self.train_solution.sfc_actual_latency + map_path_weight > self.train_solution.sfc_req_latency:
            self.train_solution.route_result = False
            self.train_solution.result = False
            if self.train_solution.sfc_req_type == "arrive":
                self.train_solution.reason = SOLUTION_DEPLOY_TYPE.SET_FAILED_FOR_LATENCY
            elif self.train_solution.sfc_req_type == "migrate":
                self.train_solution.reason = SOLUTION_DEPLOY_TYPE.CHANGE_FAILED_FOR_LATENCY
            return False
        
        # endregion 路由检查通过
        self.train_solution.route_result = True
        
        # 全部检查通过
        self.train_solution.result = True
        
        return True


        
    def do_action(self,action):
        # embed node
        v_node_rq_cpu = self.v_net.nodes[self.curr_v_node_id]['request_cpu']
        v_node_rq_ram = self.v_net.nodes[self.curr_v_node_id]['request_ram']
        v_node_rq_rom = self.v_net.nodes[self.curr_v_node_id]['request_rom']

        if self.p_net_shared_node_array_mask[self.curr_v_node_id,action] == 0:
            # 执行动作部署在了非共享节点上
            self.p_net.opt_node_attrs_value(action,'remain_cpu','decrease',v_node_rq_cpu)
            self.p_net.opt_node_attrs_value(action,'remain_ram','decrease',v_node_rq_ram)
            self.p_net.opt_node_attrs_value(action,'remain_rom','decrease',v_node_rq_rom)
        else:
            # 执行动作部署在了共享节点上
            self.p_net.opt_node_attrs_value(action,'remain_rom','decrease',v_node_rq_rom)

        # embed link
        if len(self.train_solution.selected_actions) == 0:
            # 更新接入用户时的时延
            self.train_solution.sfc_actual_latency += self.get_latency_delay_to_ue("start",action)            
        else:
            last_action = self.train_solution.selected_actions[-1]
            v_link_rq_band = self.v_net.edges[(self.curr_v_node_id,self.curr_v_node_id-1)]['request_band']

            map_path = self.p_net.get_djikstra_path(last_action,action)
            if len(map_path) == 1: 
                map_link = [(map_path[0],map_path[0])]
                map_path_weight = 0
            else:
                map_link = [(map_path[i],map_path[i+1]) for i in range(len(map_path)-1)]
                map_path_weight = self.p_net.get_path_weight(map_path)

            for link in map_link:
                self.p_net.opt_link_attrs_value(link,'remain_band','decrease',v_link_rq_band)
                
            # 更新接入中间节点的实际累积时延
            self.train_solution.sfc_actual_latency += map_path_weight

            if len(self.train_solution.selected_actions) == len(self.v_net.nodes) - 1:
                # 更新结束节点时的时延
                self.train_solution.sfc_actual_latency += self.get_latency_delay_to_ue("end",action)
