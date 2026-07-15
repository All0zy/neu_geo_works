import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import os

plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman']  # 设置为黑体等支持中文的字体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示异常

# ---------------------- 配置参数 ----------------------
data_dir = "201701"  # 数据所在目录（根据实际路径修改）
jason1_sat_id = 8  # JASON-1卫星编号（文档定义：6=JASON1）
date_format = "wm_201701{:02d}.nc"  # 文件名格式
valid_swh_range = (0.1, 25)  # 有效波高范围（过滤异常值）

# ---------------------- 工具函数 ----------------------
def load_altimeter_data(day_range):
    """加载指定日期范围的高度计数据"""
    lat_all, lon_all, swh_all, sat_all = [], [], [], []
    
    for day in day_range:
        filename = os.path.join(data_dir, date_format.format(day))
        if not os.path.exists(filename):
            print(f"警告：文件 {filename} 不存在，跳过")
            continue
        
        with nc.Dataset(filename) as f:
            # 读取核心变量（参考文档数据结构）
            lat = f.variables['lat'][:].astype(float)
            lon = f.variables['lon'][:].astype(float)
            swh = f.variables['swh'][:].astype(float)
            sat = f.variables['satellite'][:].astype(int)
            
            # 数据质量控制
            valid_mask = (swh >= valid_swh_range[0]) & (swh <= valid_swh_range[1])
            lat = lat[valid_mask]
            lon = lon[valid_mask]
            swh = swh[valid_mask]
            sat = sat[valid_mask]
            
            # 累积数据
            lat_all.extend(lat)
            lon_all.extend(lon)
            swh_all.extend(swh)
            sat_all.extend(sat)
    
    return (np.array(lat_all), np.array(lon_all), 
            np.array(swh_all), np.array(sat_all))

def plot_swh_distribution(lat, lon, swh, title, save_path=None):
    """绘制有效波高分布图（参考文档可视化风格）"""
    plt.figure(figsize=(12, 8))
    
    # 初始化地图（Miller投影，全球范围）
    m = Basemap(lat_0=22., lon_0=117., llcrnrlat=0, urcrnrlat=45, llcrnrlon=102,urcrnrlon=132,projection='cyl',resolution='i')
    
    # 绘制基础要素
    m.drawcoastlines(linewidth=0.5)
    m.fillcontinents(color='0.8', lake_color='white')
    m.drawmeridians(np.arange(-180, 181, 10), labels=[0,0,0,1], fontsize=10)
    m.drawparallels(np.arange(-90, 91, 10), labels=[1,0,0,0], fontsize=10)
    
    # 转换经纬度坐标
    x, y = m(lon, lat)
    
    # 绘制有效波高散点图（颜色映射：jet）
    scatter = m.scatter(x, y, c=swh, cmap='jet', s=0.5, vmin=0, vmax=7)
    
    # 添加颜色条和标题
    cbar = m.colorbar(scatter, location='bottom', pad="10%")
    cbar.set_label('SWH(m)', fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    
    # 保存或显示图片
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

# ---------------------- 数据加载与绘图 ----------------------
if __name__ == "__main__":  
    # 3. 2017年1月整月（1-31日）多颗高度计有效波高分布
    lat_month, lon_month, swh_month, _ = load_altimeter_data(range(1, 32))
    plot_swh_distribution(
        lat_month, lon_month, swh_month,
        title='2017年1月整月多颗高度计观测的有效波高分布',
        save_path='201701_month_multi_zh_swh.png'
    )
    
    # 6. 2017年1月整月 JASON-1高度计有效波高分布
    lat_j1_month, lon_j1_month, swh_j1_month, sat_j1_month = load_altimeter_data(range(1, 32))
    j1_mask_month = (sat_j1_month == jason1_sat_id)
    plot_swh_distribution(
        lat_j1_month[j1_mask_month], lon_j1_month[j1_mask_month], swh_j1_month[j1_mask_month],
        title='2017年1月整月JASON-2高度计观测的有效波高分布',
        save_path='201701_month_jason2_zh_swh.png'
    )