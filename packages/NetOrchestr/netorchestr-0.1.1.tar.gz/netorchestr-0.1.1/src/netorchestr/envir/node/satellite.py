
import copy
from astropy import units as u
from astropy.time import Time
from netorchestr.envir.node.base import NodeBase
from netorchestr.envir.node.switch import SwitchRouter
from netorchestr.envir.node.oran import DuAAuBase, DuAAuSimpleSDR
from netorchestr.envir.node.laser import LaserBase
from netorchestr.envir.node.container import VnfContainer
from netorchestr.envir.mobility import MobilitySat, MobilityConstellation
from netorchestr.envir.networklayer import IpManager

class SatelliteServerPlatform(NodeBase):
    def __init__(self, name: str, mobility_sat: MobilitySat, ip_pool_str: str,
                 node_resource_dict: dict[str, int], link_resource_dict: dict[str, int]):
        """卫星设施的服务器平台

        Args:
            name (str): 卫星设施名称
            mobility_sat (MobilitySat): 卫星运动模型
            ip_pool_str (str): IP 地址池, 格式参考 "192.168.0.0/24"
            node_resource_dict (dict[str, int]): 服务器平台节点资源字典
            link_resource_dict (dict[str, int]): 服务器平台链路资源字典
        """
        super().__init__(name)

        self.mobiusTraj = mobility_sat
        self.mobiusTraj.markcolor = "green"

        self.ip_manager = IpManager(ip_pool_str)
        
        self.switch = SwitchRouter(f"{self.name}_Switch")
        self.switch.ofModule = self
        self.switch.networkLayer.ip_addr = self.ip_manager.get_next_available_ip()
        self.add_submodule(self.switch)
        
        # self.duAau = DuAAuBase(f"{self.name}_DuAau", [20*u.ms, 30*u.ms])
        # self.duAau.ofModule = self
        # self.duAau.networkLayer.ip_addr = self.ip_manager.get_next_available_ip()
        # self.add_submodule(self.duAau)
        
        self.duAau = DuAAuSimpleSDR(name = f"{self.name}_DuAau", 
                                    mode_perf_map = {"Sat_Ue": {"range": 3000*u.km, "transmission_delay_range": [20*u.ms, 30*u.ms]}, 
                                                     "Sat_Ground": {"range": 3000*u.km, "transmission_delay_range": [20*u.ms, 30*u.ms]},
                                                     "Sat_Uav": {"range": 3000*u.km, "transmission_delay_range": [20*u.ms, 30*u.ms]}})
        self.duAau.ofModule = self
        self.duAau.networkLayer.ip_addr = self.ip_manager.get_next_available_ip()
        self.add_submodule(self.duAau)
        # 连接 duAau 与 switch 的物理层线缆
        switch_eth_to_duAau = self.switch.add_ethernetPhy(self.duAau.networkLayer.ip_addr)
        NodeBase.connect_peer_submodules([switch_eth_to_duAau, self.duAau.ethernetPhy])
        
        self.laser_up = LaserBase(f"{self.name}_LaserUp")
        self.laser_up.ofModule = self
        self.laser_up.networkLayer.ip_addr = self.ip_manager.get_next_available_ip()
        self.add_submodule(self.laser_up)
        switch_eth_to_laser_up = self.switch.add_ethernetPhy(self.laser_up.networkLayer.ip_addr)
        NodeBase.connect_peer_submodules([switch_eth_to_laser_up, self.laser_up.ethernetPhy])
        
        self.laser_down = LaserBase(f"{self.name}_LaserDown")
        self.laser_down.ofModule = self
        self.laser_down.networkLayer.ip_addr = self.ip_manager.get_next_available_ip()
        self.add_submodule(self.laser_down)
        switch_eth_to_laser_down = self.switch.add_ethernetPhy(self.laser_down.networkLayer.ip_addr)
        NodeBase.connect_peer_submodules([switch_eth_to_laser_down, self.laser_down.ethernetPhy])
        
        self.laser_left = LaserBase(f"{self.name}_LaserLeft")
        self.laser_left.ofModule = self
        self.laser_left.networkLayer.ip_addr = self.ip_manager.get_next_available_ip()
        self.add_submodule(self.laser_left)
        switch_eth_to_lase_left = self.switch.add_ethernetPhy(self.laser_left.networkLayer.ip_addr)
        NodeBase.connect_peer_submodules([switch_eth_to_lase_left, self.laser_left.ethernetPhy])
        
        self.laser_right = LaserBase(f"{self.name}_LaserRight")
        self.laser_right.ofModule = self
        self.laser_right.networkLayer.ip_addr = self.ip_manager.get_next_available_ip()
        self.add_submodule(self.laser_right)
        switch_eth_to_lase_right = self.switch.add_ethernetPhy(self.laser_right.networkLayer.ip_addr)
        NodeBase.connect_peer_submodules([switch_eth_to_lase_right, self.laser_right.ethernetPhy])
        
        self.laser_group = [self.laser_up, self.laser_down, self.laser_left, self.laser_right]
        
        # 初始化资源限制
        self.container_resource_max = copy.deepcopy(node_resource_dict)
        self.container_resource_remain = copy.deepcopy(node_resource_dict)
        self.container_deployed:list[VnfContainer] = []
        
        self.duAau.radioPhy.bandwidth_max = link_resource_dict["band"]
    
    def deploy_vnf(self, vnf: VnfContainer) -> VnfContainer:
        """卫星设施的服务器平台上部署 VNF

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
        """卫星设施的服务器平台上移除 VNF

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
        """获取卫星设施的服务器平台剩余资源

        Returns:
        
            dict (str, int): 剩余资源字典, 键为资源名称, 值为资源数量
        """
        return self.container_resource_remain
    
    def get_max_resource(self) -> dict[str, int]:
        """获取卫星设施的服务器平台最大资源限制

        Returns:
        
            dict (str, int): 最大资源限制字典, 键为资源名称, 值为资源数量
        """
        return self.container_resource_max
    
    def get_remaining_bandwidth(self) -> u.Quantity:
        """获取卫星设施的服务器平台剩余带宽

        Returns:
        
            u.Quantity: 剩余带宽, 单位为 u.Quantity(kbit/s)
        """
        return self.duAau.radioPhy.get_remain_bandwidth().to(u.kbit/u.s)
    
    def get_max_bandwidth(self) -> u.Quantity:
        """获取卫星设施的服务器平台最大带宽限制

        Returns:
        
            u.Quantity: 最大带宽限制, 单位为 u.Quantity(kbit/s)
        """
        return self.duAau.radioPhy.bandwidth_max.to(u.kbit/u.s)
    

