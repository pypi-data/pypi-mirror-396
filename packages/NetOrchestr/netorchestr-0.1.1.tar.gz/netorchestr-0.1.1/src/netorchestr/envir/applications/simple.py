
import random
from astropy import units as u
from netorchestr.envir.base import OModule, OGate, OMessage, OLink
from netorchestr.envir.clock import ClockTime

class SimpleApp(OModule):
    def __init__(self, name: str):
        super().__init__(name)
        
        self.clocktime = ClockTime(f"{self.name}Timer")
        self.clocktime.set_tick_interval(random.randint(1, 5)*u.min)
        self.clocktime.ofModule = self
        self.add_link(OLink('clocktime', 0*u.ms), self.clocktime)
        self.add_submodule(self.clocktime)
        
        self.pkt_count = 0
        
    def recv_msg(self, msg:"OMessage", gate:"OGate"):
        if msg.sender == f"{self.name}Timer":
            for gate in self.gates:
                if gate.name == "lowerLayerOut":
                    message = OMessage(f"{self.scheduler.now}", f"{self.name}", "All", "Hello, NetOrC!", f"{self.name}{self.pkt_count}")
                    self.send_msg(message, gate)
                    self.logger.log(event="-", time=self.scheduler.now, from_node=self.name, to_node="All", pkt_type="Hello", 
                                    pkt_size=len(message), pkt_id=message.id)
                    self.pkt_count += 1
                    self.clocktime.set_tick_interval(random.randint(1, 5)*u.min)
        elif gate.name == "lowerLayerIn":
            self.logger.log(event="+", time=self.scheduler.now, from_node=msg.sender, to_node=self.name, pkt_type="Hello", 
                            pkt_size=len(msg), pkt_id=msg.id, pkt_delay=self.scheduler.now - float(msg.timestamp))


