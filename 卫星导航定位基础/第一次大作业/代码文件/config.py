def calculate_column_average(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                values = list(map(float, line.split(',')[1:]))
                data.append(values)

    num_columns = len(data[0])
    column_sums = [0] * num_columns
    for row in data:
        for i in range(num_columns):
            column_sums[i] += abs(row[i])

    column_averages = [sum_value / len(data) for sum_value in column_sums]

    return column_averages


def write_to_config(averages, output_path):
    with open(output_path, 'w') as file:
        headers = ["x坐标差值平均值", "y坐标差值平均值", "z坐标差值平均值",
                   "x坐标百分差平均值", "y坐标百分差平均值", "z坐标百分差平均值"]
        for header, average in zip(headers, averages):
            file.write(f"{header}: {average}\n")


if __name__ == "__main__":
    input_file = "ana.txt"
    output_file = "config.txt"
    averages = calculate_column_average(input_file)
    write_to_config(averages, output_file)