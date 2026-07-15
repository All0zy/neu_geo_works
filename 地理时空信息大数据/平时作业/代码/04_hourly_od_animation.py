# -*- coding: utf-8 -*-
"""
04_hourly_od_animation.py
功能：基于完整出租车订单、taxi_zones.shp 和 Taxi Zone Lookup，生成按小时变化的纽约出租车 OD 时空演化 GIF。
运行前安装：pip install pandas pyarrow pyshp shapely pillow numpy

提示：如果全量OD线过密，可将 MIN_FLOW_TO_DRAW 从 1 改成 5 或 10。
"""

import os
import math
import numpy as np
import pandas as pd
import shapefile
from shapely.geometry import shape as shapely_shape
from PIL import Image, ImageDraw, ImageFont

ROOT = r"G:\我的云端硬盘\地理时空信息大数据"
TRIP_FILE = os.path.join(ROOT, "yellow_tripdata_2025-10.parquet")
SHP_FILE = os.path.join(ROOT, "taxi_zones", "taxi_zones.shp")
LOOKUP_FILE = os.path.join(ROOT, "taxi_zone_lookup.csv")
OUT_GIF = os.path.join(ROOT, "纽约市出租车OD时空演化动图_按小时_基于shp.gif")

MIN_FLOW_TO_DRAW = 5
W, H = 1400, 980
FRAME_DURATION_MS = 160

# 读取 shp
sf = shapefile.Reader(SHP_FILE)
shapes = sf.shapes()
geoms = {i + 1: shapely_shape(shp.__geo_interface__) for i, shp in enumerate(shapes)}
centroids = {loc: (geom.centroid.x, geom.centroid.y) for loc, geom in geoms.items()}
all_bounds = np.array([geom.bounds for geom in geoms.values()])
minx, miny = all_bounds[:, 0].min(), all_bounds[:, 1].min()
maxx, maxy = all_bounds[:, 2].max(), all_bounds[:, 3].max()

margin_left, margin_top, margin_right, margin_bottom = 40, 76, 420, 48
scale = min((W - margin_left - margin_right) / (maxx - minx), (H - margin_top - margin_bottom) / (maxy - miny))

def to_px(x, y):
    return margin_left + (x - minx) * scale, H - margin_bottom - (y - miny) * scale

poly_parts = {}
for loc, geom in geoms.items():
    parts = []
    polygons = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    for poly in polygons:
        x, y = poly.exterior.xy
        parts.append([to_px(a, b) for a, b in zip(x, y)])
    poly_parts[loc] = parts

# 字体
font_path = r"C:\Windows\Fonts\msyh.ttc"
def font(size):
    return ImageFont.truetype(font_path, size=size) if os.path.exists(font_path) else ImageFont.load_default()

font_title = font(32)
font_text = font(16)
font_small = font(14)
font_hour = font(38)

# 读取数据并统计
cols = ["tpep_pickup_datetime", "PULocationID", "DOLocationID"]
df = pd.read_parquet(TRIP_FILE, columns=cols)
df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"], errors="coerce")
df = df.dropna(subset=["tpep_pickup_datetime", "PULocationID", "DOLocationID"])
df["PULocationID"] = df["PULocationID"].astype(int)
df["DOLocationID"] = df["DOLocationID"].astype(int)
df = df[df["PULocationID"].between(1, 263) & df["DOLocationID"].between(1, 263)]
df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour

lookup = pd.read_csv(LOOKUP_FILE)
name_map = dict(zip(lookup["LocationID"], lookup["Zone"]))

hourly_total = df.groupby("pickup_hour").size().reindex(range(24), fill_value=0)
hourly_od = df.groupby(["pickup_hour", "PULocationID", "DOLocationID"]).size().reset_index(name="flow_count")
pickup_hour = df.groupby(["pickup_hour", "PULocationID"]).size().reset_index(name="pickup_count")
dropoff_hour = df.groupby(["pickup_hour", "DOLocationID"]).size().reset_index(name="dropoff_count")

max_flow = max(1, hourly_od["flow_count"].max())

def bezier(p0, p1, n=50, curv=0.16):
    x0, y0 = p0; x1, y1 = p1
    mx, my = (x0+x1)/2, (y0+y1)/2
    dx, dy = x1-x0, y1-y0
    d = math.hypot(dx, dy)
    if d == 0:
        return [p0, p1]
    ux, uy = -dy/d, dx/d
    cx, cy = mx + ux*d*curv, my + uy*d*curv
    pts = []
    for i in range(n):
        t = i/(n-1)
        pts.append(((1-t)**2*x0 + 2*(1-t)*t*cx + t**2*x1, (1-t)**2*y0 + 2*(1-t)*t*cy + t**2*y1))
    return pts

def route_width(flow):
    return 1 + 7 * math.sqrt(flow / max_flow)

frames = []
for hour in range(24):
    img = Image.new("RGBA", (W, H), (7, 17, 31, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # 分区底图
    for loc, parts in poly_parts.items():
        for part in parts:
            draw.polygon(part, fill=(16, 34, 54, 255), outline=(55, 86, 110, 165))

    hod = hourly_od[(hourly_od["pickup_hour"] == hour) & (hourly_od["flow_count"] >= MIN_FLOW_TO_DRAW)].copy()
    hod = hod.sort_values("flow_count", ascending=False)

    # 所有OD线
    for _, row in hod.iterrows():
        pu, do, flow = int(row.PULocationID), int(row.DOLocationID), int(row.flow_count)
        c = bezier(to_px(*centroids[pu]), to_px(*centroids[do]))
        w = max(1, int(route_width(flow)))
        alpha = int(35 + 150 * math.sqrt(flow / max_flow))
        draw.line(c, fill=(68, 226, 235, alpha), width=w, joint="curve")

    # 最强OD高亮
    if len(hod):
        top = hod.iloc[0]
        pu, do, flow = int(top.PULocationID), int(top.DOLocationID), int(top.flow_count)
        c = bezier(to_px(*centroids[pu]), to_px(*centroids[do]))
        for part in poly_parts[pu]:
            draw.polygon(part, fill=(42, 175, 255, 92), outline=(150, 220, 255, 240))
        for part in poly_parts[do]:
            draw.polygon(part, fill=(255, 76, 136, 92), outline=(255, 190, 212, 240))
        draw.line(c, fill=(255, 160, 46, 250), width=max(3, int(route_width(flow)) + 2), joint="curve")
        px, py = c[int(len(c) * 0.65)]
        draw.ellipse((px-8, py-8, px+8, py+8), fill=(255, 225, 110, 255))

    draw.text((42, 18), "纽约市出租车OD时空演化动图（按小时）", font=font_title, fill=(255, 255, 255, 255))
    draw.text((W-390, 100), f"{hour:02d}:00–{hour:02d}:59", font=font_hour, fill=(96, 226, 235, 255))
    draw.text((W-390, 155), f"该小时订单量：{int(hourly_total.loc[hour]):,}", font=font_text, fill=(255, 255, 255, 255))
    draw.text((W-390, 185), f"显示OD对：{len(hod):,}", font=font_text, fill=(255, 255, 255, 255))
    frames.append(img.convert("P", palette=Image.ADAPTIVE))

frames[0].save(OUT_GIF, save_all=True, append_images=frames[1:], duration=FRAME_DURATION_MS, loop=0, optimize=False)
print("已输出：", OUT_GIF)
