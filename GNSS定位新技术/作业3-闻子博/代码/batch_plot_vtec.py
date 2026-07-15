""" batch_plot_vtec.py """

""" os """
import os

""" sys """
import sys

""" json """
import json

""" math """
import math

""" random """
import random

""" numpy """
import numpy as np

""" pandas for excel export """
import pandas as pd

""" pyecharts """
from pyecharts import options as opts
from pyecharts.charts import Scatter, MapGlobe
from pyecharts.globals import ChartType, SymbolType

""" datatime """
from datetime import datetime, timedelta

""" random_color """


def random_color(limit):
    """ get random color """
    r = random.randint(0, limit)
    g = random.randint(0, limit)
    b = random.randint(0, limit)
    return (r, g, b)


""" plot tec """


def ptec(inputpath: str, year: str, doy: str, output_files_dir: str = None) -> None:
    filename = os.path.basename(inputpath).split(".")[0]
    method_name = os.path.basename(inputpath).split(".")[1]

    """ load tec_json """
    with open(inputpath, "r") as file:
        tec_json = file.read()
        tec_dict = json.loads(tec_json)

    """ figure for tec-scatter """
    figure_scatter = Scatter(init_opts=opts.InitOpts(width="1300px", height="650px", page_title=f"{filename}.vtec"))

    max_tec = 0.0  # max of tec

    start_time = datetime.strptime("0", "%H")

    le = 0

    # 创建Excel导出数据结构
    excel_data = {}

    for prn in tec_dict.keys():
        xnzero = []
        ynzero = []

        le = len(tec_dict[prn])  # epoch count

        time_label_list = []  # time labels

        for e in range(le):
            time = start_time + timedelta(seconds=e * 30)
            """ 6 hour create a datetime label """
            if time.hour % 6 == 0 and time.minute == 0 and time.second == 0:
                time_label_list.append(time.strftime("%H"))
            else:
                time_label_list.append("")

            if math.fabs(tec_dict[prn][e]) < 1.0e-6:
                continue
            else:
                xnzero.append(e)
                ynzero.append(tec_dict[prn][e])
        """ end of epochs """

        if len(ynzero) > 0 and max(ynzero) > max_tec: max_tec = max(ynzero)  # get max of tec

        tec_data = np.where(np.abs(tec_dict[prn]) < 1.0e-6, np.nan, tec_dict[prn])  # nan replace zero value

        mycolor = random_color(255)

        figure_scatter.add_xaxis(xaxis_data=range(le))
        figure_scatter.add_yaxis(series_name=prn,
                                 y_axis=tec_data,  # data
                                 color=f"rgb{mycolor}",
                                 symbol_size=2,  # scatter size
                                 label_opts=opts.LabelOpts(is_show=False),  # do not show y label
                                 )
    """ end of satellites """

    figure_scatter.set_global_opts(
        xaxis_opts=opts.AxisOpts(name="Epoch",
                                 name_gap=40,  # distance bwtween title and axis
                                 name_location="middle",
                                 name_textstyle_opts=opts.TextStyleOpts(font_family="Time New Roman", font_size=22),
                                 min_=0,
                                 max_=le,
                                 interval=720,  # 7 hour create x label
                                 type_="value",
                                 axislabel_opts=opts.LabelOpts(font_size=20, font_family='Times New Roman')),
        yaxis_opts=opts.AxisOpts(name="VTEC[TECU]",
                                 name_gap=40,
                                 name_location="middle",
                                 name_textstyle_opts=opts.TextStyleOpts(font_family="Time New Roman", font_size=22),
                                 type_="value",
                                 min_=0,
                                 max_=5 * math.floor((max_tec + 20) / 5),
                                 interval=5.0,
                                 axislabel_opts=opts.LabelOpts(font_size=20, font_family='Times New Roman',
                                                               is_show=True)),
        legend_opts=opts.LegendOpts(is_show=True,
                                    type_="scroll",
                                    pos_right="right",
                                    orient="vertical"),
        toolbox_opts=opts.ToolboxOpts(is_show=True,
                                      pos_left="center"),
    )

    # 创建Excel导出数据
    # 先创建时间和历元列
    time_points = [start_time + timedelta(seconds=e * 30) for e in range(le)]
    excel_data['Time'] = [t.strftime('%H:%M:%S') for t in time_points]
    excel_data['Epoch'] = list(range(le))

    # 添加每个卫星的TEC数据
    for prn in tec_dict.keys():
        excel_data[prn] = tec_dict[prn]

    # 创建DataFrame
    df = pd.DataFrame(excel_data)

    # 设置输出路径并确保目录存在
    if output_files_dir is None:
        output_dir = f"./plot/{year}{doy}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        html_path = f"{output_dir}/{filename.lower()}.{method_name}.vtec.html"
        excel_path = f"{output_dir}/{filename.lower()}.{method_name}.vtec.xlsx"
    else:
        if not os.path.exists(output_files_dir):
            os.makedirs(output_files_dir)
        html_path = f"{output_files_dir}/{filename.lower()}.{method_name}.vtec.html"
        excel_path = f"{output_files_dir}/{filename.lower()}.{method_name}.vtec.xlsx"

    # 导出Excel
    df.to_excel(excel_path, index=False)
    print(f"数据已导出至Excel: {excel_path}")

    # 渲染HTML
    figure_scatter.render(html_path)
    print(f"图表已保存为HTML: {html_path}")


def BATCH_PLOT(input_files_dir: str, year: str, doy: str):
    output_files_dir = f"{input_files_dir}/plot"
    if not os.path.exists(output_files_dir): os.mkdir(output_files_dir)
    files = os.listdir(input_files_dir)
    for file in files:
        file_path = os.path.join(input_files_dir, file)
        if not os.path.isfile(file_path): continue
        if len(file.split(".")) < 4: continue

        suffix = file.split(".")[-1]
        classs = file.split(".")[-2]
        method = file.split(".")[-3]
        marker = file.split(".")[-4]

        if suffix == "json" and classs == "vtec":
            print(f"处理文件: {file}")
            ptec(file_path, year, doy, output_files_dir)
    """ end all files """
    print(f"所有文件处理完成，结果保存在: {output_files_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python batch_plot_tec.py <input_files_dir=/TestData/2017244/output> <Year> <Doy>")
        sys.exit(1)

    input_files_dir = sys.argv[1]
    year = sys.argv[2]
    doy = sys.argv[3]

    print(f"开始处理目录: {input_files_dir}")
    print(f"年份: {year}, 年日: {doy}")

    BATCH_PLOT(input_files_dir, year, doy)
