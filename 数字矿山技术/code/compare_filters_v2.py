"""
对比卡尔曼滤波器(KF)、扩展卡尔曼滤波器(EKF)和错误状态卡尔曼滤波器(ESKF)的性能
本脚本采用与原始es_ekf.py相同的ESKF实现
"""
import pickle
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from mpl_toolkits.mplot3d import Axes3D
from rotations import angle_normalize, rpy_jacobian_axis_angle, skew_symmetric, Quaternion

# ============================================================================
# 中文和负号支持配置
# ============================================================================
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']  # 支持中文
plt.rcParams['axes.unicode_minus'] = False  # 负号显示
plt.rcParams['font.size'] = 10


# ============================================================================
# 1. 数据加载
# ============================================================================
data_file = Path(__file__).resolve().parent / 'data' / 'pt3_data.pkl'
with open(data_file, 'rb') as file:
    data = pickle.load(file)

gt = data['gt']
imu_f = data['imu_f']
imu_w = data['imu_w']
gnss = data['gnss']
lidar = data['lidar']

# 传感器参数
C_li = np.array([
   [ 0.99376, -0.09722,  0.05466],
   [ 0.09971,  0.99401, -0.04475],
   [-0.04998,  0.04992,  0.9975 ]
])
t_i_li = np.array([0.5, 0.1, 0.5])
lidar.data = (C_li @ lidar.data.T).T + t_i_li

# 传感器噪声方差
var_imu_f = 0.01
var_imu_w = 0.1
var_gnss  = 20.
var_lidar = 5.

# 常数
g = np.array([0, 0, -9.81])
l_jac = np.zeros([9, 6])
l_jac[3:, :] = np.eye(6)
h_jac = np.zeros([3, 9])
h_jac[:, :3] = np.eye(3)

print(f"数据点数: {imu_f.data.shape[0]}")
print(f"GNSS测量数: {gnss.t.shape[0]}")
print(f"LIDAR测量数: {lidar.t.shape[0]}\n")


# ============================================================================
# 2. ESKF实现（与原始es_ekf.py完全相同）
# ============================================================================
def run_eskf():
    """运行原始ESKF算法"""
    p_est = np.zeros([imu_f.data.shape[0], 3])
    v_est = np.zeros([imu_f.data.shape[0], 3])
    q_est = np.zeros([imu_f.data.shape[0], 4])
    p_cov = np.zeros([imu_f.data.shape[0], 9, 9])
    
    p_est[0] = gt.p[0]
    v_est[0] = gt.v[0]
    q_est[0] = Quaternion(euler=gt.r[0]).to_numpy()
    p_cov[0] = np.zeros(9)
    
    gnss_i = 0
    lidar_i = 0
    
    def measurement_update(sensor_var, p_cov_check, y_k, p_check, v_check, q_check):
        R = sensor_var * np.eye(3)
        K_k = p_cov_check @ h_jac.T @ np.linalg.inv(h_jac @ p_cov_check @ h_jac.T + R)
        delta_xk = K_k @ (y_k - p_check)
        delta_phi = delta_xk[6:]
        
        p_hat = p_check + delta_xk[:3]
        v_hat = v_check + delta_xk[3:6]
        q_hat = Quaternion(euler=delta_phi).quat_mult_right(q_check)
        p_cov_hat = (np.eye(9) - K_k @ h_jac) @ p_cov_check
        
        return p_hat, v_hat, q_hat, p_cov_hat
    
    for k in range(1, imu_f.data.shape[0]):
        delta_t = imu_f.t[k] - imu_f.t[k-1]
        C_ns = Quaternion(*q_est[k-1]).to_mat()
        
        p_est[k] = p_est[k-1] + delta_t * v_est[k-1] + ((delta_t**2)/2) * (C_ns @ imu_f.data[k-1] + g)
        v_est[k] = v_est[k-1] + delta_t * (C_ns @ imu_f.data[k-1] + g)
        q_est[k] = Quaternion(axis_angle=imu_w.data[k-1] * delta_t).quat_mult_right(q_est[k-1])
        
        F_k = np.eye(9)
        Q_k = np.eye(6)
        imu_force_data = imu_f.data[k-1].reshape((3, 1))
        F_k[0:3, 3:6] = delta_t * np.eye(3)
        F_k[3:6, 6:9] = -(C_ns @ skew_symmetric(imu_force_data.flatten())) * delta_t
        Q_k[0:3, 0:3] = var_imu_f * Q_k[0:3, 0:3]
        Q_k[3:6, 3:6] = var_imu_w * Q_k[3:6, 3:6]
        Q_k *= delta_t**2
        
        p_cov[k] = F_k @ p_cov[k-1] @ F_k.T + l_jac @ Q_k @ l_jac.T
        
        if lidar_i < lidar.t.shape[0] and abs(lidar.t[lidar_i] - imu_f.t[k-1]) < 0.001:
            p_est[k], v_est[k], q_est[k], p_cov[k] = measurement_update(
                var_lidar, p_cov[k], lidar.data[lidar_i].T, 
                p_est[k], v_est[k], q_est[k])
            lidar_i += 1
        if gnss_i < gnss.t.shape[0] and abs(gnss.t[gnss_i] - imu_f.t[k-1]) < 0.001:
            p_est[k], v_est[k], q_est[k], p_cov[k] = measurement_update(
                var_gnss, p_cov[k], gnss.data[gnss_i].T, 
                p_est[k], v_est[k], q_est[k])
            gnss_i += 1
    
    return p_est, v_est, q_est, p_cov


