# -*- coding: utf-8 -*-
"""
03_poi_od_analysis_charts.py
功能：根据出租车-POI分区对比表、OD表和功能区对比表生成统计图。
运行前安装：pip install pandas matplotlib openpyxl
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK JP", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

DATA_DIR = r"G:\我的云端硬盘\地理时空信息大数据\outputs"
OUT_DIR = os.path.join(DATA_DIR, "figures")
os.makedirs(OUT_DIR, exist_ok=True)

poi_table = os.path.join(DATA_DIR, "纽约市出租车活动强度与POI类型分区对比表.csv")
od_file = os.path.join(DATA_DIR, "od_top100.csv")
function_file = os.path.join(DATA_DIR, "纽约市典型功能分区出租车活动强度对比表.csv")

# =========================
# 1. 上车量前10分区 POI 对比图
# =========================
df = pd.read_csv(poi_table)
top_pickup = df.sort_values("上车量", ascending=False).head(10).copy()
labels = top_pickup["分区名称"]

plt.figure(figsize=(13, 7))
x = range(len(top_pickup))
plt.bar(x, top_pickup["地铁站数量"], label="地铁站")
plt.bar(x, top_pickup["餐饮商业点数量"], bottom=top_pickup["地铁站数量"], label="餐饮商业")
plt.bar(x, top_pickup["酒店旅游点数量"], bottom=top_pickup["地铁站数量"] + top_pickup["餐饮商业点数量"], label="酒店旅游")
plt.xticks(x, labels, rotation=40, ha="right")
plt.ylabel("POI数量")
plt.title("上车量前10分区与POI数量对比图")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "上车量前10分区_POI对比图.png"), dpi=300, bbox_inches="tight")
plt.close()

# =========================
# 2. 下车量前10分区 POI 对比图
# =========================
top_dropoff = df.sort_values("下车量", ascending=False).head(10).copy()
labels = top_dropoff["分区名称"]
plt.figure(figsize=(13, 7))
x = range(len(top_dropoff))
plt.bar(x, top_dropoff["地铁站数量"], label="地铁站")
plt.bar(x, top_dropoff["餐饮商业点数量"], bottom=top_dropoff["地铁站数量"], label="餐饮商业")
plt.bar(x, top_dropoff["酒店旅游点数量"], bottom=top_dropoff["地铁站数量"] + top_dropoff["餐饮商业点数量"], label="酒店旅游")
plt.xticks(x, labels, rotation=40, ha="right")
plt.ylabel("POI数量")
plt.title("下车量前10分区与POI数量对比图")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "下车量前10分区_POI对比图.png"), dpi=300, bbox_inches="tight")
plt.close()

# =========================
# 3. OD 高频流向前10图
# =========================
od = pd.read_csv(od_file).head(10).copy()
od["OD"] = od["PU_Zone"] + " → " + od["DO_Zone"]
od_sorted = od.sort_values("flow_count", ascending=True)
plt.figure(figsize=(11, 7))
plt.barh(od_sorted["OD"], od_sorted["flow_count"])
plt.xlabel("OD流量")
plt.title("2025年10月纽约市黄色出租车高频OD流向前10位图")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "OD高频流向前10图.png"), dpi=300, bbox_inches="tight")
plt.close()

# =========================
# 4. 相关性矩阵热力图与相关系数对比图
# =========================
cols = ["上车量", "下车量", "地铁站数量", "餐饮商业点数量", "酒店旅游点数量", "POI总量"]
corr = df[cols].corr(method="pearson")
plt.figure(figsize=(8, 7))
plt.imshow(corr.values, aspect="auto")
plt.xticks(range(len(cols)), cols, rotation=45, ha="right")
plt.yticks(range(len(cols)), cols)
plt.colorbar(label="Pearson相关系数")
plt.title("出租车活动强度与POI类型相关性矩阵热力图")
for i in range(len(cols)):
    for j in range(len(cols)):
        plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "出租车_POI相关性矩阵热力图.png"), dpi=300, bbox_inches="tight")
plt.close()

corr_compare = pd.DataFrame({
    "POI类型": ["地铁站", "餐饮商业", "酒店旅游"],
    "与上车量相关系数": [corr.loc["上车量", "地铁站数量"], corr.loc["上车量", "餐饮商业点数量"], corr.loc["上车量", "酒店旅游点数量"]],
    "与下车量相关系数": [corr.loc["下车量", "地铁站数量"], corr.loc["下车量", "餐饮商业点数量"], corr.loc["下车量", "酒店旅游点数量"]],
})
plt.figure(figsize=(8, 5))
x = range(len(corr_compare))
width = 0.35
plt.bar([i - width/2 for i in x], corr_compare["与上车量相关系数"], width=width, label="上车量")
plt.bar([i + width/2 for i in x], corr_compare["与下车量相关系数"], width=width, label="下车量")
plt.xticks(x, corr_compare["POI类型"])
plt.ylabel("Pearson相关系数")
plt.title("POI类型与出租车上车量/下车量相关系数对比图")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "出租车_POI相关系数对比柱状图.png"), dpi=300, bbox_inches="tight")
plt.close()

# =========================
# 5. 典型功能区对比图
# =========================
if os.path.exists(function_file):
    func = pd.read_csv(function_file)
    summary = func.groupby("功能区类型", as_index=False).agg(
        平均上车量=("上车量", "mean"),
        平均下车量=("下车量", "mean"),
        平均活动总量=("出租车活动总量", "mean"),
    )
    plt.figure(figsize=(9, 6))
    x = range(len(summary))
    plt.bar([i - 0.18 for i in x], summary["平均上车量"], width=0.36, label="平均上车量")
    plt.bar([i + 0.18 for i in x], summary["平均下车量"], width=0.36, label="平均下车量")
    plt.xticks(x, summary["功能区类型"])
    plt.ylabel("订单量")
    plt.title("不同典型功能区平均出租车活动强度对比图")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "功能类型平均出租车活动强度对比图.png"), dpi=300, bbox_inches="tight")
    plt.close()

print("统计图表已输出至：", OUT_DIR)
