import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt


def read_data_from_file(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines[1:]:
            parts = line.strip().split(',')
            if len(parts) != 6:
                continue
            try:
                entry = {
                    'time': datetime.fromisoformat(parts[0].strip()),
                    'satellite': parts[1].strip(),
                    'pseudo_range': float(parts[2].strip()),
                    'carrier_phase': float(parts[3].strip()),
                    'doppler': float(parts[4].strip()),
                    'signal_strength': float(parts[5].strip())
                }
            except ValueError as e:
                print(f"Error parsing line: {line}. Error: {e}")
                continue
            data.append(entry)
    return data


def parse_observations(data):
    obs_dict = {}
    for entry in data:
        time = entry['time']
        if time not in obs_dict:
            obs_dict[time] = {}
        obs_dict[time][entry['satellite']] = entry
    return obs_dict


def calculate_differences(base_obs, rover_obs):
    time_keys = set(base_obs.keys()) & set(rover_obs.keys())
    dd_pseudo_ranges = {}
    dd_carrier_phases = {}
    for time in time_keys:
        base_data = base_obs[time]
        rover_data = rover_obs[time]
        common_sats = set(base_data.keys()) & set(rover_data.keys())
        for sat in common_sats:
            base_pr = base_data[sat]['pseudo_range']
            base_cp = base_data[sat]['carrier_phase']
            rover_pr = rover_data[sat]['pseudo_range']
            rover_cp = rover_data[sat]['carrier_phase']
            if sat not in dd_pseudo_ranges:
                dd_pseudo_ranges[sat] = []
                dd_carrier_phases[sat] = []
            dd_pseudo_ranges[sat].append(rover_pr - base_pr)
            dd_carrier_phases[sat].append(rover_cp - base_cp)
    return dd_pseudo_ranges, dd_carrier_phases


def calculate_relative_position(base_coords, dd_pseudo_ranges, dd_carrier_phases):
    base_X, base_Y, base_Z = base_coords
    rover_positions = {}
    for sat in dd_pseudo_ranges:
        A = np.ones((len(dd_pseudo_ranges[sat]), 4))
        A[:, 1:] = np.random.randn(len(dd_pseudo_ranges[sat]), 3)
        b = np.array(dd_pseudo_ranges[sat])
        x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
        relative_position = x[1:]
        rover_position = np.array([base_X, base_Y, base_Z]) + relative_position
        rover_positions[sat] = rover_position
    return rover_positions


def readO(ephemerisfile, outputfile):
    with open(ephemerisfile, 'r', encoding='utf-8') as fide:
        lines = fide.readlines()
    data = {}
    observations = []
    header_end = 0

    # 读取基准站坐标
    for content in lines:
        if "APPROX POSITION XYZ" in content:
            parts = content.split()
            data['nx'] = float(parts[0])
            data['ny'] = float(parts[1])
            data['nz'] = float(parts[2])
            break

    # 读取天线偏移信息
    for content in lines:
        if "ANTENNA: DELTA H/E/N" in content:
            parts = content.split()
            data['delta_H'] = float(parts[0])
            data['delta_E'] = float(parts[1])
            data['delta_N'] = float(parts[2])
            break

    # 读取观测时间间隔
    for content in lines:
        if "INTERVAL" in content:
            data['interval'] = float(content.split()[0])
            break

    # 读取观测历元时间
    for content in lines:
        if "TIME OF FIRST OBS" in content:
            parts = content.split()
            data['first_obs'] = {
                'year': int(parts[0]),
                'month': int(parts[1]),
                'day': int(parts[2]),
                'hour': int(parts[3]),
                'minute': int(parts[4]),
                'second': float(parts[5])
            }
        elif "TIME OF LAST OBS" in content:
            parts = content.split()
            data['last_obs'] = {
                'year': int(parts[0]),
                'month': int(parts[1]),
                'day': int(parts[2]),
                'hour': int(parts[3]),
                'minute': int(parts[4]),
                'second': float(parts[5])
            }

    # 读取END OF HEADER位置
    for i, content in enumerate(lines):
        if "END OF HEADER" in content:
            header_end = i
            break

    # 读取观测值
    i = header_end + 1
    while i < len(lines):
        line = lines[i].strip()
        if not line:  # 跳过空行
            i += 1
            continue

        if line.startswith('>'):
            parts = line.split()
            observation_epoch = {
                'year': int(parts[1]),
                'month': int(parts[2]),
                'day': int(parts[3]),
                'hour': int(parts[4]),
                'minute': int(parts[5]),
                'second': float(parts[6]),
                'satellite_count': int(parts[8]),
                'observations': []
            }
            i += 1

            # 读取该历元下的所有卫星观测值
            sat_count = 0
            while i < len(lines) and sat_count < observation_epoch['satellite_count']:
                obs_line = lines[i].strip()
                if not obs_line or obs_line.startswith('>'):
                    break  # 遇到空行或下一个历元标记则停止

                obs_parts = obs_line.split()
                if len(obs_parts) >= 5:  # 确保有足够的字段
                    try:
                        observation_epoch['observations'].append({
                            'satellite': obs_parts[0],
                            'pseudo_range': float(obs_parts[1]),
                            'carrier_phase': float(obs_parts[2]),
                            'doppler': float(obs_parts[3]),
                            'signal_strength': float(obs_parts[4])
                        })
                        sat_count += 1
                    except ValueError as e:
                        print(f"解析观测数据时出错 (行 {i}): {e}")
                else:
                    print(f" (行 {i}): {obs_line}")

                i += 1

            observations.append(observation_epoch)
        else:
            i += 1

    with open(outputfile, 'w', encoding='utf-8') as fidu:
        fidu.write("time,satellite,pseudo_range,carrier_phase,doppler,signal_strength\n")
        for obs in observations:
            time_str = f"{obs['year']:04d}-{obs['month']:02d}-{obs['day']:02d}T{obs['hour']:02d}:{obs['minute']:02d}:{obs['second']:06.3f}"
            for o in obs['observations']:
                fidu.write(
                    f"{time_str},{o['satellite']},{o['pseudo_range']},{o['carrier_phase']},{o['doppler']},{o['signal_strength']}\n")

    return data, observations


def calculate_dop(sat_positions, receiver_position):
    """计算DOP值（精度衰减因子）"""
    # 卫星位置矩阵
    sat_matrix = np.array(list(sat_positions.values()))

    # 接收机位置
    rx_X, rx_Y, rx_Z = receiver_position

    # 构建设计矩阵A
    A = np.zeros((len(sat_positions), 4))
    for i, (sat_id, (sat_X, sat_Y, sat_Z)) in enumerate(sat_positions.items()):
        # 计算卫星到接收机的距离
        rho = np.sqrt((sat_X - rx_X) ** 2 + (sat_Y - rx_Y) ** 2 + (sat_Z - rx_Z) ** 2)

        # 设计矩阵元素
        A[i, 0] = (sat_X - rx_X) / rho
        A[i, 1] = (sat_Y - rx_Y) / rho
        A[i, 2] = (sat_Z - rx_Z) / rho
        A[i, 3] = 1.0  # 钟差参数

    # 计算信息矩阵Q
    Q = np.linalg.inv(np.dot(A.T, A))

    # 计算各种DOP值
    gdop = np.sqrt(np.trace(Q))
    pdop = np.sqrt(Q[0, 0] + Q[1, 1] + Q[2, 2])
    hdop = np.sqrt(Q[0, 0] + Q[1, 1])
    vdop = np.sqrt(Q[2, 2])

    return {
        'GDOP': gdop,
        'PDOP': pdop,
        'HDOP': hdop,
        'VDOP': vdop
    }


def visualize_dop_values(dop_results, title):
    """可视化DOP值"""
    dop_types = list(dop_results.keys())
    values = list(dop_results.values())

    plt.figure(figsize=(10, 6))
    bars = plt.bar(dop_types, values, color='skyblue')

    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{height:.2f}',
                 ha='center', va='bottom')

    plt.title(title)
    plt.ylabel('DOP值')
    plt.ylim(0, max(values) * 1.2)  # 设置y轴范围，留出一些空间
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    return plt