# ============================================================================
# 3. KF实现（标准卡尔曼滤波器 - 线性系统）
# ============================================================================
def run_kf():
    """标准卡尔曼滤波器 - 假设系统线性"""
    p_est = np.zeros([imu_f.data.shape[0], 3])
    v_est = np.zeros([imu_f.data.shape[0], 3])
    p_cov = np.zeros([imu_f.data.shape[0], 9, 9])
    
    p_est[0] = gt.p[0]
    v_est[0] = gt.v[0]
    p_cov[0] = np.eye(9) * 0.01
    
    gnss_i = 0
    lidar_i = 0
    
    def measurement_update_kf(sensor_var, p_cov_check, y_k, p_check, v_check):
        R = sensor_var * np.eye(3)
        S = h_jac @ p_cov_check @ h_jac.T + R
        K = p_cov_check @ h_jac.T @ np.linalg.inv(S)
        
        delta_x = K @ (y_k - p_check)
        p_hat = (p_check + delta_x[:3]).flatten()
        # v_check已经是1D，创建列向量进行计算
        v_check_col = v_check.reshape(3, 1)
        v_hat = (v_check_col + delta_x[3:6]).flatten()
        p_cov_hat = (np.eye(9) - K @ h_jac) @ p_cov_check
        
        return p_hat, v_hat, p_cov_hat
    
    for k in range(1, imu_f.data.shape[0]):
        delta_t = imu_f.t[k] - imu_f.t[k-1]
        
        # 线性系统：只考虑位置和速度，不考虑旋转
        p_est[k] = p_est[k-1] + delta_t * v_est[k-1]
        v_est[k] = v_est[k-1] + delta_t * np.mean(imu_f.data[k-1:k+1], axis=0)
        
        F_k = np.eye(9)
        F_k[0:3, 3:6] = delta_t * np.eye(3)
        
        Q_k = np.eye(6)
        Q_k[0:3, 0:3] = var_imu_f * Q_k[0:3, 0:3]
        Q_k[3:6, 3:6] = var_imu_w * Q_k[3:6, 3:6]
        Q_k *= delta_t**2
        
        p_cov[k] = F_k @ p_cov[k-1] @ F_k.T + l_jac @ Q_k @ l_jac.T
        
        if lidar_i < lidar.t.shape[0] and abs(lidar.t[lidar_i] - imu_f.t[k-1]) < 0.001:
            p_est[k], v_est[k], p_cov[k] = measurement_update_kf(
                var_lidar, p_cov[k], lidar.data[lidar_i].T.reshape(3, 1), 
                p_est[k].reshape(3, 1), v_est[k])
            lidar_i += 1
        if gnss_i < gnss.t.shape[0] and abs(gnss.t[gnss_i] - imu_f.t[k-1]) < 0.001:
            p_est[k], v_est[k], p_cov[k] = measurement_update_kf(
                var_gnss, p_cov[k], gnss.data[gnss_i].T.reshape(3, 1), 
                p_est[k].reshape(3, 1), v_est[k])
            gnss_i += 1
    
    return p_est, v_est, p_cov


