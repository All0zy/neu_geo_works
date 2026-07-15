import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def visualize_dop_metrics(position):
    # 将观测时间字符串转换为 datetime 对象
    observation_times = [datetime.strptime(time, '%Y-%m-%d %H:%M:%S') for time in position.observation_times]

    fig, axes = plt.subplots(5, 1, figsize=(8, 15))
    fig.suptitle("DOP 指标")

    dop_metrics = [
        (position.gdop_values, "GDOP", 'green'),
        (position.pdop_values, "PDOP", 'orange'),
        (position.hdop_values, "HDOP", 'blue'),
        (position.vdop_values, "VDOP", 'red'),
        (position.tdop_values, "TDOP", 'purple')
    ]

    for ax, (values, label, color) in zip(axes, dop_metrics):
        if values:
            # 设置 x 轴为日期格式
            ax.xaxis_date()
            # 设置 x 轴刻度为一小时一个点
            ax.xaxis.set_major_locator(mdates.HourLocator())
            # 设置 x 轴刻度标签格式，只显示时间且不显示 :
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
            # 不旋转 x 轴刻度标签
            plt.setp(ax.get_xticklabels(), rotation=0)
            # 减小坐标点的大小
            ax.plot(observation_times, values, marker='o', markersize=2, label=label, color=color)
            ax.set_ylabel(label)
            ax.legend()

    plt.tight_layout()
    plt.subplots_adjust(top=0.95)
    # 保存图片为 jpg 格式
    fig.savefig('./output/dop_metrics.jpg', format='jpg', dpi=300)
    plt.show()


def visualize_residuals(position):
    if position.final_positions and position.ApproxPos:
        final_positions = np.array(position.final_positions)
        approx_pos = np.array(position.ApproxPos)

        residuals_x = final_positions[:, 0] - approx_pos[0]
        residuals_y = final_positions[:, 1] - approx_pos[1]
        residuals_z = final_positions[:, 2] - approx_pos[2]

        residuals = [residuals_x, residuals_y, residuals_z]
        labels = ["X 坐标残差", "Y 坐标残差", "Z 坐标残差"]
        colors = ['blue', 'green', 'red']

        fig, axes = plt.subplots(3, 1, figsize=(8, 12))
        fig.suptitle("定位坐标的 X、Y、Z 残差图")

        for ax, res, label, color in zip(axes, residuals, labels, colors):
            ax.scatter(np.arange(len(res)), res, color=color, label=label, alpha=0.5)

            # 绘制 y = 0 参考线
            ax.axhline(y=0, color='black', linestyle='--', label='残差均值参考线')

            ax.set_ylabel("残差 (m)")
            ax.legend()

        plt.tight_layout()
        # 保存图片为 jpg 格式
        fig.savefig('./output/residuals.jpg', format='jpg', dpi=300)
        plt.show()


def visualize_3d_position(position):
    if position.final_positions:
        final_positions = np.array(position.final_positions)
        approx_pos = np.array(position.ApproxPos)

        xs, ys, zs = final_positions[:, 0], final_positions[:, 1], final_positions[:, 2]

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle("三维位置估计的三个立面平面图")

        # XY 平面
        axes[0].scatter(xs, ys, c='blue', marker='o', s=10, label="估计位置")
        axes[0].scatter(approx_pos[0], approx_pos[1], c='red', marker='x', s=100, label="近似位置")
        axes[0].plot(xs, ys, linestyle='--', color='gray', alpha=0.5, label="轨迹")
        axes[0].set_xlabel("X (m)")
        axes[0].set_ylabel("Y (m)")
        axes[0].set_title("XY 平面")
        axes[0].legend()

        # XZ 平面
        axes[1].scatter(xs, zs, c='blue', marker='o', s=10, label="估计位置")
        axes[1].scatter(approx_pos[0], approx_pos[2], c='red', marker='x', s=100, label="近似位置")
        axes[1].plot(xs, zs, linestyle='--', color='gray', alpha=0.5, label="轨迹")
        axes[1].set_xlabel("X (m)")
        axes[1].set_ylabel("Z (m)")
        axes[1].set_title("XZ 平面")
        axes[1].legend()

        # YZ 平面
        axes[2].scatter(ys, zs, c='blue', marker='o', s=10, label="估计位置")
        axes[2].scatter(approx_pos[1], approx_pos[2], c='red', marker='x', s=100, label="近似位置")
        axes[2].plot(ys, zs, linestyle='--', color='gray', alpha=0.5, label="轨迹")
        axes[2].set_xlabel("Y (m)")
        axes[2].set_ylabel("Z (m)")
        axes[2].set_title("YZ 平面")
        axes[2].legend()

        plt.tight_layout()
        # 保存图片为 jpg 格式
        fig.savefig('./output/3d_position.jpg', format='jpg', dpi=300)
        plt.show()
    else:
        print("No valid positioning results to visualize in 2D planes.")