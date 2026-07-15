# 定义文件路径
file_path = 'WUM0MGXRAP_20250550000_01D_05M_ORB.SP3'
# 用于存储筛选后的数据
filtered_data = []
# 标记是否处于有效的时间行之后
in_valid_time_section = False

# 打开文件并逐行读取
with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        # 检查是否为时间行
        if line.startswith('*'):
            # 解析时间信息
            parts = line.split()
            if len(parts) >= 7 and parts[1] == '2025' and parts[2] == '2' and parts[3] == '24' and parts[5] == '0':
                # 标记为处于有效时间行之后
                in_valid_time_section = True
            else:
                in_valid_time_section = False
        # 检查是否为 PC 开头的卫星数据，并且处于有效时间行之后
        elif line.startswith('PC') and in_valid_time_section:
            # 删除最后一列数据
            parts = line.strip().split()[:-1]
            # 去掉首字母 P
            if parts[0].startswith('P'):
                parts[0] = parts[0][1:]
            # 使用逗号分隔各列
            new_line = ','.join(parts)
            # 将符合条件的数据添加到筛选结果中
            filtered_data.append(new_line)

# 仅对第一列进行增序排列
filtered_data.sort(key=lambda x: x.split(',')[0])

# 你也可以将筛选后的数据保存到新文件中
output_file_path = 'sp3_data.txt'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    for data in filtered_data:
        output_file.write(data + '\n')