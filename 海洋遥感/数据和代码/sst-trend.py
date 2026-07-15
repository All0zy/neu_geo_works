import netCDF4 as nc 
import numpy as np
import datetime
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

file = nc.Dataset('sst.mnmean.nc')
lon = file.variables['lon'][:] 
lat = file.variables['lat'][:] 
sst = file.variables['sst'][:] 
time = file.variables['time'][:]

time1 = (datetime.date(1982,1,1) - datetime.date(1800,1,1)).days
time2 = (datetime.date(2022,12,31) - datetime.date(1800,1,1)).days
trange8222 = np.where((time >= time1) & (time <= time2), 1, 0) 

time8222 = time[trange8222==1] 
sst8222 = np.squeeze(sst[trange8222==1, 69, 173])

reg = np.polyfit(time8222, sst8222, 1)
ry = np.polyval(reg, time8222)

slope_per_10year = reg[0] * 365  
slope_text = f'斜率：{slope_per_10year:.3f} °C/年'

time8222_date = [datetime.datetime(1800,1,1) + datetime.timedelta(days=int(t)) for t in time8222]

plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(1,1,figsize=(8,4))
ax.plot(time8222_date, sst8222, 'b', label='SST')
ax.plot(time8222_date, ry, 'r', label='线性拟合')

plt.text(0.05, 0.95, slope_text, transform=ax.transAxes, 
         fontsize=10, verticalalignment='top', 
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.xlabel('年份', fontsize=11)
plt.ylabel('海表温度(°C)', fontsize=11)
plt.title('中国海域某点(117°E 22°N)1982-2022 海面温度变化趋势')
plt.legend(loc='upper right')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()