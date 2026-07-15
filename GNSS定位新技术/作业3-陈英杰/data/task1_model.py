#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ============================== 常量 ==============================
C = 299792458.0
F1 = 1575.42e6
F2 = 1227.60e6
TEC_COEF = (F1**2 * F2**2) / (40.3 * (F1**2 - F2**2)) / 1e16  # m -> TECU

WGS84_A = 6378137.0
WGS84_F = 1.0 / 298.257223563
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)
IONO_SHELL_H = 450e3

HK_REF_LAT = 22.3000
HK_REF_LON = 114.1700
HK_GRID_LAT = np.linspace(21.80, 22.70, 121)
HK_GRID_LON = np.linspace(113.80, 114.50, 121)


# ============================== 坐标函数 ==============================
def ecef2geodetic(x: float, y: float, z: float) -> Tuple[float, float, float]:
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
    return np.array([
        [-so, co, 0.0],
        [-sl * co, -sl * so, cl],
        [cl * co, cl * so, sl],
    ], dtype=float)


def sat_az_el(rec_xyz: np.ndarray, sat_xyz: np.ndarray) -> Tuple[float, float]:
    lat, lon, _ = ecef2geodetic(*rec_xyz)
    rot = enu_matrix(lat, lon)
    enu = rot @ (sat_xyz - rec_xyz)
    e, n, u = enu
    az = math.atan2(e, n) % (2.0 * math.pi)
    el = math.atan2(u, math.hypot(e, n))
    return az, el


def mapping_function(elev_rad: np.ndarray, h_iono: float = IONO_SHELL_H) -> np.ndarray:
    arg = WGS84_A * np.cos(elev_rad) / (WGS84_A + h_iono)
    arg = np.clip(arg, -1.0, 1.0)
    return 1.0 / np.sqrt(1.0 - arg**2)


def ipp_coords(lat_r: float, lon_r: float, az_rad: np.ndarray, elev_rad: np.ndarray, h_iono: float = IONO_SHELL_H) -> Tuple[np.ndarray, np.ndarray]:
    arg = WGS84_A * np.cos(elev_rad) / (WGS84_A + h_iono)
    arg = np.clip(arg, -1.0, 1.0)
    psi = np.pi / 2.0 - elev_rad - np.arcsin(arg)
    lat_ipp = np.arcsin(np.sin(lat_r) * np.cos(psi) + np.cos(lat_r) * np.sin(psi) * np.cos(az_rad))
    lon_ipp = lon_r + np.arcsin(np.clip(np.sin(psi) * np.sin(az_rad) / np.cos(lat_ipp), -1.0, 1.0))
    lon_ipp = (lon_ipp + np.pi) % (2.0 * np.pi) - np.pi
    return lat_ipp, lon_ipp


# ============================== RINEX读取 ==============================
def get_rinex_version(path: Path) -> float:
    with open(path, "r", errors="ignore") as f:
        line = f.readline()
    return float(line[:9].strip())


def parse_rinex2_header(path: Path) -> dict:
    header = {"obs_types": [], "approx_xyz": (0.0, 0.0, 0.0)}
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


def parse_rinex3_header(path: Path) -> dict:
    header = {"obs_types_by_sys": {}, "approx_xyz": (0.0, 0.0, 0.0)}
    with open(path, "r", errors="ignore") as f:
        while True:
            line = f.readline()
            if not line:
                break
            label = line[60:].strip()
            if label == "MARKER NAME":
                header["marker_name"] = line[:60].strip()
            elif label == "APPROX POSITION XYZ":
                vals = line[:60].split()
                header["approx_xyz"] = tuple(float(v) for v in vals[:3])
            elif label == "INTERVAL":
                try:
                    header["interval"] = float(line[:10])
                except Exception:
                    pass
            elif label == "SYS / # / OBS TYPES":
                sys = line[0]
                total = int(line[3:6])
                obs = line[7:60].split()
                while len(obs) < total:
                    pos = f.tell()
                    nxt = f.readline()
                    if not nxt:
                        break
                    if nxt[60:].strip() == "SYS / # / OBS TYPES":
                        obs.extend(nxt[7:60].split())
                    else:
                        f.seek(pos)
                        break
                header["obs_types_by_sys"][sys] = obs[:total]
            elif label == "END OF HEADER":
                break
    return header


