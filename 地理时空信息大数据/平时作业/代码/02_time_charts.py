# -*- coding: utf-8 -*-
"""
02_time_charts.py
功能：根据 hourly_orders.csv 与 weekday_hour_orders.csv 生成时间分布图。
运行前安装：pip install pandas matplotlib
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK JP", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

DATA_DIR = r"G:\我的云端硬盘\地理时空信息大数据\outputs"
OUT_DIR = os.path.join(DATA_DIR, "figures")
os.makedirs(OUT_DIR, exist_ok=True)

# =========================
# 1. 24小时订单量折线图
# =========================
hourly = pd.read_csv(os.path.join(DATA_DIR, "hourly_orders.csv"))
plt.figure(figsize=(10, 6))
plt.plot(hourly["pickup_hour"], hourly["order_count"], marker="o", linewidth=2)
plt.xticks(range(24))
plt.xlabel("小时")
plt.ylabel("订单量")
plt.title("2025年10月纽约市黄色出租车24小时订单量变化图")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "24小时订单量变化图.png"), dpi=300, bbox_inches="tight")
plt.close()

# =========================
# 2. 工作日-小时多折线图
# =========================
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekday_cn = {
    "Monday": "周一", "Tuesday": "周二", "Wednesday": "周三", "Thursday": "周四",
    "Friday": "周五", "Saturday": "周六", "Sunday": "周日"
}
wh = pd.read_csv(os.path.join(DATA_DIR, "weekday_hour_orders.csv"))
wh["pickup_weekday_name"] = pd.Categorical(wh["pickup_weekday_name"], categories=weekday_order, ordered=True)
pivot = wh.pivot(index="pickup_hour", columns="pickup_weekday_name", values="order_count")

plt.figure(figsize=(11, 7))
for col in pivot.columns:
    plt.plot(pivot.index, pivot[col], marker="o", linewidth=1.8, label=weekday_cn.get(col, col))
plt.xticks(range(24))
plt.xlabel("小时")
plt.ylabel("订单量")
plt.title("2025年10月纽约市黄色出租车工作日—小时订单量变化图")
plt.grid(True, alpha=0.3)
plt.legend(ncol=2)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "工作日小时订单量变化图.png"), dpi=300, bbox_inches="tight")
plt.close()

# =========================
# 3. 星期订单量柱状图
# =========================
weekday_total = (
    wh.groupby(["pickup_weekday", "pickup_weekday_name"], observed=False)["order_count"]
      .sum()
      .reset_index()
      .sort_values("pickup_weekday")
)
weekday_total["weekday_cn"] = weekday_total["pickup_weekday_name"].map(weekday_cn)

plt.figure(figsize=(8, 5))
plt.bar(weekday_total["weekday_cn"], weekday_total["order_count"])
plt.xlabel("星期")
plt.ylabel("订单量")
plt.title("2025年10月纽约市黄色出租车星期订单量对比图")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "星期订单量对比图.png"), dpi=300, bbox_inches="tight")
plt.close()

print("时间图表已输出至：", OUT_DIR)
