import numpy as np
import pandas as pd
from scipy.optimize import curve_fit, minimize
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
from sklearn.metrics import mean_squared_error
import logging
import re
import math
import os
from sklearn.model_selection import KFold
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio


def improved_polynomial_model(x, *params):
    """改进的多项式模型，增加更多非线性特征"""
    x = np.atleast_2d(x)  # 确保x是二维数组
    lat, lon = x[:, 0], x[:, 1]

    result = params[0]  # 常数项
    result += params[1] * lat  # 纬度线性项
    result += params[2] * lon  # 经度线性项
    result += params[3] * lat ** 2  # 纬度二次项
    result += params[4] * lon ** 2  # 经度二次项
    result += params[5] * lat * lon  # 交互项

    # 添加三角函数项来表示周期性变化
    result += params[6] * np.sin(lat)  # 纬度的季节性变化
    result += params[7] * np.cos(lat)
    result += params[8] * np.sin(lon)  # 经度的周期性变化
    result += params[9] * np.cos(lon)

    # 指数衰减项
    result += params[10] * np.exp(-lat ** 2 / 10)  # 纬度的高斯特征
    result += params[11] * np.exp(-lon ** 2 / 10)  # 经度的高斯特征

    return result


def quality_control_mask(data, threshold=3):
    """生成数据过滤mask"""
    mean = np.mean(data)
    std = np.std(data)
    mask = np.abs(data - mean) <= threshold * std
    # 物理范围检查（电离层延迟通常在0-50米范围内）
    mask = mask & (data >= 0) & (data <= 50)
    return mask


def improved_data_preprocessing(ion_delays, positions):
    """改进的数据预处理"""
    # 异常值检测 - 更严格的过滤
    q1, q3 = np.percentile(ion_delays, [25, 75])
    iqr = q3 - q1
    mask = (ion_delays >= q1 - 1.5 * iqr) & (ion_delays <= q3 + 1.5 * iqr)

    # 应用物理合理性过滤
    mask = mask & (ion_delays > 0) & (ion_delays < 30)

    # 过滤后的数据
    filtered_delays = ion_delays[mask]
    filtered_positions = positions[mask]

    # 检查是否有足够的数据点
    if len(filtered_delays) < 50:
        logging.warning(f"过滤后仅剩 {len(filtered_delays)} 个数据点，考虑放宽过滤条件")

    return filtered_delays, filtered_positions, mask


def feature_engineering(positions):
    """增强特征工程"""
    # 基础特征 - 经纬度
    lat, lon = positions[:, 0], positions[:, 1]

    # 创建更丰富的特征
    features = np.column_stack([
        lat,  # 纬度
        lon,  # 经度
        lat ** 2,  # 纬度平方
        lon ** 2,  # 经度平方
        lat * lon,  # 交互项
        np.sin(lat),  # 季节性变化特征
        np.cos(lat),  # 季节性变化特征
        np.sin(lon),  # 地理位置周期性特征
        np.cos(lon),  # 地理位置周期性特征
        np.abs(lat),  # 绝对纬度影响
        np.exp(-lat ** 2 / 10),  # 高斯分布特征
        np.exp(-lon ** 2 / 10)  # 高斯分布特征
    ])

    return features


def improved_model_fitting(ion_delays, positions):
    """改进的模型拟合函数"""
    # 数据预处理
    filtered_delays, filtered_positions, _ = improved_data_preprocessing(ion_delays, positions)

    # 标准化数据
    pos_mean = np.mean(filtered_positions, axis=0)
    pos_std = np.std(filtered_positions, axis=0)
    X_scaled = (filtered_positions - pos_mean) / pos_std

    # 初始参数设置
    n_params = 12  # 更多参数
    initial_params = np.zeros(n_params)
    initial_params[0] = np.mean(filtered_delays)  # 常数项初始化为均值

    # 随机初始化其他参数
    initial_params[1:] = np.random.normal(0, 0.1, n_params - 1)

    try:
        # 使用多次尝试和不同初始化
        best_params = None
        best_r2 = -np.inf

        for _ in range(5):  # 尝试多次拟合
            try:
                params, covariance = curve_fit(
                    improved_polynomial_model,
                    X_scaled,
                    filtered_delays,
                    p0=initial_params,
                    maxfev=10000,
                    method='lm'  # 使用Levenberg-Marquardt算法
                )

                # 计算R²
                y_pred = improved_polynomial_model(X_scaled, *params)
                r2 = 1 - np.sum((filtered_delays - y_pred) ** 2) / np.sum(
                    (filtered_delays - np.mean(filtered_delays)) ** 2)

                if r2 > best_r2:
                    best_r2 = r2
                    best_params = params

                # 随机化初始参数重新尝试
                initial_params[1:] = np.random.normal(0, 0.2, n_params - 1)

            except Exception as e:
                logging.warning(f"拟合尝试失败: {str(e)}")
                continue

        if best_params is not None:
            logging.info(f"最佳拟合 R²: {best_r2:.4f}")
            return best_params, X_scaled, filtered_delays, pos_mean, pos_std
        else:
            logging.error("所有拟合尝试都失败了")
            return initial_params, X_scaled, filtered_delays, pos_mean, pos_std

    except Exception as e:
        logging.error(f"模型拟合失败: {str(e)}")
        return initial_params, X_scaled, filtered_delays, pos_mean, pos_std