# ============================================================================
# 4. EKF实现（扩展卡尔曼滤波器 - 考虑非线性旋转）
# ============================================================================
def run_ekf():
    """扩展卡尔曼滤波器 - 处理非线性旋转"""
    p_est = np.zeros([imu_f.data.shape[0], 3])
    v_est = np.zeros([imu_f.data.shape[0], 3])
    q_est = np.zeros([imu_f.data.shape[0], 4])
    p_cov = np.zeros([imu_f.data.shape[0], 9, 9])
    
    p_est[0] = gt.p[0]
    v_est[0] = gt.v[0]
    q_est[0] = Quaternion(euler=gt.r[0]).to_numpy()
    p_cov[0] = np.eye(9) * 0.01
    
    gnss_i = 0
    lidar_i = 0
    
    def measurement_update_ekf(sensor_var, p_cov_check, y_k, p_check, v_check, q_check):
        R = sensor_var * np.eye(3)
        S = h_jac @ p_cov_check @ h_jac.T + R
        K = p_cov_check @ h_jac.T @ np.linalg.inv(S)
        
        delta_x = K @ (y_k - p_check)
        p_hat = (p_check + delta_x[:3]).flatten()
        # v_check已经是1D
        v_check_col = v_check.reshape(3, 1)
        v_hat = (v_check_col + delta_x[3:6]).flatten()
        delta_phi = delta_x[6:].flatten()
        q_hat = Quaternion(euler=delta_phi).quat_mult_right(q_check)
        
        p_cov_hat = (np.eye(9) - K @ h_jac) @ p_cov_check
        
        return p_hat, v_hat, q_hat, p_cov_hat
    
    for k in range(1, imu_f.data.shape[0]):
        delta_t = imu_f.t[k] - imu_f.t[k-1]
        C_ns = Quaternion(*q_est[k-1]).to_mat()
        
        p_est[k] = p_est[k-1] + delta_t * v_est[k-1] + ((delta_t**2)/2) * (C_ns @ imu_f.data[k-1] + g)
        v_est[k] = v_est[k-1] + delta_t * (C_ns @ imu_f.data[k-1] + g)
        q_est[k] = Quaternion(axis_angle=imu_w.data[k-1] * delta_t).quat_mult_right(q_est[k-1])
        
        F_k = np.eye(9)
        imu_force_data = imu_f.data[k-1].reshape((3, 1))
        F_k[0:3, 3:6] = delta_t * np.eye(3)
        F_k[3:6, 6:9] = -(C_ns @ skew_symmetric(imu_force_data.flatten())) * delta_t
        
        Q_k = np.eye(6)
        Q_k[0:3, 0:3] = var_imu_f * Q_k[0:3, 0:3]
        Q_k[3:6, 3:6] = var_imu_w * Q_k[3:6, 3:6]
        Q_k *= delta_t**2
        
        p_cov[k] = F_k @ p_cov[k-1] @ F_k.T + l_jac @ Q_k @ l_jac.T
        
        if lidar_i < lidar.t.shape[0] and abs(lidar.t[lidar_i] - imu_f.t[k-1]) < 0.001:
            p_est[k], v_est[k], q_est[k], p_cov[k] = measurement_update_ekf(
                var_lidar, p_cov[k], lidar.data[lidar_i].T.reshape(3, 1), 
                p_est[k].reshape(3, 1), v_est[k], q_est[k])
            lidar_i += 1
        if gnss_i < gnss.t.shape[0] and abs(gnss.t[gnss_i] - imu_f.t[k-1]) < 0.001:
            p_est[k], v_est[k], q_est[k], p_cov[k] = measurement_update_ekf(
                var_gnss, p_cov[k], gnss.data[gnss_i].T.reshape(3, 1), 
                p_est[k].reshape(3, 1), v_est[k], q_est[k])
            gnss_i += 1
    
    return p_est, v_est, q_est, p_cov


