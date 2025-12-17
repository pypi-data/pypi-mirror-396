
import numpy as np
from astropy import units as u
from astropy.time import Time

from netorchestr.envir.mobility import MobilityDynamic

class MobilityPedestrian(MobilityDynamic):
    """地面行人运动模型，模拟行人在平面上的随机行走"""
    def __init__(self, name: str, init_time: Time, init_gps: list[float],
                 boundary_checker,  # 边界检查器函数，接收(当前经纬度,自身模型)返回(调整后经纬度, 是否反弹)
                 max_speed: u.Quantity = 1.5 * u.m / u.s,  # 行人最大速度
                 min_speed: u.Quantity = 0.5 * u.m / u.s,  # 行人最小速度
                 markcolor: str = 'blue',  # 运动轨迹颜色
                 ):
        """初始化地面行人模型

        Args:
            name (str): 模型名称
            init_time (Time): 初始化时间
            init_gps (list[float]): 初始GPS坐标
            boundary_checker (_type_): 边界检查器函数
            max_speed (u.Quantity, optional): 行人最大速度. Defaults to 1.5 * u.m / u.s.
            min_speed (u.Quantity, optional): 行人最小速度. Defaults to 0.5 * u.m / u.s.
            markcolor (str, optional): 运动轨迹颜色. Defaults to 'blue'.
        """
        
        super().__init__(name, init_time, init_gps, markcolor)
        
        # 初始化运动状态
        self.direction = np.random.uniform(0, 2 * np.pi)    # 运动方向（弧度）
        self.max_speed = max_speed * u.m / u.s              # 最大速度（米/秒）
        self.min_speed = min_speed * u.m / u.s              # 最小速度（米/秒）
        self.speed = np.random.uniform(min_speed.value, 
                                       max_speed.value) * u.m / u.s  # 当前速度（米/秒）
        self.last_update_time = init_time                   # 上次更新时间
        # 边界检查器
        self.boundary_checker = boundary_checker
        
    def _update_motion_state(self):
        """更新行人的运动状态（方向和速度）"""
        # 随机调整方向（-10°至10°）
        self.direction += np.random.uniform(-np.pi/18, np.pi/18)
        self.direction %= 2 * np.pi  # 确保方向在0-2π范围内
        
        # 随机调整速度
        self.speed = np.random.uniform(self.min_speed.value, 
                                       self.max_speed.value) * u.m / u.s

    
    def update_current_gps(self, time:u.quantity):
        """更新行人当前GPS位置
        
        重写更新坐标的方法，实现行人运动逻辑
        
        Args:
            time (astropy.units.Quantity): 仿真开始后经历的时长
        
        Returns:
            list[float]: 经度、纬度、高度km
            bool: 是否是从缓存中获取的坐标
        """

        self.current_time = self.init_time + np.around(time.to(u.ms))
        
        # 检查缓存
        if self.current_time in self.cache_gps:
            self.current_gps = self.cache_gps[self.current_time]
            return self.current_gps, True
        
        # 计算时间差（秒）
        time_diff = (self.current_time - self.last_update_time).to(u.s)
        
        # 更新运动状态
        self._update_motion_state()
        
        # 计算移动距离（米）
        distance = (self.speed * time_diff).to(u.m).value
        
        # 计算经纬度变化
        earth_radius = 6378137.0  # 地球赤道半径（米）
        lon_rad = np.radians(self.current_gps[0])
        lat_rad = np.radians(self.current_gps[1])
        
        # 计算坐标增量（弧度）
        delta_lon = distance * np.cos(self.direction) / (earth_radius * np.cos(lat_rad))
        delta_lat = distance * np.sin(self.direction) / earth_radius
        
        # 计算新坐标
        new_lon = np.degrees(lon_rad + delta_lon)
        new_lat = np.degrees(lat_rad + delta_lat)
        
        # 应用边界检查与调整
        new_lon, new_lat, bounced = self.boundary_checker((new_lon, new_lat), self)
        
        # 反弹后微调位置
        if bounced:
            adj_lon_rad = np.radians(new_lon)
            adj_lat_rad = np.radians(new_lat)
            delta_lon_adj = 0.05 * distance * np.cos(self.direction) / (earth_radius * np.cos(adj_lat_rad))
            delta_lat_adj = 0.05 * distance * np.sin(self.direction) / earth_radius
            new_lon = np.degrees(adj_lon_rad + delta_lon_adj)
            new_lat = np.degrees(adj_lat_rad + delta_lat_adj)
        
        # 更新位置信息
        self.current_gps = [new_lon, new_lat, self.current_gps[2]]
        self.cache_gps[self.current_time] = self.current_gps
        
        self.last_update_time = self.current_time
        
        return self.current_gps, False
        
