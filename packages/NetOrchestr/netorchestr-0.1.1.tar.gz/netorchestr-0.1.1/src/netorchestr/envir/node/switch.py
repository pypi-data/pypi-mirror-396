
from netaddr import IPAddress
from netorchestr.envir.node.base import NodeBase
from netorchestr.envir.networklayer import NetworkProtocolMiddleIpv4
from netorchestr.envir.physicallayer import EthernetPhy

class SwitchBase(NodeBase):
    def __init__(self,name:str):
        super().__init__(name)        
        
        self.networkLayer = NetworkProtocolMiddleIpv4(f"{self.name}_NetLayer")
        self.networkLayer.ofModule = self
        self.add_submodule(self.networkLayer)
        
        self.ethernetPhyList:list[EthernetPhy] = []
    
    def add_ethernetPhy(self) -> EthernetPhy:
        ethernetPhy = EthernetPhy(f"{self.name}_Eth{len(self.ethernetPhyList)}")
        ethernetPhy.ofModule = self
        self.ethernetPhyList.append(ethernetPhy)
        self.add_submodule(ethernetPhy)
        
        layer_module_list = [self.networkLayer, ethernetPhy]
        self.connect_layer_submodules(layer_module_list)
        
        return ethernetPhy
    
    def delete_ethernetPhy(self, ethernetPhy:EthernetPhy):
        self.ethernetPhyList.remove(ethernetPhy)
        self.remove_submodule(ethernetPhy)


class SwitchRouter(NodeBase):
    def __init__(self,name:str):
        super().__init__(name)        
        
        self.networkLayer = NetworkProtocolMiddleIpv4(f"{self.name}_NetLayer")
        self.networkLayer.ofModule = self
        self.add_submodule(self.networkLayer)
        
        self.ethernetPhyMap:dict[IPAddress,EthernetPhy] = {}
        """
        路由器的以太网物理层映射表
        * 键为该路由器的物理层接口所连接设备的IP地址
        * 值为对应的以太网物理层模块
        """
        
    def add_ethernetPhy(self, device_ip_addr:IPAddress) -> EthernetPhy:
        """添加路由器的以太网物理层端口并在映射表中使其与指定IP地址对应

        Args:
            device_ip_addr (IPAddress): 指定设备的IP地址

        Returns:
            EthernetPhy: 新添加的以太网物理层模块
        """
        ethernetPhy = EthernetPhy(f"{self.name}_Eth{len(self.ethernetPhyMap.values())}")
        ethernetPhy.ofModule = self
        self.ethernetPhyMap[device_ip_addr] = ethernetPhy
        self.add_submodule(ethernetPhy)
        
        layer_module_list = [self.networkLayer, ethernetPhy]
        self.connect_layer_submodules(layer_module_list)
        
        return ethernetPhy
    
    def remove_ethernetPhy_with_eth(self, ethernetPhy:EthernetPhy):
        """删除路由器的以太网物理层映射表中的指定以太网物理层模块
            
        Args:
            ethernetPhy (EthernetPhy): 要删除的以太网物理层模块
        """
        device_ip_addr = None
        for ip_addr, phy in self.ethernetPhyMap.items():
            if phy == ethernetPhy:
                device_ip_addr = ip_addr
                break
        if device_ip_addr is not None:
            self.ethernetPhyMap.pop(device_ip_addr)
        
        self.remove_submodule(ethernetPhy)
        
    def remove_ethernetPhy_with_ip(self, device_ip_addr:IPAddress):
        """删除路由器的以太网物理层映射表中的指定IP地址对应的以太网物理层模块
            
        Args:
            device_ip_addr (IPAddress): 要删除的IP地址
        """
        ethernetPhy = self.ethernetPhyMap.pop(device_ip_addr)
        self.remove_submodule(ethernetPhy)
        
    def set_route(self, aim_ip_addr:IPAddress, ethernet_phy_name:str):
        """设置路由表
            
        Args:
            aim_ip_addr (IPAddress): 目标IP地址
            ethernet_phy (EthernetPhy): 与目标IP地址设备所连接的以太网物理层模块的名称
        """
        self.networkLayer.routing_table[aim_ip_addr] = ethernet_phy_name
    
    def delete_route(self, aim_ip_addr:IPAddress):
        """删除路由表
            
        Args:
            aim_ip_addr (IPAddress): 目标IP地址
        """
        self.networkLayer.routing_table.pop(aim_ip_addr, None)
    
    def get_route(self, aim_ip_addr:IPAddress) -> str:
        """获取路由表
            
        Args:
            aim_ip_addr (IPAddress): 目标IP地址
            
        Returns:
            str: 与目标IP地址设备所连接的以太网物理层模块的名称
        """
        ethernetPhy = self.ethernetPhyMap.get(aim_ip_addr, None)
        return ethernetPhy.name if ethernetPhy is not None else None
    
