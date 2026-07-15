import pandas as pd
import os

# =========================
# 1. 路径设置
# =========================
# 把这里改成你自己的数据文件夹路径
data_dir = r"D:\专业课\地理时空信息大数据\data_raw"

trip_file = os.path.join(data_dir, "yellow_tripdata_2025-10.parquet")
lookup_file = os.path.join(data_dir, "taxi_zone_lookup.csv")

output_dir = os.path.join(data_dir, "outputs")
os.makedirs(output_dir, exist_ok=True)

# =========================
# 2. 读取数据
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
    "total_amount"
]

print("正在读取 parquet 数据...")
df = pd.read_parquet(trip_file, columns=use_cols)

print("原始数据量：", len(df))
print(df.head())

# =========================
# 3. 基础清洗
# =========================
# 时间转为 datetime
df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"], errors="coerce")
df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"], errors="coerce")

# 删除关键字段缺失
df = df.dropna(subset=[
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "PULocationID",
    "DOLocationID",
    "trip_distance",
    "total_amount"
])

# 保证 LocationID 为整数
df["PULocationID"] = df["PULocationID"].astype(int)
df["DOLocationID"] = df["DOLocationID"].astype(int)

# 行程时长（分钟）
df["trip_duration_min"] = (
    df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
).dt.total_seconds() / 60

# 剔除明显异常值
df = df[df["trip_duration_min"] > 0]
df = df[df["trip_distance"] > 0]
df = df[df["total_amount"] > 0]

# 进一步剔除极端异常值（可按需要调整）
df = df[df["trip_duration_min"] <= 180]   # 最长 3 小时
df = df[df["trip_distance"] <= 100]       # 最长 100 英里
df = df[df["total_amount"] <= 500]        # 总费用不超过 500 美元

print("清洗后数据量：", len(df))

# =========================
# 4. 构造时间字段
# =========================
df["pickup_date"] = df["tpep_pickup_datetime"].dt.date
df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
df["pickup_weekday"] = df["tpep_pickup_datetime"].dt.dayofweek  # 周一=0, 周日=6
df["pickup_weekday_name"] = df["tpep_pickup_datetime"].dt.day_name()
df["is_weekend"] = df["pickup_weekday"].isin([5, 6]).astype(int)

# =========================
# 5. 读取分区对照表
# =========================
lookup = pd.read_csv(lookup_file)

# 统一列名，防止不同版本字段名有差异
lookup.columns = [c.strip() for c in lookup.columns]

# 常见 lookup 字段一般是：
# LocationID, Borough, Zone, service_zone
print("lookup 字段：", lookup.columns.tolist())

# =========================
# 6. 各分区上车量统计
# =========================
pickup_by_zone = (
    df.groupby("PULocationID")
      .size()
      .reset_index(name="pickup_count")
      .rename(columns={"PULocationID": "LocationID"})
)

pickup_by_zone = pickup_by_zone.merge(lookup, on="LocationID", how="left")
pickup_by_zone = pickup_by_zone.sort_values("pickup_count", ascending=False)

pickup_by_zone.to_csv(
    os.path.join(output_dir, "pickup_by_zone.csv"),
    index=False,
    encoding="utf-8-sig"
)

# =========================
# 7. 各分区下车量统计
# =========================
dropoff_by_zone = (
    df.groupby("DOLocationID")
      .size()
      .reset_index(name="dropoff_count")
      .rename(columns={"DOLocationID": "LocationID"})
)

dropoff_by_zone = dropoff_by_zone.merge(lookup, on="LocationID", how="left")
dropoff_by_zone = dropoff_by_zone.sort_values("dropoff_count", ascending=False)

dropoff_by_zone.to_csv(
    os.path.join(output_dir, "dropoff_by_zone.csv"),
    index=False,
    encoding="utf-8-sig"
)

# =========================
# 8. 24小时订单量统计
# =========================
hourly_orders = (
    df.groupby("pickup_hour")
      .size()
      .reset_index(name="order_count")
      .sort_values("pickup_hour")
)

hourly_orders.to_csv(
    os.path.join(output_dir, "hourly_orders.csv"),
    index=False,
    encoding="utf-8-sig"
)

# =========================
# 9. 星期-小时二维统计
# =========================
weekday_hour_orders = (
    df.groupby(["pickup_weekday", "pickup_weekday_name", "pickup_hour"])
      .size()
      .reset_index(name="order_count")
      .sort_values(["pickup_weekday", "pickup_hour"])
)

weekday_hour_orders.to_csv(
    os.path.join(output_dir, "weekday_hour_orders.csv"),
    index=False,
    encoding="utf-8-sig"
)

# =========================
# 10. OD流向统计（前100）
# =========================
od_table = (
    df.groupby(["PULocationID", "DOLocationID"])
      .size()
      .reset_index(name="flow_count")
      .sort_values("flow_count", ascending=False)
)

# 给起点终点加名称
lookup_from = lookup.rename(columns={
    "LocationID": "PULocationID",
    "Borough": "PU_Borough",
    "Zone": "PU_Zone",
    "service_zone": "PU_service_zone"
})

lookup_to = lookup.rename(columns={
    "LocationID": "DOLocationID",
    "Borough": "DO_Borough",
    "Zone": "DO_Zone",
    "service_zone": "DO_service_zone"
})

od_table = od_table.merge(lookup_from, on="PULocationID", how="left")
od_table = od_table.merge(lookup_to, on="DOLocationID", how="left")

od_top100 = od_table.head(100)

od_top100.to_csv(
    os.path.join(output_dir, "od_top100.csv"),
    index=False,
    encoding="utf-8-sig"
)

# =========================
# 11. 导出一份清洗后的样本，方便检查
# =========================
sample = df.sample(min(5000, len(df)), random_state=42)
sample.to_csv(
    os.path.join(output_dir, "cleaned_tripdata_sample.csv"),
    index=False,
    encoding="utf-8-sig"
)

# =========================
# 12. 控制台输出结果预览
# =========================
print("\n===== 输出完成 =====")
print("输出文件夹：", output_dir)

print("\n上车量 Top 10：")
print(pickup_by_zone.head(10))

print("\n下车量 Top 10：")
print(dropoff_by_zone.head(10))

print("\n24小时订单量：")
print(hourly_orders)

print("\nOD Top 10：")
print(od_top100.head(10))