def parse_rinex2_observations(path: Path, system: str = "G") -> Tuple[dict, pd.DataFrame]:
    header = parse_rinex2_header(path)
    obs_types = header.get("obs_types", [])
    n_obs = len(obs_types)
    rows: List[dict] = []
    with open(path, "r", errors="ignore") as f:
        for line in f:
            if "END OF HEADER" in line:
                break
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
            sat_list = line[32:68]
            while len(sat_list.replace(" ", "")) < nsat * 3:
                cont = f.readline()
                if not cont:
                    break
                sat_list += cont[32:68] if len(cont) >= 68 else cont
            sats = [sat_list[i:i + 3].strip() for i in range(0, len(sat_list), 3)]
            sats = [s for s in sats if s][:nsat]
            year = 2000 + yy if yy < 80 else 1900 + yy
            sec_int = int(ss)
            micro = int(round((ss - sec_int) * 1e6))
            epoch_time = datetime(year, mo, dd, hh, mm, sec_int, micro)
            for sat in sats:
                nlines = int(math.ceil(n_obs / 5.0))
                raw = ""
                for _ in range(nlines):
                    raw += f.readline().rstrip("\n").ljust(80)
                if flag not in (0, 1):
                    continue
                if not sat or sat[0] != system:
                    continue
                fields = [raw[i:i + 16] for i in range(0, n_obs * 16, 16)]
                rec = {"time": epoch_time, "sat": sat}
                for obs_name, field in zip(obs_types, fields):
                    val = field[:14].strip()
                    rec[obs_name] = float(val) if val else np.nan
                rows.append(rec)
    return header, pd.DataFrame(rows)


def parse_rinex3_observations(path: Path, system: str = "G") -> Tuple[dict, pd.DataFrame]:
    header = parse_rinex3_header(path)
    rows: List[dict] = []
    with open(path, "r", errors="ignore") as f:
        for line in f:
            if line[60:].strip() == "END OF HEADER":
                break
        while True:
            line = f.readline()
            if not line:
                break
            if not line.startswith(">"):
                continue
            try:
                year = int(line[2:6])
                mo = int(line[7:9])
                dd = int(line[10:12])
                hh = int(line[13:15])
                mm = int(line[16:18])
                ss = float(line[19:29])
                flag = int(line[31:32])
                nsat = int(line[32:35])
            except Exception:
                continue
            sec_int = int(ss)
            micro = int(round((ss - sec_int) * 1e6))
            epoch_time = datetime(year, mo, dd, hh, mm, sec_int, micro)
            for _ in range(nsat):
                obs_line = f.readline()
                if not obs_line:
                    break
                sat = obs_line[:3].strip()
                sys = sat[0] if sat else ""
                obs_types = header.get("obs_types_by_sys", {}).get(sys, [])
                n_obs = len(obs_types)
                if n_obs == 0:
                    continue
                raw = obs_line[3:].rstrip("\n")
                need = 16 * n_obs
                if flag not in (0, 1):
                    continue
                if sys != system:
                    continue
                raw = raw.ljust(need)
                fields = [raw[i:i + 16] for i in range(0, n_obs * 16, 16)]
                rec = {"time": epoch_time, "sat": sat}
                for obs_name, field in zip(obs_types, fields):
                    val = field[:14].strip()
                    rec[obs_name] = float(val) if val else np.nan
                rows.append(rec)
    return header, pd.DataFrame(rows)


def parse_rinex_observations(path: Path, system: str = "G") -> Tuple[dict, pd.DataFrame]:
    version = get_rinex_version(path)
    if version >= 3.0:
        return parse_rinex3_observations(path, system=system)
    return parse_rinex2_observations(path, system=system)


# ============================== SP3读取 ==============================
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
                clk = float(clk_str) * 1e-6 if clk_str else np.nan
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


