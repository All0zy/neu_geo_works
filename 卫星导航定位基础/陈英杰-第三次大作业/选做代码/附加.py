import numpy as np
from datetime import datetime


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


if __name__ == "__main__":
    # 处理新建文本文档（4）
    base_coords = (-2623864.5572, 3976998.0927, 4226091.6081)
    data1, observations1 = readO('1.txt', 'station1.txt')
    data2, observations2 = readO('2.txt', 'station2.txt')
    data3, observations3 = readO('3.txt', 'station3.txt')

    station1_data = read_data_from_file('station1.txt')
    station2_data = read_data_from_file('station2.txt')
    station3_data = read_data_from_file('station3.txt')

    station1_obs = parse_observations(station1_data)
    station2_obs = parse_observations(station2_data)
    station3_obs = parse_observations(station3_data)

    # 计算新建文本文档（1）与（2）的双差
    dd_pseudo_ranges_1_2, dd_carrier_phases_1_2 = calculate_differences(station1_obs, station2_obs)
    rover_positions_1_2 = calculate_relative_position(base_coords, dd_pseudo_ranges_1_2, dd_carrier_phases_1_2)

    # 计算新建文本文档（1）与（3）的双差
    dd_pseudo_ranges_1_3, dd_carrier_phases_1_3 = calculate_differences(station1_obs, station3_obs)
    rover_positions_1_3 = calculate_relative_position(base_coords, dd_pseudo_ranges_1_3, dd_carrier_phases_1_3)

    # 计算新建文本文档（2）与（3）的双差
    dd_pseudo_ranges_2_3, dd_carrier_phases_2_3 = calculate_differences(station2_obs, station3_obs)
    rover_positions_2_3 = calculate_relative_position(base_coords, dd_pseudo_ranges_2_3, dd_carrier_phases_2_3)

    print("新建文本文档（1）与（2）的基线解算结果：")
    for sat, pos in rover_positions_1_2.items():
        print(f"Satellite {sat} Rover Position (X, Y, Z): {pos[0]:.6f}, {pos[1]:.6f}, {pos[2]:.6f}")

    print("\n新建文本文档（1）与（3）的基线解算结果：")
    for sat, pos in rover_positions_1_3.items():
        print(f"Satellite {sat} Rover Position (X, Y, Z): {pos[0]:.6f}, {pos[1]:.6f}, {pos[2]:.6f}")

    print("\n新建文本文档（2）与（3）的基线解算结果：")
    for sat, pos in rover_positions_2_3.items():
        print(f"Satellite {sat} Rover Position (X, Y, Z): {pos[0]:.6f}, {pos[1]:.6f}, {pos[2]:.6f}")