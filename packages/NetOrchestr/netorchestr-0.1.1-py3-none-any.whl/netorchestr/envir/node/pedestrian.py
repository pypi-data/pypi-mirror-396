
from astropy import units as u
from astropy.time import Time
from netorchestr.envir.node.base import NodeBase
from netorchestr.envir.mobility import MobilityCrowd, MobilityPedestrian
from netorchestr.envir.applications.ueapp import UeAppSfc
from netorchestr.envir.networklayer import NetworkProtocolEndIpv4
from netorchestr.envir.physicallayer import RadioPhy


class PedestrianBase(NodeBase):
    def __init__(self, name: str, mobility_ped: MobilityPedestrian):
        """初始化行人节点模型基类

        Args:
            name (str): 节点名称
            mobility_ped (MobilityPedestrian): 行人移动模型
        """
        super().__init__(name)
        
        self.mobiusTraj = mobility_ped
        self.mobiusTraj.markcolor = "yellow"

        self.appLayer = UeAppSfc(f"{self.name}_App")
        self.appLayer.ofModule = self
        self.add_submodule(self.appLayer)
        
        self.networkLayer = NetworkProtocolEndIpv4(f"{self.name}_NetLayer")
        self.networkLayer.ofModule = self
        self.add_submodule(self.networkLayer)
        
        self.radioPhy = RadioPhy(f"{self.name}_Radio", 1000*u.km)
        self.radioPhy.ofModule = self
        self.add_submodule(self.radioPhy)

        layer_module_list = [self.appLayer, self.networkLayer, self.radioPhy]
        self.connect_layer_submodules(layer_module_list)
                        

class CrowdBase():
    def __init__(self, name: str, init_time: Time, pedestrian_num: int, center_gps: list[float], radius: u.quantity):
        self.name = name
        
        self.pedestrian_num = pedestrian_num
        self.center_gps = center_gps
        self.pedestrians: dict[str, PedestrianBase] = {}
        """行人字典，键为行人名称，值为行人对象"""
        
        self.mobiusTrajGroup = MobilityCrowd(f"{self.name}_Mobility", init_time)
        
        # self.mobiusTrajGroup.generate_circular_crowd(count=pedestrian_num, 
        #                                             center=center_gps,
        #                                             radius=radius, 
        #                                             max_speed=1.5*u.m/u.s, 
        #                                             min_speed=0.5*u.m/u.s
        #                                             )
        
        self.mobiusTrajGroup.generate_rectangular_crowd(count=pedestrian_num, 
                                                        center=center_gps,
                                                        width=2*radius, 
                                                        height=2*radius, 
                                                        max_speed=1.5*u.m/u.s, 
                                                        min_speed=0.5*u.m/u.s
                                                        )
        
        for i in range(self.pedestrian_num):
            ped = PedestrianBase(f"Ped{i}", 
                                 mobility_ped=list(self.mobiusTrajGroup.mobilityPeds.values())[i])
            self.pedestrians[ped.name] = ped