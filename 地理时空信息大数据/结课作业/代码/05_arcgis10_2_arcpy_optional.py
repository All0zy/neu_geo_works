# -*- coding: utf-8 -*-
"""
05_arcgis10_2_arcpy_optional.py
功能：ArcGIS 10.2 中可选的 ArcPy 自动化示例，包括属性连接、空间连接、面积计算等。
说明：ArcGIS 10.2 使用 Python 2.7 环境，代码语法应在 ArcGIS 自带 Python 中运行。
"""

import arcpy
import os

arcpy.env.overwriteOutput = True
WORKSPACE = r"G:\我的云端硬盘\地理时空信息大数据\arcgis_workspace"
arcpy.env.workspace = WORKSPACE

TAXI_ZONES = os.path.join(WORKSPACE, "taxi_zones.shp")
PICKUP_CSV = os.path.join(WORKSPACE, "pickup_by_zone.csv")
DROPOFF_CSV = os.path.join(WORKSPACE, "dropoff_by_zone.csv")
SUBWAY_POINTS = os.path.join(WORKSPACE, "nyc_subway_station.shp")
FOOD_POINTS = os.path.join(WORKSPACE, "nyc_food_shop.shp")
HOTEL_POINTS = os.path.join(WORKSPACE, "nyc_hotel_tourism.shp")

# 1. 空间连接：统计每个分区内地铁站、餐饮商业、酒店旅游点数量
arcpy.SpatialJoin_analysis(TAXI_ZONES, SUBWAY_POINTS, os.path.join(WORKSPACE, "taxi_zones_subway.shp"),
                           "JOIN_ONE_TO_ONE", "KEEP_ALL", match_option="INTERSECT")
arcpy.SpatialJoin_analysis(TAXI_ZONES, FOOD_POINTS, os.path.join(WORKSPACE, "taxi_zones_food.shp"),
                           "JOIN_ONE_TO_ONE", "KEEP_ALL", match_option="INTERSECT")
arcpy.SpatialJoin_analysis(TAXI_ZONES, HOTEL_POINTS, os.path.join(WORKSPACE, "taxi_zones_hotel.shp"),
                           "JOIN_ONE_TO_ONE", "KEEP_ALL", match_option="INTERSECT")

# 2. 面积字段计算：用于服务密度分析
if "area_km2" not in [f.name for f in arcpy.ListFields(TAXI_ZONES)]:
    arcpy.AddField_management(TAXI_ZONES, "area_km2", "DOUBLE")
arcpy.CalculateField_management(TAXI_ZONES, "area_km2", "!shape.area@SQUAREKILOMETERS!", "PYTHON")

# 3. 典型功能区字段创建
if "fun_type" not in [f.name for f in arcpy.ListFields(TAXI_ZONES)]:
    arcpy.AddField_management(TAXI_ZONES, "fun_type", "TEXT", field_length=30)
arcpy.CalculateField_management(TAXI_ZONES, "fun_type", '"General"', "PYTHON")

# 4. 按 Zone 名称赋值功能区类型
rules = {
    "Transport": ["JFK Airport", "LaGuardia Airport", "Penn Station/Madison Sq West"],
    "Commercial": ["East Village", "West Village", "Clinton East", "East Chelsea"],
    "Tourism": ["Times Sq/Theatre District", "Midtown South", "Financial District North", "Little Italy/NoLiTa"],
    "Mixed": ["Midtown Center", "Midtown East", "Union Sq", "Upper East Side South", "Upper East Side North"],
}

for typ, zones in rules.items():
    where = "zone IN ({})".format(",".join(["'{}'".format(z.replace("'", "''")) for z in zones]))
    arcpy.MakeFeatureLayer_management(TAXI_ZONES, "zone_lyr", where)
    arcpy.CalculateField_management("zone_lyr", "fun_type", '"{}"'.format(typ), "PYTHON")
    arcpy.Delete_management("zone_lyr")

print("ArcGIS空间处理示例完成。专题图符号化建议在 ArcMap 中按 fun_type 或统计字段手动设置。")
