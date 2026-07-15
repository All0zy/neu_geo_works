import numpy as np
from datetime import datetime
import os

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

def lambda_algorithm(float_solution, covariance_matrix):
    """
    LAMBDA 算法实现，用于计算整周模糊度。

    :param float_solution: 浮点解
    :param covariance_matrix: 协方差矩阵
    :return: 整数解
    """
    # 整数最小二乘降相关
    L, D = np.linalg.cholesky(covariance_matrix).T, np.diag(np.diag(np.linalg.cholesky(covariance_matrix)))
    Z = np.eye(len(float_solution))
    for k in range(len(float_solution) - 1, 0, -1):
        for j in range(k - 1, -1, -1):
            mu = np.round(L[k, j] / L[j, j])
            if mu != 0:
                Z[:, j] -= mu * Z[:, k]
                L[k, j] -= mu * L[j, j]

    # 变换浮点解
    y = np.linalg.solve(Z.T, float_solution)

    # 整数舍入
    z = np.round(y)
    # 逆变换
    N = np.dot(Z, z)
    return N

def write_baseline_results(output_file, rover_positions, ambiguity_solutions, gdop_values, ambiguity_precisions, base_coords):
    base_X, base_Y, base_Z = base_coords
    # 检查输出目录是否存在，不存在则创建
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # 修改首行内容为指定格式
            f.write("satelite,Base_X,Base_Y,Base_Z,rover_x,rover_y,rover_z,Integer Ambiguity,GDOP,Ambiguity Precision\n")
            for sat in rover_positions:
                pos = rover_positions[sat]
                ambiguity = ambiguity_solutions[sat][0]
                gdop = gdop_values[sat]
                ambiguity_precision = ambiguity_precisions[sat]
                pos_str = f"{pos[0]:.6f},{pos[1]:.6f},{pos[2]:.6f}"
                # 在每行数据中添加基准站坐标
                f.write(f"{sat},{base_X:.6f},{base_Y:.6f},{base_Z:.6f},{pos_str},{ambiguity},{gdop:.6f},{ambiguity_precision:.6f}\n")
            # 移除原有的追加基准站坐标行
    except Exception as e:
        print(f"写入文件时出错: {e}")

def calculate_relative_position(base_coords, dd_pseudo_ranges, dd_carrier_phases):
    base_X, base_Y, base_Z = base_coords
    rover_positions = {}
    ambiguity_solutions = {}
    gdop_values = {}
    ambiguity_precisions = {}
    for sat in dd_pseudo_ranges:
        A = np.ones((len(dd_pseudo_ranges[sat]), 4))
        A[:, 1:] = np.random.randn(len(dd_pseudo_ranges[sat]), 3)
        b = np.array(dd_pseudo_ranges[sat])
        x = np.linalg.lstsq(A, b, rcond=None)[0]  # 只取需要的解
        relative_position = x[1:]
        rover_position = np.array([base_X, base_Y, base_Z]) + relative_position
        rover_positions[sat] = rover_position

        # 计算 GDOP
        Q = np.linalg.inv(np.dot(A.T, A))
        gdop = np.sqrt(np.trace(Q))
        gdop_values[sat] = gdop

        # 调整 A_ambiguity 矩阵维度，只求解一个整周模糊度
        A_ambiguity = np.ones((len(dd_carrier_phases[sat]), 1))  # 仅一列，对应一个整周模糊度
        b_ambiguity = np.array(dd_carrier_phases[sat])
        float_solution = np.linalg.lstsq(A_ambiguity, b_ambiguity, rcond=None)[0]  # 只取需要的解
        # 计算协方差矩阵
        covariance_matrix = np.linalg.inv(np.dot(A_ambiguity.T, A_ambiguity))

        integer_solution = lambda_algorithm(float_solution, covariance_matrix)
        # 确保整周模糊度为正数
        integer_solution = np.abs(integer_solution)
        ambiguity_solutions[sat] = integer_solution

        # 计算整周模糊度精度
        ambiguity_precision = np.sqrt(covariance_matrix[0][0])
        ambiguity_precision = np.sqrt(covariance_matrix[0][0])
        ambiguity_precisions[sat] = ambiguity_precision

    # 将结果写入文件
    output_file = "./output/baseline_results.txt"
    write_baseline_results(output_file, rover_positions, ambiguity_solutions, gdop_values, ambiguity_precisions, base_coords)

    # 计算流动站平均坐标
    rover_positions_array = np.array(list(rover_positions.values()))
    rover_avg_x = np.mean(rover_positions_array[:, 0])
    rover_avg_y = np.mean(rover_positions_array[:, 1])
    rover_avg_z = np.mean(rover_positions_array[:, 2])

    # 输出平均坐标到新文件
    output_avg_file = "./output/average_coords.txt"
    write_average_coords(output_avg_file, base_coords, (rover_avg_x, rover_avg_y, rover_avg_z))

    return rover_positions

def write_average_coords(output_file, base_coords, rover_avg_coords):
    base_X, base_Y, base_Z = base_coords
    rover_avg_x, rover_avg_y, rover_avg_z = rover_avg_coords
    # 检查输出目录是否存在，不存在则创建
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Station Type,X,Y,Z\n")
            f.write(f"Base Station,{base_X:.6f},{base_Y:.6f},{base_Z:.6f}\n")
            f.write(f"Rover Station,{rover_avg_x:.6f},{rover_avg_y:.6f},{rover_avg_z:.6f}\n")
    except Exception as e:
        print(f"写入平均坐标文件时出错: {e}")

if __name__ == "__main__":
    base_coords = (-2267796.9641, 5009421.6975, 3220952.5436)
    # 输出基准站坐标到控制台
    print(f"基准站坐标: {base_coords}")
    base_station_data = read_data_from_file('./output/base_station.txt')
    rover_station_data = read_data_from_file('./output/rover_station.txt')

    base_obs = parse_observations(base_station_data)
    rover_obs = parse_observations(rover_station_data)

    dd_pseudo_ranges, dd_carrier_phases = calculate_differences(base_obs, rover_obs)

    rover_positions = calculate_relative_position(base_coords, dd_pseudo_ranges, dd_carrier_phases)