import pandas as pd

def save_results_to_excel(position, file_name):
    if position.final_positions:
        data1 = {
            'Observation Time': position.observation_times,
            'X': [pos[0] for pos in position.final_positions],
            'Y': [pos[1] for pos in position.final_positions],
            'Z': [pos[2] for pos in position.final_positions],
        }
        data2 = {
            'Observation Time': position.observation_times,
            'GDOP': position.gdop_values,
            'PDOP': position.pdop_values,
            'HDOP': position.hdop_values,
            'VDOP': position.vdop_values,
            'TDOP': position.tdop_values
        }
        df = pd.DataFrame(data1)
        csv_file_name1 = "./output/xyz.csv"
        df.to_csv(csv_file_name1, index=False)
        df = pd.DataFrame(data2)
        csv_file_name2 = "./output/dop.csv"
        df.to_csv(csv_file_name2, index=False)
    else:
        print("没有有效的定位结果可以保存到 Excel 文件中。")