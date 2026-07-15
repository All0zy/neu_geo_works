# -*- coding: utf-8 -*-
"""
01_clean_and_aggregate.py
功能：读取纽约市黄色出租车 Parquet 原始订单数据，完成字段筛选、异常值清洗、
时间字段构建、分区上车/下车统计、小时统计、星期-小时统计和 OD 流向统计。

运行前安装：
pip install pandas pyarrow
"""

import os
import pandas as pd

# =========================
# 1. 路径设置
# =========================
DATA_DIR = r"G:\我的云端硬盘\地理时空信息大数据"
TRIP_FILE = os.path.join(DATA_DIR, "yellow_tripdata_2025-10.parquet")
LOOKUP_FILE = os.path.join(DATA_DIR, "taxi_zone_lookup.csv")
OUT_DIR = os.path.join(DATA_DIR, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

# =========================
# 2. 读取必要字段
# =========================
use_cols = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "PULocationID",
    "DOLocationID",
    "trip_distance",
    "passenger_count",
    "payment_type",
    "fare_amount",
    "tip_amount",
    "total_amount",
]

print("正在读取 Parquet 数据...")
df = pd.read_parquet(TRIP_FILE, columns=use_cols)
print(f"原始订单数：{len(df):,}")

# =========================
# 3. 数据清洗
# =========================
df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"], errors="coerce")
df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"], errors="coerce")

df = df.dropna(subset=[
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "PULocationID",
    "DOLocationID",
    "trip_distance",
    "total_amount",
])

df["PULocationID"] = df["PULocationID"].astype(int)
df["DOLocationID"] = df["DOLocationID"].astype(int)

df["trip_duration_min"] = (
    df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
).dt.total_seconds() / 60

# 基础异常值剔除
rules = (
    (df["trip_duration_min"] > 0) &
    (df["trip_distance"] > 0) &
    (df["total_amount"] > 0) &
    (df["trip_duration_min"] <= 180) &
    (df["trip_distance"] <= 100) &
    (df["total_amount"] <= 500) &
    (df["PULocationID"].between(1, 263)) &
    (df["DOLocationID"].between(1, 263))
)
df = df.loc[rules].copy()
print(f"清洗后有效订单数：{len(df):,}")

# =========================
# 4. 构造时间字段
# =========================
df["pickup_date"] = df["tpep_pickup_datetime"].dt.date
df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
df["pickup_weekday"] = df["tpep_pickup_datetime"].dt.dayofweek  # Monday=0
weekday_map = {
    0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
    4: "Friday", 5: "Saturday", 6: "Sunday"
}
df["pickup_weekday_name"] = df["pickup_weekday"].map(weekday_map)
df["is_weekend"] = df["pickup_weekday"].isin([5, 6]).astype(int)

# =========================
# 5. 读取 Taxi Zone Lookup
# =========================
lookup = pd.read_csv(LOOKUP_FILE)
lookup.columns = [c.strip() for c in lookup.columns]

# =========================
# 6. 分区上车量统计
# =========================
pickup_by_zone = (
    df.groupby("PULocationID")
      .size()
      .reset_index(name="pickup_count")
      .rename(columns={"PULocationID": "LocationID"})
      .merge(lookup, on="LocationID", how="left")
      .sort_values("pickup_count", ascending=False)
)
pickup_by_zone.to_csv(os.path.join(OUT_DIR, "pickup_by_zone.csv"), index=False, encoding="utf-8-sig")

# =========================
# 7. 分区下车量统计
# =========================
dropoff_by_zone = (
    df.groupby("DOLocationID")
      .size()
      .reset_index(name="dropoff_count")
      .rename(columns={"DOLocationID": "LocationID"})
      .merge(lookup, on="LocationID", how="left")
      .sort_values("dropoff_count", ascending=False)
)
dropoff_by_zone.to_csv(os.path.join(OUT_DIR, "dropoff_by_zone.csv"), index=False, encoding="utf-8-sig")

# =========================
# 8. 24小时订单量统计
# =========================
hourly_orders = (
    df.groupby("pickup_hour")
      .size()
      .reset_index(name="order_count")
      .sort_values("pickup_hour")
)
hourly_orders.to_csv(os.path.join(OUT_DIR, "hourly_orders.csv"), index=False, encoding="utf-8-sig")

# =========================
# 9. 星期-小时二维统计
# =========================
weekday_hour_orders = (
    df.groupby(["pickup_weekday", "pickup_weekday_name", "pickup_hour"])
      .size()
      .reset_index(name="order_count")
      .sort_values(["pickup_weekday", "pickup_hour"])
)
weekday_hour_orders.to_csv(os.path.join(OUT_DIR, "weekday_hour_orders.csv"), index=False, encoding="utf-8-sig")

# =========================
# 10. OD流向统计
# =========================
od_table = (
    df.groupby(["PULocationID", "DOLocationID"])
      .size()
      .reset_index(name="flow_count")
      .sort_values("flow_count", ascending=False)
)

lookup_from = lookup.rename(columns={
    "LocationID": "PULocationID",
    "Borough": "PU_Borough",
    "Zone": "PU_Zone",
    "service_zone": "PU_service_zone",
})
lookup_to = lookup.rename(columns={
    "LocationID": "DOLocationID",
    "Borough": "DO_Borough",
    "Zone": "DO_Zone",
    "service_zone": "DO_service_zone",
})

od_table = od_table.merge(lookup_from, on="PULocationID", how="left")
od_table = od_table.merge(lookup_to, on="DOLocationID", how="left")
od_table.to_csv(os.path.join(OUT_DIR, "od_full.csv"), index=False, encoding="utf-8-sig")
od_table.head(100).to_csv(os.path.join(OUT_DIR, "od_top100.csv"), index=False, encoding="utf-8-sig")

# 样本导出，便于检查和小时级动画快速调试
sample = df.sample(min(5000, len(df)), random_state=42)
sample.to_csv(os.path.join(OUT_DIR, "cleaned_tripdata_sample.csv"), index=False, encoding="utf-8-sig")

print("统计完成，输出目录：", OUT_DIR)
