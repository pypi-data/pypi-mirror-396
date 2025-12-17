
import numpy as np
from scipy.optimize import bisect
import matplotlib.pyplot as plt
from astropy import units as u
from astropy.time import Time
from netorchestr.envir.base import OModule
from netorchestr.envir.node.pedestrian import CrowdBase, PedestrianBase
from netorchestr.envir.node.ground import GroundServerBase
from netorchestr.envir.node.container import VnfBase
from netorchestr.eventlog import OLogItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from netorchestr.envir.base import ONet

class ControllerGlobal4Crowd(OModule):
    def __init__(self, name:str, net:"ONet"):
        super().__init__(name)
        
        self.net = net
        self.logger = net.logger
        self.scheduler = net.scheduler
        
        # 暂用测试数据
        
        # region 定义服务功能链路 1
        self.s1_aim_delay = 3
        self.s1_aim_overrate = 0.1
        self.s1_arrive_rate = 1
        self.s1_actural_delay = []
        self.s1_predict_delay = []
        self.s1_kff = 0.004

        self.s1_kp = 0.004
        self.s1_ki = 0.0001
        self.s1_kd = 0.0001
        self.s1_i_val = 0
        self.s1_err_prev = 0

        self.s1_process_rate_init = 2
        # self.s1_process_rate_init = self.netcalculate_inverse(arrive_curve={'rho':self.s1_arrive_rate,'sigma':0}, 
        #                                                       aim_delay=10, 
        #                                                       aim_overrate=self.s1_aim_overrate, 
        #                                                       theta=0.1, 
        #                                                       nodenum=3)
        self.s1v1_process_rate = [self.s1_process_rate_init*0.5]
        self.s1v2_process_rate = [self.s1_process_rate_init*0.5]
        self.s1v3_process_rate = [self.s1_process_rate_init*0.5]
        self.s1v1_queue_len = [0]
        self.s1v2_queue_len = [0]
        self.s1v3_queue_len = [0]
        self.s1_revenue_list = [0]
        self.s1_cost_list = [0]
        # endregion
        
        # region 定义服务功能链路 2
        self.s2_aim_delay = 2
        self.s2_aim_overrate = 0.1
        self.s2_arrive_rate = 1
        self.s2_actural_delay = []
        self.s2_predict_delay = []
        self.s2_kff = 0.004

        self.s2_kp = 0.004
        self.s2_ki = 0.0001
        self.s2_kd = 0.0001
        self.s2_i_val = 0
        self.s2_err_prev = 0

        self.s2_process_init = 2
        # self.s2_process_init = self.netcalculate_inverse(arrive_curve={'rho':self.s2_arrive_rate,'sigma':0}, 
        #                                                  aim_delay=5, 
        #                                                  aim_overrate=self.s2_aim_overrate, 
        #                                                  theta=0.1, 
        #                                                  nodenum=2)
        self.s2v1_process_rate = [self.s2_process_init*0.5]
        self.s2v2_process_rate = [self.s2_process_init*0.5]
        self.s2v1_queue_len = [0]
        self.s2v2_queue_len = [0]
        self.s2_revenue_list = [0]
        self.s2_cost_list = [0]
        
        # endregion
        
    def initialize(self):
        self.logger.debug(f"{self.scheduler.now}: ControllerGlobal initialize")
        
        vnf1:VnfBase = [module.vnfList[0] for module in self.net.modules if isinstance(module, GroundServerBase) and module.name == "Vim1"][0]
        vnf2:VnfBase = [module.vnfList[0] for module in self.net.modules if isinstance(module, GroundServerBase) and module.name == "Vim2"][0]
        vnf3:VnfBase = [module.vnfList[0] for module in self.net.modules if isinstance(module, GroundServerBase) and module.name == "Vim3"][0]
        
        vnf1.appLayer.process_rate = self.s1v1_process_rate[-1] + self.s2v1_process_rate[-1]
        vnf2.appLayer.process_rate = self.s1v2_process_rate[-1] + self.s2v2_process_rate[-1]
        vnf3.appLayer.process_rate = self.s1v3_process_rate[-1]
        
        self.scheduler.process(self.controller_process_sfc_1())
        self.scheduler.process(self.controller_process_sfc_2())
        
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
    
    def controller_process_sfc_1(self):
        while True:
            yield self.scheduler.timeout(self.s1_aim_delay)
            
            ue2:PedestrianBase = [module for module in self.net.modules if isinstance(module, PedestrianBase) and module.name == "Ue2"][0]
            
            if len(ue2.appLayer.performance_record) == 0:
                continue

            tau, block = self.netcalculate(service_curve = {'rho':min(self.s1v1_process_rate[-1],self.s1v2_process_rate[-1],self.s1v3_process_rate[-1]),'sigma':0},
                                           arrive_curve = {'rho':self.s1_arrive_rate,'sigma':0},
                                           aim_overrate = self.s1_aim_overrate, theta = 0.1, nodenum = 3)
            predict_delay = tau # + link1.delay + link2.delay + link3.delay + link4.delay
            self.s1_predict_delay.append(predict_delay)
            self.s1_actural_delay.append(ue2.appLayer.performance_record[-1])
            
            vnf1:VnfBase = [module.vnfList[0] for module in self.net.modules if isinstance(module, GroundServerBase) and module.name == "Vim1"][0]
            vnf2:VnfBase = [module.vnfList[0] for module in self.net.modules if isinstance(module, GroundServerBase) and module.name == "Vim2"][0]
            vnf3:VnfBase = [module.vnfList[0] for module in self.net.modules if isinstance(module, GroundServerBase) and module.name == "Vim3"][0]
            
            self.s1v1_queue_len.append(len([req for req in vnf1.appLayer.req_processor.queue if vnf1.appLayer.req2msg[req].receiver == "Ue2App"]))
            self.s1v2_queue_len.append(len([req for req in vnf2.appLayer.req_processor.queue if vnf2.appLayer.req2msg[req].receiver == "Ue2App"]))
            self.s1v3_queue_len.append(len([req for req in vnf3.appLayer.req_processor.queue if vnf3.appLayer.req2msg[req].receiver == "Ue2App"]))
            
            value_actural = np.average(np.array(ue2.appLayer.performance_record[-20:]))
            
            value_Rff = 0 # self.s1_kff * (predict_delay - self.s1_aim_delay)
            
            value_err = value_actural - self.s1_aim_delay
            value_P = self.s1_kp * value_err
            value_I = 0 # s1_ki * value_err * s1_aim_delay + s1_i_val
            value_D = 0 # s1_kd * (s1_err_prev - value_err) / s1_aim_delay
            value_PIDff = value_P + value_I + value_D + value_Rff
            
            self.s1_i_val = value_I
            self.s1_err_prev = value_err
            
            self.s1v1_process_rate.append(max(self.s1_arrive_rate+0.001, self.s1v1_process_rate[-1] + value_PIDff))
            self.s1v2_process_rate.append(max(self.s1_arrive_rate+0.001, self.s1v2_process_rate[-1] + value_PIDff))
            self.s1v3_process_rate.append(max(self.s1_arrive_rate+0.001, self.s1v3_process_rate[-1] + value_PIDff))

            # 最终作用在各个 vnf 上
            
            vnf1.appLayer.process_rate = self.s1v1_process_rate[-1] + self.s2v1_process_rate[-1]
            vnf2.appLayer.process_rate = self.s1v2_process_rate[-1] + self.s2v2_process_rate[-1]
            vnf3.appLayer.process_rate = self.s1v3_process_rate[-1]
            
            self.s1_revenue_list.append(self.calculate_revenue(ue2.appLayer.performance_record, self.s1_aim_delay, self.s1_aim_overrate, self.s1_arrive_rate))
            self.s1_cost_list.append(self.s1v1_process_rate[-1] + self.s1v2_process_rate[-1] + self.s1v3_process_rate[-1])
            
            print(f"\n Current time: {self.scheduler.now} \t | s1_perform: {ue2.appLayer.performance_record[-1]} \n \
                | vnf1_rate: {vnf1.appLayer.process_rate} \t | vnf2_rate: {vnf2.appLayer.process_rate} \t | vnf3_rate: {vnf3.appLayer.process_rate} \n \
                | s1v1_rate: {self.s1v1_process_rate[-1]} \t | s1v2_rate: {self.s1v2_process_rate[-1]} \t | s1v3_rate: {self.s1v3_process_rate[-1]} \n \
                | s1v1_queue: {self.s1v1_queue_len[-1]} \t | s1v2_queue: {self.s1v2_queue_len[-1]} \t | s1v3_queue: {self.s1v3_queue_len[-1]}")
            
            print(f"Netcalculate: tau: {tau}  block: {block}  with rho: {min(self.s1v1_process_rate[-1],self.s1v2_process_rate[-1],self.s1v3_process_rate[-1])}")

            print(f"value_actural: {value_actural} | value_err: {value_err} | value_P: {value_P} | value_I: {value_I} | value_D: {value_D} | value_PIDff: {value_PIDff}")
            print("-"*10+"\n")


    def controller_process_sfc_2(self):
        while True:
            yield self.scheduler.timeout(self.s2_aim_delay)
            
            ue4:PedestrianBase = [module for module in self.net.modules if isinstance(module, PedestrianBase) and module.name == "Ue4"][0]
            
            if len(ue4.appLayer.performance_record) == 0:
                continue
            
            tau, block = self.netcalculate(service_curve = {'rho':min(self.s2v1_process_rate[-1],self.s2v2_process_rate[-1]),'sigma':0},
                                           arrive_curve = {'rho':self.s2_arrive_rate,'sigma':0},
                                           aim_overrate = self.s2_aim_overrate, theta = 0.1, nodenum = 2)
            predict_delay = tau # + link5.delay + link6.delay
            self.s2_predict_delay.append(predict_delay)
            self.s2_actural_delay.append(ue4.appLayer.performance_record[-1])
            
            vnf1:VnfBase = [module.vnfList[0] for module in self.net.modules if isinstance(module, GroundServerBase) and module.name == "Vim1"][0]
            vnf2:VnfBase = [module.vnfList[0] for module in self.net.modules if isinstance(module, GroundServerBase) and module.name == "Vim2"][0]
            
            self.s2v1_queue_len.append(len([req for req in vnf1.appLayer.req_processor.queue if vnf1.appLayer.req2msg[req].receiver == "Ue4App"]))
            self.s2v2_queue_len.append(len([req for req in vnf2.appLayer.req_processor.queue if vnf2.appLayer.req2msg[req].receiver == "Ue4App"]))
            
            value_actural = np.average(np.array(ue4.appLayer.performance_record[-20:]))
            
            value_Rff = 0 # self.s2_kff * (predict_delay - self.s2_aim_delay)
            
            value_err = value_actural - self.s2_aim_delay
            value_P = self.s2_kp * value_err
            value_I = 0 # s2_ki * value_err * s2_aim_delay + s2_i_val
            value_D = 0 # s2_kd * (s2_err_prev - value_err) / s2_aim_delay
            value_PIDff = value_P + value_I + value_D + value_Rff
            
            self.s2_i_val = value_I
            self.s2_err_prev = value_err
            
            self.s2v1_process_rate.append(max(self.s2_arrive_rate+0.001, self.s2v1_process_rate[-1] + value_PIDff))
            self.s2v2_process_rate.append(max(self.s2_arrive_rate+0.001, self.s2v2_process_rate[-1] + value_PIDff))
            
            # 最终作用在各个 vnf 上
            
            vnf1.appLayer.process_rate = self.s2v1_process_rate[-1] + self.s1v1_process_rate[-1]
            vnf2.appLayer.process_rate = self.s2v2_process_rate[-1] + self.s1v2_process_rate[-1]
            
            self.s2_revenue_list.append(self.calculate_revenue(ue4.appLayer.performance_record, self.s2_aim_delay, self.s2_aim_overrate, self.s2_arrive_rate))
            self.s2_cost_list.append(self.s2v1_process_rate[-1] + self.s2v2_process_rate[-1])
            
            print(f"\n Current time: {self.scheduler.now} \t | s2_perform: {ue4.appLayer.performance_record[-1]} \n \
                | vnf1_rate: {vnf1.appLayer.process_rate} \t | vnf2_rate: {vnf2.appLayer.process_rate} \n \
                | s2v1_rate: {self.s2v1_process_rate[-1]} \t | s2v2_rate: {self.s2v2_process_rate[-1]} \n \
                | s2v1_queue: {self.s2v1_queue_len[-1]} \t | s2v2_queue: {self.s2v2_queue_len[-1]}")
            
            print(f"Netcalculate: tau: {tau}  block: {block}  with rho: {min(self.s2v1_process_rate[-1],self.s2v2_process_rate[-1])}")

            print(f"value_actural: {value_actural} | value_err: {value_err} | value_P: {value_P} | value_I: {value_I} | value_D: {value_D} | value_PIDff: {value_PIDff}")        
            print("-"*10+"\n")


    def draw_results(self):
        figure = plt.figure(figsize=(10, 5))

        plt.scatter(x=[i for i in range(len(self.s1_actural_delay))], y=self.s1_actural_delay, color="black", marker=".", s=10, label="SFC1")
        plt.scatter(x=[i for i in range(len(self.s2_actural_delay))], y=self.s2_actural_delay, color="red", marker=".", s=10, label="SFC2")
        # plt.plot([i for i in range(len(self.s1_predict_delay))], self.s1_predict_delay, color="black", label="SFC1_predict", linewidth=1)
        # plt.plot([i for i in range(len(self.s2_predict_delay))], self.s2_predict_delay, color="red", label="SFC2_predict", linewidth=1)
        plt.plot([i for i in range(len(self.s1_actural_delay))], [self.s1_aim_delay]*len(self.s1_actural_delay), linestyle="--", color="black", label="SFC1_aim")
        plt.plot([i for i in range(len(self.s2_actural_delay))], [self.s2_aim_delay]*len(self.s2_actural_delay), linestyle="--", color="red", label="SFC2_aim")

        plt.xlabel("Packet")
        plt.ylabel("Delay")
        plt.legend()
        plt.savefig(f"{self.net.name}_delay.png")

        figure = plt.figure(figsize=(10, 5))

        plt.plot([i for i in range(len(self.s1v1_queue_len))], self.s1v1_queue_len, label="s1v1_queue", marker=".", linestyle="-")
        plt.plot([i for i in range(len(self.s1v2_queue_len))], self.s1v2_queue_len, label="s1v2_queue", marker="o", linestyle="-")
        plt.plot([i for i in range(len(self.s1v3_queue_len))], self.s1v3_queue_len, label="s1v3_queue", marker="*", linestyle="-")
        plt.plot([i for i in range(len(self.s2v1_queue_len))], self.s2v1_queue_len, label="s2v1_queue", marker=".", linestyle="--")
        plt.plot([i for i in range(len(self.s2v2_queue_len))], self.s2v2_queue_len, label="s2v2_queue", marker="o", linestyle="--")

        plt.xlabel("Time")
        plt.ylabel("Queue Length")
        plt.legend()
        plt.savefig(f"{self.net.name}_queue.png")

        figure = plt.figure(figsize=(10, 5))

        plt.plot([i for i in range(len(self.s1v1_process_rate))], self.s1v1_process_rate, label="s1v1_process_rate", marker=".", linestyle="-")
        plt.plot([i for i in range(len(self.s1v2_process_rate))], self.s1v2_process_rate, label="s1v2_process_rate", marker="o", linestyle="-")
        plt.plot([i for i in range(len(self.s1v3_process_rate))], self.s1v3_process_rate, label="s1v3_process_rate", marker="*", linestyle="-")
        plt.plot([i for i in range(len(self.s2v1_process_rate))], self.s2v1_process_rate, label="s2v1_process_rate", marker=".", linestyle="--")
        plt.plot([i for i in range(len(self.s2v2_process_rate))], self.s2v2_process_rate, label="s2v2_process_rate", marker="o", linestyle="--")

        plt.xlabel("Time")
        plt.ylabel("Process Rate")
        plt.legend()
        plt.savefig(f"{self.net.name}_process_rate.png")

        # endregion

        # region 输出统计结果

        pkt_delay_sfc1 = []
        pkt_delay_sfc2 = []
        loggerItems:list[OLogItem] = self.logger.extract_log_items()

        for item in loggerItems:
            if item.event == "r" and item.to_node == "Ue2App":
                if item.pkt_delay != "*":
                    pkt_delay_sfc1.append(float(item.pkt_delay))
            elif item.event == "r" and item.to_node == "Ue4App":
                if item.pkt_delay != "*":
                    pkt_delay_sfc2.append(float(item.pkt_delay))

        over_delay_num_sfc1 = 0
        over_delay_num_sfc2 = 0

        for delay in pkt_delay_sfc1:
            if delay > self.s1_aim_delay:
                over_delay_num_sfc1 += 1
                
        for delay in pkt_delay_sfc2:
            if delay > self.s2_aim_delay:
                over_delay_num_sfc2 += 1

        print(f"s1_over_delay_rate: {over_delay_num_sfc1/len(pkt_delay_sfc1)}")
        print(f"s2_over_delay_rate: {over_delay_num_sfc2/len(pkt_delay_sfc2)}")


        # endregion

        # region 输出服务功能链的收支比

        # print("sfc_1_revenue_list:",sfc_1_revenue_list)
        # print("sfc_1_cost_list:",sfc_1_cost_list)

        print("s1_rev_cost_rate:",sum(self.s1_revenue_list)/sum(self.s1_cost_list))
        print("s2_rev_cost_rate:",sum(self.s2_revenue_list)/sum(self.s2_cost_list))

        # endregion