#Anaconda/envs/minisfc python
# -*- coding: utf-8 -*-
'''
uem.py
======

.. module:: uem
  :platform: Linux
  :synopsis: Module for ue management functionality.

.. moduleauthor:: WangXi

Introduction
------------

This module implements ue management functionality, primarily used in SFC applications. It provides the following features:

- Supports UE management operations (e.g., registration, deregistration, etc.).

Version
-------

- Version 1.0 (2025/03/13): Initial version

'''

import numpy as np
from ipaddress import IPv4Address

from netorchestr.envir.base import OModule
from netorchestr.envir.node.ue import UeWithSfcReq
from netorchestr.envir.applications.ueapp import SfcReq

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from netorchestr.envir.base import ONet

class UeManager(OModule):
    def __init__(self, name:str, net:"ONet"):
        super().__init__(name)
        
        self.net = net
        
        self.ue_group:dict[int,Ue] = {}
        
        self.get_all_ue_node_info()
        
    def get_all_ue_node_info(self):
        for ue_node in self.net.find_modules_with_class(UeWithSfcReq):
            ue = Ue(name = ue_node.name, 
                    id = len(self.ue_group), 
                    node_handle = ue_node)
            self.ue_group[ue.id] = ue
        return self.ue_group
        
        
    def add_ue_into_group(self):
        pass
    
    
    def get_ue_from_group(self, ue_node_handle: UeWithSfcReq):
        for ue in self.ue_group.values():
            if ue.node_handle == ue_node_handle:
                return ue
        return None


class Ue:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)
        self.id = kwargs.get('id', None)
        self.ip = kwargs.get('ip', None)

        self.node_handle: UeWithSfcReq = kwargs.get('node_handle', None)

        for key,value in kwargs.items():
            setattr(self,key,value)        
    
    def update_ue_info(self, **kwargs):
        for key,value in kwargs.items():
            setattr(self,key,value)        
            
    def set_ip(self, ip: IPv4Address):
        self.ip = ip
        self.node_handle.set_ip_address(ip)

    def reset_ip(self):
        self.ip = None
        self.node_handle.set_ip_address(None)

    def start_transport(self, sfc_req: SfcReq, segment_list:list[IPv4Address], receiver:str):
        self.node_handle.appLayer.set_sfc_trans_task(sfc_req, segment_list, receiver)
        self.node_handle.appLayer.clocktime.start()

    def stop_transport(self):
        self.node_handle.appLayer.clocktime.stop()
        self.node_handle.appLayer.del_sfc_trans_task()
        
    def get_location(self):
        return self.node_handle.mobiusTraj.current_gps
        

        
