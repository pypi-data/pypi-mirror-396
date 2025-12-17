import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv

print("检查是否有可用的 GPU: ", torch.cuda.is_available()) 
print("查看当前使用的 GPU 设备编号: ", torch.cuda.current_device())
print("查看 GPU 名称: ", torch.cuda.get_device_name(0))

# 检查是否有可用的 GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# 定义图数据
edge_index = torch.tensor([[0, 1, 1, 2], [1, 0, 2, 1]], dtype=torch.long)  # 边索引
x = torch.tensor([[1], [2], [3]], dtype=torch.float)  # 节点特征

# 将图数据移动到 GPU
edge_index = edge_index.to(device)
x = x.to(device)

# 创建 PyG 的 Data 对象
data = Data(x=x, edge_index=edge_index)

# 定义 GCN 模型
class GCN(nn.Module):
    def __init__(self):
        super(GCN, self).__init__()
        self.conv1 = GCNConv(1, 16)  # 输入维度 1，输出维度 16
        self.conv2 = GCNConv(16, 2)  # 输入维度 16，输出维度 2

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)  # 第一层 GCN
        x = F.relu(x)  # 激活函数
        x = self.conv2(x, edge_index)  # 第二层 GCN
        return x

# 实例化模型并移动到 GPU
model = GCN().to(device)

# 前向传播
output = model(data.x, data.edge_index)
print(output)