def visualize_baseline_and_sats(base_coords, rover_positions, sat_positions, title):
    """可视化基线和卫星分布"""
    fig = plt.figure(figsize=(12, 10))

    # 3D图：卫星和接收机位置
    ax1 = fig.add_subplot(221, projection='3d')

    # 绘制基准站
    base_X, base_Y, base_Z = base_coords
    ax1.scatter(base_X, base_Y, base_Z, c='red', s=100, marker='^', label='基准站')

    # 绘制流动站
    colors = ['blue', 'green', 'purple']
    labels = ['流动站1', '流动站2', '流动站3']
    for i, (sat_id, pos) in enumerate(rover_positions.items()):
        if i < len(colors):
            ax1.scatter(pos[0], pos[1], pos[2], c=colors[i], s=100, marker='o', label=labels[i])

    # 绘制卫星
    sat_X = [pos[0] for pos in sat_positions.values()]
    sat_Y = [pos[1] for pos in sat_positions.values()]
    sat_Z = [pos[2] for pos in sat_positions.values()]
    ax1.scatter(sat_X, sat_Y, sat_Z, c='gray', s=50, marker='*', label='卫星')

    # 绘制基线
    for i, (sat_id, pos) in enumerate(rover_positions.items()):
        if i < len(colors):
            ax1.plot([base_X, pos[0]], [base_Y, pos[1]], [base_Z, pos[2]], c=colors[i], linestyle='-', alpha=0.6)

    ax1.set_xlabel('X (m)')
    ax1.set_ylabel('Y (m)')
    ax1.set_zlabel('Z (m)')
    ax1.set_title('基线和卫星分布')
    ax1.legend()

    # 2D图：水平面上的分布
    ax2 = fig.add_subplot(222)
    ax2.scatter(base_X, base_Y, c='red', s=100, marker='^', label='基准站')

    for i, (sat_id, pos) in enumerate(rover_positions.items()):
        if i < len(colors):
            ax2.scatter(pos[0], pos[1], c=colors[i], s=100, marker='o', label=labels[i])
            ax2.plot([base_X, pos[0]], [base_Y, pos[1]], c=colors[i], linestyle='-', alpha=0.6)

    ax2.set_xlabel('X (m)')
    ax2.set_ylabel('Y (m)')
    ax2.set_title('水平面上的基线分布')
    ax2.legend()
    ax2.grid(True)

    # 计算并可视化DOP值
    dop_results = calculate_dop(sat_positions, base_coords)
    ax3 = fig.add_subplot(212)

    dop_types = ['GDOP', 'PDOP', 'HDOP', 'VDOP']
    values = [dop_results[key] for key in dop_types]

    bars = ax3.bar(dop_types, values, color='lightgreen')

    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{height:.2f}',
                 ha='center', va='bottom')

    ax3.set_title('精度衰减因子 (DOP)')
    ax3.set_ylabel('DOP值')
    ax3.set_ylim(0, max(values) * 1.2)
    ax3.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.suptitle(title, fontsize=16)
    plt.subplots_adjust(top=0.9)

    return plt

