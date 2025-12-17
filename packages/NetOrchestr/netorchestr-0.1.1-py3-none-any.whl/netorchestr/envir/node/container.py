

from netorchestr.envir.node.base import NodeBase
from netorchestr.envir.applications.vnfapp import VnfAppSrv4
from netorchestr.envir.networklayer import NetworkProtocolEndIpv4
from netorchestr.envir.physicallayer import EthernetPhy

class VnfBase(NodeBase):
    def __init__(self, name: str):
        super().__init__(name)
        
        self.appLayer = VnfAppSrv4(f"{self.name}_App",service_model="Poisson")
        self.appLayer.ofModule = self
        self.add_submodule(self.appLayer)
        # 停止应用层业务发送的时钟
        self.appLayer.clocktime.stop()
        
        self.networkLayer = NetworkProtocolEndIpv4(f"{self.name}_NetLayer")
        self.networkLayer.ofModule = self
        self.add_submodule(self.networkLayer)
        
        self.ethernetPhy = EthernetPhy(f"{self.name}_Eth")
        self.ethernetPhy.ofModule = self
        self.add_submodule(self.ethernetPhy)
        
        layer_module_list = [self.appLayer, self.networkLayer, self.ethernetPhy]
        self.connect_layer_submodules(layer_module_list)


class VnfContainer(NodeBase):
    def __init__(self, name: str, type: str, resouce_limit: dict = {}):
        """ VNF 容器节点类

        Args:
            name (str): 节点名称
            type (str): 节点类型
            resouce_limit (dict): 节点资源限制
        """
        super().__init__(name)
        
        self.type = type
        self.resouce_limit = resouce_limit
        
        self.appLayer = VnfAppSrv4(f"{self.name}_App",service_model="Stabled")
        self.appLayer.ofModule = self
        self.add_submodule(self.appLayer)
        # 停止应用层业务发送的时钟
        self.appLayer.clocktime.stop()
        
        self.networkLayer = NetworkProtocolEndIpv4(f"{self.name}_NetLayer")
        self.networkLayer.ofModule = self
        self.add_submodule(self.networkLayer)
        
        self.ethernetPhy = EthernetPhy(f"{self.name}_Eth")
        self.ethernetPhy.ofModule = self
        self.add_submodule(self.ethernetPhy)
        
        layer_module_list = [self.appLayer, self.networkLayer, self.ethernetPhy]
        self.connect_layer_submodules(layer_module_list)

    def update_resource_limit(self, resouce_limit: dict):
        """更新节点资源限制"""
        
        self.resouce_limit = resouce_limit

