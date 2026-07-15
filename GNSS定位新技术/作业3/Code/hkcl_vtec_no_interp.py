"""
批量处理 hkcl 目录中的 26o + 对应 SP3 文件，计算并绘制 VTEC。
输出图形风格与 main.py 的 2x2 分析图一致，不生成插值热力图。
"""

from __future__ import annotations

import re
import warnings
from bisect import bisect_left
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

font_list = ["SimSun", "SimHei", "FangSong", "DejaVu Sans"]
for font in font_list:
    try:
        plt.rcParams["font.sans-serif"] = [font]
        break
    except Exception:
        continue

if matplotlib.get_backend().lower() != "agg":
    plt.switch_backend("Agg")

plt.rcParams["axes.unicode_minus"] = False

FREQ_L1 = 1.57542e9
FREQ_L2 = 1.22760e9
FREQ_E5A = 1.17645e9
FREQ_E5B = 1.20714e9
FREQ_B2A = 1.16140e9
FREQ_B2B = 1.20714e9

RE_WGS84 = 6378137.0
F_WGS84 = 1.0 / 298.257223563
E2_WGS84 = 2 * F_WGS84 - F_WGS84 * F_WGS84
EARTH_RADIUS = 6371000.0
IONO_SHELL_HEIGHT = 350000.0


