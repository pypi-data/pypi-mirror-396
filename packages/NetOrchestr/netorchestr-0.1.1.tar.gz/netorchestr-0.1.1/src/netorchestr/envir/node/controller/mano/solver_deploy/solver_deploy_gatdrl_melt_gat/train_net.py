
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_scatter import scatter
from torch_geometric.nn import GCNConv, global_add_pool, global_max_pool, global_mean_pool
from torch_geometric.utils import to_dense_batch
import code

class ActorCritic(nn.Module):
    def __init__(self, p_net_num_nodes, p_net_feature_dim, v_net_feature_dim, embedding_dim=64):
        super(ActorCritic, self).__init__()
        self.encoder = Encoder(v_net_feature_dim, embedding_dim=embedding_dim)
        self.actor = Actor(p_net_num_nodes, p_net_feature_dim, v_net_feature_dim, embedding_dim)
        self.critic = Critic(p_net_num_nodes, p_net_feature_dim, v_net_feature_dim, embedding_dim)
        self._last_hidden_state = None

    def encode(self, obs):
        """使用 GRU 编码器对输入的 v_net 输出进行编码，并返回编码后的特征

        Args:
            obs (dict): 包含 v_net 输出特征的字典，键为 'v_net_x', 值为 FloatTensor, 维度为 (batch_size, v_net_node_num, v_net_feature_dim)
            
        Returns:
            outputs (FloatTensor): 编码后的特征，维度为 (v_net_node_num, batch_size, embedding_dim)
        """
        x = obs['v_net_x']
        outputs, hidden_state = self.encoder(x)
        self._last_hidden_state = hidden_state
        return outputs

    def act(self, obs):
        """演员网络执行动作

        Args:
            obs (dict): 环境的当前观测，包含了智能体做出决策所需的所有信息
            
                {
                    'p_net': p_net_obs, # PyTorch Geometric 单图数据结构, 类型为 Batch, 包含节点特征、边索引、边属性等信息, 类型为 Data
                    'p_net_node': p_net_node, #  当前关注的节点, 类型为 LongTensor, 形状为 (1,)
                    'hidden_state': hidden_state, # 循环神经网络 GRU 输出的隐藏状态, 类型为 FloatTensor, 形状为 (1, 1, embedding_dim)
                    'encoder_outputs': encoder_outputs # 编码器输出, 类型为 FloatTensor, 形状为 (1, v_node_num, embedding_dim)
                }

        Returns:
            logits (FloatTensor): 动作对数几率 logits, 类型为 FloatTensor, 形状为 (1, p_node_num)
        """
        logits, outputs, hidden_state = self.actor(obs)
        self._last_hidden_state = hidden_state
        return logits

    def evaluate(self, obs):
        """评估网络输出的动作价值

        Args:
            obs (dict): 环境的当前观测，包含了智能体做出决策所需的所有信息
            
                {
                    'p_net': p_net_obs, # PyTorch Geometric 单图数据结构, 类型为 Batch, 包含节点特征、边索引、边属性等信息, 类型为 Data
                    'p_net_node': p_net_node, #  当前关注的节点, 类型为 LongTensor, 形状为 (1,)
                    'hidden_state': hidden_state, # 循环神经网络 GRU 输出的隐藏状态, 类型为 FloatTensor, 形状为 (1, 1, embedding_dim)
                    'encoder_outputs': encoder_outputs # 编码器输出, 类型为 FloatTensor, 形状为 (1, v_node_num, embedding_dim)
                }

        Returns:
            value (FloatTensor): 评估网络输出的价值, 类型为 FloatTensor, 形状为 (1, 1)
        """
        value = self.critic(obs)
        
        return value

    def get_last_rnn_state(self):
        return self._last_hidden_state

    def set_last_rnn_hidden(self, hidden_state):
        self._last_hidden_state = hidden_state


