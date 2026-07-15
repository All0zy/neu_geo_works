import matplotlib.pyplot as plt
from collections import defaultdict

# 解决中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def read_coordinates(filename):
    data = defaultdict(list)
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split(',')
                if len(parts) >= 4:
                    sat_id = parts[0]
                    x = float(parts[1]) * 100  # 转换为厘米
                    y = float(parts[2]) * 100
                    z = float(parts[3]) * 100
                    data[sat_id].append((x, y, z))
    return data


def calculate_errors(data1, data2):
    errors = defaultdict(list)
    for sat_id in data1:
        if sat_id in data2:
            if sat_id.startswith(('C01', 'C02', 'C03', 'C04', 'C05')):
                continue
            points1 = data1[sat_id]
            points2 = data2[sat_id]
            if len(points1) != len(points2):
                print(f"警告：卫星 {sat_id} 的点数量不一致，跳过。")
                continue
            for i in range(len(points1)):
                x1, y1, z1 = points1[i]
                x2, y2, z2 = points2[i]

                # 计算绝对误差（厘米）
                dx = x2 - x1
                dy = y2 - y1
                dz = z2 - z1

                # 计算相对误差（百分比）
                rx = abs(dx / x1) * 100 if x1 != 0 else 0.0
                ry = abs(dy / y1) * 100 if y1 != 0 else 0.0
                rz = abs(dz / z1) * 100 if z1 != 0 else 0.0

                errors[sat_id].append({
                    'absolute': (dx, dy, dz),
                    'relative': (rx, ry, rz)
                })
    return errors


def generate_report(errors, filename='误差分析报告.txt'):
    report = []
    report.append("卫星位置误差分析报告（序号6-45）\n")
    report.append("-----------------------\n")

    # 收集统计数据
    all_rx = []
    all_ry = []
    all_rz = []
    max_error = None
    max_sat = None
    max_point = None

    for sat_id in sorted(errors.keys()):
        # 跳过C01-C05
        if sat_id.startswith(('C01', 'C02', 'C03', 'C04', 'C05')):
            continue
        report.append(f"卫星: {sat_id}\n")
        report.append("----------------------------------------\n")
        points = errors[sat_id]
        for i, point in enumerate(points, 1):  # 点号从1开始
            dx, dy, dz = point['absolute']
            rx, ry, rz = point['relative']

            report.append(f"点号: {i}\n")
            report.append(f"绝对误差: ΔX={dx:.4f}, ΔY={dy:.4f}, ΔZ={dz:.4f}\n")
            report.append(f"相对误差: X={rx:.4f}%, Y={ry:.4f}%, Z={rz:.4f}%\n")
            report.append("\n")  # 点之间空行

            # 收集统计数据
            all_rx.append(rx)
            all_ry.append(ry)
            all_rz.append(rz)

            # 跟踪最大误差
            current_max = max(rx, ry, rz)
            if (max_error is None) or (current_max > max_error):
                max_error = current_max
                max_sat = sat_id
                max_point = i
        report.append("\n")  # 卫星之间空行

    # 统计计算
    report.append("------------ 统计结果 ------------\n")
    if all_rx:
        avg_rx = sum(all_rx) / len(all_rx)
        avg_ry = sum(all_ry) / len(all_ry)
        avg_rz = sum(all_rz) / len(all_rz)
        report.append(f"平均相对误差: X={avg_rx:.4f}%, Y={avg_ry:.4f}%, Z={avg_rz:.4f}%\n")
        report.append(f"最大相对误差: X={max(all_rx):.4f}%, Y={max(all_ry):.4f}%, Z={max(all_rz):.4f}%\n")
        report.append(f"最小相对误差: X={min(all_rx):.4f}%, Y={min(all_ry):.4f}%, Z={min(all_rz):.4f}%\n")
    else:
        report.append("没有有效误差数据。\n")

    # 最大误差详情
    report.append("------------ 最大误差详情 ------------\n")
    if max_sat and max_point:
        max_data = errors[max_sat][max_point - 1]
        dx, dy, dz = max_data['absolute']
        rx, ry, rz = max_data['relative']
        report.append(f"卫星: {max_sat}\n")
        report.append(f"点号: {max_point}\n")
        report.append(f"绝对误差: ΔX={dx:.4f}, ΔY={dy:.4f}, ΔZ={dz:.4f}\n")
        report.append(f"相对误差: X={rx:.4f}%, Y={ry:.4f}%, Z={rz:.4f}%\n")
    else:
        report.append("未找到最大误差点。\n")

    # 写入文件
    with open(filename, 'w') as f:
        f.writelines(report)


