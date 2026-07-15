import pandas as pd
import matplotlib.pyplot as plt


def read_satellite_data(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        satellite_data = {}
        for line in lines:
            line = line.strip()
            if line.endswith(':'):
                if satellite_data:
                    data.append(satellite_data)
                satellite = line[:-1]
                satellite_data = {'Satellite': satellite}
            elif line.startswith('平均百分差:'):
                satellite_data['Average Percentage Difference'] = float(line.split(':')[1].strip('%'))
            elif line.startswith('最大百分差:'):
                satellite_data['Maximum Percentage Difference'] = float(line.split(':')[1].strip('%'))
            elif line.startswith('最小百分差:'):
                satellite_data['Minimum Percentage Difference'] = float(line.split(':')[1].strip('%'))
            elif line.startswith('标准差百分差:'):
                satellite_data['Standard Deviation Percentage Difference'] = float(line.split(':')[1].strip('%'))
        if satellite_data:
            data.append(satellite_data)
    df = pd.DataFrame(data)
    return df


def plot_percentage_differences(df):
    satellites = df['Satellite'].tolist()
    average_diff = df['Average Percentage Difference'].tolist()
    max_diff = df['Maximum Percentage Difference'].tolist()
    min_diff = df['Minimum Percentage Difference'].tolist()
    std_dev_diff = df['Standard Deviation Percentage Difference'].tolist()

    bar_width = 0.2
    bar_positions1 = range(len(satellites))
    bar_positions2 = [pos + bar_width for pos in bar_positions1]
    bar_positions3 = [pos + bar_width for pos in bar_positions2]
    bar_positions4 = [pos + bar_width for pos in bar_positions3]

    plt.figure(figsize=(15, 8))
    plt.bar(bar_positions1, average_diff, width=bar_width, label='Average Percentage Difference')
    plt.bar(bar_positions2, max_diff, width=bar_width, label='Maximum Percentage Difference')
    plt.bar(bar_positions3, min_diff, width=bar_width, label='Minimum Percentage Difference')
    plt.bar(bar_positions4, std_dev_diff, width=bar_width, label='Standard Deviation Percentage Difference')

    plt.xlabel('Satellites')
    plt.ylabel('Percentage Difference (%)')
    plt.title('Distribution of Percentage Differences for Satellites')
    plt.xticks([pos + bar_width * 1.5 for pos in bar_positions1], satellites, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    file_path = r'C:\Users\93104\Desktop\误差分析.txt'
    satellite_df = read_satellite_data(file_path)
    plot_percentage_differences(satellite_df)
