"""
对比 EKF 与 ESKF 在两种传感器组合下的性能差异：
1) GNSS + IMU
2) GNSS + IMU + LiDAR
"""

import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from rotations import Quaternion, skew_symmetric


# ============================================================================
# 绘图配置
# ============================================================================
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10


# ============================================================================
# 数据加载
# ============================================================================
base_dir = Path(__file__).resolve().parent
data_file = base_dir / 'data' / 'pt3_data.pkl'
result_dir = base_dir / 'result_images'
result_dir.mkdir(exist_ok=True)

with open(data_file, 'rb') as file:
    data = pickle.load(file)

gt = data['gt']
imu_f = data['imu_f']
imu_w = data['imu_w']
gnss = data['gnss']
lidar = data['lidar']


# LiDAR外参修正（与现有脚本保持一致）
C_li = np.array([
    [0.99376, -0.09722, 0.05466],
    [0.09971, 0.99401, -0.04475],
    [-0.04998, 0.04992, 0.9975],
])
t_i_li = np.array([0.5, 0.1, 0.5])
lidar.data = (C_li @ lidar.data.T).T + t_i_li


# 噪声参数
var_imu_f = 0.01
var_imu_w = 0.1
var_gnss = 20.0
var_lidar = 5.0

g = np.array([0, 0, -9.81])
l_jac = np.zeros([9, 6])
l_jac[3:, :] = np.eye(6)
h_jac = np.zeros([3, 9])
h_jac[:, :3] = np.eye(3)


def measurement_update(sensor_var, p_cov_check, y_k, p_check, v_check, q_check):
    """位置观测更新（GNSS/LiDAR 共用）"""
    r_k = sensor_var * np.eye(3)
    k_k = p_cov_check @ h_jac.T @ np.linalg.inv(h_jac @ p_cov_check @ h_jac.T + r_k)
    delta_x = k_k @ (y_k - p_check)
    delta_phi = delta_x[6:]

    p_hat = p_check + delta_x[:3]
    v_hat = v_check + delta_x[3:6]
    q_hat = Quaternion(euler=delta_phi).quat_mult_right(q_check)
    p_cov_hat = (np.eye(9) - k_k @ h_jac) @ p_cov_check
    return p_hat, v_hat, q_hat, p_cov_hat


def run_eskf(use_lidar):
    """运行 ESKF，use_lidar 控制是否融合 LiDAR。"""
    n = imu_f.data.shape[0]
    p_est = np.zeros([n, 3])
    v_est = np.zeros([n, 3])
    q_est = np.zeros([n, 4])
    p_cov = np.zeros([n, 9, 9])

    p_est[0] = gt.p[0]
    v_est[0] = gt.v[0]
    q_est[0] = Quaternion(euler=gt.r[0]).to_numpy()
    p_cov[0] = np.zeros(9)

    gnss_i = 0
    lidar_i = 0

    for k in range(1, n):
        delta_t = imu_f.t[k] - imu_f.t[k - 1]
        c_ns = Quaternion(*q_est[k - 1]).to_mat()

        p_est[k] = p_est[k - 1] + delta_t * v_est[k - 1] + ((delta_t ** 2) / 2) * (c_ns @ imu_f.data[k - 1] + g)
        v_est[k] = v_est[k - 1] + delta_t * (c_ns @ imu_f.data[k - 1] + g)
        q_est[k] = Quaternion(axis_angle=imu_w.data[k - 1] * delta_t).quat_mult_right(q_est[k - 1])

        f_k = np.eye(9)
        q_k = np.eye(6)
        imu_force = imu_f.data[k - 1].reshape((3, 1))
        f_k[0:3, 3:6] = delta_t * np.eye(3)
        f_k[3:6, 6:9] = -(c_ns @ skew_symmetric(imu_force.flatten())) * delta_t
        q_k[0:3, 0:3] = var_imu_f * q_k[0:3, 0:3]
        q_k[3:6, 3:6] = var_imu_w * q_k[3:6, 3:6]
        q_k *= delta_t ** 2

        p_cov[k] = f_k @ p_cov[k - 1] @ f_k.T + l_jac @ q_k @ l_jac.T

        if use_lidar and lidar_i < lidar.t.shape[0] and abs(lidar.t[lidar_i] - imu_f.t[k - 1]) < 0.001:
            p_est[k], v_est[k], q_est[k], p_cov[k] = measurement_update(
                var_lidar,
                p_cov[k],
                lidar.data[lidar_i].T,
                p_est[k],
                v_est[k],
                q_est[k],
            )
            lidar_i += 1

        if gnss_i < gnss.t.shape[0] and abs(gnss.t[gnss_i] - imu_f.t[k - 1]) < 0.001:
            p_est[k], v_est[k], q_est[k], p_cov[k] = measurement_update(
                var_gnss,
                p_cov[k],
                gnss.data[gnss_i].T,
                p_est[k],
                v_est[k],
                q_est[k],
            )
            gnss_i += 1

    return p_est, v_est, q_est, p_cov