class MobilityCrowd():
    """人群运动模型，支持圆形和矩形区域构型"""
    
    def __init__(self, name: str, init_time: Time, markcolor: str = 'blue'):
        """
        初始化人群模型
        
        Args:
            name (str): 模型名称
            init_time (astropy.time.Time): 初始时间
            markcolor (str): 标记颜色, default: 'blue'
        """
        self.name = name

        self.init_time = init_time
        self.mobilityPeds: dict[str, MobilityPedestrian] = {}
        """行人集合"""
        
        self.markcolor = markcolor
        """标记颜色"""
        
        self.formation: dict = {}
        """人群构型信息"""
        
    def _create_circular_boundary_checker(self, center: list[float], radius: u.Quantity) -> callable:
        """创建圆形区域边界检查器"""
        center_lon, center_lat = center[0], center[1]
        earth_radius = 6378137.0
        
        def checker(coords: tuple[float, float], pedestrian: "MobilityPedestrian") -> tuple[float, float, bool]:
            lon, lat = coords
            # 计算与中心点的距离（米）
            dlon = np.radians(lon - center_lon)
            dlat = np.radians(lat - center_lat)
            a = np.sin(dlat/2)**2 + np.cos(np.radians(center_lat)) * np.cos(np.radians(lat)) * np.sin(dlon/2)** 2
            distance = 2 * earth_radius * np.arcsin(np.sqrt(a))
            
            if distance <= radius.to(u.m).value:
                return lon, lat, False
            
            # 超出边界时调整位置并计算反弹方向
            ratio = radius.to(u.m).value / distance
            new_lon = center_lon + (lon - center_lon) * ratio
            new_lat = center_lat + (lat - center_lat) * ratio
            
            # 计算反弹方向（反射定律）
            dx = lon - center_lon
            dy = lat - center_lat
            angle = np.arctan2(dy, dx)
            pedestrian.direction = 2 * angle - pedestrian.direction
            return new_lon, new_lat, True
        
        return checker
    
    def _create_rectangular_boundary_checker(self, center: list[float], width: u.Quantity, 
                                            height: u.Quantity, rotation: float = 0) -> callable:
        """创建矩形区域边界检查器"""
        center_lon, center_lat = center[0], center[1]
        rot_rad = np.radians(rotation)
        half_w = width.to(u.m).value / 2
        half_h = height.to(u.m).value / 2
        earth_radius = 6378137.0
        
        def checker(coords: tuple[float, float], pedestrian: "MobilityPedestrian") -> tuple[float, float, bool]:
            lon, lat = coords
            # 转换为相对于中心的米坐标
            dlon = np.radians(lon - center_lon)
            dlat = np.radians(lat - center_lat)
            x = earth_radius * dlon * np.cos(np.radians(center_lat))
            y = earth_radius * dlat
            
            # 逆旋转坐标
            x_rot = x * np.cos(rot_rad) + y * np.sin(rot_rad)
            y_rot = -x * np.sin(rot_rad) + y * np.cos(rot_rad)
            
            # 检查是否在矩形内
            if -half_w <= x_rot <= half_w and -half_h <= y_rot <= half_h:
                return lon, lat, False
            
            # 计算边界调整后坐标
            x_clamped = np.clip(x_rot, -half_w, half_w)
            y_clamped = np.clip(y_rot, -half_h, half_h)
            
            # 正向旋转回原坐标系
            x_new = x_clamped * np.cos(rot_rad) - y_clamped * np.sin(rot_rad)
            y_new = x_clamped * np.sin(rot_rad) + y_clamped * np.cos(rot_rad)
            
            # 转换回经纬度
            new_lon = center_lon + np.degrees(x_new / (earth_radius * np.cos(np.radians(center_lat))))
            new_lat = center_lat + np.degrees(y_new / earth_radius)
            
            # 计算反弹方向
            dx = x_rot - x_clamped
            dy = y_rot - y_clamped
            if abs(dx) > abs(dy):  # 左右边界反弹
                pedestrian.direction = np.pi - pedestrian.direction
            else:  # 上下边界反弹
                pedestrian.direction = -pedestrian.direction
            return new_lon, new_lat, True
        
        return checker
    
    def _generate_circular_position(self, center: list[float], radius: u.Quantity) -> list[float]:
        """在圆形区域内生成随机位置"""
        lon, lat = center[0], center[1]
        r = (radius * np.sqrt(np.random.uniform(0, 1))).to(u.m).value
        theta = np.random.uniform(0, 2 * np.pi)
        
        # 转换为经纬度
        earth_radius = 6378137.0
        dlon = r * np.cos(theta) / (earth_radius * np.cos(np.radians(lat)))
        dlat = r * np.sin(theta) / earth_radius
        return [np.degrees(np.radians(lon) + dlon), 
                np.degrees(np.radians(lat) + dlat), 0.0]
    
    def _generate_rectangular_position(self, center: list[float], width: u.Quantity, 
                                      height: u.Quantity, rotation: float = 0) -> list[float]:
        """在矩形区域内生成随机位置"""
        lon, lat = center[0], center[1]
        rot_rad = np.radians(rotation)
        x = np.random.uniform(-width.to(u.m).value/2, width.to(u.m).value/2)
        y = np.random.uniform(-height.to(u.m).value/2, height.to(u.m).value/2)
        
        # 旋转坐标
        x_rot = x * np.cos(rot_rad) - y * np.sin(rot_rad)
        y_rot = x * np.sin(rot_rad) + y * np.cos(rot_rad)
        
        # 转换为经纬度
        earth_radius = 6378137.0
        dlon = x_rot / (earth_radius * np.cos(np.radians(lat)))
        dlat = y_rot / earth_radius
        return [np.degrees(np.radians(lon) + dlon), 
                np.degrees(np.radians(lat) + dlat), 0.0]
    
    def add_pedestrian(self, pedestrian: "MobilityPedestrian") -> None:
        """添加行人到人群"""
        if pedestrian.name in self.mobilityPeds:
            raise ValueError(f"行人 {pedestrian.name} 已存在")
        self.mobilityPeds[pedestrian.name] = pedestrian
    
    def remove_pedestrian(self, name: str) -> None:
        """从人群移除行人"""
        if name in self.mobilityPeds:
            del self.mobilityPeds[name]
    
    def get_pedestrian_positions(self) -> dict[str, list[float]]:
        """获取所有行人位置"""
        return {name: ped.current_gps for name, ped in self.mobilityPeds.items()}
    
    def generate_circular_crowd(self, count: int, center: list[float], radius: float, 
                               max_speed: float = 1.5*u.m/u.s, 
                               min_speed: float = 0.5*u.m/u.s) -> None:
        """生成圆形区域人群"""
        self.formation = {
            "type": "circular",
            "params": {"center": center, "radius": radius, "count": count}
        }
        
        checker = self._create_circular_boundary_checker(center, radius)
        for i in range(count):
            pos = self._generate_circular_position(center, radius)
            ped = MobilityPedestrian(
                name=f"{self.name}Ped{i}",
                init_time=self.init_time,
                boundary_checker=checker,
                init_gps=pos,
                max_speed=max_speed,
                min_speed=min_speed,
                markcolor=self.markcolor
            )
            self.add_pedestrian(ped)
    
    def generate_rectangular_crowd(self, count: int, center: list[float], width: float, 
                                  height: float, rotation: float = 0, 
                                  max_speed: float = 1.5*u.m/u.s, 
                                  min_speed: float = 0.5*u.m/u.s) -> None:
        """生成矩形区域人群"""
        self.formation = {
            "type": "rectangular",
            "params": {
                "center": center, "width": width, "height": height,
                "rotation": rotation, "count": count
            }
        }
        
        crowd_name = self.name.split("_")[0]
        checker = self._create_rectangular_boundary_checker(center, width, height, rotation)
        for i in range(count):
            pos = self._generate_rectangular_position(center, width, height, rotation)
            ped = MobilityPedestrian(
                name=f"{crowd_name}P{i}_Mobility",
                init_time=self.init_time,
                boundary_checker=checker,
                init_gps=pos,
                max_speed=max_speed,
                min_speed=min_speed
            )
            self.add_pedestrian(ped)
