import netCDF4 as nc
import numpy as np
import datetime
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

# 读取数据
file = nc.Dataset('sst.mnmean.nc')
lon = file.variables['lon'][:]
lat = file.variables['lat'][:]
sst = file.variables['sst'][:]  # 维度：(time, lat, lon)
time = file.variables['time'][:]  # 单位：days since 1800-1-1

# 1. 处理时间：将数值时间转换为datetime格式，便于筛选1月数据
# 基准时间
base_date = datetime.date(1800, 1, 1)
# 将time转换为datetime列表
date_list = [base_date + datetime.timedelta(days=int(t)) for t in time]

# 2. 筛选1982-2022年所有1月的数据
jan_mask = []
for date in date_list:
    # 判断是否在1982-2022年且为1月
    if (1982 <= date.year <= 2022) and (date.month == 1):
        jan_mask.append(True)
    else:
        jan_mask.append(False)
jan_mask = np.array(jan_mask)

# 计算1982-2022年所有1月的平均SST
sst_jan_mean = np.mean(sst[jan_mask, :, :], axis=0)

# 3. 筛选2022年1月的数据
sst_2022_jan = sst[[date.year == 2022 and date.month == 1 for date in date_list], :, :].mean(axis=0)

# 4. 计算距平（2022年1月 - 多年1月平均）
sst_anomaly = sst_2022_jan - sst_jan_mean

# 5. 绘图
plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman']
plt.rcParams['axes.unicode_minus'] = False

lon0 = lon.mean()
lat0 = lat.mean()
lons, lats = np.meshgrid(lon, lat)

# m = Basemap(lat_0=lat0, lon_0=lon0)
m = Basemap(lat_0=22., lon_0=117., llcrnrlat=0, urcrnrlat=45, llcrnrlon=102,urcrnrlon=132,projection='cyl',resolution='i')
cs = m.contourf(lons, lats, sst_anomaly, np.arange(-1, 2, 0.1), cmap='coolwarm')  # 用冷暖色更适合距平
cbar = m.colorbar(cs, pad="10%", label='SST异常 (°C)')

# 添加地图要素
m.drawparallels(np.arange(-90., 91., 20.), labels=[1,0,0,0], fontsize=10)
m.drawmeridians(np.arange(-180., 181., 40.), labels=[0,0,0,1], fontsize=10)
m.drawcoastlines()
m.fillcontinents(color='lightgray')

plt.title('2022年1月中国海表温度距平')
plt.show()