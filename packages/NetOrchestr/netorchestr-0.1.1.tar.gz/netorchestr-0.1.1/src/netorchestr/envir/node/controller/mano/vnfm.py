#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   nfv_manager.py
@Time    :   2024/06/18 15:15:00
@Author  :   Wang Xi
@Version :   0.0
@Contact :   wangxi_chn@foxmail.com
@License :   (C)Copyright 2023-2024, Wang Xi
@Desc    :   None
'''

import copy
from netaddr import IPAddress
from netorchestr.envir.node.container import VnfContainer

class VnfManager:
    def __init__(self):
        """
        VNF Manager
        """
        self.vnfTemplates:dict[str,VnfEm] = {}
        
        self.vnf_group:dict[int,VnfEm] = {}
        self.vnf_group_id_max:int = 0


    def add_vnf_into_templates(self,vnfEm_template:'VnfEm'):
        if vnfEm_template.type in self.vnfTemplates:
            raise ValueError(f'VNF type {vnfEm_template.type} already exists in VNF templates')
        else:
            self.vnfTemplates[vnfEm_template.type] = vnfEm_template
    

    def get_vnf_from_templates(self,vnfEm_template_type:str) -> 'VnfEm':
        if vnfEm_template_type not in self.vnfTemplates:
            raise ValueError(f'VNF type {vnfEm_template_type} does not exist in VNF templates')
        vnfEm = copy.deepcopy(self.vnfTemplates[vnfEm_template_type])
        return vnfEm
    
    
    def add_vnf_into_group(self,vnfEm:'VnfEm'):
        """将VNF添加到VNF组, 并分配ID

        Args:
            vnfEm (VnfEm): vnf element management

        Raises:
            ValueError: VNF should be bound to a node before adding it to VNF group
        """
        if vnfEm.node_handler is None:
            raise ValueError(f'VNF {vnfEm.name} should be bound to a node before adding it to VNF group')
        vnfEm.id = self.vnf_group_id_max
        self.vnf_group_id_max += 1
        self.vnf_group[vnfEm.id] = vnfEm
    
    
    def get_vnf_from_group(self,vnfEm_id:int) -> 'VnfEm':
        if vnfEm_id not in self.vnf_group:
            raise ValueError(f'VNF ID {vnfEm_id} does not exist in VNF group')
        vnfEm = self.vnf_group[vnfEm_id]
        return vnfEm
    
    
    def remove_vnf_from_group(self,vnfEm_id:int):
        if vnfEm_id not in self.vnf_group:
            raise ValueError(f'VNF ID {vnfEm_id} does not exist in VNF group')
        del self.vnf_group[vnfEm_id]
           
        
class VnfEm:
    def __init__(self,**kwargs):
        """VNF Element Management

        Args:
            
        """
        self.name:str = kwargs.get('vnf_name',f'SFC*VNF*')
        self.type:str = kwargs.get('vnf_type',None)
        self.id:int = kwargs.get('vnf_id',None)
        """VNF ID, 由VNF管理器分配"""
        
        self.ip:IPAddress = kwargs.get('vnf_ip',None)
        """VNF IP, 由所部署的 NFVI 绑定的节点分配"""
        
        self.rate_per_core:float = kwargs.get('rate_per_core',10.0)
        """服务速率(pkt/ms)与CPU核数的比值, 默认为10.0, 即0.1个CPU核可以以1 pkt/ms的服务速率处理"""

        self.resource_limit:dict[str, float] = kwargs.get('resource_limit',None)
        """VNF 资源限制, 包括CPU,内存,存储等, 表示不限制资源"""
        
        self.cost_with_loc:dict[str,float] = kwargs.get('cost_with_loc',None)
        """VNF 不同部署位置下的费用, 位置包括 Ground, Sat, Uav"""
        
        self.node_handler:VnfContainer = kwargs.get('node_handler',None)
        """VNF 节点模型, 由 VNFFG 与 pysim 驱动的实体模型进行绑定"""

        self.uesd_shared:bool = kwargs.get('use_shared',False)
        """是否支持被共享使用, 默认为False"""
        self.used_sfc_id:list[int] = []
        self.used_sfc_resource:dict[int,dict[str,float]] = {}

        for key,value in kwargs.items():
            setattr(self,key,value)

    def update_resource_limit(self):
        """将VNF的资源限制更新到VNF节点模型中"""
        temp_resource_limit = {}
        for res_name in self.resource_limit.keys():
            temp_resource_limit[res_name] = 0.0
            for uesd_sfc_id,uesd_sfc_res in self.used_sfc_resource.items():
                temp_resource_limit[res_name] += uesd_sfc_res.get(res_name,0.0)
        
        self.resource_limit = copy.deepcopy(temp_resource_limit)
                
        if self.node_handler is None:
            raise ValueError(f'VNF {self.name} should be bound to a node before updating its resource limit')
        
        self.node_handler.update_resource_limit(self.resource_limit)
        self.node_handler.appLayer.process_rate = self.rate_per_core * self.resource_limit.get('cpu',None)

    def update_vnf_param(self,**kwargs):
        for key,value in kwargs.items():
            setattr(self,key,value)
            
