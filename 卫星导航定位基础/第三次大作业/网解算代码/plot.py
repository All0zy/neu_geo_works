import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# 设置 matplotlib 支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 读取 net_results.txt 文件
file_path = './output/net_results.txt'
df = pd.read_csv(file_path)

# 创建第一个 2x2 的子图布局（用于 GDOP 和模糊度精度）
fig1, axes1 = plt.subplots(2, 2, figsize=(12, 8))

# 绘制 GDOP Rover 折线图，设置颜色为蓝色，标出数据点
df.plot(x='satelite', y='GDOP Rover', ax=axes1[0, 0], title='GDOP Rover', legend=False, color='blue', marker='o')
axes1[0, 0].set_xlabel('卫星')
axes1[0, 0].set_ylabel('GDOP 值')

# 绘制 GDOP Rover2 折线图，设置颜色为绿色，标出数据点
df.plot(x='satelite', y='GDOP Rover2', ax=axes1[0, 1], title='GDOP Rover2', legend=False, color='green', marker='s')
axes1[0, 1].set_xlabel('卫星')
axes1[0, 1].set_ylabel('GDOP 值')

# 绘制 Ambiguity Precision Rover 折线图，设置颜色为红色，标出数据点
df.plot(x='satelite', y='Ambiguity Precision Rover', ax=axes1[1, 0], title='模糊度精度 Rover', legend=False, color='red', marker='^')
axes1[1, 0].set_xlabel('卫星')
axes1[1, 0].set_ylabel('模糊度精度')

# 绘制 Ambiguity Precision Rover2 折线图，设置颜色为橙色，标出数据点
df.plot(x='satelite', y='Ambiguity Precision Rover2', ax=axes1[1, 1], title='模糊度精度 Rover2', legend=False, color='orange', marker='v')
axes1[1, 1].set_xlabel('卫星')
axes1[1, 1].set_ylabel('模糊度精度')

# 自动调整第一个图的子图布局
plt.tight_layout()

# 创建第二个 2x2 的子图布局（用于 Rover 相关图）
fig2, axes2 = plt.subplots(2, 2, figsize=(12, 8))

# 第一个图：rover_x, rover_y, rover_z 的坐标 3d 散点图
ax1 = fig2.add_subplot(221, projection='3d')
rover_x = df['rover_x']
rover_y = df['rover_y']
rover_z = df['rover_z']
ax1.scatter(rover_x, rover_y, rover_z)
# 计算平均坐标
avg_rover_x = np.mean(rover_x)
avg_rover_y = np.mean(rover_y)
avg_rover_z = np.mean(rover_z)
ax1.scatter(avg_rover_x, avg_rover_y, avg_rover_z, c='red')
ax1.set_title('Rover 坐标 3D 散点图')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')

# 第二个图：Integer Ambiguity Rover 条形图
ax2 = axes2[0, 1]
ambiguity_rover = df['Integer Ambiguity Rover']
satelite = df['satelite']
ax2.bar(satelite, ambiguity_rover)
ax2.set_title('Integer Ambiguity Rover 条形图')
ax2.set_xlabel('卫星')
ax2.set_ylabel('整数模糊度')
ax2.tick_params(axis='x', rotation=90)
# 计算 Integer Ambiguity Rover 的最小值和最大值
min_ambiguity_rover = ambiguity_rover.min()
max_ambiguity_rover = ambiguity_rover.max()
# 设置合理的纵坐标范围
ax2.set_ylim(min_ambiguity_rover - 0.1 * (max_ambiguity_rover - min_ambiguity_rover), max_ambiguity_rover + 0.1 * (max_ambiguity_rover - min_ambiguity_rover))

# 第三个图：rover2_x, rover2_y, rover2_z 的坐标 3d 散点图
ax3 = fig2.add_subplot(223, projection='3d')
rover2_x = df['rover2_x']
rover2_y = df['rover2_y']
rover2_z = df['rover2_z']
ax3.scatter(rover2_x, rover2_y, rover2_z)
# 计算平均坐标
avg_rover2_x = np.mean(rover2_x)
avg_rover2_y = np.mean(rover2_y)
avg_rover2_z = np.mean(rover2_z)
ax3.scatter(avg_rover2_x, avg_rover2_y, avg_rover2_z, c='red')
ax3.set_title('Rover2 坐标 3D 散点图')
ax3.set_xlabel('X')
ax3.set_ylabel('Y')
ax3.set_zlabel('Z')

# 第四个图：Integer Ambiguity Rover2 条形图
ax4 = axes2[1, 1]
ambiguity_rover2 = df['Integer Ambiguity Rover2']
ax4.bar(satelite, ambiguity_rover2)
ax4.set_title('Integer Ambiguity Rover2 条形图')
ax4.set_xlabel('卫星')
ax4.set_ylabel('整数模糊度')
ax4.tick_params(axis='x', rotation=90)
# 计算 Integer Ambiguity Rover2 的最小值和最大值
min_ambiguity_rover2 = ambiguity_rover2.min()
max_ambiguity_rover2 = ambiguity_rover2.max()
# 设置合理的纵坐标范围
ax4.set_ylim(min_ambiguity_rover2 - 0.1 * (max_ambiguity_rover2 - min_ambiguity_rover2), max_ambiguity_rover2 + 0.1 * (max_ambiguity_rover2 - min_ambiguity_rover2))

# 自动调整第二个图的子图布局
plt.tight_layout()

# 显示两个图形
plt.show()
