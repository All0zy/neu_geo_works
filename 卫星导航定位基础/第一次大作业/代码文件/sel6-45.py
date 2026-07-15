# 定义输入文件路径
input_file_path = '北斗卫星位置.txt'
# 定义输出文件路径
output_file_path = '北斗卫星位置_C06-C45.txt'

# 打开输入文件和输出文件
with open(input_file_path, 'r', encoding='utf-8') as input_file, \
        open(output_file_path, 'w', encoding='utf-8') as output_file:
    # 遍历输入文件的每一行
    for line in input_file:
        # 去除行首尾的空白字符
        line = line.strip()
        # 遍历 C06 到 C45 的卫星编号
        for i in range(6, 46):
            satellite_id = f'C{i:02d}'
            # 如果行以当前卫星编号开头
            if line.startswith(satellite_id):
                # 按逗号分割行数据
                parts = line.split(',')
                # 提取卫星编号
                new_parts = [parts[0]]
                # 遍历剩余的数据部分
                for part in parts[1:]:
                    try:
                        # 将数据转换为浮点数并除以 1000
                        new_value = float(part) / 1000
                        # 将结果添加到新的数据部分列表
                        new_parts.append(str(new_value))
                    except ValueError:
                        # 如果转换失败，保持原始数据
                        new_parts.append(part)
                # 用逗号重新连接新的数据部分
                new_line = ','.join(new_parts)
                # 将新行写入输出文件
                output_file.write(new_line + '\n')
                break