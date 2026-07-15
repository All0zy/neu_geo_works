import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import datetime

plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman']  # 设置为黑体等支持中文的字体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示异常

# 1. 读取风场数据
u_file = nc.Dataset('uwnd.sfc.2022.nc')
v_file = nc.Dataset('vwnd.sfc.2022.nc')

# 提取核心变量（经纬度、时间、u/v风分量）
lon = u_file.variables['lon'][:]
lat = u_file.variables['lat'][:]
time = u_file.variables['time'][:]
uwnd = u_file.variables['uwnd'][:]  # 维度：(time, lat, lon)
vwnd = v_file.variables['vwnd'][:]

# 2. 筛选2022-01-01 08:00的数据（时间单位参考文档1.1.2节）
base_time = datetime.datetime(1800, 1, 1)  # 数据默认基准时间
target_time = datetime.datetime(2022, 1, 1, 8, 0, 0)
# 计算目标时间对应的天数（含8小时小数部分）
target_days = (target_time - base_time).days + 8 / 24  
# 找到最接近的时间索引
target_idx = np.argmin(np.abs(time - target_days))

# 提取目标时刻的全量风场数据（无抽稀）
u_full = uwnd[target_idx, :, :]  # 全量u分量
v_full = vwnd[target_idx, :, :]  # 全量v分量
wind_speed_full = np.sqrt(u_full**2 + v_full**2)  # 全量风速

# 3. 绘制全球风场
# 地图投影设置（参考文档实验3的Miller投影）
m = Basemap(llcrnrlon=0, llcrnrlat=-80, urcrnrlon=360, urcrnrlat=80,
            projection='mill', resolution='l')


# 网格化经纬度（匹配全量数据维度）
lons, lats = np.meshgrid(lon, lat)
x_full, y_full = m(lons, lats)  # 全量投影坐标

# 3.1 绘制风速填色图（全量数据）
cs = m.pcolor(x_full, y_full, wind_speed_full, cmap='jet', vmin=0, vmax=25)
cbar = m.colorbar(cs, location='bottom', pad="10%", label='风速 (m/s)')

# 3.2 全量绘制风向箭头（无抽稀，直接用原始数据）
# 调整箭头参数：缩小宽度、降低比例避免重叠
m.quiver(x_full, y_full, u_full, v_full, 
         scale=1000,  # 箭头比例（值越大箭头越短）
         width=0.001,  # 箭头宽度（值越小越细）
         headlength=8,  # 箭头头部长度
         headwidth=5)   # 箭头头部宽度

# 4. 添加地图基础要素（参考文档实验1-4的制图规范）
m.drawcoastlines(linewidth=0.5)  # 海岸线
m.fillcontinents(color='0.75', lake_color='white')  # 陆地填充
# 绘制经纬网格
m.drawmeridians(np.arange(0, 361, 60), labels=[0,0,0,1], fontsize=10)
m.drawparallels(np.arange(-90, 91, 30), labels=[1,0,0,0], fontsize=10)

# 标题与保存
plt.title('全球风场（风速和风向）分布(2022-01-01 08:00 UTC)', fontsize=12)
plt.savefig('global_wind_full_data.png', dpi=300, bbox_inches='tight')
plt.show()

# 关闭文件
u_file.close()
v_file.close()