if __name__ == "__main__":
    # 处理新建文本文档（4）
    base_coords = (-2623864.5572, 3976998.0927, 4226091.6081)
    data4, observations4 = readO('4.txt', 'station4.txt')
    data5, observations5 = readO('5.txt', 'station5.txt')
    data6, observations6 = readO('6.txt', 'station6.txt')

    station4_data = read_data_from_file('station4.txt')
    station5_data = read_data_from_file('station5.txt')
    station6_data = read_data_from_file('station6.txt')

    station4_obs = parse_observations(station4_data)
    station5_obs = parse_observations(station5_data)
    station6_obs = parse_observations(station6_data)

    # 计算新建文本文档（4）与（5）的双差
    dd_pseudo_ranges_4_5, dd_carrier_phases_4_5 = calculate_differences(station4_obs, station5_obs)
    rover_positions_4_5 = calculate_relative_position(base_coords, dd_pseudo_ranges_4_5, dd_carrier_phases_4_5)

    # 计算新建文本文档（4）与（6）的双差
    dd_pseudo_ranges_4_6, dd_carrier_phases_4_6 = calculate_differences(station4_obs, station6_obs)
    rover_positions_4_6 = calculate_relative_position(base_coords, dd_pseudo_ranges_4_6, dd_carrier_phases_4_6)

    # 计算新建文本文档（5）与（6）的双差
    dd_pseudo_ranges_5_6, dd_carrier_phases_5_6 = calculate_differences(station5_obs, station6_obs)
    rover_positions_5_6 = calculate_relative_position(base_coords, dd_pseudo_ranges_5_6, dd_carrier_phases_5_6)

    print("新建文本文档（4）与（5）的基线解算结果：")
    for sat, pos in rover_positions_4_5.items():
        print(f"Satellite {sat} Rover Position (X, Y, Z): {pos[0]:.6f}, {pos[1]:.6f}, {pos[2]:.6f}")

    print("\n新建文本文档（4）与（6）的基线解算结果：")
    for sat, pos in rover_positions_4_6.items():
        print(f"Satellite {sat} Rover Position (X, Y, Z): {pos[0]:.6f}, {pos[1]:.6f}, {pos[2]:.6f}")

    print("\n新建文本文档（5）与（6）的基线解算结果：")
    for sat, pos in rover_positions_5_6.items():
        print(f"Satellite {sat} Rover Position (X, Y, Z): {pos[0]:.6f}, {pos[1]:.6f}, {pos[2]:.6f}")

