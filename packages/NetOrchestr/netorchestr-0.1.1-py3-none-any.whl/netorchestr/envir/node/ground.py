
import copy
from astropy import units as u
from astropy.time import Time
from netorchestr.envir.node.base import NodeBase
from netorchestr.envir.node.switch import SwitchBase, SwitchRouter
from netorchestr.envir.node.oran import DuAAuBase, DuAAuSimpleSDR
from netorchestr.envir.node.container import VnfBase, VnfContainer
from netorchestr.envir.networklayer import IpManager
from netorchestr.envir.mobility import MobilityStatic
from netorchestr.envir.applications.simple import SimpleApp
from netorchestr.envir.physicallayer import RadioPhy

class GroundBase(NodeBase):
    def __init__(self, name: str, init_time: Time, init_gps: list[float]):
        super().__init__(name)
        
        self.mobiusTraj = MobilityStatic(f"{self.name}_Mobility", init_time, init_gps)
        self.mobiusTraj.markcolor = "blue"

        self.appLayer = SimpleApp(f"{self.name}_App")
        self.appLayer.ofModule = self
        self.add_submodule(self.appLayer)
        
        # # 停止应用层业务发送的时钟
        # self.appLayer.clocktime.stop()
        
        self.radioPhy = RadioPhy(f"{self.name}_Radio", 1000*u.km)
        self.radioPhy.ofModule = self
        self.add_submodule(self.radioPhy)
        
        layer_module_list = [self.appLayer, self.radioPhy]
        self.connect_layer_submodules(layer_module_list)
        
        
class GroundServerBase(NodeBase):
    def __init__(self, name: str, init_time: Time, init_gps: list[float]):
        super().__init__(name)
        
        self.mobiusTraj = MobilityStatic(f"{self.name}_Mobility", init_time, init_gps)
        self.mobiusTraj.markcolor = "purple"
        
        self.switch = SwitchBase(f"{self.name}_Switch")
        self.switch.ofModule = self
        self.add_submodule(self.switch)
        
        self.duAau = DuAAuBase(f"{self.name}_DuAau")
        self.duAau.ofModule = self
        self.add_submodule(self.duAau)
        
        self.vnfList:list[VnfBase] = []
        
        vnf = VnfBase(f"{self.name}_Vnf1")
        vnf.ofModule = self
        self.add_submodule(vnf)
        self.vnfList.append(vnf)
        
        self.link_internal_modules()
        
    
    def link_internal_modules(self):
        """连接 VIM 集合体内部的模块"""
        self.switch.add_ethernetPhy()
        NodeBase.connect_peer_submodules([self.switch.ethernetPhyList[-1], self.duAau.ethernetPhy])
        
        self.switch.add_ethernetPhy()
        NodeBase.connect_peer_submodules([self.switch.ethernetPhyList[-1], self.vnfList[0].ethernetPhy])


