import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import datetime
from math import radians, cos, sin, asin, sqrt

plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman']  # 设置为黑体等支持中文的字体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示异常

# ===================== 1. 高度计数据读取（文档1-529至1-530逻辑） =====================
# 初始化存储数组
latalt = np.array([])  # 高度计纬度
lonalt = np.array([])  # 高度计经度
swhalt = np.array([])  # 高度计有效波高
timealt = np.array([]) # 高度计时间（days since 1900-1-1）

# 循环读取201701文件夹下31个NC文件（文档1-529循环逻辑）
for day in range(1, 32):
    # 文件名格式化（补0，如1→01）
    day_str = str(day).zfill(2)
    filename = f"201701/wm_201701{day_str}.nc"
    # 读取数据（文档1-529 nc.Dataset用法）
    fileday = nc.Dataset(filename)
    latalt = np.concatenate((latalt, np.array(fileday.variables['lat'][:])))
    lonalt = np.concatenate((lonalt, np.array(fileday.variables['lon'][:])))
    swhalt = np.concatenate((swhalt, np.array(fileday.variables['swh'][:])))
    timealt = np.concatenate((timealt, np.array(fileday.variables['time'][:])))
    fileday.close()

# ===================== 2. 浮标数据读取与预处理（文档1-532逻辑） =====================
# 浮标信息（需根据NDBC官网查询的实际位置修正，文档1-518格式）
buoy_info = {
    '41114': {'lat': 27.552, 'lon': -80.216},  # 27°33'6"N 80°12'58"W
    '44005': {'lat': 43.201, 'lon': -69.127},  # 43°12'2"N 69°7'37"W
    '46027': {'lat': 41.840, 'lon': -124.382}  # 41°50'24"N 124°22'54"W
}
buoy_ids = ['41114', '44005', '46027']

# 初始化配准后数据存储数组（文档1-530）
bslcswh_all = np.array([])  # 配准后的浮标有效波高
slcswh_all = np.array([])  # 配准后的高度计有效波高

# ===================== 3. 球面距离计算函数（文档1-529） =====================
def geodistance(lon1, lat1, lon2, lat2):
    """计算两点间球面距离（单位：km），文档1-529定义"""
    lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    distance = 2 * asin(sqrt(a)) * 6371  # 地球半径6371km
    return distance

# ===================== 4. 高度计-浮标数据配准（文档1-530至1-536逻辑） =====================
# 时间单位统一：高度计时间（days since 1900-1-1）→ datetime（文档1-532）
timealt_datetime = [datetime.datetime(1900, 1, 1) + datetime.timedelta(days=t) for t in timealt]

# 逐个浮标配准（时空窗口：75km + 30min，文档1-525）
for bid in range(len(buoy_ids)):
    buoy_id = buoy_ids[bid]
    buoy_lat = buoy_info[buoy_id]['lat']
    buoy_lon = buoy_info[buoy_id]['lon']
    
    # 读取浮标数据（文档1-532，skiprows=2跳过标题行）
    bdata = np.loadtxt(f"fb/{buoy_id}h2017.txt", skiprows=2)
    byear = bdata[:, 0].astype(int)
    bmonth = bdata[:, 1].astype(int)
    bday = bdata[:, 2].astype(int)
    bhour = bdata[:, 3].astype(int)
    bmin = bdata[:, 4].astype(int)
    bswh = bdata[:, 8]  # 浮标有效波高（第9列，文档1-532）
    
    # 浮标时间转换（文档1-532，统一为datetime）
    btime = np.array([])
    for i in range(len(byear)):
        buoytime = datetime.datetime(byear[i], bmonth[i], bday[i], bhour[i], bmin[i], 0)
        # 转换为"days since 1900-1-1"（与高度计时间单位一致）
        buoytime = buoytime - datetime.datetime(1900, 1, 1, 0, 0, 0)
        buoytime = buoytime.total_seconds() / 3600. / 24.
        btime = np.append(btime, buoytime)
    
    # 步骤1：空间配准（筛选高度计数据：距离浮标<75km，文档1-532）
    dist = np.zeros(len(lonalt))
    for i in range(len(lonalt)):
        dist[i] = geodistance(lonalt[i], latalt[i], buoy_lon, buoy_lat)
    slctime = timealt[dist < 75]  # 空间匹配的高度计时间
    slcswh = swhalt[dist < 75]    # 空间匹配的高度计波高
    
    # 步骤2：时间配准（找最接近的浮标数据，时间差<30min，文档1-532）
    bslcswh = np.array([])
    for t in range(len(slctime)):
        t1 = abs(btime - slctime[t])
        min1 = np.min(t1)
        if min1 < 0.5 / 24.0:  # 30min = 0.5h，转换为天
            b_pos = np.where(t1 == min1)[0][0]
            bslcswh = np.append(bslcswh, bswh[b_pos])
        else:
            bslcswh = np.append(bslcswh, np.nan)
    
    # 合并所有配准数据（文档1-535）
    bslcswh_all = np.concatenate((bslcswh_all, np.squeeze(np.array(bslcswh))))
    slcswh_all = np.concatenate((slcswh_all, np.squeeze(np.array(slcswh))))

