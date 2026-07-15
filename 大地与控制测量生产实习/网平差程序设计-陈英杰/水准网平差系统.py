import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
from scipy.linalg import inv


class LevelingNetworkAdjustment:
    def __init__(self, root):
        self.root = root
        self.root.title("水准网平差系统")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")

        self.files_data = {}
        self.points = {}
        self.observations = []
        self.adj_results = {}

        self.create_widgets()

    def create_widgets(self):
        # 主框架
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 标题
        title_label = tk.Label(main_frame, text="水准网平差系统",
                               font=("Arial", 16, "bold"), bg="#f0f0f0")
        title_label.pack(pady=(0, 10))

        # 文件导入区域
        file_frame = tk.LabelFrame(main_frame, text="数据文件导入",
                                   font=("Arial", 12, "bold"), bg="#f0f0f0")
        file_frame.pack(fill=tk.X, pady=5)

        # 文件列表和按钮框架
        list_button_frame = tk.Frame(file_frame, bg="#f0f0f0")
        list_button_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 文件列表
        list_frame = tk.Frame(list_button_frame, bg="#f0f0f0")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(list_frame, text="已导入的文件:", bg="#f0f0f0",
                 font=("Arial", 10)).pack(anchor=tk.W)

        self.file_listbox = tk.Listbox(list_frame, height=8, width=60,
                                       selectbackground="#4CAF50", selectmode=tk.SINGLE)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                 command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)

        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 按钮框架
        button_frame = tk.Frame(list_button_frame, bg="#f0f0f0")
        button_frame.pack(side=tk.RIGHT, padx=(10, 0))

        tk.Button(button_frame, text="添加文件", command=self.add_files,
                  width=15, bg="#4CAF50", fg="white").pack(pady=5)
        tk.Button(button_frame, text="移除选中", command=self.remove_file,
                  width=15, bg="#f44336", fg="white").pack(pady=5)
        tk.Button(button_frame, text="清空列表", command=self.clear_files,
                  width=15, bg="#FF9800", fg="white").pack(pady=5)

        # 控制按钮区域
        control_frame = tk.Frame(main_frame, bg="#f0f0f0")
        control_frame.pack(fill=tk.X, pady=10)

        tk.Button(control_frame, text="进行平差计算", command=self.perform_adjustment,
                  bg="#2196F3", fg="white", font=("Arial", 12), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="显示平差结果", command=self.show_results,
                  bg="#9C27B0", fg="white", font=("Arial", 12), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="导出结果", command=self.export_results,
                  bg="#607D8B", fg="white", font=("Arial", 12), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="关于", command=self.show_about,
                  bg="#795548", fg="white", font=("Arial", 12), width=15).pack(side=tk.RIGHT, padx=5)

        # 结果显示区域
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # 平差结果标签
        self.results_frame = tk.Frame(notebook, bg="#f0f0f0")
        notebook.add(self.results_frame, text="平差结果")

        # 创建结果文本和滚动条
        text_frame = tk.Frame(self.results_frame, bg="#f0f0f0")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.results_text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 统计信息标签
        self.stats_frame = tk.Frame(notebook, bg="#f0f0f0")
        notebook.add(self.stats_frame, text="统计信息")

        # 创建统计信息文本
        stats_text_frame = tk.Frame(self.stats_frame, bg="#f0f0f0")
        stats_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.stats_text = tk.Text(stats_text_frame, wrap=tk.WORD, font=("Consolas", 10))
        stats_scrollbar = tk.Scrollbar(stats_text_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)

        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 详细计算标签
        self.details_frame = tk.Frame(notebook, bg="#f0f0f0")
        notebook.add(self.details_frame, text="详细计算")

        # 创建详细计算文本
        details_text_frame = tk.Frame(self.details_frame, bg="#f0f0f0")
        details_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.details_text = tk.Text(details_text_frame, wrap=tk.WORD, font=("Consolas", 9))
        details_scrollbar = tk.Scrollbar(details_text_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)

        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="选择水准测量数据文件",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        for file in files:
            if file not in self.files_data:
                try:
                    # 尝试读取CSV文件
                    df = pd.read_csv(file, encoding='utf-8')
                    self.files_data[file] = df
                    # 只显示文件名，不显示完整路径
                    file_name = file.split('/')[-1]
                    self.file_listbox.insert(tk.END, file_name)
                except Exception as e:
                    messagebox.showerror("错误", f"读取文件 {file} 时出错: {str(e)}")

    def remove_file(self):
        selection = self.file_listbox.curselection()
        if selection:
            file_index = selection[0]
            # 获取完整路径
            file_name = self.file_listbox.get(file_index)
            full_path = None
            for path in self.files_data:
                if path.endswith(file_name):
                    full_path = path
                    break

            if full_path:
                self.file_listbox.delete(file_index)
                del self.files_data[full_path]

    def clear_files(self):
        self.file_listbox.delete(0, tk.END)
        self.files_data.clear()

    def parse_data(self):
        self.points = {}
        self.observations = []

        # 已知点高程（根据您提供的数据）
        known_points = {
            'K1': 500.0,
            # 其他点的高程将在平差中确定
        }

        # 初始化点
        for point in known_points:
            self.points[point] = {'elevation': known_points[point], 'fixed': True}

        for file_path, df in self.files_data.items():
            # 查找备注列和高差列
            remark_col = None
            diff_col = None

            for col in df.columns:
                if '备注' in col:
                    remark_col = col
                if '累计高差' in col or '高差' in col:
                    diff_col = col

            if remark_col is None or diff_col is None:
                continue

            # 提取有效数据行
            for _, row in df.iterrows():
                if pd.isna(row[remark_col]):
                    continue

                remark = str(row[remark_col])
                if '至' in remark:
                    parts = remark.split('至')
                    if len(parts) == 2:
                        from_point, to_point = parts
                        # 清理点名称
                        from_point = from_point.strip()
                        to_point = to_point.strip()

                        # 提取点编号（如K1, K2等）
                        from_match = re.search(r'K\d+', from_point)
                        to_match = re.search(r'K\d+', to_point)

                        if from_match and to_match:
                            from_point = from_match.group()
                            to_point = to_match.group()

                            # 记录点
                            if from_point not in self.points:
                                self.points[from_point] = {'elevation': None, 'fixed': False}
                            if to_point not in self.points:
                                self.points[to_point] = {'elevation': None, 'fixed': False}

                            # 记录观测值
                            try:
                                diff = float(row[diff_col])
                                self.observations.append({
                                    'from': from_point,
                                    'to': to_point,
                                    'difference': diff,
                                    'file': file_path.split('/')[-1]  # 只存储文件名
                                })
                            except (ValueError, TypeError):
                                pass

    def perform_adjustment(self):
        if not self.files_data:
            messagebox.showwarning("警告", "请先导入数据文件")
            return

        try:
            self.parse_data()

            # 构建误差方程和法方程
            # 确定未知点数量
            unknown_points = [p for p in self.points if not self.points[p]['fixed']]
            n_unknown = len(unknown_points)

            if n_unknown == 0:
                messagebox.showinfo("信息", "没有需要平差的未知点")
                return

            # 构建设计矩阵A和观测向量L
            n_obs = len(self.observations)
            A = np.zeros((n_obs, n_unknown))
            L = np.zeros(n_obs)
            P = np.eye(n_obs)  # 权矩阵，这里简化为单位矩阵

            # 点名称到索引的映射
            point_to_index = {point: idx for idx, point in enumerate(unknown_points)}

            for i, obs in enumerate(self.observations):
                from_point = obs['from']
                to_point = obs['to']
                diff = obs['difference']

                # 计算观测值
                if self.points[from_point]['fixed']:
                    # 从已知点到未知点
                    if to_point in unknown_points:
                        j = point_to_index[to_point]
                        A[i, j] = 1
                        L[i] = diff + self.points[from_point]['elevation']
                elif self.points[to_point]['fixed']:
                    # 从未知点到已知点
                    if from_point in unknown_points:
                        j = point_to_index[from_point]
                        A[i, j] = -1
                        L[i] = diff - self.points[to_point]['elevation']
                else:
                    # 两个都是未知点
                    if from_point in unknown_points and to_point in unknown_points:
                        j_from = point_to_index[from_point]
                        j_to = point_to_index[to_point]
                        A[i, j_from] = -1
                        A[i, j_to] = 1
                        L[i] = diff

            # 解法方程: (A^T P A) x = A^T P L
            N = A.T @ P @ A
            t = A.T @ P @ L

            # 检查N是否可逆
            if np.linalg.det(N) == 0:
                messagebox.showerror("错误", "法方程系数矩阵奇异，无法求解")
                return

            x = np.linalg.solve(N, t)

            # 更新点的高程
            for point, idx in point_to_index.items():
                self.points[point]['elevation'] = x[idx]

            # 计算残差
            V = A @ x - L
            sigma0 = np.sqrt((V.T @ P @ V) / (n_obs - n_unknown))

            # 计算协因数矩阵
            Qxx = inv(N)

            # 计算点的高程中误差
            point_errors = {}
            for point, idx in point_to_index.items():
                point_errors[point] = sigma0 * np.sqrt(Qxx[idx, idx])

            # 存储平差结果
            self.adj_results = {
                'points': self.points,
                'residuals': V,
                'sigma0': sigma0,
                'unknown_points': unknown_points,
                'point_errors': point_errors,
                'Qxx': Qxx,
                'n_obs': n_obs,
                'n_unknown': n_unknown,
                'A': A,
                'L': L,
                'N': N,
                't': t,
                'x': x
            }

            messagebox.showinfo("成功", "平差计算完成")

        except Exception as e:
            messagebox.showerror("错误", f"平差计算过程中出错: {str(e)}")

    def show_results(self):
        if not self.adj_results:
            messagebox.showwarning("警告", "请先进行平差计算")
            return

        self.results_text.delete(1.0, tk.END)
        self.stats_text.delete(1.0, tk.END)
        self.details_text.delete(1.0, tk.END)

        # 显示点的高程
        self.results_text.insert(tk.END, "水准点高程平差结果:\n")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")

        for point, data in self.adj_results['points'].items():
            fixed_str = " (已知点)" if data['fixed'] else ""
            error_str = f" ± {self.adj_results['point_errors'].get(point, 0):.6f} m" if not data['fixed'] else ""
            self.results_text.insert(tk.END, f"{point}: {data['elevation']:.6f} m{error_str}{fixed_str}\n")

        # 显示单位权中误差
        self.results_text.insert(tk.END, f"\n单位权中误差: {self.adj_results['sigma0']:.6f} m\n")

        # 显示观测值残差
        self.results_text.insert(tk.END, "\n观测值残差:\n")
        self.results_text.insert(tk.END, "-" * 80 + "\n")

        for i, obs in enumerate(self.observations):
            residual = self.adj_results['residuals'][i]
            self.results_text.insert(tk.END,
                                     f"{obs['from']} -> {obs['to']}: {residual:8.6f} m (观测高差: {obs['difference']:8.6f} m) [来自: {obs['file']}]\n")

        # 显示统计信息
        self.stats_text.insert(tk.END, "平差统计信息:\n")
        self.stats_text.insert(tk.END, "=" * 60 + "\n\n")
        self.stats_text.insert(tk.END, f"观测值总数: {self.adj_results['n_obs']}\n")
        self.stats_text.insert(tk.END, f"未知点数量: {self.adj_results['n_unknown']}\n")
        self.stats_text.insert(tk.END, f"自由度: {self.adj_results['n_obs'] - self.adj_results['n_unknown']}\n")
        self.stats_text.insert(tk.END, f"单位权中误差: {self.adj_results['sigma0']:.6f} m\n\n")

        # 显示残差统计
        residuals = self.adj_results['residuals']
        self.stats_text.insert(tk.END, f"残差最大值: {np.max(np.abs(residuals)):.6f} m\n")
        self.stats_text.insert(tk.END, f"残差最小值: {np.min(np.abs(residuals)):.6f} m\n")
        self.stats_text.insert(tk.END, f"残差平均值: {np.mean(residuals):.6f} m\n")
        self.stats_text.insert(tk.END, f"残差标准差: {np.std(residuals):.6f} m\n\n")

        # 显示点的高程精度
        self.stats_text.insert(tk.END, "点的高程精度:\n")
        self.stats_text.insert(tk.END, "-" * 40 + "\n")
        for point, error in self.adj_results['point_errors'].items():
            self.stats_text.insert(tk.END, f"{point}: ±{error:.6f} m\n")

        # 显示详细计算信息
        self.details_text.insert(tk.END, "平差详细计算过程:\n")
        self.details_text.insert(tk.END, "=" * 60 + "\n\n")

        # 显示设计矩阵A
        self.details_text.insert(tk.END, "设计矩阵 A:\n")
        self.details_text.insert(tk.END, "-" * 40 + "\n")
        np.set_printoptions(precision=6, suppress=True, linewidth=120)
        self.details_text.insert(tk.END, f"{self.adj_results['A']}\n\n")

        # 显示观测向量L
        self.details_text.insert(tk.END, "观测向量 L:\n")
        self.details_text.insert(tk.END, "-" * 40 + "\n")
        self.details_text.insert(tk.END, f"{self.adj_results['L']}\n\n")

        # 显示法方程矩阵N
        self.details_text.insert(tk.END, "法方程矩阵 N:\n")
        self.details_text.insert(tk.END, "-" * 40 + "\n")
        self.details_text.insert(tk.END, f"{self.adj_results['N']}\n\n")

        # 显示法方程常数项t
        self.details_text.insert(tk.END, "法方程常数项 t:\n")
        self.details_text.insert(tk.END, "-" * 40 + "\n")
        self.details_text.insert(tk.END, f"{self.adj_results['t']}\n\n")

        # 显示未知数解x
        self.details_text.insert(tk.END, "未知数解 x:\n")
        self.details_text.insert(tk.END, "-" * 40 + "\n")
        self.details_text.insert(tk.END, f"{self.adj_results['x']}\n\n")

        # 显示残差向量V
        self.details_text.insert(tk.END, "残差向量 V:\n")
        self.details_text.insert(tk.END, "-" * 40 + "\n")
        self.details_text.insert(tk.END, f"{self.adj_results['residuals']}\n\n")

        # 显示协因数矩阵Qxx
        self.details_text.insert(tk.END, "协因数矩阵 Qxx:\n")
        self.details_text.insert(tk.END, "-" * 40 + "\n")
        self.details_text.insert(tk.END, f"{self.adj_results['Qxx']}\n\n")

        # 显示法方程矩阵的条件数
        cond_num = np.linalg.cond(self.adj_results['N'])
        self.details_text.insert(tk.END, f"法方程矩阵条件数: {cond_num:.6f}\n")

        # 显示法方程矩阵的行列式值
        det_n = np.linalg.det(self.adj_results['N'])
        self.details_text.insert(tk.END, f"法方程矩阵行列式值: {det_n:.6e}\n")

    def export_results(self):
        if not self.adj_results:
            messagebox.showwarning("警告", "没有可导出的结果")
            return

        file_path = filedialog.asksaveasfilename(
            title="导出平差结果",
            defaultextension=".txt",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("水准网平差结果\n")
                    f.write("=" * 60 + "\n\n")

                    f.write("水准点高程平差结果:\n\n")
                    for point, data in self.adj_results['points'].items():
                        fixed_str = " (已知点)" if data['fixed'] else ""
                        error_str = f" ± {self.adj_results['point_errors'].get(point, 0):.6f} m" if not data[
                            'fixed'] else ""
                        f.write(f"{point}: {data['elevation']:.6f} m{error_str}{fixed_str}\n")

                    f.write(f"\n单位权中误差: {self.adj_results['sigma0']:.6f} m\n")

                    f.write("\n观测值残差:\n")
                    f.write("-" * 80 + "\n")
                    for i, obs in enumerate(self.observations):
                        residual = self.adj_results['residuals'][i]
                        f.write(
                            f"{obs['from']} -> {obs['to']}: {residual:8.6f} m (观测高差: {obs['difference']:8.6f} m) [来自: {obs['file']}]\n")

                    f.write("\n平差统计信息:\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"观测值总数: {self.adj_results['n_obs']}\n")
                    f.write(f"未知点数量: {self.adj_results['n_unknown']}\n")
                    f.write(f"自由度: {self.adj_results['n_obs'] - self.adj_results['n_unknown']}\n")
                    f.write(f"单位权中误差: {self.adj_results['sigma0']:.6f} m\n\n")

                    residuals = self.adj_results['residuals']
                    f.write(f"残差最大值: {np.max(np.abs(residuals)):.6f} m\n")
                    f.write(f"残差最小值: {np.min(np.abs(residuals)):.6f} m\n")
                    f.write(f"残差平均值: {np.mean(residuals):.6f} m\n")
                    f.write(f"残差标准差: {np.std(residuals):.6f} m\n\n")

                    f.write("点的高程精度:\n")
                    f.write("-" * 40 + "\n")
                    for point, error in self.adj_results['point_errors'].items():
                        f.write(f"{point}: ±{error:.6f} m\n")

                    f.write("\n平差详细计算过程:\n")
                    f.write("=" * 60 + "\n\n")

                    # 导出详细计算信息
                    f.write("设计矩阵 A:\n")
                    f.write("-" * 40 + "\n")
                    np.set_printoptions(precision=6, suppress=True, linewidth=120)
                    f.write(f"{self.adj_results['A']}\n\n")

                    f.write("观测向量 L:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"{self.adj_results['L']}\n\n")

                    f.write("法方程矩阵 N:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"{self.adj_results['N']}\n\n")

                    f.write("法方程常数项 t:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"{self.adj_results['t']}\n\n")

                    f.write("未知数解 x:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"{self.adj_results['x']}\n\n")

                    f.write("残差向量 V:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"{self.adj_results['residuals']}\n\n")

                    f.write("协因数矩阵 Qxx:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"{self.adj_results['Qxx']}\n\n")

                    cond_num = np.linalg.cond(self.adj_results['N'])
                    f.write(f"法方程矩阵条件数: {cond_num:.6f}\n")

                    det_n = np.linalg.det(self.adj_results['N'])
                    f.write(f"法方程矩阵行列式值: {det_n:.6e}\n")

                messagebox.showinfo("成功", f"结果已导出到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出结果时出错: {str(e)}")

    def show_about(self):
        about_text = """
        水准网平差系统

        功能：
        1. 导入多个水准测量数据文件
        2. 进行最小二乘平差计算
        3. 显示平差后的点高程和精度
        4. 显示观测值残差和统计信息
        5. 显示详细计算过程
        6. 导出平差结果

        使用方法：
        1. 点击"添加文件"导入CSV数据文件
        2. 点击"进行平差计算"执行平差
        3. 查看各个标签页中的结果

        注意：本程序假设K1为已知点，高程为500.0米
        """
        messagebox.showinfo("关于", about_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = LevelingNetworkAdjustment(root)
    root.mainloop()