def constrained_model_fitting(ion_delays, positions):
    """带约束的模型拟合"""
    # 预处理
    filtered_delays, filtered_positions, _ = improved_data_preprocessing(ion_delays, positions)

    # 标准化数据
    pos_mean = np.mean(filtered_positions, axis=0)
    pos_std = np.std(filtered_positions, axis=0)
    X_scaled = (filtered_positions - pos_mean) / pos_std

    # 初始参数
    n_params = 12
    initial_params = np.zeros(n_params)
    initial_params[0] = np.mean(filtered_delays)
    initial_params[1:] = np.random.normal(0, 0.1, n_params - 1)

    # 定义目标函数，添加正则化项
    def objective(params):
        y_pred = improved_polynomial_model(X_scaled, *params)
        return np.sum((filtered_delays - y_pred) ** 2) + 0.01 * np.sum(params[1:] ** 2)  # L2正则化

    # 使用更高级的优化方法
    result = minimize(
        objective,
        initial_params,
        method='L-BFGS-B',
        options={'maxiter': 1000}
    )

    # 验证拟合结果
    final_params = result.x
    y_pred = improved_polynomial_model(X_scaled, *final_params)
    r2 = 1 - np.sum((filtered_delays - y_pred) ** 2) / np.sum((filtered_delays - np.mean(filtered_delays)) ** 2)
    logging.info(f"约束优化拟合 R²: {r2:.4f}")

    return final_params, X_scaled, filtered_delays, pos_mean, pos_std


def improved_validation(model_params, X, y, X_mean, X_std):
    """改进的模型验证"""
    X_scaled = (X - X_mean) / X_std
    y_pred = improved_polynomial_model(X_scaled, *model_params)

    # 计算评估指标
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    bias = np.mean(y_pred - y)

    # 计算R²
    r2 = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)

    # 计算相关系数
    corr = np.corrcoef(y, y_pred)[0, 1]

    logging.info(f"模型评估指标:")
    logging.info(f"RMSE: {rmse:.4f} m")
    logging.info(f"Bias: {bias:.4f} m")
    logging.info(f"R²: {r2:.4f}")
    logging.info(f"相关系数: {corr:.4f}")

    # 计算相对误差
    rel_error = np.abs(y_pred - y) / (y + 1e-10)  # 避免除零
    logging.info(f"相对误差: 均值={np.mean(rel_error):.4f}, 中位数={np.median(rel_error):.4f}")

    return rmse, bias, r2, corr, y_pred


def feature_importance_analysis(model_params):
    """特征重要性分析"""
    abs_params = np.abs(model_params[1:])  # 排除常数项
    param_names = [
        "纬度线性", "经度线性",
        "纬度平方", "经度平方", "交互项",
        "纬度sin", "纬度cos", "经度sin", "经度cos",
        "纬度高斯", "经度高斯"
    ]

    # 归一化参数
    norm_params = abs_params / np.sum(abs_params) if np.sum(abs_params) > 0 else abs_params

    # 打印特征重要性
    logging.info("特征重要性分析:")
    for name, importance in zip(param_names, norm_params):
        logging.info(f"{name}: {importance:.4f}")

    # 创建特征重要性图
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=param_names,
        y=norm_params,
        marker_color='royalblue'
    ))
    fig.update_layout(
        title="特征重要性分析",
        xaxis_title="特征",
        yaxis_title="归一化重要性",
        template="plotly_white"
    )
    fig.write_html("feature_importance.html")
    # fig.show()
    return fig


