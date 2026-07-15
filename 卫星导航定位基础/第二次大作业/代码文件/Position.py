import datetime
import numpy as np
from HatchFilter import HatchFilter
from ReadFile import ReadFile
from Satelite import Satelite


class Position:
    def __init__(self, SateliteObservation, SateliteName, Time, SateliteClockCorrect):
        self.SateliteObservation = SateliteObservation
        self.SateliteName = SateliteName
        self.Time = Time
        self.SateliteClockCorrect = SateliteClockCorrect
        self.Lines = ReadFile.OLines
        self.OHeaderLastLine = ReadFile.OHeaderLastLine
        self.ApproxPos = ReadFile.ApproxPos
        self.hatchfilter = HatchFilter(0.5)
        self.sat_filters = {}
        self.final_positions = []
        self.gdop_values = []
        self.pdop_values = []
        self.hdop_values = []
        self.vdop_values = []
        self.tdop_values = []
        self.observation_times = []

    def GenerateObs(self):
        return 0

    def MatchObservationAndCaculate(self):
        line = self.Lines[self.OHeaderLastLine]
        NReadLine = self.OHeaderLastLine
        line_count = len(self.Lines)
        while NReadLine < line_count and line:
            obs_time = [None] * 6
            obs_time[0] = int((line[1:3]).strip()) + 2000
            obs_time[1] = int((line[4:6]).strip())
            obs_time[2] = int((line[7:9]).strip())
            obs_time[3] = int((line[10:12]).strip())
            obs_time[4] = int((line[13:15]).strip())
            obs_time[5] = int((line[17:18]).strip())
            num_sat = int(line[30:32])
            if (num_sat % 12 == 0):
                n = int(num_sat / 12)
            else:
                n = int((num_sat / 12)) + 1
            sat_str = ''
            for j in range(n):
                if NReadLine + j < line_count:
                    sat_str = sat_str + self.Lines[NReadLine + j][32:68].strip()
            obs_sat_PRN = []
            for k in range(num_sat):
                obs_sat_PRN.append(sat_str[k * 3:k * 3 + 3])
            NReadLine = NReadLine + n
            ObsPseudorange = []
            for j in range(NReadLine, NReadLine + 2 * num_sat, 2):
                if j < line_count:
                    line = self.Lines[j]
                    if (line[34:46].strip() == ""):
                        Pseudorange = 0
                    else:
                        Pseudorange = float(line[34:46])
                    ObsPseudorange.append(Pseudorange)
            ObsCarrier = []
            for j in range(NReadLine, NReadLine + 2 * num_sat, 2):
                if j < line_count:
                    line = self.Lines[j]
                    if (line[46:58].strip() == ""):
                        Carrier = 0
                    else:
                        Carrier = float(line[50:63])
                    ObsCarrier.append(Carrier)
            SmoothPseudorange = []
            for j in range(num_sat):
                prn = obs_sat_PRN[j]
                carrier = ObsCarrier[j]
                pseudorange = ObsPseudorange[j]
                if prn not in self.sat_filters:
                    self.sat_filters[prn] = HatchFilter(0.5)
                filter_instance = self.sat_filters[prn]
                smoothed = filter_instance.filter(carrier, pseudorange)
                SmoothPseudorange.append(smoothed)
            SatLiteXYZ = self.MatchToSatlite(obs_time, obs_sat_PRN)
            a = self.SolutionLeastSquares(SmoothPseudorange, SatLiteXYZ, ReadFile.ApproxPos, obs_time)
            NReadLine = NReadLine + 2 * num_sat
            if NReadLine < line_count:
                line = self.Lines[NReadLine]
            else:
                break

    def MatchToSatlite(self, ObsTime, ObsSatPrn):
        SatLiteXYZ = []
        for index, SatPRN in enumerate(ObsSatPrn):
            TemXYZ = [None] * 5
            TimeDiff = []
            for index1, SatPRN1 in enumerate(self.SateliteName):
                if (SatPRN == SatPRN1):
                    TimeDiff.append(self.CaculateTimeDifference(ObsTime, self.Time[index1]))
                else:
                    TimeDiff.append(2592000)
            NotMatch = all(x == 2592000 for x in TimeDiff)
            if (NotMatch == True):
                TemXYZ[0] = 0
                TemXYZ[1] = 0
                TemXYZ[2] = 0
                TemXYZ[3] = 0
                TemXYZ[4] = 0
            else:
                MinTime = min(TimeDiff)
                MinTimeindex = TimeDiff.index(MinTime)
                satelite = Satelite(self.SateliteName[MinTimeindex], self.Time[MinTimeindex],
                                    self.SateliteClockCorrect[MinTimeindex], self.SateliteObservation[MinTimeindex])
                satelite.InitPositionOfSat(ObsTime)
                TemXYZ[0] = satelite.X
                TemXYZ[1] = satelite.Y
                TemXYZ[2] = satelite.Z
                TemXYZ[3] = 1
                TemXYZ[4] = satelite.Delta_T
            SatLiteXYZ.append(TemXYZ)
        return SatLiteXYZ

    def CaculateTimeDifference(self, Time1, Time2):
        sec1 = int(Time1[5]) if isinstance(Time1[5], int) else Time1[5]
        sec2 = int(Time2[5]) if isinstance(Time2[5], int) else Time2[5]
        time1 = datetime.datetime(Time1[0], Time1[1], Time1[2], Time1[3], Time1[4], int(sec1),
                                  microsecond=int((sec1 - int(sec1)) * 1e6))
        time2 = datetime.datetime(Time2[0], Time2[1], Time2[2], Time2[3], Time2[4], int(sec2),
                                  microsecond=int((sec2 - int(sec2)) * 1e6))
        diff = time2 - time1
        return diff.total_seconds()

    def SolutionLeastSquares(self, SmoothPseudorange, SatLiteXYZ, ApproxPos, obs_time):
        t = 0
        B = []
        L = []
        SizeSatLiteXYZ = len(SatLiteXYZ)
        for i in range(SizeSatLiteXYZ):
            t = t + SatLiteXYZ[i][3]
        if (t < 4):
            return 0
        else:
            try:
                # 计算矩阵的条件数
                for k in range(SizeSatLiteXYZ):
                    if (SatLiteXYZ[k][3] == 0):
                        continue
                    if (k == SizeSatLiteXYZ - 1):
                        break
                    P0 = np.sqrt(
                        np.square(SatLiteXYZ[k][0] - ApproxPos[0]) + np.square(
                            SatLiteXYZ[k][1] - ApproxPos[1]) + np.square(
                            SatLiteXYZ[k][2] - ApproxPos[2]))
                    TemB0 = -1 * (SatLiteXYZ[k][0] - ApproxPos[0]) / P0
                    TemB1 = -1 * (SatLiteXYZ[k][1] - ApproxPos[1]) / P0
                    TemB2 = -1 * (SatLiteXYZ[k][2] - ApproxPos[2]) / P0
                    c = 3 * (10 ** -8)
                    TemB3 = 1
                    TemBRol = [TemB0, TemB1, TemB2, TemB3]
                    B.append(TemBRol)
                    TemLRol = SmoothPseudorange[k] - P0 + c * SatLiteXYZ[k][4]
                    L.append(TemLRol)
                ArrayB = np.array(B)
                ArrayL = np.array(L)
                condition_number = np.linalg.cond(np.transpose(ArrayB) @ ArrayB)
                if condition_number > 1e12:  # 条件数过大，使用伪逆
                    x = np.linalg.pinv(np.transpose(ArrayB) @ ArrayB) @ (np.transpose(ArrayB) @ ArrayL)
                else:
                    x = np.linalg.inv(np.transpose(ArrayB) @ ArrayB) @ (np.transpose(ArrayB) @ ArrayL)
            except np.linalg.LinAlgError:
                print("矩阵奇异，使用伪逆计算")
                x = np.linalg.pinv(np.transpose(ArrayB) @ ArrayB) @ (np.transpose(ArrayB) @ ArrayL)
            PosXYZ = np.array(ApproxPos)
            updated_pos = [
                PosXYZ[0] + x[0],
                PosXYZ[1] + x[1],
                PosXYZ[2] + x[2]
            ]
            self.final_positions.append(updated_pos)
            GDOP, PDOP, HDOP, VDOP, TDOP = self.Accuracy(SatLiteXYZ, ApproxPos)
            self.gdop_values.append(GDOP)
            self.pdop_values.append(PDOP)
            self.hdop_values.append(HDOP)
            self.vdop_values.append(VDOP)
            self.tdop_values.append(TDOP)
            current_time = f"{obs_time[0]}-{obs_time[1]}-{obs_time[2]} {obs_time[3]}:{obs_time[4]}:{obs_time[5]}"
            self.observation_times.append(current_time)
            return 1

    def Accuracy(self, SatLiteXYZ, ApproxPos):
        M = np.zeros((len(SatLiteXYZ), 4))
        for i in range(len(SatLiteXYZ)):
            if (SatLiteXYZ[i][3] == 0):
                continue
            M[i][0] = -1 * (SatLiteXYZ[i][0] - ApproxPos[0])
            M[i][1] = -1 * (SatLiteXYZ[i][1] - ApproxPos[1])
            M[i][2] = -1 * (SatLiteXYZ[i][2] - ApproxPos[2])
            M[i][3] = 1
        try:
            Q = np.linalg.inv(np.transpose(M) @ M)
        except np.linalg.LinAlgError:
            print("计算精度指标时矩阵奇异，使用伪逆计算")
            Q = np.linalg.pinv(np.transpose(M) @ M)
        GDOP = np.sqrt(np.trace(Q))
        PDOP = np.sqrt(Q[0][0] + Q[1][1] + Q[2][2])
        HDOP = np.sqrt(Q[0][0] + Q[1][1])
        VDOP = np.sqrt(Q[2][2])
        TDOP = np.sqrt(Q[3][3])
        return GDOP, PDOP, HDOP, VDOP, TDOP