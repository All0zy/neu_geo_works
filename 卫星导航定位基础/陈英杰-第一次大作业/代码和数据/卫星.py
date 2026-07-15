import math as m
import numpy as np
import csv
 
infile=open("广播星历.rnx","r")
#读取原星历文件
content=infile.readlines()
infile.close()
start_num=0
all_C=[]#存储北斗星历数据块
for i in range(len(content)):
    if content[i].find("                                                            END OF HEADER") != -1:
        start_num = i + 1
for i in range(len(content)-start_num):
    line=content[start_num+i]
    if line[0]=='C':
        for j in range(0,8):
            all_C.append(content[start_num+i+j])
outFile=open("all_C.txt",'w')#存储为新的文件（只含有北斗卫星）
outFile.writelines(all_C)
outFile.close()
 
#接下来是计算卫星位置的程序
with open(
          'all_C.txt', 'r') as f:
    if f == 0:
        print("不能打开文件！")
    else:
        print("导航文件打开成功！")
    nfile_lines = f.readlines()  # 按行读取N文件
    print(len(nfile_lines))
    f.close()
 
 
 
def start_num():  # 定义数据记录的起始行
    start_num = 0
    for i in range(len(nfile_lines)):
        if nfile_lines[i].find('END OF HEADER') != -1:
            start_num = i + 1
    return start_num
 
 
def rx(fai):
    result = np.asmatrix([[1, 0, 0], [0, m.cos(fai), m.sin(fai)], [0, -1 * m.sin(fai), m.cos(fai)]])
    return result
 
 
def rz(fai):
    result = np.asmatrix([[m.cos(fai), m.sin(fai), 0], [-1 * m.sin(fai), m.cos(fai), 0], [0, 0, 1]])
    return result
 
 
n_dic_list = []
 
n_data_lines_nums = int((len(nfile_lines) - start_num()) / 8)
print("一共%d组数据" % (n_data_lines_nums))
 
# 第j组，第i行
for j in range(n_data_lines_nums):
    n_dic = {}
    for i in range(8):
        data_content = nfile_lines[start_num() + 8 * j + i]
        n_dic['数据组数'] = j + 1
        if i == 0:
            n_dic['卫星PRN号'] = str(data_content[0:3])
 
            n_dic['历元'] = data_content[4:23]
 
            n_dic['卫星钟偏差(s)'] = float(
                (data_content.strip('\n')[23:42]))  # 利用字符串切片功能来进行字符串的修改
 
            n_dic['卫星钟漂移(s/s)'] = float(
                (data_content.strip('\n')[42:61]))
 
            n_dic['卫星钟漂移速度(s/s*s)'] = float(
                (data_content.strip('\n')[61:80]))
 
        if i == 1:
            n_dic['IODE'] = float(
                (data_content.strip('\n')[4:23]))
            n_dic['C_rs'] = float(
                (data_content.strip('\n')[23:42]))
            n_dic['n'] = float(
                (data_content.strip('\n')[42:61]))
            n_dic['M0'] = float(
                (data_content.strip('\n')[61:80]))
        if i == 2:
            n_dic['C_uc'] = float(
                (data_content.strip('\n')[4:23]))
            n_dic['e'] = float(
                (data_content.strip('\n')[23:42]))
            n_dic['C_us'] = float(
                (data_content.strip('\n')[42:61]))
            n_dic['sqrt_A'] = float(
                (data_content.strip('\n')[61:80]))
        if i == 3:
            n_dic['TEO'] = float(
                (data_content.strip('\n')[4:23]))
            n_dic['C_ic'] = float(
                (data_content.strip('\n')[23:42]))
            n_dic['OMEGA'] = float(
                (data_content.strip('\n')[42:61]))
            n_dic['C_is'] = float(
                (data_content.strip('\n')[61:80]))
 
        if i == 4:
            n_dic['I_0'] = float(
                (data_content.strip('\n')[4:23]))
            n_dic['C_rc'] = float(
                (data_content.strip('\n')[23:42]))
            n_dic['w'] = float(
                (data_content.strip('\n')[42:61]))
            n_dic['OMEGA_DOT'] = float(
                (data_content.strip('\n')[61:80]))
        if i == 5:
            n_dic['IDOT'] = float(
                (data_content.strip('\n')[4:23]))
            n_dic['L2_code'] = float(
                (data_content.strip('\n')[23:42]))
            n_dic['PS_week_num'] = float(
                (data_content.strip('\n')[42:61]))
 
        if i == 6:
            n_dic['卫星精度(m)'] = float(
                (data_content.strip('\n')[4:23]))
            n_dic['卫星健康状态'] = float(
                (data_content.strip('\n')[23:42]))
            n_dic['TGD'] = float(
                (data_content.strip('\n')[42:61]))
            n_dic['IODC'] = float(
                (data_content.strip('\n')[61:80]))
 
    n_dic_list.append(n_dic)
