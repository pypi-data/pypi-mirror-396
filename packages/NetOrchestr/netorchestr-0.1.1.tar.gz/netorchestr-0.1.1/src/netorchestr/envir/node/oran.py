
from astropy import units as u
from netorchestr.envir.node.base import NodeBase
from netorchestr.envir.networklayer import NetworkProtocolDuAAu
from netorchestr.envir.physicallayer import RadioPhy, EthernetPhy, RadioPhyWithBandLimit, RadioPhySimpleSDR


class DuAAuBase(NodeBase):
    """
    O-RAN 移动通信模型
    
    Du 为数据单元, AAU 为接入单元
    
    * Du 负责以有线的形式与核心的 Cu 交互
    * AAu 负责以无线的形式发出

    该节点模型不严格划分 Du 与 AAu 的功能实现
    
    仅通过网络层模块来实现 Du 与 AAu 的交互
    
    默认将数据包实现从有线接口到无线接口的互相传递
    
    """
    def __init__(self, name: str, transmission_delay_range:list[u.Quantity] = []):
        super().__init__(name)
        
        self.networkLayer = NetworkProtocolDuAAu(f"{self.name}_NetLayer")
        self.networkLayer.ofModule = self
        self.add_submodule(self.networkLayer)
        
        self.radioPhy = RadioPhyWithBandLimit(name = f"{self.name}_Radio", 
                                              range = 150*u.km,
                                              transmission_delay_range=transmission_delay_range)
        self.radioPhy.ofModule = self
        self.add_submodule(self.radioPhy)
        
        self.ethernetPhy = EthernetPhy(f"{self.name}_Eth")
        self.ethernetPhy.ofModule = self
        self.add_submodule(self.ethernetPhy)
        
        layer_module_list = [self.networkLayer, self.radioPhy]
        self.connect_layer_submodules(layer_module_list)
        
        layer_module_list = [self.networkLayer, self.ethernetPhy]
        self.connect_layer_submodules(layer_module_list)
        

class DuAAuSimpleSDR(NodeBase):
    def __init__(self, name: str, mode_perf_map:dict[str,dict[str,u.Quantity]]):
        """初始化基于 SDR 的 DuAAu 设备实例。

        该类用于创建 DuAAu 设备的简化 SDR (软件定义无线电) 实现，通过模式性能映射表
        定义不同通信模式下的性能参数（如通信距离、传输延迟范围等）。

        Args:
            name: 设备的名称标识符，用于唯一标识该 DuAAu 设备实例。
            mode_perf_map: 字典结构，键为通信模式名称 (如 "Sat_Ue"、"Sat_Ground"),
                值为该模式对应的性能参数字典。性能参数字典的键为参数名称 (如 "range"、
                "transmission_delay_range")，值为带单位的物理量 (`u.Quantity` 类型)。

        Example:
            初始化示例：
            >>> mode_perf = {
            ...     "Sat_Ue": {
            ...         "range": 3000 * u.km,
            ...         "transmission_delay_range": [20 * u.ms, 30 * u.ms]
            ...     },
            ...     "Sat_Ground": {
            ...         "range": 5000 * u.km,
            ...         "transmission_delay_range": [10 * u.ms, 25 * u.ms]
            ...     }
            ... }
            >>> sdr = DuAAuSimpleSDR(name="DuAAu_SDR_01", mode_perf_map=mode_perf)
        """
        super().__init__(name)
        
        self.networkLayer = NetworkProtocolDuAAu(f"{self.name}_NetLayer")
        self.networkLayer.ofModule = self
        self.add_submodule(self.networkLayer)
        
        self.radioPhy = RadioPhySimpleSDR(name = f"{self.name}_Radio", 
                                          mode_perf_map = mode_perf_map)
        self.radioPhy.ofModule = self
        self.add_submodule(self.radioPhy)
        
        self.ethernetPhy = EthernetPhy(f"{self.name}_Eth")
        self.ethernetPhy.ofModule = self
        self.add_submodule(self.ethernetPhy)
        
        layer_module_list = [self.networkLayer, self.radioPhy]
        self.connect_layer_submodules(layer_module_list)
        
        layer_module_list = [self.networkLayer, self.ethernetPhy]
        self.connect_layer_submodules(layer_module_list)

