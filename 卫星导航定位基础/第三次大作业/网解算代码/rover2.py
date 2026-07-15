import numpy as np
from datetime import datetime

np.set_printoptions(threshold=np.inf)

def readO(ephemerisfile, outputfile):
    with open(ephemerisfile, 'r', encoding='utf-8') as fide:
        lines = fide.readlines()

    data = {}
    observations = []
    header_end = 0

    # 检查RINEX版本
    for content in lines:
        if "RINEX VERSION / TYPE" in content:
            version = float(content[:9].strip())
            if version < 3.04:
                print("Warning: 文件版本低于3.04，可能存在兼容性问题。")
            break

    # 读取基准站坐标
    for content in lines:
        if "APPROX POSITION XYZ" in content:
            parts = content[0:42].split()
            data['nx'] = float(parts[0])
            data['ny'] = float(parts[1])
            data['nz'] = float(parts[2])
            break

    # 读取天线偏移信息
    for content in lines:
        if "ANTENNA: DELTA H/E/N" in content:
            parts = content[0:42].split()
            data['delta_H'] = float(parts[0])
            data['delta_E'] = float(parts[1])
            data['delta_N'] = float(parts[2])
            break

    # 读取观测时间间隔
    for content in lines:
        if "INTERVAL" in content:
            parts = content[0:10].split()
            data['interval'] = float(parts[0])
            break

    # 读取观测历元时间
    for content in lines:
        if "TIME OF FIRST OBS" in content:
            parts = content[0:42].split()
            data['first_obs'] = {
                'year': int(parts[0]),
                'month': int(parts[1]),
                'day': int(parts[2]),
                'hour': int(parts[3]),
                'minute': int(parts[4]),
                'second': float(parts[5])
            }
        elif "TIME OF LAST OBS" in content:
            parts = content[0:42].split()
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
    for i in range(header_end + 1, len(lines)):
        if lines[i].startswith('>'):
            parts = lines[i].split()
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
            for _ in range(observation_epoch['satellite_count']):
                i += 1
                line = lines[i].strip()
                satellite = line[:3]
                data_fields = line[3:].split()
                if len(data_fields) >= 4:
                    raw_carrier_phase = data_fields[1]
                    raw_signal_strength = data_fields[3]
                    carrier_phase = float(data_fields[1])
                    signal_strength = float(data_fields[3])
                    observation_epoch['observations'].append({
                        'satellite': satellite,
                        'pseudo_range': float(data_fields[0]),
                        'carrier_phase': carrier_phase,
                        'doppler': float(data_fields[2]),
                        'signal_strength': signal_strength
                    })
            observations.append(observation_epoch)

    with open(outputfile, 'w', encoding='utf-8') as fidu:
        fidu.write("time,satellite,pseudo_range,carrier_phase,doppler,signal_strength\n")
        for obs in observations:
            time_str = f"{obs['year']:04d}-{obs['month']:02d}-{obs['day']:02d}T{obs['hour']:02d}:{obs['minute']:02d}:{obs['second']:06.3f}"
            for o in obs['observations']:
                fidu.write(f"{time_str},{o['satellite']},{o['pseudo_range']},{o['carrier_phase']},{o['doppler']},{o['signal_strength']}\n")

    return data, observations

# 调用函数
data, observations = readO(
    "./input/33331001.25o",
    "./output/rover2_station.txt"
)