# 数据质量控制（文档1-536）
# 1. 删除NaN值
notNaNid = np.where(~np.isnan(bslcswh_all))[0]
slcswh_all = slcswh_all[notNaNid]
bslcswh_all = bslcswh_all[notNaNid]
# 2. 删除异常值（波高0.1~20m，文档1-536）
goodQC_id = np.where((slcswh_all > 0.1) & (slcswh_all < 20) & 
                     (bslcswh_all > 0.1) & (bslcswh_all < 20))[0]
x = slcswh_all[goodQC_id]  # 高度计波高（x轴）
y = bslcswh_all[goodQC_id]  # 浮标波高（y轴）

# ===================== 5. 数据对比与验证（绘制图2，文档1-540至1-545逻辑） =====================
plt.figure(figsize=(8, 6))
# 绘制散点图
plt.scatter(x, y, alpha=0.6, s=20)
# 绘制y=x参考线（文档1-545）
plt.plot([0, 4], [0, 4], 'r-', linewidth=2)
# 计算统计指标（文档1-538公式）
Bias = (y - x).mean()          # 平均偏差
Rmse = np.sqrt(((y - x) ** 2).mean())  # 均方根误差
r = np.corrcoef(x, y)[0][1]    # 相关系数
# 添加文本标注（文档1-545位置）
plt.text(0.3, 3.6, f"Bias = {Bias:.6f}", fontsize=13)
plt.text(0.3, 3.4, f"RMSE = {Rmse:.6f}", fontsize=13)
plt.text(0.3, 3.2, f"r = {r:.6f}", fontsize=13)
# 图表格式设置（文档1-545）
plt.xlim(0, 4)
plt.ylim(0, 4)
plt.xticks(np.arange(0, 4.5, 0.5))
plt.yticks(np.arange(0, 4.5, 0.5))
plt.xlabel("高度计 SWH (m)", fontsize=13, labelpad=8)
plt.ylabel("浮标 SWH (m)", fontsize=13, labelpad=10)
plt.grid(True, alpha=0.3)
plt.title("高度计浮标对比散点图", fontsize=14)
# 保存图片（文档1-187 dpi=300）
plt.savefig("图2_高度计浮标对比散点图.png", dpi=300, bbox_inches='tight')
plt.show()

# ===================== 6. 线性回归校准（绘制图3，文档1-550至1-557逻辑） =====================
# 线性回归拟合（文档1-551）
t = np.polyfit(x, y, 1)  # 1次多项式拟合（线性）
poly = np.poly1d(t)      # 生成拟合函数
x1 = poly(x)             # 校准后的高度计波高

# 绘制校准后对比图（图3）
plt.figure(figsize=(8, 6))
# 绘制校准后散点
plt.scatter(x1, y, alpha=0.6, s=20)
# 绘制y=x参考线
plt.plot([0, 4], [0, 4], 'r-', linewidth=2)
# 绘制回归线（文档1-554）
func_x = np.linspace(0, 5, 100)
plt.plot(func_x, poly(func_x), 'k--', linewidth=2)
# 计算校准后统计指标
Bias_cal = (y - x1).mean()
Rmse_cal = np.sqrt(((y - x1) ** 2).mean())
r_cal = np.corrcoef(x1, y)[0][1]
# 添加文本标注
plt.text(0.3, 3.6, f"Bias = {Bias_cal:.6f}", fontsize=13)
plt.text(0.3, 3.4, f"RMSE = {Rmse_cal:.6f}", fontsize=13)
plt.text(0.3, 3.2, f"r = {r_cal:.6f}", fontsize=13)
# 图表格式设置
plt.xlim(0, 4)
plt.ylim(0, 4)
plt.xticks(np.arange(0, 4.5, 0.5))
plt.yticks(np.arange(0, 4.5, 0.5))
plt.xlabel("校准后高度计 SWH (m)", fontsize=13, labelpad=8)
plt.ylabel("浮标 SWH (m)", fontsize=13, labelpad=10)
plt.grid(True, alpha=0.3)
plt.title("校准后高度计浮标对比散点图", fontsize=14)
# 保存图片
plt.savefig("图3_校准后对比散点图.png", dpi=300, bbox_inches='tight')
plt.show()

# 输出校准结果（文档1-558）
print(f"线性校准方程：{poly}")
print(f"校准前 - Bias: {Bias:.6f}m, RMSE: {Rmse:.6f}m, 相关系数: {r:.6f}")
print(f"校准后 - Bias: {Bias_cal:.6f}m, RMSE: {Rmse_cal:.6f}m, 相关系数: {r_cal:.6f}")