def plot_errors(errors):
    # 过滤C01-C05并获取有效卫星
    valid_sats = [sat for sat in errors if not sat.startswith(('C01', 'C02', 'C03', 'C04', 'C05'))]
    if not valid_sats:
        print("没有有效的卫星数据")
        return

    # 计算每个卫星的平均误差
    sat_errors = []
    for sat_id in valid_sats:
        points = errors[sat_id]
        avg_abs = [sum([p['absolute'][i] for p in points]) / len(points) for i in range(3)]
        avg_rel = [sum([p['relative'][i] for p in points]) / len(points) for i in range(3)]
        sat_errors.append({
            'id': sat_id,
            'abs': avg_abs,
            'rel': avg_rel
        })

    # 分三张图显示
    total_sats = len(sat_errors)
    sats_per_plot = (total_sats + 2) // 3  # 向上取整
    for i in range(3):
        start = i * sats_per_plot
        end = start + sats_per_plot
        subset = sat_errors[start:end]
        if not subset:
            break

        # 创建图表
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        plt.subplots_adjust(wspace=0.3)

        # 绝对误差柱状图
        ax1 = axes[0]
        x = [sat['id'] for sat in subset]
        bar_width = 0.25
        offset = -bar_width

        ax1.bar(x, [s['abs'][0] for s in subset], width=bar_width, label='X轴', color='red', align='center')
        ax1.bar(x, [s['abs'][1] for s in subset], width=bar_width, label='Y轴', color='green', align='center',
                bottom=[s['abs'][0] for s in subset])
        ax1.bar(x, [s['abs'][2] for s in subset], width=bar_width, label='Z轴', color='blue', align='center',
                bottom=[s['abs'][0] + s['abs'][1] for s in subset])
        ax1.set_title('平均绝对误差 (cm)')
        ax1.set_ylabel('误差值 (cm)')
        ax1.set_xticks(x)
        ax1.set_xticklabels(x, rotation=45, ha='right')
        ax1.legend()

        # 相对误差柱状图
        ax2 = axes[1]
        ax2.bar(x, [s['rel'][0] for s in subset], width=bar_width, label='X轴', color='red', align='center')
        ax2.bar(x, [s['rel'][1] for s in subset], width=bar_width, label='Y轴', color='green', align='center',
                bottom=[s['rel'][0] for s in subset])
        ax2.bar(x, [s['rel'][2] for s in subset], width=bar_width, label='Z轴', color='blue', align='center',
                bottom=[s['rel'][0] + s['rel'][1] for s in subset])
        ax2.set_title('平均相对误差 (%)')
        ax2.set_ylabel('误差百分比')
        ax2.set_xticks(x)
        ax2.set_xticklabels(x, rotation=45, ha='right')
        ax2.legend()

        # 保存图表
        plt.tight_layout()
        plt.savefig(f'误差图像_{i + 1}.png')
        plt.close()


# 主程序
file1 = '坐标.txt'
file2 = '北斗卫星位置.txt'

data1 = read_coordinates(file1)
data2 = read_coordinates(file2)

errors = calculate_errors(data1, data2)
generate_report(errors)  # 生成报告
plot_errors(errors)  # 绘制图像

print("误差分析报告已生成：误差分析报告.txt")
print("误差图像已生成：误差图像_1.png, 误差图像_2.png, 误差图像_3.png")