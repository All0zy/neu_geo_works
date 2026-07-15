import netCDF4 as nc 
import numpy as np
import datetime
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

# 1. 读取数据
file = nc.Dataset('sst.mnmean.nc') 
lon = file.variables['lon'][:] #经度 
lat = file.variables['lat'][:] #纬度 
sst = file.variables['sst'][:] #海表温度 
time = file.variables['time'][:] #时间

# 2. 时间范围筛选（1982-2022年）
time1 = (datetime.date(1982,1,1) - datetime.date(1800,1,1)).days  
time2 = (datetime.date(2022,12,31) - datetime.date(1800,1,1)).days  
trange = np.where((time >= time1)&(time <= time2),1,0) 
time_period = time[trange==1]

# 3. 逐网格计算SST变化趋势
trendsst = np.zeros((len(lat), len(lon)))
for n in range(len(lat)):
    for m in range(len(lon)):
        sst_grid = np.squeeze(sst[trange==1, n, m])
        p = np.polyfit(time_period, sst_grid, 1)
        trendsst[n, m] = p[0] * 365.25  # 转换为°C/年

# 4. 绘图设置
plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman']  
plt.rcParams['axes.unicode_minus'] = False    

# 获取地图中心经纬度
lon0 = lon.mean()
lat0 = lat.mean()
lons, lats = np.meshgrid(lon, lat)

# 绘制地图
# m = Basemap(lat_0=lat0, lon_0=lon0) 
m = Basemap(lat_0=22., lon_0=117., llcrnrlat=0, urcrnrlat=45, llcrnrlon=102,urcrnrlon=132,projection='cyl',resolution='i')
cs = m.contourf(lons, lats, trendsst, np.arange(0, 0.05, 0.01), cmap='YlOrRd', extend='both')
cbar = m.colorbar(cs, pad="10%", label='SST变化趋势 (°C/年)')

# 添加地图要素
m.drawparallels(np.arange(-90.,91.,10.), labels=[1,0,0,0], fontsize=10)
m.drawmeridians(np.arange(-180.,181.,10.), labels=[0,0,0,1], fontsize=10)
m.drawcoastlines()
m.fillcontinents()

plt.title('1982-2022年中国海表温度变化趋势(°C/年)')  
plt.show()