# ============================================================================
# 5. 运行所有滤波器
# ============================================================================
print("运行三个卡尔曼滤波器...\n")
print("运行标准卡尔曼滤波器 (KF)...")
kf_p, kf_v, kf_cov = run_kf()

print("运行扩展卡尔曼滤波器 (EKF)...")
ekf_p, ekf_v, ekf_q, ekf_cov = run_ekf()

print("运行错误状态卡尔曼滤波器 (ESKF)...")
eskf_p, eskf_v, eskf_q, eskf_cov = run_eskf()

print("所有滤波器运行完毕!\n")


# ============================================================================
# 6. 计算误差指标
# ============================================================================
def calculate_errors(p_est, gt_p, v_est, gt_v):
    """计算位置和速度误差"""
    min_len = min(len(p_est), len(gt_p), len(v_est), len(gt_v))
    p_est_trimmed = p_est[:min_len]
    gt_p_trimmed = gt_p[:min_len]
    v_est_trimmed = v_est[:min_len]
    gt_v_trimmed = gt_v[:min_len]
    
    p_error = p_est_trimmed - gt_p_trimmed
    v_error = v_est_trimmed - gt_v_trimmed
    
    p_rmse = np.sqrt(np.mean(np.sum(p_error**2, axis=1)))
    v_rmse = np.sqrt(np.mean(np.sum(v_error**2, axis=1)))
    
    p_mae = np.mean(np.linalg.norm(p_error, axis=1))
    v_mae = np.mean(np.linalg.norm(v_error, axis=1))
    
    return {
        'p_rmse': p_rmse,
        'v_rmse': v_rmse,
        'p_mae': p_mae,
        'v_mae': v_mae,
        'p_error': p_error,
        'v_error': v_error,
        'min_len': min_len
    }

kf_errors = calculate_errors(kf_p, gt.p, kf_v, gt.v)
ekf_errors = calculate_errors(ekf_p, gt.p, ekf_v, gt.v)
eskf_errors = calculate_errors(eskf_p, gt.p, eskf_v, gt.v)

print("=== 误差指标对比 ===\n")
print("KF (标准卡尔曼滤波器):")
print(f"  位置 RMSE: {kf_errors['p_rmse']:.4f} m")
print(f"  速度 RMSE: {kf_errors['v_rmse']:.4f} m/s")
print(f"  位置 MAE:  {kf_errors['p_mae']:.4f} m")
print(f"  速度 MAE:  {kf_errors['v_mae']:.4f} m/s\n")

print("EKF (扩展卡尔曼滤波器):")
print(f"  位置 RMSE: {ekf_errors['p_rmse']:.4f} m")
print(f"  速度 RMSE: {ekf_errors['v_rmse']:.4f} m/s")
print(f"  位置 MAE:  {ekf_errors['p_mae']:.4f} m")
print(f"  速度 MAE:  {ekf_errors['v_mae']:.4f} m/s\n")

print("ESKF (错误状态卡尔曼滤波器):")
print(f"  位置 RMSE: {eskf_errors['p_rmse']:.4f} m")
print(f"  速度 RMSE: {eskf_errors['v_rmse']:.4f} m/s")
print(f"  位置 MAE:  {eskf_errors['p_mae']:.4f} m")
print(f"  速度 MAE:  {eskf_errors['v_mae']:.4f} m/s\n")


# ============================================================================
# 7. 绘制对比结果
# ============================================================================

# 图1：3D轨迹对比
fig = plt.figure(figsize=(14, 10))