def cross_validation(ion_delays, positions, n_folds=5):
    """交叉验证"""
    # 准备数据
    X = positions
    y = ion_delays

    # 创建K折交叉验证
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)

    # 评估指标
    rmse_list = []
    r2_list = []

    for train_idx, test_idx in kf.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # 拟合模型
        params, X_train_scaled, _, X_mean, X_std = improved_model_fitting(y_train, X_train)

        # 验证模型
        X_test_scaled = (X_test - X_mean) / X_std
        y_pred = improved_polynomial_model(X_test_scaled, *params)

        # 计算评估指标
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = 1 - np.sum((y_test - y_pred) ** 2) / np.sum((y_test - np.mean(y_test)) ** 2)

        rmse_list.append(rmse)
        r2_list.append(r2)

    # 输出结果
    logging.info(f"交叉验证结果:")
    logging.info(f"平均RMSE: {np.mean(rmse_list):.4f} ± {np.std(rmse_list):.4f} m")
    logging.info(f"平均R²: {np.mean(r2_list):.4f} ± {np.std(r2_list):.4f}")

    return np.mean(rmse_list), np.mean(r2_list)


def improved_visualize_results(X, y, y_pred, model_params):
    """改进的可视化函数"""
    # 创建子图
    fig = make_subplots(
        rows=2,
        cols=3,
        subplot_titles=(
            "预测值 vs 实际值",
            "残差分布",
            "模型参数重要性",
            "残差散点图",
            "预测值分布",
            "实际值分布"
        ),
        specs=[
            [{"type": "scatter"}, {"type": "histogram"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "histogram"}, {"type": "histogram"}]
        ]
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
                opacity=0.5,
                color='blue'
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
            marker_color='green',
            showlegend=False
        ),
        row=1, col=2
    )

    # 3. 参数重要性条形图
    abs_params = np.abs(model_params[1:])  # 排除常数项
    param_names = [
        "纬度线性", "经度线性",
        "纬度平方", "经度平方", "交互项",
        "纬度sin", "纬度cos", "经度sin", "经度cos",
        "纬度高斯", "经度高斯"
    ]

    # 归一化参数
    norm_params = abs_params / np.sum(abs_params) if np.sum(abs_params) > 0 else abs_params

    fig.add_trace(
        go.Bar(
            x=param_names,
            y=norm_params,
            name='参数重要性',
            marker_color='purple',
            showlegend=False
        ),
        row=1, col=3
    )

    # 4. 残差散点图 - 按预测值
    fig.add_trace(
        go.Scatter(
            x=y_pred,
            y=residuals,
            mode='markers',
            name='残差 vs 预测值',
            marker=dict(
                size=8,
                opacity=0.5,
                color='orange'
            ),
            showlegend=False
        ),
        row=2, col=1
    )

    # 添加水平参考线
    fig.add_trace(
        go.Scatter(
            x=[min(y_pred), max(y_pred)],
            y=[0, 0],
            mode='lines',
            line=dict(color='red', dash='dash'),
            showlegend=False
        ),
        row=2, col=1
    )

    # 5. 预测值分布
    fig.add_trace(
        go.Histogram(
            x=y_pred,
            nbinsx=50,
            name='预测值分布',
            marker_color='teal',
            showlegend=False
        ),
        row=2, col=2
    )

    # 6. 实际值分布
    fig.add_trace(
        go.Histogram(
            x=y,
            nbinsx=50,
            name='实际值分布',
            marker_color='salmon',
            showlegend=False
        ),
        row=2, col=3
    )

    # 更新布局
    fig.update_layout(
        title_text="改进的电离层模型分析结果",
        title_x=0.5,
        showlegend=True,
        height=800,  # 增加高度以适应更多子图
        width=1500,
        template="plotly_white"
    )

    # 更新x轴和y轴标签
    fig.update_xaxes(title_text="实际值 (m)", row=1, col=1)
    fig.update_yaxes(title_text="预测值 (m)", row=1, col=1)

    fig.update_xaxes(title_text="残差 (m)", row=1, col=2)
    fig.update_yaxes(title_text="频数", row=1, col=2)

    fig.update_xaxes(title_text="特征", row=1, col=3)
    fig.update_yaxes(title_text="归一化重要性", row=1, col=3)

    fig.update_xaxes(title_text="预测值 (m)", row=2, col=1)
    fig.update_yaxes(title_text="残差 (m)", row=2, col=1)

    fig.update_xaxes(title_text="预测值 (m)", row=2, col=2)
    fig.update_yaxes(title_text="频数", row=2, col=2)

    fig.update_xaxes(title_text="实际值 (m)", row=2, col=3)
    fig.update_yaxes(title_text="频数", row=2, col=3)

    # 保存为HTML和PNG
    pio.write_html(fig, 'improved_ionospheric_model_analysis.html')
    pio.write_image(fig, 'improved_ionospheric_model_analysis.png', scale=2)

    # 显示图形
    # fig.show()
    return fig


