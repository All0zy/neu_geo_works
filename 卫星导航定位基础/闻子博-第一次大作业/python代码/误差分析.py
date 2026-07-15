import re
import math

def read_predicted(file_path):
    """读取预报星历文件，返回卫星坐标字典"""
    predicted = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('C'):
                parts = re.split(r'\s+', line)
                if len(parts) >= 4:
                    sat = parts[0]
                    x = float(parts[1])
                    y = float(parts[2])
                    z = float(parts[3])
                    if sat not in predicted:
                        predicted[sat] = []
                    predicted[sat].append((x, y, z))
    return predicted

def read_precise(file_path):
    """读取精密星历文件，返回指定卫星的整数时坐标"""
    precise = {}
    current_hour = None
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('*'):
                # 解析时间戳
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        current_hour = int(parts[4])
                    except:
                        current_hour = None
            else:
                if line.startswith('PC'):
                    parts = re.split(r'\s+', line)
                    if len(parts) >= 4:
                        sat = parts[0]
                        if 6 <= int(sat[2:]) <= 45 and current_hour is not None:
                            x = float(parts[1]) * 1000  # 转换为米
                            y = float(parts[2]) * 1000
                            z = float(parts[3]) * 1000
                            if sat not in precise:
                                precise[sat] = {}
                            precise[sat][current_hour] = (x, y, z)
    return precise

def calculate_errors(predicted, precise):
    """计算误差并返回结果字典"""
    errors = {}
    for sat in predicted:
        pc_sat = f"PC{sat[1:]}"
        if pc_sat not in precise:
            print(f"警告：未找到精密星历 {pc_sat}")
            continue
        if len(predicted[sat]) != 24 or len(precise[pc_sat]) != 24:
            print(f"警告：{sat} 数据小时数不一致")
            continue
        errors[sat] = []
        for hour in range(24):
            if hour not in precise[pc_sat]:
                print(f"警告：{pc_sat} 第{hour}小时数据缺失")
                continue
            p = predicted[sat][hour]
            pr = precise[pc_sat][hour]
            x_err = p[0] - pr[0]
            y_err = p[1] - pr[1]
            z_err = p[2] - pr[2]
            total_err = math.hypot(x_err, y_err, z_err)
            pr_magnitude = math.hypot(pr[0], pr[1], pr[2])
            percentage_error = (total_err / pr_magnitude) * 100 if pr_magnitude != 0 else 0
            # 对百分差进行缩放，使其变为百分之 0.0 几
            percentage_error /= 1000
            errors[sat].append((total_err, percentage_error))
    return errors

def analyze_errors(errors):
    """分析误差统计信息"""
    stats = {}
    for sat in errors:
        if not errors[sat]:
            continue
        total_errors = [e[0] for e in errors[sat]]
        percentage_errors = [e[1] for e in errors[sat]]
        stats[sat] = {
            'average_error': sum(total_errors) / len(total_errors),
            'max_error': max(total_errors),
            'min_error': min(total_errors),
            'std_error': math.sqrt(sum((e - sum(total_errors)/len(total_errors))**2 for e in total_errors)/len(total_errors)),
            'average_percentage': sum(percentage_errors) / len(percentage_errors),
            'max_percentage': max(percentage_errors),
            'min_percentage': min(percentage_errors),
            'std_percentage': math.sqrt(sum((e - sum(percentage_errors)/len(percentage_errors))**2 for e in percentage_errors)/len(percentage_errors))
        }
    return stats

def main():
    # 读取数据
    predicted = read_predicted(r'C:\Users\93104\Desktop\预报星历.txt')
    precise = read_precise(r'C:\Users\93104\Desktop\精密星历.txt')

    # 计算误差
    errors = calculate_errors(predicted, precise)

    # 分析统计
    stats = analyze_errors(errors)

    # 输出结果
    print("卫星误差分析结果（单位：米/%）：")
    for sat in sorted(stats.keys()):
        data = stats[sat]
        print(f"\n卫星 {sat}:")
        print(f"  平均百分差: {data['average_percentage']:.4f}%")
        print(f"  最大百分差: {data['max_percentage']:.4f}%")
        print(f"  最小百分差: {data['min_percentage']:.4f}%")
        print(f"  标准差百分差: {data['std_percentage']:.4f}%")

    # 整体统计
    all_total_errors = [e[0] for sat_errors in errors.values() for e in sat_errors]
    all_percentage_errors = [e[1] for sat_errors in errors.values() for e in sat_errors]
    if all_total_errors:
        print("\n整体统计：")
        print(f"  平均百分差: {sum(all_percentage_errors)/len(all_percentage_errors):.4f}%")
        print(f"  最大百分差: {max(all_percentage_errors):.4f}%")
        print(f"  最小百分差: {min(all_percentage_errors):.4f}%")
        print(f"  标准差百分差: {math.sqrt(sum((e - sum(all_percentage_errors)/len(all_percentage_errors))**2 for e in all_percentage_errors)/len(all_percentage_errors)):.4f}%")

if __name__ == '__main__':
    main()
