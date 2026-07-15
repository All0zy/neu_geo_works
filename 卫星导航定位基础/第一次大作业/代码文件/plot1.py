import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot_scatter_with_mean(file_path):
    # 读取数据到DataFrame
    df = pd.read_csv(file_path, header=None, names=['id', 'x', 'y', 'z', 'x_percent', 'y_percent', 'z_percent'])

    # 计算x、y、z差值的绝对值平均值
    x_mean = np.mean(np.abs(df['x']))
    y_mean = np.mean(np.abs(df['y']))
    z_mean = np.mean(np.abs(df['z']))

    # 创建子图
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # 绘制x差值的散点图，纵坐标使用绝对值
    axes[0].scatter(range(len(df['x'])), np.abs(df['x']))
    axes[0].axhline(y=x_mean, color='r', linestyle='--', label=f'Abs Mean: {x_mean:.4f}')
    axes[0].set_title('X Difference Scatter Plot')
    axes[0].set_xlabel('Data Point Index')
    axes[0].set_ylabel('Absolute X Difference Value')
    axes[0].legend()

    # 绘制y差值的散点图，纵坐标使用绝对值
    axes[1].scatter(range(len(df['y'])), np.abs(df['y']))
    axes[1].axhline(y=y_mean, color='r', linestyle='--', label=f'Abs Mean: {y_mean:.4f}')
    axes[1].set_title('Y Difference Scatter Plot')
    axes[1].set_xlabel('Data Point Index')
    axes[1].set_ylabel('Absolute Y Difference Value')
    axes[1].legend()

    # 绘制z差值的散点图，纵坐标使用绝对值
    axes[2].scatter(range(len(df['z'])), np.abs(df['z']))
    axes[2].axhline(y=z_mean, color='r', linestyle='--', label=f'Abs Mean: {z_mean:.4f}')
    axes[2].set_title('Z Difference Scatter Plot')
    axes[2].set_xlabel('Data Point Index')
    axes[2].set_ylabel('Absolute Z Difference Value')
    axes[2].legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    input_file = "ana.txt"
    plot_scatter_with_mean(input_file)