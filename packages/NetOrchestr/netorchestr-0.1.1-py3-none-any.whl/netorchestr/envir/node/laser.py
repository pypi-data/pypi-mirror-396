
from astropy import units as u
from netorchestr.envir.node.base import NodeBase
from netorchestr.envir.networklayer import NetworkProtocolLaser
from netorchestr.envir.physicallayer import LaserPhy, EthernetPhy

class LaserBase(NodeBase):
    """激光通信模块

    Args:
        name (str): 节点名称
        
    默认将数据包实现从激光传输到以太网传输有线接口的互相传递
    """
    def __init__(self, name: str):
        super().__init__(name)
        
        self.networkLayer = NetworkProtocolLaser(f"{self.name}_NetLayer")
        self.networkLayer.ofModule = self
        self.add_submodule(self.networkLayer)
        
        self.aim_laser_ip = None
        """对接激光模块的IP地址"""
        
        self.laserPhy = LaserPhy(f"{self.name}_Laser")
        self.laserPhy.ofModule = self
        self.add_submodule(self.laserPhy)
        
        self.ethernetPhy = EthernetPhy(f"{self.name}_Eth")
        self.ethernetPhy.ofModule = self
        self.add_submodule(self.ethernetPhy)
        
        layer_module_list = [self.networkLayer, self.laserPhy]
        self.connect_layer_submodules(layer_module_list)
        
        layer_module_list = [self.networkLayer, self.ethernetPhy]
        self.connect_layer_submodules(layer_module_list)



