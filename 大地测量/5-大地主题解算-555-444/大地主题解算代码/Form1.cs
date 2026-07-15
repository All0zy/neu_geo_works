using System;
using System.Windows.Forms;

namespace GaussGeodeticCalculator
{
    public partial class MainForm : Form
    {
        // 椭球体参数
        private double a = 6378137;         // 椭圆长半轴
        private double b = 6356752.3142;    // 椭圆短半轴
        private double e_2 = 0.00669437999013;  // 第一偏心率e^2
        private double e_dot_2 = 0.00673949674227; // 第二偏心率e'^2
        private const double rou = 206264.806247096355; // 弧度到秒的转换常数

        public MainForm()
        {
            InitializeComponent();
            // 预选择WGS-84椭球体
            radioButtonWGS84.Checked = true;
            // 填充算例数据
            FillExampleData();
        }

        private void Ellipsoid_RadioButton_CheckedChanged(object sender, EventArgs e)
        {
            RadioButton rb = (RadioButton)sender;
            switch (rb.Text)
            {
                case "克拉索夫斯基椭球":
                    a = 6378245;
                    b = 6356863.0187730473;
                    e_2 = 0.006693421622966;
                    e_dot_2 = 0.006738525414683;
                    break;
                case "1975年国际椭球体":
                    a = 6378140;
                    b = 6356755.2881575287;
                    e_2 = 0.006694384999588;
                    e_dot_2 = 0.006739501819473;
                    break;
                case "WGS-84椭球体":
                    a = 6378137;
                    b = 6356752.3142;
                    e_2 = 0.00669437999013;
                    e_dot_2 = 0.00673949674227;
                    break;
                case "2000中国大地坐标系":
                    a = 6378137;
                    b = 6356752.3141;
                    e_2 = 0.00669438002290;
                    e_dot_2 = 0.00673949677548;
                    break;
            }
        }