with open('北斗卫星.csv', 'w', newline='') as f:
    header = ['数据组数', '卫星PRN号', '历元', '卫星钟偏差(s)', '卫星钟漂移(s/s)', '卫星钟漂移速度(s/s*s)', 'IODE',
              'C_rs', 'n', 'M0', 'C_uc', 'e', 'C_us', 'sqrt_A', 'TEO', 'C_ic', 'OMEGA', 'C_is', 'I_0', 'C_rc', 'w',
              'OMEGA_DOT', 'IDOT', 'L2_code', 'PS_week_num', 'L2_P_code', '卫星精度(m)', '卫星健康状态', 'TGD', 'IODC',
              'X', 'Y', 'Z']
    writer = csv.DictWriter(f, fieldnames=header)
    writer.writeheader()
    writer.writerows(n_dic_list)
f.close()
prn_x_y_z = []
with open('北斗卫星.csv', 'rt') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
 
        PRN = str(row["卫星PRN号"])
        TIME = row["历元"]
 
        year = int(TIME.strip('\n')[2:4])
 
        month = int(TIME.strip('\n')[5:7])
 
        day = int(TIME.strip('\n')[8:10])
 
        hour = int(TIME.strip('\n')[11:13])
        minute = int(TIME.strip('\n')[14:16])
        second = float(TIME.strip('\n')[17:19])
        a_0 = float(row["卫星钟偏差(s)"])
        a_1 = float(row["卫星钟漂移(s/s)"])
        a_2 = float(row["卫星钟漂移速度(s/s*s)"])
        IODE = float(row["IODE"])
        C_rs = float(row["C_rs"])
        δn = float(row["n"])
        M0 = float(row["M0"])
        C_uc = float(row["C_uc"])
        e = float(row["e"])
        C_us = float(row["C_us"])
        sqrt_A = float(row["sqrt_A"])
        TEO = float(row["TEO"])
        C_ic = float(row["C_ic"])
        OMEGA = float(row["OMEGA"])
        C_is = float(row["C_is"])
        I_0 = float(row["I_0"])
        C_rc = float(row["C_rc"])
        w = float(row["w"])
        OMEGA_DOT = float(row["OMEGA_DOT"])
        IDOT = float(row["IDOT"])
        L2_code = float(row["L2_code"])
        PS_week_num = float(row["PS_week_num"])
 
 
        TGD = float(row["TGD"])
        IODC = float(row["IODC"])
        t1 = None
        # 1.计算卫星运行平均角速度 GM:WGS84下的引力常数 =3.986005e14，a:长半径
        GM = 398600500000000
        n_0 = m.sqrt(GM) / m.pow(sqrt_A, 3)
        n = n_0 + δn
 
        # 2.计算归化时间t_k 计算t时刻的卫星位置  UT：世界时 此处以小时为单位
        UT = hour + (minute / 60.0) + (second / 3600)
        # GPS时起始时刻1980年1月6日0点   year是两位数 需要转换到四位数
        if year >= 80:
            if year == 80 and month == 1 and day < 6:
                year = year + 2000
            else:
                year = year + 1900
        else:
            year = year + 2000
        if month <= 2:
            year = year - 1
            month = month + 12  # 1，2月视为前一年13，14月
 
        # 需要将当前需计算的时刻先转换到儒略日再转换到GPS时间
        JD = (365.25 * year) + int(30.6001 * (month + 1)) + day + UT / 24 + 1720981.5
 
        WN = int((JD - 2444244.5) / 7)  # WN:GPS_week number 目标时刻的GPS周
 
        t_oc = ((JD - 2444244.5) - (7.0 * WN)) * 24 * 3600.0 - 14  # t_GPS:目标时刻的GPS秒 减去14秒为BDT
 
        # 对观测时刻t1进行钟差改正,注意：t1应是由接收机接收到的时间
 
        t_k = -14
 
 
        # 3.平近点角计算M_k = M_0+n*t_k
        M_k = M0 + n * t_k  # 实际应该是乘t_k，但是没有接收机的观测时间，所以为了练手设t_k=0
 
        # 4.偏近点角计算 E_k  (迭代计算) E_k = M_k + e*sin(E_k)
        E = 0
        E1 = 1
        count = 0
        while abs(E1 - E) > 1e-10:
            count = count + 1
            E1 = E
            E = M_k + e * m.sin(E)
            if count > 1e8:
                print("计算偏近点角时未收敛！")
                break
 
                # 5.计算卫星的真近点角
        V_k = m.atan2((m.sqrt(1 - e * e) * m.sin(E)) , (m.cos(E) - e));
 
        # 6.计算升交距角 u_0(φ_k), ω:卫星电文给出的近地点角距
        u_0 = V_k + w
 
        # 7.摄动改正项 δu、δr、δi :升交距角u、卫星矢径r和轨道倾角i的摄动量
        δu = C_uc * m.cos(2 * u_0) + C_us * m.sin(2 * u_0)
        δr = C_rc * m.cos(2 * u_0) + C_rs * m.sin(2 * u_0)
        δi = C_ic * m.cos(2 * u_0) + C_is * m.sin(2 * u_0)
 
        # 8.计算经过摄动改正的升交距角u_k、卫星矢径r_k和轨道倾角 i_k
        u = u_0 + δu
        r = m.pow(sqrt_A, 2) * (1 - e * m.cos(E)) + δr
        i = I_0 + δi + IDOT * (t_k);  # 实际乘t_k=t-t_oe
 
        # 9.计算卫星在轨道平面坐标系的坐标,卫星在轨道平面直角坐标系（X轴指向升交点）中的坐标为：
        x_k = r * m.cos(u)
        y_k = r * m.sin(u)
 
        # 10.观测时刻升交点经度Ω_k的计算，升交点经度Ω_k等于观测时刻升交点赤经Ω与格林尼治恒星时GAST之差  Ω_k=Ω_0+(ω_DOT-omega_e)*t_k-omega_e*t_oe
        omega_e = 7.292115e-5  # 地球自转角速度
        OMEGA_k = OMEGA + (OMEGA_DOT - omega_e) * t_k - omega_e * TEO;  # 星历中给出的Omega即为Omega_o=Omega_t_oe-GAST_w
 
        # 11.计算卫星在地固系中的直角坐标l
        X_k = x_k * m.cos(OMEGA_k) - y_k * m.cos(i) * m.sin(OMEGA_k)
        Y_k = x_k * m.sin(OMEGA_k) + y_k * m.cos(i) * m.cos(OMEGA_k)
        Z_k = y_k * m.sin(i)
 
        # 12.判断卫星是否为GEO卫星，否则不进行极移改正。
        if PRN in ['C01', 'C02', 'C03', 'C04', 'C05', 'C59', 'C60', 'C61']:
 
            fi = omega_e * t_k
            five = ( m.pi/180 * 5)*(-1)
            print(fi)
            a = np.asmatrix([X_k, Y_k, Z_k])
 
 
            a = rz(fi) * rx(five) * a.T
 
            X_k = str(a[0, 0])
            Y_k = str(a[1, 0])
            Z_k = str(a[2, 0])
 
            if month > 12:  # 恢复历元
                year = year + 1
                month = month - 12
 
            print("历元：", year, "年", month, "月", day, "日", hour, "时", minute, "分", second, "秒", "卫星PRN号:",
                  PRN,
                  "平均角速度:", n, "卫星平近点角:", M_k, "偏近点角:", E, "真近点角:", V_k, "升交距角:", u_0,
                  "摄动改正项:", δu,
                  δr, δi, "经摄动改正后的升交距角、卫星矢径和轨道倾角:", u, r, i, "轨道平面坐标X,Y:", x_k, y_k,
                  "观测时刻升交点经度:", OMEGA_k, "地固直角坐标系(极移改正)X:", X_k, "地固直角坐标系Y（极移改正）:", Y_k,
                  "地固直角坐标系Z（极移改正）:",
                  Z_k)
            prn_x_y_z.append(PRN + ",")
            prn_x_y_z.append(str(X_k) + ",")
            prn_x_y_z.append(str(Y_k) + ",")
            prn_x_y_z.append(str(Z_k))
            prn_x_y_z.append("\n")
 
 
        else:
          prn_x_y_z.append(PRN + ",")
          prn_x_y_z.append(str(X_k) + ",")
          prn_x_y_z.append(str(Y_k) + ",")
          prn_x_y_z.append(str(Z_k))
          prn_x_y_z.append("\n")
 
print("卫星坐标数据计算完成！")
f = open("北斗卫星位置.txt", 'w')
f.writelines(prn_x_y_z)
print("文件写入成功！")
f.close()
 
 
 
 
 
 
 
 
 
 
 
 
 