import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import matplotlib
matplotlib.use("TkAgg")

plt.rcParams["font.family"] = ["SimHei"]

class NetworkAdjustmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("20232411-张洋 网平差程序")
        self.root.geometry("1200x600")
        self.root.resizable(True, True)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.figures = []
        
        self.calculation_steps = []
        
        self.style = ttk.Style()
        self.style.theme_use('vista')
        
        self.style.configure('TButton', font=('微软雅黑', 10))
        self.style.configure('TLabel', font=('微软雅黑', 10), padding=5)
        self.style.configure('Header.TLabel', font=('微软雅黑', 12, 'bold'), padding=10)
        self.style.configure('Card.TFrame', background='#f0f0f0', relief='ridge')
        
        self.file_path = ""
        self.data = None
        self.G = None
        self.elevations = None
        self.precision_results = None
        
        self.create_widgets()
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        header_label = ttk.Label(main_frame, text="测绘2301班 20232411 张洋 水准网平差程序设计", style='Header.TLabel')
        header_label.pack(pady=10)
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制区", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 文件上传区域
        file_frame = ttk.Frame(control_frame, padding=5)
        file_frame.pack(fill=tk.X, pady=5)
        
        self.upload_btn = ttk.Button(file_frame, text="上传Excel文件", command=self.upload_file)
        self.upload_btn.pack(fill=tk.X)
        
        self.file_label = ttk.Label(file_frame, text="未选择文件", wraplength=200)
        self.file_label.pack(pady=5)
        
        # 已知点设置区域
        known_point_frame = ttk.LabelFrame(control_frame, text="已知点设置", padding=10)
        known_point_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(known_point_frame, text="已知点名称:").pack(anchor=tk.W)
        self.known_node_var = tk.StringVar(value="A")
        known_node_entry = ttk.Entry(known_point_frame, textvariable=self.known_node_var)
        known_node_entry.pack(fill=tk.X, pady=2)
        
        ttk.Label(known_point_frame, text="已知点高程:").pack(anchor=tk.W)
        self.known_elev_var = tk.StringVar(value="10.000")
        known_elev_entry = ttk.Entry(known_point_frame, textvariable=self.known_elev_var)
        known_elev_entry.pack(fill=tk.X, pady=2)
        
        # 操作按钮
        btn_frame = ttk.Frame(control_frame, padding=5)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.process_btn = ttk.Button(btn_frame, text="开始计算", command=self.process_network)
        self.process_btn.pack(fill=tk.X, pady=2)
        
        # 状态标签
        self.status_var = tk.StringVar(value="待执行")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, foreground="blue")
        status_label.pack(side=tk.BOTTOM, pady=10)
        
        # 右侧结果展示区
        result_frame = ttk.LabelFrame(main_frame, text="结果展示", padding=10)
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建笔记本控件（标签页）
        notebook = ttk.Notebook(result_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 高程结果标签页
        self.elev_frame = ttk.Frame(notebook)
        notebook.add(self.elev_frame, text="高程结果")
        
        # 创建高程结果表格
        self.create_elev_treeview()
        
        # 精度评定标签页
        self.precision_frame = ttk.Frame(notebook)
        notebook.add(self.precision_frame, text="精度评定")
        
        # 创建精度评定页面的布局框架
        precision_main = ttk.Frame(self.precision_frame, padding=10)
        precision_main.pack(fill=tk.BOTH, expand=True)
        
        # 上部统计信息区域
        stats_frame = ttk.LabelFrame(precision_main, text="平差统计信息", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 使用网格布局排列统计信息
        stats_info = [
            ("单位权中误差:", "sigma0"),
            ("自由度:", "df"),
            ("最大改正数:", "v_max"),
            ("最小改正数:", "v_min"),
            ("平均改正数:", "v_mean")
        ]
        
        for i, (label_text, key) in enumerate(stats_info):
            ttk.Label(stats_frame, text=label_text, width=15).grid(row=i//2, column=(i%2)*2, sticky=tk.W, padx=5, pady=5)
            setattr(self, f"{key}_label", ttk.Label(stats_frame, text="", width=20, foreground="#2c3e50", font=('微软雅黑', 10, 'bold')))
            getattr(self, f"{key}_label").grid(row=i//2, column=(i%2)*2 + 1, sticky=tk.W, padx=5, pady=5)
        
        # 下部点位中误差表格区域
        errors_frame = ttk.LabelFrame(precision_main, text="点位中误差", padding=10)
        errors_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表格滚动条
        scrollbar_y = ttk.Scrollbar(errors_frame, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(errors_frame, orient=tk.HORIZONTAL)
        
        # 创建点位中误差表格
        self.errors_tree = ttk.Treeview(
            errors_frame,
            columns=("node", "error"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        
        # 设置表格列标题和宽度
        self.errors_tree.heading("node", text="点号")
        self.errors_tree.heading("error", text="中误差 (m)")
        self.errors_tree.column("node", width=100, anchor=tk.CENTER)
        self.errors_tree.column("error", width=150, anchor=tk.CENTER)
        
        # 配置滚动条
        scrollbar_y.config(command=self.errors_tree.yview)
        scrollbar_x.config(command=self.errors_tree.xview)
        
        # 布局表格和滚动条
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.errors_tree.pack(fill=tk.BOTH, expand=True)
        
        # 图形展示标签页
        self.graph_frame = ttk.Frame(notebook)
        notebook.add(self.graph_frame, text="图形展示")
        
        # 计算步骤标签页
        self.calculation_frame = ttk.Frame(notebook)
        notebook.add(self.calculation_frame, text="计算步骤")
        
        # 创建计算步骤展示区域
        self.create_calculation_view()
    
    def create_elev_treeview(self):
        # 创建滚动条
        scrollbar_y = ttk.Scrollbar(self.elev_frame, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(self.elev_frame, orient=tk.HORIZONTAL)
        
        # 创建树状视图
        self.elev_tree = ttk.Treeview(
            self.elev_frame,
            columns=("node", "elevation", "correction"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        
        # 设置列标题
        self.elev_tree.heading("node", text="点号")
        self.elev_tree.heading("elevation", text="高程 (m)")
        self.elev_tree.heading("correction", text="改正数 (m)")
        
        # 设置列宽
        self.elev_tree.column("node", width=100, anchor=tk.CENTER)
        self.elev_tree.column("elevation", width=150, anchor=tk.CENTER)
        self.elev_tree.column("correction", width=150, anchor=tk.CENTER)
        
        # 配置滚动条
        scrollbar_y.config(command=self.elev_tree.yview)
        scrollbar_x.config(command=self.elev_tree.xview)
        
        # 布局
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.elev_tree.pack(fill=tk.BOTH, expand=True)
    
    def create_calculation_view(self):
        """创建计算步骤展示区域"""
        # 创建主框架
        main_frame = ttk.Frame(self.calculation_frame, padding=5)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(main_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建文本框用于显示计算步骤
        self.calc_text = tk.Text(main_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                                font=('Consolas', 10), bg='#f8f8f8', relief=tk.FLAT)
        self.calc_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        scrollbar.config(command=self.calc_text.yview)
        
        # 设置文本框为只读
        self.calc_text.config(state=tk.DISABLED)
    
    def format_matrix(self, matrix, decimals=6):
        """将矩阵格式化为字符串，确保每行单独显示"""
        # 如果是一维数组，转换为二维
        if len(matrix.shape) == 1:
            matrix = matrix.reshape(-1, 1)
            
        # 格式化矩阵的每一行
        rows = []
        for row in matrix:
            formatted_row = [f"{x:.{decimals}f}" for x in row]
            rows.append("  ".join(formatted_row))
            
        # 返回用换行符连接的行
        return "\n".join(rows)
    
    def add_calculation_step(self, title, content):
        """添加计算步骤到展示区域"""
        self.calculation_steps.append((title, content))
        
        # 启用文本框，添加内容，再设为只读
        self.calc_text.config(state=tk.NORMAL)
        self.calc_text.insert(tk.END, f"===== {title} =====\n\n")
        self.calc_text.insert(tk.END, f"{content}\n\n")
        self.calc_text.see(tk.END)  # 滚动到最后
        self.calc_text.config(state=tk.DISABLED)
    
    def clear_calculation_steps(self):
        """清除计算步骤展示"""
        self.calculation_steps = []
        self.calc_text.config(state=tk.NORMAL)
        self.calc_text.delete(1.0, tk.END)
        self.calc_text.config(state=tk.DISABLED)
    
    def upload_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if self.file_path:
            self.file_label.config(text=f"已选择: {self.file_path.split('/')[-1]}")
            self.status_var.set("文件已加载")
            # 尝试读取文件预览
            self.data = self.read_excel_data(self.file_path)
            if self.data is not None:
                self.process_btn.config(state=tk.NORMAL)
        else:
            self.file_label.config(text="未选择文件")
    
    def read_excel_data(self, file_path):
        try:
            data = pd.read_excel(file_path)
            required_columns = ['起点', '终点', '观测高差', '路线长度']
            if not all(col in data.columns for col in required_columns):
                messagebox.showerror("错误", "Excel文件必须包含以下列：起点、终点、观测高差、路线长度")
                return None
            
            # 添加计算步骤：显示读取的数据
            self.add_calculation_step("读取观测数据", f"共读取 {len(data)} 条观测数据：\n{data.to_string()}")
            
            self.status_var.set(f"成功读取数据，共{len(data)}条记录")
            return data
        except Exception as e:
            messagebox.showerror("错误", f"读取Excel文件时出错: {e}")
            return None
    
    def build_graph(self, data):
        G = nx.DiGraph()
        for index, row in data.iterrows():
            start = row['起点']
            end = row['终点']
            obs_height_diff = row['观测高差']
            route_length = row['路线长度']
            G.add_edge(start, end, obs_height_diff=obs_height_diff, route_length=route_length)
        
        try:
            assert G.number_of_edges() == len(data), "图中边的数量与数据中的路线数量不一致"
            
            # 添加计算步骤：显示图形信息
            nodes_str = ", ".join(G.nodes())
            edges_str = "\n".join([f"{u} -> {v}: 高差={d['obs_height_diff']}, 长度={d['route_length']}" 
                                 for u, v, d in G.edges(data=True)])
            self.add_calculation_step("构建水准网图", 
                                     f"节点: {nodes_str}\n边信息:\n{edges_str}")
            
            return G
        except AssertionError as e:
            messagebox.showerror("错误", str(e))
            return None
    
    def build_error_equations(self, G, num_unknowns):
        num_edges = G.number_of_edges()
        B = np.zeros((num_edges, num_unknowns))
        l = np.zeros(num_edges)
        
        node_index = {node: idx for idx, node in enumerate(G.nodes())}
        
        for edge_idx, (u, v, data) in enumerate(G.edges(data=True)):
            start_index = node_index[u]
            end_index = node_index[v]
            B[edge_idx, start_index] = -1
            B[edge_idx, end_index] = 1
            l[edge_idx] = -data['obs_height_diff']
        
        # 添加计算步骤：显示误差方程矩阵，使用格式化函数确保分行
        node_index_str = "\n".join([f"{node}: {idx}" for node, idx in node_index.items()])
        formatted_B = self.format_matrix(B)
        formatted_l = self.format_matrix(l)
        self.add_calculation_step("误差方程系数矩阵 B", 
                                 f"节点索引:\n{node_index_str}\n\nB矩阵:\n{formatted_B}\n\n常数项向量 l:\n{formatted_l}")
        
        return B, l, node_index
    
    def build_weight_matrix(self, G):
        num_edges = G.number_of_edges()
        edge_lengths = [G[u][v]['route_length'] for u, v in G.edges()]
        # 防止路线长度为0导致除零错误
        edge_lengths = np.array([max(length, 1e-6) for length in edge_lengths])
        P = np.diag(1 / edge_lengths)
        
        # 添加计算步骤：显示权矩阵，使用格式化函数确保分行
        lengths_str = "\n".join([f"边 {i}: 长度={length:.4f}, 权={1/length:.6f}" 
                               for i, length in enumerate(edge_lengths)])
        formatted_P = self.format_matrix(P)
        self.add_calculation_step("权矩阵 P", 
                                 f"路线长度与权值:\n{lengths_str}\n\nP矩阵:\n{formatted_P}")
        
        return P
    
    def indirect_adjustment(self, B, l, P, node_index, known_node):
        # 处理已知点，从未知数中移除
        known_idx = node_index[known_node]
        num_unknowns = B.shape[1]
        
        # 创建掩码，排除已知点
        mask = np.ones(num_unknowns, dtype=bool)
        mask[known_idx] = False
        
        # 构建新的B矩阵，不含已知点
        B_adj = B[:, mask]
        num_unknowns_adj = B_adj.shape[1]
        
        # 添加计算步骤：显示调整后的系数矩阵
        formatted_B_adj = self.format_matrix(B_adj)
        self.add_calculation_step("调整后的系数矩阵 B_adj", 
                                 f"已知点: {known_node} (索引 {known_idx})\n调整后的B矩阵:\n{formatted_B_adj}")
        
        # 平差计算
        Nbb = np.dot(np.dot(B_adj.T, P), B_adj)
        
        # 添加计算步骤：显示法方程系数矩阵
        formatted_Nbb = self.format_matrix(Nbb)
        self.add_calculation_step("法方程系数矩阵 Nbb", f"Nbb = B_adj^T * P * B_adj:\n{formatted_Nbb}")
        
        # 检查矩阵是否奇异
        try:
            np.linalg.cholesky(Nbb)  # 检查正定
        except np.linalg.LinAlgError:
            # 尝试添加微小扰动解决奇异问题
            Nbb += np.eye(num_unknowns_adj) * 1e-10
            formatted_Nbb_adj = self.format_matrix(Nbb)
            self.add_calculation_step("矩阵奇异处理", 
                                     f"矩阵Nbb奇异，添加微小扰动:\n{formatted_Nbb_adj}")
        
        W = np.dot(np.dot(B_adj.T, P), l)
        formatted_W = self.format_matrix(W)
        self.add_calculation_step("法方程常数项 W", f"W = B_adj^T * P * l:\n{formatted_W}")
        
        try:
            x_hat_adj = np.linalg.solve(Nbb, W)
            formatted_x_hat = self.format_matrix(x_hat_adj)
            self.add_calculation_step("参数估值", f"x_hat = Nbb^(-1) * W:\n{formatted_x_hat}")
        except np.linalg.LinAlgError as e:
            messagebox.showerror("错误", f"平差计算失败: {str(e)}")
            return None, None, None, None, None, None
        
        # 计算完整的x_hat（包含已知点）
        x_hat = np.zeros(num_unknowns)
        x_hat[mask] = x_hat_adj
        
        # 计算改正数
        v = np.dot(B_adj, x_hat_adj) - l
        formatted_v = self.format_matrix(v)
        self.add_calculation_step("观测值改正数 v", f"v = B_adj * x_hat - l:\n{formatted_v}")
        
        # 计算单位权中误差
        n = len(l)  # 观测值数量
        t = num_unknowns_adj  # 未知数数量
        sigma0 = np.sqrt(np.dot(np.dot(v.T, P), v) / (n - t)) if (n - t) > 0 else 0
        self.add_calculation_step("单位权中误差", 
                                 f"sigma0 = sqrt((v^T * P * v) / (n - t))\n其中: v^T*P*v = {np.dot(np.dot(v.T, P), v):.6f}, n-t = {n-t}\nsigma0 = {sigma0:.6f}")
        
        # 计算未知数的协因数和中误差
        Qxx = np.linalg.inv(Nbb)
        m_x = sigma0 * np.sqrt(np.diag(Qxx))
        formatted_Qxx = self.format_matrix(Qxx)
        formatted_m_x = self.format_matrix(m_x)
        self.add_calculation_step("参数协因数与中误差", 
                                 f"Qxx = Nbb^(-1):\n{formatted_Qxx}\n\n参数中误差 m_x:\n{formatted_m_x}")
        
        return v, x_hat, sigma0, Qxx, m_x, mask
    
    def calculate_elevations(self, G, x_hat, node_index, known_elevation, known_node):
        # 计算各点高程
        node_elevations = {}
        for node, idx in node_index.items():
            if node == known_node:
                node_elevations[node] = known_elevation
            else:
                node_elevations[node] = known_elevation + x_hat[idx]
        
        # 添加计算步骤：显示高程计算结果
        elev_str = "\n".join([f"{node}: {elev:.4f} m" for node, elev in node_elevations.items()])
        self.add_calculation_step("高程计算结果", 
                                 f"已知点 {known_node} 高程: {known_elevation} m\n各点高程:\n{elev_str}")
        
        return node_elevations
    
    def calculate_precision(self, G, v, P, sigma0, Qxx, m_x, mask, node_index):
        # 计算单位权中误差
        n = len(v)
        t = sum(mask)
        df = n - t
        
        # 计算观测值改正数统计
        v_max = np.max(np.abs(v))
        v_min = np.min(np.abs(v))
        v_mean = np.mean(np.abs(v))
        
        # 计算点位中误差
        point_errors = {}
        idx = 0
        for node, node_idx in node_index.items():
            if mask[node_idx]:  # 只计算未知点
                point_errors[node] = m_x[idx]
                idx += 1
        
        # 添加计算步骤：显示精度评定结果
        stats_str = (f"自由度: {df}\n"
                    f"最大改正数: {v_max:.6f}\n"
                    f"最小改正数: {v_min:.6f}\n"
                    f"平均改正数: {v_mean:.6f}")
        errors_str = "\n".join([f"{node}: {err:.6f} m" for node, err in point_errors.items()])
        self.add_calculation_step("精度评定结果", 
                                 f"{stats_str}\n\n点位中误差:\n{errors_str}")
        
        return {
            "单位权中误差": sigma0,
            "自由度": df,
            "最大改正数": v_max,
            "最小改正数": v_min,
            "平均改正数": v_mean,
            "点位中误差": point_errors
        }
    
    def network_adjustment(self):
        # 清除之前的计算步骤
        self.clear_calculation_steps()
        
        if not self.file_path:
            messagebox.showwarning("警告", "请先上传文件")
            return
        
        # 获取已知点信息
        try:
            known_node = self.known_node_var.get().strip()
            known_elevation = float(self.known_elev_var.get())
            self.add_calculation_step("已知点信息", 
                                     f"已知点: {known_node}, 高程: {known_elevation} m")
        except ValueError:
            messagebox.showerror("错误", "已知点高程必须是数字")
            return
        
        if not known_node:
            messagebox.showerror("错误", "请输入已知点名称")
            return
        
        self.status_var.set("正在进行网平差计算...")
        self.root.update()
        
        # 读取数据
        self.data = self.read_excel_data(self.file_path)
        if self.data is None:
            self.status_var.set("计算失败")
            return
        
        # 构建图形
        self.G = self.build_graph(self.data)
        if self.G is None:
            self.status_var.set("计算失败")
            return
        
        # 检查已知点是否在图形中
        if known_node not in self.G.nodes():
            messagebox.showerror("错误", f"已知点 {known_node} 不在数据中")
            self.status_var.set("计算失败")
            return
        
        # 构建误差方程
        num_unknowns = len(self.G.nodes())
        B, l, node_index = self.build_error_equations(self.G, num_unknowns)
        
        # 构建权矩阵
        P = self.build_weight_matrix(self.G)
        
        # 间接平差
        result = self.indirect_adjustment(B, l, P, node_index, known_node)
        if result[0] is None:
            self.status_var.set("计算失败")
            return
        
        v, x_hat, sigma0, Qxx, m_x, mask = result
        
        # 计算高程
        self.elevations = self.calculate_elevations(self.G, x_hat, node_index, known_elevation, known_node)
        
        # 保存改正数信息，用于显示
        self.corrections = {}
        idx = 0
        for node, node_idx in node_index.items():
            if mask[node_idx]:  # 只计算未知点
                self.corrections[node] = x_hat[node_idx]
                idx += 1
        
        # 计算精度评定指标
        self.precision_results = self.calculate_precision(
            self.G, v, P, sigma0, Qxx, m_x, mask, node_index
        )
        
        # 显示结果
        self.display_results()
        
        self.status_var.set("网平差计算完成")
        return True
    
    def display_results(self):
        # 清空之前的结果
        for item in self.elev_tree.get_children():
            self.elev_tree.delete(item)
        
        # 插入新结果，按点号排序
        for node in sorted(self.elevations.keys()):
            elevation = self.elevations[node]
            # 已知点没有改正数
            correction = self.corrections.get(node, 0.0)
            self.elev_tree.insert("", tk.END, values=(node, f"{elevation:.4f}", f"{correction:.6f}"))
        
        # 显示精度评定结果
        if self.precision_results:
            pr = self.precision_results
            # 更新统计信息标签
            self.sigma0_label.config(text=f"{pr['单位权中误差']:.6f}")
            self.df_label.config(text=f"{pr['自由度']}")
            self.v_max_label.config(text=f"{pr['最大改正数']:.6f}")
            self.v_min_label.config(text=f"{pr['最小改正数']:.6f}")
            self.v_mean_label.config(text=f"{pr['平均改正数']:.6f}")
            
            # 清空点位中误差表格
            for item in self.errors_tree.get_children():
                self.errors_tree.delete(item)
            
            # 填充点位中误差表格
            for node in sorted(pr['点位中误差'].keys()):
                self.errors_tree.insert("", tk.END, values=(node, f"{pr['点位中误差'][node]:.6f}"))
    
    def plot_network(self):
        if self.G is None:
            messagebox.showwarning("警告", "请先执行网平差")
            return
        
        # 清空图形展示区
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # 清除之前的图形引用
        self.clear_figures()
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
        self.figures.append(fig)  # 保存图形引用
        
        # 布局
        pos = nx.spring_layout(self.G, seed=42)  # 固定布局种子，使图形可重复
        
        # 绘制节点
        nx.draw_networkx_nodes(self.G, pos, node_size=500, node_color='lightblue', ax=ax)
        
        # 绘制边
        nx.draw_networkx_edges(self.G, pos, edgelist=self.G.edges(), arrowstyle='->', ax=ax)
        
        # 绘制节点标签
        node_labels = {}
        for node in self.G.nodes():
            if self.elevations:
                node_labels[node] = f"{node}\n{self.elevations[node]:.2f}m"
            else:
                node_labels[node] = node
        
        nx.draw_networkx_labels(self.G, pos, labels=node_labels, font_size=8, ax=ax)
        
        # 绘制边标签（观测高差）
        edge_labels = {(u, v): f"{d['obs_height_diff']:.2f}m\n{L:.2f}m" 
                      for u, v, d in self.G.edges(data=True) 
                      for L in [d['route_length']]}
        
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_size=7, ax=ax)
        
        plt.title("水准网示意图")
        plt.axis('off')
        plt.tight_layout()
        
        # 在Tkinter中显示图形
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def process_network(self):
        """合并执行平差和绘图功能"""
        # 先执行平差
        success = self.network_adjustment()
        # 如果平差成功，再绘制网络图
        if success:
            self.plot_network()
    
    def clear_figures(self):
        """清除所有matplotlib图形，释放资源"""
        for fig in self.figures:
            plt.close(fig)
        self.figures = []
    
    def on_close(self):
        """窗口关闭时的处理函数"""
        self.clear_figures()  # 清除所有图形
        self.root.destroy()  # 销毁主窗口
        sys.exit()  # 确保程序完全退出

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkAdjustmentApp(root)
    root.mainloop()
