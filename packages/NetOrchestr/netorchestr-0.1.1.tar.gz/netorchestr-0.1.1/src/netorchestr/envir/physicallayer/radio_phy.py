
import random
from astropy import units as u
from netorchestr.envir.base import OModule, OGate, OMessage

class RadioPhy(OModule):
    def __init__(self, name, range:u.Quantity, transmission_delay_range:list[u.Quantity] = []):
        super().__init__(name)
        
        self.range = range
        """最大通信距离"""
        
        self.transmission_delay_range = transmission_delay_range
        """传输延迟取值范围, 通常意为调制解调、编解码等信号处理延迟"""

    def recv_msg(self, msg:OMessage, in_gate:OGate):
        if in_gate.name == "upperLayerIn":
            for out_gate in self.gates:
                if out_gate.name == "lowerLayerOut":
                    
                    if self.transmission_delay_range != []:
                        random_delay_ms = random.uniform(self.transmission_delay_range[0].to(u.ms).value,
                                                         self.transmission_delay_range[1].to(u.ms).value)
                        self.gates[out_gate][0].delay = random_delay_ms * u.ms
                    self.send_msg(msg, out_gate)
        elif in_gate.name == "lowerLayerIn":
            for out_gate in self.gates:
                if out_gate.name == "upperLayerOut":
                    self.send_msg(msg, out_gate)

class RadioPhyWithBandLimit(RadioPhy):
    def __init__(self, name, range:u.Quantity, bandwidth_max:u.Quantity = 100*u.kbit/u.s,
                 bandwidth_window: u.Quantity = 0.1*u.s, transmission_delay_range:list[u.Quantity] = []):
        super().__init__(name, range)
        
        self.bandwidth_max = bandwidth_max
        """最大可使用通信带宽"""
        
        self.bandwidth_window = bandwidth_window
        """计算带宽使用的时间窗口大小"""
        
        self.message_history: list[tuple[u.Quantity, u.Quantity]] = []
        """消息历史记录，存储(时间戳, 消息大小)元组"""
        
        self.last_calculated_bandwidth: u.Quantity = 0*u.kbit/u.s
        """最后计算的平均带宽"""
        
        self.transmission_delay_range = transmission_delay_range
        """传输延迟取值范围, 通常意为调制解调、编解码等信号处理延迟"""

    def _calculate_message_size(self, msg: OMessage) -> u.Quantity:
        """估算消息大小, 以kbit为单位
        
        这里使用消息内容的字符串长度作为近似值，
        实际应用中可能需要根据具体消息结构调整
        """
        # 假设每个字符占用1字节，1字节=8比特
        if hasattr(msg, 'content'):
            byte_size = len(str(msg.content))
        else:
            byte_size = 64  # 默认大小
        
        return (byte_size * 8 * u.bit).to(u.kbit)

    def _cleanup_old_messages(self, current_time: u.Quantity) -> None:
        """清理时间窗口外的旧消息记录"""
        # 计算时间窗口的起始时间
        window_start = current_time - self.bandwidth_window
        
        # 过滤掉窗口外的消息
        self.message_history = [
            (timestamp, size) 
            for timestamp, size in self.message_history 
            if timestamp >= window_start
        ]

    def _calculate_average_bandwidth(self) -> u.Quantity:
        """在时间窗口内计算平均带宽"""
        if not self.message_history:
            return 0*u.kbit/u.s
            
        # 计算总数据量
        total_size = sum(size for _, size in self.message_history)
        
        # 计算时间窗口内的总时间
        first_time = self.message_history[0][0]
        last_time = self.message_history[-1][0]
        time_diff = last_time - first_time
        
        # 确保时间差不为零
        if time_diff <= 0*u.s:
            return 0*u.kbit/u.s
            
        # 计算平均带宽
        average_bandwidth = total_size / time_diff
        
        # 转换为合适的单位
        return average_bandwidth.to(u.kbit/u.s)

    def get_current_bandwidth(self) -> u.Quantity:
        """获取当前时间窗口内的平均带宽"""
        self._cleanup_old_messages(self.scheduler.now * u.ms)
        self.last_calculated_bandwidth = self._calculate_average_bandwidth()
        return self.last_calculated_bandwidth

    def get_remain_bandwidth(self) -> u.Quantity:
        """查询剩余带宽"""
        bandwidth_remain = self.bandwidth_max - self.last_calculated_bandwidth
        return max(bandwidth_remain, 0*u.kbit/u.s)

    def get_transmission_delay(self) -> float:
        """获取传输延迟上限"""
        if self.transmission_delay_range != []:
            return self.transmission_delay_range[1].to(u.ms).value
        else:
            return 0.0

    def recv_msg(self, msg:OMessage, in_gate:OGate):
        if in_gate.name == "upperLayerIn":
            for out_gate in self.gates:
                if out_gate.name == "lowerLayerOut":
                    
                    # begin 计算并更新已使用带宽 -------------------------------------------
                    self.message_history.append((self.scheduler.now * u.ms, self._calculate_message_size(msg)))
                    current_bandwidth = self.get_current_bandwidth()
                    if current_bandwidth > self.bandwidth_max:
                        self.logger.warning(
                            f"{self.scheduler.now}: {self.name}'s bandwidth used {current_bandwidth} "
                            f"exceeds max {self.bandwidth_max}"
                        )
                    # end 已计算并更新已使用带宽 ------------------------------------------
                    
                    self.send_msg(msg, out_gate)
        elif in_gate.name == "lowerLayerIn":
            for out_gate in self.gates:
                if out_gate.name == "upperLayerOut":
                    self.send_msg(msg, out_gate)

class RadioPhySimpleSDR(RadioPhyWithBandLimit):
    def __init__(self, name:str, mode_perf_map:dict[str,dict[str,u.Quantity]], **kwargs):
        """初始化建议软件定义无线电 SDR 的模块实例。

        该类用于创建 SDR (软件定义无线电) 模块实现，通过模式性能映射表
        定义不同通信模式下的性能参数（如通信距离、传输延迟范围等）。

        Args:
            name: 模块的名称标识符，用于唯一标识该 SDR 模块实例。
            mode_perf_map: 字典结构，键为通信模式名称 (如 "Sat_Ue"、"Sat_Ground"),
                值为该模式对应的性能参数字典。性能参数字典的键为参数名称 (如 "range"、
                "transmission_delay_range")，值为带单位的物理量 (`u.Quantity` 类型)。

        Example:
            初始化示例：
            >>> mode_perf = {
            ...     "Sat_Ue": {
            ...         "range": 3000 * u.km,
            ...         "transmission_delay_range": [20 * u.ms, 30 * u.ms]
            ...     },
            ...     "Sat_Ground": {
            ...         "range": 5000 * u.km,
            ...         "transmission_delay_range": [10 * u.ms, 25 * u.ms]
            ...     }
            ... }
            >>> sdr = DuAAuSimpleSDR(name="DuAAu_SDR_01", mode_perf_map=mode_perf)
        """
        super().__init__(name = name, range = mode_perf_map, **kwargs)
        
        self.mode_perf_map = mode_perf_map
        
    