def run_ekf(use_lidar):
    """运行 EKF，use_lidar 控制是否融合 LiDAR。"""
    n = imu_f.data.shape[0]
    p_est = np.zeros([n, 3])
    v_est = np.zeros([n, 3])
    q_est = np.zeros([n, 4])
    p_cov = np.zeros([n, 9, 9])

    p_est[0] = gt.p[0]
    v_est[0] = gt.v[0]
    q_est[0] = Quaternion(euler=gt.r[0]).to_numpy()
    p_cov[0] = np.eye(9) * 0.01

    gnss_i = 0
    lidar_i = 0

    for k in range(1, n):
        delta_t = imu_f.t[k] - imu_f.t[k - 1]
        c_ns = Quaternion(*q_est[k - 1]).to_mat()

        p_est[k] = p_est[k - 1] + delta_t * v_est[k - 1] + ((delta_t ** 2) / 2) * (c_ns @ imu_f.data[k - 1] + g)
        v_est[k] = v_est[k - 1] + delta_t * (c_ns @ imu_f.data[k - 1] + g)
        q_est[k] = Quaternion(axis_angle=imu_w.data[k - 1] * delta_t).quat_mult_right(q_est[k - 1])

        f_k = np.eye(9)
        imu_force = imu_f.data[k - 1].reshape((3, 1))
        f_k[0:3, 3:6] = delta_t * np.eye(3)
        f_k[3:6, 6:9] = -(c_ns @ skew_symmetric(imu_force.flatten())) * delta_t

        q_k = np.eye(6)
        q_k[0:3, 0:3] = var_imu_f * q_k[0:3, 0:3]
        q_k[3:6, 3:6] = var_imu_w * q_k[3:6, 3:6]
        q_k *= delta_t ** 2

        p_cov[k] = f_k @ p_cov[k - 1] @ f_k.T + l_jac @ q_k @ l_jac.T

        if use_lidar and lidar_i < lidar.t.shape[0] and abs(lidar.t[lidar_i] - imu_f.t[k - 1]) < 0.001:
            p_est[k], v_est[k], q_est[k], p_cov[k] = measurement_update(
                var_lidar,
                p_cov[k],
                lidar.data[lidar_i].T,
                p_est[k],
                v_est[k],
                q_est[k],
            )
            lidar_i += 1

        if gnss_i < gnss.t.shape[0] and abs(gnss.t[gnss_i] - imu_f.t[k - 1]) < 0.001:
            p_est[k], v_est[k], q_est[k], p_cov[k] = measurement_update(
                var_gnss,
                p_cov[k],
                gnss.data[gnss_i].T,
                p_est[k],
                v_est[k],
                q_est[k],
            )
            gnss_i += 1

    return p_est, v_est, q_est, p_cov


def calculate_errors(p_est, gt_p, v_est, gt_v):
    min_len = min(len(p_est), len(gt_p), len(v_est), len(gt_v))
    p_error = p_est[:min_len] - gt_p[:min_len]
    v_error = v_est[:min_len] - gt_v[:min_len]

    p_rmse = np.sqrt(np.mean(np.sum(p_error ** 2, axis=1)))
    v_rmse = np.sqrt(np.mean(np.sum(v_error ** 2, axis=1)))
    p_mae = np.mean(np.linalg.norm(p_error, axis=1))
    v_mae = np.mean(np.linalg.norm(v_error, axis=1))

    return {
        'p_rmse': p_rmse,
        'v_rmse': v_rmse,
        'p_mae': p_mae,
        'v_mae': v_mae,
        'p_error': p_error,
        'v_error': v_error,
        'min_len': min_len,
    }