# ============================== 观测选择 ==============================
def choose_obs_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    best_col = None
    best_n = -1
    for col in candidates:
        if col in df.columns:
            n = int(df[col].notna().sum())
            if n > best_n:
                best_col = col
                best_n = n
    return best_col if best_n > 0 else None


def pick_dual_code_columns(df: pd.DataFrame) -> Tuple[str, str]:
    c1_candidates = ["P1", "C1", "C1C", "C1W", "C1X", "C1P", "C1S", "C1L"]
    c2_candidates = ["P2", "C2", "C2W", "C2X", "C2C", "C2P", "C2S", "C2L"]
    c1 = choose_obs_column(df, c1_candidates)
    c2 = choose_obs_column(df, c2_candidates)
    if c1 is None or c2 is None:
        raise RuntimeError("No usable GPS dual-frequency code observations found.")
    return c1, c2


# ============================== TEC反演 ==============================
@dataclass
class StationResult:
    station: str
    xyz: np.ndarray
    lat_deg: float
    lon_deg: float
    obs_df: pd.DataFrame
    ts_df: pd.DataFrame


class HKRegionalModelProcessor:
    def __init__(self, obs_files: List[Path], sp3_file: Path, out_dir: Path, elev_mask_deg: float = 25.0):
        self.obs_files = obs_files
        self.sp3_file = sp3_file
        self.out_dir = out_dir
        self.elev_mask_deg = elev_mask_deg
        self.sp3 = parse_sp3(sp3_file)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def compute_station_vtec(self, obs_file: Path) -> StationResult:
        header, obs_df = parse_rinex_observations(obs_file, system="G")
        if obs_df.empty:
            raise RuntimeError(f"{obs_file.name}: no GPS observations parsed.")
        xyz = np.array(header.get("approx_xyz", (0.0, 0.0, 0.0)), dtype=float)
        if np.linalg.norm(xyz) < 1.0:
            raise RuntimeError(f"{obs_file.name}: missing receiver coordinate.")
        lat_rad, lon_rad, _ = ecef2geodetic(*xyz)
        lat_deg = math.degrees(lat_rad)
        lon_deg = math.degrees(lon_rad)
        station = header.get("marker_name", obs_file.stem).strip()

        c1, c2 = pick_dual_code_columns(obs_df)
        use = obs_df[["time", "sat", c1, c2]].copy()
        use["P1"] = use[c1]
        use["P2"] = use[c2]
        use = use.dropna(subset=["P1", "P2"])
        use = use[use["sat"].isin(self.sp3.keys())].reset_index(drop=True)
        if use.empty:
            raise RuntimeError(f"{obs_file.name}: no usable GPS code pairs.")

        satpos = np.zeros((len(use), 3), dtype=float)
        for sat, idx in use.groupby("sat").groups.items():
            idx = np.array(list(idx), dtype=int)
            xyzs, _ = interp_sat_state(self.sp3, sat, use.loc[idx, "time"])
            satpos[idx, :] = xyzs

        az_list, el_list = [], []
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

        ipp_lat, ipp_lon = ipp_coords(lat_rad, lon_rad, use["az_rad"].to_numpy(), use["el_rad"].to_numpy())
        use["ipp_lat_deg"] = np.degrees(ipp_lat)
        use["ipp_lon_deg"] = np.degrees(ipp_lon)
        use["station"] = station
        use["station_lat_deg"] = lat_deg
        use["station_lon_deg"] = lon_deg

        parts = []
        for _, g in use.groupby("sat"):
            med = float(g["vtec_raw"].median())
            mad = float(np.median(np.abs(g["vtec_raw"] - med)))
            if np.isfinite(mad) and mad > 0:
                g = g[np.abs(g["vtec_raw"] - med) <= 5.0 * 1.4826 * mad]
            if not g.empty:
                parts.append(g)
        use = pd.concat(parts, ignore_index=True)

        sat_bias = use.groupby("sat")["vtec_raw"].quantile(0.05).rename("bias")
        use = use.join(sat_bias, on="sat")
        use["vtec_tecu"] = (use["vtec_raw"] - use["bias"]).clip(lower=0.0)
        use = use[(use["vtec_tecu"] >= 0.0) & (use["vtec_tecu"] <= 120.0)].copy()

        utc_hour = pd.to_datetime(use["time"]).dt.hour + pd.to_datetime(use["time"]).dt.minute / 60.0 + pd.to_datetime(use["time"]).dt.second / 3600.0
        use["utc_hour"] = utc_hour
        use["hk_local_hour"] = (utc_hour + 8.0) % 24.0
        use["lst_hour_ref"] = (utc_hour + HK_REF_LON / 15.0) % 24.0

        ts = use.groupby("time").agg(
            vtec_median=("vtec_tecu", "median"),
            vtec_mean=("vtec_tecu", "mean"),
            nsat=("vtec_tecu", "size"),
        ).reset_index()
        ts["station"] = station
        ts["station_lat_deg"] = lat_deg
        ts["station_lon_deg"] = lon_deg
        return StationResult(station=station, xyz=xyz, lat_deg=lat_deg, lon_deg=lon_deg, obs_df=use, ts_df=ts)

    def run_all(self) -> Tuple[List[StationResult], pd.DataFrame, pd.DataFrame]:
        results = []
        summaries = []
        obs_all = []
        for obs_file in self.obs_files:
            res = self.compute_station_vtec(obs_file)
            results.append(res)
            obs_all.append(res.obs_df)
            summaries.append({
                "station": res.station,
                "lat_deg": res.lat_deg,
                "lon_deg": res.lon_deg,
                "mean_vtec_tecu": res.ts_df["vtec_median"].mean(),
                "max_vtec_tecu": res.ts_df["vtec_median"].max(),
                "epoch_count": len(res.ts_df),
                "obs_count": len(res.obs_df),
            })
            res.obs_df.to_csv(self.out_dir / f"{res.station}_vtec_obs.csv", index=False)
            res.ts_df.to_csv(self.out_dir / f"{res.station}_vtec_timeseries.csv", index=False)
        summary_df = pd.DataFrame(summaries).sort_values("station").reset_index(drop=True)
        obs_all_df = pd.concat(obs_all, ignore_index=True)
        summary_df.to_csv(self.out_dir / "hk_station_summary.csv", index=False)
        obs_all_df.to_csv(self.out_dir / "hk_all_obs_vtec.csv", index=False)
        return results, summary_df, obs_all_df