class Actor(nn.Module):
    def __init__(self, p_net_num_nodes, p_net_feature_dim, v_net_feature_dim, embedding_dim=64):
        super(Actor, self).__init__()
        self.decoder = Decoder(p_net_num_nodes, p_net_feature_dim, embedding_dim=embedding_dim)

    def forward(self, obs):
        """Return logits of actions

        Args:
            obs (dict): 环境的当前观测，包含了智能体做出决策所需的所有信息
            
                {
                    'p_net': p_net_obs, # PyTorch Geometric 单图数据结构, 类型为 Batch, 包含节点特征、边索引、边属性等信息, 类型为 Data
                    'p_net_node': p_net_node, #  当前关注的节点, 类型为 LongTensor, 形状为 (1,)
                    'hidden_state': hidden_state, # 循环神经网络 GRU 输出的隐藏状态, 类型为 FloatTensor, 形状为 (1, 1, embedding_dim)
                    'encoder_outputs': encoder_outputs # 编码器输出, 类型为 FloatTensor, 形状为 (1, v_node_num, embedding_dim)
                }

        Returns:
            logits (FloatTensor): 动作对数几率 logits, 类型为 FloatTensor, 形状为 (1, p_node_num)
            
            outputs (FloatTensor): 当前时间步的 GRU 输出, 类型为 FloatTensor, 形状为 (1, 1, embedding_dim)
            
            hidden_state (FloatTensor): 更新后的隐藏状态, 类型为 FloatTensor, 形状为 (1, 1, embedding_dim)
        """
        
        logits, outputs, hidden_state = self.decoder(obs)
        return logits, outputs, hidden_state


class Critic(nn.Module):
    def __init__(self, p_net_num_nodes, p_net_feature_dim, v_net_feature_dim, embedding_dim=64):
        """Critic of the Actor-Critic network.
        
        Args:
            p_net_num_nodes (int): p_net 节点数量
            p_net_feature_dim (int): p_net 输入特征的维度
            v_net_feature_dim (int): v_net 输入特征的维度
            embedding_dim (int): 嵌入维度 (默认 64, 即编码后的特征维度)
            
        Note:
            价值网络 (Value Network) 的核心, 基于当前观测, 计算当前状态的价值 value 评估 “当前状态有多好”
            
            Critic 和 Actor 复用 Decoder 结构，共享底层特征提取能力（比如 p_net 的 GCN 结构特征、V 网的注意力特征、GRU 时序特征）
            
            减少参数冗余，提升训练效率（这是 Actor-Critic 框架的常见设计）
            
            虽然结构相同，但 Actor 和 Critic 的 Decoder 是两个独立实例, 各自有独立的权重参数, 训练时分别更新 (Actor 用策略梯度更新, Critic 用 MSE 损失更新价值预测)
            
            Actor 需要为每个可能的动作分配分数, 因此输出维度与动作数一致; Critic 只需评估 “当前状态” 的整体价值, 因此输出是标量 (压缩所有动作维度为 1).
            
        """
        
        super(Critic, self).__init__()
        
        # Critic 的 self.decoder 与 Actor 的 self.decoder 是完全相同的 Decoder 类实例（结构、参数独立，但网络结构一致）
        self.decoder = Decoder(p_net_num_nodes, p_net_feature_dim, embedding_dim=embedding_dim)

    def forward(self, obs):
        """Return logits of actions
        
        Args:
            obs (dict): 环境的当前观测，包含了智能体做出决策所需的所有信息
            
                {
                    'p_net': p_net_obs, # PyTorch Geometric 单图数据结构, 类型为 Batch, 包含节点特征、边索引、边属性等信息, 类型为 Data
                    'p_net_node': p_net_node, #  当前关注的节点, 类型为 LongTensor, 形状为 (1,)
                    'hidden_state': hidden_state, # 循环神经网络 GRU 输出的隐藏状态, 类型为 FloatTensor, 形状为 (1, 1, embedding_dim)
                    'encoder_outputs': encoder_outputs # 编码器输出, 类型为 FloatTensor, 形状为 (1, v_node_num, embedding_dim)
                }

        Returns:
            value (FloatTensor): 评估网络输出的价值, 类型为 FloatTensor, 形状为 (1, 1)
        """
        
        # 输入 obs 与 Actor 完全一致（含 p_net 图数据、hidden_state、encoder_outputs 等）
        # 因此 Decoder 输出的 logits 维度也和 Actor 相同：(1, p_node_num)（1 是 batch_size，p_node_num 是 p_net 节点数）
        # 这里的 logits 并非 “动作对数几率”（Actor 中是），而是 Decoder 最后一层 MLP 输出的 “节点分数”，仅作为中间特征使用。
        logits, outputs, hidden_state = self.decoder(obs)
        
        # 计算状态价值
        # 对 Decoder 输出的 logits 做最后一维的均值计算（dim=-1 即对 p_node_num 维度求平均）(1, p_node_num) → (1, 1)
        # 本质上是通过对所有 p_net 节点的分数取平均，得到一个标量价值，这个标量代表当前观测状态的 “整体好坏程度”（比如未来期望回报）。
        value = torch.mean(logits, dim=-1, keepdim=True)
        
        return value