class ConstellationServerPlatform():
    def __init__(self, name: str, init_time: Time, sat_num: int, plane_num:int, 
                 ip_pool_str_list: list[str], node_resource_dict: dict[str, int], link_resource_dict: dict[str, int]):
        """星座设施的服务器平台集合
        
        
        Args:
            name (str): 星座设施名称
            init_time (Time): 初始时间
            sat_num (int): 卫星数量
            plane_num (int): 轨道面数量
            ip_pool_str_list (list[str]): IP 地址池列表, 格式参考 "[192.168.0.0/24, 192.168.1.0/24, ...]",
                                                列表长度应等于 sat_num
            node_resource_dict (dict[str, int]): 各个卫星上服务器平台节点资源字典
            link_resource_dict (dict[str, int]): 各个卫星上服务器平台链路资源字典
        """
        self.name = name
        
        self.sat_num = sat_num
        self.plane_num = plane_num
        self.satellites: dict[str, SatelliteServerPlatform] = {}  
        """卫星字典，键为卫星名称，值为卫星对象"""
        
        self.mobiusTrajGroup = MobilityConstellation(f"{self.name}_Mobility", init_time)
        self.mobiusTrajGroup.generate_walker_formation(init_time=init_time,
                                                    T=self.sat_num,  # 总卫星数量
                                                    P=self.plane_num,# 轨道面数量
                                                    F=0.5, # 相位因子
                                                    a=6371+590,  # 半长轴（单位：km）
                                                    e=0,  # 偏心率
                                                    inc=53,  # 倾角（单位：度）
                                                    )
        
        for i in range(self.sat_num):
            sat = SatelliteServerPlatform(name=list(self.mobiusTrajGroup.mobilitySats.keys())[i].split("_")[0], 
                                          mobility_sat=list(self.mobiusTrajGroup.mobilitySats.values())[i],
                                          ip_pool_str=ip_pool_str_list[i],
                                          node_resource_dict=copy.deepcopy(node_resource_dict),
                                          link_resource_dict=copy.deepcopy(link_resource_dict))
            self.satellites[sat.name] = sat
        
        self.create_inter_satellite_links()

    def create_inter_satellite_links(self):
        """创建卫星间的链路, 即将各个卫星上的激光模块完成连接"""
        T = self.sat_num
        P = self.plane_num
        S = T // P
        
        # 将卫星按轨道面和相对位置组织成二维数组
        satellites_grid = [[None for _ in range(S)] for _ in range(P)]
        for sat in list(self.satellites.values()):
            orbit_plane_num = int(sat.mobiusTraj.raan * P / 360)  # 根据 RAAN 确定轨道面编号
            sat_num = int(sat.mobiusTraj.init_nu * S / 360)  # 根据真近点角确定卫星编号
            satellites_grid[orbit_plane_num][sat_num] = sat

        # 遍历每个轨道面和每颗卫星，创建星间链路
        for orbit_plane_num in range(P):
            for sat_num in range(S):
                current_sat:SatelliteServerPlatform = satellites_grid[orbit_plane_num][sat_num]

                # 上邻居（同一轨道面上的前一颗卫星）
                upper_neighbor:SatelliteServerPlatform = satellites_grid[orbit_plane_num][(sat_num - 1) % S]
                connect_module =[current_sat.laser_up.laserPhy, upper_neighbor.laser_down.laserPhy]
                NodeBase.connect_peer_submodules(connect_module)
                current_sat.laser_up.aim_laser_ip = upper_neighbor.laser_down.networkLayer.ip_addr
                upper_neighbor.laser_down.aim_laser_ip = current_sat.laser_up.networkLayer.ip_addr

                # 下邻居（同一轨道面上的后一颗卫星）已被循环处理
                # lower_neighbor:SatelliteServerPlatform = satellites_grid[orbit_plane_num][(sat_num + 1) % S]
                # connect_module =[current_sat.laser_down.laserPhy, lower_neighbor.laser_up.laserPhy]
                # NodeBase.connect_peer_submodules(connect_module)

                # 左邻居（相邻轨道面上相同相对位置的卫星）已被循环处理
                left_orbit_plane = (orbit_plane_num - 1) % P
                left_neighbor:SatelliteServerPlatform = satellites_grid[left_orbit_plane][sat_num]
                connect_module =[current_sat.laser_left.laserPhy, left_neighbor.laser_right.laserPhy]
                NodeBase.connect_peer_submodules(connect_module)
                current_sat.laser_left.aim_laser_ip = left_neighbor.laser_right.networkLayer.ip_addr
                left_neighbor.laser_right.aim_laser_ip = current_sat.laser_left.networkLayer.ip_addr

                # 右邻居（相邻轨道面上相同相对位置的卫星）
                # right_orbit_plane = (orbit_plane_num + 1) % P
                # right_neighbor:SatelliteServerPlatform = satellites_grid[right_orbit_plane][sat_num]
                # connect_module =[current_sat.laser_right.laserPhy, right_neighbor.laser_left.laserPhy]
                # NodeBase.connect_peer_submodules(connect_module)
        

