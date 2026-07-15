# 纽约市出租车时空大数据处理与制图代码包

## 文件说明

- `01_clean_and_aggregate.py`：读取 Parquet 原始订单数据，完成清洗、时间字段构建、分区统计、OD统计。
- `02_time_charts.py`：根据统计表生成 24 小时折线图、工作日—小时多折线图、星期订单量柱状图。
- `03_poi_od_analysis_charts.py`：生成 POI 对比图、OD 高频流向图、相关性矩阵热力图、典型功能区对比图。
- `04_hourly_od_animation.py`：生成按小时变化的 OD 时空演化 GIF 动图。
- `05_arcgis10_2_arcpy_optional.py`：ArcGIS10.2/ArcPy 自动化处理示例，包括空间连接、面积计算、功能区赋值。

## 推荐运行顺序

1. 先运行 `01_clean_and_aggregate.py`，得到基础 CSV 统计表。
2. 再运行 `02_time_charts.py`，生成时间统计图。
3. 完成 ArcGIS 空间连接后，导出 POI 分区统计表，再运行 `03_poi_od_analysis_charts.py`。
4. 如需动图展示，运行 `04_hourly_od_animation.py`。
5. 如使用 ArcGIS10.2 自带 Python，可参考 `05_arcgis10_2_arcpy_optional.py`。

## 注意事项

- 代码中的 `DATA_DIR` 或 `ROOT` 需要改成你自己电脑上的数据路径。
- ArcGIS10.2 自带 Python 版本较旧，建议普通数据处理和图表生成使用独立 Python 3 环境，ArcPy 脚本单独在 ArcGIS Python 中运行。
- 如果 GIF 线条过密，可提高 `MIN_FLOW_TO_DRAW` 的阈值，如从 5 调整到 10。
