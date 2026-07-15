import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def read_satellite_data(file_path):
    """读取卫星数据文件"""
    try:
        data = pd.read_csv(file_path)
        print(f"成功读取数据: {len(data)} 条记录")
        return data
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到")
        return pd.DataFrame()
    except Exception as e:
        print(f"错误: 读取文件时发生异常: {e}")
        return pd.DataFrame()


def plot_pseudo_range_over_time(data):
    """绘制伪距随时间变化图"""
    plt.figure(figsize=(12, 6))
    for satellite in data['satellite'].unique():
        satellite_data = data[data['satellite'] == satellite]
        plt.plot(satellite_data['time'], satellite_data['pseudo_range'], 'o-',
                 linewidth=1.5, markersize=3, label=satellite)

    plt.xlabel('时间 (秒)', fontsize=12)
    plt.ylabel('伪距 (米)', fontsize=12)
    plt.title('不同卫星伪距随时间变化', fontsize=14)
    plt.legend(loc='upper right', ncol=2, fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_carrier_phase_over_time(data):
    """绘制载波相位随时间变化图"""
    plt.figure(figsize=(12, 6))
    for satellite in data['satellite'].unique():
        satellite_data = data[data['satellite'] == satellite]
        plt.plot(satellite_data['time'], satellite_data['carrier_phase'], 's-',
                 linewidth=1.5, markersize=3, label=satellite)

    plt.xlabel('时间 (秒)', fontsize=12)
    plt.ylabel('载波相位 (周)', fontsize=12)
    plt.title('不同卫星载波相位随时间变化', fontsize=14)
    plt.legend(loc='upper right', ncol=2, fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_doppler_over_time(data):
    """绘制多普勒频移随时间变化图"""
    plt.figure(figsize=(12, 6))
    for satellite in data['satellite'].unique():
        satellite_data = data[data['satellite'] == satellite]
        plt.plot(satellite_data['time'], satellite_data['doppler'], '^-',
                 linewidth=1.5, markersize=3, label=satellite)

    plt.xlabel('时间 (秒)', fontsize=12)
    plt.ylabel('多普勒频移 (Hz)', fontsize=12)
    plt.title('不同卫星多普勒频移随时间变化', fontsize=14)
    plt.legend(loc='upper right', ncol=2, fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_signal_strength_over_time(data):
    """绘制信号强度随时间变化图"""
    plt.figure(figsize=(12, 6))
    for satellite in data['satellite'].unique():
        satellite_data = data[data['satellite'] == satellite]
        plt.plot(satellite_data['time'], satellite_data['signal_strength'], 'D-',
                 linewidth=1.5, markersize=3, label=satellite)

    plt.xlabel('时间 (秒)', fontsize=12)
    plt.ylabel('信号强度 (dBHz)', fontsize=12)
    plt.title('不同卫星信号强度随时间变化', fontsize=14)
    plt.legend(loc='upper right', ncol=2, fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_signal_strength_boxplot(data):
    """绘制信号强度分布箱线图"""
    plt.figure(figsize=(14, 7))
    sns.boxplot(x='satellite', y='signal_strength', data=data)

    plt.xlabel('卫星编号', fontsize=12)
    plt.ylabel('信号强度 (dBHz)', fontsize=12)
    plt.title('不同卫星信号强度分布', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_satellite_positions_2d(data):
    """绘制卫星二维位置分布图"""
    plt.figure(figsize=(10, 10))

    # 获取所有卫星ID
    satellites = data['satellite'].unique()

    # 设置颜色映射
    colors = cm.rainbow(np.linspace(0, 1, len(satellites)))

    for i, sat in enumerate(satellites):
        sat_data = data[data['satellite'] == sat]
        plt.scatter(sat_data['x'], sat_data['y'], s=50, c=[colors[i]],
                    alpha=0.7, label=sat, edgecolors='w', linewidths=0.5)

    # 绘制基准站位置（假设在原点）
    plt.scatter(0, 0, s=200, c='black', marker='^', label='基准站')

    plt.xlabel('X 坐标 (米)', fontsize=12)
    plt.ylabel('Y 坐标 (米)', fontsize=12)
    plt.title('卫星二维位置分布', fontsize=14)
    plt.legend(loc='upper right', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.axis('equal')
    plt.tight_layout()
    plt.show()


def plot_satellite_positions_3d(data):
    """绘制卫星三维位置分布图"""
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    # 获取所有卫星ID
    satellites = data['satellite'].unique()

    # 设置颜色映射
    colors = cm.rainbow(np.linspace(0, 1, len(satellites)))

    for i, sat in enumerate(satellites):
        sat_data = data[data['satellite'] == sat]
        ax.scatter(sat_data['x'], sat_data['y'], sat_data['z'],
                   s=50, c=[colors[i]], alpha=0.7, label=sat,
                   edgecolors='w', linewidths=0.5)

    # 绘制基准站位置（假设在原点）
    ax.scatter(0, 0, 0, s=200, c='black', marker='^', label='基准站')

    ax.set_xlabel('X 坐标 (米)', fontsize=12)
    ax.set_ylabel('Y 坐标 (米)', fontsize=12)
    ax.set_zlabel('Z 坐标 (米)', fontsize=12)
    ax.set_title('卫星三维位置分布', fontsize=14)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True)
    plt.tight_layout()
    plt.show()


def plot_signal_strength_3d(data):
    """绘制信号强度随卫星位置变化的3D图"""
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    # 获取所有卫星ID
    satellites = data['satellite'].unique()

    # 设置颜色映射
    colors = cm.rainbow(np.linspace(0, 1, len(satellites)))

    for i, sat in enumerate(satellites):
        sat_data = data[data['satellite'] == sat]
        scatter = ax.scatter(sat_data['x'], sat_data['y'], sat_data['z'],
                             s=sat_data['signal_strength'] * 2,  # 信号强度决定点的大小
                             c=sat_data['signal_strength'],  # 信号强度决定颜色
                             cmap='viridis', alpha=0.7,
                             edgecolors='w', linewidths=0.5)

    # 添加颜色条
    cbar = fig.colorbar(scatter, ax=ax, pad=0.1)
    cbar.set_label('信号强度 (dBHz)', fontsize=12)

    ax.set_xlabel('X 坐标 (米)', fontsize=12)
    ax.set_ylabel('Y 坐标 (米)', fontsize=12)
    ax.set_zlabel('Z 坐标 (米)', fontsize=12)
    ax.set_title('卫星信号强度三维分布', fontsize=14)
    ax.grid(True)
    plt.tight_layout()
    plt.show()


def plot_correlation_heatmap(data):
    """绘制数据相关性热力图"""
    # 选择需要计算相关性的列
    numeric_cols = ['pseudo_range', 'carrier_phase', 'doppler', 'signal_strength', 'x', 'y', 'z']

    # 计算相关系数矩阵
    corr_matrix = data[numeric_cols].corr()

    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f',
                square=True, linewidths=0.5, cbar_kws={'shrink': 0.8})
    plt.title('数据相关性热力图', fontsize=14)
    plt.tight_layout()
    plt.show()


def main():
    """主函数"""
    file_path = 'rover_station.txt'  # 请替换为实际文件路径
    satellite_data = read_satellite_data(file_path)

    if not satellite_data.empty:
        # 基本可视化
        plot_pseudo_range_over_time(satellite_data)
        plot_carrier_phase_over_time(satellite_data)
        plot_doppler_over_time(satellite_data)
        plot_signal_strength_over_time(satellite_data)
        plot_signal_strength_boxplot(satellite_data)

        # 二维和三维可视化
        plot_satellite_positions_2d(satellite_data)
        plot_satellite_positions_3d(satellite_data)
        plot_signal_strength_3d(satellite_data)

        # 相关性分析
        plot_correlation_heatmap(satellite_data)


if __name__ == "__main__":
    main()