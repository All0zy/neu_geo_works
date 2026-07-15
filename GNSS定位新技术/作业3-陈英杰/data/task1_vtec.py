#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GNSS TEC反演：任务一第1问——不同纬度测站VTEC对比分析

功能：
1. 读取6个不同纬度测站的RINEX 2.x观测文件和1个SP3精密星历；
2. 基于GPS双频伪距组合估计STEC，并通过单层薄壳模型映射为VTEC；
3. 对6个不同纬度测站进行VTEC对比分析（按地方太阳时对齐）；
4. 输出CSV结果、汇总表和图件。

说明：
- 当前数据中未提供DCB文件，因此脚本采用“按卫星低分位数归零”的方式估计并削弱硬件偏差，
  更适合做课程作业中的相对VTEC对比分析；若后续补充CODE/IGS DCB，可替换为严格绝对改正。
- SMST站头坐标为0，脚本会自动用首个可用历元的伪距观测反算近似站坐标。
"""

from __future__ import annotations

import math
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ------------------------------ 常量 ------------------------------
C = 299792458.0
F1 = 1575.42e6
F2 = 1227.60e6
LAMBDA1 = C / F1
LAMBDA2 = C / F2
TEC_COEF = (F1**2 * F2**2) / (40.3 * (F1**2 - F2**2)) / 1e16  # m -> TECU

WGS84_A = 6378137.0
WGS84_F = 1.0 / 298.257223563
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)
IONO_SHELL_H = 450e3

HK_REGION = {
    "lat_min": 19.5,
    "lat_max": 25.5,
    "lon_min": 111.5,
    "lon_max": 117.0,
    "lat0": 22.30,
    "lon0": 114.20,
}


# ------------------------------ 基本坐标函数 ------------------------------
def ecef2geodetic(x: float, y: float, z: float) -> Tuple[float, float, float]:
    if np.isclose([x, y, z], [0.0, 0.0, 0.0]).all():
        return np.nan, np.nan, np.nan

    lon = math.atan2(y, x)
    p = math.hypot(x, y)
    lat = math.atan2(z, p * (1.0 - WGS84_E2))

    for _ in range(12):
        sin_lat = math.sin(lat)
        n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * sin_lat * sin_lat)
        h = p / math.cos(lat) - n
        lat_new = math.atan2(z, p * (1.0 - WGS84_E2 * n / (n + h)))
        if abs(lat_new - lat) < 1e-13:
            lat = lat_new
            break
        lat = lat_new

    sin_lat = math.sin(lat)
    n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * sin_lat * sin_lat)
    h = p / math.cos(lat) - n
    return lat, lon, h


def enu_matrix(lat: float, lon: float) -> np.ndarray:
    sl, cl = math.sin(lat), math.cos(lat)
    so, co = math.sin(lon), math.cos(lon)
    return np.array(
        [
            [-so, co, 0.0],
            [-sl * co, -sl * so, cl],
            [cl * co, cl * so, sl],
        ],
        dtype=float,
    )


def sat_az_el(rec_xyz: np.ndarray, sat_xyz: np.ndarray) -> Tuple[float, float]:
    lat, lon, _ = ecef2geodetic(*rec_xyz)
    rot = enu_matrix(lat, lon)
    enu = rot @ (sat_xyz - rec_xyz)
    e, n, u = enu
    az = math.atan2(e, n) % (2.0 * math.pi)
    el = math.atan2(u, math.hypot(e, n))
    return az, el


def mapping_function(elev_rad: np.ndarray, h_iono: float = IONO_SHELL_H) -> np.ndarray:
    return 1.0 / np.sqrt(1.0 - (WGS84_A * np.cos(elev_rad) / (WGS84_A + h_iono)) ** 2)


def ipp_coords(
    lat_r: float,
    lon_r: float,
    az_rad: np.ndarray,
    elev_rad: np.ndarray,
    h_iono: float = IONO_SHELL_H,
) -> Tuple[np.ndarray, np.ndarray]:
    psi = np.pi / 2.0 - elev_rad - np.arcsin(
        np.clip(WGS84_A * np.cos(elev_rad) / (WGS84_A + h_iono), -1.0, 1.0)
    )
    lat_ipp = np.arcsin(
        np.sin(lat_r) * np.cos(psi) + np.cos(lat_r) * np.sin(psi) * np.cos(az_rad)
    )
    lon_ipp = lon_r + np.arcsin(
        np.clip(np.sin(psi) * np.sin(az_rad) / np.cos(lat_ipp), -1.0, 1.0)
    )
    lon_ipp = (lon_ipp + np.pi) % (2.0 * np.pi) - np.pi
    return lat_ipp, lon_ipp


# ------------------------------ 数据读取 ------------------------------
def parse_rinex2_header(path: Path) -> dict:
    header = {"obs_types": []}
    obs_types: List[str] = []

    with open(path, "r", errors="ignore") as f:
        while True:
            line = f.readline()
            if not line:
                break

            if "MARKER NAME" in line:
                header["marker_name"] = line[:60].strip()
            elif "APPROX POSITION XYZ" in line:
                vals = line[:60].split()
                header["approx_xyz"] = tuple(float(v) for v in vals[:3])
            elif "INTERVAL" in line:
                try:
                    header["interval"] = float(line[:10])
                except Exception:
                    pass
            elif "TIME OF FIRST OBS" in line:
                parts = line[:43].split()
                if len(parts) >= 6:
                    y, m, d, hh, mm = map(int, parts[:5])
                    ss = float(parts[5])
                    header["time_of_first_obs"] = (y, m, d, hh, mm, ss)
            elif "# / TYPES OF OBSERV" in line:
                total = int(line[:6].split()[0])
                obs_types.extend(line[6:60].split())
                while len(obs_types) < total:
                    pos = f.tell()
                    nxt = f.readline()
                    if not nxt:
                        break
                    if "# / TYPES OF OBSERV" in nxt:
                        obs_types.extend(nxt[6:60].split())
                    else:
                        f.seek(pos)
                        break
                header["obs_types"] = obs_types[:total]
            elif "END OF HEADER" in line:
                break

    return header


def parse_rinex2_observations(
    path: Path,
    system: str = "G",
    max_epochs: Optional[int] = None,
) -> Tuple[dict, pd.DataFrame]:
    header = parse_rinex2_header(path)
    obs_types = header.get("obs_types", [])
    n_obs = len(obs_types)
    rows: List[dict] = []

    with open(path, "r", errors="ignore") as f:
        for line in f:
            if "END OF HEADER" in line:
                break

        epoch_count = 0
        while True:
            line = f.readline()
            if not line:
                break
            if len(line) < 32:
                continue

            try:
                yy = int(line[0:3])
                mo = int(line[3:6])
                dd = int(line[6:9])
                hh = int(line[9:12])
                mm = int(line[12:15])
                ss = float(line[15:26])
                flag = int(line[28:29])
                nsat = int(line[29:32])
            except Exception:
                continue

            if flag not in (0, 1):
                sat_list = line[32:68]
                while len(sat_list.replace(" ", "")) < nsat * 3:
                    cont = f.readline()
                    if not cont:
                        break
                    sat_list += cont[32:68] if len(cont) >= 68 else cont
                for _ in range(nsat):
                    nlines = int(math.ceil(n_obs / 5.0))
                    for _ in range(nlines):
                        _ = f.readline()
                continue

            year = 2000 + yy if yy < 80 else 1900 + yy
            sec_int = int(ss)
            micro = int(round((ss - sec_int) * 1e6))
            epoch_time = datetime(year, mo, dd, hh, mm, sec_int, micro)

            sat_list = line[32:68]
            while len(sat_list.replace(" ", "")) < nsat * 3:
                cont = f.readline()
                if not cont:
                    break
                sat_list += cont[32:68] if len(cont) >= 68 else cont

            sats = [sat_list[i : i + 3].strip() for i in range(0, len(sat_list), 3)]
            sats = [s for s in sats if s][:nsat]

            for sat in sats:
                nlines = int(math.ceil(n_obs / 5.0))
                raw = ""
                for _ in range(nlines):
                    raw += f.readline().rstrip("\n").ljust(80)

                if sat[0] != system:
                    continue

                fields = [raw[i : i + 16] for i in range(0, n_obs * 16, 16)]
                rec = {"time": epoch_time, "sat": sat}
                for obs_name, field in zip(obs_types, fields):
                    val = field[:14].strip()
                    rec[obs_name] = float(val) if val else np.nan
                rows.append(rec)

            epoch_count += 1
            if max_epochs is not None and epoch_count >= max_epochs:
                break

    return header, pd.DataFrame(rows)


def parse_sp3(path: Path, system: str = "G") -> Dict[str, dict]:
    data: Dict[str, List[Tuple[float, float, float, float, float]]] = defaultdict(list)
    current_time: Optional[datetime] = None

    with open(path, "r", errors="ignore") as f:
        for line in f:
            if line.startswith("*"):
                year = int(line[3:7])
                mo = int(line[8:10])
                dd = int(line[11:13])
                hh = int(line[14:16])
                mm = int(line[17:19])
                ss = float(line[20:31])
                current_time = datetime(year, mo, dd, hh, mm, int(ss), int(round((ss - int(ss)) * 1e6)))
                continue

            if line.startswith("P") and current_time is not None:
                sat = line[1:4]
                if sat[0] != system:
                    continue
                x = float(line[4:18]) * 1000.0
                y = float(line[18:32]) * 1000.0
                z = float(line[32:46]) * 1000.0
                clk_str = line[46:60].strip()
                clk = float(clk_str) * 1e-6 if clk_str else np.nan  # seconds
                t_unix = pd.Timestamp(current_time).value / 1e9
                data[sat].append((t_unix, x, y, z, clk))

    sp3 = {}
    for sat, values in data.items():
        arr = np.array(values, dtype=float)
        sp3[sat] = {"t": arr[:, 0], "xyz": arr[:, 1:4], "clk": arr[:, 4]}
    return sp3


def interp_sat_state(sp3: Dict[str, dict], sat: str, times: Iterable[datetime]) -> Tuple[np.ndarray, np.ndarray]:
    item = sp3[sat]
    tt = np.array([pd.Timestamp(t).value / 1e9 for t in pd.to_datetime(list(times))], dtype=float)
    xyz = np.vstack([np.interp(tt, item["t"], item["xyz"][:, i]) for i in range(3)]).T
    clk = np.interp(tt, item["t"], item["clk"])
    return xyz, clk


# ------------------------------ 站坐标估计（用于SMST） ------------------------------
def solve_receiver_position(epoch_df: pd.DataFrame, sp3: Dict[str, dict], max_iter: int = 8) -> np.ndarray:
    pr_col = choose_obs_column(epoch_df, ["P1", "C1"])
    if pr_col is None:
        raise ValueError("No pseudorange found for receiver position estimation.")

    data = epoch_df[["time", "sat", pr_col]].copy()
    data = data.rename(columns={pr_col: "PR"}).dropna(subset=["PR"])
    data = data[data["sat"].isin(sp3.keys())].reset_index(drop=True)
    if len(data) < 4:
        raise ValueError("Not enough satellites for receiver position estimation.")

    t = data.loc[0, "time"]
    sat_xyz_list = []
    sat_clk_list = []
    for sat in data["sat"]:
        xyz, clk = interp_sat_state(sp3, sat, [t])
        sat_xyz_list.append(xyz[0])
        sat_clk_list.append(clk[0])

    sat_xyz = np.array(sat_xyz_list, dtype=float)
    sat_clk = np.array(sat_clk_list, dtype=float)
    pr = data["PR"].to_numpy(dtype=float) + C * sat_clk

    x = np.array([1.0e6, 1.0e6, 1.0e6], dtype=float)
    cb = 0.0

    for _ in range(max_iter):
        rho = np.linalg.norm(sat_xyz - x, axis=1)
        h = np.zeros((len(rho), 4), dtype=float)
        h[:, :3] = -(sat_xyz - x) / rho[:, None]
        h[:, 3] = 1.0
        v = pr - (rho + cb)
        dx, *_ = np.linalg.lstsq(h, v, rcond=None)
        x += dx[:3]
        cb += dx[3]
        if np.linalg.norm(dx[:3]) < 1e-3:
            break

    return x


# ------------------------------ VTEC反演 ------------------------------
def choose_obs_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    best_col = None
    best_n = -1
    for col in candidates:
        if col in df.columns:
            count = int(df[col].notna().sum())
            if count > best_n:
                best_col = col
                best_n = count
    return best_col if best_n > 0 else None


@dataclass
class StationResult:
    station: str
    xyz: np.ndarray
    lat_deg: float
    lon_deg: float
    obs_df: pd.DataFrame
    ts_df: pd.DataFrame


class TECProcessor:
    def __init__(self, obs_files: List[Path], sp3_file: Path, out_dir: Path, elev_mask_deg: float = 20.0):
        self.obs_files = obs_files
        self.sp3_file = sp3_file
        self.out_dir = out_dir
        self.elev_mask_deg = elev_mask_deg
        self.sp3 = parse_sp3(sp3_file)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def get_station_xyz(self, header: dict, obs_df: pd.DataFrame) -> np.ndarray:
        xyz = np.array(header.get("approx_xyz", (0.0, 0.0, 0.0)), dtype=float)
        if np.linalg.norm(xyz) > 1.0:
            return xyz

        for _, grp in obs_df.groupby("time"):
            try:
                xyz = solve_receiver_position(grp, self.sp3)
                return xyz
            except Exception:
                continue

        raise RuntimeError("Unable to estimate receiver coordinate from observations.")

    def compute_station_vtec(self, obs_file: Path) -> StationResult:
        header, obs_df = parse_rinex2_observations(obs_file, system="G")
        if obs_df.empty:
            raise RuntimeError(f"{obs_file.name}: no GPS observations parsed.")

        xyz = self.get_station_xyz(header, obs_df)
        lat_rad, lon_rad, _ = ecef2geodetic(*xyz)
        lat_deg = math.degrees(lat_rad)
        lon_deg = math.degrees(lon_rad)
        station = header.get("marker_name", obs_file.stem).strip()

        p1_col = choose_obs_column(obs_df, ["P1", "C1"])
        p2_col = choose_obs_column(obs_df, ["P2", "C2"])
        if p1_col is None or p2_col is None:
            raise RuntimeError(f"{obs_file.name}: missing dual-frequency code observations.")

        use = obs_df[["time", "sat", p1_col, p2_col]].copy()
        use["P1"] = use[p1_col]
        use["P2"] = use[p2_col]
        use = use.dropna(subset=["P1", "P2"])
        use = use[use["sat"].isin(self.sp3.keys())].reset_index(drop=True)
        if use.empty:
            raise RuntimeError(f"{obs_file.name}: no usable GPS code pairs.")

        satpos = np.zeros((len(use), 3), dtype=float)
        for sat, idx in use.groupby("sat").groups.items():
            idx = np.array(list(idx), dtype=int)
            xyzs, _ = interp_sat_state(self.sp3, sat, use.loc[idx, "time"])
            satpos[idx, :] = xyzs

        az_list = []
        el_list = []
        for sat_xyz in satpos:
            az, el = sat_az_el(xyz, sat_xyz)
            az_list.append(az)
            el_list.append(el)

        use["az_rad"] = az_list
        use["el_rad"] = el_list
        use = use[use["el_rad"] >= math.radians(self.elev_mask_deg)].copy()
        if use.empty:
            raise RuntimeError(f"{obs_file.name}: no data above elevation mask.")

        use["stec_tecu"] = TEC_COEF * (use["P2"] - use["P1"])
        use = use[np.isfinite(use["stec_tecu"])].copy()
        use["mf"] = mapping_function(use["el_rad"].to_numpy())
        use["vtec_raw"] = use["stec_tecu"] / use["mf"]

        ipp_lat, ipp_lon = ipp_coords(
            lat_rad,
            lon_rad,
            use["az_rad"].to_numpy(),
            use["el_rad"].to_numpy(),
        )
        use["ipp_lat_deg"] = np.degrees(ipp_lat)
        use["ipp_lon_deg"] = np.degrees(ipp_lon)
        use["station"] = station
        use["station_lat_deg"] = lat_deg
        use["station_lon_deg"] = lon_deg

        # 按卫星剔除粗差
        groups = []
        for _, g in use.groupby("sat"):
            med = float(g["vtec_raw"].median())
            mad = float(np.median(np.abs(g["vtec_raw"] - med)))
            if np.isfinite(mad) and mad > 0.0:
                g = g[np.abs(g["vtec_raw"] - med) <= 5.0 * 1.4826 * mad]
            if not g.empty:
                groups.append(g)
        use = pd.concat(groups, ignore_index=True)

        # 缺少DCB时，用卫星低分位数近似消除硬件偏差
        sat_bias = use.groupby("sat")["vtec_raw"].quantile(0.05).rename("bias")
        use = use.join(sat_bias, on="sat")
        use["vtec_tecu"] = (use["vtec_raw"] - use["bias"]).clip(lower=0.0)
        use = use[(use["vtec_tecu"] >= 0.0) & (use["vtec_tecu"] <= 120.0)].copy()

        utc_hour = (
            pd.to_datetime(use["time"]).dt.hour
            + pd.to_datetime(use["time"]).dt.minute / 60.0
            + pd.to_datetime(use["time"]).dt.second / 3600.0
        )
        use["lst_hour"] = (utc_hour + lon_deg / 15.0) % 24.0

        ts = (
            use.groupby("time")
            .agg(
                vtec_median=("vtec_tecu", "median"),
                vtec_mean=("vtec_tecu", "mean"),
                vtec_std=("vtec_tecu", "std"),
                nsat=("vtec_tecu", "size"),
                lst_hour=("lst_hour", "mean"),
            )
            .reset_index()
        )
        ts["station"] = station
        ts["station_lat_deg"] = lat_deg
        ts["station_lon_deg"] = lon_deg

        return StationResult(station=station, xyz=xyz, lat_deg=lat_deg, lon_deg=lon_deg, obs_df=use, ts_df=ts)

    def run_all_stations(self) -> Tuple[List[StationResult], pd.DataFrame, pd.DataFrame]:
        results: List[StationResult] = []
        summaries = []
        ts_list = []

        for obs_file in self.obs_files:
            result = self.compute_station_vtec(obs_file)
            results.append(result)
            ts_list.append(result.ts_df)

            summaries.append(
                {
                    "station": result.station,
                    "lat_deg": result.lat_deg,
                    "lon_deg": result.lon_deg,
                    "mean_vtec_tecu": result.ts_df["vtec_median"].mean(),
                    "max_vtec_tecu": result.ts_df["vtec_median"].max(),
                    "min_vtec_tecu": result.ts_df["vtec_median"].min(),
                    "diurnal_amp_tecu": result.ts_df["vtec_median"].max() - result.ts_df["vtec_median"].min(),
                    "epoch_count": len(result.ts_df),
                    "obs_count": len(result.obs_df),
                }
            )

            result.obs_df.to_csv(self.out_dir / f"{result.station}_vtec_obs.csv", index=False)
            result.ts_df.to_csv(self.out_dir / f"{result.station}_vtec_timeseries.csv", index=False)

        summary_df = pd.DataFrame(summaries).sort_values("lat_deg").reset_index(drop=True)
        ts_all = pd.concat(ts_list, ignore_index=True)
        summary_df.to_csv(self.out_dir / "station_summary.csv", index=False)
        ts_all.to_csv(self.out_dir / "all_station_timeseries.csv", index=False)
        return results, summary_df, ts_all


# ------------------------------ 图件输出 ------------------------------
def plot_station_comparison(results: List[StationResult], summary_df: pd.DataFrame, out_dir: Path) -> None:
    ordered = sorted(results, key=lambda r: r.lat_deg)

    fig = plt.figure(figsize=(14, 7.5))
    for res in ordered:
        temp = res.ts_df.copy().sort_values(["lst_hour", "time"]).reset_index(drop=True)
        plt.plot(
            temp["lst_hour"],
            temp["vtec_median"],
            linewidth=1.0,
            alpha=0.95,
            label=f"{res.station} ({res.lat_deg:.1f}°)",
        )
    plt.xlim(0, 24)
    plt.xticks(np.arange(0, 25, 2))
    plt.xlabel("Local Solar Time (hour)")
    plt.ylabel("Median VTEC (TECU)")
    plt.title("VTEC comparison for six stations at different latitudes (30 s cadence)")
    plt.grid(True, alpha=0.3)
    plt.legend(ncol=2, fontsize=9)
    plt.tight_layout()
    plt.savefig(out_dir / "station_vtec_comparison_lst_30s.png", dpi=220)
    plt.savefig(out_dir / "station_vtec_comparison_lst.png", dpi=220)
    plt.close(fig)

    fig = plt.figure(figsize=(10, 6))
    plt.plot(summary_df["lat_deg"], summary_df["mean_vtec_tecu"], marker="o", linewidth=2.0, label="Daily mean VTEC")
    plt.plot(summary_df["lat_deg"], summary_df["max_vtec_tecu"], marker="s", linewidth=2.0, label="Daily max VTEC")
    plt.plot(summary_df["lat_deg"], summary_df["diurnal_amp_tecu"], marker="^", linewidth=2.0, label="Diurnal amplitude")
    for _, row in summary_df.iterrows():
        plt.text(row["lat_deg"], row["max_vtec_tecu"] + 0.7, row["station"], fontsize=8, ha="center")
    plt.xlabel("Station latitude (deg)")
    plt.ylabel("VTEC statistic (TECU)")
    plt.title("VTEC statistics versus latitude")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "station_vtec_statistics_vs_latitude.png", dpi=220)
    plt.close(fig)

# ------------------------------ 香港区域电离层模型 ------------------------------
def build_design_matrix(x: np.ndarray, y: np.ndarray, t: np.ndarray) -> np.ndarray:
    return np.column_stack(
        [
            np.ones_like(x),
            x,
            y,
            t,
            x**2,
            x * y,
            y**2,
            x * t,
            y * t,
            t**2,
        ]
    )


def fit_hongkong_regional_model(hk_obs_df: pd.DataFrame, out_dir: Path) -> Tuple[np.ndarray, pd.DataFrame]:
    region = hk_obs_df[
        hk_obs_df["ipp_lat_deg"].between(HK_REGION["lat_min"], HK_REGION["lat_max"])
        & hk_obs_df["ipp_lon_deg"].between(HK_REGION["lon_min"], HK_REGION["lon_max"])
    ].copy()

    if region.empty:
        raise RuntimeError("No HK-region IPP samples were selected for regional model fitting.")

    region["x"] = region["ipp_lat_deg"] - HK_REGION["lat0"]
    region["y"] = region["ipp_lon_deg"] - HK_REGION["lon0"]
    region["t"] = region["lst_hour"] - 12.0

    x = region["x"].to_numpy(dtype=float)
    y = region["y"].to_numpy(dtype=float)
    t = region["t"].to_numpy(dtype=float)
    z = region["vtec_tecu"].to_numpy(dtype=float)

    design = build_design_matrix(x, y, t)
    coef, *_ = np.linalg.lstsq(design, z, rcond=None)
    region["vtec_model"] = design @ coef
    region["residual"] = region["vtec_tecu"] - region["vtec_model"]

    coef_names = ["c0", "c1_x", "c2_y", "c3_t", "c4_x2", "c5_xy", "c6_y2", "c7_xt", "c8_yt", "c9_t2"]
    coef_df = pd.DataFrame({"coefficient": coef_names, "value": coef})
    coef_df.to_csv(out_dir / "hongkong_regional_model_coefficients.csv", index=False)
    region.to_csv(out_dir / "hongkong_regional_model_samples.csv", index=False)

    rms = float(np.sqrt(np.mean(region["residual"] ** 2)))
    mae = float(np.mean(np.abs(region["residual"])))
    metrics_df = pd.DataFrame({"metric": ["sample_count", "rms_tecu", "mae_tecu"], "value": [len(region), rms, mae]})
    metrics_df.to_csv(out_dir / "hongkong_regional_model_metrics.csv", index=False)

    # 拟合效果图
    fig = plt.figure(figsize=(10, 5))
    plt.scatter(region["vtec_tecu"], region["vtec_model"], s=8, alpha=0.35)
    lo = min(region["vtec_tecu"].min(), region["vtec_model"].min())
    hi = max(region["vtec_tecu"].max(), region["vtec_model"].max())
    plt.plot([lo, hi], [lo, hi], linestyle="--", linewidth=1.5)
    plt.xlabel("Observed VTEC (TECU)")
    plt.ylabel("Model VTEC (TECU)")
    plt.title(f"Hong Kong regional polynomial model fit (RMS = {rms:.2f} TECU)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_dir / "hongkong_regional_model_fit.png", dpi=220)
    plt.close(fig)

    fig = plt.figure(figsize=(10, 5))
    plt.hist(region["residual"], bins=50)
    plt.xlabel("Residual (TECU)")
    plt.ylabel("Count")
    plt.title("Residual distribution of Hong Kong regional ionospheric model")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(out_dir / "hongkong_regional_model_residual_hist.png", dpi=220)
    plt.close(fig)

    return coef, region


def evaluate_hk_model_grid(coef: np.ndarray, lst_hour: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    lat_grid = np.linspace(21.6, 23.6, 81)
    lon_grid = np.linspace(113.5, 115.5, 81)
    lat_mesh, lon_mesh = np.meshgrid(lat_grid, lon_grid, indexing="ij")

    x = lat_mesh - HK_REGION["lat0"]
    y = lon_mesh - HK_REGION["lon0"]
    t = np.full_like(x, lst_hour - 12.0)
    design = build_design_matrix(x.ravel(), y.ravel(), t.ravel())
    vtec = (design @ coef).reshape(lat_mesh.shape)
    return lat_mesh, lon_mesh, vtec


def plot_hk_model_snapshots(coef: np.ndarray, out_dir: Path, lst_hours: List[float]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
    axes = axes.ravel()

    for ax, hour in zip(axes, lst_hours):
        lat_mesh, lon_mesh, vtec = evaluate_hk_model_grid(coef, hour)
        im = ax.contourf(lon_mesh, lat_mesh, vtec, levels=18)
        ax.set_title(f"HK regional ionosphere model @ LST {hour:02.0f}:00")
        ax.set_xlabel("Longitude (deg)")
        ax.set_ylabel("Latitude (deg)")
        ax.grid(True, alpha=0.15)
        fig.colorbar(im, ax=ax, shrink=0.9, label="VTEC (TECU)")

    fig.suptitle("Hong Kong regional VTEC model snapshots")
    plt.savefig(out_dir / "hongkong_regional_model_snapshots.png", dpi=220)
    plt.close(fig)


# ------------------------------ 主程序 ------------------------------
def find_first(base_dir: Path, patterns: list[str]) -> Path:
    for pat in patterns:
        matches = sorted(base_dir.glob(pat))
        if matches:
            return matches[0]
    raise FileNotFoundError(f"No file matched: {patterns}")


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    out_dir = base_dir / "task1_vtec_outputs"

    obs_files = [
        find_first(base_dir, ["hkws0270*.26o", "HKWS0270*.26o"]),
        find_first(base_dir, ["holm0270*.26o", "HOLM0270*.26o"]),
        find_first(base_dir, ["novm0270*.26o", "NOVM0270*.26o"]),
        find_first(base_dir, ["nrc10270*.26o", "NRC10270*.26o"]),
        find_first(base_dir, ["salu0270*.26o", "SALU0270*.26o"]),
        find_first(base_dir, ["coso0270*.26o", "COSO0270*.26o"]),
    ]
    sp3_file = find_first(base_dir, ["WUM0MGXRAP_20260270000_01D_05M_ORB*.SP3", "WUM0MGXRAP_20260270000_01D_05M_ORB*.sp3"])

    processor = TECProcessor(obs_files=obs_files, sp3_file=sp3_file, out_dir=out_dir, elev_mask_deg=20.0)
    results, summary_df, ts_all = processor.run_all_stations()
    plot_station_comparison(results, summary_df, out_dir)

    # 输出一个便于写实验报告的排序表
    report_df = summary_df.copy().sort_values("lat_deg").reset_index(drop=True)
    report_df["latitude_rank"] = range(1, len(report_df) + 1)
    report_df = report_df[[
        "latitude_rank",
        "station",
        "lat_deg",
        "lon_deg",
        "mean_vtec_tecu",
        "max_vtec_tecu",
        "min_vtec_tecu",
        "diurnal_amp_tecu",
        "epoch_count",
        "obs_count",
    ]]
    report_df.to_csv(out_dir / "task1_station_summary_for_report.csv", index=False)

    # 输出30秒历元序列，便于直接作图或写报告
    ts_30s = (
        ts_all.copy()
        .sort_values(["station_lat_deg", "lst_hour", "time"])
        .reset_index(drop=True)
    )
    ts_30s.to_csv(out_dir / "task1_30s_lst_vtec.csv", index=False)

    # 同时保留整点统计，便于表格化展示
    ts_hourly = ts_all.copy()
    ts_hourly["lst_bin"] = ts_hourly["lst_hour"].round().astype(int) % 24
    hourly = (
        ts_hourly.groupby(["station", "station_lat_deg", "lst_bin"])["vtec_median"]
        .median()
        .reset_index()
        .sort_values(["station_lat_deg", "lst_bin"])
    )
    hourly.to_csv(out_dir / "task1_hourly_lst_vtec.csv", index=False)

    print("Done.")
    print(f"Output directory: {out_dir}")
    print("Stations used:")
    for r in sorted(results, key=lambda x: x.lat_deg):
        print(f" - {r.station:8s}  lat={r.lat_deg:8.3f}  lon={r.lon_deg:8.3f}")
    print("Generated files:")
    for p in sorted(out_dir.glob("*")):
        print(" -", p.name)


if __name__ == "__main__":
    main()
