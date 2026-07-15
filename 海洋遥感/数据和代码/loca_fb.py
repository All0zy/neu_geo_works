from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman']  # 设置为黑体等支持中文的字体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示异常

# 浮标位置信息
buoy_info = {
    '41114': {'lat': 27.552, 'lon': -80.216},  # 27°33'6"N 80°12'58"W
    '44005': {'lat': 43.201, 'lon': -69.127},  # 43°12'2"N 69°7'37"W
    '46027': {'lat': 41.840, 'lon': -124.382}  # 41°50'24"N 124°22'54"W
}

# 提取纬度、经度和浮标ID
latitudes = np.array([info['lat'] for info in buoy_info.values()])
longitudes = np.array([info['lon'] for info in buoy_info.values()])
buoy_names = np.array(list(buoy_info.keys()))

# 创建Basemap对象，设置地图范围和分辨率
m = Basemap(
    llcrnrlon=-180, 
    llcrnrlat=-30, 
    urcrnrlon=-30, 
    urcrnrlat=60,
    resolution='l'
)

# 绘制地图元素
m.drawparallels(np.arange(-90., 90., 18.), labels=[1, 0, 0, 0])
m.drawmeridians(np.arange(-180., 180., 30.), labels=[0, 0, 0, 1])
m.drawcoastlines()
m.fillcontinents(color='white')

# 转换经纬度为地图坐标并绘制浮标
x, y = m(longitudes, latitudes)
plt.scatter(x, y, c='blue', s=50)

# 标注浮标ID
for i in range(len(buoy_names)):
    plt.text(x[i] + 2, y[i] - 2, buoy_names[i], color='blue', fontsize=12)

# 显示图形
plt.title('浮标位置分布')
plt.show()