# 子图1：3D轨迹 - KF
ax1 = fig.add_subplot(2, 3, 1, projection='3d')
ax1.plot(gt.p[:, 0], gt.p[:, 1], gt.p[:, 2], 'k-', linewidth=2, label='Ground Truth')
ax1.plot(kf_p[:, 0], kf_p[:, 1], kf_p[:, 2], 'r--', alpha=0.7, label='KF')
ax1.scatter(gnss.data[:, 0], gnss.data[:, 1], gnss.data[:, 2], c='g', marker='o', s=20, label='GNSS')
ax1.set_xlabel('Easting [m]')
ax1.set_ylabel('Northing [m]')
ax1.set_zlabel('Up [m]')
ax1.set_title('KF 3D轨迹')
ax1.legend(fontsize=8)
ax1.view_init(elev=45, azim=-50)

# 子图2：3D轨迹 - EKF
ax2 = fig.add_subplot(2, 3, 2, projection='3d')
ax2.plot(gt.p[:, 0], gt.p[:, 1], gt.p[:, 2], 'k-', linewidth=2, label='Ground Truth')
ax2.plot(ekf_p[:, 0], ekf_p[:, 1], ekf_p[:, 2], 'b--', alpha=0.7, label='EKF')
ax2.scatter(gnss.data[:, 0], gnss.data[:, 1], gnss.data[:, 2], c='g', marker='o', s=20, label='GNSS')
ax2.set_xlabel('Easting [m]')
ax2.set_ylabel('Northing [m]')
ax2.set_zlabel('Up [m]')
ax2.set_title('EKF 3D轨迹')
ax2.legend(fontsize=8)
ax2.view_init(elev=45, azim=-50)

# 子图3：3D轨迹 - ESKF
ax3 = fig.add_subplot(2, 3, 3, projection='3d')
ax3.plot(gt.p[:, 0], gt.p[:, 1], gt.p[:, 2], 'k-', linewidth=2, label='Ground Truth')
ax3.plot(eskf_p[:, 0], eskf_p[:, 1], eskf_p[:, 2], 'orange', linestyle='--', alpha=0.7, label='ESKF')
ax3.scatter(gnss.data[:, 0], gnss.data[:, 1], gnss.data[:, 2], c='g', marker='o', s=20, label='GNSS')
ax3.set_xlabel('Easting [m]')
ax3.set_ylabel('Northing [m]')
ax3.set_zlabel('Up [m]')
ax3.set_title('ESKF 3D轨迹')
ax3.legend(fontsize=8)
ax3.view_init(elev=45, azim=-50)

# 子图4：位置误差随时间变化
ax4 = fig.add_subplot(2, 3, 4)
min_len = kf_errors['min_len']
time = imu_f.t[:min_len] / 1000
kf_p_error_norm = np.linalg.norm(kf_errors['p_error'], axis=1)
ekf_p_error_norm = np.linalg.norm(ekf_errors['p_error'], axis=1)
eskf_p_error_norm = np.linalg.norm(eskf_errors['p_error'], axis=1)

ax4.plot(time, kf_p_error_norm, 'r-', label='KF', alpha=0.7)
ax4.plot(time, ekf_p_error_norm, 'b-', label='EKF', alpha=0.7)
ax4.plot(time, eskf_p_error_norm, 'orange', label='ESKF', alpha=0.7)
ax4.set_xlabel('时间 [s]')
ax4.set_ylabel('位置误差 [m]')
ax4.set_title('位置误差随时间变化')
ax4.legend()
ax4.grid(True, alpha=0.3)

# 子图5：速度误差随时间变化
ax5 = fig.add_subplot(2, 3, 5)
kf_v_error_norm = np.linalg.norm(kf_errors['v_error'], axis=1)
ekf_v_error_norm = np.linalg.norm(ekf_errors['v_error'], axis=1)
eskf_v_error_norm = np.linalg.norm(eskf_errors['v_error'], axis=1)

ax5.plot(time, kf_v_error_norm, 'r-', label='KF', alpha=0.7)
ax5.plot(time, ekf_v_error_norm, 'b-', label='EKF', alpha=0.7)
ax5.plot(time, eskf_v_error_norm, 'orange', label='ESKF', alpha=0.7)
ax5.set_xlabel('时间 [s]')
ax5.set_ylabel('速度误差 [m/s]')
ax5.set_title('速度误差随时间变化')
ax5.legend()
ax5.grid(True, alpha=0.3)

