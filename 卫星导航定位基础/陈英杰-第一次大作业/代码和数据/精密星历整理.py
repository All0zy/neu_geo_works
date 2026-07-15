import re

def parse_precise_eph(file_path):
    """解析精密星历文件，提取北斗卫星位置并保留24小时时刻"""
    precise_data = {}
    current_time = 0  # 使用时间点索引作为标识
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 检测时间点分隔符（以*开头的行）
            if line.startswith('*'):
                current_time += 1
            # 匹配PC开头的北斗卫星行
            if re.match(r'^PC\d{2}', line):
                parts = line.split()
                sat_id = parts[0].replace('PC', 'C')  # 统一为C开头
                # 提取前三个坐标并转换单位（千米→米）
                x = float(parts[1]) * 1000
                y = float(parts[2]) * 1000
                z = float(parts[3]) * 1000
                # 存储数据（仅保留24小时时刻）
                if current_time % 12 == 1:  # 每小时第一个时间点（5分钟间隔的第1个点）
                    if sat_id not in precise_data:
                        precise_data[sat_id] = []
                    precise_data[sat_id].append((x, y, z))
    return precise_data

def save_eph_data(data, output_file):
    """保存数据为指定格式"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for sat_id in sorted(data.keys()):
            for coords in data[sat_id]:
                f.write(f"{sat_id},{coords[0]},{coords[1]},{coords[2]}\n")

if __name__ == "__main__":
    # 解析精密星历文件并提取24小时时刻
    precise_data = parse_precise_eph('精密星历.SP3')
    
    # 保存为指定格式
    save_eph_data(precise_data, '坐标.txt')
    
    print("精密星历数据已转换为24小时时刻，保存为 坐标.txt")
    print("文件格式与广播星历文件一致：")
    print("卫星ID,X坐标,Y坐标,Z坐标（单位：米）")
    print("包含24个时间点（每小时一个点）")