class Encoder(nn.Module):
    def __init__(self, v_net_feature_dim, embedding_dim=64):
        """Encoder of the Actor-Critic network.
        
        Args:
            v_net_feature_dim (int): v_net 输入特征的维度
            embedding_dim (int): 嵌入维度 (默认 64, 即编码后的特征维度)
        """
        super(Encoder, self).__init__()
        
        self.emb = nn.Linear(v_net_feature_dim, embedding_dim)
        """线性嵌入层"""
        
        self.gru = nn.GRU(embedding_dim, embedding_dim)
        """GRU循环神经网络层"""

    def forward(self, x):
        """Encoder forward
        
        对输入的特征数据进行编码，输出序列编码结果和最终的隐藏状态

        Args:
            x (FloatTensor): 维度为 (batch_size, seq_len, feature_dim)
            
            例如 (1 * v_net_node_num * v_net_feature_dim)

        Returns:
            outputs (FloatTensor): 为 GRU 每个时间步的输出，维度为 (seq_len, batch_size, embedding_dim) → (v_node_num, 1, 64)
            hidden_state (FloatTensor): 最后一个时间步的隐藏状态，维度为 (num_layers * num_directions, batch_size, embedding_dim) → (1, batch_size, 64)

        """
        # 调整维度顺序, 维度变为：(seq_len, batch_size, feature_dim) 以匹配 GRU 层要求输入
        x = x.permute(1, 0, 2)
        
        # self.emb 特征嵌入, 将输入的 feature_dim 维特征映射到 64 维, 得到 (seq_len, batch_size, 64)
        # F.relu 应用激活函数，增加非线性表达能力, 得到仍为 (seq_len, batch_size, 64)
        embeddings = F.relu(self.emb(x))
        
        # self.gru 循环神经网络层, 输出为 (seq_len, batch_size, 64)
        # outputs 为 GRU 每个时间步的输出，维度为 (seq_len, batch_size, embedding_dim) → (v_node_num, 1, 64)
        # hidden_state 为最后一个时间步的隐藏状态，维度为 (num_layers * num_directions, batch_size, embedding_dim) 
        #   → 此处因默认单层单向 GRU，故为 (1, 1, 64)（对应注释中的 1 * 1 * embedding_dim）
        outputs, hidden_state = self.gru(embeddings)

        return outputs, hidden_state
    