class RINEXReader:
    """RINEX 3.xx 观测文件读取器。"""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.header = {}
        self.data = {}
        self.obs_types = {}
        self.obs_indices = {}
        self.parse()

    def parse(self):
        with open(self.filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        header_end = 0
        for i, line in enumerate(lines):
            if "END OF HEADER" in line:
                header_end = i
                break

            if len(line) < 60:
                continue

            label = line[60:].strip()
            content = line[:60].strip()

            if label == "MARKER NAME":
                self.header["marker_name"] = content
            elif label == "APPROX POSITION XYZ":
                parts = content.split()
                if len(parts) >= 3:
                    try:
                        self.header["approx_pos"] = (float(parts[0]), float(parts[1]), float(parts[2]))
                    except Exception:
                        pass
            elif label == "SYS / # / OBS TYPES":
                sys_name = content[0] if content else "G"
                if sys_name not in self.obs_types:
                    self.obs_types[sys_name] = []
                obs_line = content[1:].strip()
                types = [t for t in obs_line.split() if not t.isdigit()]
                self.obs_types[sys_name].extend(types)

        for sys_name, types in self.obs_types.items():
            self.obs_indices[sys_name] = {t: idx for idx, t in enumerate(types)}

        current_epoch = None
        epoch_data = {}
        i = header_end + 1

        while i < len(lines):
            line = lines[i]
            if line.startswith(">"):
                if current_epoch is not None and epoch_data:
                    self.data[current_epoch] = epoch_data
                    epoch_data = {}

                try:
                    parts = line.split()
                    current_epoch = datetime(
                        int(parts[1]),
                        int(parts[2]),
                        int(parts[3]),
                        int(parts[4]),
                        int(parts[5]),
                        int(float(parts[6])),
                    )
                except Exception:
                    current_epoch = None
                i += 1
                continue

            if current_epoch is None or len(line) < 3:
                i += 1
                continue

            sat_id = line[:3].strip()
            if not sat_id:
                i += 1
                continue

            obs_values = []
            obs_str = line[3:]
            for j in range(0, len(obs_str), 16):
                chunk = obs_str[j : j + 16]
                if not chunk.strip():
                    obs_values.append(np.nan)
                    continue
                try:
                    obs_values.append(float(chunk[:14]))
                except Exception:
                    obs_values.append(np.nan)

            epoch_data[sat_id] = obs_values
            i += 1

        if current_epoch is not None and epoch_data:
            self.data[current_epoch] = epoch_data


class SP3Reader:
    """SP3 精密轨道读取器，支持线性插值。"""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.orbits = {}
        self.epochs = []
        self.parse()

    def parse(self):
        with open(self.filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        current_epoch = None
        for line in lines:
            if line.startswith("*"):
                try:
                    parts = line.split()
                    current_epoch = datetime(
                        int(parts[1]),
                        int(parts[2]),
                        int(parts[3]),
                        int(parts[4]),
                        int(parts[5]),
                        int(float(parts[6])),
                    )
                    if current_epoch not in self.orbits:
                        self.orbits[current_epoch] = {}
                except Exception:
                    current_epoch = None
                continue

            if current_epoch is None or not line.startswith("P"):
                continue

            try:
                sat_id = line[1:4].strip()
                x = float(line[4:18].strip())
                y = float(line[18:32].strip())
                z = float(line[32:46].strip())
                # SP3 坐标单位为 km
                self.orbits[current_epoch][sat_id] = (x * 1000.0, y * 1000.0, z * 1000.0)
            except Exception:
                continue

        self.epochs = sorted(self.orbits.keys())

    def get_sat_position(self, sat_id: str, epoch: datetime):
        if not self.epochs:
            return None

        idx = bisect_left(self.epochs, epoch)

        candidates = []
        if idx < len(self.epochs):
            candidates.append(self.epochs[idx])
        if idx > 0:
            candidates.append(self.epochs[idx - 1])

        exact_epoch = None
        for ep in candidates:
            if ep == epoch and sat_id in self.orbits.get(ep, {}):
                exact_epoch = ep
                break

        if exact_epoch is not None:
            return np.array(self.orbits[exact_epoch][sat_id], dtype=float)

        prev_ep = None
        next_ep = None

        for j in range(idx - 1, -1, -1):
            ep = self.epochs[j]
            if sat_id in self.orbits.get(ep, {}):
                prev_ep = ep
                break

        for j in range(idx, len(self.epochs)):
            ep = self.epochs[j]
            if sat_id in self.orbits.get(ep, {}):
                next_ep = ep
                break

        if prev_ep is None and next_ep is None:
            return None
        if prev_ep is None:
            if abs((next_ep - epoch).total_seconds()) <= 300:
                return np.array(self.orbits[next_ep][sat_id], dtype=float)
            return None
        if next_ep is None:
            if abs((epoch - prev_ep).total_seconds()) <= 300:
                return np.array(self.orbits[prev_ep][sat_id], dtype=float)
            return None

        total = (next_ep - prev_ep).total_seconds()
        if total <= 0:
            return np.array(self.orbits[prev_ep][sat_id], dtype=float)

        if abs((epoch - prev_ep).total_seconds()) > 600 and abs((next_ep - epoch).total_seconds()) > 600:
            return None

        p0 = np.array(self.orbits[prev_ep][sat_id], dtype=float)
        p1 = np.array(self.orbits[next_ep][sat_id], dtype=float)
        ratio = (epoch - prev_ep).total_seconds() / total
        return p0 + ratio * (p1 - p0)


def ecef_to_geodetic(x: float, y: float, z: float):
    lon = np.arctan2(y, x)
    p = np.sqrt(x * x + y * y)
    lat = np.arctan2(z, p * (1 - E2_WGS84))

    for _ in range(6):
        sin_lat = np.sin(lat)
        n = RE_WGS84 / np.sqrt(1 - E2_WGS84 * sin_lat * sin_lat)
        lat = np.arctan2(z + E2_WGS84 * n * sin_lat, p)

    return lat, lon


def elevation_angle_deg(sta_xyz: np.ndarray, sat_xyz: np.ndarray):
    lat, lon = ecef_to_geodetic(sta_xyz[0], sta_xyz[1], sta_xyz[2])

    dx = sat_xyz - sta_xyz
    sin_lat = np.sin(lat)
    cos_lat = np.cos(lat)
    sin_lon = np.sin(lon)
    cos_lon = np.cos(lon)

    # ECEF 到 ENU 旋转
    t = np.array(
        [
            [-sin_lon, cos_lon, 0],
            [-sin_lat * cos_lon, -sin_lat * sin_lon, cos_lat],
            [cos_lat * cos_lon, cos_lat * sin_lon, sin_lat],
        ]
    )

    enu = t @ dx
    horiz = np.sqrt(enu[0] ** 2 + enu[1] ** 2)
    if horiz <= 1e-9 and abs(enu[2]) <= 1e-9:
        return None
    elev = np.degrees(np.arctan2(enu[2], horiz))
    return float(elev)


def calc_stec_tecu(p1: float, p2: float, f1: float, f2: float):
    if np.isnan(p1) or np.isnan(p2) or p1 <= 0 or p2 <= 0:
        return np.nan

    f1_sq = f1 * f1
    f2_sq = f2 * f2
    denom = 40.308e16 * (f1_sq - f2_sq)
    if abs(denom) < 1e-12:
        return np.nan

    return (f1_sq * f2_sq * abs(p2 - p1)) / abs(denom)


def mapping_function(elev_deg: float):
    if elev_deg is None or elev_deg <= 0:
        return np.nan

    elev_rad = np.radians(elev_deg)
    cos_z = np.cos(elev_rad)
    ratio = (EARTH_RADIUS * cos_z) / (EARTH_RADIUS + IONO_SHELL_HEIGHT)
    inside = 1.0 - ratio * ratio
    if inside <= 1e-8:
        return np.nan

    return 1.0 / np.sqrt(inside)


def select_dual_frequency(sys_type: str, indices: dict, obs_values: list):
    c1_val = None
    c2_val = None
    freq1 = FREQ_L1
    freq2 = FREQ_L2

    def read_pair(code1: str, code2: str):
        if code1 in indices and code2 in indices:
            i1 = indices[code1]
            i2 = indices[code2]
            if len(obs_values) > max(i1, i2):
                return obs_values[i1], obs_values[i2]
        return None, None

    if sys_type == "G":
        for p1, p2 in [("C1C", "C2W"), ("C1C", "C2S"), ("C1C", "C2X")]:
            c1_val, c2_val = read_pair(p1, p2)
            if c1_val is not None:
                break
    elif sys_type == "R":
        for p1, p2 in [("C1C", "C2C"), ("C1C", "C2P")]:
            c1_val, c2_val = read_pair(p1, p2)
            if c1_val is not None:
                break
    elif sys_type == "E":
        c1_val, c2_val = read_pair("C1X", "C7X")
        if c1_val is not None:
            freq1 = FREQ_E5A
            freq2 = FREQ_E5B
        else:
            c1_val, c2_val = read_pair("C1C", "C7X")
            if c1_val is not None:
                freq1 = FREQ_L1
                freq2 = FREQ_E5B
    elif sys_type == "C":
        c1_val, c2_val = read_pair("C2I", "C7I")
        if c1_val is not None:
            freq1 = FREQ_B2A
            freq2 = FREQ_B2B
        else:
            c1_val, c2_val = read_pair("C2I", "C5X")
    elif sys_type == "J":
        for p1, p2 in [("C1C", "C2X"), ("C1C", "C2S")]:
            c1_val, c2_val = read_pair(p1, p2)
            if c1_val is not None:
                break

    return c1_val, c2_val, freq1, freq2


def find_matching_sp3(hkcl_dir: Path, rinex_name: str):
    match = re.search(r"_(\d{7})\d{4}_", rinex_name)
    if not match:
        return None
    yydoy = match.group(1)

    candidates = sorted(hkcl_dir.glob(f"*_{yydoy}0000_*_ORB.SP3"))
    if candidates:
        return candidates[0]
    return None


def process_hkcl_data(work_dir: Path):
    hkcl_dir = work_dir / "hklm"
    output_dir = work_dir / "output" / "hklm_no_interp"
    output_dir.mkdir(parents=True, exist_ok=True)

    rinex_files = sorted(hkcl_dir.glob("*.26o"))
    print(f"找到 {len(rinex_files)} 个 26o 文件")

    results = {}

    for rinex_file in rinex_files:
        sp3_file = find_matching_sp3(hkcl_dir, rinex_file.name)
        if sp3_file is None:
            print(f"[跳过] {rinex_file.name} 未找到对应 SP3")
            continue

        print(f"\n处理: {rinex_file.name}")
        print(f"对应SP3: {sp3_file.name}")

        rinex = RINEXReader(rinex_file)
        sp3 = SP3Reader(sp3_file)

        sta_pos = rinex.header.get("approx_pos")
        if sta_pos is None:
            print("  [跳过] 缺少测站坐标(APPROX POSITION XYZ)")
            continue

        sta_xyz = np.array(sta_pos, dtype=float)
        station_key = rinex_file.stem
        station_vtec = []

        total_epochs = 0
        valid_epochs = 0
        valid_sats = 0

        for epoch, satellites in sorted(rinex.data.items()):
            total_epochs += 1
            epoch_vals = []

            for sat_id, obs_values in satellites.items():
                sys_type = sat_id[0]
                indices = rinex.obs_indices.get(sys_type)
                if not indices:
                    continue

                c1, c2, f1, f2 = select_dual_frequency(sys_type, indices, obs_values)
                if c1 is None or c2 is None:
                    continue
                if np.isnan(c1) or np.isnan(c2):
                    continue

                sat_xyz = sp3.get_sat_position(sat_id, epoch)
                if sat_xyz is None:
                    continue

                elev = elevation_angle_deg(sta_xyz, sat_xyz)
                if elev is None or elev < 10.0:
                    continue

                stec = calc_stec_tecu(c1, c2, f1, f2)
                if np.isnan(stec):
                    continue

                mf = mapping_function(elev)
                if np.isnan(mf) or mf <= 0:
                    continue

                vtec = stec / mf
                if np.isfinite(vtec) and 0 < vtec < 500:
                    epoch_vals.append(vtec)
                    valid_sats += 1

            if epoch_vals:
                station_vtec.append(
                    {
                        "epoch": epoch,
                        "vtec": float(np.mean(epoch_vals)),
                        "sat_count": len(epoch_vals),
                    }
                )
                valid_epochs += 1

        if station_vtec:
            results[station_key] = station_vtec
            print(
                f"  [OK] VTEC历元 {len(station_vtec)} (总epochs: {total_epochs}, 有效epochs: {valid_epochs}, 有效卫星: {valid_sats})"
            )
        else:
            print(
                f"  [失败] 未获得有效VTEC (总epochs: {total_epochs}, 有效卫星: {valid_sats})"
            )

    return results, output_dir


def save_vtec_to_csv(vtec_results: dict, output_dir: Path):
    for station, data in vtec_results.items():
        df = pd.DataFrame(data)
        out = output_dir / f"{station}_VTEC.csv"
        df.to_csv(out, index=False)
        print(f"已保存CSV: {out.name}")


def plot_vtec_data(vtec_results: dict, output_dir: Path):
    for station, data in vtec_results.items():
        df = pd.DataFrame(data)
        if df.empty:
            continue

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.patch.set_facecolor("white")
        fig.suptitle(f"{station} VTEC数据分析", fontsize=16, fontweight="bold", y=0.995)

        ax1 = axes[0, 0]
        x_axis = np.arange(len(df))
        ax1.plot(x_axis, df["vtec"].values, linewidth=2, color="#1f77b4", marker="o", markersize=2, alpha=0.8)
        ax1.fill_between(x_axis, df["vtec"].values, alpha=0.2, color="#1f77b4")
        ax1.set_xlabel("时间索引（30秒间隔）", fontsize=10)
        ax1.set_ylabel("VTEC (TECU)", fontsize=10)
        ax1.set_title("VTEC时间序列", fontsize=11, fontweight="bold", pad=10)
        ax1.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)
        ax1.set_facecolor("#f8f9fa")

        n_ticks = min(10, max(1, len(df) // 288))
        tick_positions = np.linspace(0, len(df) - 1, n_ticks, dtype=int)
        ax1.set_xticks(tick_positions)
        tick_labels = [pd.to_datetime(df["epoch"].iloc[i]).strftime("%H:%M") for i in tick_positions]
        ax1.set_xticklabels(tick_labels, rotation=45, fontsize=8)

        ax2 = axes[0, 1]
        _, _, patches = ax2.hist(df["vtec"], bins=30, color="#ff7f0e", edgecolor="black", alpha=0.7)
        cm = plt.cm.Oranges
        for i, patch in enumerate(patches):
            patch.set_facecolor(cm(0.4 + 0.6 * i / max(1, len(patches))))
        mean_val = float(df["vtec"].mean())
        ax2.axvline(mean_val, color="red", linestyle="--", linewidth=2.5, label=f"平均: {mean_val:.2f} TECU")
        ax2.set_xlabel("VTEC (TECU)", fontsize=10)
        ax2.set_ylabel("频数", fontsize=10)
        ax2.set_title("VTEC分布直方图", fontsize=11, fontweight="bold", pad=10)
        ax2.legend(fontsize=9, loc="upper right")
        ax2.grid(True, alpha=0.3, axis="y", linestyle="--", linewidth=0.5)
        ax2.set_facecolor("#f8f9fa")

        ax3 = axes[1, 0]
        ax3.boxplot(
            df["vtec"],
            vert=True,
            patch_artist=True,
            widths=0.5,
            boxprops=dict(facecolor="#2ca02c", alpha=0.7),
            medianprops=dict(color="red", linewidth=2),
            whiskerprops=dict(color="black", linewidth=1.5),
            capprops=dict(color="black", linewidth=1.5),
            flierprops=dict(marker="o", markerfacecolor="red", markersize=5, alpha=0.5),
        )
        ax3.set_ylabel("VTEC (TECU)", fontsize=10)
        ax3.set_title("VTEC箱线图统计", fontsize=11, fontweight="bold", pad=10)
        ax3.set_xticklabels([station])
        ax3.grid(True, alpha=0.3, axis="y", linestyle="--", linewidth=0.5)
        ax3.set_facecolor("#f8f9fa")

        q1 = float(df["vtec"].quantile(0.25))
        q3 = float(df["vtec"].quantile(0.75))
        median = float(df["vtec"].median())
        stats_text = f"Q1: {q1:.1f}\nMedian: {median:.1f}\nQ3: {q3:.1f}"
        ax3.text(1.25, q1, stats_text, fontsize=8, bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

        ax4 = axes[1, 1]
        scatter = ax4.scatter(
            df["sat_count"],
            df["vtec"],
            c=range(len(df)),
            cmap="viridis",
            s=60,
            alpha=0.6,
            edgecolors="black",
            linewidth=0.5,
        )
        ax4.set_xlabel("可见卫星数", fontsize=10)
        ax4.set_ylabel("VTEC (TECU)", fontsize=10)
        ax4.set_title("卫星数 vs VTEC", fontsize=11, fontweight="bold", pad=10)
        ax4.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)
        ax4.set_facecolor("#f8f9fa")

        if len(df) >= 3 and df["sat_count"].nunique() > 1:
            z = np.polyfit(df["sat_count"], df["vtec"], 2)
            p = np.poly1d(z)
            x_trend = np.linspace(df["sat_count"].min(), df["sat_count"].max(), 100)
            ax4.plot(x_trend, p(x_trend), "r--", linewidth=2, alpha=0.6, label="趋势线")
            ax4.legend(fontsize=9)

        cbar = plt.colorbar(scatter, ax=ax4)
        cbar.set_label("时间顺序", fontsize=9)

        plt.tight_layout()
        out_png = output_dir / f"{station}_VTEC_plot.png"
        plt.savefig(out_png, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)

        print(f"已保存图表: {out_png.name}")


def plot_all_vtec_in_one(vtec_results: dict, output_dir: Path):
    """将所有文件的VTEC时间序列绘制到同一张图。"""
    if not vtec_results:
        return

    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor("white")

    colors = plt.cm.tab20(np.linspace(0, 1, max(2, len(vtec_results))))
    for (station, data), color in zip(sorted(vtec_results.items()), colors):
        df = pd.DataFrame(data)
        if df.empty:
            continue

        df = df.sort_values("epoch")
        ax.plot(
            pd.to_datetime(df["epoch"]),
            df["vtec"],
            marker="o",
            markersize=2,
            linewidth=1.6,
            alpha=0.8,
            color=color,
            label=station,
        )

    ax.set_xlabel("时间", fontsize=12, fontweight="bold")
    ax.set_ylabel("VTEC (TECU)", fontsize=12, fontweight="bold")
    ax.set_title("hklm全部文件 VTEC 对比", fontsize=14, fontweight="bold", pad=16)
    ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)
    ax.set_facecolor("#f8f9fa")
    ax.legend(loc="upper left", fontsize=9, ncol=2, framealpha=0.95, edgecolor="black")
    plt.xticks(rotation=45, fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()

    out_png = output_dir / "HKLM_全部文件_VTEC同图.png"
    plt.savefig(out_png, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"已保存汇总图: {out_png.name}")


def split_station_id(file_stem: str):
    """从文件名中提取测站ID, 如 HKCL00HKG_R_xxx -> HKCL00HKG。"""
    if "_R_" in file_stem:
        return file_stem.split("_R_")[0]
    return file_stem


def generate_storm_window_products(vtec_results: dict, output_dir: Path, event_date_str: str = "2026-01-19", window_days: int = 3):
    """
    生成同一测站在磁暴日前后窗口的分析产物:
    1) 7天同站重叠曲线图
    2) 前期/主相/后期对比统计表CSV
    """
    if not vtec_results:
        return

    event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
    start_date = event_date - timedelta(days=window_days)
    end_date = event_date + timedelta(days=window_days)

    grouped = {}
    for file_key, records in vtec_results.items():
        if not records:
            continue

        station_id = split_station_id(file_key)
        day = pd.to_datetime(records[0]["epoch"]).date()
        if day < start_date or day > end_date:
            continue

        if station_id not in grouped:
            grouped[station_id] = {}
        grouped[station_id][day] = pd.DataFrame(records)

    if not grouped:
        print("未找到事件窗口内可用数据")
        return

    for station_id, day_map in grouped.items():
        ordered_days = [start_date + timedelta(days=i) for i in range(2 * window_days + 1)]
        available_days = [d for d in ordered_days if d in day_map]

        if not available_days:
            continue

        fig, ax = plt.subplots(figsize=(14, 8))
        fig.patch.set_facecolor("white")
        colors = plt.cm.tab10(np.linspace(0, 1, max(2, len(available_days))))

        for d, color in zip(available_days, colors):
            df = day_map[d].copy()
            df["epoch"] = pd.to_datetime(df["epoch"])
            df = df.sort_values("epoch")

            sod = (
                df["epoch"].dt.hour * 3600
                + df["epoch"].dt.minute * 60
                + df["epoch"].dt.second
            )

            ax.plot(
                sod,
                df["vtec"],
                linewidth=1.6,
                marker="o",
                markersize=1.6,
                alpha=0.82,
                color=color,
                label=d.strftime("%Y-%m-%d"),
            )

        tick_seconds = np.arange(0, 24 * 3600 + 1, 2 * 3600)
        tick_labels = [f"{int(t // 3600):02d}:00" for t in tick_seconds]
        ax.set_xticks(tick_seconds)
        ax.set_xticklabels(tick_labels, rotation=45, fontsize=9)
        ax.set_xlabel("时刻 (HH:MM)", fontsize=12, fontweight="bold")
        ax.set_ylabel("VTEC (TECU)", fontsize=12, fontweight="bold")
        ax.set_title(
            f"{station_id} {event_date_str}前后3天 VTEC重叠曲线",
            fontsize=14,
            fontweight="bold",
            pad=16,
        )
        ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)
        ax.set_facecolor("#f8f9fa")
        ax.legend(loc="upper left", fontsize=9, ncol=2, framealpha=0.95, edgecolor="black")
        plt.yticks(fontsize=9)
        plt.tight_layout()

        overlay_png = output_dir / f"{station_id}_{event_date.strftime('%Y%m%d')}_前后3天_重叠曲线.png"
        plt.savefig(overlay_png, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"已保存重叠曲线图: {overlay_png.name}")

        period_values = {
            "前期": [],
            "主相": [],
            "后期": [],
        }

        for d in available_days:
            vals = day_map[d]["vtec"].to_numpy(dtype=float)
            vals = vals[np.isfinite(vals)]
            if vals.size == 0:
                continue

            if d < event_date:
                period_values["前期"].append(vals)
            elif d == event_date:
                period_values["主相"].append(vals)
            else:
                period_values["后期"].append(vals)

        stat_rows = []
        for period_name in ["前期", "主相", "后期"]:
            if period_values[period_name]:
                merged = np.concatenate(period_values[period_name])
            else:
                merged = np.array([], dtype=float)

            if merged.size == 0:
                stat_rows.append(
                    {
                        "station": station_id,
                        "period": period_name,
                        "event_date": event_date_str,
                        "day_count": 0,
                        "sample_count": 0,
                        "vtec_mean": np.nan,
                        "vtec_median": np.nan,
                        "vtec_std": np.nan,
                        "vtec_min": np.nan,
                        "vtec_max": np.nan,
                        "vtec_p95": np.nan,
                    }
                )
                continue

            stat_rows.append(
                {
                    "station": station_id,
                    "period": period_name,
                    "event_date": event_date_str,
                    "day_count": len(period_values[period_name]),
                    "sample_count": int(merged.size),
                    "vtec_mean": float(np.mean(merged)),
                    "vtec_median": float(np.median(merged)),
                    "vtec_std": float(np.std(merged, ddof=1)) if merged.size > 1 else 0.0,
                    "vtec_min": float(np.min(merged)),
                    "vtec_max": float(np.max(merged)),
                    "vtec_p95": float(np.percentile(merged, 95)),
                }
            )

        stat_df = pd.DataFrame(stat_rows)
        stat_csv = output_dir / f"{station_id}_{event_date.strftime('%Y%m%d')}_前主后_对比统计.csv"
        stat_df.to_csv(stat_csv, index=False, encoding="utf-8-sig")
        print(f"已保存对比统计CSV: {stat_csv.name}")


def main():
    code_dir = Path(__file__).resolve().parent

    print("=" * 56)
    print("hkcl目录 VTEC处理（无插值热力图）")
    print("=" * 56)
    print(f"工作目录: {code_dir}")

    vtec_results, output_dir = process_hkcl_data(code_dir)
    if not vtec_results:
        print("未得到可用VTEC结果")
        return

    print(f"\n成功处理 {len(vtec_results)} 个文件")
    save_vtec_to_csv(vtec_results, output_dir)
    plot_vtec_data(vtec_results, output_dir)
    plot_all_vtec_in_one(vtec_results, output_dir)
    generate_storm_window_products(vtec_results, output_dir, event_date_str="2026-01-19", window_days=3)

    print("\n处理完成")
    print(f"输出目录: {output_dir}")


if __name__ == "__main__":
    main()