class GroundServerPlatform(NodeBase):
    def __init__(self, name: str, init_time: Time, init_gps: list[float], ip_pool_str: str,
                 node_resource_dict: dict[str, int], link_resource_dict: dict[str, int]):
        """地面设施的服务器平台

        Args:
            name (str): 地面设施名称
            init_time (Time): 初始化时间
            init_gps (list[float]): 初始化 GPS 坐标, [纬度, 经度, 高度km]
            ip_pool_str (str): IP 地址池, 格式参考 "192.168.0.0/24"
        """
        
        super().__init__(name)
        
        self.mobiusTraj = MobilityStatic(f"{self.name}_Mobility", init_time, init_gps)
        self.mobiusTraj.markcolor = "purple"
        
        self.ip_manager = IpManager(ip_pool_str)
        
        self.switch = SwitchRouter(f"{self.name}_Switch")
        self.switch.ofModule = self
        self.switch.networkLayer.ip_addr = self.ip_manager.get_next_available_ip()
        self.add_submodule(self.switch)
        
        # self.duAau = DuAAuBase(f"{self.name}_DuAau")
        # self.duAau.ofModule = self
        # self.duAau.networkLayer.ip_addr = self.ip_manager.get_next_available_ip()
        # self.add_submodule(self.duAau)
        
        self.duAau = DuAAuSimpleSDR(name = f"{self.name}_DuAau", 
                                    mode_perf_map = {"Ground_Ue": {"range": 10*u.km, "transmission_delay_range": [5*u.ms, 10*u.ms]}, 
                                                     "Ground_Uav": {"range": 5*u.km, "transmission_delay_range": [5*u.ms, 10*u.ms]}, 
                                                     "Ground_Sat": {"range": 3000*u.km, "transmission_delay_range": [20*u.ms, 30*u.ms]}})
        self.duAau.ofModule = self
        self.duAau.networkLayer.ip_addr = self.ip_manager.get_next_available_ip()
        self.add_submodule(self.duAau)
        # 连接 duAau 与 switch 的物理层线缆
        switch_eth_to_duAau = self.switch.add_ethernetPhy(self.duAau.networkLayer.ip_addr)
        NodeBase.connect_peer_submodules([switch_eth_to_duAau, self.duAau.ethernetPhy])

        # 初始化资源限制
        self.container_resource_max = copy.deepcopy(node_resource_dict)
        self.container_resource_remain = copy.deepcopy(node_resource_dict)
        self.container_deployed:list[VnfContainer] = []
        
        self.duAau.radioPhy.bandwidth_max = link_resource_dict["band"]
        
    def deploy_vnf(self, vnf: VnfContainer) -> VnfContainer:
        """地面设施的服务器平台上部署 VNF

        Args:
            vnf (VnfContainer): 要部署的 VNF (未被激活)
            
        Returns:
            VnfContainer: 部署成功的 VNF, 可用于获取已部署的 VNF 被分配到的 IP 地址等相关信息
        """
        
        # 检查资源是否足够
        for res_name, res_limit in vnf.resouce_limit.items():
            if res_name not in self.container_resource_max:
                self.logger.error(f"{self.scheduler.now}: 服务器 {self.name} 中不存在 vnf 请求的资源类型 {res_name}")
            if res_limit > self.container_resource_remain[res_name]:
                self.logger.warning(f"{self.scheduler.now}: 服务器 {self.name} 中剩余资源不足, 理论上无法部署 vnf {vnf.name}")
            
        # 部署 VNF
        vnf.ofModule = self
        vnf.networkLayer.ip_addr = self.ip_manager.get_next_available_ip()
        self.add_submodule(vnf)
        self.container_deployed.append(vnf)
        for res_name, res_limit in vnf.resouce_limit.items():
            self.container_resource_remain[res_name] -= res_limit
        switch_eth_to_vnf = self.switch.add_ethernetPhy(vnf.networkLayer.ip_addr)
        NodeBase.connect_peer_submodules([switch_eth_to_vnf, vnf.ethernetPhy])
        
        # 激活 VNF 和与其相连的路由器的端口模块, 使其与 Simpy 环境绑定
        self.switch.networkLayer.activate_gate(list(self.switch.networkLayer.gates.keys())[-2])
        self.switch.networkLayer.activate_gate(list(self.switch.networkLayer.gates.keys())[-1])
        switch_eth_to_vnf._activate(self.scheduler, self.logger)
        vnf._activate(self.scheduler, self.logger)
        
        return vnf
    
    def update_remain_resource(self):
        """更新 VNF 资源占用信息 (仅用于更新剩余资源信息)"""
        container_resource_occupied = {}
        for vnf_deployed in self.container_deployed:
            for res_name, res_limit in vnf_deployed.resouce_limit.items():
                if res_name not in container_resource_occupied:
                    container_resource_occupied[res_name] = 0
                container_resource_occupied[res_name] += res_limit
        for res_name, res_val in self.container_resource_max.items():
            self.container_resource_remain[res_name] = res_val - container_resource_occupied.get(res_name, 0)
        return self.container_resource_remain
    
    def remove_vnf(self, vnf: VnfContainer):
        """地面设施的服务器平台上移除 VNF

        Args:
            vnf (VnfBase): 要移除的 VNF
        """
        
        # 移除 VNF
        self.remove_submodule(vnf)
        self.container_deployed.remove(vnf)
        for res_name, res_limit in vnf.resouce_limit.items():
            self.container_resource_remain[res_name] += res_limit
        self.switch.remove_ethernetPhy_with_ip(vnf.networkLayer.ip_addr)
        self.ip_manager.release_ip(vnf.networkLayer.ip_addr)
        
    def get_remaining_resource(self) -> dict[str, int]:
        """获取地面设施的服务器平台剩余资源

        Returns:
        
            dict (str, int): 剩余资源字典, 键为资源名称, 值为资源数量
        """
        return self.container_resource_remain
    
    def get_max_resource(self) -> dict[str, int]:
        """获取地面设施的服务器平台最大资源限制

        Returns:
        
            dict (str, int): 最大资源限制字典, 键为资源名称, 值为资源数量
        """
        return self.container_resource_max
    
    def get_remaining_bandwidth(self) -> u.Quantity:
        """获取地面设施的服务器平台剩余带宽

        Returns:
        
            u.Quantity: 剩余带宽, 单位为 u.Quantity(kbit/s)
        """
        return self.duAau.radioPhy.get_remain_bandwidth().to(u.kbit/u.s)
    
    def get_max_bandwidth(self) -> u.Quantity:
        """获取地面设施的服务器平台最大带宽限制

        Returns:
        
            u.Quantity: 最大带宽限制, 单位为 u.Quantity(kbit/s)
        """
        return self.duAau.radioPhy.bandwidth_max.to(u.kbit/u.s)
    
    