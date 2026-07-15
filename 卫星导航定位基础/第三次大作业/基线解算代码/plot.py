import matplotlib.pyplot as plt
import csv
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # 导入 3D 绘图模块

# 文件路径
file_path = './output/baseline_results.txt'

# 初始化数据列表
satellites = []
gdop_values = []
ambiguity_precisions = []
rover_x = []
rover_y = []
rover_z = []
ambiguity_solutions = []

# 读取文件
with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        satellites.append(row['satelite'])
        gdop_values.append(float(row['GDOP']))
        ambiguity_precisions.append(float(row['Ambiguity Precision']))
        rover_x.append(float(row['rover_x']))
        rover_y.append(float(row['rover_y']))
        rover_z.append(float(row['rover_z']))
        ambiguity_solutions.append(float(row['Integer Ambiguity']))

# 创建一个包含两个子图的画布
fig, axes = plt.subplots(2, 1, figsize=(10, 10), sharex=True)

# 绘制 GDOP 折线图
axes[0].plot(satellites, gdop_values, marker='o', color='orange')
axes[0].set_title('GDOP')
axes[0].set_ylabel('Value')
axes[0].tick_params(axis='x', rotation=45)

# 绘制 Ambiguity Precision 折线图
axes[1].plot(satellites, ambiguity_precisions, marker='o', color='green')
axes[1].set_title('Ambiguity Precision')
axes[1].set_xlabel('Satellite')
axes[1].set_ylabel('Value')
axes[1].tick_params(axis='x', rotation=45)

# 自动调整布局
plt.tight_layout()

# 创建新的画布用于绘制流动站三维坐标和整周未知数柱状图
fig2 = plt.figure(figsize=(15, 7))

# 绘制流动站三维坐标散点图
ax1 = fig2.add_subplot(121, projection='3d')
ax1.scatter(rover_x, rover_y, rover_z, c='b', marker='o')

# 计算平均坐标
rover_avg_x = np.mean(rover_x)
rover_avg_y = np.mean(rover_y)
rover_avg_z = np.mean(rover_z)

# 标记平均点
ax1.scatter(rover_avg_x, rover_avg_y, rover_avg_z, c='r', marker='o', s=100, label='Average Position')
ax1.legend()

ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
ax1.set_title('Rover Positions in 3D')

# 绘制整周未知数柱状图
ax2 = fig2.add_subplot(122)
ax2.bar(satellites, ambiguity_solutions, color='purple')
ax2.set_xlabel('Satellite')
ax2.set_ylabel('Ambiguity Solution')
ax2.set_title('Ambiguity Solutions')
# 设置纵坐标为对数刻度
ax2.set_yscale('log')
ax2.tick_params(axis='x', rotation=45)

# 自动调整布局
plt.tight_layout()

# 显示图形
plt.show()
