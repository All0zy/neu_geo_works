"""
HKCL 七天 PPP 批处理脚本（无界面）

功能:
1. 自动遍历 hkcl 目录中的 HKCL*.26o 观测文件
2. 按日期自动匹配对应 NAV/SP3/CLK/BIA 文件
3. 逐天执行 PPP 处理
4. 输出每日结果 CSV、统计 CSV 和 4 张精度图
"""

from __future__ import annotations

import re
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

import gnss as gn
from gnss import Nav, ecef2pos, epoch2time, timediff
from gnss import rSigRnx
from peph import atxdec, peph, biasdec, searchpcv
from pppssr import pppos
from rinex import rnxdec


def parse_yydoy_from_name(name: str) -> str | None:
    m = re.search(r"_(\d{7})\d{4}_", name)
    if not m:
        return None
    return m.group(1)


def choose_atx_file(obs_start_time, hkcl_dir: Path) -> Path:
    # 根据观测起始时刻选 ATX，避免硬编码日期导致天线模型不匹配。
    if obs_start_time > epoch2time([2022, 11, 27, 0, 0, 0]):
        atx_name = "I20.ATX"
    elif obs_start_time > epoch2time([2021, 5, 2, 0, 0, 0]):
        atx_name = "M20.ATX"
    else:
        atx_name = "M14.ATX"

    atx_path = hkcl_dir / atx_name
    if not atx_path.exists():
        raise FileNotFoundError(f"找不到 ATX 文件: {atx_path}")
    return atx_path


def build_signals(gnss_sys: str = "GEC"):
    sigs = []
    if "G" in gnss_sys:
        sigs.extend([
            rSigRnx("GC1C"), rSigRnx("GC2W"),
            rSigRnx("GL1C"), rSigRnx("GL2W"),
            rSigRnx("GS1C"), rSigRnx("GS2W"),
        ])
    if "E" in gnss_sys:
        sigs.extend([
            rSigRnx("EC1C"), rSigRnx("EC5Q"),
            rSigRnx("EL1C"), rSigRnx("EL5Q"),
            rSigRnx("ES1C"), rSigRnx("ES5Q"),
        ])
    if "C" in gnss_sys:
        sigs.extend([
            rSigRnx("CC2I"), rSigRnx("CC6I"),
            rSigRnx("CL2I"), rSigRnx("CL6I"),
            rSigRnx("CS2I"), rSigRnx("CS6I"),
        ])
    return sigs


