import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# 读取数据
data = pd.read_csv('北斗卫星位置.txt', header=None, names=['satellite', 'x', 'y', 'z'], delimiter=',')

# 三维散点图优化
def plot_3d():
    fig = plt.figure(figsize=(14, 10))  # 增大画布尺寸
    ax = fig.add_subplot(111, projection='3d')
    
    # 颜色映射（使用tab20增强区分度）
    cmap = plt.cm.get_cmap('tab20', len(data['satellite'].unique()))
    
    # 绘制每个卫星位置
    for i, sat in enumerate(data['satellite'].unique()):
        sat_data = data[data['satellite'] == sat]
        ax.scatter(sat_data['x'], sat_data['y'], sat_data['z'],
                   c=cmap(i), s=5, alpha=0.7, label=f'Satellite {sat}')
    
    # 美化设置
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.set_zlabel('Z (m)', fontsize=12)
    ax.set_title('BeiDou Satellite Positions (3D View)', fontsize=14, pad=20)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.view_init(elev=30, azim=45)  # 调整视角
    
    # 优化图例
    legend = ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left',
                       ncol=2, fontsize=8)  # 分两列显示，减小字体
    plt.setp(legend.get_title(), fontsize=10)  # 图例标题字体
    
    plt.tight_layout()
    plt.savefig('beidou_3d_optimized.png', dpi=300, bbox_inches='tight')
    plt.close()

# 二维散点图优化
def plot_2d():
    fig, ax = plt.subplots(figsize=(16, 9))  # 采用16:9宽屏比例
    ax.set_aspect('equal')  # 保持XY轴比例一致
    
    # 颜色映射（使用tab20增强区分度）
    cmap = plt.cm.get_cmap('tab20', len(data['satellite'].unique()))
    
    # 绘制每个卫星位置
    for i, sat in enumerate(data['satellite'].unique()):
        sat_data = data[data['satellite'] == sat]
        ax.scatter(sat_data['x'], sat_data['y'],
                   c=cmap(i), s=5, alpha=0.7, label=f'Satellite {sat}')
    
    # 美化设置
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.set_title('BeiDou Satellite Positions (2D Projection)', fontsize=14, pad=20)
    ax.grid(True, alpha=0.3)
    ax.set_facecolor('#f0f0f0')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 优化图例（分三列显示）
    legend = ax.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center',
                       ncol=3, fontsize=8, frameon=False)  # 放在底部，分三列
    plt.setp(legend.get_title(), fontsize=10)  # 图例标题字体
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])  # 调整布局防止图例被截断
    plt.savefig('beidou_2d_optimized.png', dpi=300, bbox_inches='tight')
    plt.close()

# 执行绘图
plot_3d()
plot_2d()