"""
Plot PPP positioning accuracy from CSV results
Generates 4 accuracy visualization figures
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import os

# Get script directory and construct full path to CSV file
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_filename = os.path.join(script_dir, 'test_pppigs_results.csv')

# Check if CSV file exists
if not os.path.exists(csv_filename):
    print(f"错误: 找不到文件 '{csv_filename}'")
    print("请先运行 test_pppigs.py 生成CSV结果文件")
    print("执行命令: python test_pppigs.py")
    exit(1)

print(f"读取文件: {csv_filename}")

df = pd.read_csv(csv_filename)

# Extract data
enu = np.array([df['East(m)'], df['North(m)'], df['Up(m)']]).T
smode = df['Mode'].values
t = np.arange(len(smode)) * 30 / 86400.0  # Time in days (30s per epoch)

# Calculate 2D horizontal error
h_2d = np.sqrt(enu[:, 0]**2 + enu[:, 1]**2)

# Get indices for different modes
idx0 = np.where(smode == 0)[0]  # no solution
idx5 = np.where(smode == 5)[0]  # float
idx4 = np.where(smode == 4)[0]  # fix

print(f"Total epochs: {len(smode)}")
print(f"No solution: {len(idx0)}")
print(f"Float solution: {len(idx5)}")
print(f"Fixed solution: {len(idx4)}")
print()

# ========== Figure 1: CEP (Circular Error Probability) ==========
fig1, ax1 = plt.subplots(figsize=[9, 9])

mode_info = [(idx0, 'r', 'no solution'), 
             (idx5, 'y', 'float'), 
             (idx4, 'g', 'fix')]

for idx, color, label in mode_info:
    if len(idx) > 0:
        ax1.scatter(enu[idx, 0], enu[idx, 1], c=color, alpha=0.6, s=20, label=label)

ax1.set_xlabel('East [m]', fontsize=12)
ax1.set_ylabel('North [m]', fontsize=12)
ax1.set_title('Horizontal Position Error Distribution (CEP)', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.axis('equal')
ax1.legend(fontsize=11)

fig1.savefig('accuracy_cep.png', dpi=300, bbox_inches='tight')
fig1.savefig('accuracy_cep.eps', format='eps', bbox_inches='tight')
print("Figure 1 saved: accuracy_cep.png")

# ========== Figure 2: Error Distribution Histograms ==========
fig2, axes = plt.subplots(1, 3, figsize=[15, 4])
labels = ['East', 'North', 'Up']

for i, label in enumerate(labels):
    valid_mask = ~np.isnan(enu[:, i])
    axes[i].hist(enu[valid_mask, i], bins=50, edgecolor='black', alpha=0.7, color='steelblue')
    axes[i].set_xlabel(f'{label} Error [m]', fontsize=11)
    axes[i].set_ylabel('Frequency', fontsize=11)
    axes[i].set_title(f'{label} Error Distribution', fontsize=12, fontweight='bold')
    axes[i].grid(True, alpha=0.3)
    
    # Print statistics
    mean_err = np.nanmean(enu[valid_mask, i])
    std_err = np.nanstd(enu[valid_mask, i])
    print(f"{label}: Mean={mean_err:.4f}m, RMS={std_err:.4f}m")

plt.tight_layout()
fig2.savefig('accuracy_histogram.png', dpi=300, bbox_inches='tight')
fig2.savefig('accuracy_histogram.eps', format='eps', bbox_inches='tight')
print("Figure 2 saved: accuracy_histogram.png\n")

# ========== Figure 3: 3D Position Error ==========
fig3 = plt.figure(figsize=[10, 8])
ax3 = fig3.add_subplot(111, projection='3d')

for idx, color, label in mode_info:
    if len(idx) > 0:
        ax3.scatter(enu[idx, 0], enu[idx, 1], enu[idx, 2], 
                   c=color, alpha=0.6, s=20, label=label)

ax3.set_xlabel('East [m]', fontsize=11)
ax3.set_ylabel('North [m]', fontsize=11)
ax3.set_zlabel('Up [m]', fontsize=11)
ax3.set_title('3D Position Error Distribution', fontsize=14, fontweight='bold')
ax3.legend(fontsize=11)

fig3.savefig('accuracy_3d.png', dpi=300, bbox_inches='tight')
fig3.savefig('accuracy_3d.eps', format='eps', bbox_inches='tight')
print("Figure 3 saved: accuracy_3d.png")

# ========== Figure 4: RMS vs Time and CDF ==========
fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=[14, 5])

# Subplot 4a: Positioning accuracy vs time
for idx, color, label in mode_info:
    if len(idx) > 0:
        ax4a.plot(t[idx], h_2d[idx], '.', color=color, label=label, alpha=0.6, markersize=4)

ax4a.set_ylabel('Horizontal Error 2D [m]', fontsize=11)
ax4a.set_xlabel('Time [day]', fontsize=11)
ax4a.set_title('Positioning Accuracy vs Time', fontsize=12, fontweight='bold')
ax4a.grid(True, alpha=0.3)
ax4a.legend(fontsize=10)

# Subplot 4b: Cumulative Distribution Function (CDF)
if len(idx4) > 0:
    h_2d_fix = np.sort(h_2d[idx4])
    cdf = np.linspace(0, 100, len(h_2d_fix))
    ax4b.plot(h_2d_fix, cdf, 'g-', linewidth=2.5, label='Fixed solution')
    
    # Calculate percentiles
    p50 = np.percentile(h_2d_fix, 50)
    p95 = np.percentile(h_2d_fix, 95)
    ax4b.axvline(p50, color='g', linestyle='--', alpha=0.5, label=f'50%: {p50:.3f}m')
    ax4b.axvline(p95, color='r', linestyle='--', alpha=0.5, label=f'95%: {p95:.3f}m')
    
    print(f"Fixed solution CDF statistics:")
    print(f"  50% (Median): {p50:.4f}m")
    print(f"  95%: {p95:.4f}m")

ax4b.set_xlabel('Horizontal Error [m]', fontsize=11)
ax4b.set_ylabel('Cumulative Probability [%]', fontsize=11)
ax4b.set_title('CDF of Fixed Solution Accuracy', fontsize=12, fontweight='bold')
ax4b.grid(True, alpha=0.3)
ax4b.legend(fontsize=10)

plt.tight_layout()
fig4.savefig('accuracy_rms_cdf.png', dpi=300, bbox_inches='tight')
fig4.savefig('accuracy_rms_cdf.eps', format='eps', bbox_inches='tight')
print("Figure 4 saved: accuracy_rms_cdf.png\n")

# ========== Print Summary Statistics ==========
print("="*50)
print("SUMMARY STATISTICS")
print("="*50)

for idx, mode_name in [(idx0, "No Solution"), (idx5, "Float"), (idx4, "Fixed")]:
    if len(idx) > 0:
        print(f"\n{mode_name} (N={len(idx)}):")
        h_2d_mode = h_2d[idx]
        print(f"  Horizontal (2D):")
        print(f"    Mean:    {np.nanmean(h_2d_mode):.4f} m")
        print(f"    RMS:     {np.nanstd(h_2d_mode):.4f} m")
        print(f"    Max:     {np.nanmax(h_2d_mode):.4f} m")
        print(f"  Vertical (Up):")
        print(f"    Mean:    {np.nanmean(enu[idx, 2]):.4f} m")
        print(f"    RMS:     {np.nanstd(enu[idx, 2]):.4f} m")
        print(f"    Max:     {np.nanmax(enu[idx, 2]):.4f} m")

print("\n" + "="*50)
print("All figures saved successfully!")
print("="*50)

plt.show()