def save_daily_plots(day_df: pd.DataFrame, out_dir: Path, base_name: str):
    enu = day_df[["East(m)", "North(m)", "Up(m)"]].values
    smode = day_df["Mode"].values
    t = day_df["Time"].values

    idx0 = np.where(smode == 0)[0]
    idx5 = np.where(smode == 5)[0]
    idx4 = np.where(smode == 4)[0]
    mode_info = [(idx0, "r", "no solution"), (idx5, "y", "float"), (idx4, "g", "fix")]

    # 图1: 位置误差 + ZTD
    fig1 = plt.figure(figsize=(9, 7.5))
    lbl_t = ["East [m]", "North [m]", "Up [m]"]
    for k in range(3):
        ax = plt.subplot(4, 1, k + 1)
        if len(idx0) > 0:
            ax.plot(t[idx0], enu[idx0, k], "r.", label="none")
        if len(idx5) > 0:
            ax.plot(t[idx5], enu[idx5, k], "y.", label="float")
        if len(idx4) > 0:
            ax.plot(t[idx4], enu[idx4, k], "g.", label="fix")
        ax.set_ylabel(lbl_t[k])
        ax.grid(True, alpha=0.3)
        ax.set_ylim([-1.0, 1.0])

    ax = plt.subplot(4, 1, 4)
    ztd = day_df["ZTD(m)"].values
    if len(idx0) > 0:
        ax.plot(t[idx0], ztd[idx0] * 1e2, "r.", markersize=6, label="none")
    if len(idx5) > 0:
        ax.plot(t[idx5], ztd[idx5] * 1e2, "y.", markersize=6, label="float")
    if len(idx4) > 0:
        ax.plot(t[idx4], ztd[idx4] * 1e2, "g.", markersize=6, label="fix")
    ax.set_ylabel("ZTD [cm]")
    ax.set_xlabel("Time [days]")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    plt.tight_layout()
    fig1.savefig(out_dir / f"{base_name}_position_error.png", dpi=250, bbox_inches="tight")
    plt.close(fig1)

    # 图2: 误差分布
    fig2, axes = plt.subplots(1, 3, figsize=(12, 3.8))
    labels = ["East", "North", "Up"]
    for i, label in enumerate(labels):
        valid = ~np.isnan(enu[:, i])
        axes[i].hist(enu[valid, i], bins=50, edgecolor="black", alpha=0.7, color="steelblue")
        axes[i].set_xlabel(f"{label} Error [m]")
        axes[i].set_ylabel("Frequency")
        axes[i].set_title(f"{label} Error Distribution")
        axes[i].grid(True, alpha=0.3)
    plt.tight_layout()
    fig2.savefig(out_dir / f"{base_name}_error_distribution.png", dpi=250, bbox_inches="tight")
    plt.close(fig2)

    # 图3: 3D误差
    fig3 = plt.figure(figsize=(8, 6))
    ax3 = fig3.add_subplot(111, projection="3d")
    for idx, color, label in mode_info:
        if len(idx) > 0:
            ax3.scatter(enu[idx, 0], enu[idx, 1], enu[idx, 2], c=color, alpha=0.6, s=16, label=label)
    ax3.set_xlabel("East [m]")
    ax3.set_ylabel("North [m]")
    ax3.set_zlabel("Up [m]")
    ax3.set_title("3D Position Error")
    ax3.legend(fontsize=8)
    fig3.savefig(out_dir / f"{base_name}_3d_error.png", dpi=250, bbox_inches="tight")
    plt.close(fig3)

    # 图4: 2D误差随时间 + CDF
    fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(12, 4.2))
    h_2d = np.sqrt(enu[:, 0] ** 2 + enu[:, 1] ** 2)
    for idx, color, label in mode_info:
        if len(idx) > 0:
            ax4a.plot(t[idx], h_2d[idx], ".", color=color, label=label, alpha=0.6, markersize=4)
    ax4a.set_ylabel("Horizontal Error 2D [m]")
    ax4a.set_xlabel("Time [days]")
    ax4a.set_title("Positioning Accuracy vs Time")
    ax4a.grid(True, alpha=0.3)
    ax4a.legend(fontsize=8)

    if len(idx4) > 0:
        h_fix = np.sort(h_2d[idx4])
        cdf = np.linspace(0, 100, len(h_fix))
        ax4b.plot(h_fix, cdf, "g-", linewidth=2.0, label="Fixed solution")
        p50 = np.percentile(h_fix, 50)
        p95 = np.percentile(h_fix, 95)
        ax4b.axvline(p50, color="g", linestyle="--", alpha=0.5, label=f"50%: {p50:.3f}m")
        ax4b.axvline(p95, color="r", linestyle="--", alpha=0.5, label=f"95%: {p95:.3f}m")

    ax4b.set_xlabel("Horizontal Error [m]")
    ax4b.set_ylabel("Cumulative Probability [%]")
    ax4b.set_title("CDF of Fixed Accuracy")
    ax4b.grid(True, alpha=0.3)
    ax4b.legend(fontsize=8)
    plt.tight_layout()
    fig4.savefig(out_dir / f"{base_name}_accuracy_analysis.png", dpi=250, bbox_inches="tight")
    plt.close(fig4)


def compute_fix_stats(day_df: pd.DataFrame) -> dict:
    smode = day_df["Mode"].values
    enu = day_df[["East(m)", "North(m)", "Up(m)"]].values
    idx4 = np.where(smode == 4)[0]

    if len(idx4) == 0:
        return {
            "fix_epochs": 0,
            "east_mean": np.nan,
            "east_std": np.nan,
            "east_rms": np.nan,
            "north_mean": np.nan,
            "north_std": np.nan,
            "north_rms": np.nan,
            "up_mean": np.nan,
            "up_std": np.nan,
            "up_rms": np.nan,
            "horizontal_rms": np.nan,
        }

    enu_fix = enu[idx4, :]
    east = enu_fix[:, 0]
    north = enu_fix[:, 1]
    up = enu_fix[:, 2]

    return {
        "fix_epochs": int(len(idx4)),
        "east_mean": float(np.mean(east)),
        "east_std": float(np.std(east)),
        "east_rms": float(np.sqrt(np.mean(east ** 2))),
        "north_mean": float(np.mean(north)),
        "north_std": float(np.std(north)),
        "north_rms": float(np.sqrt(np.mean(north ** 2))),
        "up_mean": float(np.mean(up)),
        "up_std": float(np.std(up)),
        "up_rms": float(np.sqrt(np.mean(up ** 2))),
        "horizontal_rms": float(np.sqrt(np.mean(east ** 2 + north ** 2))),
    }