# 子图6：误差指标条形图
ax6 = fig.add_subplot(2, 3, 6)
methods = ['KF', 'EKF', 'ESKF']
p_rmse = [kf_errors['p_rmse'], ekf_errors['p_rmse'], eskf_errors['p_rmse']]
x_pos = np.arange(len(methods))
width = 0.35

bars1 = ax6.bar(x_pos, p_rmse, width, label='位置RMSE', alpha=0.8, color=['red', 'blue', 'orange'])
ax6.set_ylabel('RMSE [m]')
ax6.set_title('位置误差RMSE对比')
ax6.set_xticks(x_pos)
ax6.set_xticklabels(methods)
ax6.grid(True, alpha=0.3, axis='y')

# 添加值标签
for bar in bars1:
    height = bar.get_height()
    ax6.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.3f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(Path(__file__).resolve().parent / 'result_images' / 'filter_comparison.png', dpi=150, bbox_inches='tight')
print("图表已保存到: result_images/filter_comparison.png")

# 图2：详细的X/Y/Z位置误差
fig2, axes = plt.subplots(3, 1, figsize=(12, 10))

# X方向
axes[0].plot(time, kf_errors['p_error'][:, 0], 'r-', label='KF', alpha=0.7)
axes[0].plot(time, ekf_errors['p_error'][:, 0], 'b-', label='EKF', alpha=0.7)
axes[0].plot(time, eskf_errors['p_error'][:, 0], 'orange', label='ESKF', alpha=0.7)
axes[0].axhline(0, color='k', linestyle='--', alpha=0.3)
axes[0].set_ylabel('X方向误差 [m]')
axes[0].set_title('X方向位置误差')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Y方向
axes[1].plot(time, kf_errors['p_error'][:, 1], 'r-', label='KF', alpha=0.7)
axes[1].plot(time, ekf_errors['p_error'][:, 1], 'b-', label='EKF', alpha=0.7)
axes[1].plot(time, eskf_errors['p_error'][:, 1], 'orange', label='ESKF', alpha=0.7)
axes[1].axhline(0, color='k', linestyle='--', alpha=0.3)
axes[1].set_ylabel('Y方向误差 [m]')
axes[1].set_title('Y方向位置误差')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Z方向
axes[2].plot(time, kf_errors['p_error'][:, 2], 'r-', label='KF', alpha=0.7)
axes[2].plot(time, ekf_errors['p_error'][:, 2], 'b-', label='EKF', alpha=0.7)
axes[2].plot(time, eskf_errors['p_error'][:, 2], 'orange', label='ESKF', alpha=0.7)
axes[2].axhline(0, color='k', linestyle='--', alpha=0.3)
axes[2].set_ylabel('Z方向误差 [m]')
axes[2].set_xlabel('时间 [s]')
axes[2].set_title('Z方向位置误差')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(Path(__file__).resolve().parent / 'result_images' / 'position_errors_xyz.png', dpi=150, bbox_inches='tight')
print("图表已保存到: result_images/position_errors_xyz.png")

plt.show()

# ============================================================================
# 8. EKF和ESKF单独对比 - 新增
# ============================================================================
print("\n" + "="*60)
print("EKF 与 ESKF 单独对比")
print("="*60)
print(f"\nEKF 位置 RMSE: {ekf_errors['p_rmse']:.4f} m")
print(f"ESKF 位置 RMSE: {eskf_errors['p_rmse']:.4f} m")
print(f"改进: {(ekf_errors['p_rmse'] - eskf_errors['p_rmse']) / ekf_errors['p_rmse'] * 100:.2f}%\n")

# 图3：EKF vs ESKF 3D轨迹对比
fig3 = plt.figure(figsize=(14, 6))

