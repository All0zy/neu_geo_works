import numpy as np
from datetime import datetime

np.set_printoptions(threshold=np.inf)

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

    # 读取接收机和天线信息
    for content in lines:
        if "REC #" in content:
            parts = content.split()
            data['receiver_number'] = parts[0]
            data['receiver_type'] = parts[1]
            data['receiver_version'] = parts[2]
        elif "ANT #" in content:
            parts = content.split()
            data['antenna_number'] = parts[0]
            data['antenna_type'] = parts[1]

    # 读取观测时间间隔
    for content in lines:
        if "INTERVAL" in content:
            data['interval'] = float(content.split()[0])
            break

    # 读取观测历元时间
    for content in lines:
        if "TIME OF OBS" in content:
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
                parts = lines[i].split()
                if parts[0].startswith('G'):  # 只保留以"G"开头的卫星数据
                    try:
                        observation_epoch['observations'].append({
                            'satellite': parts[0],
                            'pseudo_range': float(parts[1]),
                            'carrier_phase': float(parts[2]),
                            'doppler': float(parts[3]),
                            'signal_strength': float(parts[4])
                        })
                    except ValueError:
                        continue
            if observation_epoch['observations']:  # 只添加有观测数据的历元
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
    r"C:\Users\15338\Desktop\pythonProject\WUH200CHN_R_20250270000_01D_30S_MO.rnx",
    r"C:\Users\15338\Desktop\pythonProject\station2.txt"
)
