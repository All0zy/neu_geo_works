"""
Batch VTEC processing for observation files in obv/ using matching SP3 orbit files.
Supports mixed RINEX v2/v3 observation formats.
Outputs per-file CSV + 4-subplot figure and one overlapped comparison plot.
"""

from __future__ import annotations

import math
import re
import warnings
from bisect import bisect_left
from datetime import datetime
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

if matplotlib.get_backend().lower() != "agg":
    plt.switch_backend("Agg")

plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.sans-serif"] = ["SimHei", "SimSun", "DejaVu Sans"]

# Frequencies (Hz)
FREQ_L1 = 1.57542e9
FREQ_L2 = 1.22760e9
FREQ_E5A = 1.17645e9
FREQ_E5B = 1.20714e9
FREQ_B2A = 1.16140e9
FREQ_B2B = 1.20714e9

# Geometry
RE_WGS84 = 6378137.0
F_WGS84 = 1.0 / 298.257223563
E2_WGS84 = 2 * F_WGS84 - F_WGS84 * F_WGS84
EARTH_RADIUS = 6371000.0
IONO_SHELL_HEIGHT = 350000.0


class MixedRINEXReader:
    """Reader for mixed RINEX v2/v3 observation files."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.version = 0.0
        self.header = {}
        self.obs_types_sys = {}
        self.obs_types_global = []
        self.obs_indices = {}
        self.data = {}
        self.parse()

    def parse(self):
        with open(self.filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        header_end = self._parse_header(lines)
        self._build_obs_indices()

        data_lines = lines[header_end + 1 :]
        if self.version >= 3.0:
            self._parse_v3(data_lines)
        else:
            self._parse_v2(data_lines)

    def _parse_header(self, lines):
        i = 0
        while i < len(lines):
            line = lines[i]
            if "END OF HEADER" in line:
                return i

            label = line[60:].strip() if len(line) >= 60 else ""
            content = line[:60]

            if label == "RINEX VERSION / TYPE":
                try:
                    self.version = float(content[:9].strip())
                except Exception:
                    self.version = 0.0

            elif label == "MARKER NAME":
                self.header["marker_name"] = content.strip()

            elif label == "APPROX POSITION XYZ":
                parts = content.split()
                if len(parts) >= 3:
                    try:
                        self.header["approx_pos"] = (float(parts[0]), float(parts[1]), float(parts[2]))
                    except Exception:
                        pass

            elif label == "SYS / # / OBS TYPES":
                sys_name = content[0] if content else "G"
                cnt = int(content[3:6]) if content[3:6].strip() else 0
                types = content[7:60].split()
                while len(types) < cnt and i + 1 < len(lines):
                    if "SYS / # / OBS TYPES" not in lines[i + 1][60:]:
                        break
                    i += 1
                    types.extend(lines[i][7:60].split())
                self.obs_types_sys[sys_name] = types[:cnt]

            elif label == "# / TYPES OF OBSERV":
                cnt = int(content[0:6]) if content[0:6].strip() else 0
                types = content[6:60].split()
                while len(types) < cnt and i + 1 < len(lines):
                    if "# / TYPES OF OBSERV" not in lines[i + 1][60:]:
                        break
                    i += 1
                    types.extend(lines[i][6:60].split())
                self.obs_types_global = types[:cnt]

            i += 1

        return max(0, len(lines) - 1)

    def _build_obs_indices(self):
        if self.obs_types_sys:
            for sys_name, types in self.obs_types_sys.items():
                self.obs_indices[sys_name] = {t: idx for idx, t in enumerate(types)}
        elif self.obs_types_global:
            default_systems = ["G", "R", "E", "C", "J", "S"]
            for sys_name in default_systems:
                self.obs_indices[sys_name] = {t: idx for idx, t in enumerate(self.obs_types_global)}

    def _parse_v3(self, lines):
        i = 0
        current_epoch = None
        while i < len(lines):
            line = lines[i]
            if not line.startswith(">"):
                i += 1
                continue

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
                nsat = int(parts[8]) if len(parts) > 8 else 0
            except Exception:
                i += 1
                continue

            i += 1
            epoch_data = {}
            sat_read = 0
            while i < len(lines) and sat_read < nsat:
                row = lines[i]
                if row.startswith(">"):
                    i -= 1
                    break

                sat_id = row[:3].strip()
                if sat_id:
                    values = self._parse_obs_line_chunks(row[3:], max_chunks=None)
                    epoch_data[sat_id] = values
                    sat_read += 1
                i += 1

            if current_epoch and epoch_data:
                self.data[current_epoch] = epoch_data
            i += 1

    def _parse_v2(self, lines):
        i = 0
        while i < len(lines):
            line = lines[i]
            if len(line) < 32:
                i += 1
                continue

            try:
                yy = int(line[1:3])
                year = yy + 2000 if yy < 80 else yy + 1900
                month = int(line[4:6])
                day = int(line[7:9])
                hour = int(line[10:12])
                minute = int(line[13:15])
                sec = int(float(line[15:26]))
                flag = int(line[28:29]) if line[28:29].strip() else 0
                nsat = int(line[29:32]) if line[29:32].strip() else 0
            except Exception:
                i += 1
                continue

            epoch = datetime(year, month, day, hour, minute, sec)

            # Event records in RINEX2: skip announced lines.
            if flag > 1:
                i += 1 + max(nsat, 0)
                continue

            sat_tokens = []
            sat_text = line[32:68]
            sat_tokens.extend([sat_text[j : j + 3] for j in range(0, len(sat_text), 3)])
            sat_ids = [s.strip() for s in sat_tokens if s.strip()]

            while len(sat_ids) < nsat and i + 1 < len(lines):
                i += 1
                cont = lines[i]
                sat_tokens = [cont[j : j + 3] for j in range(32, min(len(cont), 68), 3)]
                sat_ids.extend([s.strip() for s in sat_tokens if s.strip()])

            epoch_data = {}
            for sat_raw in sat_ids[:nsat]:
                i += 1
                if i >= len(lines):
                    break

                sys_name, sat_id = self._normalize_sat_id(sat_raw)
                obs_types = self.obs_types_sys.get(sys_name, self.obs_types_global)
                n_obs = len(obs_types)
                n_lines = max(1, math.ceil(n_obs / 5.0))

                obs_lines = [lines[i]]
                for _ in range(n_lines - 1):
                    i += 1
                    if i >= len(lines):
                        break
                    obs_lines.append(lines[i])

                values = []
                for li, obs_line in enumerate(obs_lines):
                    # RINEX2 观测记录行没有卫星号前缀，首行同样从第1列开始按16字符切片。
                    offset = 0
                    for k in range(5):
                        start = offset + 16 * k
                        end = start + 16
                        chunk = obs_line[start:end]
                        if not chunk:
                            continue
                        field = chunk[:14].strip()
                        if field:
                            try:
                                values.append(float(field))
                            except Exception:
                                values.append(np.nan)
                        else:
                            values.append(np.nan)
                        if len(values) >= n_obs:
                            break
                    if len(values) >= n_obs:
                        break

                if len(values) < n_obs:
                    values.extend([np.nan] * (n_obs - len(values)))

                epoch_data[sat_id] = values

            if epoch_data:
                self.data[epoch] = epoch_data

            i += 1

    @staticmethod
    def _parse_obs_line_chunks(obs_str, max_chunks=None):
        values = []
        for j in range(0, len(obs_str), 16):
            if max_chunks is not None and len(values) >= max_chunks:
                break
            chunk = obs_str[j : j + 16]
            if not chunk:
                continue
            field = chunk[:14].strip()
            if field:
                try:
                    values.append(float(field))
                except Exception:
                    values.append(np.nan)
            else:
                values.append(np.nan)
        return values

    @staticmethod
    def _normalize_sat_id(sat_raw):
        sat_raw = sat_raw.strip()
        if not sat_raw:
            return "G", ""
        if sat_raw[0].isalpha() and len(sat_raw) >= 2:
            sys_name = sat_raw[0]
            prn = sat_raw[1:].strip().zfill(2)
            return sys_name, f"{sys_name}{prn}"
        prn = sat_raw.strip().zfill(2)
        return "G", f"G{prn}"


class SP3Reader:
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
                    self.orbits.setdefault(current_epoch, {})
                except Exception:
                    current_epoch = None
                continue

            if current_epoch is None or not line.startswith("P"):
                continue

            try:
                sat_id = line[1:4].strip()
                x = float(line[4:18].strip()) * 1000.0
                y = float(line[18:32].strip()) * 1000.0
                z = float(line[32:46].strip()) * 1000.0
                self.orbits[current_epoch][sat_id] = (x, y, z)
            except Exception:
                continue

        self.epochs = sorted(self.orbits.keys())

    def get_sat_position(self, sat_id: str, epoch: datetime):
        if not self.epochs:
            return None

        idx = bisect_left(self.epochs, epoch)
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
    return float(np.degrees(np.arctan2(enu[2], horiz)))


def calc_stec_tecu(p1: float, p2: float, f1: float, f2: float):
    if np.isnan(p1) or np.isnan(p2) or p1 <= 0 or p2 <= 0:
        return np.nan
    f1_sq = f1 * f1
    f2_sq = f2 * f2
    den = 40.308e16 * (f1_sq - f2_sq)
    if abs(den) < 1e-12:
        return np.nan
    return (f1_sq * f2_sq * abs(p2 - p1)) / abs(den)


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
        gps_pairs = [
            ("C1C", "C2W"), ("C1C", "C2S"), ("C1C", "C2X"),
            ("C1", "P2"), ("C1", "C2"), ("P1", "P2"),
        ]
        for p1, p2 in gps_pairs:
            c1_val, c2_val = read_pair(p1, p2)
            if c1_val is not None:
                break

    elif sys_type == "R":
        glo_pairs = [("C1C", "C2C"), ("C1C", "C2P"), ("C1", "P2"), ("C1", "C2")]
        for p1, p2 in glo_pairs:
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

    # RINEX2 常见通用码兜底（如 C1/C2, P1/P2）。
    if c1_val is None:
        for p1, p2 in [("C1", "C2"), ("P1", "P2"), ("C1", "P2"), ("P1", "C2")]:
            c1_val, c2_val = read_pair(p1, p2)
            if c1_val is not None:
                break

    return c1_val, c2_val, freq1, freq2


def extract_yydoy(filename: str, first_epoch: datetime | None = None):
    m = re.search(r"_(\d{7})\d{4}_", filename)
    if m:
        return m.group(1)

    m2 = re.search(r"(\d{7})", filename)
    if m2:
        return m2.group(1)

    if first_epoch is not None:
        doy = first_epoch.timetuple().tm_yday
        return f"{first_epoch.year}{doy:03d}"

    return None


def process_obv_data(work_dir: Path):
    obv_dir = work_dir / "9obv"
    sp3_dir = work_dir / "sp3"
    output_dir = work_dir / "output" / "9obv_vtec"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not obv_dir.exists():
        raise FileNotFoundError(f"输入目录不存在: {obv_dir}")

    obs_files = sorted(
        list(obv_dir.glob("*.26o"))
        + list(obv_dir.glob("*.rnx"))
        + list(obv_dir.glob("*.O"))
        + list(obv_dir.glob("*.o"))
    )

    print(f"找到观测文件: {len(obs_files)}")
    results = {}

    for obs_file in obs_files:
        print(f"\n处理: {obs_file.name}")
        rinex = MixedRINEXReader(obs_file)
        if not rinex.data:
            print("  [跳过] 无有效观测历元")
            continue

        first_epoch = min(rinex.data.keys())
        yydoy = extract_yydoy(obs_file.name, first_epoch=first_epoch)
        if yydoy is None:
            print("  [跳过] 无法匹配日期")
            continue

        sp3_candidates = sorted(sp3_dir.glob(f"*_{yydoy}0000_*_ORB.SP3"))
        if not sp3_candidates:
            print(f"  [跳过] 未找到SP3: yydoy={yydoy}")
            continue

        sp3_file = sp3_candidates[0]
        print(f"  SP3: {sp3_file.name}")

        sta_pos = rinex.header.get("approx_pos")
        if sta_pos is None:
            print("  [跳过] 无APPROX POSITION XYZ")
            continue

        sp3 = SP3Reader(sp3_file)
        sta_xyz = np.array(sta_pos, dtype=float)

        station_name = rinex.header.get("marker_name", obs_file.stem).strip() or obs_file.stem
        station_key = obs_file.stem

        def compute_station_vtec(use_sp3_mapping: bool):
            station_vtec_local = []
            total_epochs_local = 0
            valid_epochs_local = 0
            valid_sats_local = 0

            for epoch, satellites in sorted(rinex.data.items()):
                total_epochs_local += 1
                epoch_vals = []

                for sat_id, obs_values in satellites.items():
                    if not sat_id:
                        continue
                    sys_type = sat_id[0]
                    indices = rinex.obs_indices.get(sys_type)
                    if not indices:
                        indices = rinex.obs_indices.get("G", {})
                    if not indices:
                        continue

                    c1, c2, f1, f2 = select_dual_frequency(sys_type, indices, obs_values)
                    if c1 is None or c2 is None:
                        continue
                    if np.isnan(c1) or np.isnan(c2):
                        continue

                    stec = calc_stec_tecu(c1, c2, f1, f2)
                    if np.isnan(stec):
                        continue

                    if use_sp3_mapping:
                        sat_xyz = sp3.get_sat_position(sat_id, epoch)
                        if sat_xyz is None:
                            continue

                        elev = elevation_angle_deg(sta_xyz, sat_xyz)
                        if elev is None or elev < 10.0:
                            continue

                        mf = mapping_function(elev)
                        if np.isnan(mf) or mf <= 0:
                            continue
                        vtec = stec / mf
                        valid_range = (0 < vtec < 500)
                    else:
                        # 兜底路径: 使用STEC近似，避免因SP3/高度角链路问题全站失效。
                        vtec = stec
                        valid_range = (0 < vtec < 1200)

                    if np.isfinite(vtec) and valid_range:
                        epoch_vals.append(vtec)
                        valid_sats_local += 1

                if epoch_vals:
                    station_vtec_local.append(
                        {
                            "epoch": epoch,
                            "vtec": float(np.mean(epoch_vals)),
                            "sat_count": len(epoch_vals),
                            "station": station_name,
                            "obs_file": obs_file.name,
                            "mode": "SP3映射" if use_sp3_mapping else "双频兜底",
                        }
                    )
                    valid_epochs_local += 1

            return station_vtec_local, total_epochs_local, valid_epochs_local, valid_sats_local

        station_vtec, total_epochs, valid_epochs, valid_sats = compute_station_vtec(use_sp3_mapping=True)

        if not station_vtec:
            print("  [提示] SP3映射模式无有效结果，尝试双频兜底模式...")
            station_vtec, total_epochs, valid_epochs, valid_sats = compute_station_vtec(use_sp3_mapping=False)

        if station_vtec:
            results[station_key] = station_vtec
            print(
                f"  [OK] 历元 {len(station_vtec)} / {total_epochs}, "
                f"有效卫星观测 {valid_sats}"
            )
        else:
            print(f"  [失败] 未计算出有效VTEC, 总历元 {total_epochs}")

    return results, output_dir


def save_vtec_to_csv(vtec_results: dict, output_dir: Path):
    for key, data in vtec_results.items():
        df = pd.DataFrame(data)
        out_csv = output_dir / f"{key}_VTEC.csv"
        df.to_csv(out_csv, index=False)
        print(f"已保存CSV: {out_csv.name}")


def plot_vtec_four_panels(vtec_results: dict, output_dir: Path):
    for key, data in vtec_results.items():
        df = pd.DataFrame(data)
        if df.empty:
            continue

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.patch.set_facecolor("white")
        fig.suptitle(f"{key} VTEC数据分析", fontsize=16, fontweight="bold", y=0.995)

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
        ax3.set_xticklabels([key])
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
        out_png = output_dir / f"{key}_VTEC_plot.png"
        plt.savefig(out_png, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"已保存四子图: {out_png.name}")


def plot_overlay(vtec_results: dict, output_dir: Path):
    if not vtec_results:
        return

    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor("white")

    colors = plt.cm.tab20(np.linspace(0, 1, max(2, len(vtec_results))))
    for (key, data), color in zip(sorted(vtec_results.items()), colors):
        df = pd.DataFrame(data)
        if df.empty:
            continue

        t = pd.to_datetime(df["epoch"])
        sod = t.dt.hour * 3600 + t.dt.minute * 60 + t.dt.second
        ax.plot(sod, df["vtec"], marker="o", markersize=2, linewidth=1.4, alpha=0.78, color=color, label=key)

    ticks = np.arange(0, 24 * 3600 + 1, 2 * 3600)
    labels = [f"{int(x // 3600):02d}:00" for x in ticks]
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, rotation=45, fontsize=9)

    ax.set_xlabel("时刻 (HH:MM)", fontsize=12, fontweight="bold")
    ax.set_ylabel("VTEC (TECU)", fontsize=12, fontweight="bold")
    ax.set_title("obv全部文件 VTEC重叠对比", fontsize=14, fontweight="bold", pad=16)
    ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)
    ax.set_facecolor("#f8f9fa")
    ax.legend(loc="upper left", fontsize=8, ncol=2, framealpha=0.95, edgecolor="black")
    plt.tight_layout()

    out_png = output_dir / "OBV_全部文件_VTEC重叠图.png"
    plt.savefig(out_png, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"已保存重叠图: {out_png.name}")


def main():
    work_dir = Path(__file__).resolve().parent
    print("=" * 60)
    print("9obv目录 VTEC处理 (混合RINEX版本, 使用SP3, 无插值)")
    print("=" * 60)

    vtec_results, output_dir = process_obv_data(work_dir)
    if not vtec_results:
        print("未得到有效VTEC结果")
        return

    save_vtec_to_csv(vtec_results, output_dir)
    plot_vtec_four_panels(vtec_results, output_dir)
    plot_overlay(vtec_results, output_dir)

    print("\n处理完成")
    print(f"输出目录: {output_dir}")


if __name__ == "__main__":
    main()
