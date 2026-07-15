import netCDF4 as nc #导入库 
file=nc.Dataset('sst.mnmean.nc') 
print(file) #读取文件信息
print(file.variables['sst'])

lon = file.variables['lon'][:] #经度 
lat = file.variables['lat'][:] #纬度 
sst = file.variables['sst'][:] #海表温度 
time = file.variables['time'][:] #时间

import numpy as np
import datetime

# 时间单位是 days since 1800-1-1 00:00:00（基准时刻）
time1 = datetime.date(2022,1,1) - datetime.date(1800,1,1)
# time1为基准时刻到1998.1.1的时间，time1.days 为这一时间对应的天数
time2 = datetime.date(2022,1,31) - datetime.date(1800,1,1)
# time2为基准时刻到1998.12.31的时间，time2.days 为这一时间对应的天数
trange = np.where((time >= time1.days)&(time <= time2.days),1,0)
sst1998 = np.mean(sst[trange==1,:,:],0)

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman']  # 设置为黑体等支持中文的字体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示异常

# 获取地图中心经纬度坐标 lat0 和 lon0
lon0 = lon.mean()
lat0 = lat.mean()
# 对经纬度网格化
lons, lats = np.meshgrid(lon, lat)
# 画图
m = Basemap(lat_0=lat0, lon_0=lon0) 
# m = Basemap(lat_0=22., lon_0=117., llcrnrlat=0, urcrnrlat=45, llcrnrlon=102,urcrnrlon=132,projection='cyl',resolution='i')
cs = m.contourf(lons, lats, sst1998, range(-10,35,1), cmap='jet')
# 绘制填充的等值线，range(0,35,1)表示从0~35每隔1绘制一条等高线
cbar = m.colorbar(cs, pad="10%", label='SST(degC)')
# 为地图添加上海岸线和经纬网格
m.drawparallels(np.arange(-90.,91.,20.), labels=[1,0,0,0], fontsize=10)
m.drawmeridians(np.arange(-180.,181.,40.), labels=[0,0,0,1], fontsize=10)
m.drawcoastlines()
m.fillcontinents()
plt.title('全球平均海面温度(2022年1月)')  # 添加标题
plt.show()