"""
VTEC数据处理和绘制
从RINEX观测文件(OBV)和SP3轨道文件生成各测站的VTEC数据,并输出CSV和图表
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta
import warnings
from scipy.interpolate import griddata
from scipy.signal import savgol_filter
import imageio
import io
import json
from shapely.geometry import Point, shape
from shapely.ops import unary_union

warnings.filterwarnings('ignore')

import matplotlib
font_list = ['SimSun', 'SimHei',  'FangSong', 'DejaVu Sans']
for font in font_list:
    try:
        plt.rcParams['font.sans-serif'] = [font]
        break
    except:
        continue

# 或者直接使用系统字体路径
import os
import platform
if platform.system() == 'Windows':
    # Windows系统字体路径
    font_paths = [
        'C:\\Windows\\Fonts\\SimHei.ttf',
        'C:\\Windows\\Fonts\\simsun.ttc',
        'C:\\Windows\\Fonts\\FangSong.ttf'
    ]
    for font_path in font_paths:
        if os.path.exists(font_path):
            matplotlib.font_manager.fontManager.addfont(font_path)
            plt.rcParams['font.sans-serif'] = [os.path.basename(font_path).split('.')[0]]
            break

plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 常数定义
SPEED_OF_LIGHT = 299792458.0  # m/s
FREQ_L1 = 1.57542e9  # Hz
FREQ_L2 = 1.22760e9  # Hz
FREQ_L5 = 1.17645e9  # Hz
FREQ_E5A = 1.17645e9  # Hz
FREQ_E5B = 1.20714e9  # Hz
FREQ_B2A = 1.16140e9  # Hz
FREQ_B2B = 1.20714e9  # Hz

# 电子质量常数
K_ION = 40.308193e16  # m^3 / s^2

class RINEXReader:
    """RINEX观测文件读取器"""
    
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.header = {}
        self.data = {}
        self.obs_types = {}  # 各系统的观测类型名称
        self.obs_indices = {}  # 各系统的观测类型索引{sys: {type_name: index}}
        self.parse()
    
    def parse(self):
        """解析RINEX文件"""
        with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # 解析header
        header_end = 0
        for i, line in enumerate(lines):
            if 'END OF HEADER' in line:
                header_end = i
                break
            
            if len(line) >= 60:
                label = line[60:].strip()
                content = line[:60].strip()
                
                if label == 'MARKER NAME':
                    self.header['marker_name'] = content
                elif label == 'APPROX POSITION XYZ':
                    parts = content.split()
                    if len(parts) >= 3:
                        try:
                            self.header['approx_pos'] = (float(parts[0]), float(parts[1]), float(parts[2]))
                        except:
                            pass
                elif label == 'TIME OF FIRST OBS':
                    parts = content.split()
                    if len(parts) >= 5:
                        try:
                            self.header['time_first'] = datetime(
                                int(parts[0]), int(parts[1]), int(parts[2]),
                                int(parts[3]), int(parts[4]), int(float(parts[5]))
                            )
                        except:
                            pass
                elif label == 'INTERVAL':
                    try:
                        self.header['interval'] = float(content)
                    except:
                        pass
                elif label == 'SYS / # / OBS TYPES':
                    sys = content[0] if content else 'G'
                    if sys not in self.obs_types:
                        self.obs_types[sys] = []
                    # 提取观测类型（跳过第一个数字）
                    obs_line = content[1:].strip()
                    types = obs_line.split()
                    # 过滤掉纯数字的count字段
                    types = [t for t in types if not t.isdigit()]
                    self.obs_types[sys].extend(types)
        
        # 建立观测类型索引
        for sys, types in self.obs_types.items():
            self.obs_indices[sys] = {t: i for i, t in enumerate(types)}
        
        # 解析观测数据
        current_epoch = None
        epoch_data = {}
        
        i = header_end + 1
        while i < len(lines):
            line = lines[i]
            
            # 检查epoch行（以> 开头）
            if line.startswith('>'):
                # 保存前一个epoch的数据
                if current_epoch is not None and epoch_data:
                    self.data[current_epoch] = epoch_data
                    epoch_data = {}
                
                try:
                    parts = line.split()
                    year = int(parts[1])
                    month = int(parts[2])
                    day = int(parts[3])
                    hour = int(parts[4])
                    minute = int(parts[5])
                    second = float(parts[6])
                    current_epoch = datetime(year, month, day, hour, minute, int(second))
                    
                    # 下一行开始是观测数据
                    i += 1
                    
                    # 读取该epoch下的所有观测数据
                    while i < len(lines):
                        data_line = lines[i]
                        
                        # 如果遇到下一个epoch,则中断
                        if data_line.startswith('>'):
                            i -= 1  # 回退到下一个epoch行
                            break
                        
                        if len(data_line) < 1:
                            i += 1
                            continue
                        
                        # 解析卫星号和观测数据
                        try:
                            sat_id = data_line[:3].strip()
                            if not sat_id or sat_id.startswith('>'):
                                i += 1
                                continue
                            
                            obs_str = data_line[3:]
                            obs_values = []
                            
                            # 以16个字符为一个观测值
                            for j in range(0, len(obs_str), 16):
                                obs_chunk = obs_str[j:j+16]
                                if obs_chunk.strip():
                                    try:
                                        val = float(obs_chunk[:14])
                                        obs_values.append(val)
                                    except:
                                        obs_values.append(np.nan)
                                else:
                                    obs_values.append(np.nan)
                            
                            if sat_id not in epoch_data:
                                epoch_data[sat_id] = obs_values
                        except:
                            pass
                        
                        i += 1
                    
                    continue
                except:
                    pass
            
            i += 1
        
        # 保存最后一个epoch
        if current_epoch is not None and epoch_data:
            self.data[current_epoch] = epoch_data
        
        print(f"  已解析 {len(self.data)} 个epoch，观测类型索引: {self.obs_indices}")


def ecef_to_lonlat(x, y, z):
    """
    将ECEF坐标（地心地固坐标）转换为经纬度
    """
    a = 6378137.0  # WGS84椭球长半轴(m)
    b = 6356752.3142  # WGS84椭球短半轴(m)
    e2 = 1 - (b**2 / a**2)  # 第一离心率平方
    
    p = np.sqrt(x**2 + y**2)
    lat = np.arctan2(z, p * (1 - e2))
    
    # 迭代计算精确纬度
    for _ in range(5):
        N = a / np.sqrt(1 - e2 * np.sin(lat)**2)
        lat = np.arctan2(z + e2 * N * np.sin(lat), p)
    
    lon = np.arctan2(y, x)
    
    # 转换为度
    lon_deg = np.degrees(lon)
    lat_deg = np.degrees(lat)
    
    return lon_deg, lat_deg


class SP3Reader:
    """SP3轨道文件读取器"""
    
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.orbits = {}
        self.parse()
    
    def parse(self):
        """解析SP3文件"""
        with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        current_epoch = None
        
        for line in lines:
            if line.startswith('*'):
                # 解析epoch行
                try:
                    parts = line.split()
                    year = int(parts[1])
                    month = int(parts[2])
                    day = int(parts[3])
                    hour = int(parts[4])
                    minute = int(parts[5])
                    second = int(float(parts[6]))
                    current_epoch = datetime(year, month, day, hour, minute, second)
                    if current_epoch not in self.orbits:
                        self.orbits[current_epoch] = {}
                except:
                    continue
            
            elif line.startswith('P') and current_epoch:
                # 解析位置行
                try:
                    sat_id = line[1:4].strip()
                    x = float(line[4:18].strip())
                    y = float(line[18:32].strip())
                    z = float(line[32:46].strip())
                    
                    # SP3中坐标单位是km,转换为m
                    if abs(x) > 1e6:  # km
                        x *= 1000
                        y *= 1000
                        z *= 1000
                    
                    self.orbits[current_epoch][sat_id] = (x, y, z)
                except:
                    continue


def calculate_vtec(c1, c2, freq1=FREQ_L1, freq2=FREQ_L2):
    """
    计算VTEC (垂直总电子含量)
    使用双频伪距电离层延迟方法
    
    参数:
    c1: 频率1的伪距(m)
    c2: 频率2的伪距(m)
    freq1, freq2: 两个频率(Hz)
    
    返回: VTEC值(TECU)
    """
    if np.isnan(c1) or np.isnan(c2):
        return np.nan
    
    if c1 <= 0 or c2 <= 0:
        return np.nan
    
    try:
        # 标准电离层延迟公式
        # TEC(TECU) = (f1² × f2²) / (40.308 × (f1² - f2²)) × (P2 - P1)
        # 其中 40.308 × 1e16 m³/s² 是电磁常数
        
        f1_sq = freq1 ** 2
        f2_sq = freq2 ** 2
        
        # 伪距差(m)
        delta_p = abs(c2 - c1)
        
        # 分子分母
        numerator = f1_sq * f2_sq * delta_p
        denominator = 40.308e16 * (f1_sq - f2_sq)
        
        # VTEC (TECU)
        vtec = numerator / abs(denominator)
        
        return vtec
    except:
        return np.nan


def process_vtec_data(work_dir):
    """处理VTEC数据"""
    
    work_path = Path(work_dir)
    obv_dir = work_path / 'obv'
    sp3_dir = work_path / 'sp3'
    output_dir = work_path / 'output'
    output_dir.mkdir(exist_ok=True)
    
    # 收集所有观测文件
    obv_files = list(obv_dir.glob('*.26o'))
    print(f"找到 {len(obv_files)} 个观测文件")
    
    vtec_results = {}
    station_coords = {}  # 新增：存储测站坐标 {station_name: (lon, lat)}
    first_file = True
    
    for obv_file in obv_files:
        print(f"\n处理文件: {obv_file.name}")
        
        try:
            # 读取RINEX文件
            rinex = RINEXReader(str(obv_file))
            
            if not rinex.data:
                print(f"  未找到观测数据")
                continue
            
            # 提取测站名称
            marker_name = rinex.header.get('marker_name', obv_file.stem).strip()
            print(f"  测站: {marker_name}")
            
            # 新增：提取测站坐标（ECEF转经纬度）
            if 'approx_pos' in rinex.header:
                x, y, z = rinex.header['approx_pos']
                lon, lat = ecef_to_lonlat(x, y, z)
                station_coords[marker_name] = (lon, lat)
                print(f"  坐标: ({lon:.4f}°E, {lat:.4f}°N)")
            
            station_vtec = []
            total_epochs = 0
            valid_epochs = 0
            valid_sats = 0
            debug_count = 0
            
            # 处理每个epoch的观测数据
            for epoch, satellites in sorted(rinex.data.items()):
                total_epochs += 1
                epoch_vtec_values = []
                
                for sat_id, obs_values in satellites.items():
                    try:
                        sys_type = sat_id[0]  # 获取系统类型
                        
                        # 根据系统类型选择合适的双频伪距
                        c1_val = None
                        c2_val = None
                        freq1 = FREQ_L1
                        freq2 = FREQ_L2
                        
                        if sys_type not in rinex.obs_indices:
                            continue
                        
                        indices = rinex.obs_indices[sys_type]
                        
                        # GPS系统
                        if sys_type == 'G':
                            # 优先使用 C1C 和 C2W
                            if 'C1C' in indices and 'C2W' in indices:
                                c1_idx = indices['C1C']
                                c2_idx = indices['C2W']
                                if len(obs_values) > max(c1_idx, c2_idx):
                                    c1_val = obs_values[c1_idx]
                                    c2_val = obs_values[c2_idx]
                            # 备选: C1C 和 C2S
                            elif 'C1C' in indices and 'C2S' in indices:
                                c1_idx = indices['C1C']
                                c2_idx = indices['C2S']
                                if len(obs_values) > max(c1_idx, c2_idx):
                                    c1_val = obs_values[c1_idx]
                                    c2_val = obs_values[c2_idx]
                            # 备选: C1C 和 C2X
                            elif 'C1C' in indices and 'C2X' in indices:
                                c1_idx = indices['C1C']
                                c2_idx = indices['C2X']
                                if len(obs_values) > max(c1_idx, c2_idx):
                                    c1_val = obs_values[c1_idx]
                                    c2_val = obs_values[c2_idx]
                        
                        # GLONASS系统
                        elif sys_type == 'R':
                            if 'C1C' in indices and 'C2C' in indices:
                                c1_idx = indices['C1C']
                                c2_idx = indices['C2C']
                                if len(obs_values) > max(c1_idx, c2_idx):
                                    c1_val = obs_values[c1_idx]
                                    c2_val = obs_values[c2_idx]
                            elif 'C1C' in indices and 'C2P' in indices:
                                c1_idx = indices['C1C']
                                c2_idx = indices['C2P']
                                if len(obs_values) > max(c1_idx, c2_idx):
                                    c1_val = obs_values[c1_idx]
                                    c2_val = obs_values[c2_idx]
                        
                        # Galileo系统
                        elif sys_type == 'E':
                            if 'C1X' in indices and 'C7X' in indices:
                                c1_idx = indices['C1X']
                                c2_idx = indices['C7X']
                                if len(obs_values) > max(c1_idx, c2_idx):
                                    c1_val = obs_values[c1_idx]
                                    c2_val = obs_values[c2_idx]
                                    freq1 = FREQ_E5A
                                    freq2 = FREQ_E5B
                            elif 'C1C' in indices and 'C7X' in indices:
                                c1_idx = indices['C1C']
                                c2_idx = indices['C7X']
                                if len(obs_values) > max(c1_idx, c2_idx):
                                    c1_val = obs_values[c1_idx]
                                    c2_val = obs_values[c2_idx]
                                    freq1 = 1.57542e9  # E1
                                    freq2 = FREQ_E5B
                        
                        # BeiDou系统
                        elif sys_type == 'C':
                            if 'C2I' in indices and 'C7I' in indices:
                                c1_idx = indices['C2I']
                                c2_idx = indices['C7I']
                                if len(obs_values) > max(c1_idx, c2_idx):
                                    c1_val = obs_values[c1_idx]
                                    c2_val = obs_values[c2_idx]
                                    freq1 = FREQ_B2A
                                    freq2 = FREQ_B2B
                            elif 'C2I' in indices and 'C5X' in indices:
                                c1_idx = indices['C2I']
                                c2_idx = indices['C5X']
                                if len(obs_values) > max(c1_idx, c2_idx):
                                    c1_val = obs_values[c1_idx]
                                    c2_val = obs_values[c2_idx]
                        
                        # QZSS系统
                        elif sys_type == 'J':
                            if 'C1C' in indices and 'C2X' in indices:
                                c1_idx = indices['C1C']
                                c2_idx = indices['C2X']
                                if len(obs_values) > max(c1_idx, c2_idx):
                                    c1_val = obs_values[c1_idx]
                                    c2_val = obs_values[c2_idx]
                            elif 'C1C' in indices and 'C2S' in indices:
                                c1_idx = indices['C1C']
                                c2_idx = indices['C2S']
                                if len(obs_values) > max(c1_idx, c2_idx):
                                    c1_val = obs_values[c1_idx]
                                    c2_val = obs_values[c2_idx]
                        
                        # 计算VTEC
                        if c1_val is not None and c2_val is not None:
                            if not (np.isnan(c1_val) or np.isnan(c2_val)):
                                vtec = calculate_vtec(c1_val, c2_val, freq1, freq2)
                                
                                # 调试输出（仅限第一个文件的前几个有效值）
                                if first_file and debug_count < 5 and not np.isnan(vtec):
                                    print(f"    DEBUG {sat_id}: c1={c1_val:.1f}, c2={c2_val:.1f}, vtec={vtec:.2f}")
                                    debug_count += 1
                                
                                # 放宽VTEC范围检查
                                if not np.isnan(vtec) and 0 < vtec < 500:
                                    epoch_vtec_values.append(vtec)
                                    valid_sats += 1
                    except Exception as e:
                        continue
                
                # 计算该epoch的平均VTEC
                if epoch_vtec_values:
                    avg_vtec = np.mean(epoch_vtec_values)
                    station_vtec.append({
                        'epoch': epoch,
                        'vtec': avg_vtec,
                        'sat_count': len(epoch_vtec_values)
                    })
                    valid_epochs += 1
            
            if station_vtec:
                vtec_results[marker_name] = station_vtec
                print(f"  [OK] 计算得 {len(station_vtec)} 个时刻的VTEC数据 (总epochs: {total_epochs}, 有效: {valid_epochs}, 有效卫星: {valid_sats})")
            else:
                print(f"  [FAIL] 未计算出任何有效VTEC数据 (总epochs: {total_epochs}, 有效卫星: {valid_sats})")
            
            first_file = False
            
        except Exception as e:
            print(f"  处理出错: {e}")
            import traceback
            traceback.print_exc()
    
    return vtec_results, station_coords, output_dir


def save_vtec_to_csv(vtec_results, output_dir):
    """保存VTEC数据到CSV"""
    
    for station, data in vtec_results.items():
        df = pd.DataFrame(data)
        
        # 保存为CSV
        csv_file = output_dir / f"{station}_VTEC.csv"
        df.to_csv(csv_file, index=False)
        print(f"已保存: {csv_file}")
        
        # 显示统计信息
        print(f"  统计 - {station}:")
        print(f"    平均VTEC: {df['vtec'].mean():.2f} TECU")
        print(f"    最大VTEC: {df['vtec'].max():.2f} TECU")
        print(f"    最小VTEC: {df['vtec'].min():.2f} TECU")
        print(f"    标准差: {df['vtec'].std():.2f} TECU\n")


def plot_vtec_data(vtec_results, output_dir):
    """绘制VTEC图表 - 使用纯matplotlib"""
    
    # 定义颜色方案
    colors = plt.cm.tab20(np.linspace(0, 1, max(len(vtec_results), 2)))
    
    # 为每个测站绘制图表
    for idx, (station, data) in enumerate(vtec_results.items()):
        df = pd.DataFrame(data)
        primary_color = '#1f77b4'  # matplotlib默认蓝色
        
        # 创建图表 - 使用matplotlib样式
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.patch.set_facecolor('white')
        fig.suptitle(f'{station} VTEC数据分析', fontsize=16, fontweight='bold', y=0.995)
        
        # 1. 时间序列图
        ax1 = axes[0, 0]
        x_axis = np.arange(len(df))
        ax1.plot(x_axis, df['vtec'].values, linewidth=2, color=primary_color, marker='o', markersize=2, alpha=0.8)
        ax1.fill_between(x_axis, df['vtec'].values, alpha=0.2, color=primary_color)
        ax1.set_xlabel('时间索引（30秒间隔）', fontsize=10)
        ax1.set_ylabel('VTEC (TECU)', fontsize=10)
        ax1.set_title('VTEC时间序列', fontsize=11, fontweight='bold', pad=10)
        ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax1.set_facecolor('#f8f9fa')
        # 仅显示部分x轴标签以避免拥挤
        n_ticks = min(10, len(df) // 288)  # 最多10个刻度
        if n_ticks > 0:
            tick_positions = np.linspace(0, len(df)-1, n_ticks, dtype=int)
            ax1.set_xticks(tick_positions)
            tick_labels = [df['epoch'].iloc[i].strftime('%H:%M') for i in tick_positions]
            ax1.set_xticklabels(tick_labels, rotation=45, fontsize=8)
        
        # 2. 直方图
        ax2 = axes[0, 1]
        n, bins, patches = ax2.hist(df['vtec'], bins=30, color='#ff7f0e', edgecolor='black', alpha=0.7)
        # 梯度着色
        cm = plt.cm.Oranges
        for i, patch in enumerate(patches):
            patch.set_facecolor(cm(0.4 + 0.6 * i / len(patches)))
        mean_val = df['vtec'].mean()
        ax2.axvline(mean_val, color='red', linestyle='--', linewidth=2.5, label=f'平均: {mean_val:.2f} TECU')
        ax2.set_xlabel('VTEC (TECU)', fontsize=10)
        ax2.set_ylabel('频数', fontsize=10)
        ax2.set_title('VTEC分布直方图', fontsize=11, fontweight='bold', pad=10)
        ax2.legend(fontsize=9, loc='upper right')
        ax2.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=0.5)
        ax2.set_facecolor('#f8f9fa')
        
        # 3. 箱线图
        ax3 = axes[1, 0]
        bp = ax3.boxplot(df['vtec'], vert=True, patch_artist=True, widths=0.5,
                        boxprops=dict(facecolor='#2ca02c', alpha=0.7),
                        medianprops=dict(color='red', linewidth=2),
                        whiskerprops=dict(color='black', linewidth=1.5),
                        capprops=dict(color='black', linewidth=1.5),
                        flierprops=dict(marker='o', markerfacecolor='red', markersize=5, alpha=0.5))
        ax3.set_ylabel('VTEC (TECU)', fontsize=10)
        ax3.set_title('VTEC箱线图统计', fontsize=11, fontweight='bold', pad=10)
        ax3.set_xticklabels([station])
        ax3.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=0.5)
        ax3.set_facecolor('#f8f9fa')
        
        # 添加统计信息文本
        q1 = df['vtec'].quantile(0.25)
        q3 = df['vtec'].quantile(0.75)
        median = df['vtec'].median()
        stats_text = f'Q1: {q1:.1f}\nMedian: {median:.1f}\nQ3: {q3:.1f}'
        ax3.text(1.25, q1, stats_text, fontsize=8, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 4. 卫星数量与VTEC关系（散点图）
        ax4 = axes[1, 1]
        scatter = ax4.scatter(df['sat_count'], df['vtec'], 
                            c=range(len(df)), cmap='viridis', 
                            s=60, alpha=0.6, edgecolors='black', linewidth=0.5)
        ax4.set_xlabel('可见卫星数', fontsize=10)
        ax4.set_ylabel('VTEC (TECU)', fontsize=10)
        ax4.set_title('卫星数 vs VTEC', fontsize=11, fontweight='bold', pad=10)
        ax4.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax4.set_facecolor('#f8f9fa')
        
        # 添加趋势线
        z = np.polyfit(df['sat_count'], df['vtec'], 2)
        p = np.poly1d(z)
        x_trend = np.linspace(df['sat_count'].min(), df['sat_count'].max(), 100)
        ax4.plot(x_trend, p(x_trend), 'r--', linewidth=2, alpha=0.6, label='趋势线')
        ax4.legend(fontsize=9)
        
        cbar = plt.colorbar(scatter, ax=ax4)
        cbar.set_label('时间顺序', fontsize=9)
        
        plt.tight_layout()
        
        # 保存图表
        plot_file = output_dir / f"{station}_VTEC_plot.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"已保存图表: {plot_file}")
        
        plt.close(fig)
    
    # 绘制所有测站对比图
    if len(vtec_results) > 1:
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.patch.set_facecolor('white')
        
        # 使用循环颜色
        colors_list = plt.cm.tab20(np.linspace(0, 1, len(vtec_results)))
        
        for (station, data), color in zip(vtec_results.items(), colors_list):
            df = pd.DataFrame(data)
            ax.plot(df['epoch'], df['vtec'], marker='o', markersize=2, 
                   label=station, linewidth=1.8, alpha=0.75, color=color)
        
        ax.set_xlabel('时间', fontsize=12, fontweight='bold')
        ax.set_ylabel('VTEC (TECU)', fontsize=12, fontweight='bold')
        ax.set_title('全部测站VTEC对比分析', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=9, ncol=3, framealpha=0.95, edgecolor='black')
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_facecolor('#f8f9fa')
        plt.xticks(rotation=45, fontsize=9)
        plt.yticks(fontsize=9)
        
        plt.tight_layout()
        
        compare_file = output_dir / "所有测站_VTEC对比.png"
        plt.savefig(compare_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"已保存对比图表: {compare_file}")
        
        plt.close(fig)


def polynomial_powers(degree):
    """生成二维多项式的幂次组合。"""
    powers = []
    for total in range(degree + 1):
        for px in range(total + 1):
            py = total - px
            powers.append((px, py))
    return powers


def build_design_matrix(x, y, powers):
    """构造二维多项式拟合的设计矩阵。"""
    cols = [(x ** px) * (y ** py) for px, py in powers]
    return np.vstack(cols).T


def fit_polynomial_surface(lon, lat, values, degree):
    """对单个历元的测站VTEC做二维多项式拟合。"""
    lon0 = float(np.mean(lon))
    lat0 = float(np.mean(lat))
    lon_scale = float(np.std(lon)) if float(np.std(lon)) > 1.0e-12 else 1.0
    lat_scale = float(np.std(lat)) if float(np.std(lat)) > 1.0e-12 else 1.0

    xn = (lon - lon0) / lon_scale
    yn = (lat - lat0) / lat_scale

    powers = polynomial_powers(degree)
    design = build_design_matrix(xn, yn, powers)
    coeffs, _, _, _ = np.linalg.lstsq(design, values, rcond=None)

    norm = {
        "lon0": lon0,
        "lat0": lat0,
        "lon_scale": lon_scale,
        "lat_scale": lat_scale,
    }
    return coeffs, powers, norm


def evaluate_surface(lon_grid, lat_grid, coeffs, powers, norm):
    """计算拟合曲面在网格上的值。"""
    xn = (lon_grid - norm["lon0"]) / norm["lon_scale"]
    yn = (lat_grid - norm["lat0"]) / norm["lat_scale"]

    z = np.zeros_like(lon_grid, dtype=float)
    for c, (px, py) in zip(coeffs, powers):
        z += c * (xn ** px) * (yn ** py)
    return z


def choose_degree(requested_degree, point_count):
    """根据可用测站数自动降阶，避免欠定。"""
    for deg in range(requested_degree, -1, -1):
        term_count = (deg + 1) * (deg + 2) // 2
        if point_count >= term_count:
            return deg
    return 0


def blend_to_center(z_grid, center_weight=0.12):
    """轻微向全局均值回拉，减少边缘发散感。"""
    finite = np.isfinite(z_grid)
    if not np.any(finite):
        return z_grid

    mean_val = float(np.mean(z_grid[finite]))
    return (1.0 - center_weight) * z_grid + center_weight * mean_val


def load_geojson_mask(geojson_path):
    """从GeoJSON文件加载香港地界，返回shapely Polygon对象。"""
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        # 遍历所有特征，合并所有几何体
        polygons = []
        for feature in geojson_data.get('features', []):
            geom = feature.get('geometry')
            if geom:
                poly = shape(geom)
                polygons.append(poly)
        
        if polygons:
            # 合并所有多边形
            mask = unary_union(polygons)
            return mask
        return None
    except Exception as e:
        print(f"  警告: 加载GeoJSON失败 ({e})，将不使用掩膜")
        return None


def apply_geojson_mask(lon_grid, lat_grid, surface, mask):
    """根据GeoJSON掩膜过滤热力图，只保留香港地界内的值。"""
    if mask is None:
        return surface
    
    masked_surface = surface.copy()
    flat_surface = masked_surface.flatten()
    
    for idx, (lon, lat) in enumerate(zip(lon_grid.flatten(), lat_grid.flatten())):
        point = Point(lon, lat)
        if not mask.contains(point):
            flat_surface[idx] = np.nan
    
    return flat_surface.reshape(masked_surface.shape)


def render_station_heatmap(ax, lon_grid, lat_grid, surface, station_lons, station_lats, station_values, station_names, title, vmin, vmax):
    """绘制单帧平滑热力图。"""
    surface = np.clip(surface, vmin, vmax)
    levels = np.linspace(vmin, vmax, 40)

    cf = ax.contourf(lon_grid, lat_grid, surface, levels=levels, cmap='turbo', extend='both', antialiased=True)
    ax.contour(lon_grid, lat_grid, surface, levels=8, colors='white', linewidths=0.45, alpha=0.35)

    sc = ax.scatter(
        station_lons,
        station_lats,
        c=np.clip(station_values, vmin, vmax),
        cmap='turbo',
        vmin=vmin,
        vmax=vmax,
        s=42,
        edgecolors='white',
        linewidths=0.8,
        zorder=5,
    )

    for lon, lat, name, value in zip(station_lons, station_lats, station_names, station_values):
        if np.isfinite(value):
            ax.text(
                lon,
                lat,
                name,
                fontsize=7,
                ha='center',
                va='bottom',
                color='#1b1b1b',
                bbox=dict(boxstyle='round,pad=0.12', facecolor='white', edgecolor='none', alpha=0.65),
            )

    ax.set_xlabel('经度 (°E)', fontsize=11)
    ax.set_ylabel('纬度 (°N)', fontsize=11)
    ax.set_title(title, fontsize=13, pad=10)
    ax.grid(True, alpha=0.18, linestyle='--', linewidth=0.5)
    ax.set_facecolor('#f7f8fb')
    ax.set_aspect('equal', adjustable='box')
    return cf, sc


def generate_ionosphere_heatmap(vtec_results, station_coords, output_dir, geojson_mask=None, mask_name=''):
    """生成香港区域电离层热力图，并导出GIF和每小时PNG。
    
    参数:
    geojson_mask: 可选的GeoJSON掩膜对象
    mask_name: 用于区分输出目录，如 '' （原始）或 '_masked' （掩膜版）
    """

    heatmap_dir = output_dir / f'heatmap{mask_name}'
    heatmap_dir.mkdir(exist_ok=True)

    station_names = [name for name in station_coords.keys() if name in vtec_results]
    if not station_names:
        print("  没有可用于绘图的测站坐标")
        return

    station_lons = np.array([station_coords[name][0] for name in station_names], dtype=float)
    station_lats = np.array([station_coords[name][1] for name in station_names], dtype=float)

    lon_span = float(np.max(station_lons) - np.min(station_lons))
    lat_span = float(np.max(station_lats) - np.min(station_lats))
    lon_pad = max(0.015, lon_span * 0.18)
    lat_pad = max(0.015, lat_span * 0.18)

    lon_axis = np.linspace(float(np.min(station_lons) - lon_pad), float(np.max(station_lons) + lon_pad), 180)
    lat_axis = np.linspace(float(np.min(station_lats) - lat_pad), float(np.max(station_lats) + lat_pad), 180)
    lon_grid, lat_grid = np.meshgrid(lon_axis, lat_axis)

    all_epochs = sorted({obs['epoch'] for station_data in vtec_results.values() for obs in station_data})
    if not all_epochs:
        print("  没有可用历元")
        return

    epoch_to_index = {epoch: idx for idx, epoch in enumerate(all_epochs)}
    frame_epochs = [epoch for epoch in all_epochs if epoch.minute % 10 == 0 and epoch.second == 0]
    hourly_epochs = [epoch for epoch in all_epochs if epoch.minute == 0 and epoch.second == 0]

    print(f"  共 {len(all_epochs)} 个历元，GIF帧 {len(frame_epochs)} 个，每小时PNG {len(hourly_epochs)} 张")

    # 统一色阶：用全局分位数做稳健截断，避免每帧漂移和整体发蓝
    all_values = []
    for station_name in station_names:
        values = np.array([obs['vtec'] for obs in vtec_results[station_name]], dtype=float)
        values = values[np.isfinite(values)]
        if values.size:
            all_values.append(values)

    if all_values:
        merged_values = np.concatenate(all_values)
        global_vmin = float(np.nanpercentile(merged_values, 2))
        global_vmax = float(np.nanpercentile(merged_values, 98))
    else:
        global_vmin, global_vmax = 0.0, 250.0

    if not np.isfinite(global_vmin):
        global_vmin = 0.0
    if not np.isfinite(global_vmax):
        global_vmax = 250.0
    if global_vmax - global_vmin < 15.0:
        global_vmax = global_vmin + 15.0
    global_vmin = max(0.0, global_vmin)

    requested_degree = 2
    gif_frames = []
    frame_count = 0
    hourly_count = 0

    def render_epoch(epoch, save_path=None):
        values = []
        lons = []
        lats = []
        matched_names = []

        for station_name in station_names:
            station_data = vtec_results[station_name]
            match_value = np.nan
            for obs in station_data:
                if obs['epoch'] == epoch:
                    match_value = float(obs['vtec'])
                    break
            if np.isfinite(match_value):
                values.append(match_value)
                matched_names.append(station_name)
                lon, lat = station_coords[station_name]
                lons.append(lon)
                lats.append(lat)

        if len(values) < 3:
            return None

        values = np.array(values, dtype=float)
        lons = np.array(lons, dtype=float)
        lats = np.array(lats, dtype=float)

        degree = choose_degree(requested_degree, len(values))
        coeffs, powers, norm = fit_polynomial_surface(lons, lats, values, degree)
        surface = evaluate_surface(lon_grid, lat_grid, coeffs, powers, norm)
        surface = blend_to_center(surface, center_weight=0.10)
        surface = np.clip(surface, global_vmin, global_vmax)
        # 应用GeoJSON掩膜
        surface = apply_geojson_mask(lon_grid, lat_grid, surface, geojson_mask)

        fig, ax = plt.subplots(figsize=(9.8, 8.2), dpi=150)
        fig.patch.set_facecolor('white')

        hh = epoch.hour
        mm = epoch.minute
        ss = epoch.second
        title = f'香港区域电离层VTEC平滑场 | {epoch.strftime("%Y-%m-%d %H:%M:%S")} | {degree}阶多项式'
        cf, sc = render_station_heatmap(
            ax=ax,
            lon_grid=lon_grid,
            lat_grid=lat_grid,
            surface=surface,
            station_lons=lons,
            station_lats=lats,
            station_values=values,
            station_names=matched_names,
            title=title,
            vmin=global_vmin,
            vmax=global_vmax,
        )

        cbar = fig.colorbar(cf, ax=ax, pad=0.02, shrink=0.92)
        cbar.set_label('VTEC (TECU)')

        stats_text = (
            f'平均: {np.nanmean(values):.1f} TECU\n'
            f'最小: {np.nanmin(values):.1f} TECU\n'
            f'最大: {np.nanmax(values):.1f} TECU\n'
            f'测站: {len(values)}/{len(station_names)}'
        )
        ax.text(
            0.02,
            0.98,
            stats_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.28', facecolor='white', edgecolor='none', alpha=0.70),
        )

        fig.tight_layout()

        if save_path is not None:
            fig.savefig(save_path, dpi=160, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            return None

        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        frame = imageio.imread(img_buffer)
        plt.close(fig)
        return frame, degree

    print('  处理GIF帧...')
    for idx, epoch in enumerate(frame_epochs, start=1):
        rendered = render_epoch(epoch)
        if rendered is None:
            continue
        frame, degree = rendered
        gif_frames.append(frame)
        frame_count += 1
        print(f"    GIF帧 {frame_count}: {epoch.strftime('%H:%M')} (阶数: {degree}, 色阶: {global_vmin:.1f}-{global_vmax:.1f})")

    print('  处理每小时PNG...')
    for epoch in hourly_epochs:
        hourly_file = heatmap_dir / f"VTEC_heatmap_{epoch.strftime('%Y%m%d_%H')}.png"
        rendered = render_epoch(epoch, save_path=hourly_file)
        if rendered is None:
            hourly_count += 1
            print(f"    已保存小时PNG: {hourly_file.name} (色阶: {global_vmin:.1f}-{global_vmax:.1f})")

    if gif_frames:
        gif_file = output_dir / f'VTEC_ionosphere_animation{mask_name}.gif'
        imageio.mimsave(gif_file, gif_frames, duration=0.6, loop=0)
        print(f"  已生成GIF: {gif_file.name} ({frame_count} 帧)")

    print('  热力图生成完成！')
    print(f'    - GIF: {frame_count} 帧')
    print(f'    - 每小时PNG: {hourly_count} 张')


def main():
    """主函数"""
    
    # 使用绝对路径获取工作目录
    code_dir = Path(__file__).resolve().parent
    
    print("=" * 50)
    print("VTEC数据处理和绘制")
    print("=" * 50)
    print(f"工作目录: {code_dir}\n")
    
    # 处理VTEC数据
    vtec_results, station_coords, output_dir = process_vtec_data(code_dir)
    
    if not vtec_results:
        print("未找到任何可处理的VTEC数据!")
        return
    
    print(f"\n成功处理 {len(vtec_results)} 个测站")
    print("=" * 50)
    
    # 保存到CSV
    print("\n保存CSV文件...")
    save_vtec_to_csv(vtec_results, output_dir)
    
    # 绘制图表
    print("\n绘制图表...")
    plot_vtec_data(vtec_results, output_dir)
    
    # 生成热力图和GIF
    if len(station_coords) >= 3:  # 至少需要3个点进行插值
        # 加载GeoJSON掩膜
        geojson_path = code_dir / '香港特别行政区.geojson'
        geojson_mask = None
        if geojson_path.exists():
            geojson_mask = load_geojson_mask(geojson_path)
            if geojson_mask:
                print("  已加载香港地界掩膜")
        
        # 生成原始热力图（不使用掩膜）
        print("\n生成电离层热力图和GIF（原始版本，无掩膜）...")
        generate_ionosphere_heatmap(vtec_results, station_coords, output_dir, geojson_mask=None, mask_name='')
        
        # 生成掩膜版本的热力图
        if geojson_mask:
            print("\n生成电离层热力图和GIF（掩膜版本，仅香港地界）...")
            generate_ionosphere_heatmap(vtec_results, station_coords, output_dir, geojson_mask=geojson_mask, mask_name='_masked')
    
    print("\n所有处理完成!")
    print(f"输出目录: {output_dir}")


if __name__ == "__main__":
    main()