class Decoder(nn.Module):
    def __init__(self, p_net_num_nodes, feature_dim, embedding_dim=64):
        super(Decoder, self).__init__()
        
        # 嵌入层将离散的整数索引（如单词 ID、类别 ID）映射为连续的低维向量（嵌入向量），是 NLP、推荐系统等领域的基础组件
        #     输入：一批整数索引（形状通常为 (batch_size, sequence_length)，每个元素是单个离散 ID）
        #     输出：对应的嵌入向量（形状为 (batch_size, sequence_length, embedding_dim)，每个 ID 被替换为长度为 embedding_dim 的向量）
        #     核心价值：将离散特征转化为连续向量，让模型能学习到特征间的语义关联
        self.emb = nn.Embedding(p_net_num_nodes + 1, embedding_dim)
        
        self.att = Attention(embedding_dim)
        
        self.gat = GCNConvNet(feature_dim, embedding_dim, embedding_dim=embedding_dim, dropout_prob=0., return_batch=True)
        
        self.mlp = nn.Sequential(
            nn.Linear(embedding_dim, 1),
            nn.Flatten()
        )
        
        self.gru = nn.GRU(embedding_dim, embedding_dim)
        self._last_hidden_state = None
        
        self.distance_decay = DistanceDecayAttention()

    def forward(self, obs:dict):
        """Decoder foward

        Args:
            obs (dict): 环境的当前观测，包含了智能体做出决策所需的所有信息
            
                {
                    'p_net': p_net_obs, # PyTorch Geometric 单图数据结构, 类型为 Batch, 包含节点特征、边索引、边属性等信息, 类型为 Data
                    'p_net_node': p_net_node, # 当前关注的节点, 类型为 LongTensor, 形状为 (1,)
                    'hidden_state': hidden_state, # 循环神经网络 GRU 输出的隐藏状态, 类型为 FloatTensor, 形状为 (1, 1, embedding_dim)
                    'encoder_outputs': encoder_outputs # 编码器输出, 类型为 FloatTensor, 形状为 (1, v_node_num, embedding_dim)
                }

        Returns:
            logits (FloatTensor): 动作对数几率 logits, 类型为 FloatTensor, 形状为 (1, p_node_num)
            outputs (FloatTensor): 当前时间步的 GRU 输出, 类型为 FloatTensor, 形状为 (1, 1, embedding_dim)
            hidden_state (FloatTensor): 更新后的隐藏状态, 类型为 FloatTensor, 形状为 (1, 1, embedding_dim)
        """
        # 1. 从观测中提取核心数据
        # 提取 p_net 节点特征, PyG 的 Batch 对象（单图场景），含 x（p_node_num, p_net_feature_dim）、edge_index（2, p_edge_num）、batch（节点归属标记）
        batch_p_net = obs['p_net']
        # 提取 GRU 上一步隐藏状态, 维度 (1, 1, embedding_dim)
        hidden_state = obs['hidden_state']
        # 当前关注的节点, 类型为 LongTensor, 维度 (1,)（长整型）。
        p_node_id = obs['p_net_node']
        # 编码器输出, 类型为 FloatTensor, 维度 (1, v_node_num, embedding_dim)
        encoder_outputs = obs['encoder_outputs']
        # 动作掩码（可选）
        mask = obs.get('mask',None)
        
        # 2. 调整隐藏状态维度适配 GRU 输入格式, 维度变为 (1, 1, embedding_dim)
        # 从 (1,1,64) → (1,1,64)（因原维度已符合 GRU 要求，此步不改变形状，仅确保格式统一）
        # GRU 要求隐藏状态格式：(num_layers*num_directions, batch_size, embedding_dim)
        hidden_state = hidden_state.permute(1, 0, 2)
        
        # 3. 节点嵌入与注意力机制
        p_node_emb = self.emb(p_node_id).unsqueeze(0) # 输出维度：(1, 1, 64)
        # self.emb 是 Embedding 层（输入范围 0~p_net_num_nodes，输出 64 维）
        # p_node_id (1,) → Embedding 后 (1,64) → unsqueeze(0) 新增 GRU 所需的 seq_len 维度（此处 seq_len=1）
        context, attention = self.att(hidden_state, encoder_outputs, mask)
        # 注意力机制融合 V 网编码特征与 GRU 隐藏状态, 输出维度：(1, 1, embedding_dim), (1, v_node_num, embedding_dim)
        
        # 4. GRU 时序建模：更新隐藏状态
        outputs, hidden_state = self.gru(p_node_emb, hidden_state)
        # outputs：当前时间步的 GRU 输出, 与输入序列长度一致，此处为 (1,1,64)
        # hidden_state：更新后的隐藏状态, 融合了当前节点信息与历史时序信息，用于下一轮决策
        
        # 5. GAT 图特征提取：学习 p_net 节点的结构特征, 输出维度：(p_node_num, 64)
        p_node_embeddings = self.gat(batch_p_net)
        # 调整维度：适配 batch 格式, batch_p_net.num_graphs=1（单图场景），reshape 后新增 batch 维度，符合后续融合逻辑, 输出维度：(1, p_node_num, 64)
        p_node_embeddings = p_node_embeddings.reshape(batch_p_net.num_graphs, -1, p_node_embeddings.shape[-1])
        # 融合上下文向量（v_net 注意力特征）与 p_net 结构特征, 由于广播机制相加后得到的维度仍为 (1, p_node_num, 64)
        p_node_embeddings = p_node_embeddings + context
        
        # 6. MLP 输出动作对数几率 logits, 输出维度：(1, p_node_num)
        logits = self.mlp(p_node_embeddings)
        # self.mlp 是简单的两层网络：
        # - 第一层：Linear(64, 1) → 将每个 p_net 节点的 64 维特征映射为 1 维分数，输出 (1, p_node_num, 1)
        # - 第二层：Flatten() → 展平为 (1, p_node_num)，即每个 p_net 节点对应一个动作分数（未归一化）
        
        # 7. 距离衰减修正
        logits = self.distance_decay(
                obs={"batch_p_net": batch_p_net,
                     "p_node_id": p_node_id,
                    }, 
                logits=logits
            )
        
        return logits, outputs, hidden_state


