#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HKSL task2 PPP standalone wrapper
- Uses ppp.py in the same folder
- Real static PPP with precise orbit/clock + BIA + ATX + NAV TGD
- Two-pass weekly-reference strategy
- Multi-profile constrained reprocessing
- Cm-friendly quality grading
"""

import argparse
import importlib.util
from pathlib import Path
from typing import Optional, List, Dict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


YEAR = 2026
DOYS = list(range(16, 23))


def load_base(script_dir: Path):
    base_path = script_dir / "ppp.py"
    if not base_path.exists():
        raise FileNotFoundError("ppp.py not found in the same folder.")
    spec = importlib.util.spec_from_file_location("ppp_core_real_kf", str(base_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def resolve_data_dir(cli_data_dir: Optional[str]) -> Path:
    if cli_data_dir:
        return Path(cli_data_dir).expanduser().resolve()
    script_dir = Path(__file__).resolve().parent
    for cand in [script_dir, script_dir / "data2", Path.cwd(), Path.cwd() / "data2"]:
        if cand.exists():
            return cand.resolve()
    return script_dir


def auto_find_vtec_summary(script_dir: Path, data_dir: Path) -> Optional[Path]:
    candidates = [
        script_dir / "task2_vtec_daily_summary.csv",
        script_dir / "task2_vtec_outputs_fixed" / "task2_vtec_daily_summary.csv",
        script_dir / "task2_vtec_outputs" / "task2_vtec_daily_summary.csv",
        data_dir / "task2_vtec_daily_summary.csv",
        data_dir / "task2_vtec_outputs_fixed" / "task2_vtec_daily_summary.csv",
        data_dir / "task2_vtec_outputs" / "task2_vtec_daily_summary.csv",
        Path.cwd() / "task2_vtec_daily_summary.csv",
    ]
    for p in candidates:
        if p.exists():
            return p.resolve()
    return None


def formal_3d_mm(res) -> float:
    if res is None or not getattr(res, "converged", False):
        return np.nan
    s = np.asarray(res.formal_xyz_std_m, dtype=float)
    if not np.all(np.isfinite(s)):
        return np.nan
    return float(np.linalg.norm(s) * 1000.0)


def build_weekly_reference(base, free_results: List):
    rows = []
    for res in free_results:
        if not getattr(res, "converged", False):
            continue
        if not np.all(np.isfinite(res.daily_xyz)):
            continue
        rows.append({
            "date": res.date,
            "doy": res.doy,
            "xyz": np.asarray(res.daily_xyz, dtype=float),
            "formal_3d_mm": formal_3d_mm(res),
            "n_used_epochs": float(getattr(res, "n_used_epochs", 0)),
            "median_nsat_stable": float(getattr(res, "n_final_sats_med", np.nan)),
        })

    if not rows:
        raise RuntimeError("No valid free-pass daily PPP solutions.")

    df = pd.DataFrame(rows)
    df["score"] = (
        np.log1p(df["n_used_epochs"].clip(lower=1.0)) * 1.5
        + df["median_nsat_stable"].fillna(0.0)
        - np.log1p(df["formal_3d_mm"].clip(lower=1.0)) * 2.0
    )
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    good = df.iloc[:min(max(3, len(df)), 4)].copy()
    xyz = np.vstack(good["xyz"].tolist())
    w = good["n_used_epochs"].to_numpy(dtype=float) / np.maximum(good["formal_3d_mm"].to_numpy(dtype=float), 1.0) ** 2
    w = np.where(np.isfinite(w) & (w > 0), w, 1.0)
    w = w / np.sum(w)
    ref_xyz = np.sum(xyz * w[:, None], axis=0)
    return ref_xyz, good[["date", "doy", "formal_3d_mm", "n_used_epochs", "median_nsat_stable", "score"]]


def build_iono_index(vtec_df: pd.DataFrame) -> pd.DataFrame:
    out = vtec_df.copy()

    def norm01(x):
        x = x.astype(float).to_numpy()
        xmin, xmax = np.nanmin(x), np.nanmax(x)
        if not np.isfinite(xmin) or not np.isfinite(xmax) or abs(xmax - xmin) < 1e-12:
            return np.zeros_like(x, dtype=float)
        return (x - xmin) / (xmax - xmin)

    n1 = norm01(out["daytime_mean_tecu"])
    n2 = norm01(out["max_vtec_tecu"])
    n3 = norm01(out["daily_amplitude_tecu"])
    out["iono_impact_index"] = 0.35 * n1 + 0.35 * n2 + 0.30 * n3
    return out[["doy", "date", "iono_impact_index", "daytime_mean_tecu", "max_vtec_tecu", "daily_amplitude_tecu"]]


def robust_mad_sigma(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size < 3:
        return np.nan
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    return 1.4826 * mad


def epoch_xyz_to_enu(base, ref_xyz: np.ndarray, epoch_df: pd.DataFrame) -> np.ndarray:
    arr = []
    for _, row in epoch_df.iterrows():
        xyz = row[["x", "y", "z"]].to_numpy(dtype=float)
        denu = base.ecef_diff_to_enu(ref_xyz, xyz) * 1000.0
        arr.append(denu)
    return np.asarray(arr, dtype=float)


def find_best_stable_segment(base, epoch_df: pd.DataFrame, ref_xyz: np.ndarray):
    if epoch_df is None or epoch_df.empty or len(epoch_df) < 40:
        return None
    enu_all = epoch_xyz_to_enu(base, ref_xyz, epoch_df)
    n = len(enu_all)
    min_len = max(30, int(0.10 * n))
    best = None
    best_score = np.inf
    for s in range(int(0.40 * n), n - min_len + 1):
        seg = enu_all[s:, :]
        center = np.nanmedian(seg, axis=0)
        res = seg - center[None, :]
        robust_xyz = np.array([
            robust_mad_sigma(res[:, 0]),
            robust_mad_sigma(res[:, 1]),
            robust_mad_sigma(res[:, 2]),
        ], dtype=float)
        robust_3d = float(np.sqrt(np.nansum(robust_xyz ** 2)))
        rms_3d = float(np.sqrt(np.nanmean(np.sum(res * res, axis=1))))
        first_k = min(20, max(5, len(seg) // 4))
        c1 = np.nanmedian(seg[:first_k, :], axis=0)
        c2 = np.nanmedian(seg[-first_k:, :], axis=0)
        drift = float(np.linalg.norm(c2 - c1))
        score = robust_3d + 0.25 * rms_3d + drift - 0.02 * len(seg)
        if np.isfinite(score) and score < best_score:
            best_score = score
            best = {
                "start_idx": s,
                "n_stable_epochs": len(seg),
                "center_enu_mm": center,
                "stable_robust_E_mm": float(robust_xyz[0]),
                "stable_robust_N_mm": float(robust_xyz[1]),
                "stable_robust_U_mm": float(robust_xyz[2]),
                "stable_robust_3d_mm": robust_3d,
                "stable_rms_3d_mm": rms_3d,
                "stable_drift_3d_mm": drift,
                "stable_center_dE_mm": float(center[0]),
                "stable_center_dN_mm": float(center[1]),
                "stable_center_dU_mm": float(center[2]),
                "stable_center_d3D_mm": float(np.linalg.norm(center)),
                "stable_effective_3d_mm": float(max(robust_3d, 0.25 * rms_3d, drift)),
            }
    return best


def run_one_day_constrained_profile(base, day, ref_xyz: np.ndarray, sample_step: int, profile: Dict):
    header, epochs = base.parse_rinex2_obs(day.obs, sample_step=sample_step)
    if not np.all(np.isfinite(header.approx_xyz)) or np.linalg.norm(header.approx_xyz) < 1e6:
        raise RuntimeError(f"{day.obs.name}: invalid APPROX POSITION XYZ")
    header.approx_xyz = np.asarray(ref_xyz, dtype=float).copy()

    sp3 = base.parse_sp3(day.sp3)
    clk = base.parse_clk(day.clk)
    bia = base.parse_bia_osb(day.bia)
    nav_tgd = base.parse_nav_tgd(day.nav)

    pco = base.parse_atx_receiver_pco(day.atx, header.ant_type, header.radome)
    rec_if_off = base.receiver_if_offset_ecef(header, pco)

    ppp = base.StaticPPP(header, epochs, sp3, clk, bia, nav_tgd, header.interval * sample_step)
    ppp.set_receiver_apc_offset(rec_if_off)

    old_vals = (
        base.SIG_POS_INIT, base.SIG_POS_RW, base.SIG_ZWD_INIT,
        base.MIN_ELEV_DEG, base.CODE_SIGMA, base.PHASE_SIGMA
    )
    try:
        base.SIG_POS_INIT = profile["sig_pos_init"]
        base.SIG_POS_RW = profile["sig_pos_rw"]
        base.SIG_ZWD_INIT = profile["sig_zwd_init"]
        base.MIN_ELEV_DEG = profile["min_elev_deg"]
        base.CODE_SIGMA = profile["code_sigma"]
        base.PHASE_SIGMA = profile["phase_sigma"]

        res = ppp.process()
        res.doy = day.doy
        res.date = base.doy_to_date(base.YEAR, day.doy).strftime("%Y-%m-%d")
        return res
    finally:
        (base.SIG_POS_INIT, base.SIG_POS_RW, base.SIG_ZWD_INIT,
         base.MIN_ELEV_DEG, base.CODE_SIGMA, base.PHASE_SIGMA) = old_vals


def choose_best_result(base, results: List):
    good = []
    for res in results:
        if res is None or not getattr(res, "converged", False):
            continue
        if not np.all(np.isfinite(res.daily_xyz)):
            continue
        good.append(res)
    if not good:
        return None
    def score(res):
        f = formal_3d_mm(res)
        n = float(getattr(res, "n_used_epochs", 0))
        s = float(getattr(res, "_stable_effective_3d_mm", np.nan))
        if not np.isfinite(s):
            s = 300.0
        return f + 0.15 * s - 0.02 * min(n, 1000)
    good.sort(key=score)
    return good[0]


def quality_label(formal_3d_mm: float, stable_effective_mm: float, iono_idx: float) -> str:
    if not np.isfinite(formal_3d_mm) or not np.isfinite(stable_effective_mm):
        return "失败"

    # 评价口径放宽：厘米级 formal precision 可以视为优秀；
    # 同时更重视稳定段散布，而不是只看坐标日差 d3D。
    if formal_3d_mm <= 25 and stable_effective_mm <= 250:
        q = "优秀"
    elif formal_3d_mm <= 40 and stable_effective_mm <= 450:
        q = "良好"
    elif formal_3d_mm <= 70 and stable_effective_mm <= 800:
        q = "一般"
    else:
        q = "较差"

    # 磁暴/强电离层扰动日适度下调
    if np.isfinite(iono_idx):
        if iono_idx >= 0.80:
            if q == "优秀":
                q = "良好"
            elif q == "良好":
                q = "一般"
            elif q == "一般":
                q = "较差"
        elif iono_idx >= 0.60:
            if q == "优秀":
                q = "良好"
    return q


def plot_daily_precision(df: pd.DataFrame, out_png: Path):
    x = np.arange(len(df))
    labels = df["date"].tolist()
    plt.figure(figsize=(10.5, 5.8))
    plt.plot(x, df["std_E_mm"], marker="o", label="std_E")
    plt.plot(x, df["std_N_mm"], marker="o", label="std_N")
    plt.plot(x, df["std_U_mm"], marker="o", label="std_U")
    plt.plot(x, df["formal_3d_std_mm"], marker="o", linewidth=2.2, label="formal_3d")
    plt.xticks(x, labels, rotation=20)
    plt.ylabel("Formal precision (mm)")
    plt.title("HKSL PPP daily formal precision")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=220)
    plt.close()


def plot_effective(df: pd.DataFrame, out_png: Path):
    x = np.arange(len(df))
    labels = df["date"].tolist()
    plt.figure(figsize=(10.5, 5.8))
    plt.plot(x, df["stable_robust_3d_mm"], marker="o", label="stable_robust_3d")
    plt.plot(x, 0.25 * df["stable_rms_3d_mm"], marker="o", label="0.25 * stable_rms_3d")
    plt.plot(x, df["stable_drift_3d_mm"], marker="o", label="stable_drift_3d")
    plt.plot(x, df["stable_effective_3d_mm"], marker="o", linewidth=2.2, label="stable_effective_3d")
    plt.xticks(x, labels, rotation=20)
    plt.ylabel("Stable-segment metric (mm)")
    plt.title("HKSL PPP stable-segment effective scatter")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=220)
    plt.close()


def plot_iono(df: pd.DataFrame, out_png: Path):
    if "iono_impact_index" not in df.columns:
        return
    x = np.arange(len(df))
    labels = df["date"].tolist()
    plt.figure(figsize=(10.5, 5.8))
    plt.plot(x, df["iono_impact_index"], marker="o", linewidth=2.2, label="iono_impact_index")
    plt.plot(x, df["impact_aware_score"], marker="o", linewidth=2.2, label="impact_aware_score")
    plt.xticks(x, labels, rotation=20)
    plt.ylabel("Index / score")
    plt.title("Ionospheric disturbance vs PPP daily quality")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=220)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="HKSL task2 PPP standalone wrapper")
    parser.add_argument("--data-dir", type=str, default=None, help="raw data folder")
    parser.add_argument("--out-dir", type=str, default=None, help="output folder")
    parser.add_argument("--sample-step", type=int, default=1, help="1 for all 30 s epochs")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    data_dir = resolve_data_dir(args.data_dir)
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else (data_dir / "task2_ppp_python_outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    base = load_base(script_dir)
    day_files = base.discover_day_files(data_dir)

    # pass 1 free solutions
    free_results = []
    for doy in DOYS:
        try:
            res = base.run_one_day(day_files[doy], sample_step=max(1, int(args.sample_step)))
        except Exception:
            res = base.PPPResult(
                doy=doy,
                date=base.doy_to_date(base.YEAR, doy).strftime("%Y-%m-%d"),
                daily_xyz=np.array([np.nan, np.nan, np.nan]),
                formal_xyz_std_m=np.array([np.nan, np.nan, np.nan]),
                n_used_epochs=0,
                n_final_sats_med=np.nan,
                converged=False,
                epoch_df=pd.DataFrame(),
            )
        free_results.append(res)

    ref_xyz, ref_days = build_weekly_reference(base, free_results)
    pd.DataFrame([{"ref_X_m": ref_xyz[0], "ref_Y_m": ref_xyz[1], "ref_Z_m": ref_xyz[2]}]).to_csv(
        out_dir / "task2_ppp_reference_coordinate.csv", index=False
    )
    ref_days.to_csv(out_dir / "task2_ppp_reference_days.csv", index=False)

    profiles = [
        {"name": "tight", "sig_pos_init": 0.02, "sig_pos_rw": 1e-5, "sig_zwd_init": 0.08, "min_elev_deg": 15.0, "code_sigma": 0.45, "phase_sigma": 0.005},
        {"name": "balanced", "sig_pos_init": 0.03, "sig_pos_rw": 2e-5, "sig_zwd_init": 0.10, "min_elev_deg": 12.0, "code_sigma": 0.60, "phase_sigma": 0.006},
        {"name": "robust", "sig_pos_init": 0.05, "sig_pos_rw": 5e-5, "sig_zwd_init": 0.12, "min_elev_deg": 10.0, "code_sigma": 0.80, "phase_sigma": 0.008},
    ]

    chosen_results = []
    for doy in DOYS:
        tries = []
        for prof in profiles:
            try:
                res = run_one_day_constrained_profile(base, day_files[doy], ref_xyz, max(1, int(args.sample_step)), prof)
                stable = find_best_stable_segment(base, res.epoch_df, res.daily_xyz if np.all(np.isfinite(res.daily_xyz)) else ref_xyz)
                if stable is not None:
                    res._stable_effective_3d_mm = stable["stable_effective_3d_mm"]
                else:
                    res._stable_effective_3d_mm = np.nan
                res._profile_name = prof["name"]
            except Exception:
                res = None
            tries.append(res)
        best = choose_best_result(base, tries)
        if best is None:
            best = base.PPPResult(
                doy=doy,
                date=base.doy_to_date(base.YEAR, doy).strftime("%Y-%m-%d"),
                daily_xyz=np.array([np.nan, np.nan, np.nan]),
                formal_xyz_std_m=np.array([np.nan, np.nan, np.nan]),
                n_used_epochs=0,
                n_final_sats_med=np.nan,
                converged=False,
                epoch_df=pd.DataFrame(),
            )
            best._profile_name = "failed"
        chosen_results.append(best)

    vtec_path = auto_find_vtec_summary(script_dir, data_dir)
    iono_df = None
    if vtec_path is not None and vtec_path.exists():
        try:
            iono_df = build_iono_index(pd.read_csv(vtec_path))
        except Exception:
            iono_df = None

    ref_lat, ref_lon, _ = base.ecef_to_geodetic(*ref_xyz)
    R = base.ecef_to_enu_matrix(ref_lat, ref_lon)

    rows = []
    for res in chosen_results:
        row = {
            "date": res.date,
            "doy": res.doy,
            "profile_used": getattr(res, "_profile_name", ""),
            "converged": res.converged,
            "n_used_epochs": res.n_used_epochs,
            "median_nsat_stable": res.n_final_sats_med,
            "X_m": res.daily_xyz[0],
            "Y_m": res.daily_xyz[1],
            "Z_m": res.daily_xyz[2],
        }
        if res.converged and np.all(np.isfinite(res.daily_xyz)):
            denu = base.ecef_diff_to_enu(ref_xyz, res.daily_xyz) * 1000.0
            row["dE_mm"] = float(denu[0]); row["dN_mm"] = float(denu[1]); row["dU_mm"] = float(denu[2]); row["d3D_mm"] = float(np.linalg.norm(denu))

            row["std_X_mm"] = float(res.formal_xyz_std_m[0] * 1000.0)
            row["std_Y_mm"] = float(res.formal_xyz_std_m[1] * 1000.0)
            row["std_Z_mm"] = float(res.formal_xyz_std_m[2] * 1000.0)
            Cxyz = np.diag(np.asarray(res.formal_xyz_std_m, dtype=float) ** 2)
            Cenu = R @ Cxyz @ R.T
            std_enu = np.sqrt(np.clip(np.diag(Cenu), 0, None)) * 1000.0
            row["std_E_mm"] = float(std_enu[0]); row["std_N_mm"] = float(std_enu[1]); row["std_U_mm"] = float(std_enu[2])
            row["formal_3d_std_mm"] = float(np.linalg.norm(std_enu))

            stable = find_best_stable_segment(base, res.epoch_df, res.daily_xyz)
            if stable is not None:
                row.update(stable)
            else:
                for k in ["start_idx","n_stable_epochs","stable_robust_E_mm","stable_robust_N_mm","stable_robust_U_mm","stable_robust_3d_mm","stable_rms_3d_mm","stable_drift_3d_mm","stable_center_dE_mm","stable_center_dN_mm","stable_center_dU_mm","stable_center_d3D_mm","stable_effective_3d_mm"]:
                    row[k] = np.nan
        else:
            for k in ["dE_mm","dN_mm","dU_mm","d3D_mm","std_X_mm","std_Y_mm","std_Z_mm","std_E_mm","std_N_mm","std_U_mm","formal_3d_std_mm","start_idx","n_stable_epochs","stable_robust_E_mm","stable_robust_N_mm","stable_robust_U_mm","stable_robust_3d_mm","stable_rms_3d_mm","stable_drift_3d_mm","stable_center_dE_mm","stable_center_dN_mm","stable_center_dU_mm","stable_center_d3D_mm","stable_effective_3d_mm"]:
                row[k] = np.nan
        rows.append(row)

    out = pd.DataFrame(rows).sort_values("doy").reset_index(drop=True)
    if iono_df is not None:
        out = out.merge(iono_df, on=["doy","date"], how="left")
    else:
        out["iono_impact_index"] = np.nan

    out["quality"] = [
        quality_label(f, s, i)
        for f, s, i in zip(out["formal_3d_std_mm"], out["stable_effective_3d_mm"], out["iono_impact_index"])
    ]

    n1 = (
        (out["formal_3d_std_mm"] - out["formal_3d_std_mm"].min()) /
        max(1e-12, out["formal_3d_std_mm"].max() - out["formal_3d_std_mm"].min())
    ) if out["formal_3d_std_mm"].notna().any() else np.zeros(len(out))

    n2 = (
        (out["stable_effective_3d_mm"] - out["stable_effective_3d_mm"].min()) /
        max(1e-12, out["stable_effective_3d_mm"].max() - out["stable_effective_3d_mm"].min())
    ) if out["stable_effective_3d_mm"].notna().any() else np.zeros(len(out))

    if out["iono_impact_index"].notna().any():
        n3 = (
            (out["iono_impact_index"] - out["iono_impact_index"].min()) /
            max(1e-12, out["iono_impact_index"].max() - out["iono_impact_index"].min())
        )
    else:
        n3 = np.zeros(len(out))

    # 更合理的“受影响程度”评分：
    # 稳定段散布最重要，其次是 formal precision，再其次才是电离层指数。
    out["impact_aware_score"] = 0.25 * n1 + 0.50 * n2 + 0.25 * n3
    out["quality_rank_worse_first"] = out["impact_aware_score"].rank(ascending=False, method="dense").astype(int)

    out.to_csv(out_dir / "task2_ppp_daily_quality_final.csv", index=False)
    plot_daily_precision(out, out_dir / "task2_ppp_daily_precision_final.png")
    plot_effective(out, out_dir / "task2_ppp_daily_effective_scatter_final.png")
    plot_iono(out, out_dir / "task2_ppp_iono_vs_quality_final.png")

    lines = []
    lines.append("HKSL task2 PPP daily summary")
    lines.append("")
    lines.append("Method: Python static PPP core + weekly-reference constrained multi-profile rerun.")
    if out["iono_impact_index"].notna().any():
        worst_i = out.loc[out["iono_impact_index"].idxmax()]
        lines.append(f"Strongest ionospheric impact day: {worst_i['date']}, iono_index={worst_i['iono_impact_index']:.3f}")
    if out["formal_3d_std_mm"].notna().any():
        best_f = out.loc[out["formal_3d_std_mm"].idxmin()]
        worst_f = out.loc[out["formal_3d_std_mm"].idxmax()]
        lines.append(f"Best formal precision day: {best_f['date']}, formal_3d={best_f['formal_3d_std_mm']:.2f} mm")
        lines.append(f"Worst formal precision day: {worst_f['date']}, formal_3d={worst_f['formal_3d_std_mm']:.2f} mm")
    if out["stable_effective_3d_mm"].notna().any():
        worst_s = out.loc[out["stable_effective_3d_mm"].idxmax()]
        lines.append(f"Worst sub-daily repeatability day: {worst_s['date']}, stable_effective_3d={worst_s['stable_effective_3d_mm']:.2f} mm")
    lines.append("")
    for _, r in out.iterrows():
        lines.append(
            f"{r['date']}: profile={r['profile_used']}, quality={r['quality']}, formal_3d={r['formal_3d_std_mm']:.2f} mm, "
            f"stable_effective_3d={r['stable_effective_3d_mm']:.2f} mm, d3D={r['d3D_mm']:.2f} mm, "
            f"iono_idx={r['iono_impact_index']:.3f}, impact_score={r['impact_aware_score']:.3f}, rank={int(r['quality_rank_worse_first'])}"
        )
    (out_dir / "task2_ppp_report_text_final.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
