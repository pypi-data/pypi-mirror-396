
import numpy as np
from astropy import units as u
from netorchestr.envir.base import OModule, OGate
from netorchestr.envir.mobility.base import MobilityBase
from netorchestr.envir.physicallayer import RadioPhy, RadioPhySimpleSDR

class RadioMedium(OModule):
    def __init__(self, name:str):
        super().__init__(name)
        
    def recv_msg(self, msg, gate:"OGate"):
        from_module_radio:RadioPhy = self.gates[gate][1].ofModule
        for to_gate in [temp_gate for temp_gate in self.gates if temp_gate.name == "upperLayerOut"]:
            to_module_radio:RadioPhy = self.gates[to_gate][1].ofModule
            if from_module_radio == to_module_radio:
                continue
            
            if isinstance(from_module_radio, RadioPhySimpleSDR) and isinstance(to_module_radio, RadioPhySimpleSDR):
                # 使用 RadioPhySimpleSDR 模型获取通信范围
                flag, distance, latency = self.is_in_communication_range_with_RadioPhySimpleSDR(from_module_radio, to_module_radio)
            else:
                # 使用 RadioPhy 模型获取通信范围
                flag, distance, latency = self.is_in_communication_range_with_RadioPhy(from_module_radio, to_module_radio)
                
            if flag:
                self.gates[to_gate][0].delay = latency
                self.send_msg(msg, to_gate)
    
    def has_common_sdr_mode(self, from_module_radio:"RadioPhySimpleSDR", to_module_radio:"RadioPhySimpleSDR"):
        """判断两个 SDR 模块的通信模式是否有交集, 并更新该模式下的通信范围

        Args:
            from_module_radio (RadioPhySimpleSDR): SDR 模块1
            to_module_radio (RadioPhySimpleSDR): SDR 模块2
            
        Returns:
            bool: 是否存在相同的通信模式
        """
        from_module_radio_sdr_modes = from_module_radio.mode_perf_map
        to_module_radio_sdr_modes = to_module_radio.mode_perf_map
        
        for mode1, perf1 in from_module_radio_sdr_modes.items():
            
            # 拆分模式1为两个实体（如"Ue_Ground"拆分为["Ue", "Ground"]）
            entities = mode1.split("_")
            
            if len(entities) != 2:
                continue  # 跳过格式不正确的模式（非"A_B"结构）
            
            # 生成逆模式（如"Ground_Ue"）
            mode2 = f"{entities[1]}_{entities[0]}"
            
            # 检查逆模式是否存在于第二个模块中
            if mode2 in to_module_radio_sdr_modes:
                # 找到了两个模块的通信模式的交集，更新当前的最大通信范围
                from_module_radio.range = perf1["range"]
                from_module_radio.transmission_delay_range = perf1["transmission_delay_range"]
                
                to_module_radio.range = to_module_radio_sdr_modes[mode2]["range"]
                to_module_radio.transmission_delay_range = to_module_radio_sdr_modes[mode2]["transmission_delay_range"]
                
                self.logger.debug(f"{self.scheduler.now}: Module {from_module_radio.name} get common sdr mode with {to_module_radio.name}: {mode1} and {mode2}")
                return True
        
        self.logger.debug(f"{self.scheduler.now}: Module {from_module_radio.name} has no common sdr mode with {to_module_radio.name}")
        return False
        
    def is_in_communication_range_with_RadioPhySimpleSDR(self, from_module:"RadioPhySimpleSDR", to_module:"RadioPhySimpleSDR"):
        """判断两个 SDR 模块是否在相互的通信范围内

        Args:
            from_module (RadioPhySimpleSDR): SDR 模块 1
            
            to_module (RadioPhySimpleSDR): SDR 模块 2

        Returns:
            bool: 是否在通信范围内
            
            u.quantity: 对应的距离
            
            u.quantity: 对应的延迟
        """
        
        # 判断两个 SDR 模块的通信模式是否有交集
        mode_flag = self.has_common_sdr_mode(from_module, to_module)
        if mode_flag:
            return self.is_in_communication_range_with_RadioPhy(from_module, to_module)
        else:
            return False, np.inf * u.km, np.inf * u.ms
        
    def is_in_communication_range_with_RadioPhy(self, from_module:"RadioPhy", to_module:"RadioPhy"):
        # 筛选运动模型
        from_module_top = from_module.find_top_module()
        to_module_top = to_module.find_top_module()
        
        if not hasattr(from_module_top, "mobiusTraj") or not hasattr(to_module_top, "mobiusTraj"):
            raise ValueError("The node as top module must have mobility model with attribute 'mobiusTraj' ")
        
        from_node_mobilily:MobilityBase = from_module_top.mobiusTraj
        from_node_gps, catch_flag = from_node_mobilily.update_current_gps(self.scheduler.now * u.ms)
        if not catch_flag: 
            self.logger.debug(f"{self.scheduler.now}: Module {self.name} need {from_module_top.name} update current gps: {from_node_gps}")
        
        to_node_mobilily:MobilityBase = to_module_top.mobiusTraj
        to_node_gps, catch_flag = to_node_mobilily.update_current_gps(self.scheduler.now * u.ms)
        if not catch_flag: 
            self.logger.debug(f"{self.scheduler.now}: Module {self.name} need {to_module_top.name} update current gps: {to_node_gps}")
        
        # 计算距离
        distance = MobilityBase.calculate_distance(from_node_gps, to_node_gps)

        # 判断是否在通信范围内
        if distance < from_module.range and distance < to_module.range:
            # 计算传播延迟
            c = 299792458 * u.m / u.s
            delay = distance / c
            # 加入传输延迟（平均分布）
            delay += np.random.uniform(from_module.transmission_delay_range[0].to(u.ms).value, 
                                       from_module.transmission_delay_range[1].to(u.ms).value) * u.ms
            
            return True, distance, delay
        else:
            return False, np.inf * u.km, np.inf * u.ms