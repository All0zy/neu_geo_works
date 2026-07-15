import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import numpy as np
import threading
import time
import os

# 设置Matplotlib后端为TkAgg
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 导入项目模块
import gnss as gn
from gnss import ecef2pos, Nav
from gnss import time2doy, time2str, timediff, epoch2time, sat2prn, time2epoch
from gnss import rSigRnx, uGNSS
from gnss import sys2str
from peph import atxdec, searchpcv
from peph import peph, biasdec
from pppssr import pppos
from rinex import rnxdec

class GNSSGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GNSS PPP 处理工具")
        self.root.geometry("1000x600")  # 减小窗口高度，使其更适合不同屏幕尺寸
        
        # 文件路径变量
        self.navfile = ""
        self.obsfile = ""
        self.orbfile = ""
        self.clkfile = ""
        self.bsxfile = ""
        
        # 结果变量
        self.results = None
        self.fig = None
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左右分栏
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # 创建顶部框架，包含文件选择和右侧控件
        self.top_frame = ttk.Frame(self.left_frame)
        self.top_frame.pack(fill=tk.X, pady=5)
        
        # 文件选择框架
        self.file_frame = ttk.LabelFrame(self.top_frame, text="文件选择", padding="10")
        self.file_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 导航文件
        ttk.Label(self.file_frame, text="导航文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.nav_entry = ttk.Entry(self.file_frame, width=30)
        self.nav_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Button(self.file_frame, text="浏览", command=lambda: self.browse_file("nav")).grid(row=0, column=2, pady=5)
        
        # 观测文件
        ttk.Label(self.file_frame, text="观测文件:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.obs_entry = ttk.Entry(self.file_frame, width=30)
        self.obs_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Button(self.file_frame, text="浏览", command=lambda: self.browse_file("obs")).grid(row=1, column=2, pady=5)
        
        # 精密轨道文件
        ttk.Label(self.file_frame, text="精密轨道文件:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.orb_entry = ttk.Entry(self.file_frame, width=30)
        self.orb_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Button(self.file_frame, text="浏览", command=lambda: self.browse_file("orb")).grid(row=2, column=2, pady=5)
        
        # 钟差文件
        ttk.Label(self.file_frame, text="钟差文件:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.clk_entry = ttk.Entry(self.file_frame, width=30)
        self.clk_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        ttk.Button(self.file_frame, text="浏览", command=lambda: self.browse_file("clk")).grid(row=3, column=2, pady=5)
        
        # 偏置文件
        ttk.Label(self.file_frame, text="偏置文件:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.bsx_entry = ttk.Entry(self.file_frame, width=30)
        self.bsx_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        ttk.Button(self.file_frame, text="浏览", command=lambda: self.browse_file("bsx")).grid(row=4, column=2, pady=5)
        
        # 右侧控件框架
        self.control_frame = ttk.LabelFrame(self.top_frame, text="控制选项", padding="10")
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # 卫星系统选择
        ttk.Label(self.control_frame, text="卫星系统:").pack(anchor=tk.W, pady=5)
        
        self.gps_var = tk.BooleanVar(value=True)
        self.gal_var = tk.BooleanVar(value=True)
        self.bds_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(self.control_frame, text="GPS", variable=self.gps_var).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(self.control_frame, text="Galileo", variable=self.gal_var).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(self.control_frame, text="BeiDou", variable=self.bds_var).pack(anchor=tk.W, pady=2)
        
        # 进度条
        ttk.Label(self.control_frame, text="计算进度:").pack(anchor=tk.W, pady=5)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.control_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_label = ttk.Label(self.control_frame, text="准备就绪")
        self.progress_label.pack(pady=5)
        
        # 开始计算按钮
        self.calc_button = ttk.Button(self.control_frame, text="开始计算", command=self.start_calculation)
        self.calc_button.pack(pady=10)
        
        # 历元进度显示
        self.epoch_frame = ttk.LabelFrame(self.left_frame, text="实时进度", padding="10")
        self.epoch_frame.pack(fill=tk.X, pady=5)
        
        self.epoch_label = ttk.Label(self.epoch_frame, text="等待计算...", font=('Arial', 10))
        self.epoch_label.pack(fill=tk.X, pady=5)
        
        # 结果框架
        self.result_frame = ttk.LabelFrame(self.left_frame, text="精度显示", padding="10")
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 结果标签 - 调整布局为5行，每行显示相关数据
        self.result_labels = {}
        
        # 第一行：East数据
        ttk.Label(self.result_frame, text="East均值:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.E, pady=3, padx=5)
        east_mean_label = ttk.Label(self.result_frame, text="--", font=('Arial', 9, 'bold'))
        east_mean_label.grid(row=0, column=1, sticky=tk.W, pady=3, padx=5)
        self.result_labels["East均值"] = east_mean_label
        
        ttk.Label(self.result_frame, text="East标准差:", font=('Arial', 9)).grid(row=0, column=2, sticky=tk.E, pady=3, padx=5)
        east_std_label = ttk.Label(self.result_frame, text="--", font=('Arial', 9, 'bold'))
        east_std_label.grid(row=0, column=3, sticky=tk.W, pady=3, padx=5)
        self.result_labels["East标准差"] = east_std_label
        
        ttk.Label(self.result_frame, text="East RMS:", font=('Arial', 9)).grid(row=0, column=4, sticky=tk.E, pady=3, padx=5)
        east_rms_label = ttk.Label(self.result_frame, text="--", font=('Arial', 9, 'bold'))
        east_rms_label.grid(row=0, column=5, sticky=tk.W, pady=3, padx=5)
        self.result_labels["East RMS"] = east_rms_label
        
        # 第二行：North数据
        ttk.Label(self.result_frame, text="North均值:", font=('Arial', 9)).grid(row=1, column=0, sticky=tk.E, pady=3, padx=5)
        north_mean_label = ttk.Label(self.result_frame, text="--", font=('Arial', 9, 'bold'))
        north_mean_label.grid(row=1, column=1, sticky=tk.W, pady=3, padx=5)
        self.result_labels["North均值"] = north_mean_label
        
        ttk.Label(self.result_frame, text="North标准差:", font=('Arial', 9)).grid(row=1, column=2, sticky=tk.E, pady=3, padx=5)
        north_std_label = ttk.Label(self.result_frame, text="--", font=('Arial', 9, 'bold'))
        north_std_label.grid(row=1, column=3, sticky=tk.W, pady=3, padx=5)
        self.result_labels["North标准差"] = north_std_label
        
        ttk.Label(self.result_frame, text="North RMS:", font=('Arial', 9)).grid(row=1, column=4, sticky=tk.E, pady=3, padx=5)
        north_rms_label = ttk.Label(self.result_frame, text="--", font=('Arial', 9, 'bold'))
        north_rms_label.grid(row=1, column=5, sticky=tk.W, pady=3, padx=5)
        self.result_labels["North RMS"] = north_rms_label
        
        # 第三行：Up数据
        ttk.Label(self.result_frame, text="Up均值:", font=('Arial', 9)).grid(row=2, column=0, sticky=tk.E, pady=3, padx=5)
        up_mean_label = ttk.Label(self.result_frame, text="--", font=('Arial', 9, 'bold'))
        up_mean_label.grid(row=2, column=1, sticky=tk.W, pady=3, padx=5)
        self.result_labels["Up均值"] = up_mean_label
        
        ttk.Label(self.result_frame, text="Up标准差:", font=('Arial', 9)).grid(row=2, column=2, sticky=tk.E, pady=3, padx=5)
        up_std_label = ttk.Label(self.result_frame, text="--", font=('Arial', 9, 'bold'))
        up_std_label.grid(row=2, column=3, sticky=tk.W, pady=3, padx=5)
        self.result_labels["Up标准差"] = up_std_label
        
        ttk.Label(self.result_frame, text="Up RMS:", font=('Arial', 9)).grid(row=2, column=4, sticky=tk.E, pady=3, padx=5)
        up_rms_label = ttk.Label(self.result_frame, text="--", font=('Arial', 9, 'bold'))
        up_rms_label.grid(row=2, column=5, sticky=tk.W, pady=3, padx=5)
        self.result_labels["Up RMS"] = up_rms_label
        
        # 第四行：水平数据
        ttk.Label(self.result_frame, text="水平RMS:", font=('Arial', 9)).grid(row=3, column=0, sticky=tk.E, pady=3, padx=5)
        horizontal_rms_label = ttk.Label(self.result_frame, text="--", font=('Arial', 9, 'bold'))
        horizontal_rms_label.grid(row=3, column=1, sticky=tk.W, pady=3, padx=5, columnspan=5)
        self.result_labels["水平RMS"] = horizontal_rms_label
        
        # 第五行：有效历元数
        ttk.Label(self.result_frame, text="有效历元数:", font=('Arial', 9)).grid(row=4, column=0, sticky=tk.E, pady=3, padx=5)
        epoch_count_label = ttk.Label(self.result_frame, text="--", font=('Arial', 9, 'bold'))
        epoch_count_label.grid(row=4, column=1, sticky=tk.W, pady=3, padx=5, columnspan=5)
        self.result_labels["有效历元数"] = epoch_count_label
        
        # 图表框架（右侧）
        self.plot_frame = ttk.LabelFrame(self.right_frame, text="精度图表", padding="10")
        self.plot_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 图表选择标签页
        self.notebook = ttk.Notebook(self.plot_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建图表页面
        self.plot_pages = {}
        self.plot_canvases = {}  # 保存canvas对象，防止被垃圾回收
        plot_names = ["位置误差", "误差分布", "3D误差", "精度分析"]
        for name in plot_names:
            page = ttk.Frame(self.notebook)
            self.notebook.add(page, text=name)
            self.plot_pages[name] = page
            self.plot_canvases[name] = None
    
    def browse_file(self, file_type):
        # 根据文件类型设置不同的筛选
        file_filters = {
            "nav": ["RINEX文件", "*.rnx", "所有文件", "*.*"],
            "obs": ["RINEX文件", "*.rnx", "所有文件", "*.*"],
            "orb": ["SP3文件", "*.sp3", "所有文件", "*.*"],
            "clk": ["CLK文件", "*.clk", "所有文件", "*.*"],
            "bsx": ["BIA文件", "*.bia", "所有文件", "*.*"]
        }
        
        filters = file_filters.get(file_type, ["所有文件", "*.*"])
        file_path = filedialog.askopenfilename(filetypes=[(filters[0], filters[1]), (filters[2], filters[3])])
        
        if file_path:
            if file_type == "nav":
                self.navfile = file_path
                self.nav_entry.delete(0, tk.END)
                self.nav_entry.insert(0, file_path)
            elif file_type == "obs":
                self.obsfile = file_path
                self.obs_entry.delete(0, tk.END)
                self.obs_entry.insert(0, file_path)
            elif file_type == "orb":
                self.orbfile = file_path
                self.orb_entry.delete(0, tk.END)
                self.orb_entry.insert(0, file_path)
            elif file_type == "clk":
                self.clkfile = file_path
                self.clk_entry.delete(0, tk.END)
                self.clk_entry.insert(0, file_path)
            elif file_type == "bsx":
                self.bsxfile = file_path
                self.bsx_entry.delete(0, tk.END)
                self.bsx_entry.insert(0, file_path)
    
    def start_calculation(self):
        # 检查文件是否都已选择
        if not all([self.navfile, self.obsfile, self.orbfile, self.clkfile, self.bsxfile]):
            messagebox.showerror("错误", "请选择所有必要的文件")
            return
        
        # 禁用计算按钮
        self.calc_button.config(state=tk.DISABLED)
        
        # 清空结果和图表
        # 清空结果标签
        for label in self.result_labels:
            self.result_labels[label].config(text="--")
        # 清空历元进度
        self.epoch_label.config(text="开始计算...")
        # 清空图表
        for page_name, page in self.plot_pages.items():
            for widget in page.winfo_children():
                widget.destroy()
        
        # 启动计算线程
        calculation_thread = threading.Thread(target=self.calculate)
        calculation_thread.daemon = True
        calculation_thread.start()
    
    def calculate(self):
        try:
            # 重置进度
            self.update_progress(0, "准备中...")
            
            # 定义信号
            gnss = ""
            if self.gps_var.get():
                gnss += "G"
            if self.gal_var.get():
                gnss += "E"
            if self.bds_var.get():
                gnss += "C"
            
            sigs = []
            if 'G' in gnss:
                sigs.extend([rSigRnx("GC1C"), rSigRnx("GC2W"),
                            rSigRnx("GL1C"), rSigRnx("GL2W"),
                            rSigRnx("GS1C"), rSigRnx("GS2W")])
            if 'E' in gnss:
                sigs.extend([rSigRnx("EC1C"), rSigRnx("EC5Q"),
                            rSigRnx("EL1C"), rSigRnx("EL5Q"),
                            rSigRnx("ES1C"), rSigRnx("ES5Q")])
            if 'C' in gnss:
                sigs.extend([rSigRnx("CC2I"), rSigRnx("CC6I"),
                            rSigRnx("CL2I"), rSigRnx("CL6I"),
                            rSigRnx("CS2I"), rSigRnx("CS6I")])
            
            # 初始化对象
            rnx = rnxdec()
            rnx.setSignals(sigs)
            
            nav = Nav()
            orb = peph()
            
            # 定位模式
            nav.pmode = 0  # 静态
            
            # 解码RINEX导航数据
            nav = rnx.decode_nav(self.navfile, nav)
            
            # 加载精密轨道和钟差
            nav = orb.parse_sp3(self.orbfile, nav)
            nav = rnx.decode_clk(self.clkfile, nav)
            
            # 加载码和相位偏置
            bsx = biasdec()
            bsx.parse(self.bsxfile)
            
            # 加载天线相位中心数据
            time = epoch2time([2026, 2, 22, 0, 0, 0])
            if time > epoch2time([2022, 11, 27, 0, 0, 0]):
                atxfile = '../data/I20.ATX'
            elif time > epoch2time([2021, 5, 2, 0, 0, 0]):
                atxfile = '../data/M20.ATX'
            else:
                atxfile = '../data/M14.ATX'
            
            atx = atxdec()
            atx.readpcv(atxfile)
            
            # 初始化数据结构
            nep = 1440
            t = np.zeros(nep)
            enu = np.ones((nep, 3))*np.nan
            sol = np.zeros((nep, 4))
            ztd = np.zeros((nep, 1))
            smode = np.zeros(nep, dtype=int)
            
            # 日志级别
            nav.monlevel = 1
            
            # 加载RINEX观测文件头
            if rnx.decode_obsh(self.obsfile) >= 0:
                # 自动替换信号
                rnx.autoSubstituteSignals()
                
                # 初始化位置
                ppp = pppos(nav, rnx.pos, 'test_pppigs.log')
                nav.ephopt = 4  # IGS
                nav.armode = 3
                
                # 禁用C/N0检查
                nav.cnr_min = 0.0
                nav.cnr_min_gpy = 0.0
                nav.elmin = np.deg2rad(5.0)
                nav.thresar = 2.0
                
                # 设置PCO/PCV信息
                nav.sat_ant = atx.pcvs
                nav.rcv_ant = searchpcv(atx.pcvr, rnx.ant, rnx.ts)
                
                # 跳过历元直到开始时间
                obs = rnx.decode_obs()
                while time > obs.t and obs.t.time != 0:
                    obs = rnx.decode_obs()
                
                # 基准位置
                xyz_ref = [-2994429.4511, 4951309.9057, 2674497.1692]
                pos_ref = ecef2pos(xyz_ref)
                
                # 处理历元（进度条只显示历元计算进度）
                for ne in range(nep):
                    # 更新进度（只反应历元计算进度）
                    progress = (ne / nep) * 100
                    self.update_progress(progress, f"处理历元 {ne+1}/{nep}")
                    
                    # 设置初始历元
                    if ne == 0:
                        nav.t = obs.t
                        t0 = obs.t
                    
                    # 调用PPP模块
                    ppp.process(obs, orb=orb, bsx=bsx)
                    
                    # 保存输出
                    t[ne] = timediff(nav.t, t0)/86400.0
                    sol = nav.xa[0:3] if nav.smode == 4 else nav.x[0:3]
                    enu[ne, :] = gn.ecef2enu(pos_ref, sol-xyz_ref)
                    ztd[ne] = nav.xa[ppp.IT(nav.na)] if nav.smode == 4 else nav.x[ppp.IT(nav.na)]
                    smode[ne] = nav.smode
                    
                    # 显示历元进度
                    epoch_info = f"{time2str(obs.t)} ENU {enu[ne, 0]:7.3f} {enu[ne, 1]:7.3f} {enu[ne, 2]:7.3f}, 2D {np.sqrt(enu[ne, 0]**2+enu[ne, 1]**2):6.3f}, mode {smode[ne]:1d}"
                    self.update_epoch_progress(epoch_info)
                    
                    # 获取新历元
                    obs = rnx.decode_obs()
                    if obs.t.time == 0:
                        break
                
                # 关闭文件
                rnx.fobs.close()
                if nav.fout is not None:
                    nav.fout.close()
                
                # 将图表创建和结果计算移到主线程执行
                self.root.after(0, lambda: self.generate_results(t, enu, ztd, smode))
                
                self.update_progress(100, "计算完成!")
                
        except Exception as e:
            self.update_progress(0, f"计算错误: {str(e)}")
            messagebox.showerror("错误", f"计算过程中出现错误: {str(e)}")
        finally:
            # 启用计算按钮（确保在主线程中执行）
            def enable_calc_button():
                try:
                    if hasattr(self, 'calc_button') and self.calc_button.winfo_exists():
                        self.calc_button.config(state=tk.NORMAL)
                except Exception:
                    pass
            self.root.after(0, enable_calc_button)
    
    def update_progress(self, value, message):
        def update_gui():
            try:
                if hasattr(self, 'progress_var') and hasattr(self, 'progress_label'):
                    if self.progress_label.winfo_exists():
                        self.progress_var.set(value)
                        self.progress_label.config(text=message)
            except Exception:
                pass
        self.root.after(0, update_gui)
    
    def update_epoch_progress(self, epoch_info):
        def update_gui():
            try:
                if hasattr(self, 'epoch_label') and self.epoch_label.winfo_exists():
                    self.epoch_label.config(text=epoch_info)
            except Exception:
                pass
        self.root.after(0, update_gui)
    
    def generate_plots(self, t, enu, ztd, smode):
        # 清空所有图表页面
        for page_name, page in self.plot_pages.items():
            for widget in page.winfo_children():
                widget.destroy()
        
        # 保存数据用于绘图
        self.t = t
        self.enu = enu
        self.smode = smode
        
        # 生成第一个图表：位置误差
        fig1 = plt.figure(figsize=[7, 4.5])  # 减小图表高度
        # 过滤有效数据
        idx4 = np.where(smode == 4)[0]  # fix
        idx5 = np.where(smode == 5)[0]  # float
        idx0 = np.where(smode == 0)[0]  # no solution
        
        # 绘制ENU误差
        lbl_t = ['East [m]', 'North [m]', 'Up [m]']
        
        for k in range(3):
            plt.subplot(4, 1, k+1)
            if len(idx0) > 0:
                plt.plot(t[idx0], enu[idx0, k], 'r.', label='none')
            if len(idx5) > 0:
                plt.plot(t[idx5], enu[idx5, k], 'y.', label='float')
            if len(idx4) > 0:
                plt.plot(t[idx4], enu[idx4, k], 'g.', label='fix')
            
            plt.ylabel(lbl_t[k])
            plt.grid()
            plt.ylim([-1.0, 1.0])
        
        # 绘制ZTD
        plt.subplot(4, 1, 4)
        if len(idx0) > 0:
            plt.plot(t[idx0], ztd[idx0]*1e2, 'r.', markersize=8, label='none')
        if len(idx5) > 0:
            plt.plot(t[idx5], ztd[idx5]*1e2, 'y.', markersize=8, label='float')
        if len(idx4) > 0:
            plt.plot(t[idx4], ztd[idx4]*1e2, 'g.', markersize=8, label='fix')
        plt.ylabel('ZTD [cm]')
        plt.grid()
        plt.xlabel('Time [days]')
        plt.legend()
        
        # 将图表嵌入到第一个页面
        canvas1 = FigureCanvasTkAgg(fig1, master=self.plot_pages["位置误差"])
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.plot_canvases["位置误差"] = canvas1  # 保存canvas对象
        
        # 生成其他图表（使用plot_accuracy模块）
        # 注意：这里需要保存数据到CSV文件，然后调用plot_accuracy
        self.save_results_to_csv(t, enu, smode)
        
        # 生成第二个图表：误差分布
        fig2 = plt.figure(figsize=[7, 4.5])  # 减小图表高度
        labels = ['East', 'North', 'Up']
        for i, label in enumerate(labels):
            plt.subplot(1, 3, i+1)
            valid_mask = ~np.isnan(enu[:, i])
            plt.hist(enu[valid_mask, i], bins=50, edgecolor='black', alpha=0.7, color='steelblue')
            plt.xlabel(f'{label} Error [m]')
            plt.ylabel('Frequency')
            plt.title(f'{label} Error Distribution')
            plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        canvas2 = FigureCanvasTkAgg(fig2, master=self.plot_pages["误差分布"])
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.plot_canvases["误差分布"] = canvas2  # 保存canvas对象
        
        # 生成第三个图表：3D误差
        fig3 = plt.figure(figsize=[7, 4.5])  # 减小图表高度
        ax3 = fig3.add_subplot(111, projection='3d')
        mode_info = [(idx0, 'r', 'no solution'), (idx5, 'y', 'float'), (idx4, 'g', 'fix')]
        for idx, color, label in mode_info:
            if len(idx) > 0:
                ax3.scatter(enu[idx, 0], enu[idx, 1], enu[idx, 2], c=color, alpha=0.6, s=20, label=label)
        ax3.set_xlabel('East [m]')
        ax3.set_ylabel('North [m]')
        ax3.set_zlabel('Up [m]')
        ax3.set_title('3D Position Error Distribution')
        ax3.legend()
        
        canvas3 = FigureCanvasTkAgg(fig3, master=self.plot_pages["3D误差"])
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.plot_canvases["3D误差"] = canvas3  # 保存canvas对象
        
        # 生成第四个图表：精度分析
        fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=[7, 3])  # 保持较小的高度
        # 绘制精度vs时间
        h_2d = np.sqrt(enu[:, 0]**2 + enu[:, 1]**2)
        for idx, color, label in mode_info:
            if len(idx) > 0:
                ax4a.plot(t[idx], h_2d[idx], '.', color=color, label=label, alpha=0.6, markersize=4)
        ax4a.set_ylabel('Horizontal Error 2D [m]')
        ax4a.set_xlabel('Time [day]')
        ax4a.set_title('Positioning Accuracy vs Time')
        ax4a.grid(True, alpha=0.3)
        ax4a.legend(fontsize=8)
        
        # 绘制CDF
        if len(idx4) > 0:
            h_2d_fix = np.sort(h_2d[idx4])
            cdf = np.linspace(0, 100, len(h_2d_fix))
            ax4b.plot(h_2d_fix, cdf, 'g-', linewidth=2.5, label='Fixed solution')
            p50 = np.percentile(h_2d_fix, 50)
            p95 = np.percentile(h_2d_fix, 95)
            ax4b.axvline(p50, color='g', linestyle='--', alpha=0.5, label=f'50%: {p50:.3f}m')
            ax4b.axvline(p95, color='r', linestyle='--', alpha=0.5, label=f'95%: {p95:.3f}m')
        ax4b.set_xlabel('Horizontal Error [m]')
        ax4b.set_ylabel('Cumulative Probability [%]')
        ax4b.set_title('CDF of Fixed Solution Accuracy')
        ax4b.grid(True, alpha=0.3)
        ax4b.legend(fontsize=8)
        plt.tight_layout()
        
        canvas4 = FigureCanvasTkAgg(fig4, master=self.plot_pages["精度分析"])
        canvas4.draw()
        canvas4.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.plot_canvases["精度分析"] = canvas4  # 保存 canvas 对象
        
        # 保存图表为 PNG 格式
        fig1.savefig('gui_position_error.png', format='png', bbox_inches='tight', dpi=300)
        fig2.savefig('gui_error_distribution.png', format='png', bbox_inches='tight', dpi=300)
        fig3.savefig('gui_3d_error.png', format='png', bbox_inches='tight', dpi=300)
        fig4.savefig('gui_accuracy_analysis.png', format='png', bbox_inches='tight', dpi=300)
        print("图表已保存为 PNG 格式")
    
    def generate_results(self, t, enu, ztd, smode):
        # 生成图表
        self.generate_plots(t, enu, ztd, smode)
        
        # 计算误差参数
        self.calculate_error_stats(enu, smode)
    
    def save_results_to_csv(self, t, enu, smode):
        # 保存结果到CSV文件，供plot_accuracy使用
        import pandas as pd
        df = pd.DataFrame({
            'Time': t,
            'East(m)': enu[:, 0],
            'North(m)': enu[:, 1],
            'Up(m)': enu[:, 2],
            'Mode': smode
        })
        df.to_csv('test_pppigs_results.csv', index=False)
    
    def calculate_error_stats(self, enu, smode):
        # 过滤fix模式的数据
        idx4 = np.where(smode == 4)[0]
        if len(idx4) == 0:
            for label in self.result_labels:
                self.result_labels[label].config(text="--")
            return
        
        # 提取fix模式的ENU误差
        enu_fix = enu[idx4, :]
        
        # 计算统计量
        east_std = np.std(enu_fix[:, 0])
        north_std = np.std(enu_fix[:, 1])
        up_std = np.std(enu_fix[:, 2])
        
        # 计算平均误差
        east_mean = np.mean(enu_fix[:, 0])
        north_mean = np.mean(enu_fix[:, 1])
        up_mean = np.mean(enu_fix[:, 2])
        
        # 计算RMS
        east_rms = np.sqrt(np.mean(enu_fix[:, 0]**2))
        north_rms = np.sqrt(np.mean(enu_fix[:, 1]**2))
        up_rms = np.sqrt(np.mean(enu_fix[:, 2]**2))
        horizontal_rms = np.sqrt(np.mean(enu_fix[:, 0]**2 + enu_fix[:, 1]**2))
        
        # 确保在主线程中更新UI
        def update_labels():
            self.result_labels["East均值"].config(text=f"{east_mean:.4f} m")
            self.result_labels["East标准差"].config(text=f"{east_std:.4f} m")
            self.result_labels["East RMS"].config(text=f"{east_rms:.4f} m")
            self.result_labels["North均值"].config(text=f"{north_mean:.4f} m")
            self.result_labels["North标准差"].config(text=f"{north_std:.4f} m")
            self.result_labels["North RMS"].config(text=f"{north_rms:.4f} m")
            self.result_labels["Up均值"].config(text=f"{up_mean:.4f} m")
            self.result_labels["Up标准差"].config(text=f"{up_std:.4f} m")
            self.result_labels["Up RMS"].config(text=f"{up_rms:.4f} m")
            self.result_labels["水平RMS"].config(text=f"{horizontal_rms:.4f} m")
            self.result_labels["有效历元数"].config(text=f"{len(idx4)}")
        
        # 使用after方法确保在主线程中执行
        self.root.after(0, update_labels)

if __name__ == "__main__":
    root = tk.Tk()
    app = GNSSGUI(root)
    root.mainloop()