# ============================== 区域模型 ==============================
def build_poly2_design(dlat: np.ndarray, dlon: np.ndarray) -> np.ndarray:
    return np.column_stack([
        np.ones_like(dlat),
        dlat,
        dlon,
        dlat**2,
        dlat * dlon,
        dlon**2,
    ])


def fit_polynomial_epoch_model(obs_all_df: pd.DataFrame, out_dir: Path, bin_minutes: int = 30) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = obs_all_df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df["time_bin"] = df["time"].dt.floor(f"{bin_minutes}min")
    df["dlat"] = df["ipp_lat_deg"] - HK_REF_LAT
    df["dlon"] = df["ipp_lon_deg"] - HK_REF_LON

    coef_rows = []
    pred_parts = []

    for time_bin, g in df.groupby("time_bin"):
        g = g.copy()
        if len(g) < 20:
            continue
        design = build_poly2_design(g["dlat"].to_numpy(), g["dlon"].to_numpy())
        if np.linalg.matrix_rank(design) < 6:
            continue
        coef, *_ = np.linalg.lstsq(design, g["vtec_tecu"].to_numpy(), rcond=None)
        pred = design @ coef
        resid = g["vtec_tecu"].to_numpy() - pred
        g["vtec_model"] = pred
        g["residual"] = resid
        pred_parts.append(g)
        coef_rows.append({
            "time_bin": time_bin,
            "sample_count": len(g),
            "rms_tecu": float(np.sqrt(np.mean(resid**2))),
            "mae_tecu": float(np.mean(np.abs(resid))),
            "c0": coef[0],
            "c1_dlat": coef[1],
            "c2_dlon": coef[2],
            "c3_dlat2": coef[3],
            "c4_dlat_dlon": coef[4],
            "c5_dlon2": coef[5],
        })

    coef_df = pd.DataFrame(coef_rows).sort_values("time_bin").reset_index(drop=True)
    pred_df = pd.concat(pred_parts, ignore_index=True) if pred_parts else pd.DataFrame()
    coef_df.to_csv(out_dir / "hk_regional_model_coefficients_by_epoch.csv", index=False)
    pred_df.to_csv(out_dir / "hk_regional_model_samples_with_residual.csv", index=False)
    return coef_df, pred_df


