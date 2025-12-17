#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   nfv_orchestrator.py
@Time    :   2024/06/18 19:57:29
@Author  :   Wang Xi
@Version :   0.0
@Contact :   wangxi_chn@foxmail.com
@License :   (C)Copyright 2023-2024, Wang Xi
@Desc    :   None
'''

import os
import copy
from astropy import units as u
from astropy.time import Time
from netorchestr.envir.base import OModule
from netorchestr.envir.applications.ueapp import SfcReq
from netorchestr.envir.node.container import VnfContainer
from netorchestr.envir.node.controller.mano.vnfm import VnfManager, VnfEm
from netorchestr.envir.node.controller.mano.uem import UeManager
from netorchestr.envir.node.controller.mano.vim import VnfVim
from netorchestr.envir.node.controller.mano.trace import TRACE_RESULT, TRACE_NFVI
from netorchestr.envir.node.controller.mano.solver_deploy import SolverDeployBase, SolutionDeploy
from netorchestr.envir.node.controller.mano.solver_e2e import SolverE2EBase, SolutionE2E

class NfvOrchestrator(OModule):
    def __init__(self,name:str, vnfManager:VnfManager, ueManager:UeManager, vnfVim:VnfVim):
        super().__init__(name)
        
        self.vnfManager = vnfManager
        self.ueManager = ueManager
        self.vnfVim = vnfVim
        
        self.vnffg_group:list[VnffgManager] = []
        self.vnffg_group_history:list[VnffgManager] = []
        
        self.system_total_cost = 0.0
        self.system_total_rev = 0.0
        

    def set_solver_deploy(self, solver_deploy:SolverDeployBase):
        
        TraceResultFile = os.path.join(self.vnfVim.net.logger.log_dir, f'nfvo_deploy_{solver_deploy.__class__.__name__}.csv')
        TRACE_RESULT.set(TraceResultFile)
        TraceNfviFile = os.path.join(self.vnfVim.net.logger.log_dir, f'nfvo_resource_{solver_deploy.__class__.__name__}.csv')
        TRACE_NFVI.set(TraceNfviFile)
        
        TRACE_RESULT.ready(['Event', 'Time', 'SfcId', 'Result', 'Shared', 'Resource', 'Vnffgs', 'Solution','Reason','UsedTime','SfcCost','SfcRev','SysCost','SysRev','SysRevCostRatio'])
        contextDict = {'Event':'I','Time':0.00,
                       'Resource':self.vnfVim.get_net_remain_resource_list()}
        TRACE_RESULT.write(contextDict)

        TRACE_NFVI.ready(['Event', 'Time']+[element for nfvi in self.vnfVim.nfvi_group.values() 
                                                    for element in [nfvi.name+"_cpu", nfvi.name+"_ram", nfvi.name+"_rom", nfvi.name+"_band", nfvi.name+"_vnfs"]])
        contextDict = {'Event':'I','Time':0.00}
        contextDict.update({
                            key: value for nfvi in self.vnfVim.nfvi_group.values() 
                            for key, value in [
                                (nfvi.name + "_cpu", nfvi.resource_remain.get('cpu', 0)),
                                (nfvi.name + "_ram", nfvi.resource_remain.get('ram', 0)),
                                (nfvi.name + "_rom", nfvi.resource_remain.get('rom', 0)),
                                (nfvi.name + "_band", nfvi.get_remain_bandwidth()),
                                (nfvi.name + "_vnfs", nfvi.get_deployed_vnfs())]
                            })
        TRACE_NFVI.write(contextDict)
        
        self.solver_deploy = solver_deploy
        self.solver_deploy.ready_for_controller(self)


    def receive_sfc_req(self, sfc_req:SfcReq, req_type:str):
        if req_type == 'arrive':
            self.__handle_arrive(sfc_req)
        elif req_type == 'leave':
            self.__handle_leave(sfc_req)
        else:
            pass
            
    
    def __handle_arrive(self, sfc_req:SfcReq):
        if self.solver_deploy == None:
            raise ValueError(f"{self.name}: Solver Deploy is not set yet!")
        
        vnffgManager = VnffgManager(f"vnffg{sfc_req.id}", self, sfc_req)
        vnffgManager._activate(self.scheduler, self.logger)
        
        handle_start_time = Time.now()
        solutions_deploy = vnffgManager.handle_arrive() # vnffgManager接管sfc_req，并返回部署方案集合
        handle_end_time = Time.now()
        
        if solutions_deploy[-1].current_result == True:
            self.vnffg_group.append(vnffgManager)
            self.logger.info(f"{self.scheduler.now}: make new vnffg_manager for sfc_req: {sfc_req.id}, current vnffg_group_len: {len(self.vnffg_group)}")
        else:
            pass
        
        # region Arrive Trace ------------------------------------------------------------------
        self.update_system_cost_rev()
        
        contextDict = {'Event':'+','Time':self.scheduler.now,'SfcId':sfc_req.id,
                    'Result':solutions_deploy[-1].current_result,
                    'Shared':solutions_deploy[-1].share_node,
                    'Resource':self.vnfVim.get_net_remain_resource_list(),
                    'Vnffgs':[vnffg.id for vnffg in self.vnffg_group],
                    'Solution':  f"node:{self.vnfVim.get_nfvis_name_with_id(list(solutions_deploy[-1].map_node.values()))}" 
                                + f" & link:{[[self.vnfVim.get_nfvis_name_with_id([link_pare[0],link_pare[1]]) for link_pare in path_link] for path_link in list(solutions_deploy[-1].map_link.values())]}"
                                + f" & latency:{solutions_deploy[-1].current_latency.to(u.ms)}/{vnffgManager.sfc_req.sfc_qos.get('latency').to(u.ms)}",
                    'Reason':solutions_deploy[-1].current_description,
                    'UsedTime':(handle_end_time-handle_start_time).to(u.s),
                    'SfcCost':vnffgManager.get_current_total_cost(),
                    'SfcRev':vnffgManager.get_current_total_revenue(),
                    'SysCost':self.system_total_cost,
                    'SysRev':self.system_total_rev,
                    'SysRevCostRatio':self.system_total_rev/self.system_total_cost if self.system_total_cost!= 0 else 0.0}
            
        TRACE_RESULT.write(contextDict)

        contextDict = {'Event':'+','Time':self.scheduler.now}
        contextDict.update({
                            key: value for nfvi in self.vnfVim.nfvi_group.values() 
                            for key, value in [
                                (nfvi.name + "_cpu", nfvi.resource_remain.get('cpu', 0)),
                                (nfvi.name + "_ram", nfvi.resource_remain.get('ram', 0)),
                                (nfvi.name + "_rom", nfvi.resource_remain.get('rom', 0)),
                                (nfvi.name + "_band", nfvi.get_remain_bandwidth()),
                                (nfvi.name + "_vnfs", nfvi.get_deployed_vnfs())]
                            })
        TRACE_NFVI.write(contextDict)
        # endregion ------------------------------------------------------------------

    def __handle_leave(self, sfc_req:SfcReq):
        solutions_deploy = None
        for vnffgManager in self.vnffg_group:
            if vnffgManager.sfc_req == sfc_req:
                solutions_deploy = vnffgManager.handle_ending()
                self.vnffg_group_history.append(vnffgManager)
                self.vnffg_group.remove(vnffgManager)
                self.logger.info(f"{self.scheduler.now}: remove vnffg_manager for sfc_req: {sfc_req.id}, "
                                 f"current vnffg_group_len: {len(self.vnffg_group)}")
                break
    
        # region Leave Trace ------------------------------------------------------------------
        self.update_system_cost_rev()
        
        contextDict = {'Event':'-','Time':self.scheduler.now,'SfcId':sfc_req.id,
                       'Resource':self.vnfVim.get_net_remain_resource_list(),
                       'Vnffgs':[vnffg.id for vnffg in self.vnffg_group],
                       'SysCost': self.system_total_cost,
                       'SysRev': self.system_total_rev,
                       'SysRevCostRatio': self.system_total_rev/self.system_total_cost if self.system_total_cost!= 0 else 0.0}
        if solutions_deploy == None:
            # 没有找到对应的vnffg，说明是服务被提前结束
            contextDict['Result'] = False
        else:
            # 找到对应的vnffg，说明是服务可以被正常结束
            contextDict['Result'] = solutions_deploy[-1].current_result
            contextDict['Reason'] = solutions_deploy[-1].current_description
            contextDict['SfcCost'] = vnffgManager.get_current_total_cost()
            contextDict['SfcRev'] = vnffgManager.get_current_total_revenue()
        TRACE_RESULT.write(contextDict)

        contextDict = {'Event':'-','Time':self.scheduler.now}
        contextDict.update({
                            key: value for nfvi in self.vnfVim.nfvi_group.values() 
                            for key, value in [
                                (nfvi.name + "_cpu", nfvi.resource_remain.get('cpu', 0)),
                                (nfvi.name + "_ram", nfvi.resource_remain.get('ram', 0)),
                                (nfvi.name + "_rom", nfvi.resource_remain.get('rom', 0)),
                                (nfvi.name + "_band", nfvi.get_remain_bandwidth()),
                                (nfvi.name + "_vnfs", nfvi.get_deployed_vnfs())]
                            })
        TRACE_NFVI.write(contextDict)
        # endregion ------------------------------------------------------------------
    
    def update_system_cost_rev(self):
        """计算 NFVO 系统总的成本与收益"""
        self.system_total_cost = 0.0
        self.system_total_rev = 0.0
        for vnffgManager in self.vnffg_group:
            self.system_total_cost += vnffgManager.get_current_total_cost()
            self.system_total_rev += vnffgManager.get_current_total_revenue()
        for vnffgManager in self.vnffg_group_history:
            self.system_total_cost += vnffgManager.get_current_total_cost()
            self.system_total_rev += vnffgManager.get_current_total_revenue()
    
class VnffgManager(OModule):
    def __init__(self, name:str, nfvo:NfvOrchestrator, sfc_req:SfcReq):
        super().__init__(name)
        
        self.id = sfc_req.id

        self.nfvo = nfvo
        self.vnfVim = nfvo.vnfVim
        self.vnfManager = nfvo.vnfManager
        self.ueManager = nfvo.ueManager
        self.sfc_req = sfc_req
        self.vnfEms:list[VnfEm] = []
        
        if self.sfc_req.sfc_type in ['Ue2Ue','UeAccess']:
            self.ue_access_start = self.ueManager.get_ue_from_group(self.sfc_req.sfc_end_point[0])
            self.ue_access_end = self.ueManager.get_ue_from_group(self.sfc_req.sfc_end_point[1])
        
        self.solver_deploy = nfvo.solver_deploy
        self.solver_deploy_guardian_process = False
        self.solutions_deploy:list[SolutionDeploy] = []
        """在 SFC 运行过程中所产生的编排方案历史记录, 由求解器得到最新的编排方案后, 由 VnffgManager 记录并保存"""
        
        self.solver_e2e:SolverE2EBase = None
        self.solver_e2e_process = False
        self.solutions_e2e:list[SolutionE2E] = []
        

    def handle_arrive(self):
        solution_deploy:SolutionDeploy = self.solver_deploy.solve_embedding(self)
        
        if solution_deploy.current_result == True:
            # 如果嵌入成功，则按照solution进行部署
            self.__action_embedding_vnfs(solution_deploy)
            
            if self.sfc_req.sfc_type == 'Ue2Ue':
                self.__action_access_route_with_ue2ue_type(solution_deploy)
                self.__action_start_transport_with_ue2ue_type()
        else:
            # 如果嵌入失败，则不做任何部署
            pass

        # 不管成功与否，都要保存当前的部署方案
        self.solutions_deploy.append(copy.deepcopy(solution_deploy))
        
        if solution_deploy.current_result == True:
            # 如果部署成功，则启动 部署 维护进程
            self.solver_deploy_guardian_process = True
            self.scheduler.process(self.handle_guardian_process())
            
            # 如果部署成功，则启动 E2E 调度进程
            if self.sfc_req.sfc_type == 'Ue2Ue':
                self.solver_e2e = SolverE2EBase(self)
                self.solver_e2e_process = True
                self.scheduler.process(self.handle_adjustment_process())
            
        return self.solutions_deploy


    def handle_ending(self):
        solution:SolutionDeploy = self.solver_deploy.solve_ending(self)
        
        if solution.current_result == True:
            # 如果服务正常结束，则停止 E2E 调度进程
            if self.sfc_req.sfc_type == 'Ue2Ue':
                self.solver_e2e_process = False
                self.solver_e2e.solve_ending()
            
            # 如果服务正常结束，则停止 部署 维护进程
            self.solver_deploy_guardian_process = False
        
        if solution.current_result == True:
            # 如果服务正常结束，则按照之前的求解释放资源
            if self.sfc_req.sfc_type == 'Ue2Ue':
                self.__action_stop_transport_with_ue2ue_type()
                self.__action_release_route_with_ue2ue_type(solution)
            
            self.__action_release_vnfs(solution)
        else:
            # 如果服务按照异常结束，则无需释放资源，因为之前发生异常时已经处理过了
            pass

        # 不管成功与否，都要保存当前的部署方案
        self.solutions_deploy.append(copy.deepcopy(solution))
        
        return self.solutions_deploy
    
        
    def handle_topochange(self):
        # 在迁移过程中，应该关闭 部署 的维护进程与 E2E 调度进程
        self.solver_deploy_guardian_process = False
        
        if self.sfc_req.sfc_type == 'Ue2Ue':
            self.solver_e2e_process = False
            self.solver_e2e.solve_ending() # 在结束后会被覆盖新的调度器，因此暂时结算
        
        #   先按照之前的部署释放资源
        if self.sfc_req.sfc_type == 'Ue2Ue':
            self.__action_stop_transport_with_ue2ue_type()
            self.__action_release_route_with_ue2ue_type(self.solutions_deploy[-1])
            
        self.__action_release_vnfs(self.solutions_deploy[-1])
        
        handle_start_time = Time.now()
        solution_deploy:SolutionDeploy = self.solver_deploy.solve_migration(self)
        handle_end_time = Time.now()
        
        if solution_deploy.current_result == True:
            # 如果迁移成功按照新的部署方案部署
            self.__action_embedding_vnfs(solution_deploy)
            if self.sfc_req.sfc_type == 'Ue2Ue':
                self.__action_access_route_with_ue2ue_type(solution_deploy)
                self.__action_start_transport_with_ue2ue_type()
        else:
            # 如果迁移失败，将自己从 nfvo 管理器中移除
            self.nfvo.vnffg_group_history.append(self)
            self.nfvo.vnffg_group.remove(self)

        # 不管成功与否，都要保存当前的部署方案
        self.solutions_deploy.append(copy.deepcopy(solution_deploy))
        
        if solution_deploy.current_result == True:
            # 如果迁移成功，则重新启动 部署 维护进程与 E2E 调度进程
            self.solver_deploy_guardian_process = True
            
            if self.sfc_req.sfc_type == 'Ue2Ue':
                self.solver_e2e = SolverE2EBase(self) # 需使用新的调度器管理资源分配
                self.solver_e2e_process = True
        else:
            # 如果迁移失败，则停止 e2e 维护进程与调度进程
            
            if self.sfc_req.sfc_type == 'Ue2Ue':
                self.solver_e2e_process = False
            
            self.solver_deploy_guardian_process = False
        
        # region Migrate Trace ------------------------------------------------------------------
        self.nfvo.update_system_cost_rev()
        
        contextDict = {'Event':'d','Time':self.scheduler.now,'SfcId':self.sfc_req.id,
                    'Result':self.solutions_deploy[-1].current_result,
                    'Shared':self.solutions_deploy[-1].share_node,
                    'Resource':self.vnfVim.get_net_remain_resource_list(),
                    'Vnffgs':[self.id],
                    'Solution':  f"node:{self.vnfVim.get_nfvis_name_with_id(list(self.solutions_deploy[-1].map_node.values()))}" 
                                + f" & link:{[[self.vnfVim.get_nfvis_name_with_id([link_pare[0],link_pare[1]]) for link_pare in path_link] for path_link in list(self.solutions_deploy[-1].map_link.values())]}"
                                + f" & latency:{self.solutions_deploy[-1].current_latency.to(u.ms)}/{self.sfc_req.sfc_qos.get('latency').to(u.ms)}",
                    'Reason':self.solutions_deploy[-1].current_description,
                    'UsedTime':(handle_end_time-handle_start_time).to(u.s),
                    'SfcCost':self.get_current_total_cost(),
                    'SfcRev':self.get_current_total_revenue(),
                    'SysCost':self.nfvo.system_total_cost,
                    'SysRev':self.nfvo.system_total_rev,
                    'SysRevCostRatio':self.nfvo.system_total_rev/self.nfvo.system_total_cost if self.nfvo.system_total_cost!= 0 else 0.0}
        TRACE_RESULT.write(contextDict)

        contextDict = {'Event':'d','Time':self.scheduler.now}
        contextDict.update({
                            key: value for nfvi in self.vnfVim.nfvi_group.values() 
                            for key, value in [
                                (nfvi.name + "_cpu", nfvi.resource_remain.get('cpu', 0)),
                                (nfvi.name + "_ram", nfvi.resource_remain.get('ram', 0)),
                                (nfvi.name + "_rom", nfvi.resource_remain.get('rom', 0)),
                                (nfvi.name + "_band", nfvi.get_remain_bandwidth()),
                                (nfvi.name + "_vnfs", nfvi.get_deployed_vnfs())]
                            })
        TRACE_NFVI.write(contextDict)
        # endregion ------------------------------------------------------------------


    def handle_adjustment_process(self):
        while self.solver_e2e_process:
            yield self.scheduler.timeout(self.sfc_req.sfc_qos.get('latency').to(u.ms).value)
            
            solution_e2e:SolutionE2E = self.solver_e2e.solve_adjustment()
            
            if solution_e2e == None:
            # 当前时刻调度器无输出，等待下一个时刻
                continue
            
            if solution_e2e.current_result == True:
                # 如果调度器成功输出，按照结果更新资源限制
                for i,vnfEm in enumerate(self.vnfEms):
                    for res_name, res_val in solution_e2e.resource.items():
                        if res_name in vnfEm.resource_limit and self.sfc_req.id in vnfEm.used_sfc_id:
                            vnfEm.used_sfc_resource[self.sfc_req.id][res_name] = res_val[i]
                            vnfEm.update_resource_limit()
            else:
                # 如果调度器失败输出，则不做任何调整
                pass
            
            # 无论成功与否，都要保存当前的调度结果
            self.solutions_e2e.append(copy.deepcopy(solution_e2e))
            
            # Print Trance ------------------------------------------------------------------
            contextDict = {'Event':'e','Time':self.scheduler.now,'SfcId':self.sfc_req.id,
                        'Result':self.solutions_e2e[-1].current_result,
                        'Resource':self.vnfVim.get_net_remain_resource_list(),
                        'Vnffgs':[self.id]}
            if self.solutions_e2e[-1].current_result == True:
                contextDict['Solution'] = self.solutions_e2e[-1].resource.get('cpu', None)
            else:
                contextDict['Reason'] = self.solutions_e2e[-1].current_description
                
            TRACE_RESULT.write(contextDict)

            contextDict = {'Event':'e','Time':self.scheduler.now}
            contextDict.update({
                                key: value for nfvi in self.vnfVim.nfvi_group.values() 
                                for key, value in [
                                    (nfvi.name + "_cpu", nfvi.resource_remain.get('cpu', 0)),
                                    (nfvi.name + "_ram", nfvi.resource_remain.get('ram', 0)),
                                    (nfvi.name + "_rom", nfvi.resource_remain.get('rom', 0)),
                                    (nfvi.name + "_band", nfvi.get_remain_bandwidth()),
                                    (nfvi.name + "_vnfs", nfvi.get_deployed_vnfs())]
                                })
            TRACE_NFVI.write(contextDict)
            # Print Trance End ------------------------------------------------------------------

    
    def handle_guardian_process(self, cycle=2):
        """维护 部署 进程函数
        
        Args:
            cycle (int, optional): 维护周期相较于端到端时延倍率. Defaults to 2.
            
        Yields:
            调度器超时对象，用于控制监测周期
            
        Notes:
            认为按照当前部署方案使得端到端的传播时延累积已经超过了用户服务质量要求，则需要进行迁移。
            
            因为端到端的时延由传播时延+处理时延组成, 既然传播时延已经超过了用户服务质量要求，则说明处理时延已经不足以满足用户的需求，
            
            因此需要迁移到另一个 NFVI 节点, 试图降低传播时延。
        """
        while self.solver_deploy_guardian_process:
            # 等待监测周期
            yield self.scheduler.timeout(cycle * self.sfc_req.sfc_qos.get('latency').to(u.ms).value)
            current_latency = self.solver_deploy.get_latency_predict(self,direct=False)
            # print(f"solver_deploy_guardian_process: {current_latency}")
            if current_latency > self.sfc_req.sfc_qos.get('latency') and self.vnfEms != []:
                # 只有当当前时延超过用户服务质量要求，且 VNF 节点资源仍然可用时才进行迁移（有可能已结束服务）
                self.handle_topochange()
            
    def __action_embedding_vnfs(self,solution:SolutionDeploy):
        for i, nfvi_id in enumerate(solution.map_node.values()):
            # 获取所需部署 VNF 所在的 NFVI
            nfvi = self.vnfVim.nfvi_group[nfvi_id]
            if solution.share_node[i] == None:
                # 实例化新的 VNF 节点
                vnfem = self.vnfManager.get_vnf_from_templates(self.sfc_req.sfc_vnfs_type[i])
                vnfem.name = f"SFC{self.id}VNF{i}"
                vnfem.node_handler = VnfContainer(vnfem.name, vnfem.type)
                vnfem.uesd_shared = self.sfc_req.sfc_vnfs_shared[i] # 标识该 VNF 节点是否支持被多个 SFC 共享使用
                vnfem.used_sfc_id.append(self.sfc_req.id)
                vnfem.used_sfc_resource[self.sfc_req.id] = {}
                for res_name, res_val_list in solution.resource.items():
                    if res_name in vnfem.resource_limit:
                        vnfem.used_sfc_resource[self.sfc_req.id][res_name] = res_val_list[i]
                vnfem.update_resource_limit()
                nfvi.deploy_VNF(vnfem)
                self.vnfManager.add_vnf_into_group(vnfem)
                self.logger.info(f"{self.scheduler.now}: {self.name} deploy new VNF {vnfem.name} on NFVI {nfvi.name}")

            elif solution.share_node[i] != None:
                # 复用已部署的 VNF 节点
                vnfem_id = solution.share_node[i]
                vnfem = self.vnfManager.get_vnf_from_group(vnfem_id)
                vnfem.used_sfc_id.append(self.sfc_req.id)
                vnfem.used_sfc_resource[self.sfc_req.id] = {}
                for res_name, res_val_list in solution.resource.items():
                    if res_name in vnfem.resource_limit:
                        vnfem.used_sfc_resource[self.sfc_req.id][res_name] = res_val_list[i]
                vnfem.update_resource_limit()
                nfvi.update_remain_resource()
                self.logger.info(f"{self.scheduler.now}: {self.name} reuse the VNF {vnfem.name} on NFVI {nfvi.name}")
                
            self.vnfEms.append(vnfem)
            
    def __action_access_route_with_ue2ue_type(self,solution:SolutionDeploy):
        # 在 SFC 的首尾 VNF 所在的 NFVI 上接入 UE 节点（为 UE 节点分配 IP 地址）
        nfvi_access_start = self.vnfVim.nfvi_group[list(solution.map_node.values())[0]]
        nfvi_access_end = self.vnfVim.nfvi_group[list(solution.map_node.values())[-1]]
            # 接入业务发起方 UE 节点
        nfvi_access_start.access_ue(self.ue_access_start)
        self.logger.info(f"{self.scheduler.now}: {self.name} access "
                            f"UE {self.ue_access_start.name}:{self.ue_access_start.ip} "
                            f"on NFVI {nfvi_access_start.name}")
            # 接入业务接收方 UE 节点
        nfvi_access_end.access_ue(self.ue_access_end)
        self.logger.info(f"{self.scheduler.now}: {self.name} access "
                            f"UE {self.ue_access_end.name}:{self.ue_access_end.ip} "
                            f"on NFVI {nfvi_access_end.name}")
        
        # 配置部署了 VNF 的各个 NFVI 上的转发路由表
        for i, nfvi_id in enumerate(solution.map_node.values()):
            nfvi = self.vnfVim.nfvi_group[nfvi_id]
            
            # 在 NFVI 上配置导引到在自己设备上的 VNF 的转发表
            vnfEm_self = self.vnfEms[i]
            nfvi.set_route(aim_ip_addr=vnfEm_self.node_handler.networkLayer.ip_addr,
                            ethernet_phy_name=nfvi.get_route(vnfEm_self.node_handler.networkLayer.ip_addr))
            self.logger.info(f"{self.scheduler.now}: {self.name} set route for "
                                f"VNF {vnfEm_self.node_handler.name}:{vnfEm_self.node_handler.networkLayer.ip_addr} "
                                f"on NFVI {nfvi.name} use EthPhy")
            
            if i+1 < len(self.vnfEms):
                # 在 NFVI 上配置导引到下一跳 NFVI 上的 VNF 的转发表
                if solution.map_node[i+1] == solution.map_node[i]:
                    # 下一跳要部署 VNF 的 NFVI 也是自身 (导引本地 VNF 之前已经完成了)
                    pass
                else:
                    # 下一跳要部署 VNF 的 NFVI 不是自身，将其发至无线设备或者激光设备
                    vnfEm_next = self.vnfEms[i+1]
                    path = solution.map_link[(i,i+1)]
                    for sub_path in path:
                        nfvi_1 = self.vnfVim.nfvi_group[sub_path[0]]
                        nfvi_2 = self.vnfVim.nfvi_group[sub_path[1]]

                        if nfvi_1.node_type == "Sat" and nfvi_2.node_type == "Sat":
                            # 两端都是激光设备，需将流量导引至激光设备
                            nfvi_1_lasers_aim_ip = [laser.aim_laser_ip for laser in nfvi_1.node_handle.laser_group]
                            nfvi_2_laser_ip = [laser.networkLayer.ip_addr for laser in nfvi_2.node_handle.laser_group]
                            # 找到交集
                            aim_laser_ip = list(set(nfvi_1_lasers_aim_ip) & set(nfvi_2_laser_ip))
                            if len(aim_laser_ip) == 0:
                                # 无交集，说明两个平台之间激光不通，之前的部署方案不合理
                                raise Exception(f"{self.name}: No laser intersection between {nfvi_1.name} and {nfvi_2.name}")
                            else:
                                # 找到该交集对应的激光设备
                                aim_laser_ip = aim_laser_ip[0]
                                to_laser = [laser for laser in nfvi_1.node_handle.laser_group 
                                             if laser.aim_laser_ip == aim_laser_ip]
                                nfvi_1.set_route(aim_ip_addr=vnfEm_next.node_handler.networkLayer.ip_addr,
                                                  ethernet_phy_name=nfvi_1.get_route(to_laser[0].networkLayer.ip_addr))
                                self.logger.info(f"{self.scheduler.now}: {self.name} set route for "
                                            f"VNF {vnfEm_next.node_handler.name}:{vnfEm_next.node_handler.networkLayer.ip_addr} "
                                            f"on NFVI {nfvi_1.name} Use Laser {to_laser[0].name}")
                        else:
                            # 其中某一段是无线设备，需将流量导引至无线设备
                            nfvi_1.set_route(aim_ip_addr=vnfEm_next.node_handler.networkLayer.ip_addr,
                                             ethernet_phy_name=nfvi_1.get_radio_ethernet_phy_name())
                            self.logger.info(f"{self.scheduler.now}: {self.name} set route for "
                                            f"VNF {vnfEm_next.node_handler.name}:{vnfEm_next.node_handler.networkLayer.ip_addr} "
                                            f"on NFVI {nfvi_1.name} Use Radio")
            else:
                # 在末端 NFVI 上配置导引到最后一跳 UE 上的 VNF 的转发表（发至无线设备中）
                nfvi.set_route(aim_ip_addr=self.ue_access_end.ip,
                                ethernet_phy_name=nfvi.get_radio_ethernet_phy_name())
                self.logger.info(f"{self.scheduler.now}: {self.name} set route for "
                                    f"UE {self.ue_access_end.node_handle.name}:{self.ue_access_end.ip} "
                                    f"on NFVI {nfvi.name} Use Radio")


    def __action_start_transport_with_ue2ue_type(self):
        # 启动 UE 间的传输流, 定义传输路径（使用数据包中的段路由）
        sfc_pkt_segment = []
        sfc_pkt_segment.append(self.ue_access_end.ip)
        for vnfem in self.vnfEms[::-1]:
            sfc_pkt_segment.append(vnfem.node_handler.networkLayer.ip_addr)
            
        self.ue_access_start.start_transport(sfc_req=self.sfc_req, 
                                             segment_list=sfc_pkt_segment, 
                                             receiver=self.ue_access_end.name)
        self.logger.info(f"{self.scheduler.now}: {self.name} start transport for "
                            f"{self.ue_access_start.name}:{self.ue_access_start.ip} "
                            f"-> {self.ue_access_end.name}:{self.ue_access_end.ip} "
                            f"with segment {sfc_pkt_segment}")


    def __action_release_vnfs(self,solution:SolutionDeploy):
        if self.vnfEms == []:
            return
        
        for i, nfvi_id in enumerate(solution.map_node.values()):
            # 提取需要释放的 VNF 的信息
            vnfem = self.vnfEms[i]
            
            # 检查是否有其他 SFC 正在使用该 VNF
            if self.sfc_req.id in vnfem.used_sfc_id:
                vnfem.used_sfc_id.remove(self.sfc_req.id)
                vnfem.used_sfc_resource.pop(self.sfc_req.id)

            if len(vnfem.used_sfc_id) == 0:
                # 如果没有其他 SFC 正在使用该 VNF，则命令 NFVI 释放该 VNF 节点
                nfvi = self.vnfVim.nfvi_group[nfvi_id]
                nfvi.undeploy_VNF(vnfem)
                self.logger.info(f"{self.scheduler.now}: {self.name} undeploy VNF {vnfem.name} on NFVI {nfvi.name}")
            else:
                # 如果仍有其他 SFC 正在使用该 VNF，则保留该 VNF 节点
                nfvi = self.vnfVim.nfvi_group[nfvi_id]
                self.logger.info(f"{self.scheduler.now}: {self.name} does not undeploy VNF {vnfem.name} is still used by SFC {vnfem.used_sfc_id} on NFVI {nfvi.name}")
                vnfem.update_resource_limit()
                
        # 清空 VNF 节点列表
        self.vnfEms.clear()
    
    def __action_release_route_with_ue2ue_type(self,solution:SolutionDeploy):
        # 第一步：释放 SFC 的首尾 VNF 所在的 NFVI 上接入 UE 节点 ---------------------------------
        nfvi_access_start = self.vnfVim.nfvi_group[list(solution.map_node.values())[0]]
        nfvi_access_end = self.vnfVim.nfvi_group[list(solution.map_node.values())[-1]]
        # 释放业务发起方 UE 节点
        nfvi_access_start.unaccess_ue(self.ue_access_start)
        self.logger.info(f"{self.scheduler.now}: {self.name} release "
                            f"UE {self.ue_access_start.name}"
                            f"on NFVI {nfvi_access_start.name}")
        # 释放业务接收方 UE 节点
        nfvi_access_end.unaccess_ue(self.ue_access_end)
        self.logger.info(f"{self.scheduler.now}: {self.name} release "
                            f"UE {self.ue_access_end.name}"
                            f"on NFVI {nfvi_access_end.name}")
        
        # 第二步：释放各个 NFVI 上的转发路由表  -----------------------------------------------------
        for i, nfvi_id in enumerate(solution.map_node.values()):
            nfvi = self.vnfVim.nfvi_group[nfvi_id]
            
            # 1：处理在 NFVI 上导引到在自己设备上的 VNF 的转发表
            vnfEm_self = self.vnfEms[i]
            
            # 清理 vnfEm_self 上该 sfc 的使用标记
            if self.sfc_req.id in vnfEm_self.used_sfc_id:
                vnfEm_self.used_sfc_id.remove(self.sfc_req.id)
                vnfEm_self.used_sfc_resource.pop(self.sfc_req.id)
                
            if len(vnfEm_self.used_sfc_id) == 0:
            # 如果没有其他 SFC 正在使用该 VNF，则删除该 VNF 的转发表
                nfvi.delete_route(aim_ip_addr=vnfEm_self.node_handler.networkLayer.ip_addr)
                self.logger.info(f"{self.scheduler.now}: {self.name} delete route for "
                                    f"VNF {vnfEm_self.name}:{vnfEm_self.node_handler.networkLayer.ip_addr} "
                                    f"on NFVI {nfvi.name}")
            else:
            # 如果仍有其他 SFC 正在使用该 VNF，则保留该 VNF 的转发表
                self.logger.info(f"{self.scheduler.now}: {self.name} does not delete route for "
                                 f"VNF {vnfEm_self.name} is still used by SFC {vnfEm_self.used_sfc_id} "
                                 f"on NFVI {nfvi.name}")
            
            # 2：处理在 NFVI 上导引到下一跳 NFVI 上的 VNF 的转发表
            if i+1 < len(self.vnfEms):
                if solution.map_node[i+1] == solution.map_node[i]:
                    # 下一跳要部署 VNF 的 NFVI 也是自身 (删除本地 VNF 的导引之前已经完成了)
                    pass
                else:
                    # 下一跳要部署 VNF 的 NFVI 不是自身，删除导引至下一跳 NFVI 上的 VNF 的转发表
                    vnfEm_next = self.vnfEms[i+1]
                    if self.sfc_req.id in vnfEm_next.used_sfc_id:
                        vnfEm_next.used_sfc_id.remove(self.sfc_req.id)
                        vnfEm_next.used_sfc_resource.pop(self.sfc_req.id)
                    # 检查是否有其他 SFC 与该 SFC 使用相同的转发逻辑
                    if len(set(vnfEm_self.used_sfc_id) & set(vnfEm_next.used_sfc_id)) == 0:
                        # 如果没有其他 SFC 与该 SFC 使用相同的转发逻辑，即 vnfEm_self 和 vnfEm_next 不存在交集
                        path = solution.map_link[(i,i+1)]
                        for sub_path in path:
                            nfvi_1 = self.vnfVim.nfvi_group[sub_path[0]]
                            nfvi_2 = self.vnfVim.nfvi_group[sub_path[1]]
                            nfvi_1.delete_route(aim_ip_addr=vnfEm_next.node_handler.networkLayer.ip_addr)
                            self.logger.info(f"{self.scheduler.now}: {self.name} delete route for "
                                        f"VNF {vnfEm_next.name}:{vnfEm_next.node_handler.networkLayer.ip_addr} "
                                        f"on NFVI {nfvi_1.name}")
                    else:
                        # 如果仍有其他 SFC 与该 SFC 使用相同的转发逻辑，则保留该 VNF 的转发表
                        self.logger.info(f"{self.scheduler.now}: {self.name} does not delete route for "
                                        f"VNF {vnfEm_next.name} is still used by SFC {vnfEm_next.used_sfc_id} "
                                        f"on NFVI {nfvi.name}")
            else:
                # 处理末端转发（至最终 UE）
                nfvi.delete_route(aim_ip_addr=self.ue_access_end.ip)
                self.logger.info(f"{self.scheduler.now}: {self.name} delete route for "
                                    f"UE {self.ue_access_end.node_handle.name}:{self.ue_access_end.ip} "
                                    f"on NFVI {nfvi.name}")
    
    def __action_stop_transport_with_ue2ue_type(self):
        # 停止 UE 间的传输流
        self.ue_access_start.stop_transport()
        self.logger.info(f"{self.scheduler.now}: {self.name} stop transport for "
                            f"{self.ue_access_start.name}:{self.ue_access_start.ip} "
                            f"-> {self.ue_access_end.name}:{self.ue_access_end.ip}")
            
    def get_current_total_cost(self):
        """计算当前时刻总的服务开销
        """
        total_cost = 0
        if len(self.solutions_deploy) == 0:
            total_cost = 0
        else:
            total_cost += self.solutions_deploy[-1].cost_resource
            total_cost += self.solutions_deploy[-1].cost_migration
        
        return total_cost
            
    def get_current_total_revenue(self):
        """计算当前时刻总的服务收益
        """
        total_revenue = 0
        if len(self.solutions_deploy) == 0:
            return 0
        else:
            total_revenue += self.solutions_deploy[-1].revenue
        
        return total_revenue
