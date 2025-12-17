
import os
from matplotlib import pyplot as plt
from astropy import units as u
from enum import Enum, auto
import numpy as np
from scipy.optimize import bisect
from netorchestr.common.util import DataAnalysis

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from netorchestr.envir.node.controller.mano.nfvo import VnffgManager, VnfEm
    from netorchestr.eventlog import OLogItem

class SOLUTION_E2E_TYPE(Enum):
    NOTHING = auto()
    ADJ_SUCCESS = auto()
    ADJ_FAILED_FOR_NODE_CPU = auto()
    ADJ_FAILED_FOR_NODE_RAM = auto()
    ADJ_FAILED_FOR_LINK_BAND = auto()
    ADJ_FAILED_FOR_LATENCY = auto()

class SolutionE2E:
    def __init__(self) -> None:
        self.current_result: bool = False
        self.current_description :SOLUTION_E2E_TYPE = SOLUTION_E2E_TYPE.NOTHING

        self.resource: dict[str:list[int]] = {}
        """dict[resource name:list[value]]
        Description: the resources allocated on each VNF and link between VNFs
        """
        
        self.current_revenue: float = 0.0
        self.current_cost: float = 0.0

class SolverE2EBase():
    def __init__(self, vnffgManager:"VnffgManager"):
        self.vnffgManager = vnffgManager
        
        self.solution_deploy = vnffgManager.solutions_deploy[-1]
        
        self.aim_delay = self.vnffgManager.sfc_req.sfc_qos.get("latency", None).to(u.ms).value
        """目标延迟, 单位毫秒"""
        self.aim_overrate = self.vnffgManager.sfc_req.sfc_qos.get("overrate", None)
        """目标超载率, 小于1, 无量纲"""
        self.arrive_rate = 1/(self.vnffgManager.sfc_req.sfc_trans_model.get("interval", None).to(u.ms).value)
        """到达速率, 单位包每毫秒"""
        
        self.control_time = [self.vnffgManager.scheduler.now]
        
        self.last_record_length = 0 # 初始化上一次用户接收记录的长度
        self.actural_delay = [0]
        self.predict_delay = [0]
        self.kff = 0.002

        self.kp = 0.005
        self.ki = 0.0001
        self.kd = 0.0001
        self.i_val = 0
        """PID 算法中的积分项"""
        self.err_prev = 0
        """PID 算法中的前一时刻误差"""
        
        self.process_rate:dict["VnfEm",list[float]] = {}
        for i,vnfEm in enumerate(self.vnffgManager.vnfEms):
            self.process_rate[vnfEm] = [self.solution_deploy.resource.get("cpu", None)[i] * vnfEm.rate_per_core]
            
        self.queue_length:dict["VnfEm",list[float]] = {}
        for i,vnfEm in enumerate(self.vnffgManager.vnfEms):
            self.queue_length[vnfEm] = [0]
            
        self.revenue_list:list[float] = [0.0]
        self.cost_list:list[float] = [0.0]

    def calculate_revenue(self, performance_record:list[float], aim_delay:float, aim_overrate:float, arrive_rate:float):
        R_D = 1 - performance_record[-1]/aim_delay
        watch_window = 100
        delay_over_num = 0
        if len(performance_record) > watch_window:
            for i in range(len(performance_record)-watch_window, len(performance_record)):
                if performance_record[i] > aim_delay:
                    delay_over_num += 1
            P = delay_over_num/watch_window
        else:
            for i in range(len(performance_record)):
                if performance_record[i] > aim_delay:
                    delay_over_num += 1
            P = delay_over_num/len(performance_record)
        R_P = np.exp(-P/aim_overrate)
        R = arrive_rate * R_D * R_P
        return R 
    
    def netcalculate(self, service_curve:dict[str:float], arrive_curve:dict[str:float], aim_overrate:float, theta:float, nodenum:int):
        if service_curve['rho'] < arrive_curve['rho']:
            return np.inf, np.inf
        elif service_curve['rho'] == arrive_curve['rho']:
            gamma = 1
        else:
            gamma = 1 + 1 / (1 - np.exp(-theta * (service_curve['rho']-arrive_curve['rho'])))
        
        tau_left = service_curve['sigma'] / service_curve['rho']
        tau_right = (nodenum * np.log(gamma) - np.log(aim_overrate)) / (theta * service_curve['rho'])
        tau = tau_left + tau_right
        block = service_curve['sigma'] + (np.log(gamma) - np.log(aim_overrate))/theta
        return tau, block

    def netcalculate_inverse(self,arrive_curve:dict[str:float], aim_delay:float, aim_overrate:float, theta:float, nodenum:int):
        def equation(x, y_target):
            numerator = (nodenum * np.log(1 + 1 / (1 - np.exp(-theta * (x - arrive_curve['rho']))))) - np.log(aim_overrate)
            denominator = theta * x
            return numerator/denominator - y_target
        
        rho_left = arrive_curve['rho'] + 0.001
        rho_right = arrive_curve['rho'] * 10
        rho = bisect(lambda x: equation(x, aim_delay), rho_left, rho_right)
        return rho


    def solve_adjustment(self) -> SolutionE2E:
        if len(self.vnffgManager.vnfEms) == 0:
            # 还未完成部署，无法进行各个 vnf 的资源调度
            return None
        
        current_record_length = len(self.vnffgManager.ue_access_end.node_handle.appLayer.performance_record)
        
        if self.last_record_length == current_record_length:
            # 末端用户还未接收到新的数据包无法进行获取控制器的反馈
            return None
        else:
            # 末端用户接收到新的数据包,更新上一次用户接收记录的长度
            self.last_record_length = current_record_length 
        
        self.control_time.append(self.vnffgManager.scheduler.now)
        
        min_vnf_rate = np.inf
        min_vnf_index = -1
        for i,vnfEm in enumerate(self.vnffgManager.vnfEms):
            if self.process_rate[vnfEm][-1] < min_vnf_rate:
                min_vnf_rate = self.process_rate[vnfEm][-1]
                min_vnf_index = i
                
        tau, block = self.netcalculate(service_curve = {'rho':min_vnf_rate,
                                                        'sigma':0},
                                       arrive_curve = {'rho':self.arrive_rate,
                                                       'sigma':0},
                                       aim_overrate = self.aim_overrate, theta = 0.1, nodenum = len(self.vnffgManager.vnfEms))
        predict_delay = tau + 40 + 10 * len(self.vnffgManager.vnfEms)
        self.predict_delay.append(predict_delay)
        self.actural_delay.append(self.vnffgManager.ue_access_end.node_handle.appLayer.performance_record[-1])
        
        for vnfEm in self.vnffgManager.vnfEms:
            self.queue_length[vnfEm].append(
                len([req for req in vnfEm.node_handler.appLayer.req_processor.queue 
                     if vnfEm.node_handler.appLayer.req2msg[req].receiver == self.vnffgManager.ue_access_end.node_handle.name]))
        
        value_actural = np.average(np.array(self.vnffgManager.ue_access_end.node_handle.appLayer.performance_record[-20:]))
        
        value_Rff = self.kff * (predict_delay - self.aim_delay)
        
        value_err = value_actural - self.aim_delay
        value_P = self.kp * value_err
        value_I = 0#self.ki * value_err * self.aim_delay + self.i_val
        value_D = 0#self.kd * (self.err_prev - value_err) / self.aim_delay
        value_PIDff = value_P + value_I + value_D + value_Rff
        
        self.i_val = value_I
        self.err_prev = value_err
        
        
        solution_e2e = SolutionE2E()
        solution_e2e.resource["cpu"] = []
        if value_PIDff > 0:
            # 需要增加计算资源时仅对最小的 vnf 增加资源 (瓶颈 vnf)
            for i,vnfEm in enumerate(self.vnffgManager.vnfEms):
                if i == min_vnf_index:
                    self.process_rate[vnfEm].append(max(self.arrive_rate+0.1, self.process_rate[vnfEm][-1] + value_PIDff))
                else:
                    self.process_rate[vnfEm].append(self.process_rate[vnfEm][-1] + 0.0)
                    
                solution_e2e.resource["cpu"].append(self.process_rate[vnfEm][-1]/vnfEm.rate_per_core)
        else:
            # 需要减少计算资源时对所有 vnf 同时减少资源
            for i,vnfEm in enumerate(self.vnffgManager.vnfEms):
                self.process_rate[vnfEm].append(max(self.arrive_rate+0.1, self.process_rate[vnfEm][-1] + value_PIDff))
                solution_e2e.resource["cpu"].append(self.process_rate[vnfEm][-1]/vnfEm.rate_per_core)
        
        self.revenue_list.append(self.calculate_revenue(
                                    self.vnffgManager.ue_access_end.node_handle.appLayer.performance_record, 
                                    self.aim_delay, 
                                    self.aim_overrate, 
                                    self.arrive_rate))
        self.cost_list.append(sum(solution_e2e.resource.get("cpu", [])))
        
        print(f"\n Current time: {DataAnalysis.format_milliseconds(self.vnffgManager.scheduler.now)} \t | Vnffg {self.vnffgManager.id} report: \n"
              f"e2e delay: {self.actural_delay[-1]} | aim delay: {self.aim_delay} | predict delay: {predict_delay}\n"
              f"vnf total rate: {[vnfEm.node_handler.appLayer.process_rate for vnfEm in self.vnffgManager.vnfEms]} \n"
              f"vnf occupy rate: {[self.process_rate[vnfEm][-1] for vnfEm in self.vnffgManager.vnfEms]} \n"
              f"vnf total cpu: {[vnfEm.node_handler.resouce_limit.get('cpu', None) for vnfEm in self.vnffgManager.vnfEms]} \n"
              f"vnf occupy cpu: {[solution_e2e.resource['cpu'][i] for i,vnfEm in enumerate(self.vnffgManager.vnfEms)]} \n"
              f"vnf queue length: {[self.queue_length[vnfEm][-1] for vnfEm in self.vnffgManager.vnfEms]} \n"
              )
        print(f"Netcalculate: tau: {tau}  block: {block}  with rho: {min([self.process_rate[vnfEm][-1] for vnfEm in self.vnffgManager.vnfEms])} ")
        print(f"value_actural: {value_actural} | value_err: {value_err} | value_P: {value_P} | value_I: {value_I} "
              f"| value_D: {value_D} | value_Rff: {value_Rff} | value_PIDff: {value_PIDff}")
        print("-"*10+"\n")
        
        solution_e2e.current_result = True
        solution_e2e.current_description = SOLUTION_E2E_TYPE.ADJ_SUCCESS
        solution_e2e.current_revenue = self.revenue_list[-1]
        solution_e2e.current_cost = self.cost_list[-1]
        
        return solution_e2e     


    def solve_ending(self):
        """调度求解器结束时调用
        
        保存相关数据并绘图
        
        该函数会在当前工作空间下生成文件夹TraceVNFFG/，并在该文件夹下生成相关的图片文件
        
        进行最终收益率和成本率的计算
        """
        
        save_id = self.vnffgManager.scheduler.now
        
        fig_save_path = os.path.join(self.vnffgManager.vnfVim.net.logger.log_dir,
                                     "nfvo_monitor_figs",
                                     "TraceVNFFG",
                                     self.vnffgManager.name)
        os.makedirs(fig_save_path, exist_ok=True)
        
        plt.figure(figsize=(10, 5))
        plt.scatter(x=self.control_time, y=self.actural_delay, color="black", marker=".", s=10, label=f"{self.vnffgManager.name}_actural")
        # plt.plot(self.control_time, self.predict_delay, color="black", label=f"{self.vnffgManager.name}_predict", linewidth=1)
        plt.plot(self.control_time, [self.aim_delay]*len(self.control_time), linestyle="--", color="black", label=f"{self.vnffgManager.name}_aim")
        plt.xlabel("Time")
        plt.ylabel("Delay")
        plt.legend()
        plt.savefig(os.path.join(fig_save_path,f"{self.vnffgManager.name}_delay_{save_id}.png"))

        plt.figure(figsize=(10, 5))
        for vnfEm in self.queue_length.keys():
            plt.plot(self.control_time, self.queue_length[vnfEm], label=f"{vnfEm.name}_queue")
        plt.xlabel("Time")
        plt.ylabel("Queue Length")
        plt.legend()
        plt.savefig(os.path.join(fig_save_path,f"{self.vnffgManager.name}_queue_{save_id}.png"))

        plt.figure(figsize=(10, 5))
        for vnfEm in self.process_rate.keys():
            plt.plot(self.control_time, self.process_rate[vnfEm], label=f"{vnfEm.name}_rate")
        plt.xlabel("Time")
        plt.ylabel("Process Rate")
        plt.legend()
        plt.savefig(os.path.join(fig_save_path,f"{self.vnffgManager.name}_rate_{save_id}.png"))


        pkt_delay_receiver = []
        loggerItems:list[OLogItem] = self.vnffgManager.logger.extract_log_items()

        for item in loggerItems:
            if item.event == "r" and item.to_node == self.vnffgManager.ue_access_end.node_handle.name:
                if item.pkt_delay != "*":
                    pkt_delay_receiver.append(float(item.pkt_delay))
                    
        over_delay_num = 0
        for delay in pkt_delay_receiver:
            if delay > self.aim_delay:
                over_delay_num += 1
        
        print("\n\n"+"*"*10)
        print(f"{self.vnffgManager.name} at {save_id} pause service, revenue and cost report: ")
        print("*"*10)
        if len(pkt_delay_receiver) != 0:
            print(f"{self.vnffgManager.name}_over_delay_rate: {over_delay_num/len(pkt_delay_receiver)}")
        if sum(self.cost_list) != 0:
            print(f"{self.vnffgManager.name}_rev_cost_rate:",sum(self.revenue_list)/sum(self.cost_list))
        print("-"*10+"\n\n")
    
        data_save_path = os.path.join(self.vnffgManager.vnfVim.net.logger.log_dir,
                                       "nfvo_monitor_data",
                                       "TraceVNFFG",
                                       self.vnffgManager.name)
        os.makedirs(data_save_path, exist_ok=True)
    
        save_data = {}
        save_data["vnffg_id"] = self.vnffgManager.id
        save_data["ue_list"] = [self.vnffgManager.ue_access_start.node_handle.name,
                                self.vnffgManager.ue_access_end.node_handle.name]
        save_data["ue_ip_list"] = [self.vnffgManager.ue_access_start.ip,
                                    self.vnffgManager.ue_access_end.ip]
        save_data["vnf_list"] = [vnfEm.name for vnfEm in self.vnffgManager.vnfEms]
        save_data["vnf_ip_list"] = [vnfEm.ip for vnfEm in self.vnffgManager.vnfEms]
        save_data["control_time"] = self.control_time
        save_data["actural_delay"] = self.actural_delay
        save_data["predict_delay"] = self.predict_delay
        save_data["queue_length"] = {vnfEm.id:self.queue_length[vnfEm] for vnfEm in self.queue_length.keys()}
        save_data["process_rate"] = {vnfEm.id:self.process_rate[vnfEm] for vnfEm in self.process_rate.keys()}
        save_data["revenue_list"] = self.revenue_list
        save_data["cost_list"] = self.cost_list
        save_data["aim_delay"] = self.aim_delay
        save_data["aim_overrate"] = self.aim_overrate
        save_data["arrive_rate"] = self.arrive_rate
        save_data["kp"] = self.kp
        save_data["ki"] = self.ki
        save_data["kd"] = self.kd
        save_data["kff"] = self.kff
        save_data["pkt_delay_receiver"] = pkt_delay_receiver
        save_data["over_delay_num"] = over_delay_num
        
        import pickle
        with open(os.path.join(data_save_path,f"{self.vnffgManager.name}_data_{save_id}.pkl"), "wb") as f:
            pickle.dump(save_data, f)
            