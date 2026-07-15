import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
from sklearn.metrics import mean_squared_error
import logging
import re
import math
import os
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

def polynomial_model(x, *params):
    """简化的多项式模型函数"""
    x = np.atleast_2d(x)  # 确保x是二维数组
    lat, lon = x[:, 0], x[:, 1]

    # 简化为二次多项式模型
    result = params[0]  # 常数项
    result += params[1] * lat  # 一次项
    result += params[2] * lon
    result += params[3] * lat ** 2  # 二次项
    result += params[4] * lon ** 2
    result += params[5] * lat * lon  # 交叉项

    return result


def quality_control_mask(data, threshold=3):
    """生成数据过滤mask"""
    mean = np.mean(data)
    std = np.std(data)
    mask = np.abs(data - mean) <= threshold * std
    # 物理范围检查（电离层延迟通常在0-50米范围内）
    mask = mask & (data >= 0) & (data <= 50)
    return mask


def fit_ionospheric_model(ion_delays, positions, degree=2):
    """简化的模型拟合函数"""
    X = np.array(positions)
    y = np.array(ion_delays)

    # 数据标准化
    X_mean = np.mean(X, axis=0)
    X_std = np.std(X, axis=0)
    X_scaled = (X - X_mean) / X_std

    mask = quality_control_mask(y)
    X_cleaned = X_scaled[mask]
    y_cleaned = y[mask]

    # 使用6个参数的简化模型
    n_params = 6
    initial_params = np.zeros(n_params)
    initial_params[0] = np.mean(y_cleaned)  # 常数项初始化为均值

    try:
        params, _ = curve_fit(
            polynomial_model,
            X_cleaned,
            y_cleaned,
            p0=initial_params,
            maxfev=5000
        )

        # 计算R²
        y_pred = polynomial_model(X_cleaned, *params)
        r2 = 1 - np.sum((y_cleaned - y_pred) ** 2) / np.sum((y_cleaned - np.mean(y_cleaned)) ** 2)
        logging.info(f"模型拟合优度 R²: {r2:.4f}")

        return params, X_cleaned, y_cleaned, X_mean, X_std
    except Exception as e:
        logging.error(f"模型拟合失败: {str(e)}")
        return np.full(n_params, np.mean(y_cleaned)), X_cleaned, y_cleaned, X_mean, X_std


def validate_model(model_params, X, y, X_mean, X_std):
    """修改后的模型验证函数"""
    try:
        # 标准化输入数据
        X_scaled = (X - X_mean) / X_std

        # 预测
        y_pred = polynomial_model(X_scaled, *model_params)

        # 确保维度一致
        assert len(y_pred) == len(y), f"预测值维度 {len(y_pred)} 与真实值维度 {len(y)} 不匹配"

        # 计算评估指标
        mse = mean_squared_error(y, y_pred)
        rmse = np.sqrt(mse)
        bias = np.mean(y_pred - y)

        logging.info(f"模型评估指标:")
        logging.info(f"RMSE: {rmse:.4f} m")
        logging.info(f"Bias: {bias:.4f} m")

        return rmse, bias
    except Exception as e:
        logging.error(f"模型验证失败: {str(e)}")
        return float('inf'), float('inf')

def visualize_results(X, y, y_pred, model_params):
    """使用Plotly进行可视化"""
    # 创建子图
    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=(
            "预测值 vs 实际值",
            "残差分布",
            "模型参数重要性"
        )
    )

    # 1. 预测值 vs 实际值散点图
    fig.add_trace(
        go.Scatter(
            x=y,
            y=y_pred,
            mode='markers',
            name='数据点',
            marker=dict(
                size=8,
                opacity=0.5
            )
        ),
        row=1, col=1
    )

    # 添加对角线
    min_val = min(y.min(), y_pred.min())
    max_val = max(y.max(), y_pred.max())
    fig.add_trace(
        go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            name='理想拟合线',
            line=dict(color='red', dash='dash')
        ),
        row=1, col=1
    )

    # 2. 残差分布直方图
    residuals = y_pred - y
    fig.add_trace(
        go.Histogram(
            x=residuals,
            nbinsx=50,
            name='残差分布',
            showlegend=False
        ),
        row=1, col=2
    )

    # 3. 参数重要性条形图
    fig.add_trace(
        go.Bar(
            x=list(range(len(model_params))),
            y=np.abs(model_params),
            name='参数绝对值',
            showlegend=False
        ),
        row=1, col=3
    )

    # 更新布局
    fig.update_layout(
        title_text="电离层模型分析结果",
        title_x=0.5,
        showlegend=True,
        height=500,
        width=1500,
        template="plotly_white"
    )

    # 更新x轴和y轴标签
    fig.update_xaxes(title_text="实际值 (m)", row=1, col=1)
    fig.update_yaxes(title_text="预测值 (m)", row=1, col=1)
    fig.update_xaxes(title_text="残差 (m)", row=1, col=2)
    fig.update_xaxes(title_text="参数序号", row=1, col=3)
    fig.update_yaxes(title_text="参数绝对值", row=1, col=3)

    # 保存为HTML和PNG
    pio.write_html(fig, 'ionospheric_model_analysis.html')
    pio.write_image(fig, 'ionospheric_model_analysis.png', scale=2)

    # 显示图形（可选）
    fig.show()