ax1 = fig3.add_subplot(1, 2, 1, projection='3d')
ax1.plot(gt.p[:, 0], gt.p[:, 1], gt.p[:, 2], 'k-', linewidth=2.5, label='真实轨迹')
ax1.plot(ekf_p[:, 0], ekf_p[:, 1], ekf_p[:, 2], 'b--', alpha=0.8, linewidth=2, label='EKF估计')
ax1.scatter(gnss.data[:, 0], gnss.data[:, 1], gnss.data[:, 2], c='g', marker='o', s=30, label='GNSS测量')
ax1.set_xlabel('东向 [m]')
ax1.set_ylabel('北向 [m]')
ax1.set_zlabel('竖向 [m]')
ax1.set_title('EKF 三维轨迹')
ax1.legend(fontsize=9)
ax1.view_init(elev=45, azim=-50)

ax2 = fig3.add_subplot(1, 2, 2, projection='3d')
ax2.plot(gt.p[:, 0], gt.p[:, 1], gt.p[:, 2], 'k-', linewidth=2.5, label='真实轨迹')
ax2.plot(eskf_p[:, 0], eskf_p[:, 1], eskf_p[:, 2], 'orange', linestyle='--', alpha=0.8, linewidth=2, label='ESKF估计')
ax2.scatter(gnss.data[:, 0], gnss.data[:, 1], gnss.data[:, 2], c='g', marker='o', s=30, label='GNSS测量')
ax2.set_xlabel('东向 [m]')
ax2.set_ylabel('北向 [m]')
ax2.set_zlabel('竖向 [m]')
ax2.set_title('ESKF 三维轨迹')
ax2.legend(fontsize=9)
ax2.view_init(elev=45, azim=-50)

plt.tight_layout()
plt.savefig(Path(__file__).resolve().parent / 'result_images' / 'ekf_vs_eskf_3d.png', dpi=150, bbox_inches='tight')
print("图表已保存到: result_images/ekf_vs_eskf_3d.png")

# 图4：EKF vs ESKF 误差详细对比
fig4, axes = plt.subplots(2, 2, figsize=(14, 10))

# 位置误差曲线
ax = axes[0, 0]
ekf_p_error_norm = np.linalg.norm(ekf_errors['p_error'], axis=1)
eskf_p_error_norm = np.linalg.norm(eskf_errors['p_error'], axis=1)
ax.plot(time, ekf_p_error_norm, 'b-', label='EKF', linewidth=2, alpha=0.8)
ax.plot(time, eskf_p_error_norm, 'orange', label='ESKF', linewidth=2, alpha=0.8)
ax.fill_between(time, ekf_p_error_norm, eskf_p_error_norm, alpha=0.2, color='green', label='改进区间')
ax.set_xlabel('时间 [s]')
ax.set_ylabel('位置误差 [m]')
ax.set_title('位置误差随时间变化')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# 速度误差曲线
ax = axes[0, 1]
ekf_v_error_norm = np.linalg.norm(ekf_errors['v_error'], axis=1)
eskf_v_error_norm = np.linalg.norm(eskf_errors['v_error'], axis=1)
ax.plot(time, ekf_v_error_norm, 'b-', label='EKF', linewidth=2, alpha=0.8)
ax.plot(time, eskf_v_error_norm, 'orange', label='ESKF', linewidth=2, alpha=0.8)
ax.fill_between(time, ekf_v_error_norm, eskf_v_error_norm, alpha=0.2, color='green', label='改进区间')
ax.set_xlabel('时间 [s]')
ax.set_ylabel('速度误差 [m/s]')
ax.set_title('速度误差随时间变化')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# 误差指标对比
ax = axes[1, 0]
methods = ['EKF', 'ESKF']
p_rmse = [ekf_errors['p_rmse'], eskf_errors['p_rmse']]
v_rmse = [ekf_errors['v_rmse'], eskf_errors['v_rmse']]
x_pos = np.arange(len(methods))
width = 0.35

bars1 = ax.bar(x_pos - width/2, p_rmse, width, label='位置RMSE', alpha=0.8, color=['blue', 'orange'])
bars2 = ax.bar(x_pos + width/2, v_rmse, width, label='速度RMSE', alpha=0.8, color=['lightblue', 'lightyellow'])