def save_model(model_params, output_file):
    """保存模型参数"""
    param_names = [
        "常数项",
        "纬度线性", "经度线性",
        "纬度平方", "经度平方", "交互项",
        "纬度sin", "纬度cos", "经度sin", "经度cos",
        "纬度高斯", "经度高斯"
    ]

    with open(output_file, 'w') as f:
        f.write(f"模型生成时间: {datetime.now()}\n")
        f.write("模型参数:\n")
        for i, param in enumerate(model_params):
            param_name = param_names[i] if i < len(param_names) else f"系数 {i}"
            f.write(f"{param_name}: {param}\n")


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
                ion_delay = (f2 ** 2 / (f1 ** 2 - f2 ** 2)) * (lambda1 * l1_phase - lambda2 * l2_phase)
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
                ion_delay = (f2 ** 2 / (f1 ** 2 - f2 ** 2)) * (lambda1 * l1_phase - p2_code)
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
                ion_delay = (f2 ** 2 / (f1 ** 2 - f2 ** 2)) * (c1_code - p2_code)
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
        # 文件路径设置
        output_dir = "ionospheric_model_results"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        sp3_file = "C:/Users/顾诺/Desktop/作业大三下/GNSS/文件下载_任务二/igv23632_18_423.sp3/igv23632_18.sp3"
        rinex_file = "C:/Users/顾诺/Desktop/作业大三下/GNSS/文件下载_任务二/hksl1110_423.25o/hksl1110.25o"
        output_file = os.path.join(output_dir, "improved_ionospheric_model.txt")

        # 调试选项
        DEBUG_MODE = True

        # 配置日志
        log_file = os.path.join(output_dir, "processing.log")
        logging.basicConfig(
            level=logging.DEBUG if DEBUG_MODE else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        logging.info("========== 开始电离层模型拟合处理 ==========")
        logging.info(f"SP3文件: {sp3_file}")
        logging.info(f"RINEX文件: {rinex_file}")

        # 解析SP3文件
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

        # 解析RINEX文件
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

        # 检查RINEX和SP3数据时间重叠
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

        # 计算电离层延迟
        logging.info("计算电离层延迟...")
        ion_delays = []
        positions = []
        processed_epochs = 0
        successful_calculations = 0

        # 找出共同的卫星
        rinex_sats = set()
        for epoch in rinex_data:
            if 'satellites' in epoch:
                rinex_sats.update(epoch['satellites'])

        sp3_sats = set(sat_positions.keys())
        common_sats = rinex_sats.intersection(sp3_sats)

        logging.info(f"RINEX和SP3文件中共同的卫星: {len(common_sats)}个")

        # 处理历元数据
        for epoch in rinex_data:
            if not epoch or 'satellites' not in epoch or 'observations' not in epoch:
                continue

            epoch_time = epoch['time']
            if epoch_time < overlap_start or epoch_time > overlap_end:
                continue

            processed_epochs += 1
            if processed_epochs % 100 == 0:
                logging.info(f"已处理 {processed_epochs} 个历元...")

            for sat in epoch['satellites']:
                sat_id = sat.strip()
                if not sat_id or sat_id not in common_sats:
                    continue

                if sat_id not in sat_positions:
                    continue

                sat_pos_list = sat_positions[sat_id]
                if not sat_pos_list:
                    continue

                # 找到最接近的卫星位置
                closest_pos_idx = 0
                min_time_diff = float('inf')

                for idx, pos_data in enumerate(sat_pos_list):
                    time_diff = abs((pos_data['time'] - epoch_time).total_seconds())
                    if time_diff < min_time_diff:
                        min_time_diff = time_diff
                        closest_pos_idx = idx

                if min_time_diff > 900:  # 15分钟
                    continue

                sat_pos = sat_pos_list[closest_pos_idx]['position']

                # 获取观测数据并计算电离层延迟
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
                        except Exception as e:
                            logging.error(f"计算电离层延迟时出错: {str(e)}")

        logging.info(f"处理完成，共处理 {processed_epochs} 个历元")
        logging.info(f"成功计算 {successful_calculations} 个电离层延迟值")

        if len(ion_delays) == 0:
            logging.error("没有成功计算出任何电离层延迟值")
            return

        # 将数据转换为NumPy数组
        ion_delays = np.array(ion_delays)
        positions = np.array(positions)

        # 基本统计分析
        logging.info("进行基本统计分析...")
        logging.info(f"电离层延迟统计: 均值={np.mean(ion_delays):.4f}m, 标准差={np.std(ion_delays):.4f}m")
        logging.info(f"最小值: {np.min(ion_delays):.4f}m, 最大值: {np.max(ion_delays):.4f}m")
        logging.info(f"中位数: {np.median(ion_delays):.4f}m")

        # 保存原始数据
        np.savez(os.path.join(output_dir, "raw_data.npz"), ion_delays=ion_delays, positions=positions)

        # 改进的数据预处理
        logging.info("进行改进的数据预处理...")
        filtered_delays, filtered_positions, filter_mask = improved_data_preprocessing(ion_delays, positions)
        logging.info(f"过滤前: {len(ion_delays)}个数据点")
        logging.info(f"过滤后: {len(filtered_delays)}个数据点")
        logging.info(f"过滤后数据统计: 均值={np.mean(filtered_delays):.4f}m, 标准差={np.std(filtered_delays):.4f}m")

        # 保存过滤后的数据
        np.savez(os.path.join(output_dir, "filtered_data.npz"),
                 ion_delays=filtered_delays, positions=filtered_positions)

        # 交叉验证
        logging.info("执行交叉验证...")
        try:
            cv_rmse, cv_r2 = cross_validation(filtered_delays, filtered_positions)
            logging.info(f"交叉验证RMSE: {cv_rmse:.4f}m, R²: {cv_r2:.4f}")
        except Exception as e:
            logging.error(f"交叉验证失败: {str(e)}")

        # 常规模型拟合
        logging.info("使用改进的方法拟合电离层模型...")
        model_params, X_scaled, y_cleaned, X_mean, X_std = improved_model_fitting(filtered_delays, filtered_positions)

        # 尝试约束优化方法
        logging.info("使用约束优化方法拟合电离层模型...")
        try:
            constrained_params, _, _, _, _ = constrained_model_fitting(filtered_delays, filtered_positions)
            logging.info("约束优化拟合完成")
        except Exception as e:
            logging.error(f"约束优化拟合失败: {str(e)}")
            constrained_params = model_params

        # 模型验证
        logging.info("验证模型性能...")
        rmse, bias, r2, corr, y_pred = improved_validation(model_params, filtered_positions, filtered_delays, X_mean,
                                                           X_std)

        # 特征重要性分析
        logging.info("进行特征重要性分析...")
        feature_importance_fig = feature_importance_analysis(model_params)
        # 保存模型
        logging.info("保存最终模型...")
        save_model(model_params, output_file)
        # 也保存约束优化的模型
        save_model(constrained_params, os.path.join(output_dir, "constrained_model.txt"))
        # 可视化结果
        logging.info("可视化结果...")
        vis_fig = improved_visualize_results(filtered_positions, filtered_delays, y_pred, model_params)





        # 保存结果摘要
        with open(os.path.join(output_dir, "model_summary.txt"), 'w') as f:
            f.write("电离层模型拟合结果摘要\n")
            f.write("=======================\n\n")
            f.write(f"处理时间: {datetime.now()}\n")
            f.write(f"数据点总数: {len(ion_delays)}\n")
            f.write(f"过滤后数据点: {len(filtered_delays)}\n")
            f.write(f"模型性能指标:\n")
            f.write(f"  RMSE: {rmse:.4f} m\n")
            f.write(f"  Bias: {bias:.4f} m\n")
            f.write(f"  R²: {r2:.4f}\n")
            f.write(f"  相关系数: {corr:.4f}\n")
            f.write(f"  交叉验证RMSE: {cv_rmse:.4f} m\n")
            f.write(f"  交叉验证R²: {cv_r2:.4f}\n\n")
            f.write(f"模型参数:\n")
            param_names = [
                "常数项",
                "纬度线性", "经度线性",
                "纬度平方", "经度平方", "交互项",
                "纬度sin", "纬度cos", "经度sin", "经度cos",
                "纬度高斯", "经度高斯"
            ]
            for i, param in enumerate(model_params):
                param_name = param_names[i] if i < len(param_names) else f"系数 {i}"
                f.write(f"  {param_name}: {param:.8f}\n")

        logging.info("所有处理完成！")

    except Exception as e:
        logging.error(f"处理过程中出现错误: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()