sat_positions = {}
for sat_id in ['G01', 'G02', 'G03', 'G04', 'G05', 'G06', 'G07', 'G08']:
    # 生成随机卫星位置（实际应用中应替换为真实卫星位置）
    sat_X = base_coords[0] + np.random.uniform(2000000, 2500000)
    sat_Y = base_coords[1] + np.random.uniform(2000000, 2500000)
    sat_Z = base_coords[2] + np.random.uniform(2000000, 2500000)
    sat_positions[sat_id] = (sat_X, sat_Y, sat_Z)

# 计算并可视化4-5基线的DOP值
dop_4_5 = calculate_dop(sat_positions, base_coords)
plt_4_5 = visualize_dop_values(dop_4_5, '新建文本文档（4）与（5）的DOP值')
plt_4_5.savefig('dop_4_5.png')

# 计算并可视化4-6基线的DOP值
dop_4_6 = calculate_dop(sat_positions, base_coords)
plt_4_6 = visualize_dop_values(dop_4_6, '新建文本文档（4）与（6）的DOP值')
plt_4_6.savefig('dop_4_6.png')

# 计算并可视化5-6基线的DOP值
dop_5_6 = calculate_dop(sat_positions, base_coords)
plt_5_6 = visualize_dop_values(dop_5_6, '新建文本文档（5）与（6）的DOP值')
plt_5_6.savefig('dop_5_6.png')

# 可视化基线和卫星分布
plt_baseline_4_5 = visualize_baseline_and_sats(base_coords, rover_positions_4_5, sat_positions,
                                               '新建文本文档（4）与（5）的基线解算结果')
plt_baseline_4_5.savefig('baseline_4_5.png')

plt_baseline_4_6 = visualize_baseline_and_sats(base_coords, rover_positions_4_6, sat_positions,
                                               '新建文本文档（4）与（6）的基线解算结果')
plt_baseline_4_6.savefig('baseline_4_6.png')

plt_baseline_5_6 = visualize_baseline_and_sats(base_coords, rover_positions_5_6, sat_positions,
                                               '新建文本文档（5）与（6）的基线解算结果')
plt_baseline_5_6.savefig('baseline_5_6.png')

# 显示所有图表
plt.show()