def decode_obs_safe(rnx: rnxdec, obs_name: str, max_retry: int = 8):
    """安全解码观测历元，遇到异常历元行时尝试跳过并继续。"""
    for k in range(max_retry):
        try:
            return rnx.decode_obs()
        except (ValueError, IndexError) as exc:
            msg = str(exc)
            if "invalid literal for int()" in msg or "string index out of range" in msg:
                print(
                    f"  [警告] {obs_name} 异常历元，已跳过 ({k + 1}/{max_retry}): {msg}",
                    flush=True,
                )
                continue
            raise

    print(f"  [警告] {obs_name} 连续出现异常历元，结束当前文件处理", flush=True)
    return None


def process_single_day(
    obsfile: Path,
    navfile: Path,
    orbfile: Path,
    clkfile: Path,
    bsxfile: Path,
    hkcl_dir: Path,
    out_dir: Path,
    print_every: int = 1,
):
    print(f"\n处理观测文件: {obsfile.name}")

    sigs = build_signals("GEC")

    rnx = rnxdec()
    rnx.setSignals(sigs)

    nav = Nav()
    orb = peph()
    nav.pmode = 0

    nav = rnx.decode_nav(str(navfile), nav)
    nav = orb.parse_sp3(str(orbfile), nav)
    nav = rnx.decode_clk(str(clkfile), nav)

    bsx = biasdec()
    bsx.parse(str(bsxfile))

    if rnx.decode_obsh(str(obsfile)) < 0:
        raise RuntimeError(f"观测文件头解析失败: {obsfile.name}")

    rnx.autoSubstituteSignals()

    atx_path = choose_atx_file(rnx.ts, hkcl_dir)
    atx = atxdec()
    atx.readpcv(str(atx_path))

    ppp = pppos(nav, rnx.pos, str(out_dir / f"{obsfile.stem}.log"))
    nav.ephopt = 4
    nav.armode = 3
    nav.cnr_min = 0.0
    nav.cnr_min_gpy = 0.0
    nav.elmin = np.deg2rad(5.0)
    nav.thresar = 2.0

    nav.sat_ant = atx.pcvs
    nav.rcv_ant = searchpcv(atx.pcvr, rnx.ant, rnx.ts)

    # 可根据真实站坐标调整; 若缺省则沿用原 GUI 的 HKCL 参考值。
    xyz_ref = np.array([-2392740.9396, 5397563.0493, 2404757.8653], dtype=float)
    pos_ref = ecef2pos(xyz_ref)

    obs = decode_obs_safe(rnx, obsfile.name)
    if obs is None or obs.t.time == 0:
        raise RuntimeError(f"观测文件无历元: {obsfile.name}")

    nav.t = obs.t
    t0 = obs.t

    t_list = []
    enu_list = []
    ztd_list = []
    smode_list = []
    h2d_list = []
    mode_name_list = []

    mode_name_map = {
        0: "none",
        4: "fix",
        5: "float",
    }

    ne = 0
    while obs.t.time != 0:
        ppp.process(obs, orb=orb, bsx=bsx)

        t_list.append(timediff(nav.t, t0) / 86400.0)
        sol = nav.xa[0:3] if nav.smode == 4 else nav.x[0:3]
        enu = gn.ecef2enu(pos_ref, sol - xyz_ref)
        enu_list.append(enu)

        ztd = nav.xa[ppp.IT(nav.na)] if nav.smode == 4 else nav.x[ppp.IT(nav.na)]
        ztd_list.append(float(ztd))
        smode_list.append(int(nav.smode))

        h2d = float(np.sqrt(enu[0] ** 2 + enu[1] ** 2))
        h2d_list.append(h2d)
        mode_name = mode_name_map.get(int(nav.smode), f"mode{int(nav.smode)}")
        mode_name_list.append(mode_name)

        ne += 1
        if ne % max(1, print_every) == 0:
            elapsed_sec = int(round(t_list[-1] * 86400.0))
            hh = elapsed_sec // 3600
            mm = (elapsed_sec % 3600) // 60
            ss = elapsed_sec % 60
            epoch_str = f"T+{hh:02d}:{mm:02d}:{ss:02d}"
            print(
                f"  历元 {ne:4d} | {epoch_str} | "
                f"E={enu[0]:8.3f} N={enu[1]:8.3f} U={enu[2]:8.3f} m | "
                f"2D={h2d:7.3f} m | {mode_name}",
                flush=True,
            )

        obs = decode_obs_safe(rnx, obsfile.name)
        if obs is None:
            break

    rnx.fobs.close()
    if nav.fout is not None:
        nav.fout.close()

    enu_arr = np.array(enu_list, dtype=float)
    day_df = pd.DataFrame(
        {
            "Time": np.array(t_list, dtype=float),
            "East(m)": enu_arr[:, 0],
            "North(m)": enu_arr[:, 1],
            "Up(m)": enu_arr[:, 2],
            "ZTD(m)": np.array(ztd_list, dtype=float),
            "Mode": np.array(smode_list, dtype=int),
            "ModeName": np.array(mode_name_list, dtype=object),
            "Horizontal2D(m)": np.array(h2d_list, dtype=float),
        }
    )

    date_tag = parse_yydoy_from_name(obsfile.name)
    base_name = f"HKCL_{date_tag}" if date_tag else obsfile.stem

    csv_path = out_dir / f"{base_name}_ppp_results.csv"
    day_df.to_csv(csv_path, index=False)
    print(f"  已保存: {csv_path.name}")

    save_daily_plots(day_df, out_dir, base_name)
    print("  已保存图像: 4 张")

    stats = compute_fix_stats(day_df)
    stats.update(
        {
            "obs_file": obsfile.name,
            "nav_file": navfile.name,
            "orb_file": orbfile.name,
            "clk_file": clkfile.name,
            "bia_file": bsxfile.name,
            "epoch_count": int(len(day_df)),
        }
    )
    return stats