def evaluate_grid_from_coef(coef_row: pd.Series) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    lat_mesh, lon_mesh = np.meshgrid(HK_GRID_LAT, HK_GRID_LON, indexing="ij")
    dlat = lat_mesh - HK_REF_LAT
    dlon = lon_mesh - HK_REF_LON
    design = build_poly2_design(dlat.ravel(), dlon.ravel())
    coef = np.array([
        coef_row["c0"], coef_row["c1_dlat"], coef_row["c2_dlon"],
        coef_row["c3_dlat2"], coef_row["c4_dlat_dlon"], coef_row["c5_dlon2"],
    ], dtype=float)
    vtec = (design @ coef).reshape(lat_mesh.shape)
    return lat_mesh, lon_mesh, vtec


def plot_epoch_metrics(coef_df: pd.DataFrame, out_dir: Path) -> None:
    fig = plt.figure(figsize=(11, 5))
    plt.plot(pd.to_datetime(coef_df["time_bin"]), coef_df["rms_tecu"], marker="o", linewidth=1.8)
    plt.xlabel("UTC time")
    plt.ylabel("RMS (TECU)")
    plt.title("Hong Kong regional polynomial model RMS by epoch")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_dir / "hk_regional_model_rms_timeseries.png", dpi=220)
    plt.close(fig)


def plot_snapshot_maps(coef_df: pd.DataFrame, station_summary: pd.DataFrame, out_dir: Path) -> None:
    if len(coef_df) == 0:
        return

    coef_df = coef_df.copy()
    coef_df["time_bin"] = pd.to_datetime(coef_df["time_bin"])

    target_hours = pd.date_range(
        coef_df["time_bin"].min().floor("D"),
        coef_df["time_bin"].min().floor("D") + pd.Timedelta(hours=23),
        freq="1h",
    )

    selected_rows = []
    used_idx = set()
    for th in target_hours:
        diffs = (coef_df["time_bin"] - th).abs()
        cand_idx = int(diffs.idxmin())
        if cand_idx in used_idx:
            exact = coef_df.index[coef_df["time_bin"] == th]
            if len(exact) > 0:
                cand_idx = int(exact[0])
        used_idx.add(cand_idx)
        selected_rows.append(coef_df.loc[cand_idx])
    snap_df = pd.DataFrame(selected_rows).reset_index(drop=True)

    fig, axes = plt.subplots(6, 4, figsize=(18, 24), constrained_layout=True)
    axes = axes.ravel()

    all_grids = []
    for _, row in snap_df.iterrows():
        _, _, vtec = evaluate_grid_from_coef(row)
        all_grids.append(vtec)
    vmin = float(np.nanmin([g.min() for g in all_grids]))
    vmax = float(np.nanmax([g.max() for g in all_grids]))
    levels = np.linspace(vmin, vmax, 18)

    for ax, (_, row), vtec in zip(axes, snap_df.iterrows(), all_grids):
        lat_mesh, lon_mesh, _ = evaluate_grid_from_coef(row)
        im = ax.contourf(lon_mesh, lat_mesh, vtec, levels=levels)
        ax.scatter(station_summary["lon_deg"], station_summary["lat_deg"], marker="^", s=20)
        ts = pd.to_datetime(row["time_bin"])
        ax.set_title(f"UTC {ts:%H:%M} | HKT {(ts.hour + 8) % 24:02d}:{ts.minute:02d}", fontsize=10)
        ax.set_xlabel("Lon (deg)")
        ax.set_ylabel("Lat (deg)")
        ax.grid(True, alpha=0.15)

    cbar = fig.colorbar(im, ax=axes.tolist(), shrink=0.98, pad=0.01)
    cbar.set_label("VTEC (TECU)")
    fig.suptitle("Hong Kong regional ionospheric polynomial model for 24 hours", fontsize=16)
    plt.savefig(out_dir / "hk_regional_polynomial_model_24h.png", dpi=220)
    plt.savefig(out_dir / "hk_regional_polynomial_model_snapshots.png", dpi=220)
    plt.close(fig)




