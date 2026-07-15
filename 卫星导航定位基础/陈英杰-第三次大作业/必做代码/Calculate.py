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

if __name__ == "__main__":
    base_coords = (-2267796.9641, 5009421.6975, 3220952.5436)
    base_station_data = read_data_from_file('station1.txt')
    rover_station_data = read_data_from_file('station2.txt')

    base_obs = parse_observations(base_station_data)
    rover_obs = parse_observations(rover_station_data)

    dd_pseudo_ranges, dd_carrier_phases = calculate_differences(base_obs, rover_obs)

    rover_positions = calculate_relative_position(base_coords, dd_pseudo_ranges, dd_carrier_phases)

    for sat, pos in rover_positions.items():
        print(f"Satellite {sat} Rover Position (X, Y, Z): {pos[0]:.6f}, {pos[1]:.6f}, {pos[2]:.6f}")
