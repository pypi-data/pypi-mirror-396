
import numpy as np
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation, CartesianRepresentation, ITRS, GCRS, Angle
from poliastro.bodies import Earth
from poliastro.twobody import Orbit

from netorchestr.envir.mobility import MobilityDynamic

class MobilitySat(MobilityDynamic):
    def __init__(self, name:str, init_time:Time, a:float, e:float, 
                 inc:float, raan:float, argp:float, init_nu:float, markcolor:str = 'green'):
        """卫星轨道运动模型
        
        Args:
            name (str): 模型名称
            init_time (astropy.time.Time): 初始时间
            a (float): 轨道半长轴,单位km
            e (float): 轨道偏心率,单位度
            inc (float): 轨道倾角,单位度
            raan (float): 轨道升交点经度,单位度
            argp (float): 轨道近地点幅角,单位度
            init_nu (float): 卫星初始真近点角,单位度
            update_by_clock (bool): 是否使用时钟更新位置信息
            markcolor (str, optional): 标记颜色. Defaults to 'green'.
        
        """
        super().__init__(name, init_time, init_gps=[0,0,0], markcolor=markcolor)
        
        self.a = a
        """轨道半长轴,单位km"""
        
        self.e = e
        """轨道偏心率,单位度"""
        
        self.inc = inc
        """轨道倾角,单位度"""
        
        self.raan = raan
        """轨道升交点经度,单位度"""
        
        self.argp = argp
        """轨道近地点幅角,单位度"""
        
        self.init_nu = init_nu
        """卫星初始真近点角,单位度"""

        self.orb = Orbit.from_classical(attractor=Earth, a=self.a*u.km, ecc=self.e*u.one,
                                        inc=self._deg_to_rad(self.inc)*u.rad, 
                                        raan=self._deg_to_rad(self.raan)*u.rad, 
                                        argp=self._deg_to_rad(self.argp)*u.rad,
                                        nu=self._deg_to_rad(self.init_nu)*u.rad)
        
        self.init_gps, _ = self.update_current_gps(0 * u.ms)
        
    
    def _deg_to_rad(self,angle_deg):
        """将角度转换为弧度制"""
        angle_rad = Angle(angle_deg, unit=u.deg).to(u.rad).to_value()
        # 确保角度在 -π 到 π 范围内
        return (angle_rad + np.pi) % (2 * np.pi) - np.pi
    
    
    def update_current_gps(self,time:u.quantity):
        """更新卫星的当前定位信息
        
        Args:
            time (astropy.units.Quantity): 仿真开始后经历的时长
        
        Returns:
            List[float]: 卫星当前位置 [经度, 纬度, 高度km]
            bool: 是否是从缓存中获取的坐标
        """
        self.current_time = self.init_time + np.around(time.to(u.ms))
        # 检查缓存中是否有当前时间的坐标
        if self.current_time in self.cache_gps:
            self.current_gps = self.cache_gps[self.current_time]
            return self.current_gps, True

        propagated_orb = self.orb.propagate(self.current_time)

        # 获取卫星的位置向量
        r, _ = propagated_orb.rv()  # r: 位置向量, v: 速度向量

        # 将位置向量转换为地固坐标系 (ITRS)
        gcrs_position = GCRS(CartesianRepresentation(r),obstime=self.current_time)
        itrs_position = gcrs_position.transform_to(ITRS(obstime=self.current_time))

        # 将地固坐标系的位置转换为地理坐标
        location = EarthLocation(*itrs_position.cartesian.xyz)
        subpoint_lon, subpoint_lat, subpoint_alt = location.to_geodetic()

        self.current_gps = [subpoint_lon.value, subpoint_lat.value, subpoint_alt.value]
        
        # 缓存当前时间坐标
        self.cache_gps[self.current_time] = self.current_gps
            
        return self.current_gps, False

