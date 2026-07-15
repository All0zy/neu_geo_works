using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace DaDiToPingMian
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            // 初始化下拉框
            comboBox1.Items.Clear(); // 清空现有项
            comboBox1.Items.AddRange(TName);
            comboBox1.SelectedIndex = 0; // 默认选择WGS-84椭球体

            // 初始化表格
            InitializeDataGridViews();
        }

        // 椭球体参数
        string[] TName = { "克拉索夫斯基椭球体", "1975年国际椭球体", "WGS-84椭球体", "2000中国大地坐标系" };
        double[] EList = { 0.006693421622966, 0.006694384999588, 0.00669437999013, 0.00669438002290 };
        double[] EAList = { 0.006738525414683, 0.006739501819473, 0.00673949674227, 0.00673949677548 };
        double[] a = { 6378245, 6378140, 6378137, 6378137 };
        double[] b = { 6356698.9017827110, 6399596.6519880105, 6399593.6258, 6399593.6259 };

        bool status = false; // 转换状态：false-大地坐标转空间直角坐标，true-空间直角坐标转大地坐标
        double[,] dataList1, dataList2; // 输入数据和结果数据

        private void comboBox1_SelectedIndexChanged(object sender, EventArgs e)
        {
            int index = comboBox1.SelectedIndex;
            if (index >= 0 && index < TName.Length)
            {
                label1.Text = $"当前选择：\n椭球：{TName[index]}\n\n椭球参数：\na={a[index]}\nb={b[index]}\ne²={EList[index]:F12}\ne'²={EAList[index]:F12}";
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            // 保存当前数据
            SaveCurrentData();

            // 切换状态
            status = !status;
            label2.Text = status ? "空间直角坐标 → 大地坐标" : "大地坐标 → 空间直角坐标";

            // 更新表格列结构（不清空数据）
            UpdateDataGridViews();

            // 重新加载数据
            LoadSavedData();

            // 确保上方表格始终为输入，下方为输出
            dataGridView1.Location = new Point(278, 49);
            dataGridView2.Location = new Point(278, 203);
        }

        private DataTable savedInputData = new DataTable();
        private DataTable savedOutputData = new DataTable();

        private void SaveCurrentData()
        {
            // 保存当前输入表格数据
            savedInputData = new DataTable();
            foreach (DataGridViewColumn col in dataGridView1.Columns)
            {
                savedInputData.Columns.Add(col.Name, typeof(string));
            }

            foreach (DataGridViewRow row in dataGridView1.Rows)
            {
                if (!row.IsNewRow)
                {
                    DataRow dataRow = savedInputData.NewRow();
                    for (int i = 0; i < row.Cells.Count; i++)
                    {
                        dataRow[i] = row.Cells[i].Value?.ToString() ?? "";
                    }
                    savedInputData.Rows.Add(dataRow);
                }
            }

            // 保存当前输出表格数据
            savedOutputData = new DataTable();
            foreach (DataGridViewColumn col in dataGridView2.Columns)
            {
                savedOutputData.Columns.Add(col.Name, typeof(string));
            }

            foreach (DataGridViewRow row in dataGridView2.Rows)
            {
                if (!row.IsNewRow)
                {
                    DataRow dataRow = savedOutputData.NewRow();
                    for (int i = 0; i < row.Cells.Count; i++)
                    {
                        dataRow[i] = row.Cells[i].Value?.ToString() ?? "";
                    }
                    savedOutputData.Rows.Add(dataRow);
                }
            }
        }

        private void LoadSavedData()
        {
            // 清空表格但保留列结构
            dataGridView1.Rows.Clear();
            dataGridView2.Rows.Clear();

            // 恢复输入表格数据
            if (savedInputData.Columns.Count > 0)
            {
                foreach (DataRow dataRow in savedInputData.Rows)
                {
                    DataGridViewRow row = new DataGridViewRow();
                    row.CreateCells(dataGridView1);

                    for (int i = 0; i < dataRow.ItemArray.Length && i < dataGridView1.Columns.Count; i++)
                    {
                        row.Cells[i].Value = dataRow[i];
                    }

                    dataGridView1.Rows.Add(row);
                }
            }

            // 恢复输出表格数据
            if (savedOutputData.Columns.Count > 0)
            {
                foreach (DataRow dataRow in savedOutputData.Rows)
                {
                    DataGridViewRow row = new DataGridViewRow();
                    row.CreateCells(dataGridView2);

                    for (int i = 0; i < dataRow.ItemArray.Length && i < dataGridView2.Columns.Count; i++)
                    {
                        row.Cells[i].Value = dataRow[i];
                    }

                    dataGridView2.Rows.Add(row);
                }
            }
        }

        private void InitializeDataGridViews()
        {
            // 清空表格列
            dataGridView1.Columns.Clear();
            dataGridView2.Columns.Clear();

            // 添加点号列
            dataGridView1.Columns.Add("PointID", "点号");
            dataGridView2.Columns.Add("PointID", "点号");

            if (status) // 空间直角坐标转大地坐标
            {
                // 配置输入表格列
                dataGridView1.Columns.Add("X", "X(m)");
                dataGridView1.Columns.Add("Y", "Y(m)");
                dataGridView1.Columns.Add("Z", "Z(m)");

                // 配置输出表格列
                dataGridView2.Columns.Add("B", "B(°)");
                dataGridView2.Columns.Add("L", "L(°)");
                dataGridView2.Columns.Add("H", "H(m)");
            }
            else // 大地坐标转空间直角坐标
            {
                // 配置输入表格列
                dataGridView1.Columns.Add("B", "B(°)");
                dataGridView1.Columns.Add("L", "L(°)");
                dataGridView1.Columns.Add("H", "H(m)");

                // 配置输出表格列
                dataGridView2.Columns.Add("X", "X(m)");
                dataGridView2.Columns.Add("Y", "Y(m)");
                dataGridView2.Columns.Add("Z", "Z(m)");
            }

            // 设置表格样式
            SetupDataGridViewStyles();
        }

        private void UpdateDataGridViews()
        {
            // 保存当前列标题
            Dictionary<int, string> inputColumnHeaders = new Dictionary<int, string>();
            Dictionary<int, string> outputColumnHeaders = new Dictionary<int, string>();

            for (int i = 0; i < dataGridView1.Columns.Count; i++)
            {
                inputColumnHeaders[i] = dataGridView1.Columns[i].HeaderText;
            }

            for (int i = 0; i < dataGridView2.Columns.Count; i++)
            {
                outputColumnHeaders[i] = dataGridView2.Columns[i].HeaderText;
            }

            // 清空表格列
            dataGridView1.Columns.Clear();
            dataGridView2.Columns.Clear();

            // 添加点号列
            dataGridView1.Columns.Add("PointID", "点号");
            dataGridView2.Columns.Add("PointID", "点号");

            if (status) // 空间直角坐标转大地坐标
            {
                // 配置输入表格列
                dataGridView1.Columns.Add("X", "X(m)");
                dataGridView1.Columns.Add("Y", "Y(m)");
                dataGridView1.Columns.Add("Z", "Z(m)");

                // 配置输出表格列
                dataGridView2.Columns.Add("B", "B(°)");
                dataGridView2.Columns.Add("L", "L(°)");
                dataGridView2.Columns.Add("H", "H(m)");
            }
            else // 大地坐标转空间直角坐标
            {
                // 配置输入表格列
                dataGridView1.Columns.Add("B", "B(°)");
                dataGridView1.Columns.Add("L", "L(°)");
                dataGridView1.Columns.Add("H", "H(m)");

                // 配置输出表格列
                dataGridView2.Columns.Add("X", "X(m)");
                dataGridView2.Columns.Add("Y", "Y(m)");
                dataGridView2.Columns.Add("Z", "Z(m)");
            }

            // 设置表格样式
            SetupDataGridViewStyles();
        }

        private void SetupDataGridViewStyles()
        {
            foreach (DataGridView grid in new[] { dataGridView1, dataGridView2 })
            {
                // 设置列宽自适应
                grid.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.AllCells;

                // 设置列样式
                foreach (DataGridViewColumn col in grid.Columns)
                {
                    col.SortMode = DataGridViewColumnSortMode.NotSortable;
                }

                // 设置单元格样式
                grid.DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;
                grid.DefaultCellStyle.Format = "F8"; // 默认8位小数
            }

            // 为输入表格设置特定格式
            if (status) // 输入为空间直角坐标
            {
                dataGridView1.Columns[1].DefaultCellStyle.Format = "F3"; // X坐标3位小数
                dataGridView1.Columns[2].DefaultCellStyle.Format = "F3"; // Y坐标3位小数
                dataGridView1.Columns[3].DefaultCellStyle.Format = "F3"; // Z坐标3位小数
            }
            else // 输入为大地坐标
            {
                dataGridView1.Columns[1].DefaultCellStyle.Format = "F8"; // B坐标8位小数
                dataGridView1.Columns[2].DefaultCellStyle.Format = "F8"; // L坐标8位小数
                dataGridView1.Columns[3].DefaultCellStyle.Format = "F3"; // H坐标3位小数
            }

            // 设置输入表格允许添加行
            dataGridView1.AllowUserToAddRows = true;
            dataGridView1.AllowUserToDeleteRows = true;

            // 设置输出表格为只读
            dataGridView2.AllowUserToAddRows = false;
            dataGridView2.AllowUserToDeleteRows = false;
            dataGridView2.ReadOnly = true;
        }

        private void button2_Click(object sender, EventArgs e)
        {
            try
            {
                // 检查是否选择了椭球体
                if (comboBox1.SelectedIndex < 0)
                {
                    MessageBox.Show("请先选择椭球体！", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                // 确保上方表格为输入
                DataGridView inputGrid = dataGridView1;

                int selectedIndex = comboBox1.SelectedIndex;
                double ea2 = EAList[selectedIndex];  // 第二偏心率平方
                double e2 = EList[selectedIndex];    // 第一偏心率平方
                double semiMajorAxis = a[selectedIndex]; // 长半轴

                // 获取实际数据行数（排除新添加的空行）
                int rows = inputGrid.Rows.Count;
                if (inputGrid.AllowUserToAddRows)
                    rows--; // 减去自动添加的空行

                if (rows <= 0)
                {
                    MessageBox.Show("请先输入数据！", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                int cols = inputGrid.Columns.Count;

                // 初始化数据数组
                dataList1 = new double[rows, cols];
                dataList2 = new double[rows, cols];

                // 从输入表格读取数据
                for (int i = 0; i < rows; i++)
                {
                    for (int j = 0; j < cols; j++)
                    {
                        if (i < inputGrid.Rows.Count && j < inputGrid.Columns.Count)
                        {
                            object cellValue = inputGrid.Rows[i].Cells[j].Value;

                            if (cellValue == null || cellValue == DBNull.Value)
                                dataList1[i, j] = 0;
                            else if (double.TryParse(cellValue.ToString(), out double result))
                                dataList1[i, j] = result;
                            else
                                dataList1[i, j] = 0;
                        }
                    }
                }

                // 进行坐标转换
                for (int i = 0; i < rows; i++)
                {
                    if (status) // 空间直角坐标 -> 大地坐标
                    {
                        double X = dataList1[i, 1];
                        double Y = dataList1[i, 2];
                        double Z = dataList1[i, 3];

                        double p = Math.Sqrt(X * X + Y * Y);

                        // 处理极点特殊情况
                        if (p < 1e-10) // 接近极点
                        {
                            dataList2[i, 0] = dataList1[i, 0]; // 点号
                            dataList2[i, 1] = Z >= 0 ? 90.0 : -90.0; // 纬度为±90°
                            dataList2[i, 2] = 0.0; // 经度设为0（极点经度无意义）
                            dataList2[i, 3] = Math.Abs(Z) - b[selectedIndex]; // 大地高
                            continue;
                        }

                        // 迭代法计算纬度B
                        double B = Math.Atan2(Z, p); // 初始值
                        double tolerance = 5e-10;   // 收敛容差（5×10⁻¹⁰）
                        double delta = 1.0;         // 迭代步长
                        int maxIterations = 10;     // 最大迭代次数
                        int iteration = 0;

                        while (delta > tolerance && iteration < maxIterations)
                        {
                            double sinB = Math.Sin(B);
                            double cosB = Math.Cos(B);

                            // 防止除零错误
                            if (Math.Abs(cosB) < 1e-10)
                                break;

                            double N = semiMajorAxis / Math.Sqrt(1 - e2 * sinB * sinB);
                            double B_next = Math.Atan2(Z, p * (1 - e2 * N / (N + Z / sinB)));
                            delta = Math.Abs(B_next - B);
                            B = B_next;
                            iteration++;
                        }

                        double L = Math.Atan2(Y, X);
                        double N_final = semiMajorAxis / Math.Sqrt(1 - e2 * Math.Pow(Math.Sin(B), 2));

                        // 防止除零错误
                        double cosB_final = Math.Cos(B);
                        if (Math.Abs(cosB_final) < 1e-10)
                            cosB_final = 1e-10; // 设置一个极小值，避免除零

                        double H = p / cosB_final - N_final;

                        // 确保结果数组索引有效
                        if (i < dataList2.GetLength(0) && 0 < dataList2.GetLength(1))
                            dataList2[i, 0] = dataList1[i, 0]; // 点号

                        if (i < dataList2.GetLength(0) && 1 < dataList2.GetLength(1))
                            dataList2[i, 1] = B * (180 / Math.PI); // 弧度转度

                        if (i < dataList2.GetLength(0) && 2 < dataList2.GetLength(1))
                            dataList2[i, 2] = L * (180 / Math.PI); // 弧度转度

                        if (i < dataList2.GetLength(0) && 3 < dataList2.GetLength(1))
                            dataList2[i, 3] = H;
                    }
                    else // 大地坐标 -> 空间直角坐标
                    {
                        double B = dataList1[i, 1] * (Math.PI / 180); // 度转弧度
                        double L = dataList1[i, 2] * (Math.PI / 180); // 度转弧度
                        double H = dataList1[i, 3];

                        double N = semiMajorAxis / Math.Sqrt(1 - e2 * Math.Pow(Math.Sin(B), 2));
                        double X = (N + H) * Math.Cos(B) * Math.Cos(L);
                        double Y = (N + H) * Math.Cos(B) * Math.Sin(L);
                        double Z = (N * (1 - e2) + H) * Math.Sin(B);

                        // 确保结果数组索引有效
                        if (i < dataList2.GetLength(0) && 0 < dataList2.GetLength(1))
                            dataList2[i, 0] = dataList1[i, 0]; // 点号

                        if (i < dataList2.GetLength(0) && 1 < dataList2.GetLength(1))
                            dataList2[i, 1] = X;

                        if (i < dataList2.GetLength(0) && 2 < dataList2.GetLength(1))
                            dataList2[i, 2] = Y;

                        if (i < dataList2.GetLength(0) && 3 < dataList2.GetLength(1))
                            dataList2[i, 3] = Z;
                    }
                }

                // 将转换结果显示在下方表格中
                dataGridView2.Rows.Clear();
                for (int i = 0; i < rows; i++)
                {
                    if (i < dataList2.GetLength(0))
                    {
                        DataGridViewRow row = new DataGridViewRow();
                        row.CreateCells(dataGridView2);

                        for (int j = 0; j < cols && j < dataList2.GetLength(1); j++)
                        {
                            // 根据数据类型设置不同的显示格式
                            if (j == 0) // 点号
                                row.Cells[j].Value = dataList2[i, j];
                            else if (j == 1 || j == 2) // 经纬度保留8位小数
                                row.Cells[j].Value = dataList2[i, j].ToString("F8");
                            else // 高度和坐标值保留3位小数
                                row.Cells[j].Value = dataList2[i, j].ToString("F3");
                        }

                        dataGridView2.Rows.Add(row);
                    }
                }

                MessageBox.Show("坐标转换完成！", "成功", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (IndexOutOfRangeException ex)
            {
                MessageBox.Show($"索引超出界限错误：{ex.Message}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                Console.WriteLine($"堆栈跟踪：{ex.StackTrace}");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"发生错误：{ex.Message}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                Console.WriteLine($"堆栈跟踪：{ex.StackTrace}");
            }
        }

        private void dataGridView2_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {
            // 单元格点击事件
        }

        private void dataGridView1_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {
            // 单元格点击事件
        }

        private void button3_Click(object sender, EventArgs e) // 清空数据按钮事件
        {
            dataGridView1.Rows.Clear();
            dataGridView2.Rows.Clear();
        }
    }
}