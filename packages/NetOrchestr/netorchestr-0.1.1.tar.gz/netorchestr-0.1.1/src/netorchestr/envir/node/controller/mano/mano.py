#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   nfv_mano.py
@Time    :   2024/06/18 17:51:03
@Author  :   Wang Xi
@Version :   0.0
@Contact :   wangxi_chn@foxmail.com
@License :   (C)Copyright 2023-2024, Wang Xi
@Desc    :   None
'''


from astropy import units as u
from netorchestr.envir.applications.ueapp import SfcReq
from netorchestr.envir.node.base import NodeBase
from netorchestr.envir.node.controller.mano.vnfm import VnfManager
from netorchestr.envir.node.controller.mano.uem import UeManager
from netorchestr.envir.node.controller.mano.vim import VnfVim
from netorchestr.envir.node.controller.mano.nfvo import NfvOrchestrator

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from netorchestr.envir.base import ONet

class SfcReqEvent:
    def __init__(self, sfcReq:SfcReq, req_type:str, req_time:u.Quantity):
        self.sfcReq = sfcReq
        self.req_type = req_type
        self.req_time = req_time

class ControllerMano(NodeBase):
    def __init__(self, name:str, net:"ONet", vnfManager:VnfManager, sfcReqlist:list[SfcReq]):
        super().__init__(name)
        
        self.net = net
        self.logger = net.logger
        self.scheduler = net.scheduler
        
        self.sfcReqlist = sfcReqlist
        self.vnfManager = vnfManager
        
        self.ueManager = UeManager("UEM",net)
        self.ueManager.ofModule = self
        self.add_submodule(self.ueManager)
        
        self.vnfVim = VnfVim("VIM",net)
        self.vnfVim.ofModule = self
        self.add_submodule(self.vnfVim)
        
        self.nfvOrchestrator = NfvOrchestrator("NFVO",
                                               self.vnfManager,
                                               self.ueManager,
                                               self.vnfVim)
        self.nfvOrchestrator.ofModule = self
        self.add_submodule(self.nfvOrchestrator)
        
        self.sfcReqEventList = self.__generate_sfc_req_event_list()
        
        self.scheduler.process(self.__process_sfc_req_event())

    def set_solver_deploy(self, solver_deploy):
        self.nfvOrchestrator.set_solver_deploy(solver_deploy)

    def __generate_sfc_req_event_list(self):
        arrive_sfc_req_event_list = [SfcReqEvent(sfcReq = sfcReq, 
                                                 req_type = "arrive", 
                                                 req_time = sfcReq.start_time) 
                                     for sfcReq in self.sfcReqlist]
        
        leave_sfc_req_event_list = [SfcReqEvent(sfcReq = sfcReq, 
                                                req_type = "leave", 
                                                req_time = sfcReq.end_time) 
                                   for sfcReq in self.sfcReqlist]

        sfc_req_event_list = arrive_sfc_req_event_list + leave_sfc_req_event_list
        sfc_req_event_list.sort(key=lambda x:x.req_time)
        
        return sfc_req_event_list


    def __process_sfc_req_event(self):
        if len(self.sfcReqEventList) == 0:
            return
        
        while len(self.sfcReqEventList) > 0:
            current_time = self.scheduler.now
            event_time = self.sfcReqEventList[0].req_time.to(u.ms).value
            timeout = max(0, event_time - current_time)
            
            yield self.scheduler.timeout(timeout)
            
            sfc_req_event = self.sfcReqEventList.pop(0)
            self.logger.info(f"{self.scheduler.now}: nfvOrchestrator receives sfcReq {sfc_req_event.sfcReq.id} {sfc_req_event.req_type}")
            self.nfvOrchestrator.receive_sfc_req(sfc_req_event.sfcReq, sfc_req_event.req_type)
            
    
    
    



