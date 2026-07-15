from ReadFile import ReadFile
from Position import Position
from Plot import visualize_dop_metrics, visualize_3d_position, visualize_residuals
from Result import save_results_to_excel

def main():
    file_pairs = [["./input/opmt0550.25o",
         "./input/brdc0550.25n"]]# 可以加入多个文件

    for file_pair in file_pairs:
        readfile = ReadFile(file_pair)
        readfile.CaculateSatelites()
        position = Position(readfile.SateliteObservation, readfile.PosName, readfile.Time,
                            readfile.SateliteClockCorrect)
        position.MatchObservationAndCaculate()
        file_name = file_pair[0].split('//')[-1].split('.')[0]
        save_results_to_excel(position, file_name)
        if position.final_positions:
            visualize_3d_position(position)
            visualize_dop_metrics(position)
            visualize_residuals(position)
        else:
            print("No valid positioning results to visualize.")


if __name__ == "__main__":
    main()
