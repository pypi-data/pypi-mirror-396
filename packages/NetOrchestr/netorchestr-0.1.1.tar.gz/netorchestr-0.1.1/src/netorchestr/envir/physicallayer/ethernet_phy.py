
from astropy import units as u
from netorchestr.envir.base import OModule, OGate, OMessage

class EthernetPhy(OModule):
    def __init__(self, name: str):
        """有线连接物理层

        Args:
            name (str): 模块名称
        """
        super().__init__(name)
        
    def recv_msg(self, msg, gate):
        if gate.name == "upperLayerIn":
            for gate in self.gates:
                if gate.name == "lowerLayerOut":
                    self.send_msg(msg, gate)
        elif gate.name == "lowerLayerIn":
            for gate in self.gates:
                if gate.name == "upperLayerOut":
                    self.send_msg(msg, gate)


