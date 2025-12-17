
from astropy import units as u
from netorchestr.envir.base import OModule, OGate, OMessage
from netorchestr.envir.mobility import MobilityBase

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from netorchestr.envir.node.satellite import SatelliteServerPlatform


class LaserPhy(OModule):
    def __init__(self, name: str):
        """激光通信物理层

        Args:
            name (str): 模块名称
        """
        super().__init__(name)
        
    def recv_msg(self, msg, gate):
        if gate.name == "upperLayerIn":
            for gate in self.gates:
                if gate.name == "lowerLayerOut":
                    node_self:"SatelliteServerPlatform" = self.find_top_module()
                    node_self_gps, catch_flag = node_self.mobiusTraj.update_current_gps(self.scheduler.now * u.ms)
                    if not catch_flag: self.logger.debug(f"{self.scheduler.now}: Module {self.name} need {node_self.name} update current gps: {node_self_gps}")
                    
                    node_aim:"SatelliteServerPlatform" = self.gates[gate][1].ofModule.find_top_module()
                    node_aim_gps, catch_flag = node_aim.mobiusTraj.update_current_gps(self.scheduler.now * u.ms)
                    if not catch_flag: self.logger.debug(f"{self.scheduler.now}: Module {self.name} need {node_aim.name} update current gps: {node_aim_gps}")
                    
                    distance = MobilityBase.calculate_distance(node_self_gps, node_aim_gps)
                    
                    light_speed = 3e8 * u.m / u.s
                    time_delay = (distance / light_speed).to(u.ms)
                    self.gates[gate][0].delay = time_delay
                    self.send_msg(msg, gate)
        elif gate.name == "lowerLayerIn":
            for gate in self.gates:
                if gate.name == "upperLayerOut":
                    self.send_msg(msg, gate)


