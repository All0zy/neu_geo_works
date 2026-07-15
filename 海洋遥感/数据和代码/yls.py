import netCDF4 as nc 
file = nc.Dataset('AQUA_MODIS.20220101_20220131.L3m.MO.CHL.chlor_a.9km.nc') 
# print(file)
# print(file.variables['chlor_a'])
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman']  # 设置为黑体等支持中文的字体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示异常

chlor = (file.variables['chlor_a'][:])  #叶绿素浓度读入
lons = (file.variables['lon'][:]) #经度读入
lats = (file.variables['lat'][:]) #纬度读入
#对经纬度进行编织，注意 lon、lat 和 lons、lats 是不同的变量。
lon, lat = np.meshgrid(lons, lats)
#画图 （“\”反斜杠对代码进行换行。）
# 中国
# m = Basemap(lat_0=22., lon_0=117., llcrnrlat=0, urcrnrlat=45, llcrnrlon=102,urcrnrlon=132,projection='mill',resolution='i')
# 全球
m = Basemap(llcrnrlon=-180,llcrnrlat=-80,urcrnrlon=180, urcrnrlat=80,projection='mill',resolution='l')
# 把实际经纬度坐标转换成投影地图下的经纬度坐标
mlon,mlat = m(lon,lat)
#绘制浓度分布
chl = np.log(chlor)
# m.pcolor (mlon,mlat,chl)
m.drawparallels(np.arange(-90.,91.,20.),labels = [1,0,0,0], fontsize=10)
m.drawmeridians(np.arange(-180.,181.,40.),labels = [0,0,0,1], fontsize=10)

m.drawcoastlines()
m.fillcontinents(color = 'white')
cs = m.pcolor(mlon,mlat,chl,cmap='jet')

cbar = m.colorbar(cs,location = 'bottom',label = 'Log(叶绿素浓度) ($\mu$g/L)',pad = "10%")
plt.title('全球海域叶绿素浓度梯度图(2022年1月)', fontsize = '10')
#显示图片
plt.show()