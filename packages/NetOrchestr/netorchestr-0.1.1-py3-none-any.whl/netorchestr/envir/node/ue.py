
from ipaddress import IPv4Address
from astropy import units as u
from astropy.time import Time
from netorchestr.envir.node.base import NodeBase
from netorchestr.envir.mobility import MobilityTraj
from netorchestr.envir.applications.ueapp import UeAppSfc, UeAppSfcDefine
from netorchestr.envir.networklayer import NetworkProtocolEndIpv4
from netorchestr.envir.physicallayer import RadioPhy, RadioPhySimpleSDR


class UeBase(NodeBase):
    def __init__(self, name: str, init_time: Time, init_gps: list[float]):
        super().__init__(name)
        
        self.mobiusTraj = MobilityTraj(f"{self.name}_Mobility", init_time, init_gps)
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


class UeWithSfcReq(NodeBase):
    def __init__(self, name: str, init_time: Time, init_gps: list[float]):
        super().__init__(name)
        
        self.mobiusTraj = MobilityTraj(f"{self.name}_Mobility", init_time, init_gps)
        self.mobiusTraj.markcolor = "yellow"
        
        self.appLayer = UeAppSfcDefine(f"{self.name}_App")
        self.appLayer.ofModule = self
        self.add_submodule(self.appLayer)
        self.appLayer.clocktime.stop()
        
        self.networkLayer = NetworkProtocolEndIpv4(f"{self.name}_NetLayer")
        self.networkLayer.ofModule = self
        self.add_submodule(self.networkLayer)
        
        # self.radioPhy = RadioPhy(f"{self.name}_Radio", 150*u.km, [35*u.ms, 40*u.ms])
        # self.radioPhy.ofModule = self
        # self.add_submodule(self.radioPhy)
        
        self.radioPhy = RadioPhySimpleSDR(name = f"{self.name}_Radio", 
                                          mode_perf_map = {"Ue_Ground": {"range": 10*u.km, "transmission_delay_range": [5*u.ms, 10*u.ms]},
                                                           "Ue_Uav": {"range": 5*u.km, "transmission_delay_range": [20*u.ms, 30*u.ms]}, 
                                                           "Ue_Sat": {"range": 3000*u.km, "transmission_delay_range": [20*u.ms, 30*u.ms]}})
        self.radioPhy.ofModule = self
        self.add_submodule(self.radioPhy)

        layer_module_list = [self.appLayer, self.networkLayer, self.radioPhy]
        self.connect_layer_submodules(layer_module_list)

    def set_ip_address(self, ip_addr: IPv4Address):
        self.networkLayer.ip_addr = ip_addr

