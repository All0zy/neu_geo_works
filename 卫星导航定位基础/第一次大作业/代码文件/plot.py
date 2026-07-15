import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot_boxplots(file_path):
    # 读取数据到DataFrame
    df = pd.read_csv(file_path, header=None, names=['id', 'x', 'y', 'z', 'x_percent', 'y_percent', 'z_percent'])

    # 提取差值数据列
    diff_columns = ['x', 'y', 'z']
    diff_data = [df[col] for col in diff_columns]

    # 提取百分差数据列
    percent_diff_columns = ['x_percent', 'y_percent', 'z_percent']
    percent_diff_data = [df[col] for col in percent_diff_columns]

    # 计算差值数据列的绝对值平均值
    diff_abs_mean = [np.mean(np.abs(df[col])) for col in diff_columns]

    # 计算百分差数据列的绝对值平均值
    percent_diff_abs_mean = [np.mean(np.abs(df[col])) for col in percent_diff_columns]

    # 绘制差值数据的箱线图
    plt.figure(figsize=(10, 6))
    positions_diff = np.arange(len(diff_columns))
    bp_diff = plt.boxplot(diff_data, positions=positions_diff, widths=0.5)
    plt.xticks(positions_diff, diff_columns)
    plt.xlabel('Coordinate Difference Columns')
    plt.ylabel('Values')
    plt.title('Boxplots of Coordinate Differences')
    for i, box in enumerate(bp_diff['boxes']):
        y = box.get_ydata()[1]
        plt.text(positions_diff[i], y, f'{diff_abs_mean[i]:.4f}', ha='center', va='bottom')
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.show()
    
if __name__ == "__main__":
    input_file = "ana.txt"
    plot_boxplots(input_file)