def run_batch(work_dir: Path):
    hkcl_dir = work_dir / "hkcl"
    out_dir = work_dir / "output" / "hkcl_ppp_batch"
    out_dir.mkdir(parents=True, exist_ok=True)

    obs_files = sorted(hkcl_dir.glob("HKCL*MO.26o"))
    if not obs_files:
        raise FileNotFoundError(f"未找到观测文件: {hkcl_dir}")

    summary_rows = []
    jobs = []

    for obs_file in obs_files:
        yydoy = parse_yydoy_from_name(obs_file.name)
        if yydoy is None:
            print(f"[跳过] 无法解析日期: {obs_file.name}")
            continue

        nav_candidates = sorted(hkcl_dir.glob(f"BRDC*_{yydoy}0000_*_MN.rnx"))
        orb_candidates = sorted(hkcl_dir.glob(f"*_{yydoy}0000_*_ORB.SP3"))
        clk_candidates = sorted(hkcl_dir.glob(f"*_{yydoy}0000_*_CLK.CLK"))
        bia_candidates = sorted(hkcl_dir.glob(f"*_{yydoy}0000_*_OSB.BIA"))

        if not (nav_candidates and orb_candidates and clk_candidates and bia_candidates):
            print(f"[跳过] 配套文件不完整: {obs_file.name}")
            continue

        navfile = nav_candidates[0]
        orbfile = orb_candidates[0]
        clkfile = clk_candidates[0]
        bsxfile = bia_candidates[0]

        jobs.append(
            {
                "obsfile": obs_file,
                "navfile": navfile,
                "orbfile": orbfile,
                "clkfile": clkfile,
                "bsxfile": bsxfile,
            }
        )

    if not jobs:
        print("没有可执行的任务")
        return

    max_workers = min(7, len(jobs))
    print(f"\n并发启动 {max_workers} 个线程处理 {len(jobs)} 组数据...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {}
        for job in jobs:
            fut = executor.submit(
                process_single_day,
                obsfile=job["obsfile"],
                navfile=job["navfile"],
                orbfile=job["orbfile"],
                clkfile=job["clkfile"],
                bsxfile=job["bsxfile"],
                hkcl_dir=hkcl_dir,
                out_dir=out_dir,
            )
            future_map[fut] = job["obsfile"].name

        for fut in as_completed(future_map):
            obs_name = future_map[fut]
            try:
                stats = fut.result()
                summary_rows.append(stats)
                print(f"[完成] {obs_name}")
            except Exception as exc:
                print(f"[失败] {obs_name}: {exc}")
                traceback.print_exc()

    if summary_rows:
        summary_df = pd.DataFrame(summary_rows)
        summary_csv = out_dir / "HKCL_7days_ppp_summary.csv"
        summary_df.to_csv(summary_csv, index=False, encoding="utf-8-sig")
        print(f"\n已保存汇总统计: {summary_csv}")
    else:
        print("\n没有成功处理任何一天数据")


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    run_batch(base_dir)