def save_model(model_params, output_file):
    """保存模型参数"""
    with open(output_file, 'w') as f:
        f.write(f"模型生成时间: {datetime.now()}\n")
        f.write("模型参数:\n")
        for i, param in enumerate(model_params):
            f.write(f"系数 {i}: {param}\n")

def calculate_ionospheric_delay(obs_data, sat_pos, rec_pos):
    """计算电离层延迟"""
    try:
        if not rec_pos or len(rec_pos) < 3:
            logging.error("接收机位置数据无效")
            return None

        dx = sat_pos['x'] - rec_pos[0]
        dy = sat_pos['y'] - rec_pos[1]
        dz = sat_pos['z'] - rec_pos[2]
        distance = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

        f1 = 1575.42e6  # GPS L1频率 (Hz)
        f2 = 1227.60e6  # GPS L2频率 (Hz)
        c = 299792458.0  # 光速 (m/s)
        lambda1 = c / f1  # L1波长
        lambda2 = c / f2  # L2波长

        if 'L1' in obs_data and 'L2' in obs_data:
            try:
                l1_phase = obs_data['L1']
                l2_phase = obs_data['L2']
                ion_delay = (f2**2 / (f1**2 - f2**2)) * (lambda1 * l1_phase - lambda2 * l2_phase)
                logging.debug(f"使用L1和L2计算电离层延迟: L1={l1_phase}, L2={l2_phase}, delay={ion_delay}")
                return ion_delay
            except Exception as e:
                logging.error(f"使用L1和L2计算电离层延迟时出错: {str(e)}")
                logging.error(f"观测数据: {obs_data}")
                return None
        elif 'L1' in obs_data and 'P2' in obs_data:
            try:
                l1_phase = obs_data['L1']
                p2_code = obs_data['P2']
                ion_delay = (f2**2 / (f1**2 - f2**2)) * (lambda1 * l1_phase - p2_code)
                logging.debug(f"使用L1和P2计算电离层延迟: L1={l1_phase}, P2={p2_code}, delay={ion_delay}")
                return ion_delay
            except Exception as e:
                logging.error(f"使用L1和P2计算电离层延迟时出错: {str(e)}")
                logging.error(f"观测数据: {obs_data}")
                return None
        elif 'C1' in obs_data and 'P2' in obs_data:
            try:
                c1_code = obs_data['C1']
                p2_code = obs_data['P2']
                ion_delay = (f2**2 / (f1**2 - f2**2)) * (c1_code - p2_code)
                logging.debug(f"使用C1和P2计算电离层延迟: C1={c1_code}, P2={p2_code}, delay={ion_delay}")
                return ion_delay
            except Exception as e:
                logging.error(f"使用C1和P2计算电离层延迟时出错: {str(e)}")
                logging.error(f"观测数据: {obs_data}")
                return None
        else:
            logging.debug(f"缺少必要的观测值: {obs_data}")
            return None
    except Exception as e:
        logging.error(f"计算电离层延迟时出错: {str(e)}")
        logging.error(f"观测数据: {obs_data}")
        return None

