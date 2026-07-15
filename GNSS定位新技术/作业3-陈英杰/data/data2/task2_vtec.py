#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务二第一部分（修正版）：
分析 HKSL 测站 2026-01-19 磁暴前后各三天（2026-01-16 ~ 2026-01-22）的电离层变化情况。

本版修正重点：
1. 修复 RINEX2 历元续行卫星列表解析错误（这是之前图像异常的主要原因）
2. 明确按你现在的实际文件名读取：无 (1)，无 .gz 压缩包
3. 优先使用“载波相位平滑/码观测定平”的 TEC 反演，曲线更平滑、更适合做 7 天对比
4. 输出 30 s 历元曲线 + 平滑曲线 + 每天统计表，只做 VTEC，不做 PPP
"""

import argparse
import gzip
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# =========================
# 常量
# =========================
C = 299792458.0
F1 = 1575.42e6
F2 = 1227.60e6
LAM1 = C / F1
LAM2 = C / F2
RE = 6378137.0
IONO_H = 450000.0
YEAR = 2026
DOYS = list(range(16, 23))
CENTER_DOY = 19

# TEC 转换系数（TECU）
TEC_FACTOR = (F1**2 * F2**2) / (40.3 * (F1**2 - F2**2)) / 1e16


# =========================
# 基础工具
# =========================
def open_text_auto(path: Path):
    if path.suffix.lower() == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", errors="ignore")
    return open(path, "r", encoding="utf-8", errors="ignore")


def safe_mean(x):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    return np.mean(x) if x.size else np.nan


def safe_median(x):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    return np.median(x) if x.size else np.nan


def doy_to_date(year: int, doy: int) -> datetime:
    return datetime(year, 1, 1) + timedelta(days=doy - 1)


def sod_of_dt(dt: datetime) -> float:
    return dt.hour * 3600.0 + dt.minute * 60.0 + dt.second + dt.microsecond * 1e-6


def resolve_data_dir(cli_data_dir: Optional[str]) -> Path:
    if cli_data_dir:
        return Path(cli_data_dir).expanduser().resolve()
    script_dir = Path(__file__).resolve().parent
    cands = [script_dir, script_dir / "data2", Path.cwd(), Path.cwd() / "data2"]
    for c in cands:
        if c.exists():
            return c.resolve()
    return script_dir


# =========================
# 坐标转换
# =========================
def ecef_to_geodetic(x, y, z):
    a = 6378137.0
    f = 1.0 / 298.257223563
    e2 = f * (2 - f)

    lon = math.atan2(y, x)
    p = math.hypot(x, y)
    lat = math.atan2(z, p * (1 - e2))

    for _ in range(12):
        sin_lat = math.sin(lat)
        N = a / math.sqrt(1 - e2 * sin_lat * sin_lat)
        h = p / math.cos(lat) - N
        lat_new = math.atan2(z, p * (1 - e2 * N / (N + h)))
        if abs(lat_new - lat) < 1e-13:
            lat = lat_new
            break
        lat = lat_new

    sin_lat = math.sin(lat)
    N = a / math.sqrt(1 - e2 * sin_lat * sin_lat)
    h = p / math.cos(lat) - N
    return lat, lon, h


def ecef_to_enu_matrix(lat, lon):
    sl, cl = math.sin(lat), math.cos(lat)
    sb, cb = math.sin(lon), math.cos(lon)
    return np.array([
        [-sb, cb, 0.0],
        [-sl * cb, -sl * sb, cl],
        [cl * cb, cl * sb, sl],
    ])


def sat_elevation_azimuth(rec_xyz, sat_xyz):
    lat, lon, _ = ecef_to_geodetic(*rec_xyz)
    R = ecef_to_enu_matrix(lat, lon)
    los = sat_xyz - rec_xyz
    enu = R @ los
    e, n, u = enu
    el = math.atan2(u, math.hypot(e, n))
    az = math.atan2(e, n)
    if az < 0:
        az += 2 * math.pi
    return el, az


def mapping_function(el_rad):
    s = (RE * math.cos(el_rad)) / (RE + IONO_H)
    s = min(max(s, -0.999999999), 0.999999999)
    return 1.0 / math.sqrt(1.0 - s * s)


def local_solar_hour(dt: datetime, lon_deg: float) -> float:
    lst = sod_of_dt(dt) / 3600.0 + lon_deg / 15.0
    while lst < 0:
        lst += 24.0
    while lst >= 24.0:
        lst -= 24.0
    return lst


# =========================
# 文件发现
# =========================
@dataclass
class DayFiles:
    doy: int
    obs: Path
    sp3: Path


def discover_inputs(data_dir: Path) -> Dict[int, DayFiles]:
    files = {}
    for doy in DOYS:
        obs = data_dir / f"hksl{doy:03d}0.26o"
        sp3 = data_dir / f"WUM0MGXRAP_{YEAR}{doy:03d}0000_01D_05M_ORB.SP3"

        # 兼容仍有 .gz 的情况，但本版默认按你说的“已全部解压”处理
        if not obs.exists():
            obs_gz = obs.with_suffix(obs.suffix + ".gz")
            if obs_gz.exists():
                obs = obs_gz
        if not sp3.exists():
            sp3_gz = sp3.with_suffix(sp3.suffix + ".gz")
            if sp3_gz.exists():
                sp3 = sp3_gz

        if not obs.exists() or not sp3.exists():
            raise FileNotFoundError(
                f"DOY {doy} 缺少必要文件。\n"
                f"期望观测文件：{obs.name}\n"
                f"期望精密轨道：{sp3.name}\n"
                f"当前数据目录：{data_dir}"
            )
        files[doy] = DayFiles(doy=doy, obs=obs, sp3=sp3)
    return files


# =========================
# RINEX2 观测文件读取（修正版）
# =========================
@dataclass
class RinexObs:
    approx_xyz: np.ndarray
    obs_types: List[str]
    epochs: List[datetime]
    data: List[Dict[str, Dict[str, float]]]


def parse_rinex2_obs(path: Path) -> RinexObs:
    approx_xyz = np.array([np.nan, np.nan, np.nan], dtype=float)
    obs_types: List[str] = []

    with open_text_auto(path) as f:
        lines = f.readlines()

    i = 0
    # 头文件
    while i < len(lines):
        line = lines[i].rstrip("\n")
        label = line[60:].strip() if len(line) >= 60 else ""

        if "APPROX POSITION XYZ" in label:
            parts = line[:60].split()
            if len(parts) >= 3:
                approx_xyz = np.array([float(parts[0]), float(parts[1]), float(parts[2])], dtype=float)

        elif "# / TYPES OF OBSERV" in label:
            parts = line[:60].split()
            if len(parts) >= 1:
                n_types = int(parts[0])
                obs_types.extend(parts[1:])
                while len(obs_types) < n_types:
                    i += 1
                    cont = lines[i][:60].split()
                    obs_types.extend(cont)
                obs_types = obs_types[:n_types]

        elif "END OF HEADER" in label:
            i += 1
            break

        i += 1

    epochs: List[datetime] = []
    data: List[Dict[str, Dict[str, float]]] = []

    while i < len(lines):
        line = lines[i].rstrip("\n")
        if len(line) < 32:
            i += 1
            continue

        try:
            yy = int(line[0:3])
            mm = int(line[3:6])
            dd = int(line[6:9])
            hh = int(line[9:12])
            mi = int(line[12:15])
            ss = float(line[15:26])
            flag = int(line[28:29])
            nsat = int(line[29:32])
        except Exception:
            i += 1
            continue

        year = 2000 + yy if yy < 80 else 1900 + yy
        sec_int = int(ss)
        usec = int(round((ss - sec_int) * 1e6))
        dt = datetime(year, mm, dd, hh, mi, sec_int, usec)

        # 关键修正：续行卫星列表只能从 32:68 读取，不能整行按 3 字符硬切
        sat_ids: List[str] = []
        remain = line[32:68]
        for k in range(0, len(remain), 3):
            s = remain[k:k + 3].strip()
            if s:
                sat_ids.append(s)

        while len(sat_ids) < nsat:
            i += 1
            cont = lines[i].rstrip("\n")
            remain = cont[32:68]
            for k in range(0, len(remain), 3):
                s = remain[k:k + 3].strip()
                if s:
                    sat_ids.append(s)

        i += 1
        epoch_obs: Dict[str, Dict[str, float]] = {}
        ntypes = len(obs_types)
        nlines_per_sat = (ntypes + 4) // 5

        for sat in sat_ids:
            vals = []
            for _ in range(nlines_per_sat):
                if i >= len(lines):
                    break
                obs_line = lines[i].rstrip("\n")
                i += 1
                for k in range(0, min(len(obs_line), 80), 16):
                    field = obs_line[k:k + 16]
                    try:
                        vals.append(float(field[:14]))
                    except Exception:
                        vals.append(np.nan)
            vals = vals[:ntypes]
            epoch_obs[sat] = {name: val for name, val in zip(obs_types, vals)}

        if flag == 0:
            epochs.append(dt)
            data.append(epoch_obs)

    return RinexObs(approx_xyz=approx_xyz, obs_types=obs_types, epochs=epochs, data=data)


# =========================
# SP3 读取
# =========================
def parse_sp3(path: Path) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    sat_times: Dict[str, List[float]] = {}
    sat_pos: Dict[str, List[List[float]]] = {}

    current_dt = None
    day_roll_count = 0
    prev_sod = None

    with open_text_auto(path) as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line:
                continue

            if line.startswith("*"):
                try:
                    year = int(line[3:7])
                    mon = int(line[8:10])
                    day = int(line[11:13])
                    hh = int(line[14:16])
                    mm = int(line[17:19])
                    ss = float(line[20:31])
                    sec_i = int(ss)
                    usec = int(round((ss - sec_i) * 1e6))
                    current_dt = datetime(year, mon, day, hh, mm, sec_i, usec)

                    sod = sod_of_dt(current_dt)
                    if prev_sod is not None and sod < prev_sod:
                        day_roll_count += 1
                    prev_sod = sod
                except Exception:
                    current_dt = None
                continue

            if current_dt is None:
                continue

            if line.startswith("PG"):
                prn = line[1:4].strip()
                if not prn.startswith("G"):
                    continue
                try:
                    x = float(line[4:18]) * 1000.0
                    y = float(line[18:32]) * 1000.0
                    z = float(line[32:46]) * 1000.0
                except Exception:
                    continue

                sod = sod_of_dt(current_dt) + day_roll_count * 86400.0
                sat_times.setdefault(prn, []).append(sod)
                sat_pos.setdefault(prn, []).append([x, y, z])

    out: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
    for prn in sat_times:
        t = np.asarray(sat_times[prn], dtype=float)
        x = np.asarray(sat_pos[prn], dtype=float)
        idx = np.argsort(t)
        out[prn] = (t[idx], x[idx, :])
    return out


def interp_sat_pos(sp3: Dict[str, Tuple[np.ndarray, np.ndarray]], prn: str, t_sec: float) -> Optional[np.ndarray]:
    if prn not in sp3:
        return None
    t, xyz = sp3[prn]
    if t.size < 2:
        return None
    if t_sec < t[0] or t_sec > t[-1]:
        return None
    return np.array([
        np.interp(t_sec, t, xyz[:, 0]),
        np.interp(t_sec, t, xyz[:, 1]),
        np.interp(t_sec, t, xyz[:, 2]),
    ], dtype=float)


# =========================
# TEC 反演
# =========================
def choose_code_pair(obs_map: Dict[str, float]) -> Optional[Tuple[float, float]]:
    # HKSL 文件里通常 C1、P2、C2 都可用
    candidates = [("C1", "P2"), ("C1", "C2"), ("P1", "P2")]
    for a, b in candidates:
        va = obs_map.get(a, np.nan)
        vb = obs_map.get(b, np.nan)
        if np.isfinite(va) and np.isfinite(vb):
            return va, vb
    return None


def choose_phase_pair(obs_map: Dict[str, float]) -> Optional[Tuple[float, float]]:
    l1 = obs_map.get("L1", np.nan)
    l2 = obs_map.get("L2", np.nan)
    if np.isfinite(l1) and np.isfinite(l2):
        return l1, l2
    return None


def code_stec_tecu(p1_m: float, p2_m: float) -> float:
    return TEC_FACTOR * (p2_m - p1_m)


def phase_stec_tecu(l1_cyc: float, l2_cyc: float) -> float:
    l4_m = l1_cyc * LAM1 - l2_cyc * LAM2
    return TEC_FACTOR * l4_m


def segment_arcs(times_sec: np.ndarray, phase_stec: np.ndarray, max_gap_sec: float = 90.0, max_jump_tecu: float = 4.0):
    n = len(times_sec)
    if n == 0:
        return []
    edges = [0]
    for i in range(1, n):
        gap = times_sec[i] - times_sec[i - 1]
        jump = abs(phase_stec[i] - phase_stec[i - 1]) if np.isfinite(phase_stec[i]) and np.isfinite(phase_stec[i - 1]) else np.inf
        if gap > max_gap_sec or jump > max_jump_tecu:
            edges.append(i)
    edges.append(n)
    return [(edges[k], edges[k + 1]) for k in range(len(edges) - 1)]


def robust_low_percentile_bias(x: np.ndarray, q: float = 5.0) -> float:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return np.nan
    return np.nanpercentile(x, q)


def compute_day_vtec(day: DayFiles, min_el_deg: float = 20.0) -> pd.DataFrame:
    obs = parse_rinex2_obs(day.obs)
    if not np.all(np.isfinite(obs.approx_xyz)) or np.linalg.norm(obs.approx_xyz) < 1000:
        raise RuntimeError(f"{day.obs.name} 头文件缺少有效 APPROX POSITION XYZ")

    rec_xyz = obs.approx_xyz.copy()
    lat, lon, _ = ecef_to_geodetic(*rec_xyz)
    lon_deg = math.degrees(lon)

    sp3 = parse_sp3(day.sp3)
    min_el = math.radians(min_el_deg)

    rows = []
    for dt, ep in zip(obs.epochs, obs.data):
        sod = sod_of_dt(dt)
        for prn, omap in ep.items():
            if not prn.startswith("G"):
                continue

            sat_xyz = interp_sat_pos(sp3, prn, sod)
            if sat_xyz is None:
                continue

            el, az = sat_elevation_azimuth(rec_xyz, sat_xyz)
            if el < min_el:
                continue

            cp = choose_code_pair(omap)
            pp = choose_phase_pair(omap)

            code_stec = np.nan
            phase_stec = np.nan

            if cp is not None:
                code_stec = code_stec_tecu(cp[0], cp[1])
            if pp is not None:
                phase_stec = phase_stec_tecu(pp[0], pp[1])

            if not np.isfinite(code_stec) and not np.isfinite(phase_stec):
                continue

            rows.append({
                "datetime": dt,
                "doy": day.doy,
                "prn": prn,
                "sod": sod,
                "lst_hour": local_solar_hour(dt, lon_deg),
                "elevation_deg": math.degrees(el),
                "azimuth_deg": math.degrees(az),
                "code_stec_tecu": code_stec,
                "phase_stec_tecu": phase_stec,
                "mf": mapping_function(el),
            })

    if not rows:
        raise RuntimeError(f"DOY {day.doy} 未提取到有效电离层样本")

    df = pd.DataFrame(rows).sort_values(["prn", "sod"]).reset_index(drop=True)

    # 逐卫星进行“载波定平到码观测”
    leveled_parts = []
    for prn, g in df.groupby("prn", sort=True):
        g = g.sort_values("sod").copy().reset_index(drop=True)
        t = g["sod"].to_numpy(dtype=float)
        code_arr = g["code_stec_tecu"].to_numpy(dtype=float)
        phase_arr = g["phase_stec_tecu"].to_numpy(dtype=float)

        # 若该星没有相位，则退化为码观测
        if np.sum(np.isfinite(phase_arr)) < 10:
            g["stec_tecu"] = code_arr
            leveled_parts.append(g)
            continue

        arcs = segment_arcs(t, np.where(np.isfinite(phase_arr), phase_arr, np.nan), max_gap_sec=90.0, max_jump_tecu=4.0)
        stec_final = np.full(len(g), np.nan, dtype=float)

        for i0, i1 in arcs:
            sub_code = code_arr[i0:i1]
            sub_phase = phase_arr[i0:i1]

            mask_both = np.isfinite(sub_code) & np.isfinite(sub_phase)
            if np.sum(mask_both) >= 8:
                level = np.median(sub_code[mask_both] - sub_phase[mask_both])
                sub_final = sub_phase + level
            else:
                sub_final = sub_code.copy()

            stec_final[i0:i1] = sub_final

        # 对仍为空的位置，回填码观测
        fallback = ~np.isfinite(stec_final) & np.isfinite(code_arr)
        stec_final[fallback] = code_arr[fallback]

        g["stec_tecu"] = stec_final
        leveled_parts.append(g)

    df = pd.concat(leveled_parts, ignore_index=True)

    # 映射到 VTEC
    df["vtec_raw_tecu"] = df["stec_tecu"] / df["mf"]

    # 卫星偏差归一：低分位数归零
    corrected_parts = []
    for prn, g in df.groupby("prn", sort=True):
        x = g["vtec_raw_tecu"].to_numpy(dtype=float)
        x = x[np.isfinite(x)]
        if x.size < 20:
            continue
        bias = robust_low_percentile_bias(x, q=5.0)
        gg = g.copy()
        gg["vtec_tecu"] = gg["vtec_raw_tecu"] - bias
        gg = gg[np.isfinite(gg["vtec_tecu"])].copy()
        gg = gg[(gg["vtec_tecu"] >= -2.0) & (gg["vtec_tecu"] <= 150.0)].copy()
        corrected_parts.append(gg)

    if not corrected_parts:
        raise RuntimeError(f"DOY {day.doy} VTEC 偏差修正后无有效样本")

    df = pd.concat(corrected_parts, ignore_index=True)
    df["vtec_tecu"] = df["vtec_tecu"].clip(lower=0.0)

    return df


# =========================
# 汇总与绘图
# =========================
def build_30s_series(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x["time_bin_30s"] = np.round(x["sod"] / 30.0) * 30.0
    x["lst_bin_30s"] = np.round(x["lst_hour"] * 120.0) / 120.0

    g = x.groupby(["doy", "time_bin_30s", "lst_bin_30s"], as_index=False)["vtec_tecu"].median()
    g = g.rename(columns={"vtec_tecu": "vtec_30s_tecu"})
    g = g.sort_values(["doy", "time_bin_30s"]).reset_index(drop=True)

    # 做一个 11 点滑动中值（约 5.5 min）用于出图更平滑
    smooth_parts = []
    for doy, sub in g.groupby("doy"):
        sub = sub.sort_values("time_bin_30s").copy()
        sub["vtec_smooth_tecu"] = (
            sub["vtec_30s_tecu"]
            .rolling(window=11, center=True, min_periods=3)
            .median()
        )
        # 边缘回填
        mask = ~np.isfinite(sub["vtec_smooth_tecu"])
        sub.loc[mask, "vtec_smooth_tecu"] = sub.loc[mask, "vtec_30s_tecu"]
        smooth_parts.append(sub)

    return pd.concat(smooth_parts, ignore_index=True)


def summarize_daily(df30: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for doy, g in df30.groupby("doy"):
        g = g.sort_values("time_bin_30s")
        lst = g["lst_bin_30s"].to_numpy(dtype=float)
        v = g["vtec_smooth_tecu"].to_numpy(dtype=float)

        day_mask = (lst >= 8.0) & (lst <= 18.0)
        aft_mask = (lst >= 12.0) & (lst <= 16.0)

        vmax = np.nanmax(v) if len(v) else np.nan
        vmin = np.nanmin(v) if len(v) else np.nan
        peak_lst = lst[np.nanargmax(v)] if len(v) else np.nan

        rows.append({
            "doy": doy,
            "date": doy_to_date(YEAR, doy).strftime("%Y-%m-%d"),
            "daily_mean_tecu": safe_mean(v),
            "daytime_mean_tecu": safe_mean(v[day_mask]),
            "afternoon_mean_tecu": safe_mean(v[aft_mask]),
            "max_vtec_tecu": vmax,
            "min_vtec_tecu": vmin,
            "daily_amplitude_tecu": vmax - vmin if np.isfinite(vmax) and np.isfinite(vmin) else np.nan,
            "peak_lst_hour": peak_lst,
            "n_30s_epochs": len(g),
        })

    summary = pd.DataFrame(rows).sort_values("doy").reset_index(drop=True)
    ref = summary.loc[summary["doy"] == CENTER_DOY].iloc[0]

    for col in ["daytime_mean_tecu", "afternoon_mean_tecu", "max_vtec_tecu", "daily_amplitude_tecu"]:
        summary[f"{col}_delta_vs_0119"] = summary[col] - ref[col]
        if np.isfinite(ref[col]) and abs(ref[col]) > 1e-12:
            summary[f"{col}_pct_vs_0119"] = (summary[col] - ref[col]) / ref[col] * 100.0
        else:
            summary[f"{col}_pct_vs_0119"] = np.nan

    return summary


def classify_day(row: pd.Series, ref: pd.Series) -> str:
    if row["doy"] == CENTER_DOY:
        return "磁暴主日参考"

    score = 0
    if row["daytime_mean_tecu"] > ref["daytime_mean_tecu"] * 1.08:
        score += 1
    elif row["daytime_mean_tecu"] < ref["daytime_mean_tecu"] * 0.92:
        score -= 1

    if row["max_vtec_tecu"] > ref["max_vtec_tecu"] * 1.08:
        score += 1
    elif row["max_vtec_tecu"] < ref["max_vtec_tecu"] * 0.92:
        score -= 1

    if row["daily_amplitude_tecu"] > ref["daily_amplitude_tecu"] * 1.08:
        score += 1
    elif row["daily_amplitude_tecu"] < ref["daily_amplitude_tecu"] * 0.92:
        score -= 1

    if score >= 2:
        return "明显增强"
    if score == 1:
        return "略增强"
    if score == 0:
        return "接近主日"
    if score == -1:
        return "略减弱"
    return "明显减弱"


def plot_vtec_7days(df30: pd.DataFrame, out_png: Path):
    plt.figure(figsize=(12.5, 6.5))
    for doy, g in sorted(df30.groupby("doy"), key=lambda x: x[0]):
        g = g.sort_values("lst_bin_30s")
        x = g["lst_bin_30s"].to_numpy(dtype=float)
        y = g["vtec_smooth_tecu"].to_numpy(dtype=float)
        lw = 2.4 if doy == CENTER_DOY else 1.35
        z = 5 if doy == CENTER_DOY else 2
        label = f"{doy_to_date(YEAR, doy).strftime('%m-%d')} (DOY {doy})"
        plt.plot(x, y, linewidth=lw, label=label, zorder=z)

    plt.xlim(0, 24)
    plt.xticks(np.arange(0, 25, 2))
    plt.xlabel("Local Solar Time (hour)")
    plt.ylabel("VTEC (TECU)")
    plt.title("HKSL station VTEC curves for 2026-01-16 to 2026-01-22")
    plt.grid(True, alpha=0.28)
    plt.legend(ncol=2, fontsize=9)
    plt.tight_layout()
    plt.savefig(out_png, dpi=220)
    plt.close()


def plot_daily_statistics(summary: pd.DataFrame, out_png: Path):
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 10), sharex=True)
    x = np.arange(len(summary))
    labels = summary["date"].tolist()

    axes[0].bar(x, summary["daytime_mean_tecu"])
    axes[0].set_ylabel("Daytime mean VTEC")
    axes[0].grid(True, axis="y", alpha=0.3)

    axes[1].bar(x, summary["max_vtec_tecu"])
    axes[1].set_ylabel("Peak VTEC")
    axes[1].grid(True, axis="y", alpha=0.3)

    axes[2].bar(x, summary["daily_amplitude_tecu"])
    axes[2].set_ylabel("Daily amplitude")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(labels, rotation=20)
    axes[2].grid(True, axis="y", alpha=0.3)

    fig.suptitle("Daily VTEC statistics of HKSL (2026-01-16 ~ 2026-01-22)")
    plt.tight_layout()
    plt.savefig(out_png, dpi=220)
    plt.close()


def build_report_text(summary: pd.DataFrame) -> str:
    ref = summary.loc[summary["doy"] == CENTER_DOY].iloc[0]
    lines = []
    lines.append("任务二第一部分：HKSL测站2026年1月19日磁暴前后各三天的电离层变化分析")
    lines.append("")
    lines.append("本次分析对象为HKSL单测站，时间范围为2026-01-16至2026-01-22。")
    lines.append("利用双频观测和SP3精密轨道反演VTEC，并以1月19日作为磁暴主日参考。")
    lines.append("")
    lines.append(
        f"1月19日当天，白天平均VTEC为{ref['daytime_mean_tecu']:.2f} TECU，"
        f"峰值为{ref['max_vtec_tecu']:.2f} TECU，"
        f"日变化幅度为{ref['daily_amplitude_tecu']:.2f} TECU，"
        f"峰值出现在地方时{ref['peak_lst_hour']:.2f} h附近。"
    )
    lines.append("")
    lines.append("逐日比较如下：")
    for _, row in summary.iterrows():
        state = row["day_state"]
        if row["doy"] == CENTER_DOY:
            lines.append(
                f"{row['date']}：磁暴主日参考。白天平均VTEC={row['daytime_mean_tecu']:.2f} TECU，"
                f"峰值={row['max_vtec_tecu']:.2f} TECU，幅度={row['daily_amplitude_tecu']:.2f} TECU。"
            )
        else:
            lines.append(
                f"{row['date']}：{state}。相对1月19日，白天平均VTEC变化"
                f"{row['daytime_mean_tecu_delta_vs_0119']:+.2f} TECU，"
                f"峰值变化{row['max_vtec_tecu_delta_vs_0119']:+.2f} TECU，"
                f"日变化幅度变化{row['daily_amplitude_tecu_delta_vs_0119']:+.2f} TECU。"
            )
    lines.append("")
    lines.append("原因讨论：")
    lines.append(
        "磁暴期间，太阳风扰动增强会通过磁层-电离层-热层耦合机制改变局地电场、热层成分和中性风场，"
        "从而引起电离层电子密度上升或下降。"
    )
    lines.append(
        "若VTEC明显增大，通常表现为磁暴正相效应；若VTEC减小，则多与成分扰动、复合增强和等离子体耗散有关，"
        "可视为负相效应。"
    )
    lines.append(
        "因此，可以通过比较1月19日前后三天的白天平均值、峰值及日变化幅度，判断磁暴扰动的强弱、持续时间与恢复过程。"
    )
    return "\n".join(lines)


# =========================
# 主流程
# =========================
def run_task2_vtec_only(data_dir: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    files = discover_inputs(data_dir)

    all_days = []
    for doy in DOYS:
        print(f"[INFO] Processing DOY {doy} ...")
        df = compute_day_vtec(files[doy], min_el_deg=20.0)
        all_days.append(df)

    all_df = pd.concat(all_days, ignore_index=True)
    all_df.to_csv(out_dir / "task2_vtec_all_samples.csv", index=False)

    df30 = build_30s_series(all_df)
    df30.to_csv(out_dir / "task2_vtec_30s_series.csv", index=False)

    summary = summarize_daily(df30)
    ref = summary.loc[summary["doy"] == CENTER_DOY].iloc[0]
    summary["day_state"] = [classify_day(r, ref) for _, r in summary.iterrows()]
    summary.to_csv(out_dir / "task2_vtec_daily_summary.csv", index=False)

    plot_vtec_7days(df30, out_dir / "task2_vtec_7days_curve.png")
    plot_daily_statistics(summary, out_dir / "task2_vtec_daily_statistics.png")

    report_text = build_report_text(summary)
    (out_dir / "task2_vtec_report_text.txt").write_text(report_text, encoding="utf-8")

    print("[DONE] 输出目录：", out_dir)
    print("  - task2_vtec_all_samples.csv")
    print("  - task2_vtec_30s_series.csv")
    print("  - task2_vtec_daily_summary.csv")
    print("  - task2_vtec_7days_curve.png")
    print("  - task2_vtec_daily_statistics.png")
    print("  - task2_vtec_report_text.txt")


def main():
    parser = argparse.ArgumentParser(description="任务二第一部分：HKSL测站磁暴前后电离层变化分析（修正版，仅VTEC）")
    parser.add_argument("--data-dir", type=str, default=None, help="数据目录。默认自动取脚本所在目录或其 data2 子目录")
    parser.add_argument("--out-dir", type=str, default=None, help="输出目录。默认 <data-dir>/task2_vtec_outputs_fixed")
    args = parser.parse_args()

    data_dir = resolve_data_dir(args.data_dir)
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else (data_dir / "task2_vtec_outputs_fixed")

    run_task2_vtec_only(data_dir, out_dir)


if __name__ == "__main__":
    main()