def plot_fit_curve_overall(pred_df: pd.DataFrame, out_dir: Path, resample_minutes: int = 10) -> None:
    if pred_df.empty:
        return
    df = pred_df.copy()
    df["time"] = pd.to_datetime(df["time"])
    curve = (
        df.set_index("time")[["vtec_tecu", "vtec_model"]]
        .resample(f"{resample_minutes}min")
        .median()
        .dropna()
        .reset_index()
    )
    curve.to_csv(out_dir / "hk_regional_model_fit_curve_overall.csv", index=False)

    fig = plt.figure(figsize=(12, 5))
    plt.plot(curve["time"], curve["vtec_tecu"], linewidth=1.6, label="Observed median VTEC")
    plt.plot(curve["time"], curve["vtec_model"], linewidth=1.6, label="Polynomial fitted VTEC")
    plt.xlabel("UTC time")
    plt.ylabel("VTEC (TECU)")
    plt.title(f"Hong Kong regional ionospheric model fitted curve ({resample_minutes}-min median)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "hk_regional_model_fit_curve_overall.png", dpi=220)
    plt.close(fig)


def plot_fit_curve_by_station(pred_df: pd.DataFrame, out_dir: Path, resample_minutes: int = 10) -> None:
    if pred_df.empty or "station" not in pred_df.columns:
        return
    df = pred_df.copy()
    df["time"] = pd.to_datetime(df["time"])
    stations = sorted(df["station"].dropna().unique())
    if len(stations) == 0:
        return

    export_parts = []
    n = len(stations)
    ncols = 2
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 3.4 * nrows), constrained_layout=True)
    axes = np.array(axes).reshape(-1)

    for ax, st in zip(axes, stations):
        g = df[df["station"] == st].copy()
        curve = (
            g.set_index("time")[["vtec_tecu", "vtec_model"]]
            .resample(f"{resample_minutes}min")
            .median()
            .dropna()
            .reset_index()
        )
        if curve.empty:
            ax.set_visible(False)
            continue
        curve["station"] = st
        export_parts.append(curve.copy())
        ax.plot(curve["time"], curve["vtec_tecu"], linewidth=1.3, label="Obs")
        ax.plot(curve["time"], curve["vtec_model"], linewidth=1.3, label="Fit")
        rmse = float(np.sqrt(np.mean((curve["vtec_tecu"] - curve["vtec_model"]) ** 2)))
        ax.set_title(f"{st}  RMSE={rmse:.2f} TECU", fontsize=10)
        ax.set_xlabel("UTC")
        ax.set_ylabel("VTEC")
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=8, loc="upper right")

    for ax in axes[len(stations):]:
        ax.set_visible(False)

    fig.suptitle(f"Observed and fitted VTEC curves for Hong Kong stations ({resample_minutes}-min median)", fontsize=15)
    plt.savefig(out_dir / "hk_regional_model_fit_curve_by_station.png", dpi=220)
    plt.close(fig)

    if export_parts:
        pd.concat(export_parts, ignore_index=True).to_csv(out_dir / "hk_regional_model_fit_curve_by_station.csv", index=False)