class RinexParser:
    def __init__(self, file_path, debug_mode=False):
        self.file_path = file_path
        self.header = {}
        self.observations = []
        self.debug_mode = debug_mode

    def parse_epoch(self, lines):
        """修正后的历元解析方法"""
        try:
            header = lines[0].strip('\n')
            year_str = header[1:3].strip()
            year = int(year_str) + 2000 if int(year_str) < 80 else int(year_str) + 1900
            month = int(header[4:6].strip())
            day = int(header[7:9].strip())
            hour = int(header[10:12].strip())
            minute = int(header[13:15].strip())
            second = float(header[16:26].strip())

            num_sats_str = header[29:32].strip()
            num_sats = int(num_sats_str) if num_sats_str else 0

            sats = []
            sat_line = header[32:].replace('\n', '').lstrip()
            line_ptr = 1

            while len(sats) < num_sats and line_ptr < len(lines):
                for i in range(0, len(sat_line), 3):
                    if len(sats) >= num_sats:
                        break
                    prn = sat_line[i:i + 3].strip()
                    if len(prn) == 3 and prn[0] in ['G', 'R', 'C', 'E']:
                        sats.append(prn)

                if len(sats) < num_sats and line_ptr < len(lines):
                    sat_line = lines[line_ptr][:60].replace('\n', '').lstrip()
                    line_ptr += 1

            obs_types = []
            for line in lines:
                if line.startswith('# / TYPES OF OBSERV'):
                    types_line = line[0:60].strip()
                    for i in range(0, len(types_line), 6):
                        obs_type = types_line[i:i + 6].strip()
                        if obs_type:
                            obs_types.append(obs_type)
                    break

            if not obs_types:
                obs_types = ['C1', 'L1', 'D1', 'S1', 'P2', 'L2', 'D2', 'S2', 'C2', 'C5', 'L5', 'D5', 'S5']

            if self.debug_mode:
                logging.debug(f"观测类型列表: {obs_types}")

            num_obs_types = len(obs_types)
            lines_per_sat = (num_obs_types - 1) // 5 + 1
            observations = {}
            line_ptr = 1 + ((len(sats) - 1) // 12)

            if self.debug_mode:
                logging.debug(f"卫星数量: {len(sats)}, 起始行指针: {line_ptr}")

            for sat in sats:
                if line_ptr + lines_per_sat > len(lines):
                    if self.debug_mode:
                        logging.debug(f"行指针超出范围: {line_ptr}/{len(lines)}")
                    break

                obs_values = {}
                obs_index = 0

                for line_offset in range(lines_per_sat):
                    current_line = line_ptr + line_offset
                    if current_line >= len(lines):
                        break

                    line = lines[current_line].rstrip('\n')
                    if self.debug_mode:
                        logging.debug(f"解析行 {current_line}: {line}")

                    for col in range(5):
                        if obs_index >= num_obs_types:
                            break

                        start = col * 16
                        end = start + 14
                        if end > len(line):
                            break

                        obs_type = obs_types[obs_index]
                        val_str = line[start:end].strip()

                        if val_str and val_str not in ('', '0.0'):
                            try:
                                obs_values[obs_type] = float(val_str)
                                if self.debug_mode:
                                    logging.debug(f"卫星 {sat} 观测值 {obs_type}: {val_str}")
                            except ValueError:
                                if self.debug_mode:
                                    logging.debug(f"无效观测值: {val_str} for {obs_type}")

                        obs_index += 1

                if 'L1' in obs_values and ('L2' in obs_values or 'P2' in obs_values):
                    observations[sat] = obs_values
                    if self.debug_mode:
                        logging.debug(f"卫星 {sat} 有效观测: {list(obs_values.keys())}")
                else:
                    if self.debug_mode:
                        missing = []
                        if 'L1' not in obs_values: missing.append('L1')
                        if 'L2' not in obs_values and 'P2' not in obs_values: missing.append('L2/P2')
                        logging.debug(f"卫星 {sat} 缺失必要观测值: {missing}")

                line_ptr += lines_per_sat

            return {
                'time': datetime(year, month, day, hour, minute, int(second)),
                'satellites': sats,
                'observations': observations
            }
        except Exception as e:
            logging.error(f"解析错误: {str(e)}", exc_info=True)
            return None

    def parse_header(self, lines):
        header = {}
        for line in lines:
            if line.startswith('RINEX VERSION / TYPE'):
                header['version'] = float(line[:9])
                header['type'] = line[20:21]
            elif line.startswith('PGM / RUN BY / DATE'):
                header['program'] = line[:20].strip()
                header['agency'] = line[20:40].strip()
                header['date'] = line[40:60].strip()
            elif line.startswith('MARKER NAME'):
                header['marker_name'] = line[:60].strip()
            elif line.startswith('MARKER NUMBER'):
                header['marker_number'] = line[:60].strip()
            elif line.startswith('OBSERVER / AGENCY'):
                header['observer'] = line[:20].strip()
                header['agency'] = line[20:60].strip()
            elif line.startswith('REC # / TYPE / VERS'):
                header['receiver'] = line[:20].strip()
                header['receiver_type'] = line[20:40].strip()
                header['receiver_version'] = line[40:60].strip()
            elif line.startswith('ANT # / TYPE'):
                header['antenna'] = line[:20].strip()
                header['antenna_type'] = line[20:40].strip()
            elif line.startswith('APPROX POSITION XYZ'):
                header['position'] = [-2393382.4160, 5393861.1750, 2412592.4110]
                if self.debug_mode:
                    logging.debug(f"设置接收机位置: {header['position']}")
            elif line.startswith('ANTENNA: DELTA H/E/N'):
                header['antenna_delta'] = [float(x) for x in line[:60].split()]
            elif line.startswith('WAVELENGTH FACT L1/2'):
                header['wavelength_factor'] = [int(x) for x in line[:60].split()]
            elif line.startswith('# / TYPES OF OBSERV'):
                obs_types = []
                current_types = line[:60].split()
                obs_types.extend([t for t in current_types if t.isalnum()])

                next_line_idx = lines.index(line) + 1
                if next_line_idx < len(lines) and '# / TYPES OF OBSERV' in lines[next_line_idx]:
                    next_types = lines[next_line_idx][:60].split()
                    obs_types.extend([t for t in next_types if t.isalnum()])

                header['obs_types'] = obs_types
                if self.debug_mode:
                    logging.debug(f"解析到的观测类型: {obs_types}")
            elif line.startswith('INTERVAL'):
                header['interval'] = float(line[:60])
            elif line.startswith('TIME OF FIRST OBS'):
                header['first_obs'] = {
                    'year': int(line[:6]),
                    'month': int(line[6:12]),
                    'day': int(line[12:18]),
                    'hour': int(line[18:24]),
                    'minute': int(line[24:30]),
                    'second': float(line[30:43]),
                    'system': line[48:51]
                }
            elif line.startswith('TIME OF LAST OBS'):
                header['last_obs'] = {
                    'year': int(line[:6]),
                    'month': int(line[6:12]),
                    'day': int(line[12:18]),
                    'hour': int(line[18:24]),
                    'minute': int(line[24:30]),
                    'second': float(line[30:43]),
                    'system': line[48:51]
                }
            elif line.startswith('LEAP SECONDS'):
                header['leap_seconds'] = int(line[:60])
            elif line.startswith('# OF SATELLITES'):
                header['num_satellites'] = int(line[:60])
            elif line.startswith('PRN / # OF OBS'):
                if 'satellite_obs' not in header:
                    header['satellite_obs'] = {}
                sat = line[:3].strip()
                obs_counts = [int(x) for x in line[3:60].split()]
                header['satellite_obs'][sat] = obs_counts

        if self.debug_mode:
            logging.debug("解析到的文件头信息:")
            for key, value in header.items():
                if key != 'satellite_obs':
                    logging.debug(f"{key}: {value}")

        return header

    def parse(self):
        """解析RINEX文件"""
        with open(self.file_path, 'r') as f:
            lines = f.readlines()

        self.parse_header(lines)
        header_end = next(i for i, l in enumerate(lines) if 'END OF HEADER' in l)

        current_epoch = []
        epoch_re = re.compile(r'^\s*\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d+\.\d+')

        for line in lines[header_end + 1:]:
            if epoch_re.match(line):
                if current_epoch:
                    parsed = self.parse_epoch(current_epoch)
                    if parsed:
                        self.observations.append(parsed)
                current_epoch = [line]
            else:
                current_epoch.append(line)

        if current_epoch:
            parsed = self.parse_epoch(current_epoch)
            if parsed:
                self.observations.append(parsed)

        return self.observations

class SP3Parser:
    def __init__(self, file_path, debug_mode=False):
        self.file_path = file_path
        self.epochs = []
        self.header = {}
        self.debug_mode = debug_mode

    def parse_header(self, lines):
        """解析SP3文件头"""
        for line in lines:
            if line.startswith('#cP'):
                try:
                    year = int(line[3:7])
                    month = int(line[8:10])
                    day = int(line[11:13])
                    hour = int(line[14:16])
                    minute = int(line[17:19])
                    second = int(float(line[20:31]))

                    self.header['start_time'] = datetime(year, month, day, hour, minute, second)
                    self.header['epoch_count'] = int(line[32:38])
                    self.header['data_used'] = line[39:43].strip()
                    self.header['coordinate_system'] = line[44:48].strip()
                    self.header['orbit_type'] = line[49:52].strip()
                    self.header['agency'] = line[53:60].strip()
                except Exception as e:
                    logging.error(f"解析时间时出错: {str(e)}")
                    logging.error(f"问题行: {line}")
                    raise

            elif line.startswith('##'):
                parts = line.split()
                self.header['gps_week'] = int(parts[1])
                self.header['gps_seconds'] = float(parts[2])
                self.header['epoch_interval'] = float(parts[3])
                self.header['mjd'] = int(parts[4])
                self.header['fractional_day'] = float(parts[5])
            elif line.startswith('+'):
                if 'satellites' not in self.header:
                    self.header['satellites'] = []
                sat_list = line[3:].strip()
                for i in range(0, len(sat_list), 3):
                    if i + 3 <= len(sat_list):
                        sat_id = sat_list[i:i + 3].strip()
                        if sat_id:
                            if len(sat_id) >= 2:
                                sys_id = sat_id[0]
                                sat_num = sat_id[1:].strip()
                                if sat_num.isdigit():
                                    sat_id = f"{sys_id}{sat_num.zfill(2)}"
                            self.header['satellites'].append(sat_id)
            elif line.startswith('*'):
                break

    def parse_epoch(self, lines):
        """解析SP3文件历元数据"""
        epoch = {}
        header_line = lines[0].strip()

        try:
            parts = header_line.split()
            year = int(parts[1])
            month = int(parts[2])
            day = int(parts[3])
            hour = int(parts[4])
            minute = int(float(parts[5]))
            second = int(float(parts[6]))

            epoch['time'] = datetime(year, month, day, hour, minute, second)

            positions = {}
            for line in lines[1:]:
                if line.startswith('P'):
                    sat_id = line[1:4].strip()
                    if len(sat_id) >= 2:
                        sys_id = sat_id[0]
                        sat_num = sat_id[1:].strip()
                        if sat_num.isdigit():
                            sat_id = f"{sys_id}{sat_num.zfill(2)}"

                    try:
                        positions[sat_id] = {
                            'x': float(line[4:18]),
                            'y': float(line[18:32]),
                            'z': float(line[32:46]),
                            'clock': float(line[46:60])
                        }
                    except ValueError as e:
                        logging.error(f"解析卫星位置时出错: {str(e)}")
                        logging.error(f"问题行: {line}")
                        continue

            epoch['positions'] = positions
            return epoch

        except Exception as e:
            logging.error(f"解析历元数据时出错: {str(e)}")
            logging.error(f"问题行: {header_line}")
            return None

    def parse(self):
        """解析SP3文件"""
        with open(self.file_path, 'r') as f:
            lines = f.readlines()

        self.parse_header(lines)

        current_epoch = []
        for line in lines:
            if line.startswith('*'):
                if current_epoch:
                    epoch_data = self.parse_epoch(current_epoch)
                    if epoch_data:
                        self.epochs.append(epoch_data)
                current_epoch = [line]
            elif line.startswith('P'):
                current_epoch.append(line)

        if current_epoch:
            epoch_data = self.parse_epoch(current_epoch)
            if epoch_data:
                self.epochs.append(epoch_data)

        return self.epochs

def main():
    try:
        # 文件路径
        sp3_file = "C:/Users\顾诺\Desktop\作业大三下\GNSS\文件下载_任务二\igv23632_18_423.sp3\igv23632_18.sp3"
        rinex_file = "C:/Users\顾诺\Desktop\作业大三下\GNSS\文件下载_任务二\hksl1110_423.25o\hksl1110.25o"

        # 调试选项
        DEBUG_MODE = True

        # 配置日志
        logging.basicConfig(
            level=logging.DEBUG if DEBUG_MODE else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        logging.info("开始解析SP3文件...")
        sp3_parser = SP3Parser(sp3_file, debug_mode=DEBUG_MODE)
        sp3_data = sp3_parser.parse()
        logging.info(f"SP3文件解析完成，共{len(sp3_data)}个历元")

        # 创建卫星位置查找表
        sat_positions = {}
        for epoch in sp3_data:
            for sat_id, pos in epoch['positions'].items():
                if sat_id not in sat_positions:
                    sat_positions[sat_id] = []
                sat_positions[sat_id].append({
                    'time': epoch['time'],
                    'position': pos
                })

        for sat_id, positions in sat_positions.items():
            logging.debug(f"卫星 {sat_id} 在SP3文件中有 {len(positions)} 个历元")

        logging.info(f"SP3文件中包含的卫星: {list(sat_positions.keys())}")

        logging.info("开始解析RINEX文件...")
        rinex_parser = RinexParser(rinex_file, debug_mode=DEBUG_MODE)
        rinex_data = rinex_parser.parse()
        logging.info(f"RINEX文件解析完成，共{len(rinex_data)}个历元")

        # 检查接收机位置
        rec_pos = rinex_parser.header.get('position')
        if rec_pos is None:
            rec_pos = [-2393382.4160, 5393861.1750, 2412592.4110]
            logging.warning("使用默认接收机位置")

        logging.info(f"接收机位置: {rec_pos}")

        valid_obs_types = [ot for ot in rinex_parser.header.get('obs_types', []) if len(ot) <= 3 and ot.isalnum()]
        logging.info(f"RINEX文件中的有效观测类型: {valid_obs_types}")

        if 'satellites' in rinex_parser.header:
            logging.info(f"RINEX文件中包含的卫星: {rinex_parser.header['satellites']}")

        if sp3_data and rinex_data:
            sp3_start = sp3_data[0]['time']
            sp3_end = sp3_data[-1]['time']
            rinex_start = rinex_data[0]['time']
            rinex_end = rinex_data[-1]['time']

            logging.info(f"SP3文件时间范围: {sp3_start} 到 {sp3_end}")
            logging.info(f"RINEX文件时间范围: {rinex_start} 到 {rinex_end}")

            overlap_start = max(sp3_start, rinex_start)
            overlap_end = min(sp3_end, rinex_end)

            if overlap_start > overlap_end:
                logging.error("SP3文件和RINEX文件的时间范围不重叠!")
                return
            else:
                logging.info(f"有效重叠时间范围: {overlap_start} 到 {overlap_end}")
                logging.info(f"约有 {(overlap_end - overlap_start).total_seconds() / 30} 个可用历元")

        if DEBUG_MODE:
            if sp3_data:
                sample_epoch = sp3_data[0]
                sample_sats = list(sample_epoch['positions'].keys())[:5]
                logging.debug(f"SP3文件样本数据(第一个历元):")
                for sat in sample_sats:
                    logging.debug(f"  卫星 {sat} 位置: {sample_epoch['positions'][sat]}")

            if rinex_data:
                sample_epoch = rinex_data[0]
                if 'observations' in sample_epoch and sample_epoch['observations']:
                    sample_sats = list(sample_epoch['observations'].keys())[:5]
                    logging.debug(f"RINEX文件样本数据(第一个历元):")
                    for sat in sample_sats:
                        logging.debug(f"  卫星 {sat} 观测值: {sample_epoch['observations'][sat]}")

                    for sat in sample_sats:
                        if sat in sample_epoch['observations']:
                            obs = sample_epoch['observations'][sat]
                            if 'L1' in obs and 'L2' in obs:
                                logging.debug(f"  找到有效的L1/L2观测值: 卫星 {sat}, L1={obs['L1']}, L2={obs['L2']}")
                            else:
                                logging.debug(f"  卫星 {sat} 缺少L1/L2观测值, 可用: {list(obs.keys())}")

        logging.info("计算电离层延迟...")
        ion_delays = []
        positions = []
        processed_epochs = 0
        successful_calculations = 0
        missing_sat_count = 0
        missing_obs_count = 0
        error_count = 0

        rinex_sats = set()
        for epoch in rinex_data:
            if 'satellites' in epoch:
                rinex_sats.update(epoch['satellites'])

        sp3_sats = set(sat_positions.keys())
        common_sats = rinex_sats.intersection(sp3_sats)

        logging.info(f"RINEX和SP3文件中共同的卫星: {sorted(common_sats)}")
        logging.info(f"仅在RINEX中的卫星: {sorted(rinex_sats - sp3_sats)}")
        logging.info(f"仅在SP3中的卫星: {sorted(sp3_sats - rinex_sats)}")

        for epoch in rinex_data:
            if not epoch or 'satellites' not in epoch or 'observations' not in epoch:
                continue

            epoch_time = epoch['time']
            if epoch_time < overlap_start or epoch_time > overlap_end:
                continue

            processed_epochs += 1
            if processed_epochs % 1000 == 0:
                logging.info(f"已处理 {processed_epochs} 个历元...")

            for sat in epoch['satellites']:
                sat_id = sat.strip()
                if not sat_id or sat_id not in common_sats:
                    continue

                if sat_id not in sat_positions:
                    missing_sat_count += 1
                    continue

                sat_pos_list = sat_positions[sat_id]
                if not sat_pos_list:
                    missing_sat_count += 1
                    continue

                closest_pos_idx = 0
                min_time_diff = float('inf')

                for idx, pos_data in enumerate(sat_pos_list):
                    time_diff = abs((pos_data['time'] - epoch_time).total_seconds())
                    if time_diff < min_time_diff:
                        min_time_diff = time_diff
                        closest_pos_idx = idx

                if min_time_diff > 900:
                    logging.debug(f"卫星{sat_id}位置时间差过大: {min_time_diff}秒")
                    missing_sat_count += 1
                    continue

                sat_pos = sat_pos_list[closest_pos_idx]['position']

                if 'observations' in epoch:
                    obs_data = epoch['observations'].get(sat_id, {})

                    if ('L1' in obs_data and 'L2' in obs_data) or ('L1' in obs_data and 'P2' in obs_data):
                        try:
                            delay = calculate_ionospheric_delay(
                                obs_data,
                                sat_pos,
                                rec_pos
                            )
                            if delay is not None:
                                ion_delays.append(delay)
                                positions.append(rec_pos[:2])  # 只使用经纬度
                                successful_calculations += 1
                                if DEBUG_MODE and successful_calculations % 100 == 0:
                                    logging.debug(f"成功计算第 {successful_calculations} 个电离层延迟值")
                        except Exception as e:
                            error_count += 1
                            logging.error(f"计算电离层延迟时出错: {str(e)}")
                            logging.error(f"卫星: {sat_id}, 观测数据: {obs_data}")
                    else:
                        missing_obs_count += 1
                        if DEBUG_MODE:
                            logging.debug(f"卫星 {sat_id} 缺少必要的观测值: {obs_data}")

        logging.info(f"处理完成，共处理 {processed_epochs} 个历元")
        logging.info(f"成功计算 {successful_calculations} 个电离层延迟值")
        logging.info(f"缺少卫星位置数据: {missing_sat_count} 次")
        logging.info(f"缺少观测值: {missing_obs_count} 次")
        logging.info(f"计算错误: {error_count} 次")

        if len(ion_delays) == 0:
            logging.error("没有成功计算出任何电离层延迟值")
            return

        logging.info("进行数据质量控制...")
        ion_delays = np.array(ion_delays)
        positions = np.array(positions)

        mask = quality_control_mask(ion_delays)
        ion_delays = ion_delays[mask]
        positions = positions[mask]

        logging.info(f"质量控制后剩余 {len(ion_delays)} 个数据点")
        logging.info(f"电离层延迟统计: 均值={np.mean(ion_delays):.4f}m, 标准差={np.std(ion_delays):.4f}m")

        # 在main函数中
        logging.info("拟合电离层模型...")
        model_params, X, y_cleaned, X_mean, X_std = fit_ionospheric_model(ion_delays, positions)

        logging.info("验证模型...")
        rmse, bias = validate_model(model_params, X, y_cleaned, X_mean, X_std)


        print("模型为：\n")
        print(model_params)
        logging.info("保存模型参数...")
        save_model(model_params, "D:\gnss大作业\output.txt")

        logging.info("处理完成！")

    except Exception as e:
        logging.error(f"处理过程中出现错误: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    main()