def print_metrics(title, metrics):
    print(title)
    print(f"  位置 RMSE: {metrics['p_rmse']:.4f} m")
    print(f"  速度 RMSE: {metrics['v_rmse']:.4f} m/s")
    print(f"  位置 MAE : {metrics['p_mae']:.4f} m")
    print(f"  速度 MAE : {metrics['v_mae']:.4f} m/s")


print('开始运行对比...')
print(f'IMU 数据点数: {imu_f.data.shape[0]}')
print(f'GNSS 测量数: {gnss.t.shape[0]}')
print(f'LiDAR 测量数: {lidar.t.shape[0]}\n')


results = {}
sensor_modes = {
    'gnss_imu': {'name': 'GNSS + IMU', 'use_lidar': False},
    'gnss_imu_lidar': {'name': 'GNSS + IMU + LiDAR', 'use_lidar': True},
}

for mode_key, mode_cfg in sensor_modes.items():
    print(f"=== 传感器组合: {mode_cfg['name']} ===")

    ekf_p, ekf_v, _, _ = run_ekf(use_lidar=mode_cfg['use_lidar'])
    eskf_p, eskf_v, _, _ = run_eskf(use_lidar=mode_cfg['use_lidar'])

    ekf_err = calculate_errors(ekf_p, gt.p, ekf_v, gt.v)
    eskf_err = calculate_errors(eskf_p, gt.p, eskf_v, gt.v)

    results[mode_key] = {
        'cfg': mode_cfg,
        'ekf': {'p': ekf_p, 'v': ekf_v, 'err': ekf_err},
        'eskf': {'p': eskf_p, 'v': eskf_v, 'err': eskf_err},
    }

    print_metrics('EKF:', ekf_err)
    print_metrics('ESKF:', eskf_err)

    if ekf_err['p_rmse'] > 1e-12:
        improve = (ekf_err['p_rmse'] - eskf_err['p_rmse']) / ekf_err['p_rmse'] * 100.0
    else:
        improve = 0.0
    print(f'  ESKF 相比 EKF 的位置 RMSE 改进: {improve:.2f}%\n')


print('=== 同一滤波方法下，加入 LiDAR 的收益 ===')
for method in ['ekf', 'eskf']:
    base = results['gnss_imu'][method]['err']
    fused = results['gnss_imu_lidar'][method]['err']

    p_gain = base['p_rmse'] - fused['p_rmse']
    v_gain = base['v_rmse'] - fused['v_rmse']
    p_gain_ratio = (p_gain / base['p_rmse'] * 100.0) if base['p_rmse'] > 1e-12 else 0.0
    v_gain_ratio = (v_gain / base['v_rmse'] * 100.0) if base['v_rmse'] > 1e-12 else 0.0

    print(f"{method.upper()}:")
    print(f'  位置 RMSE 降低: {p_gain:.4f} m ({p_gain_ratio:.2f}%)')
    print(f'  速度 RMSE 降低: {v_gain:.4f} m/s ({v_gain_ratio:.2f}%)')


# ============================================================================
# 绘图
# ============================================================================
fig = plt.figure(figsize=(14, 10))