class Attention(nn.Module):
    def __init__(self, hidden_dim):
        """注意力机制网络

        Args:
            hidden_dim (int): 循环神经网络 GRU 输出的隐藏状态的维度
        """
        
        super().__init__()
        self.attn = nn.Linear(hidden_dim * 2, hidden_dim)
        self.v = nn.Linear(hidden_dim, 1, bias=False)

    def forward(self, hidden, encoder_outputs, mask=None):
        """Attention forward

        Args:
            hidden (FloatTensor): 循环神经网络 GRU 输出的隐藏状态, 类型为 FloatTensor, 形状为 (num_layers * num_directions, batch_size, hidden_dim) -> (1, 1, embedding_dim)
            encoder_outputs (FloatTensor): 编码器输出, 类型为 FloatTensor, 形状为 (batch_size, seq_len, hidden_dim * num_directions) -> (1, v_node_num, embedding_dim)
            mask (BoolTensor, optional): 动作掩码（可选）, 类型为 BoolTensor, 形状为 (1, v_node_num)

        Returns:
            context (FloatTensor): 注意力机制融合后的特征, 类型为 FloatTensor, 形状为 (1, 1, embedding_dim)
            attn_weights (FloatTensor): 注意力权重, 类型为 FloatTensor, 形状为 (1, v_node_num)
        """
        batch_size = encoder_outputs.size(0)
        seq_len = encoder_outputs.size(1)
        
        # 调整 hidden_state 维度：从 (1,1,64) → (1, v_node_num, 64) 通过重复 v_node_num 次实现与 encoder_outputs 对齐
        hidden = hidden.transpose(0, 1).repeat(1, seq_len, 1)  # shape: (batch_size, seq_len, hidden_dim)
        
        # 拼接 hidden_state 与 encoder_outputs：维度 (1, v_node_num, 128) → 经线性层压缩为 (1, v_node_num, 64)，再通过 tanh 激活。
        energy = torch.tanh(self.attn(torch.cat([hidden, encoder_outputs], dim=2)))  # shape: (batch_size, seq_len, hidden_dim)
        
        # 计算注意力权重：通过 self.v 线性层将 64 维特征映射为 1 维分数 → softmax 归一化，得到 (1, v_node_num) 的权重（表示每个 v_net 节点的重要性）。
        attn_weights = F.softmax(self.v(energy).squeeze(2), dim=1)  # shape: (batch_size, seq_len)
        
        # 应用掩码（若有）：将不可行动作对应的权重置为 -1e10，使其在 softmax 后概率趋近于 0。
        if mask is not None:
            attn_weights = attn_weights.masked_fill(mask == 0, -1e10)
            
        # 计算上下文向量 context：通过矩阵乘法（bmm）将 V 网特征与注意力权重加权求和，得到 (1,1,64) 的全局特征（融合了 v_net 关键信息）。
        context = torch.bmm(attn_weights.unsqueeze(1), encoder_outputs)  # shape: (batch_size, 1, hidden_dim * num_directions)
        
        return context, attn_weights
    

class GraphPooling(nn.Module):
    def __init__(self, aggr='sum', **kwargs):
        super(GraphPooling, self).__init__()
        if aggr in ['att', 'attention']:
            output_dim = kwargs.get('output_dim')
            self.pooling = GraphAttentionPooling(output_dim)
        elif aggr in ['add', 'sum']:
            self.pooling = global_add_pool
        elif aggr == 'max':
            self.pooling = global_max_pool
        elif aggr == 'mean':
            self.pooling = global_mean_pool
        else:
            return NotImplementedError

    def forward(self, x, batch):
        return self.pooling(x, batch)


