import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# -------------------------- 1. 数据预处理（读取+清洗）--------------------------
def load_single_wave_data(file_path):
    """读取单个浮标文件并预处理时间和有效波高字段"""
    columns = [
        'YY', 'MM', 'DD', 'hh', 'mm', 'WDIR', 'WSPD', 'GST', 'WVHT', 
        'DPD', 'APD', 'MWD', 'PRES', 'ATMP', 'WTMP', 'DEWP', 'VIS', 'TIDE'
    ]
    df = pd.read_csv(
        file_path,
        skiprows=2,  # 跳过前两行注释表头
        sep='\s+',  # 按空格分隔数据
        names=columns,
        dtype={'YY': int, 'MM': int, 'DD': int, 'hh': int, 'mm': int, 'WVHT': float}
    )
    
    # 筛选2017年1月数据
    df = df[(df['YY'] == 2017) & (df['MM'] == 1)]
    
    # 显式指定年、月、日、时、分的格式
    df['datetime'] = pd.to_datetime(
        df['YY'].astype(str) + '-' + 
        df['MM'].astype(str) + '-' + 
        df['DD'].astype(str) + ' ' + 
        df['hh'].astype(str) + ':' + 
        df['mm'].astype(str),
        format='%Y-%m-%d %H:%M'
    )
    
    # 清洗异常值（99.0为无效值）
    df = df[df['WVHT'] < 99.0].sort_values('datetime').reset_index(drop=True)
    return df

# -------------------------- 2. 绘制多文件时间序列图（5个纵向子图）--------------------------
def plot_multi_wave_time_series(file_list, save_path='multi_wave_height_201701.png'):
    """绘制五个文件各自的有效波高时间序列，纵向排列，Y轴自适应"""
    plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman']  # 设置为黑体等支持中文的字体
    plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示异常
    
    # 创建画布
    fig, axes = plt.subplots(
        nrows=3, ncols=1, 
        figsize=(15, 15),  # 调整高度以适应五个子图
        sharex=False,      # 每个子图独立显示时间轴
        gridspec_kw={'hspace': 0.3}  # 增加子图间距
    )
    
    # 定义配色和文件标题映射
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
    file_titles = {
        '41114h2017.txt': '浮标41114 2017年1月有效波高',
        '44005h2017.txt': '浮标44005 2017年1月有效波高',
        '46027h2017.txt': '浮标46027 2017年1月有效波高'
    }
    
    # 逐个文件绘制子图
    for i, (file_path, color) in enumerate(zip(file_list, colors)):
        df = load_single_wave_data(file_path)
        ax = axes[i]
        
        # 绘制有效波高时间序列
        ax.plot(
            df['datetime'], df['WVHT'],
            color=color, linewidth=1.2, alpha=0.8, label='有效波高'
        )
        
        # 子图样式设置
        # 修复路径分割问题，适配Windows系统
        file_name = file_path.split('\\')[-1] if '\\' in file_path else file_path.split('/')[-1]
        ax.set_title(file_titles[file_name], fontsize=20, fontweight='bold', pad=10)
        ax.set_ylabel('有效波高 (m)', fontsize=16)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=16, loc='upper right')
        
        # Y轴自适应（根据每个浮标的数据范围自动调整）
        if not df.empty:
            y_min = df['WVHT'].min()
            y_max = df['WVHT'].max()
            # 给Y轴留一定的上下空间
            ax.set_ylim(y_min - 0.2, y_max + 0.2)  
        
        # 美化x轴
        ax.tick_params(axis='x')
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d %H:%M'))
        ax.set_xlabel('时间', fontsize=16)
    
    # 整体布局调整
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(
        save_path,
        dpi=300,
        bbox_inches='tight'
    )
    plt.close()
    print(f"图片已保存至：{save_path}")

# -------------------------- 3. 主函数（执行流程）--------------------------
if __name__ == "__main__":
    # 定义fb文件夹下的五个文件路径
    file_list = [
        'fb/41114h2017.txt',
        'fb/44005h2017.txt',
        'fb/46027h2017.txt'
    ]

    plot_multi_wave_time_series(file_list)
    print("多浮标有效波高时间序列图绘制完成！")