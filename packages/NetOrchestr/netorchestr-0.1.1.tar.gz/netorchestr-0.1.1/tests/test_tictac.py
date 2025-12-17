import pytest

from netorchestr.envir import OMessage, OLink, OGate, OModule, ONet

class Txc(OModule):
    def __init__(self, name:str):
        super().__init__(name)

    def initialize(self):
        if self.name == 'tic':
            msg = OMessage(0, 'tic', 'toc', 'tictocMsg', '0')
            self.send_msg(msg, 'out')

    def recv_msg(self, msg:OMessage, gate:OGate):
        self.send_msg(msg, 'out')

def test_tictac():
    net = ONet('Tictoc')
    tic = Txc('tic')
    toc = Txc('toc')
    
    gate_tic = OGate('out', tic)
    gate_toc = OGate('out', toc)
    
    tic.gates[gate_tic] = (OLink('tic-toc', 20.0), gate_toc)
    toc.gates[gate_toc] = (OLink('tic-toc', 100.0), gate_tic)
    
    net.add_module(tic)
    net.add_module(toc)
    
    net.run(1000)

if __name__ == '__main__':
    pytest.main()
