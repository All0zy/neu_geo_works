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
        ambiguity_precisions[sat] = ambiguity_precision

    # 修改返回值，返回 4 个变量
    return rover_positions, ambiguity_solutions, gdop_values, ambiguity_precisions


# 修改函数，使其接受基准站坐标
def write_results_to_file(rover_positions, third_positions, ambiguity_solutions_rover, ambiguity_solutions_third, gdop_values_rover, gdop_values_third, ambiguity_precisions_rover, ambiguity_precisions_third, base_coords):
    output_file = "./output/net_results.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        # 使用新的表头
        f.write("satelite,Base_X,Base_Y,Base_Z,rover_x,rover_y,rover_z,rover2_x,rover2_y,rover2_z,Integer Ambiguity Rover,Integer Ambiguity Rover2,GDOP Rover,GDOP Rover2,Ambiguity Precision Rover,Ambiguity Precision Rover2\n")
        common_sats = set(rover_positions.keys()) | set(third_positions.keys())
        base_X, base_Y, base_Z = base_coords
        for sat in common_sats:
            rover_pos = rover_positions.get(sat, [0, 0, 0])
            third_pos = third_positions.get(sat, [0, 0, 0])
            
            if any(coord == 0 for coord in rover_pos) or any(coord == 0 for coord in third_pos):
                continue
            
            ambiguity_rover = ambiguity_solutions_rover.get(sat, [0])[0]
            ambiguity_third = ambiguity_solutions_third.get(sat, [0])[0]
            gdop_rover = gdop_values_rover.get(sat, 0)
            gdop_third = gdop_values_third.get(sat, 0)
            ambiguity_precision_rover = ambiguity_precisions_rover.get(sat, 0)
            ambiguity_precision_third = ambiguity_precisions_third.get(sat, 0)

            rover_pos_str = f"{rover_pos[0]:.6f},{rover_pos[1]:.6f},{rover_pos[2]:.6f}"
            third_pos_str = f"{third_pos[0]:.6f},{third_pos[1]:.6f},{third_pos[2]:.6f}"
            base_pos_str = f"{base_X:.6f},{base_Y:.6f},{base_Z:.6f}"
            f.write(f"{sat},{base_pos_str},{rover_pos_str},{third_pos_str},{ambiguity_rover},{ambiguity_third},{gdop_rover:.6f},{gdop_third:.6f},{ambiguity_precision_rover:.6f},{ambiguity_precision_third:.6f}\n")


def calculate_average_positions(rover_positions, third_positions, base_coords):
    """
    计算三个站坐标的平均值。

    :param rover_positions: 流动站 rover 的坐标
    :param third_positions: 流动站 rover2 的坐标
    :param base_coords: 基准站的坐标
    :return: 三个站各自坐标的平均值
    """
    rover_coords = np.array(list(rover_positions.values()))
    third_coords = np.array(list(third_positions.values()))
    base_coords_arr = np.array([base_coords] * len(rover_coords))  # 使基准站坐标数量与流动站一致

    avg_rover = np.mean(rover_coords, axis=0)
    avg_third = np.mean(third_coords, axis=0)
    avg_base = np.mean(base_coords_arr, axis=0)

    return avg_base, avg_rover, avg_third


def write_average_results_to_file(avg_base, avg_rover, avg_third):
    """
    将三个站坐标的平均值写入文件。

    :param avg_base: 基准站坐标的平均值
    :param avg_rover: 流动站 rover 坐标的平均值
    :param avg_third: 流动站 rover2 坐标的平均值
    """
    output_file = "./output/average_results.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Station,X_Avg,Y_Avg,Z_Avg\n")
        f.write(f"Base,{avg_base[0]:.6f},{avg_base[1]:.6f},{avg_base[2]:.6f}\n")
        f.write(f"Rover,{avg_rover[0]:.6f},{avg_rover[1]:.6f},{avg_rover[2]:.6f}\n")
        f.write(f"Rover2,{avg_third[0]:.6f},{avg_third[1]:.6f},{avg_third[2]:.6f}\n")

if __name__ == "__main__":
    base_coords = (-2267796.9641, 5009421.6975, 3220952.5436)
    base_station_data = read_data_from_file('./output/base_station.txt')
    rover_station_data = read_data_from_file('./output/rover_station.txt')
    third_station_data = read_data_from_file('./output/rover2_station.txt')

    base_obs = parse_observations(base_station_data)
    rover_obs = parse_observations(rover_station_data)
    third_obs = parse_observations(third_station_data)

    # 计算 rover 与 base 的双差
    dd_pseudo_ranges_rover_base, dd_carrier_phases_rover_base = calculate_differences(base_obs, rover_obs)
    # 计算 third 与 base 的双差
    dd_pseudo_ranges_third_base, dd_carrier_phases_third_base = calculate_differences(base_obs, third_obs)

    # 计算 rover 点位置
    rover_positions, ambiguity_solutions_rover, gdop_values_rover, ambiguity_precisions_rover = calculate_relative_position(base_coords, dd_pseudo_ranges_rover_base, dd_carrier_phases_rover_base)
    # 计算 third 点位置
    third_positions, ambiguity_solutions_third, gdop_values_third, ambiguity_precisions_third = calculate_relative_position(base_coords, dd_pseudo_ranges_third_base, dd_carrier_phases_third_base)

    # 写入结果文件，传入基准站坐标
    write_results_to_file(rover_positions, third_positions, ambiguity_solutions_rover, ambiguity_solutions_third, gdop_values_rover, gdop_values_third, ambiguity_precisions_rover, ambiguity_precisions_third, base_coords)

    # 计算三个站坐标的平均值
    avg_base, avg_rover, avg_third = calculate_average_positions(rover_positions, third_positions, base_coords)
    # 将平均值写入新文件
    write_average_results_to_file(avg_base, avg_rover, avg_third)