class MobilityConstellation():
    def __init__(self, name:str, init_time:Time, markcolor:str='green'):
        """星座运动模型定义
        Args:
            name (str): 模型名称
            init_time (astropy.time.Time): 初始时间
            markcolor (str, optional): 标记颜色. Defaults to 'green'.
        
        Note:
            星座运动模型是由多个卫星运动模型组成的集合
        """
        self.name = name
        
        self.init_time = init_time
        
        self.mobilitySats: dict[str, MobilitySat] = {}  
        """卫星运动模型字典，键为卫星名称，值为卫星运动模型对象"""
        
        self.markcolor = markcolor
        """标记颜色"""
        
        self.formation: dict[str, dict] = {}
        """星座构型信息"""
    
    def add_satellite(self, satellite: MobilitySat) -> None:
        """添加卫星运动模型到星座
        
        Args:
            satellite (MobilitySat): 要添加的卫星运动模型对象
        """
        if satellite.name in self.mobilitySats:
            raise ValueError(f"卫星 '{satellite.name}' 已存在于星座中")
        self.mobilitySats[satellite.name] = satellite
    
    def remove_satellite(self, satellite_name: str) -> None:
        """从星座中移除卫星运动模型
        
        Args:
            satellite_name (str): 要移除的卫星运动模型名称
        """
        if satellite_name not in self.mobilitySats:
            raise ValueError(f"卫星 '{satellite_name}' 不存在于星座中")
        del self.mobilitySats[satellite_name]

    def get_satellite(self, satellite_name: str) -> MobilitySat:
        """获取星座中的卫星对象
        
        Args:
            satellite_name (str): 卫星名称
            
        Returns:
            Satellite: 对应的卫星对象
        """
        return self.mobilitySats.get(satellite_name)
        
    def get_satellite_positions(self) -> dict[str, list[float]]:
        """获取所有卫星的当前位置
        
        Returns:
            Dict[str, List[float]]: 卫星位置字典，键为卫星名称，值为 [经度, 纬度, 高度]
        """
        return {name: sat.current_gps for name, sat in self.mobilitySats.items()}

    def get_satellite_count(self) -> int:
        """获取星座中的卫星数量
        
        Returns:
            int: 卫星数量
        """
        return len(self.mobilitySats)

    def __set_formation(self, formation_type: str, parameters: dict) -> None:
        """设置星座构型
        
        Args:
            formation_type (str): 构型类型, 如Walker、Walker-Delta等
            parameters (Dict): 构型参数
        """
        self.formation = {
            "type": formation_type,
            "parameters": parameters
        }
    
    def generate_walker_formation(self, T: int, P: int, F: float, a: float, e: float,
                                  inc: float, init_time: Time) -> None:
        """创建 Walker 星座构型
        
        Args:
            T (int): 总卫星数量
            P (int): 轨道面数量
            F (float): 相位因子, 范围 [0, 1)
            a (float): 半长轴, 单位km
            e (float): 偏心率
            inc (float): 倾角, 单位度
            init_time (astropy.time.Time): 初始时间
        """
        
        # 每个轨道面上的卫星数量
        S = T // P
        if T % P != 0:
            raise ValueError("Total mobilitySats (T) must be divisible by the number of orbital planes (P).")
        
        # 保存构型信息
        self.__set_formation("Walker", {
            "T": T,
            "P": P,
            "F": F,
            "a": a,
            "e": e,
            "inc": inc,
            "init_time": init_time.isot # 普通的年月日时分秒格式
        })

        for orbit_plane_num in range(P):
            raan = 360 / P * orbit_plane_num  # 升交点赤经（RAAN）
            for sat_num in range(S):
                # 计算真近点角（考虑相位因子）
                true_anomaly = 360 / S * sat_num + F * 360 / P * orbit_plane_num
                true_anomaly %= 360  # 确保角度在 [0, 360) 范围内

                # 创建卫星对象
                constellation_name = self.name.split("_")[0]
                mobilitySat_name = f"{constellation_name}P{orbit_plane_num}S{sat_num}_Mobility"
                mobilitySat = MobilitySat(
                    name=mobilitySat_name,
                    init_time=init_time,
                    a=a,
                    e=e,
                    inc=inc,
                    raan=raan,
                    argp=0,  # 近地点幅角设为 0
                    init_nu=true_anomaly,
                    markcolor=self.markcolor
                )
                
                self.add_satellite(mobilitySat)






