from astropy import units as u
from netorchestr.envir.base.omodule import OModule
from netorchestr.envir.base.omessage import OMessage

class ClockTime(OModule):
    def __init__(self, name:str):
        super().__init__(name)
        
        self.tick_stop = False
        """是否停止定时器"""
        
        self.tick_interval = 1 * u.ms
        """定时器间隔"""
        
        self.tick_process = None
        """存储定时器进程的引用"""
        
        self.tick_restart_event = None
        """存储重启事件的引用"""

    def initialize(self):
        self.tick_process = self.scheduler.process(self.__clock_tick())
        
    def __clock_tick(self):
        while True:
            if self.tick_stop:
                # 使用simpy的Condition对象等待重启信号
                self.tick_restart_event = self.scheduler.event()
                yield self.tick_restart_event
                self.tick_stop = False
                self.tick_restart_event = None
            else:
                yield self.scheduler.timeout(self.tick_interval.to(u.ms).value)
                for gate in self.gates:
                    link, aim_gate = self.gates[gate]
                    aim_module = aim_gate.ofModule
                    time_finish_msg = OMessage(timestamp=self.scheduler.now, 
                                               sender=self.name, 
                                               receiver=aim_module.name, 
                                               content="", 
                                               id="tic", 
                                               ttl="")
                    self.send_msg(time_finish_msg, gate)

    def set_tick_interval(self, tick_interval: u.Quantity):
        self.tick_interval = tick_interval

    def stop(self):
        """停止定时器"""
        self.tick_stop = True

    def start(self):
        """启动定时器"""
        # 如果进程已停止，重新启动它
        self.tick_stop = False
        if hasattr(self, 'process') and self.process:
            # 唤醒可能正在等待的进程
            if self.process.is_alive:
                # 触发重启事件
                if self.tick_restart_event and not self.tick_restart_event.triggered:
                    self.tick_restart_event.succeed()
        else:
            # 如果进程未初始化或已结束，重新启动
            self.process = self.scheduler.process(self.__clock_tick())


