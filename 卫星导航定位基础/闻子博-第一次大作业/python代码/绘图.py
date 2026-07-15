import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import mplcursors


def read_bds_coordinates(filename):
    ids = []
    x = []
    y = []
    z = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('C'):
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    ids.append(parts[0])
                    x.append(float(parts[1]))
                    y.append(float(parts[2]))
                    z.append(float(parts[3]))
    return ids, x, y, z


def plot_bds_coordinates(ids, x, y, z):
    # 创建颜色映射字典
    color_map = {
        'C01': '#1f77b4', 'C02': '#ff7f0e', 'C03': '#2ca02c', 'C04': '#d62728', 'C05': '#9467bd',
        'C06': '#8c564b', 'C07': '#e377c2', 'C08': '#7f7f7f', 'C09': '#bcbd22', 'C10': '#17becf',
        'C11': '#aec7e8', 'C12': '#ffbb78', 'C13': '#98df8a', 'C14': '#ff9896', 'C16': '#c5b0d5',
        'C19': '#c49c94', 'C20': '#f7b6d2', 'C21': '#c7c7c7', 'C22': '#dbdb8d', 'C23': '#9edae5',
        'C24': '#8c6d31', 'C25': '#393b79', 'C26': '#555555', 'C27': '#ad494a', 'C28': '#8c96c6',
        'C29': '#cc6666', 'C30': '#66cc99', 'C32': '#3366cc', 'C33': '#993366', 'C34': '#669933',
        'C35': '#cc33cc', 'C36': '#33cccc', 'C37': '#999933', 'C38': '#666699', 'C39': '#996633',
        'C40': '#339966', 'C41': '#cc9966', 'C42': '#66cc66', 'C43': '#993399', 'C44': '#336699',
        'C45': '#999966', 'C46': '#669999', 'C47': '#cc6699', 'C48': '#99cc66', 'C49': '#6666cc',
        'C50': '#cc3399', 'C59': '#33cc99', 'C60': '#9966cc'
    }

    # 创建图形和子图
    fig = plt.figure(figsize=(15, 7))
    fig.patch.set_facecolor('#f0f0f0')  # 背景色
    # 二维视图
    ax2d = fig.add_subplot(121)
    ax2d.set_facecolor('#eaeaf2')  # 子图背景色
    colors_2d = [color_map[id] for id in ids]
    sc2d = ax2d.scatter(x, y, c=colors_2d, alpha=0.8, s=20)
    ax2d.set_xlabel('X (m)', fontsize=10)
    ax2d.set_ylabel('Y (m)', fontsize=10)
    ax2d.set_title('BDS Satellite Coordinates (2D View)', fontsize=12)
    # 三维视图
    ax3d = fig.add_subplot(122, projection='3d')
    ax3d.set_facecolor('#eaeaf2')
    colors_3d = [color_map[id] for id in ids]
    sc3d = ax3d.scatter(x, y, z, c=colors_3d, alpha=0.7, s=20)
    ax3d.set_xlabel('X (m)', fontsize=10)
    ax3d.set_ylabel('Y (m)', fontsize=10)
    ax3d.set_zlabel('Z (m)', fontsize=10)
    ax3d.set_title('BDS Satellite Coordinates (3D View)', fontsize=12)
    ax3d.view_init(elev=25, azim=45)  # 调整视角
    # 悬停提示样式
    tooltip_style = {
        'arrowprops': dict(facecolor='black', shrink=0.05),
        'bbox': dict(facecolor='white', alpha=0.9, edgecolor='gray')
    }
    # 二维悬停事件
    def hover2d(sel):
        index = sel.target.index
        msg = f'Satellite: {ids[index]}\nX: {x[index]:.2f} m\nY: {y[index]:.2f} m'
        sel.annotation.set_text(msg)
        sel.annotation.set(**tooltip_style)
    # 三维悬停事件
    def hover3d(sel):
        index = sel.target.index
        msg = f'Satellite: {ids[index]}\nX: {x[index]:.2f} m\nY: {y[index]:.2f} m\nZ: {z[index]:.2f} m'
        sel.annotation.set_text(msg)
        sel.annotation.set(**tooltip_style)
    # 绑定悬停事件
    mplcursors.cursor(sc2d, hover=mplcursors.HoverMode.Transient).connect("add", hover2d)
    mplcursors.cursor(sc3d, hover=mplcursors.HoverMode.Transient).connect("add", hover3d)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # 读取坐标数据
    ids, x, y, z = read_bds_coordinates('北斗卫星位置.txt')
    # 绘制图形
    plot_bds_coordinates(ids, x, y, z)