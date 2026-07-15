import pandas as pd
import plotly.graph_objects as go

# 读取数据
data = pd.read_csv('北斗卫星位置.txt', header=None, names=['卫星名称', 'x', 'y', 'z'])

# 建立卫星编号与类型的映射关系
def get_satellite_type(satellite):
    if satellite in ['C01', 'C02', 'C03', 'C04', 'C05', 'C59', 'C60', 'C61']:
        return 'GEO'
    elif satellite in ['C06', 'C07', 'C08', 'C09', 'C10', 'C13', 'C16', 'C31', 'C38', 'C39', 'C40']:
        return 'IGSO'
    else:
        return 'MEO'

data['卫星类型'] = data['卫星名称'].apply(get_satellite_type)

# 创建平面散点图
fig = go.Figure()

# 存储所有卫星轨迹的可见性状态，初始都为True
all_visible = []
# 定义不同类型卫星的颜色
type_colors = {'GEO': 'red', 'IGSO': 'orange', 'MEO': 'blue'}

# 存储每个卫星的可见性状态，初始全为 True
visibility_states = []
for satellite, group in data.groupby('卫星名称'):
    satellite_type = get_satellite_type(satellite)
    fig.add_trace(go.Scatter(
        x=group['x'],
        y=group['y'],
        mode='markers',
        name=satellite,
        marker=dict(
            size=5,
            opacity=0.8,
            color=type_colors[satellite_type]
        ),
    ))
    visibility_states.append(True)

# 生成每个卫星单独显示时的可见性列表
buttons = []

# 添加全部显示按钮
buttons.append({
    'label': '全部显示',
    'method': 'update',
    'args': [{'visible': visibility_states},
             {'title': '卫星平面散点图'}]
})

# 按卫星类型添加显示按钮
satellite_types = data['卫星类型'].unique()
for sat_type in satellite_types:
    visibility = [get_satellite_type(fig.data[i].name) == sat_type for i in range(len(fig.data))]
    buttons.append({
        'label': sat_type,
        'method': 'update',
        'args': [{'visible': visibility},
                 {'title': f'{sat_type} 卫星轨迹'}]
    })

for i in range(len(fig.data)):
    new_visibility = [False] * len(fig.data)
    new_visibility[i] = True
    buttons.append({
        'label': fig.data[i].name,
        'method': 'update',
        'args': [{'visible': new_visibility},
                 {'title': f'{fig.data[i].name} 卫星轨迹'}]
    })

# 更新布局，添加下拉菜单
fig.update_layout(
    title='卫星平面散点图',
    xaxis_title='x坐标',
    yaxis_title='y坐标',
    plot_bgcolor='white',
    paper_bgcolor='white',
    updatemenus=[{
        'buttons': buttons,
        'direction': 'down',
        'showactive': True,
        'x': 1.1,
        'xanchor': 'left',
        'y': 1.05,
        'yanchor': 'top'
    }]
)

fig.show()
    