class GCNConvNet(nn.Module):
    """Graph Attention Network (GAT) for graph feature extraction"""
    def __init__(self, input_dim, output_dim, embedding_dim=128, num_layers=3, batch_norm=True, dropout_prob=1.0, 
                 return_batch=False, pooling=None, **kwargs):
        """
            Args:
                input_dim (int): input feature dimension
                output_dim (int): output feature dimension
                embedding_dim (int, optional): hidden feature dimension. Defaults to 128.
                num_layers (int, optional): number of GCN layers. Defaults to 3.
                batch_norm (bool, optional): whether to use batch normalization. Defaults to True.
                dropout_prob (float, optional): dropout probability. Defaults to 1.0.
                return_batch (bool, optional): whether to return batch vector. Defaults to False.
                pooling (str, optional): graph pooling method. Defaults to None.

        """
        super(GCNConvNet, self).__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.num_layers = num_layers
        self.return_batch = return_batch
        self.pooling = pooling
        if self.pooling is not None:
            self.graph_pooling = GraphPooling(aggr=pooling, output_dim=output_dim)

        for layer_id in range(self.num_layers):
            if self.num_layers == 1:
                conv = GCNConv(input_dim, output_dim)
            elif layer_id == 0:
                conv = GCNConv(input_dim, embedding_dim)
            elif layer_id == num_layers - 1:
                conv = GCNConv(embedding_dim, output_dim)
            else:
                conv = GCNConv(embedding_dim, embedding_dim)
                
            norm_dim = output_dim if layer_id == num_layers - 1 else embedding_dim
            
            # 批量归一化, 对特征维度进行标准化处理，减少 “内部协变量偏移（Internal Covariate Shift）”，加速模型训练并提升稳定性
            #   训练过程中，每一层的输入特征分布可能会因前层参数更新而发生变化（即 “协变量偏移”），导致后层需要不断适应新的分布，减慢训练速度，甚至导致梯度爆炸 / 消失
            #   nn.BatchNorm1d 通过以下步骤解决这个问题：
            #   1. 计算批次统计量：对当前批次（batch）的所有样本，在每个特征维度上计算均值 μ 和方差 σ²；
            #   2. 标准化：将每个特征值减去均值、除以标准差（加小 epsilon 避免除零），得到均值为 0、方差为 1 的标准化特征；
            #   3. 缩放与偏移（可训练）：引入两个可训练参数 γ（缩放因子）和 β（偏移因子），让模型自主学习是否保留标准化后的分布（γ=1, β=0 时等价于纯标准化，否则可调整特征分布）
            #   GCN 的每一层输出是节点特征矩阵（形状 (num_nodes, feature_dim)），nn.BatchNorm1d 作用于 特征维度（feature_dim 维），即对每个特征维度的所有节点进行批量归一化。
            norm = nn.BatchNorm1d(norm_dim) if batch_norm else nn.Identity()
            
            # 随机失活, 随机丢弃部分神经元（特征），强制模型学习 “冗余特征表示”，避免过度依赖某些特定特征，从而增强泛化能力（防止过拟合）。
            #    以概率 p 随机将输入特征矩阵中的部分元素置为 0，测试时则关闭 dropout，同时将所有特征值乘以 (1-p)，确保测试时的输出分布与训练时一致。
            #    通常作用于节点特征矩阵，随机丢弃部分节点的特征维度（或部分节点的全部特征），打破特征间的 “共适应性”（即避免模型过度依赖某些强特征，忽略其他潜在有用的弱特征）。
            dout = nn.Dropout(dropout_prob) if dropout_prob < 1. else nn.Identity()

            self.add_module('conv_{}'.format(layer_id), conv)
            self.add_module('norm_{}'.format(layer_id), norm)
            self.add_module('dout_{}'.format(layer_id), dout)

        self._init_parameters()

    def _init_parameters(self):
        for layer_id in range(self.num_layers):
            nn.init.orthogonal_(getattr(self, f'conv_{layer_id}').lin.weight)

    def forward(self, input):
        """GCNConvNet forward

        Args:
            input (Data): PyG 的 Batch 对象（单图场景），含 x (p_node_num, p_net_feature_dim)、edge_index (2, p_edge_num)、batch (节点归属标记)

        Returns:
            x (FloatTensor): 每个 p_net 节点的结构特征 (1, p_node_num, 64)
            
        Note:
            中间层用 leaky_relu, 最后层用 BatchNorm + Dropout
        """
        
        x, edge_index, edge_attr = input['x'], input['edge_index'], input['edge_attr']
        
        for layer_id in range(self.num_layers):
            conv = getattr(self, 'conv_{}'.format(layer_id))
            norm = getattr(self, 'norm_{}'.format(layer_id))
            dout = getattr(self, 'dout_{}'.format(layer_id))
            x = conv(x, edge_index)
            if layer_id == self.num_layers - 1:
                x = dout(norm(x))
            else:
                x = F.leaky_relu(dout(norm(x)))
                
        if self.return_batch:
            # 将 PyG 的默认批量处理方式（稀疏模式）的稀疏批量表示转换为更直观的密集批量表示
            #     x 的维度为 (batch_size, max_num_nodes_in_batch, 64)
            #     mask 为标识填充节点的掩码，维度为 (batch_size, max_num_nodes_in_batch)
            x, mask = to_dense_batch(x, input.batch)
            
        if self.pooling is not None:
            x = self.graph_pooling(x, input.batch)
            
        return x


