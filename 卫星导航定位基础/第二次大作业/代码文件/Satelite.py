import datetime
import numpy as np

class Satelite:
    def __init__(self, SateliteName, Time, SateliteClockCorrect, SateliteObservation):
        self.SateliteName = SateliteName
        self.GpsSeconds = Satelite.ctime2gps(Time)
        self.Time = Time
        self.SateliteRefTime = Time
        self.SateliteClockCorrect = SateliteClockCorrect
        self.SateliteObservation = SateliteObservation
        self.Delta_T = 0

    def InitPositionOfSat(self, ObsTime):
        [sat_x, sat_y, sat_z, delta_t_value] = Satelite.caculate_pos_of_sat(self.SateliteObservation,
                                                                            self.SateliteClockCorrect, ObsTime,
                                                                            self.Time)
        self.X = sat_x
        self.Y = sat_y
        self.Z = sat_z
        self.Delta_T = delta_t_value

    @classmethod
    def GetPositionOfSat(self):
        return self.X, self.Y, self.Z

    @staticmethod
    def ctime2gps(time):
        gps_epoch = datetime.datetime(1980, 1, 6, 0, 0, 0)
        given_time = datetime.datetime(time[0], time[1], time[2], time[3], time[4], int(time[5]))
        time_diff = given_time - gps_epoch
        total_seconds = time_diff.total_seconds()
        gps_week, gps_seconds = divmod(total_seconds, 604800)
        return gps_week, gps_seconds

    @staticmethod
    def caculate_pos_of_sat(matrix, a3, obstime, reftime):
        GM = 3.986005 * pow(10, 5)
        n0 = np.sqrt(GM) / pow(matrix[1, 3], 3)
        n = n0 + matrix[0, 2]
        gps_obsweek, gps_obssec = Satelite.ctime2gps(obstime)
        gps_refweek, gps_refseconds = Satelite.ctime2gps(reftime)
        delta_t = a3[0] + a3[1] * (gps_obssec - gps_refseconds) + a3[2] * pow(gps_obssec - gps_refseconds, 2)
        t = gps_refseconds - delta_t
        tk = t - matrix[2, 0]
        Mk = matrix[0, 3] + n * tk
        Mk = Mk % (np.pi * 2)
        Ek = Mk
        Ek_old = Ek
        for i in range(10):
            Ek = Mk + matrix[1, 1] * np.sin(Ek)
            if (abs(Ek - Ek_old) < 1e-10):
                break
            else:
                Ek_old = Ek
        cos_Vk = (np.cos(Ek) - matrix[1, 1]) / (1 - matrix[1, 1] * np.cos(Ek))
        sin_Vk = (np.sqrt(1 - matrix[1, 1] * matrix[1, 1]) * np.sin(Ek)) / (1 - matrix[1, 1] * np.cos(Ek))
        Vk = np.arctan(np.sqrt(1 - matrix[1, 1] * matrix[1, 1]) * np.sin(Ek) / (np.cos(Ek) - matrix[1, 1]))
        phi_k = Vk + matrix[3, 2]
        phi_k = phi_k % (np.pi * 2)
        delta_u = matrix[1, 0] * np.cos(2 * phi_k) + matrix[1, 2] * np.sin(2 * phi_k)
        delta_r = matrix[3, 1] * np.cos(2 * phi_k) + matrix[0, 1] * np.sin(2 * phi_k)
        delta_i = matrix[2, 1] * np.cos(2 * phi_k) + matrix[2, 3] * np.sin(2 * phi_k)
        uk = phi_k + delta_u
        rk = pow(matrix[1, 3], 2) * (1 - matrix[1, 1] * np.cos(Ek)) + delta_r
        ik = matrix[3, 0] + delta_i + matrix[4, 0] * tk
        xk = rk * np.cos(uk)
        yk = rk * np.sin(uk)
        we = 7.29211567 * pow(10, -5)
        omegek = matrix[2, 2] + (matrix[3, 3] - we) * tk - we * matrix[2, 0]
        Xk = xk * np.cos(omegek) - yk * np.cos(ik) * np.sin(omegek)
        Yk = xk * np.sin(omegek) + yk * np.cos(ik) * np.cos(omegek)
        Zk = yk * np.sin(ik)
        return Xk, Yk, Zk, delta_t
