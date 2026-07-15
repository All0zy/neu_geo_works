import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
from datetime import datetime

# 修改后的 get_results 函数
def get_results():
    # 模拟读取结果文件
    dop_values = []
    positions = []
    with open(r'D:\python\python代码\ade\output\results_20250408_221526.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        dop_start = lines.index("PDOP     TDOP     HDOP     VDOP     GDOP    \n") + 2
        dop_end = dop_start + 25
        for line in lines[dop_start:dop_end]:
            values = [float(val) for val in line.split()]
            if len(values) == 5:  # 确保每行有 5 个值
                dop_values.append(values)

        coord_start = lines.index("平差后的测站坐标:\n") + 3
        for line in lines[coord_start:]:
            if line.strip():
                coords = line.strip().split()
                for i in range(0, len(coords), 3):
                    position = [float(coords[i]), float(coords[i + 1]), float(coords[i + 2])]
                    positions.append(position)

    return {
        'dop_values': np.array(dop_values),
        'positions': np.array(positions)
    }

# 可视化成功计算的位置（三维）
def visualize_positions(positions):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2], c='b', marker='o')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('所有成功计算的位置（三维）')
    plt.show()

# 可视化五种精度评价因子（折线图）
def visualize_dop_values(dop_values):
    labels = ['PDOP', 'TDOP', 'HDOP', 'VDOP', 'GDOP']
    epochs = np.arange(len(dop_values))

    plt.figure()
    for i in range(5):
        plt.plot(epochs, dop_values[:, i], label=labels[i])

    plt.xlabel('历元')
    plt.ylabel('精度评价因子值')
    plt.title('五种精度评价因子折线图')
    plt.legend()
    plt.show()

# 可视化平差后的测站坐标（三维）
def visualize_adjusted_coords(positions):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2], c='r', marker='s')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('平差后的测站坐标（三维）')
    plt.show()

# 主函数
def main():
    results = get_results()
    positions = results['positions']
    dop_values = results['dop_values']

    # 可视化成功计算的位置
    visualize_positions(positions)

    # 可视化五种精度评价因子
    visualize_dop_values(dop_values)

    # 可视化平差后的测站坐标
    visualize_adjusted_coords(positions)

if __name__ == "__main__":
    main()