        private void ForwardCalculation()
        {
            try
            {
                // 输入验证
                if (!ValidateInput(tb正算起点纬度度, tb正算起点纬度分, tb正算起点纬度秒,
                                   tb正算起点经度度, tb正算起点经度分, tb正算起点经度秒,
                                   tb正算方位角度, tb正算方位角分, tb正算方位角秒,
                                   tb正算大地线长))
                    return;

                // 转换输入为弧度
                double B1 = ConvertToRadians(tb正算起点纬度度.Text, tb正算起点纬度分.Text, tb正算起点纬度秒.Text);
                double L1 = ConvertToRadians(tb正算起点经度度.Text, tb正算起点经度分.Text, tb正算起点经度秒.Text);
                double A1 = ConvertToRadians(tb正算方位角度.Text, tb正算方位角分.Text, tb正算方位角秒.Text);
                double S = Convert.ToDouble(tb正算大地线长.Text);

                double c = a * a / b;
                double W = Math.Sqrt(1 - e_2 * Math.Sin(B1) * Math.Sin(B1));
                double V = Math.Sqrt(1 + e_dot_2 * Math.Cos(B1) * Math.Cos(B1));
                double M1 = a * (1 - e_2) / (W * W * W);
                double N1 = a / W;
                double t1 = Math.Tan(B1);

                // 初始迭代值
                double delta_B = V * V / N1 * rou * S * Math.Cos(A1);
                double delta_L = rou / N1 * S / Math.Cos(B1) * Math.Sin(A1);
                double delta_A = rou / N1 * S * Math.Sin(A1) * t1;

                double Bm = B1 + delta_B / rou / 2;
                double Am = A1 + delta_A / rou / 2;
                double tm = Math.Tan(Bm);
                double nm = e_dot_2 * Math.Cos(Bm) * Math.Cos(Bm);
                double Wm = Math.Sqrt(1 - e_2 * Math.Sin(Bm) * Math.Sin(Bm));
                double Vm = Math.Sqrt(1 + e_dot_2 * Math.Cos(Bm) * Math.Cos(Bm));
                double Mm = a * (1 - e_2) / (Wm * Wm * Wm);
                double Nm = a / Wm;

                double chB, chL, chA;
                do
                {
                    chB = delta_B;
                    chL = delta_L;
                    chA = delta_A;

                    delta_B = Vm * Vm / Nm * rou * S * Math.Cos(Am) *
                        (1 + S * S / 24 / Nm / Nm * (Math.Pow(2 + 3 * tm * tm + 3 * Math.Pow(nm * tm, 2), 2)) + 3 *
                        nm * nm * Math.Cos(Am) * (tm * tm - 1 - nm * nm - 4 * tm * tm * nm * nm));

                    delta_L = rou / Nm * S / Math.Cos(Bm) * Math.Sin(Am) *
                        (1 + S * S / 24 / Nm / Nm * (Math.Sin(Am) * Math.Sin(Am) * tm * tm - Math.Cos(Am) * Math.Cos(Am) *
                        (1 + nm * nm - 9 * tm * tm * nm * nm + Math.Pow(nm, 4))));

                    delta_A = rou / Nm * S * Math.Sin(Am) * tm *
                        (1 + S * S / 24 / Nm / Nm * (Math.Cos(Am) * Math.Cos(Am) * (2 + 7 * nm * nm + 9 * tm * tm * nm * nm + 5 * Math.Pow(nm, 4))
                        + Math.Sin(Am) * Math.Sin(Am) * (2 + tm * tm + 2 * nm * nm)));

                    Bm = B1 + delta_B / rou / 2;
                    Am = A1 + delta_A / rou / 2;
                    Wm = Math.Sqrt(1 - e_2 * Math.Sin(Bm) * Math.Sin(Bm));
                    Vm = Math.Sqrt(1 + e_dot_2 * Math.Cos(Bm) * Math.Cos(Bm));
                    Mm = a * (1 - e_2) / (Wm * Wm * Wm);
                    Nm = a / Wm;
                    tm = Math.Tan(Bm);
                    nm = e_dot_2 * Math.Cos(Bm) * Math.Cos(Bm);
                } while (Math.Abs(chB - delta_B) > 1e-4 || Math.Abs(chA - delta_A) > 1e-4 || Math.Abs(chL - delta_L) > 1e-4);

                double B2 = (B1 + delta_B / rou) * 180 / Math.PI;
                double L2 = (L1 + delta_L / rou) * 180 / Math.PI;
                double A21 = (A1 + delta_A / rou) * 180 / Math.PI;

                if (A1 > 180)
                    A21 = A21 + 180;
                else
                    A21 = A21 - 180;

                if (A21 < 0)
                    A21 += 360;

                // 转换为度分秒并显示
                ConvertToDMS(B2, tb正算终点纬度度, tb正算终点纬度分, tb正算终点纬度秒);
                ConvertToDMS(L2, tb正算终点经度度, tb正算终点经度分, tb正算终点经度秒);
                ConvertToDMS(A21, tb正算反方位角度, tb正算反方位角分, tb正算反方位角秒);
            }
            catch (Exception ex)
            {
                MessageBox.Show("正算错误: " + ex.Message, "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void InverseCalculation()
        {
            try
            {
                // 输入验证
                if (!ValidateInput(tb反算起点纬度度, tb反算起点纬度分, tb反算起点纬度秒,
                                   tb反算起点经度度, tb反算起点经度分, tb反算起点经度秒,
                                   tb反算终点纬度度, tb反算终点纬度分, tb反算终点纬度秒,
                                   tb反算终点经度度, tb反算终点经度分, tb反算终点经度秒))
                    return;

                // 转换输入为弧度
                double B1 = ConvertToRadians(tb反算起点纬度度.Text, tb反算起点纬度分.Text, tb反算起点纬度秒.Text);
                double L1 = ConvertToRadians(tb反算起点经度度.Text, tb反算起点经度分.Text, tb反算起点经度秒.Text);
                double B2 = ConvertToRadians(tb反算终点纬度度.Text, tb反算终点纬度分.Text, tb反算终点纬度秒.Text);
                double L2 = ConvertToRadians(tb反算终点经度度.Text, tb反算终点经度分.Text, tb反算终点经度秒.Text);

                double Bm = (B1 + B2) / 2;
                double Lm = (L1 + L2) / 2;
                double tm = Math.Tan(Bm);
                double nm = e_dot_2 * Math.Cos(Bm) * Math.Cos(Bm);
                double Wm = Math.Sqrt(1 - e_2 * Math.Sin(Bm) * Math.Sin(Bm));
                double Vm = Math.Sqrt(1 + e_dot_2 * Math.Cos(Bm) * Math.Cos(Bm));
                double Mm = a * (1 - e_2) / (Wm * Wm * Wm);
                double Nm = a / Wm;

                double r01 = Nm / rou * Math.Cos(Bm);
                double r21 = Nm * Math.Cos(Bm) / 24 / Math.Pow(Vm, 4) / Math.Pow(rou, 3) * (1 + nm * nm - 9 * Math.Pow(nm * tm * nm * nm, 2));
                double r03 = -Nm / 24 / Math.Pow(rou, 3) * Math.Pow(Math.Cos(Bm), 3) * tm * tm;
                double S10 = Nm / rou / Vm / Vm;
                double S12 = Nm * Math.Cos(Bm) * Math.Cos(Bm) / 24 / Math.Pow(Vm, 2) / Math.Pow(rou, 3) * (2 + 3 * tm * tm + 2 * nm * nm);
                double S30 = Nm / 8 / Math.Pow(rou, 3) / Math.Pow(Vm, 6) * (nm * nm - tm * tm * nm * nm);

                double delta_B = (B2 - B1) * rou;
                double delta_L = (L2 - L1) * rou;

                double SsinAm = r01 * delta_L + r21 * delta_B * delta_B * delta_L + r03 * Math.Pow(delta_L, 3);
                double ScosAm = S10 * delta_B + S12 * delta_B * delta_L * delta_L + S30 * Math.Pow(delta_B, 3);
                double t01 = tm * Math.Cos(Bm);
                double t21 = Math.Cos(Bm) * tm * (2 + 7 * nm * nm + 9 * tm * tm * nm * nm + 5 * Math.Pow(nm, 4)) / 24 / rou / rou / Math.Pow(Vm, 4);
                double t03 = Math.Pow(Math.Cos(Bm), 3) * tm * (2 + tm * tm + 2 * nm * nm) / 24 / rou / rou;

                double delta_A = t01 * delta_L + t21 * delta_B * delta_B * delta_L + t03 * Math.Pow(delta_L, 3);
                double Am = Math.Atan(SsinAm / ScosAm);

                if (Am < 0)
                    Am = Am + 2 * Math.PI;

                double A1 = Am - delta_A / 2 / rou;
                double A21 = Am + delta_A / 2 / rou;

                if (A1 > Math.PI)
                    A21 = A21 - Math.PI;
                if (A1 < Math.PI)
                    A21 = A21 + Math.PI;

                double S = ScosAm / Math.Cos(Am);

                // 转换为度分秒并显示
                tb反算大地线长.Text = S.ToString("F4");
                ConvertToDMS(A1 * 180 / Math.PI, tb反算正方位角度, tb反算正方位角分, tb反算正方位角秒);
                ConvertToDMS(A21 * 180 / Math.PI, tb反算反方位角度, tb反算反方位角分, tb反算反方位角秒);
            }
            catch (Exception ex)
            {
                MessageBox.Show("反算错误: " + ex.Message, "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private double ConvertToRadians(string d, string m, string s)
        {
            double degree = Convert.ToDouble(d);
            double minute = Convert.ToDouble(m);
            double second = Convert.ToDouble(s);
            return (degree + minute / 60 + second / 3600) * Math.PI / 180;
        }

        private void ConvertToDMS(double angle, TextBox tbD, TextBox tbM, TextBox tbS)
        {
            double d = Math.Floor(angle);
            double m = Math.Floor((angle - d) * 60);
            double s = ((angle - d) * 60 - m) * 60;

            tbD.Text = d.ToString("F0");
            tbM.Text = m.ToString("F0");
            tbS.Text = s.ToString("F4");
        }

        private bool ValidateInput(params TextBox[] textBoxes)
        {
            foreach (TextBox tb in textBoxes)
            {
                if (string.IsNullOrEmpty(tb.Text) || !double.TryParse(tb.Text, out double result))
                {
                    MessageBox.Show("请输入有效的数字", "输入错误", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    tb.Focus();
                    return false;
                }
            }
            return true;
        }

        private void FillExampleData()
        {
            // 正算算例数据
            tb正算起点纬度度.Text = "47";
            tb正算起点纬度分.Text = "46";
            tb正算起点纬度秒.Text = "52.6470";
            tb正算起点经度度.Text = "35";
            tb正算起点经度分.Text = "49";
            tb正算起点经度秒.Text = "36.3300";
            tb正算方位角度.Text = "44";
            tb正算方位角分.Text = "12";
            tb正算方位角秒.Text = "13.664";
            tb正算大地线长.Text = "44797.2826";

            // 反算算例数据
            tb反算起点纬度度.Text = "47";
            tb反算起点纬度分.Text = "46";
            tb反算起点纬度秒.Text = "52.6470";
            tb反算起点经度度.Text = "35";
            tb反算起点经度分.Text = "49";
            tb反算起点经度秒.Text = "36.3300";
            tb反算终点纬度度.Text = "48";
            tb反算终点纬度分.Text = "04";
            tb反算终点纬度秒.Text = "09.6384";
            tb反算终点经度度.Text = "36";
            tb反算终点经度分.Text = "14";
            tb反算终点经度秒.Text = "45.0505";
        }

        private void btn正算_Click(object sender, EventArgs e)
        {
            ForwardCalculation();
        }

        private void btn反算_Click(object sender, EventArgs e)
        {
            InverseCalculation();
        }

        private void groupBox1_Enter(object sender, EventArgs e)
        {

        }

        private void groupBox3_Enter(object sender, EventArgs e)
        {

        }

        private void MainForm_Load(object sender, EventArgs e)
        {

        }
    }
}