# 读取文件内容
def read_file(file_path):
    data = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            satellite = parts[0]
            if satellite not in data:
                data[satellite] = []
            data[satellite].append([float(part) for part in parts[1:]])
    return data


# 计算差值和百分差
def calculate_differences(data1, data2):
    differences = []
    percentage_differences = []
    for satellite in data1:
        if satellite in data2:
            for i in range(len(data1[satellite])):
                diff = [(data1[satellite][i][j] - data2[satellite][i][j]) * 1000 for j in range(3)]
                pct_diff = [(data1[satellite][i][j] - data2[satellite][i][j]) / data2[satellite][i][j] * 100 if
                            data2[satellite][i][j] != 0 else 0 for j in range(3)]
                diff = [round(abs(d), 7) for d in diff]  # 取绝对值
                pct_diff = [round(abs(p), 7) for p in pct_diff]  # 取绝对值
                differences.append([satellite] + diff)
                percentage_differences.append([satellite] + pct_diff)
    return differences, percentage_differences

# 将百分差转换为科学计数法并保留7位有效数字
def to_scientific_notation(data):
    new_data = []
    for row in data:
        satellite = row[0]
        values = [format(float(num), '.7e') for num in row[1:]]  # 转换全部百分差数据
        new_data.append([satellite] + values)
    return new_data


# 写入新文件
def write_to_file(differences, percentage_differences, output_path):
    with open(output_path, 'w') as file:
        for i in range(len(differences)):
            diff_str = ','.join([str(d) for d in differences[i]])
            pct_diff = to_scientific_notation([percentage_differences[i]])[0]
            pct_diff_str = ','.join(pct_diff[1:])  # 去掉卫星编号
            file.write(f"{diff_str},{pct_diff_str}\n")


if __name__ == "__main__":
    file1_path = '北斗卫星位置_C06-C45.txt'
    file2_path = 'sp3_data.txt'
    output_path = 'ana.txt'

    data1 = read_file(file1_path)
    data2 = read_file(file2_path)

    differences, percentage_differences = calculate_differences(data1, data2)
    write_to_file(differences, percentage_differences, output_path)