# 轨迹对比：GNSS+IMU
ax1 = fig.add_subplot(2, 2, 1, projection='3d')
ax1.plot(gt.p[:, 0], gt.p[:, 1], gt.p[:, 2], 'k-', linewidth=2.0, label='Ground Truth')
ax1.plot(results['gnss_imu']['ekf']['p'][:, 0], results['gnss_imu']['ekf']['p'][:, 1], results['gnss_imu']['ekf']['p'][:, 2], 'b--', linewidth=1.5, label='EKF')
ax1.plot(results['gnss_imu']['eskf']['p'][:, 0], results['gnss_imu']['eskf']['p'][:, 1], results['gnss_imu']['eskf']['p'][:, 2], color='orange', linestyle='--', linewidth=1.5, label='ESKF')
ax1.scatter(gnss.data[:, 0], gnss.data[:, 1], gnss.data[:, 2], c='g', s=10, alpha=0.6, label='GNSS')
ax1.set_title('GNSS + IMU 轨迹对比')
ax1.set_xlabel('E [m]')
ax1.set_ylabel('N [m]')
ax1.set_zlabel('U [m]')
ax1.legend(fontsize=8)
ax1.view_init(elev=45, azim=-50)

# 轨迹对比：GNSS+IMU+LiDAR
ax2 = fig.add_subplot(2, 2, 2, projection='3d')
ax2.plot(gt.p[:, 0], gt.p[:, 1], gt.p[:, 2], 'k-', linewidth=2.0, label='Ground Truth')
ax2.plot(results['gnss_imu_lidar']['ekf']['p'][:, 0], results['gnss_imu_lidar']['ekf']['p'][:, 1], results['gnss_imu_lidar']['ekf']['p'][:, 2], 'b--', linewidth=1.5, label='EKF')
ax2.plot(results['gnss_imu_lidar']['eskf']['p'][:, 0], results['gnss_imu_lidar']['eskf']['p'][:, 1], results['gnss_imu_lidar']['eskf']['p'][:, 2], color='orange', linestyle='--', linewidth=1.5, label='ESKF')
ax2.scatter(gnss.data[:, 0], gnss.data[:, 1], gnss.data[:, 2], c='g', s=10, alpha=0.6, label='GNSS')
ax2.scatter(lidar.data[:, 0], lidar.data[:, 1], lidar.data[:, 2], c='r', s=8, alpha=0.4, label='LiDAR')
ax2.set_title('GNSS + IMU + LiDAR 轨迹对比')
ax2.set_xlabel('E [m]')
ax2.set_ylabel('N [m]')
ax2.set_zlabel('U [m]')
ax2.legend(fontsize=8)
ax2.view_init(elev=45, azim=-50)

# 位置RMSE条形图
ax3 = fig.add_subplot(2, 2, 3)
labels = ['EKF\nGNSS+IMU', 'EKF\n+LiDAR', 'ESKF\nGNSS+IMU', 'ESKF\n+LiDAR']
p_rmse_values = [
    results['gnss_imu']['ekf']['err']['p_rmse'],
    results['gnss_imu_lidar']['ekf']['err']['p_rmse'],
    results['gnss_imu']['eskf']['err']['p_rmse'],
    results['gnss_imu_lidar']['eskf']['err']['p_rmse'],
]
bars = ax3.bar(labels, p_rmse_values, color=['royalblue', 'lightskyblue', 'darkorange', 'moccasin'])
ax3.set_title('位置 RMSE 对比')
ax3.set_ylabel('RMSE [m]')
ax3.grid(True, axis='y', alpha=0.3)
for bar in bars:
    h = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width() / 2.0, h, f'{h:.3f}', ha='center', va='bottom', fontsize=8)

# 速度RMSE条形图
ax4 = fig.add_subplot(2, 2, 4)
v_rmse_values = [
    results['gnss_imu']['ekf']['err']['v_rmse'],
    results['gnss_imu_lidar']['ekf']['err']['v_rmse'],
    results['gnss_imu']['eskf']['err']['v_rmse'],
    results['gnss_imu_lidar']['eskf']['err']['v_rmse'],
]
bars = ax4.bar(labels, v_rmse_values, color=['royalblue', 'lightskyblue', 'darkorange', 'moccasin'])
ax4.set_title('速度 RMSE 对比')
ax4.set_ylabel('RMSE [m/s]')
ax4.grid(True, axis='y', alpha=0.3)
for bar in bars:
    h = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width() / 2.0, h, f'{h:.3f}', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
out_file = result_dir / 'ekf_eskf_sensor_sets_comparison.png'
plt.savefig(out_file, dpi=150, bbox_inches='tight')
print(f'图像已保存: {out_file}')