class DistanceDecayAttention(nn.Module):
    def __init__(self, decay_rate=0.2):
        super(DistanceDecayAttention, self).__init__()
        self.decay_rate = decay_rate    # 时延衰减系数（控制衰减速度）
    
    def _compute_single_latency_distance(self, edge_index, effective_latency, num_nodes, target_node_id):
        """
        为单个样本计算最短时延距离, Dijkstra 算法的单次执行
        
        这里的 edge_index 和 effective_latency 已经是针对单个图的了
        """
        adj = [[] for _ in range(num_nodes)]
        for i in range(edge_index.shape[1]):
            u = edge_index[0, i].item()
            v = edge_index[1, i].item()
            latency = effective_latency[i].item()
            if latency == 1.0:
                continue
            adj[u].append((v, latency))
            adj[v].append((u, latency))

        distance = [float('inf')] * num_nodes
        distance[target_node_id] = 0
        heap = []
        import heapq
        heapq.heappush(heap, (0, target_node_id))

        while heap:
            current_dist, u = heapq.heappop(heap)
            if current_dist > distance[u]:
                continue
            for v, latency in adj[u]:
                if distance[v] > distance[u] + latency:
                    distance[v] = distance[u] + latency
                    heapq.heappush(heap, (distance[v], v))

        return distance
    
    def _compute_batch_latency_distance(self, batch_p_net, p_node_id):
        """
        为整个批次计算最短时延距离 (假设批次中所有图的节点数和边数都相同)。

        Args:
            batch_p_net (DataBatch): 包含批量图数据的 DataBatch 对象。
            p_node_id (torch.Tensor): 批次中每个图对应的目标节点 ID, 形状为 (batch_size,).

        Returns:
            torch.Tensor: 批次中每个图的最短时延距离矩阵, 形状为 (batch_size, NUM_NODES)。
        """
        batch_size = batch_p_net.num_graphs
        device = batch_p_net.x.device

        # 每个图的节点数和边数是固定的
        NUM_NODES = batch_p_net.x.shape[0] // batch_size
        NUM_EDGES = batch_p_net.edge_index.shape[1] // batch_size
        
        # 从 batch_p_net 中提取批量数据
        # edge_index: [2, total_edges] -> 我们将在循环中按块处理
        edge_index = batch_p_net.edge_index
        edge_attr = batch_p_net.edge_attr # [total_edges, N] 或 [batch_size, total_edges_per_batch, N]

        # 初始化一个批次距离张量，并用 inf 填充
        batch_distance = torch.full((batch_size, NUM_NODES), float('inf'), device=device)

        for i in range(batch_size):
            # --- 计算当前图的节点偏移量 ---
            # ptr[i] 是第 i 个图的第一个节点在全局节点列表中的索引
            node_offset = batch_p_net.ptr[i].item()
            
            # --- 提取单个图的数据 ---
            # 1. 提取边索引
            # 每个图有 NUM_EDGES 条边，所以第 i 个图的边是从 i*NUM_EDGES 到 (i+1)*NUM_EDGES
            start_idx = i * NUM_EDGES
            end_idx = start_idx + NUM_EDGES
            single_edge_index_global = edge_index[:, start_idx:end_idx]
            single_edge_index_local = single_edge_index_global - node_offset

            # 2. 提取边属性并计算有效时延
            single_edge_attr_batch = edge_attr[start_idx:end_idx, :]
            # 计算有效时延 (例如，取第一个采样点)
            if single_edge_attr_batch.dim() == 2 and single_edge_attr_batch.shape[1] > 1:
                effective_latency = single_edge_attr_batch[:, 0]
            else:
                effective_latency = single_edge_attr_batch.squeeze(-1)

            # 3. 提取目标节点 ID
            single_target_node_id = p_node_id[i].item()

            # --- 计算单个图的最短时延距离 ---
            distance_i = self._compute_single_latency_distance(
                edge_index=single_edge_index_local,
                effective_latency=effective_latency,
                num_nodes=NUM_NODES,
                target_node_id=single_target_node_id
            )

            # 将结果放入批次张量中
            batch_distance[i, :] = torch.tensor(distance_i, dtype=torch.float32, device=device)

        return batch_distance
    
    def forward(self, obs, logits):
        """基于最短时延修正动作 logits

        Args:
            edge_index: 物理网络边索引 (2, p_edge_num)
            edge_attr: 边时延属性
            num_nodes: 节点总数
            last_node_id: 上一部署节点 ID
            logits: 原始动作 logits

        Returns:
            adjusted_logits: 修正后的动作 logits
        """
        # 计算最短时延距离
        latency_distance = self._compute_batch_latency_distance(
            batch_p_net=obs['batch_p_net'],
            p_node_id=obs['p_node_id']
        )
        
        # 生成时延衰减系数：采用指数衰减，时延越小系数越大
        decay_coeff = torch.exp(-self.decay_rate * latency_distance)
        
        # 对无穷大距离（不可达节点）设置极小衰减系数
        decay_coeff[latency_distance == float('inf')] = 1e-8
        
        # 修正 logits
        adjusted_logits = logits * decay_coeff
        
        return adjusted_logits