ax.set_ylabel('RMSE')
ax.set_title('误差指标对比（位置和速度）')
ax.set_xticks(x_pos)
ax.set_xticklabels(methods)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, axis='y')

# 添加值标签
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=8)

# X/Y/Z方向位置误差对比
ax = axes[1, 1]
x_indices = np.arange(3)
ekf_xyz_rmse = [np.sqrt(np.mean(ekf_errors['p_error'][:, i]**2)) for i in range(3)]
eskf_xyz_rmse = [np.sqrt(np.mean(eskf_errors['p_error'][:, i]**2)) for i in range(3)]
directions = ['X (东向)', 'Y (北向)', 'Z (竖向)']

bars1 = ax.bar(x_indices - width/2, ekf_xyz_rmse, width, label='EKF', alpha=0.8, color='blue')
bars2 = ax.bar(x_indices + width/2, eskf_xyz_rmse, width, label='ESKF', alpha=0.8, color='orange')

ax.set_ylabel('RMSE [m]')
ax.set_title('各方向位置误差RMSE对比')
ax.set_xticks(x_indices)
ax.set_xticklabels(directions)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, axis='y')

# 添加值标签
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig(Path(__file__).resolve().parent / 'result_images' / 'ekf_vs_eskf_detailed.png', dpi=150, bbox_inches='tight')
print("图表已保存到: result_images/ekf_vs_eskf_detailed.png")

# 图5：EKF vs ESKF X/Y/Z详细误差
fig5, axes = plt.subplots(3, 1, figsize=(14, 10))

# X方向
axes[0].plot(time, ekf_errors['p_error'][:, 0], 'b-', label='EKF', linewidth=2, alpha=0.8)
axes[0].plot(time, eskf_errors['p_error'][:, 0], 'orange', label='ESKF', linewidth=2, alpha=0.8)
axes[0].axhline(0, color='k', linestyle='--', alpha=0.3, linewidth=1)
axes[0].fill_between(time, ekf_errors['p_error'][:, 0], eskf_errors['p_error'][:, 0], 
                       alpha=0.2, color='green')
axes[0].set_ylabel('误差 [m]')
axes[0].set_title('X方向（东向）位置误差对比')
axes[0].legend(fontsize=9)
axes[0].grid(True, alpha=0.3)

# Y方向
axes[1].plot(time, ekf_errors['p_error'][:, 1], 'b-', label='EKF', linewidth=2, alpha=0.8)
axes[1].plot(time, eskf_errors['p_error'][:, 1], 'orange', label='ESKF', linewidth=2, alpha=0.8)
axes[1].axhline(0, color='k', linestyle='--', alpha=0.3, linewidth=1)
axes[1].fill_between(time, ekf_errors['p_error'][:, 1], eskf_errors['p_error'][:, 1], 
                       alpha=0.2, color='green')
axes[1].set_ylabel('误差 [m]')
axes[1].set_title('Y方向（北向）位置误差对比')
axes[1].legend(fontsize=9)
axes[1].grid(True, alpha=0.3)

# Z方向
axes[2].plot(time, ekf_errors['p_error'][:, 2], 'b-', label='EKF', linewidth=2, alpha=0.8)
axes[2].plot(time, eskf_errors['p_error'][:, 2], 'orange', label='ESKF', linewidth=2, alpha=0.8)
axes[2].axhline(0, color='k', linestyle='--', alpha=0.3, linewidth=1)
axes[2].fill_between(time, ekf_errors['p_error'][:, 2], eskf_errors['p_error'][:, 2], 
                       alpha=0.2, color='green')
axes[2].set_xlabel('时间 [s]')
axes[2].set_ylabel('误差 [m]')
axes[2].set_title('Z方向（竖向）位置误差对比')
axes[2].legend(fontsize=9)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(Path(__file__).resolve().parent / 'result_images' / 'ekf_vs_eskf_xyz.png', dpi=150, bbox_inches='tight')
print("图表已保存到: result_images/ekf_vs_eskf_xyz.png")

plt.show()
