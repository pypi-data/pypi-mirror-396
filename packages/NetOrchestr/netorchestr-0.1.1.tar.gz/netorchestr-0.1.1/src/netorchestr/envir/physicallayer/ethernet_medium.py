
from astropy import units as u
from collections import defaultdict
from netorchestr.envir.base import OModule, OGate
from netorchestr.envir.mobility.base import MobilityBase, MobilityStatic, MobilityDynamic
from netorchestr.envir.physicallayer import EthernetPhy

class EthernetMedium(OModule):
    def __init__(self, name:str):
        """有线连接传输介质层"""
        super().__init__(name)
        
        self.interface_ethernet:dict[EthernetPhy, dict[EthernetPhy,float]] = defaultdict(lambda: defaultdict(dict))
        """转发接口表 [EthernetPhy->[EthernetPhy:distance]] """

    def recv_msg(self, msg, gate:"OGate"):
        from_module_ethphy = self.gates[gate][1].ofModule
        to_module_ethphy_list = list(self.interface_ethernet[from_module_ethphy].keys())
        for to_gate in [temp_gate for temp_gate in self.gates if temp_gate.name == "upperLayerOut"]:
            if self.gates[to_gate][1].ofModule in to_module_ethphy_list:
                to_module_ethphy = self.gates[to_gate][1].ofModule
                distance = self.update_distance(from_module_ethphy, to_module_ethphy) * u.km
                c = 299792458 * u.m / u.s
                self.gates[to_gate][0].delay = (distance / c).to(u.ms)
                self.send_msg(msg, to_gate)
                
    def update_distance(self, from_module:"EthernetPhy", to_module:"EthernetPhy") -> float:
        """计算接口两端设备之间的距离

        Args:
            from_module (EthernetPhy): 端口1的设备
            to_module (EthernetPhy): 端口2的设备

        Returns:
            float: 距离(单位: km)
        """
        
        from_node = from_module.ofModule
        to_node = to_module.ofModule
        # 筛选运动模型
        from_node_mobilily = [m for m in from_node.oSubModules if isinstance(m, MobilityBase)]
        from_node_mobilily = from_node_mobilily[0]
        to_node_mobilily = [m for m in to_node.oSubModules if isinstance(m, MobilityBase)]
        to_node_mobilily = to_node_mobilily[0]
        if isinstance(from_node_mobilily, MobilityStatic) and isinstance(to_node_mobilily, MobilityStatic):
            # 静态运动模型
            if self.interface_ethernet[from_module][to_module] == None:
                from_node_gps,catch_flag = from_node_mobilily.update_current_gps(self.scheduler.now * u.ms)
                if not catch_flag: self.logger.debug(f"{self.scheduler.now}: Module {self.name} need {from_node_mobilily.name} update current gps: {from_node_gps}")
                
                to_node_gps,catch_flag = to_node_mobilily.update_current_gps(self.scheduler.now * u.ms)
                if not catch_flag: self.logger.debug(f"{self.scheduler.now}: Module {self.name} need {to_node_mobilily.name} update current gps: {to_node_gps}")
                
                distance = from_node_mobilily.calculate_distance(from_node_gps, to_node_gps).to(u.km).value
                self.interface_ethernet[from_module][to_module] = distance
                return distance
            else:
                return self.interface_ethernet[from_module][to_module]
        else:
            # 动态运动模型
            from_node_gps,catch_flag = from_node_mobilily.update_current_gps(self.scheduler.now * u.ms)
            if not catch_flag: self.logger.debug(f"{self.scheduler.now}: Module {self.name} need {from_node_mobilily.name} update current gps: {from_node_gps}")
            
            to_node_gps,catch_flag = to_node_mobilily.update_current_gps(self.scheduler.now * u.ms)
            if not catch_flag: self.logger.debug(f"{self.scheduler.now}: Module {self.name} need {to_node_mobilily.name} update current gps: {to_node_gps}")
            
            distance = from_node_mobilily.calculate_distance(from_node_gps, to_node_gps).to(u.km).value
            return distance
        