class GraphAttentionPooling(nn.Module):
    """Attention module to extract global feature of a graph."""
    def __init__(self, input_dim):
        super(GraphAttentionPooling, self).__init__()
        self.input_dim = input_dim
        self.weight = nn.Parameter(torch.Tensor(self.input_dim, self.input_dim))
        self._init_parameters()

    def _init_parameters(self):
        """Initializing weights."""
        nn.init.orthogonal_(self.weight)

    def forward(self, x, batch, size=None):
        """
        Making a forward propagation pass to create a graph level representation.

        Args:
            x (torch.Tensor): Result of the GNN.
            batch (torch.Tensor): Batch vector, which assigns each node to a specific example
            size (int, optional): Number of nodes in the graph. Defaults to None.

        Returns:
            representation: A graph level representation matrix.
        """
        size = batch[-1].item() + 1 if size is None else size
        mean = scatter(x, batch, dim=0, dim_size=size, reduce='mean')
        transformed_global = torch.tanh(torch.mm(mean, self.weight))

        coefs = torch.sigmoid((x * transformed_global[batch] * 10).sum(dim=1))
        weighted = coefs.unsqueeze(-1) * x

        return scatter(weighted, batch, dim=0, dim_size=size, reduce='add')

    def get_coefs(self, x):
        mean = x.mean(dim=0)
        transformed_global = torch.tanh(torch.matmul(mean, self.weight))

        return torch.sigmoid(torch.matmul(x, transformed_global))


def apply_mask_to_logit(logit, mask=None):
    """
    对动作的对数几率 (logit) 施加掩码

    Args:
        logit (tensor): 输入的对数几率 tensor
        mask (tensor, optional): 掩码 tensor, 形状为 (batch_size, p_node_num)
        
    Returns:
        masked_logit (tensor): 经过掩码后的对数几率 tensor, 形状为 (batch_size, p_node_num). 
        可行动作保留原始 logit, 不可行动作的 logit 被替换为 -1e8, 后续 softmax 后不可行动作的概率几乎为 0
    """
    if mask is None:
        return logit
    
    # 掩码格式标准化
    if not isinstance(mask, torch.Tensor):
        mask = torch.BoolTensor(mask) # 非张量类型转为布尔张量
    # 确保掩码是 PyTorch 布尔张量, 把掩码移动到与 logit 相同的计算设备（CPU/GPU），避免设备不匹配报错。
    # 调整掩码维度 reshape(logit.size())，确保和 logit 完全一致
    mask = mask.bool().to(logit.device).reshape(logit.size())

    # 生成掩码用的极小值张量
    NEG_TENSER = torch.tensor(-1e8).float()
    # 让极小值张量的类型（如 float32/float64）和设备，与 logit 保持一致，确保计算兼容
    mask_value_tensor = NEG_TENSER.type_as(logit).to(logit.device)
    # 按条件选择元素 —— 条件为 True 时取 x（原始 logit），为 False 时取 y（极小值 -1e8）
    masked_logit = torch.where(mask, logit, mask_value_tensor)
    
    return masked_logit


if __name__ == "__main__":
    device = torch.device('cpu')
    policy = ActorCritic(p_net_num_nodes=100, p_net_feature_dim=5, v_net_feature_dim=2, embedding_dim=64).to(device)

    code.interact(banner="",local=locals())
