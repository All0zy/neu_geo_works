
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real static PPP for HKSL daily precision comparison (2026-01-16 ~ 2026-01-22)

Features
--------
- GPS-only static PPP
- Uses observation (.o), broadcast nav (.n), precise orbit (.SP3), precise clock (.CLK),
  OSB bias (.BIA), and antenna file (.ATX) when available
- Iono-free code and phase combinations
- Static EKF with states:
    X,Y,Z, receiver clock, zenith wet delay, float ambiguities
- Simple cycle-slip detection using geometry-free phase combination
- Troposphere: Saastamoinen + Niell mapping + estimated ZWD
- Receiver antenna offset from RINEX header + ATX receiver PCO
- Daily formal precision + weekly repeatability (relative to weekly median coordinate)
- Produces CSV tables and figures

Notes
-----
This is a real-solution script, not a simulated one. However:
- Millimeter-level *absolute* PPP is not guaranteed from a single-day GPS-only solution.
- What is more realistic is centimeter-level absolute agreement and millimeter-to-centimeter
  formal precision / day-to-day repeatability on good days.
- Satellite antenna corrections, phase wind-up, and some geophysical corrections are simplified
  or omitted here to keep the code self-contained.
"""

import argparse
import gzip
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =============================================================================
# Constants
# =============================================================================
C = 299792458.0
OMEGA_E = 7.2921151467e-5
MU_GPS = 3.986005e14

F1 = 1575.42e6
F2 = 1227.60e6
L1 = C / F1
L2 = C / F2

ALPHA_IF = F1**2 / (F1**2 - F2**2)
BETA_IF = F2**2 / (F1**2 - F2**2)

RE = 6378137.0
F_WGS84 = 1 / 298.257223563
E2 = F_WGS84 * (2 - F_WGS84)

YEAR = 2026
DOYS = list(range(16, 23))

# process noise
SIG_POS_RW = 0.0005     # m / sqrt(epoch), static very small
SIG_CLK_RW = 100.0      # m / sqrt(epoch), receiver clock white-ish
SIG_ZWD_RW = 0.005      # m / sqrt(hour) -> converted below
SIG_AMB_RW = 0.00001    # m / sqrt(epoch), almost constant
SIG_AMB_INIT = 100.0    # m
SIG_CLK_INIT = 1e5      # m
SIG_ZWD_INIT = 0.3      # m
SIG_POS_INIT = 20.0     # m

# observation noise
CODE_SIGMA = 0.8        # m at zenith for IF code
PHASE_SIGMA = 0.01      # m at zenith for IF phase
MIN_ELEV_DEG = 10.0

# cycle slip
GF_JUMP_M = 0.08
GAP_SLIP_SEC = 120.0

# output labels
QUALITY_LEVELS = [
    (8.0, 10.0, "优秀"),
    (15.0, 20.0, "良好"),
    (30.0, 40.0, "一般"),
]


# =============================================================================
# Utility
# =============================================================================
def open_text_auto(path: Path):
    if str(path).lower().endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="ignore")
    return open(path, "r", encoding="utf-8", errors="ignore")


def doy_to_date(year: int, doy: int) -> datetime:
    return datetime(year, 1, 1) + timedelta(days=doy - 1)


def sod_of_dt(dt: datetime) -> float:
    return dt.hour * 3600.0 + dt.minute * 60.0 + dt.second + dt.microsecond * 1e-6


def safe_float(s: str) -> float:
    try:
        return float(s.replace("D", "E"))
    except Exception:
        return np.nan


def weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    if len(values) == 0:
        return np.nan
    idx = np.argsort(values)
    v = values[idx]
    w = weights[idx]
    cw = np.cumsum(w) / np.sum(w)
    return v[np.searchsorted(cw, 0.5)]


def resolve_data_dir(cli_data_dir: Optional[str]) -> Path:
    if cli_data_dir:
        return Path(cli_data_dir).expanduser().resolve()
    script_dir = Path(__file__).resolve().parent
    for cand in [script_dir, script_dir / "data2", Path.cwd(), Path.cwd() / "data2"]:
        if cand.exists():
            return cand.resolve()
    return script_dir


def find_first_existing(cands: List[Path]) -> Optional[Path]:
    for p in cands:
        if p.exists():
            return p
    return None


# =============================================================================
# Coordinate transforms
# =============================================================================
def ecef_to_geodetic(x, y, z):
    lon = math.atan2(y, x)
    p = math.hypot(x, y)
    lat = math.atan2(z, p * (1 - E2))
    for _ in range(10):
        sin_lat = math.sin(lat)
        N = RE / math.sqrt(1 - E2 * sin_lat * sin_lat)
        h = p / math.cos(lat) - N
        lat_new = math.atan2(z, p * (1 - E2 * N / (N + h)))
        if abs(lat_new - lat) < 1e-13:
            lat = lat_new
            break
        lat = lat_new
    sin_lat = math.sin(lat)
    N = RE / math.sqrt(1 - E2 * sin_lat * sin_lat)
    h = p / math.cos(lat) - N
    return lat, lon, h


def enu_to_ecef_vector(lat, lon, e, n, u):
    sl, cl = math.sin(lat), math.cos(lat)
    sb, cb = math.sin(lon), math.cos(lon)
    R = np.array([
        [-sb, -sl * cb, cl * cb],
        [ cb, -sl * sb, cl * sb],
        [ 0.0,     cl,     sl],
    ])
    return R @ np.array([e, n, u], dtype=float)


def ecef_to_enu_matrix(lat, lon):
    sl, cl = math.sin(lat), math.cos(lat)
    sb, cb = math.sin(lon), math.cos(lon)
    return np.array([
        [-sb,  cb, 0.0],
        [-sl * cb, -sl * sb, cl],
        [ cl * cb,  cl * sb, sl],
    ])


def ecef_diff_to_enu(ref_xyz, xyz):
    lat, lon, _ = ecef_to_geodetic(*ref_xyz)
    R = ecef_to_enu_matrix(lat, lon)
    return R @ (xyz - ref_xyz)


def sat_elev_az(rec_xyz, sat_xyz):
    lat, lon, _ = ecef_to_geodetic(*rec_xyz)
    R = ecef_to_enu_matrix(lat, lon)
    enu = R @ (sat_xyz - rec_xyz)
    e, n, u = enu
    el = math.atan2(u, math.hypot(e, n))
    az = math.atan2(e, n)
    if az < 0:
        az += 2 * math.pi
    return el, az


def earth_rotation_correction(sat_xyz, transit_time):
    ang = OMEGA_E * transit_time
    cos_a = math.cos(ang)
    sin_a = math.sin(ang)
    x, y, z = sat_xyz
    return np.array([cos_a * x + sin_a * y, -sin_a * x + cos_a * y, z], dtype=float)


# =============================================================================
# Niell mapping + Saastamoinen
# =============================================================================
def _interp_by_lat(lat_deg_abs, arr):
    lats = np.array([15.0, 30.0, 45.0, 60.0, 75.0], dtype=float)
    if lat_deg_abs <= lats[0]:
        return arr[0]
    if lat_deg_abs >= lats[-1]:
        return arr[-1]
    i = np.searchsorted(lats, lat_deg_abs) - 1
    t = (lat_deg_abs - lats[i]) / (lats[i + 1] - lats[i])
    return arr[i] * (1 - t) + arr[i + 1] * t


def niell_mapping(el_rad, lat_rad, doy, h_m):
    sinE = max(0.01, math.sin(el_rad))
    lat = abs(math.degrees(lat_rad))

    ah_avg = np.array([1.2769934e-3, 1.2683230e-3, 1.2465397e-3, 1.2196049e-3, 1.2045996e-3])
    bh_avg = np.array([2.9153695e-3, 2.9152299e-3, 2.9288445e-3, 2.9022565e-3, 2.9024912e-3])
    ch_avg = np.array([62.610505e-3, 62.837393e-3, 63.721774e-3, 63.824265e-3, 64.258455e-3])

    ah_amp = np.array([0.0, 1.2709626e-5, 2.6523662e-5, 3.4000452e-5, 4.1202191e-5])
    bh_amp = np.array([0.0, 2.1414979e-5, 3.0160779e-5, 7.2562722e-5, 1.1723375e-4])
    ch_amp = np.array([0.0, 9.0128400e-5, 4.3497037e-5, 8.4795348e-4, 1.7037206e-3])

    aw = np.array([5.8021897e-4, 5.6794847e-4, 5.8118019e-4, 5.9727542e-4, 6.1641693e-4])
    bw = np.array([1.4275268e-3, 1.5138625e-3, 1.4572752e-3, 1.5007428e-3, 1.7599082e-3])
    cw = np.array([4.3472961e-2, 4.6729510e-2, 4.3908931e-2, 4.4626982e-2, 5.4736038e-2])

    # seasonal term
    phase = 2 * math.pi * (doy - 28) / 365.25
    if lat_rad < 0:
        phase += math.pi

    a_h = _interp_by_lat(lat, ah_avg - ah_amp * math.cos(phase))
    b_h = _interp_by_lat(lat, bh_avg - bh_amp * math.cos(phase))
    c_h = _interp_by_lat(lat, ch_avg - ch_amp * math.cos(phase))
    a_w = _interp_by_lat(lat, aw)
    b_w = _interp_by_lat(lat, bw)
    c_w = _interp_by_lat(lat, cw)

    def mapping(a, b, c):
        top = 1 + a / (1 + b / (1 + c))
        bot = sinE + a / (sinE + b / (sinE + c))
        return top / bot

    mh = mapping(a_h, b_h, c_h)
    mw = mapping(a_w, b_w, c_w)

    # height correction (hydrostatic)
    hs_km = max(0.0, h_m / 1000.0)
    a_ht = 2.53e-5
    b_ht = 5.49e-3
    c_ht = 1.14e-3
    mht = (1 / sinE) - mapping(a_ht, b_ht, c_ht)
    mh += mht * hs_km

    return mh, mw


def saastamoinen_zhd(lat_rad, h_m):
    h = max(-100.0, h_m)
    P = 1013.25 * (1 - 2.2557e-5 * h) ** 5.2568
    return 0.0022768 * P / (1 - 0.00266 * math.cos(2 * lat_rad) - 0.00028 * h / 1e3)


# =============================================================================
# File discovery
# =============================================================================
@dataclass
class DayFiles:
    doy: int
    obs: Path
    nav: Optional[Path]
    sp3: Path
    clk: Optional[Path]
    bia: Optional[Path]
    atx: Optional[Path]


def discover_day_files(data_dir: Path) -> Dict[int, DayFiles]:
    atx = find_first_existing([
        data_dir / "I20.ATX",
        data_dir / "I20(1).ATX",
        data_dir / "IGS20_2401.ATX",
    ])
    files = {}
    for doy in DOYS:
        obs = find_first_existing([
            data_dir / f"hksl{doy:03d}0.26o",
            data_dir / f"hksl{doy:03d}0(1).26o",
            data_dir / f"hksl{doy:03d}0.26o.gz",
            data_dir / f"hksl{doy:03d}0(1).26o.gz",
        ])
        nav = find_first_existing([
            data_dir / f"brdc{doy:03d}0.26n",
            data_dir / f"brdc{doy:03d}0.26n.gz",
        ])
        sp3 = find_first_existing([
            data_dir / f"WUM0MGXRAP_{YEAR}{doy:03d}0000_01D_05M_ORB.SP3",
            data_dir / f"WUM0MGXRAP_{YEAR}{doy:03d}0000_01D_05M_ORB(1).SP3",
            data_dir / f"WUM0MGXRAP_{YEAR}{doy:03d}0000_01D_05M_ORB.SP3.gz",
            data_dir / f"WUM0MGXRAP_{YEAR}{doy:03d}0000_01D_05M_ORB(1).SP3.gz",
        ])
        clk = find_first_existing([
            data_dir / f"WUM0MGXRAP_{YEAR}{doy:03d}0000_01D_30S_CLK.CLK",
            data_dir / f"WUM0MGXRAP_{YEAR}{doy:03d}0000_01D_30S_CLK(1).CLK",
            data_dir / f"WUM0MGXRAP_{YEAR}{doy:03d}0000_01D_30S_CLK.CLK.gz",
            data_dir / f"WUM0MGXRAP_{YEAR}{doy:03d}0000_01D_30S_CLK(1).CLK.gz",
        ])
        bia = find_first_existing([
            data_dir / f"WUM0MGXRAP_{YEAR}{doy:03d}0000_01D_01D_OSB.BIA",
            data_dir / f"WUM0MGXRAP_{YEAR}{doy:03d}0000_01D_01D_OSB(1).BIA",
            data_dir / f"WUM0MGXRAP_{YEAR}{doy:03d}0000_01D_01D_OSB.BIA.gz",
            data_dir / f"WUM0MGXRAP_{YEAR}{doy:03d}0000_01D_01D_OSB(1).BIA.gz",
        ])

        if obs is None or sp3 is None:
            raise FileNotFoundError(f"DOY {doy} missing required obs/sp3 in {data_dir}")
        files[doy] = DayFiles(doy, obs, nav, sp3, clk, bia, atx)
    return files


# =============================================================================
# RINEX observation parser
# =============================================================================
@dataclass
class ObsHeader:
    approx_xyz: np.ndarray
    ant_delta_hen: np.ndarray  # H,E,N in meters
    ant_type: str
    radome: str
    rec_type: str
    obs_types: List[str]
    interval: float


@dataclass
class EpochObs:
    dt: datetime
    sod: float
    sats: Dict[str, Dict[str, float]]


def parse_rinex2_obs(path: Path, sample_step: int = 1) -> Tuple[ObsHeader, List[EpochObs]]:
    with open_text_auto(path) as f:
        lines = f.readlines()

    approx_xyz = np.array([np.nan, np.nan, np.nan], dtype=float)
    ant_delta_hen = np.array([0.0, 0.0, 0.0], dtype=float)
    ant_type = ""
    radome = ""
    rec_type = ""
    obs_types: List[str] = []
    interval = 30.0

    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        label = line[60:].strip() if len(line) >= 60 else ""

        if "APPROX POSITION XYZ" in label:
            parts = line[:60].split()
            approx_xyz = np.array([float(parts[0]), float(parts[1]), float(parts[2])], dtype=float)
        elif "ANTENNA: DELTA H/E/N" in label:
            parts = line[:60].split()
            ant_delta_hen = np.array([float(parts[0]), float(parts[1]), float(parts[2])], dtype=float)
        elif "ANT # / TYPE" in label:
            ant_type = line[20:36].strip()
            radome = line[36:40].strip()
        elif "REC # / TYPE / VERS" in label:
            rec_type = line[20:40].strip()
        elif "# / TYPES OF OBSERV" in label:
            parts = line[:60].split()
            n = int(parts[0])
            obs_types.extend(parts[1:])
            while len(obs_types) < n:
                i += 1
                obs_types.extend(lines[i][:60].split())
            obs_types = obs_types[:n]
        elif "INTERVAL" in label:
            try:
                interval = float(line[:10])
            except Exception:
                pass
        elif "END OF HEADER" in label:
            i += 1
            break
        i += 1

    header = ObsHeader(
        approx_xyz=approx_xyz,
        ant_delta_hen=ant_delta_hen,
        ant_type=ant_type,
        radome=radome if radome else "NONE",
        rec_type=rec_type,
        obs_types=obs_types,
        interval=interval,
    )

    epochs: List[EpochObs] = []
    epoch_index = 0
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
        sec_i = int(ss)
        usec = int(round((ss - sec_i) * 1e6))
        dt = datetime(year, mm, dd, hh, mi, sec_i, usec)

        sat_ids = []
        chunk = line[32:68]
        for k in range(0, len(chunk), 3):
            s = chunk[k:k + 3].strip()
            if s:
                sat_ids.append(s)

        while len(sat_ids) < nsat:
            i += 1
            cont = lines[i].rstrip("\n")
            chunk = cont[32:68]
            for k in range(0, len(chunk), 3):
                s = chunk[k:k + 3].strip()
                if s:
                    sat_ids.append(s)

        i += 1
        ntypes = len(obs_types)
        nlines_per_sat = (ntypes + 4) // 5
        sats = {}

        for sat in sat_ids:
            vals = []
            for _ in range(nlines_per_sat):
                if i >= len(lines):
                    break
                obs_line = lines[i].rstrip("\n")
                i += 1
                for k in range(0, min(80, len(obs_line)), 16):
                    field = obs_line[k:k + 16]
                    try:
                        vals.append(float(field[:14]))
                    except Exception:
                        vals.append(np.nan)
            vals = vals[:ntypes]
            sats[sat] = {k: v for k, v in zip(obs_types, vals)}

        if flag == 0:
            if epoch_index % sample_step == 0:
                epochs.append(EpochObs(dt=dt, sod=sod_of_dt(dt), sats=sats))
            epoch_index += 1

    return header, epochs


# =============================================================================
# SP3 precise orbit
# =============================================================================
def parse_sp3(path: Path) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    sat_t = {}
    sat_x = {}
    current_dt = None
    day_roll = 0
    prev_sod = None

    with open_text_auto(path) as f:
        for raw in f:
            line = raw.rstrip("\n")
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
                        day_roll += 1
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
                x = safe_float(line[4:18]) * 1000.0
                y = safe_float(line[18:32]) * 1000.0
                z = safe_float(line[32:46]) * 1000.0
                if not (np.isfinite(x) and np.isfinite(y) and np.isfinite(z)):
                    continue
                t = sod_of_dt(current_dt) + day_roll * 86400.0
                sat_t.setdefault(prn, []).append(t)
                sat_x.setdefault(prn, []).append([x, y, z])

    out = {}
    for prn, ts in sat_t.items():
        t = np.asarray(ts, dtype=float)
        x = np.asarray(sat_x[prn], dtype=float)
        idx = np.argsort(t)
        out[prn] = (t[idx], x[idx])
    return out


def interp_linear_vec(times: np.ndarray, values: np.ndarray, t: float) -> Optional[np.ndarray]:
    if len(times) < 2:
        return None
    tc = min(max(t, float(times[0])), float(times[-1]))
    return np.array([np.interp(tc, times, values[:, i]) for i in range(values.shape[1])], dtype=float)


# =============================================================================
# CLK precise clock
# =============================================================================
def parse_clk(path: Optional[Path]) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    if path is None:
        return {}
    sat_t = {}
    sat_clk = {}
    current_day_roll = {}
    prev_sod = {}

    with open_text_auto(path) as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.startswith("AS "):
                continue
            prn = line[3:6].strip()
            if not prn.startswith("G"):
                continue
            try:
                year = int(line[8:12])
                mon = int(line[13:15])
                day = int(line[16:18])
                hh = int(line[19:21])
                mi = int(line[22:24])
                ss = float(line[25:34])
                clk = safe_float(line[40:59])  # seconds
            except Exception:
                continue
            sec_i = int(ss)
            usec = int(round((ss - sec_i) * 1e6))
            dt = datetime(year, mon, day, hh, mi, sec_i, usec)
            sod = sod_of_dt(dt)

            if prn not in current_day_roll:
                current_day_roll[prn] = 0
                prev_sod[prn] = sod
            else:
                if sod < prev_sod[prn]:
                    current_day_roll[prn] += 1
                prev_sod[prn] = sod

            t = sod + current_day_roll[prn] * 86400.0
            sat_t.setdefault(prn, []).append(t)
            sat_clk.setdefault(prn, []).append(clk)

    out = {}
    for prn, ts in sat_t.items():
        t = np.asarray(ts, dtype=float)
        c = np.asarray(sat_clk[prn], dtype=float)
        idx = np.argsort(t)
        out[prn] = (t[idx], c[idx])
    return out


def interp_clk(clk_map: Dict[str, Tuple[np.ndarray, np.ndarray]], prn: str, t: float) -> Optional[float]:
    if prn not in clk_map:
        return None
    tt, cc = clk_map[prn]
    if len(tt) < 2:
        return None
    tc = min(max(t, float(tt[0])), float(tt[-1]))
    return float(np.interp(tc, tt, cc))


# =============================================================================
# Broadcast nav (TGD only fallback)
# =============================================================================
def parse_nav_tgd(path: Optional[Path]) -> Dict[str, float]:
    if path is None or not path.exists():
        return {}
    with open_text_auto(path) as f:
        lines = f.readlines()

    # RINEX2 nav: 8 lines per record after END OF HEADER
    i = 0
    while i < len(lines):
        if "END OF HEADER" in lines[i]:
            i += 1
            break
        i += 1

    tgd = {}
    while i + 7 < len(lines):
        l1 = lines[i]
        try:
            prn_num = int(l1[0:2])
            prn = f"G{prn_num:02d}"
        except Exception:
            i += 1
            continue
        # line 7 (0-based 6) has TGD in cols 42:61 typically
        l7 = lines[i + 6]
        val = safe_float(l7[42:61])
        if np.isfinite(val):
            tgd[prn] = val  # seconds
        i += 8
    return tgd


# =============================================================================
# OSB biases
# =============================================================================
def parse_bia_osb(path: Optional[Path]) -> Dict[Tuple[str, str], float]:
    if path is None or not path.exists():
        return {}
    out = {}
    with open_text_auto(path) as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.startswith(" DOCB "):
                continue
            parts = line.split()
            if len(parts) < 8:
                continue
            # DOCB G080 G01 C1C 2026:... ns 0.11975 0.00000
            prn = parts[2]
            obs = parts[3]
            unit = parts[6]
            value = safe_float(parts[7])
            if prn.startswith("G") and unit == "ns" and np.isfinite(value):
                out[(prn, obs)] = value * 1e-9 * C  # meters
    return out


def map_rinex2_code_to_osb(obs_name: str) -> Optional[str]:
    # conservative mapping for this HKSL GPS file
    mapping = {
        "C1": "C1C",
        "P1": "C1W",
        "P2": "C2W",
        "C2": "C2W",   # fallback
        "C5": "C5Q",
    }
    return mapping.get(obs_name)


# =============================================================================
# ATX receiver PCO
# =============================================================================
def parse_atx_receiver_pco(path: Optional[Path], ant_type: str, radome: str) -> Dict[str, np.ndarray]:
    """
    Return frequency PCO for GPS receiver antenna in meters:
      {"G01": [N,E,U], "G02": [N,E,U]}
    """
    if path is None or not path.exists():
        return {}
    ant_type = (ant_type or "").strip()
    radome = (radome or "NONE").strip()
    out = {}
    with open_text_auto(path) as f:
        lines = f.readlines()

    i = 0
    in_target = False
    while i < len(lines):
        line = lines[i].rstrip("\n")
        label = line[60:].strip() if len(line) >= 60 else ""

        if "START OF ANTENNA" in label:
            in_target = False
        elif "TYPE / SERIAL NO" in label:
            t = line[0:20].strip()
            r = line[20:40].strip()
            in_target = (t == ant_type and r == radome)
        elif in_target and "START OF FREQUENCY" in label:
            freq = line[:10].strip()
            i += 1
            if i < len(lines):
                pco_line = lines[i]
                try:
                    n = float(pco_line[0:10]) / 1000.0
                    e = float(pco_line[10:20]) / 1000.0
                    u = float(pco_line[20:30]) / 1000.0
                    out[freq] = np.array([n, e, u], dtype=float)
                except Exception:
                    pass
        elif in_target and "END OF ANTENNA" in label:
            break
        i += 1
    return out


def receiver_if_offset_ecef(header: ObsHeader, atx_pco: Dict[str, np.ndarray]) -> np.ndarray:
    # header delta: H/E/N
    lat, lon, _ = ecef_to_geodetic(*header.approx_xyz)
    e = header.ant_delta_hen[1]
    n = header.ant_delta_hen[2]
    u = header.ant_delta_hen[0]

    pco1 = atx_pco.get("G01", np.zeros(3))
    pco2 = atx_pco.get("G02", np.zeros(3))
    # ATX order N/E/U
    pco1_enu = np.array([pco1[1], pco1[0], pco1[2]])
    pco2_enu = np.array([pco2[1], pco2[0], pco2[2]])
    if_pco_enu = ALPHA_IF * pco1_enu - BETA_IF * pco2_enu

    total_enu = np.array([e, n, u], dtype=float) + if_pco_enu
    return enu_to_ecef_vector(lat, lon, *total_enu)


# =============================================================================
# Observation selection and combinations
# =============================================================================
def choose_code_pair(obs_map: Dict[str, float]) -> Optional[Tuple[str, str, float, float]]:
    for a, b in [("C1", "P2"), ("P1", "P2"), ("C1", "C2")]:
        va = obs_map.get(a, np.nan)
        vb = obs_map.get(b, np.nan)
        if np.isfinite(va) and np.isfinite(vb):
            return a, b, float(va), float(vb)
    return None


def choose_phase_pair(obs_map: Dict[str, float]) -> Optional[Tuple[float, float]]:
    l1 = obs_map.get("L1", np.nan)
    l2 = obs_map.get("L2", np.nan)
    if np.isfinite(l1) and np.isfinite(l2):
        return float(l1), float(l2)
    return None


def if_code(p1_m: float, p2_m: float) -> float:
    return ALPHA_IF * p1_m - BETA_IF * p2_m


def if_phase(l1_cyc: float, l2_cyc: float) -> float:
    return ALPHA_IF * (l1_cyc * L1) - BETA_IF * (l2_cyc * L2)


# =============================================================================
# Kalman filter PPP
# =============================================================================
@dataclass
class PPPResult:
    doy: int
    date: str
    daily_xyz: np.ndarray
    formal_xyz_std_m: np.ndarray
    n_used_epochs: int
    n_final_sats_med: float
    converged: bool
    epoch_df: pd.DataFrame = field(default_factory=pd.DataFrame)


class StaticPPP:
    def __init__(
        self,
        header: ObsHeader,
        epochs: List[EpochObs],
        sp3: Dict[str, Tuple[np.ndarray, np.ndarray]],
        clk: Dict[str, Tuple[np.ndarray, np.ndarray]],
        bia: Dict[Tuple[str, str], float],
        nav_tgd: Dict[str, float],
        sample_interval: float,
    ):
        self.header = header
        self.epochs = epochs
        self.sp3 = sp3
        self.clk = clk
        self.bia = bia
        self.nav_tgd = nav_tgd
        self.sample_interval = sample_interval

        self.rec_apc_offset_ecef = np.zeros(3)
        self._setup_offsets()

        self.state = None
        self.P = None
        self.amb_index: Dict[str, int] = {}
        self.last_gf: Dict[str, float] = {}
        self.last_t: Dict[str, float] = {}

        self.epoch_solutions = []

    def _setup_offsets(self):
        atx_pco = parse_atx_receiver_pco(
            self.header_path_atx if hasattr(self, "header_path_atx") else None,
            self.header.ant_type,
            self.header.radome,
        )

    def set_receiver_apc_offset(self, dr_ecef: np.ndarray):
        self.rec_apc_offset_ecef = dr_ecef.copy()

    def init_filter(self):
        x0 = np.zeros(5, dtype=float)
        x0[0:3] = self.header.approx_xyz
        x0[3] = 0.0      # receiver clock (m)
        x0[4] = 0.10     # zwd (m)
        self.state = x0
        self.P = np.diag([SIG_POS_INIT**2] * 3 + [SIG_CLK_INIT**2, SIG_ZWD_INIT**2])

    def augment_ambiguity(self, prn: str, approx_amb: float = 0.0):
        if prn in self.amb_index:
            return
        old_n = len(self.state)
        self.state = np.concatenate([self.state, [approx_amb]])
        P_new = np.zeros((old_n + 1, old_n + 1))
        P_new[:old_n, :old_n] = self.P
        P_new[old_n, old_n] = SIG_AMB_INIT**2
        self.P = P_new
        self.amb_index[prn] = old_n

    def reset_ambiguity(self, prn: str):
        if prn not in self.amb_index:
            return
        idx = self.amb_index[prn]
        self.P[idx, idx] = SIG_AMB_INIT**2

    def time_update(self, dt_sec: float):
        if dt_sec <= 0:
            return
        q_pos = (SIG_POS_RW * math.sqrt(dt_sec / self.sample_interval)) ** 2
        q_clk = (SIG_CLK_RW * math.sqrt(dt_sec / self.sample_interval)) ** 2
        q_zwd = (SIG_ZWD_RW * math.sqrt(dt_sec / 3600.0)) ** 2
        q_amb = (SIG_AMB_RW * math.sqrt(dt_sec / self.sample_interval)) ** 2

        Q = np.zeros_like(self.P)
        Q[0, 0] = q_pos
        Q[1, 1] = q_pos
        Q[2, 2] = q_pos
        Q[3, 3] = q_clk
        Q[4, 4] = q_zwd
        for prn, idx in self.amb_index.items():
            Q[idx, idx] = q_amb
        self.P = self.P + Q

    def _obs_for_sat(self, ep: EpochObs, prn: str):
        omap = ep.sats.get(prn)
        if omap is None:
            return None

        code_sel = choose_code_pair(omap)
        phase_sel = choose_phase_pair(omap)
        if code_sel is None or phase_sel is None:
            return None

        c1_name, c2_name, p1, p2 = code_sel
        l1, l2 = phase_sel

        # code OSB correction in meters
        b1 = 0.0
        b2 = 0.0
        osb1 = map_rinex2_code_to_osb(c1_name)
        osb2 = map_rinex2_code_to_osb(c2_name)
        if osb1 is not None:
            b1 = self.bia.get((prn, osb1), 0.0)
        if osb2 is not None:
            b2 = self.bia.get((prn, osb2), 0.0)

        p1c = p1 - b1
        p2c = p2 - b2

        Pif = if_code(p1c, p2c)
        Lif = if_phase(l1, l2)

        # simple cycle slip detection with geometry-free phase
        gf = l1 * L1 - l2 * L2
        slipped = False
        if prn in self.last_gf:
            dt_gap = ep.sod - self.last_t[prn]
            if dt_gap > GAP_SLIP_SEC or abs(gf - self.last_gf[prn]) > GF_JUMP_M:
                slipped = True
        self.last_gf[prn] = gf
        self.last_t[prn] = ep.sod

        return {
            "Pif": Pif,
            "Lif": Lif,
            "slipped": slipped,
        }

    def _precise_sat(self, prn: str, t_sec: float, rec_xyz: np.ndarray):
        if prn not in self.sp3:
            return None
        tt, xx = self.sp3[prn]
        sat0 = interp_linear_vec(tt, xx, t_sec)
        if sat0 is None:
            return None

        rho0 = np.linalg.norm(sat0 - rec_xyz)
        tau = rho0 / C
        sat = interp_linear_vec(tt, xx, t_sec - tau)
        if sat is None:
            sat = sat0
        sat = earth_rotation_correction(sat, tau)

        dts = interp_clk(self.clk, prn, t_sec - tau)
        if dts is None:
            dts = 0.0
        return sat, dts

    def process(self) -> PPPResult:
        self.init_filter()
        lat0, lon0, h0 = ecef_to_geodetic(*self.header.approx_xyz)
        zhd = saastamoinen_zhd(lat0, h0)

        last_sod = None
        epoch_out = []


        for ep in self.epochs:
            if last_sod is None:
                last_sod = ep.sod
            self.time_update(ep.sod - last_sod)
            last_sod = ep.sod

            # Prepare observations once per epoch (avoids duplicate slip bookkeeping)
            rec_xyz_pre = self.state[0:3].copy()
            obs_cache = {}
            visible_prns = []
            for prn in [s for s in ep.sats.keys() if s.startswith("G")]:
                obs = self._obs_for_sat(ep, prn)
                if obs is None:
                    continue
                satclk = self._precise_sat(prn, ep.sod, rec_xyz_pre)
                if satclk is None:
                    continue
                sat_xyz, dts = satclk
                el, _ = sat_elev_az(rec_xyz_pre, sat_xyz)
                if el < math.radians(MIN_ELEV_DEG):
                    continue
                if prn not in self.amb_index:
                    self.augment_ambiguity(prn, obs["Lif"] - obs["Pif"])
                elif obs["slipped"]:
                    self.reset_ambiguity(prn)
                    self.state[self.amb_index[prn]] = obs["Lif"] - obs["Pif"]
                obs_cache[prn] = obs
                visible_prns.append(prn)

            x = self.state.copy()
            P = self.P.copy()

            for it in range(2):  # light iteration
                H_rows = []
                v_rows = []
                R_diag = []
                used_sats = []

                rec_xyz = x[0:3]
                lat, lon, h = ecef_to_geodetic(*rec_xyz)
                mh_cache = {}
                mw_cache = {}

                # coarse clock initialization from code prefit at current position
                if it == 0:
                    coarse_terms = []
                    for prn0 in visible_prns:
                        obs0 = obs_cache[prn0]
                        satclk0 = self._precise_sat(prn0, ep.sod, rec_xyz)
                        if satclk0 is None:
                            continue
                        sat_xyz0, dts0 = satclk0
                        el0, _ = sat_elev_az(rec_xyz, sat_xyz0)
                        if el0 < math.radians(MIN_ELEV_DEG):
                            continue
                        rho_vec0 = sat_xyz0 - rec_xyz
                        rho0 = np.linalg.norm(rho_vec0)
                        if rho0 < 1.0:
                            continue
                        los0 = rho_vec0 / rho0
                        apc_corr0 = -np.dot(los0, self.rec_apc_offset_ecef)
                        mh0, mw0 = niell_mapping(el0, lat, ep.dt.timetuple().tm_yday, h)
                        trop0 = mh0 * zhd + mw0 * x[4]
                        coarse_terms.append(obs0["Pif"] - (rho0 - C * dts0 + trop0 + apc_corr0))
                    if len(coarse_terms) >= 4:
                        x[3] = float(np.median(coarse_terms))

                for prn in visible_prns:
                    obs = obs_cache[prn]
                    satclk = self._precise_sat(prn, ep.sod, rec_xyz)
                    if satclk is None:
                        continue
                    sat_xyz, dts = satclk

                    el, az = sat_elev_az(rec_xyz, sat_xyz)
                    if el < math.radians(MIN_ELEV_DEG):
                        continue

                    idx_amb = self.amb_index[prn]

                    rho_vec = sat_xyz - rec_xyz
                    rho = np.linalg.norm(rho_vec)
                    if rho < 1.0:
                        continue
                    los = rho_vec / rho

                    apc_corr = -np.dot(los, self.rec_apc_offset_ecef)

                    if prn not in mh_cache:
                        mh, mw = niell_mapping(el, lat, ep.dt.timetuple().tm_yday, h)
                        mh_cache[prn] = mh
                        mw_cache[prn] = mw
                    mh = mh_cache[prn]
                    mw = mw_cache[prn]
                    trop = mh * zhd + mw * x[4]

                    pred_geom = rho + x[3] - C * dts + trop + apc_corr

                    v_code = obs["Pif"] - pred_geom
                    h_code = np.zeros(len(x))
                    h_code[0:3] = -los
                    h_code[3] = 1.0
                    h_code[4] = mw

                    v_phase = obs["Lif"] - (pred_geom + x[idx_amb])
                    h_phase = h_code.copy()
                    h_phase[idx_amb] = 1.0

                    sin_el = max(0.1, math.sin(el))
                    sig_code = CODE_SIGMA / sin_el
                    sig_phase = PHASE_SIGMA / sin_el

                    if abs(v_code) > 50.0 or abs(v_phase) > 20.0:
                        continue

                    H_rows.append(h_code)
                    v_rows.append(v_code)
                    R_diag.append(sig_code**2)

                    H_rows.append(h_phase)
                    v_rows.append(v_phase)
                    R_diag.append(sig_phase**2)

                    used_sats.append(prn)

                if len(used_sats) < 4:
                    break

                H = np.vstack(H_rows)
                v = np.asarray(v_rows, dtype=float)
                Rm = np.diag(R_diag)

                innov_sigma = np.sqrt(np.clip(np.diag(Rm), 1e-12, None))
                robust = np.ones_like(v)
                for k in range(len(v)):
                    r = abs(v[k]) / innov_sigma[k]
                    if r > 6:
                        robust[k] = 100.0
                    elif r > 3:
                        robust[k] = (r / 3.0) ** 2
                Rm = np.diag(np.diag(Rm) * robust)

                S = H @ P @ H.T + Rm
                try:
                    K = P @ H.T @ np.linalg.inv(S)
                except np.linalg.LinAlgError:
                    K = P @ H.T @ np.linalg.pinv(S)

                dx = K @ v
                x = x + dx
                I = np.eye(len(x))
                P = (I - K @ H) @ P @ (I - K @ H).T + K @ Rm @ K.T

                if np.linalg.norm(dx[0:3]) < 1e-4 and abs(dx[4]) < 1e-4:
                    break

            self.state = x
            self.P = P

            pos_std = np.sqrt(np.clip(np.diag(P)[0:3], 0, None))
            n_used = len(set(used_sats)) if 'used_sats' in locals() else 0

            epoch_out.append({
                "datetime": ep.dt,
                "sod": ep.sod,
                "x": x[0],
                "y": x[1],
                "z": x[2],
                "clk_m": x[3],
                "zwd_m": x[4],
                "std_x_m": pos_std[0],
                "std_y_m": pos_std[1],
                "std_z_m": pos_std[2],
                "nsat": n_used,
            })

        epoch_df = pd.DataFrame(epoch_out)
        if len(epoch_df) < 20:
            return PPPResult(
                doy=0, date="", daily_xyz=np.array([np.nan, np.nan, np.nan]),
                formal_xyz_std_m=np.array([np.nan, np.nan, np.nan]),
                n_used_epochs=0, n_final_sats_med=np.nan, converged=False, epoch_df=epoch_df
            )

        # stable segment = last 25% epochs with nsat>=4
        epoch_df = epoch_df[epoch_df["nsat"] >= 4].copy()
        if len(epoch_df) < 20:
            return PPPResult(
                doy=0, date="", daily_xyz=np.array([np.nan, np.nan, np.nan]),
                formal_xyz_std_m=np.array([np.nan, np.nan, np.nan]),
                n_used_epochs=0, n_final_sats_med=np.nan, converged=False, epoch_df=epoch_df
            )

        start = int(len(epoch_df) * 0.75)
        stable = epoch_df.iloc[start:].copy()
        if len(stable) < 10:
            stable = epoch_df.iloc[max(0, len(epoch_df)-20):].copy()

        w = 1.0 / np.clip(stable[["std_x_m", "std_y_m", "std_z_m"]].mean(axis=1).to_numpy(), 1e-4, None)
        xyz = np.vstack([stable["x"].to_numpy(), stable["y"].to_numpy(), stable["z"].to_numpy()]).T
        daily_xyz = np.array([weighted_median(xyz[:, i], w) for i in range(3)], dtype=float)
        formal_std = stable[["std_x_m", "std_y_m", "std_z_m"]].median().to_numpy(dtype=float)

        return PPPResult(
            doy=ep.dt.timetuple().tm_yday,
            date=ep.dt.strftime("%Y-%m-%d"),
            daily_xyz=daily_xyz,
            formal_xyz_std_m=formal_std,
            n_used_epochs=len(epoch_df),
            n_final_sats_med=float(stable["nsat"].median()),
            converged=True,
            epoch_df=epoch_df,
        )


# =============================================================================
# Daily processing
# =============================================================================
def run_one_day(day: DayFiles, sample_step: int = 1) -> PPPResult:
    header, epochs = parse_rinex2_obs(day.obs, sample_step=sample_step)
    if not np.all(np.isfinite(header.approx_xyz)) or np.linalg.norm(header.approx_xyz) < 1e6:
        raise RuntimeError(f"{day.obs.name}: invalid APPROX POSITION XYZ")

    sp3 = parse_sp3(day.sp3)
    clk = parse_clk(day.clk)
    bia = parse_bia_osb(day.bia)
    nav_tgd = parse_nav_tgd(day.nav)

    pco = parse_atx_receiver_pco(day.atx, header.ant_type, header.radome)
    rec_if_off = receiver_if_offset_ecef(header, pco)

    ppp = StaticPPP(header, epochs, sp3, clk, bia, nav_tgd, header.interval * sample_step)
    ppp.set_receiver_apc_offset(rec_if_off)

    result = ppp.process()
    result.doy = day.doy
    result.date = doy_to_date(YEAR, day.doy).strftime("%Y-%m-%d")
    return result


def quality_label(formal_3d_mm: float, d3d_mm: float) -> str:
    for f_thr, d_thr, label in QUALITY_LEVELS:
        if formal_3d_mm <= f_thr and d3d_mm <= d_thr:
            return label
    return "较差"


# =============================================================================
# Plotting
# =============================================================================
def plot_daily_precision(df: pd.DataFrame, out_png: Path):
    plt.figure(figsize=(10, 5.5))
    x = np.arange(len(df))
    labels = df["date"].tolist()
    plt.plot(x, df["std_E_mm"], marker="o", label="E")
    plt.plot(x, df["std_N_mm"], marker="o", label="N")
    plt.plot(x, df["std_U_mm"], marker="o", label="U")
    plt.plot(x, df["formal_3d_std_mm"], marker="o", linewidth=2.2, label="3D formal precision")
    plt.xticks(x, labels, rotation=20)
    plt.ylabel("Formal precision (mm)")
    plt.title("HKSL daily static PPP formal precision")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=220)
    plt.close()


def plot_daily_repeatability(df: pd.DataFrame, out_png: Path):
    plt.figure(figsize=(10, 5.5))
    x = np.arange(len(df))
    labels = df["date"].tolist()
    plt.plot(x, df["dE_mm"], marker="o", label="dE")
    plt.plot(x, df["dN_mm"], marker="o", label="dN")
    plt.plot(x, df["dU_mm"], marker="o", label="dU")
    plt.plot(x, df["d3D_mm"], marker="o", linewidth=2.2, label="d3D")
    plt.xticks(x, labels, rotation=20)
    plt.ylabel("Offset relative to weekly reference (mm)")
    plt.title("HKSL daily PPP repeatability relative to weekly median coordinate")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=220)
    plt.close()


def plot_epoch_convergence(epoch_df: pd.DataFrame, ref_xyz: np.ndarray, out_png: Path, title: str):
    if epoch_df.empty:
        return
    diffs = np.vstack([ecef_diff_to_enu(ref_xyz, row[["x", "y", "z"]].to_numpy(dtype=float)) for _, row in epoch_df.iterrows()])
    plt.figure(figsize=(10, 6))
    plt.plot(epoch_df["sod"] / 3600.0, diffs[:, 0] * 1000.0, label="E")
    plt.plot(epoch_df["sod"] / 3600.0, diffs[:, 1] * 1000.0, label="N")
    plt.plot(epoch_df["sod"] / 3600.0, diffs[:, 2] * 1000.0, label="U")
    plt.xlabel("UTC hour")
    plt.ylabel("Offset from daily solution (mm)")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=220)
    plt.close()


# =============================================================================
# Main workflow
# =============================================================================
def run_weekly_ppp(data_dir: Path, out_dir: Path, sample_step: int = 1):
    out_dir.mkdir(parents=True, exist_ok=True)
    files = discover_day_files(data_dir)

    results: List[PPPResult] = []
    for doy in DOYS:
        print(f"[INFO] PPP processing DOY {doy} ...")
        try:
            res = run_one_day(files[doy], sample_step=sample_step)
        except Exception as e:
            print(f"[WARN] DOY {doy} failed: {e}")
            res = PPPResult(
                doy=doy,
                date=doy_to_date(YEAR, doy).strftime("%Y-%m-%d"),
                daily_xyz=np.array([np.nan, np.nan, np.nan]),
                formal_xyz_std_m=np.array([np.nan, np.nan, np.nan]),
                n_used_epochs=0,
                n_final_sats_med=np.nan,
                converged=False,
                epoch_df=pd.DataFrame(),
            )
        results.append(res)

    # weekly reference coordinate = median of valid daily coordinates
    valids = [r for r in results if r.converged and np.all(np.isfinite(r.daily_xyz))]
    if not valids:
        raise RuntimeError("No valid daily PPP solutions were produced.")

    xyz_stack = np.vstack([r.daily_xyz for r in valids])
    ref_xyz = np.median(xyz_stack, axis=0)

    rows = []
    ref_lat, ref_lon, _ = ecef_to_geodetic(*ref_xyz)
    for r in results:
        row = {
            "date": r.date,
            "doy": r.doy,
            "converged": r.converged,
            "n_used_epochs": r.n_used_epochs,
            "median_nsat_stable": r.n_final_sats_med,
            "X_m": r.daily_xyz[0],
            "Y_m": r.daily_xyz[1],
            "Z_m": r.daily_xyz[2],
        }
        if r.converged and np.all(np.isfinite(r.daily_xyz)):
            enu_std = ecef_to_enu_matrix(ref_lat, ref_lon) @ r.formal_xyz_std_m  # only indicative
            # better: transform covariance; absent cross-cov -> approximate with xyz std
            denu = ecef_diff_to_enu(ref_xyz, r.daily_xyz)
            row["dE_mm"] = denu[0] * 1000.0
            row["dN_mm"] = denu[1] * 1000.0
            row["dU_mm"] = denu[2] * 1000.0
            row["d3D_mm"] = np.linalg.norm(denu) * 1000.0

            row["std_X_mm"] = r.formal_xyz_std_m[0] * 1000.0
            row["std_Y_mm"] = r.formal_xyz_std_m[1] * 1000.0
            row["std_Z_mm"] = r.formal_xyz_std_m[2] * 1000.0

            # approximate ENU std from diagonal only
            R = ecef_to_enu_matrix(ref_lat, ref_lon)
            Cxyz = np.diag(r.formal_xyz_std_m**2)
            Cenu = R @ Cxyz @ R.T
            std_enu = np.sqrt(np.clip(np.diag(Cenu), 0, None)) * 1000.0
            row["std_E_mm"] = std_enu[0]
            row["std_N_mm"] = std_enu[1]
            row["std_U_mm"] = std_enu[2]
            row["formal_3d_std_mm"] = np.sqrt(np.sum(std_enu**2))
            row["quality"] = quality_label(row["formal_3d_std_mm"], row["d3D_mm"])
        else:
            for k in ["dE_mm","dN_mm","dU_mm","d3D_mm","std_X_mm","std_Y_mm","std_Z_mm",
                      "std_E_mm","std_N_mm","std_U_mm","formal_3d_std_mm"]:
                row[k] = np.nan
            row["quality"] = "失败"
        rows.append(row)

    df = pd.DataFrame(rows).sort_values("doy").reset_index(drop=True)
    df.to_csv(out_dir / "task2_ppp_daily_quality.csv", index=False)

    pd.DataFrame([{
        "ref_X_m": ref_xyz[0],
        "ref_Y_m": ref_xyz[1],
        "ref_Z_m": ref_xyz[2],
    }]).to_csv(out_dir / "task2_ppp_reference_coordinate.csv", index=False)

    for r in results:
        if r.converged and not r.epoch_df.empty:
            plot_epoch_convergence(
                r.epoch_df, r.daily_xyz,
                out_dir / f"task2_ppp_convergence_{r.date}.png",
                f"HKSL PPP convergence {r.date}"
            )

    plot_daily_precision(df, out_dir / "task2_ppp_daily_precision_mm.png")
    plot_daily_repeatability(df, out_dir / "task2_ppp_daily_repeatability_mm.png")

    lines = []
    lines.append("HKSL weekly static PPP summary")
    lines.append("")
    best_prec = df.loc[df["formal_3d_std_mm"].idxmin()]
    worst_prec = df.loc[df["formal_3d_std_mm"].idxmax()]
    lines.append(f"Best formal precision day: {best_prec['date']}, 3D std = {best_prec['formal_3d_std_mm']:.2f} mm")
    lines.append(f"Worst formal precision day: {worst_prec['date']}, 3D std = {worst_prec['formal_3d_std_mm']:.2f} mm")
    lines.append("")
    lines.append("Daily quality table:")
    for _, row in df.iterrows():
        lines.append(
            f"{row['date']}: quality={row['quality']}, formal_3d_std={row['formal_3d_std_mm']:.2f} mm, "
            f"d3D={row['d3D_mm']:.2f} mm, epochs={int(row['n_used_epochs']) if np.isfinite(row['n_used_epochs']) else 0}"
        )
    (out_dir / "task2_ppp_report_text.txt").write_text("\n".join(lines), encoding="utf-8")

    print("[DONE] saved to", out_dir)
    return df


def main():
    parser = argparse.ArgumentParser(description="Real static PPP daily precision for HKSL")
    parser.add_argument("--data-dir", type=str, default=None, help="data folder")
    parser.add_argument("--out-dir", type=str, default=None, help="output folder")
    parser.add_argument("--sample-step", type=int, default=1, help="use every N-th epoch (1=30s all epochs)")
    args = parser.parse_args()

    data_dir = resolve_data_dir(args.data_dir)
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else (data_dir / "task2_ppp_real_outputs")
    run_weekly_ppp(data_dir, out_dir, sample_step=max(1, int(args.sample_step)))


if __name__ == "__main__":
    main()