def plot_fit_scatter(pred_df: pd.DataFrame, out_dir: Path) -> None:
    if pred_df.empty:
        return
    rms = float(np.sqrt(np.mean(pred_df["residual"]**2)))
    mae = float(np.mean(np.abs(pred_df["residual"])))

    plot_df = pred_df
    if len(plot_df) > 20000:
        plot_df = plot_df.sample(20000, random_state=42)

    fig = plt.figure(figsize=(8, 6))
    plt.scatter(plot_df["vtec_tecu"], plot_df["vtec_model"], s=8, alpha=0.35)
    lo = min(pred_df["vtec_tecu"].min(), pred_df["vtec_model"].min())
    hi = max(pred_df["vtec_tecu"].max(), pred_df["vtec_model"].max())
    plt.plot([lo, hi], [lo, hi], linestyle="--", linewidth=1.5)
    plt.xlabel("Observed VTEC (TECU)")
    plt.ylabel("Polynomial-model VTEC (TECU)")
    plt.title(f"Hong Kong regional polynomial model fit\nRMS={rms:.2f} TECU, MAE={mae:.2f} TECU")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_dir / "hk_regional_model_fit_scatter.png", dpi=220)
    plt.close(fig)

    metrics = pd.DataFrame({
        "metric": ["sample_count", "epoch_count", "rms_tecu", "mae_tecu"],
        "value": [len(pred_df), pred_df["time_bin"].nunique(), rms, mae],
    })
    metrics.to_csv(out_dir / "hk_regional_model_metrics.csv", index=False)


# ============================== 主程序 ==============================
def find_first(base_dir: Path, patterns: List[str]) -> Path:
    for pat in patterns:
        matches = sorted(base_dir.glob(pat))
        if matches:
            return matches[0]
    raise FileNotFoundError(f"No file matched {patterns}")


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    out_dir = base_dir / "task1_hk_model_outputs"

    obs_files = [
        find_first(base_dir, ["hkws0270*.26o", "HKWS0270*.26o"]),
        find_first(base_dir, ["HKCL00HKG_R_20260270000_01D_30S_MO.26o"]),
        find_first(base_dir, ["HKKT00HKG_R_20260270000_01D_30S_MO.26o"]),
        find_first(base_dir, ["HKMW00HKG_R_20260270000_01D_30S_MO.26o"]),
        find_first(base_dir, ["HKOH00HKG_R_20260270000_01D_30S_MO.26o"]),
        find_first(base_dir, ["HKSC00HKG_R_20260270000_01D_30S_MO.26o"]),
        find_first(base_dir, ["HKST00HKG_R_20260270000_01D_30S_MO.26o"]),
    ]
    sp3_file = find_first(base_dir, ["WUM0MGXRAP_20260270000_01D_05M_ORB*.SP3", "WUM0MGXRAP_20260270000_01D_05M_ORB*.sp3"])

    processor = HKRegionalModelProcessor(obs_files=obs_files, sp3_file=sp3_file, out_dir=out_dir, elev_mask_deg=25.0)
    results, station_summary, obs_all_df = processor.run_all()

    coef_df, pred_df = fit_polynomial_epoch_model(obs_all_df, out_dir, bin_minutes=60)
    plot_epoch_metrics(coef_df, out_dir)
    plot_snapshot_maps(coef_df, station_summary, out_dir)
    plot_fit_curve_overall(pred_df, out_dir, resample_minutes=10)
    plot_fit_curve_by_station(pred_df, out_dir, resample_minutes=10)
    plot_fit_scatter(pred_df, out_dir)

    print("Done.")
    print(f"Output directory: {out_dir}")
    print("Stations used:")
    for r in results:
        print(f" - {r.station:8s}  lat={r.lat_deg:8.4f}  lon={r.lon_deg:8.4f}")
    print(f"Model epochs: {len(coef_df)}")
    if not pred_df.empty:
        rms = float(np.sqrt(np.mean(pred_df['residual']**2)))
        mae = float(np.mean(np.abs(pred_df['residual'])))
        print(f"Overall RMS: {rms:.3f} TECU")
        print(f"Overall MAE: {mae:.3f} TECU")


if __name__ == "__main__":
    main()
