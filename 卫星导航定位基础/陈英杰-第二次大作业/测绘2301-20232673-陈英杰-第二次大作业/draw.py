import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# 结果文件路径
file_path = r"C:\Users\Liu\Desktop\ade\output\results_20250409_012923.txt"

# 读取文件
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 提取DOP值
dop_start_index = lines.index("PDOP     TDOP     HDOP     VDOP     GDOP    \n") + 2
dop_values = []
for line in lines[dop_start_index:dop_start_index + 25]:
    values = [float(x) for x in line.split()]
    if len(values) == 5:
        dop_values.append(values)

dop_values = np.array(dop_values)

# 提取测站坐标
coord_start_index = lines.index("平差后的测站坐标:\n") + 2
coords = []
for line in lines[coord_start_index:]:
    if line.strip():
        parts = line.strip().split()
        for i in range(0, len(parts), 3):
            coord = [float(x) for x in parts[i:i + 3]]
            coords.append(coord)

coords = np.array(coords)

# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300

# 设置全局字体和字体大小
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 12

# 设置线条样式和颜色
line_styles = ['-', '--', '-.', ':', '-']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

# 绘制DOP值折线图
plt.figure(figsize=(12, 6))
labels = ['PDOP', 'TDOP', 'HDOP', 'VDOP', 'GDOP']
for i in range(5):
    plt.plot(dop_values[:, i], label=labels[i], linestyle=line_styles[i], color=colors[i], linewidth=2)

plt.title('DOP Values Over Epochs', fontsize=16, fontweight='bold')
plt.xlabel('Epoch', fontsize=14)
plt.ylabel('Value', fontsize=14)
plt.legend(fontsize=12, loc='upper right')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# 绘制测站坐标折线图
plt.figure(figsize=(12, 6))
coord_labels = ['X', 'Y', 'Z']
for i in range(3):
    plt.plot(coords[:, i], label=coord_labels[i], linestyle=line_styles[i % 3], color=colors[i % 3], linewidth=2)

plt.title('Station Coordinates Over Epochs', fontsize=16, fontweight='bold')
plt.xlabel('Epoch', fontsize=14)
plt.ylabel('Coordinate Value', fontsize=14)
plt.legend(fontsize=12, loc='upper right')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# 绘制测站坐标散点图
plt.figure(figsize=(12, 6))
sc = plt.scatter(coords[:, 0], coords[:, 1], c=coords[:, 2], cmap='viridis', s=50, edgecolor='k', alpha=0.7)
plt.colorbar(sc, label='Z Coordinate')
plt.title('Scatter Plot of Station Coordinates (X vs Y with Z as Color)', fontsize=16, fontweight='bold')
plt.xlabel('X Coordinate', fontsize=14)
plt.ylabel('Y Coordinate', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# 绘制测站坐标的3D散点图
fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(111, projection='3d')
sc = ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2], c=coords[:, 2], cmap='viridis', s=50, edgecolor='k', alpha=0.7)
fig.colorbar(sc, ax=ax, label='Z Coordinate')
ax.set_title('3D Scatter Plot of Station Coordinates', fontsize=16, fontweight='bold')
ax.set_xlabel('X Coordinate', fontsize=14)
ax.set_ylabel('Y Coordinate', fontsize=14)
ax.set_zlabel('Z Coordinate', fontsize=14)
plt.tight_layout()
plt.show()