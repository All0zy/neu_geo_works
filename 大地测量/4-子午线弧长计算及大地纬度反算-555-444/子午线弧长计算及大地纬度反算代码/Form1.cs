using System;
using System.Windows.Forms;
using System.Globalization;
using System.Drawing;

namespace GeodeticMeridianCalculation
{
    public partial class Form1 : Form
    {
        // 椭球参数（北京54坐标系）
        private const double A = 6378245;
        private const double Alpha = 1 / 298.3;
        private readonly double E2 = (2 * Alpha - Alpha * Alpha) / (1 + Alpha);
        private const double A0 = 111134.861;
        private const double C = 6367588.4969;
        private const double Epsilon = 1e-10;

        public Form1()
        {
            InitializeComponent();
            SetExampleValues();
        }

        private void SetExampleValues()
        {
            txtB1.Text = "30";    // P1纬度
            txtL1.Text = "181°45'36\"";    // P1经度（仅显示）
            txtB2.Text = "30.5";  // P2纬度
            txtL2.Text = "181°45'36\"";  // P2经度（仅显示）
        }

        private void btnCalculate_Click(object sender, EventArgs e)
        {
            try
            {
                // 解析输入
                double b1 = ParseCoordinate(txtB1.Text, "纬度P1");
                double b2 = ParseCoordinate(txtB2.Text, "纬度P2");

                // 第一部分：赤道到点的弧长
                string part1 = GetPart1Result(b1, b2);

                // 第二部分：反算纬度（直接法/间接法）
                string part2 = GetPart2Result(b1, b2);

                // 第三部分：两点间弧长及纬度差
                string part3 = GetPart3Result(b1, b2);

                // 分区块显示结果
                rtbResult.Clear();
                ShowSection("一、赤道到点的子午线弧长", part1, Color.Teal);
                ShowSection("二、由弧长反算大地纬度", part2, Color.Navy);
                ShowSection("三、两点间子午线弧长与纬度差", part3, Color.Maroon);
            }
            catch (Exception ex)
            {
                rtbResult.ForeColor = Color.Red;
                rtbResult.Text = $"错误：{ex.Message}";
            }
        }

        // 第一部分：赤道到点的弧长
        private string GetPart1Result(double b1, double b2)
        {
            double x1 = CalculateMeridianArcLength(b1);
            double x2 = CalculateMeridianArcLength(b2);
            return $@"P1（B={b1:F4}°）: {x1:F3} m
P2（B={b2:F4}°）: {x2:F3} m";
        }

        // 第二部分：反算纬度
        private string GetPart2Result(double b1, double b2)
        {
            double x1 = CalculateMeridianArcLength(b1);
            double x2 = CalculateMeridianArcLength(b2);

            // 直接法（迭代法）
            double directB1 = InverseLatitudeDirect(x1);
            double directB2 = InverseLatitudeDirect(x2);

            // 间接法（级数展开）
            double indirectB1 = InverseLatitudeIndirect(x1);
            double indirectB2 = InverseLatitudeIndirect(x2);

            return $@"[直接法（迭代法）]
  P1反算: {directB1:F8}° （误差：{Math.Abs(directB1 - b1):F10}°）
  P2反算: {directB2:F8}° （误差：{Math.Abs(directB2 - b2):F10}°）

[间接法（级数展开）]
  P1反算: {indirectB1:F8}° （误差：{Math.Abs(indirectB1 - b1):F10}°）
  P2反算: {indirectB2:F8}° （误差：{Math.Abs(indirectB2 - b2):F10}°）";
        }

        // 第三部分：两点间弧长与纬度差
        private string GetPart3Result(double b1, double b2)
        {
            double deltaB = b2 - b1;
            double deltaXDirectP1 = DeltaXDirectFromP1(b1, deltaB);
            double deltaXDirectMid = DeltaXDirectFromMid(b1, b2);
            double deltaXIndirect = CalculateMeridianArcLength(b2) - CalculateMeridianArcLength(b1);

            // 新增：由弧长反算纬度差（间接法）
            double deltaB_FromX = InverseDeltaB(deltaXIndirect);

            return $@"[直接法（起点P1展开）]
  ΔX = {deltaXDirectP1:F3} m

[直接法（中点Bm展开）]
  ΔX = {deltaXDirectMid:F3} m

[间接法（X₂-X₁）]
  ΔX = {deltaXIndirect:F3} m

[反算纬度差]
  ΔB: {deltaB_FromX:F6}°";
        }

        // 由弧长反算纬度差（用于第三部分）
        private double InverseDeltaB(double deltaX)
        {
            double x1 = 0; // 赤道到赤道的弧长为0
            double x2 = deltaX;
            double b2 = InverseLatitudeDirect(x2);
            return b2 - 0; // 从赤道反算，故ΔB = b2 - 0
        }

        // 计算子午线弧长
        private double CalculateMeridianArcLength(double bDeg)
        {
            double bRad = bDeg * Math.PI / 180;
            return A0 * bDeg - 16036.480 * Math.Sin(2 * bRad) + 16.828 * Math.Sin(4 * bRad) - 0.022 * Math.Sin(6 * bRad);
        }

        // 直接法反算纬度（迭代法）
        private double InverseLatitudeDirect(double x)
        {
            double betaRad = x / C;
            double bCurr = betaRad, bPrev = 0;
            for (int i = 0; i < 100; i++)
            {
                bPrev = bCurr;
                double sin2B = Math.Sin(2 * bPrev);
                double sin4B = Math.Sin(4 * bPrev);
                double sin6B = Math.Sin(6 * bPrev);
                bCurr = (x + 32005.780 * sin2B - 135.3303 * sin4B + 0.7092 * sin6B) / A0 * Math.PI / 180;
                if (Math.Abs(bCurr - bPrev) < Epsilon) break;
            }
            return bCurr * 180 / Math.PI;
        }

        // 间接法反算纬度（级数展开）
        private double InverseLatitudeIndirect(double x)
        {
            double betaDeg = x / A0;
            double betaRad = betaDeg * Math.PI / 180;
            double p2 = 2.518828e-3, p4 = 3.701007e-6;
            return (betaRad + p2 * Math.Sin(2 * betaRad) + p4 * Math.Sin(4 * betaRad)) * 180 / Math.PI;
        }

        // 直接法（起点展开）
        private double DeltaXDirectFromP1(double b1Deg, double deltaBDeg)
        {
            double b1Rad = b1Deg * Math.PI / 180;
            double deltaBRad = deltaBDeg * Math.PI / 180;
            double M1 = A * (1 - E2) / Math.Pow(1 - E2 * Math.Sin(b1Rad) * Math.Sin(b1Rad), 1.5);
            double term = (3.0 / 2) * A * E2 * (1 - E2) * deltaBRad * deltaBRad / 2 *
                (1 + 5.0 / 2 * E2 * Math.Sin(b1Rad) * Math.Sin(b1Rad)) * Math.Sin(2 * b1Rad);
            return M1 * deltaBRad + term + (3.0 / 2 * A * E2 * (1 - E2) * Math.Cos(2 * b1Rad) * Math.Pow(deltaBRad, 3)) / 3;
        }

        // 直接法（中点展开）
        private double DeltaXDirectFromMid(double b1Deg, double b2Deg)
        {
            double bmDeg = (b1Deg + b2Deg) / 2;
            double bmRad = bmDeg * Math.PI / 180;
            double deltaBRad = (b2Deg - b1Deg) * Math.PI / 180;
            double Mm = A * (1 - E2) / Math.Pow(1 - E2 * Math.Sin(bmRad) * Math.Sin(bmRad), 1.5);
            double term = (A * E2 * (1 - E2) / 8) * Math.Cos(2 * bmRad) * deltaBRad * deltaBRad;
            return Mm * deltaBRad + term;
        }

        // 坐标解析
        private double ParseCoordinate(string input, string type)
        {
            if (!double.TryParse(input, out double value))
                throw new ArgumentException($"{type}格式错误");
            if (type.Contains("纬度") && (value < -90 || value > 90))
                throw new ArgumentException($"{type}必须在[-90°, 90°]之间");
            return value;
        }

        // 分区块显示结果
        private void ShowSection(string title, string content, Color color)
        {
            rtbResult.SelectionColor = Color.Black;
            rtbResult.AppendText(Environment.NewLine);
            rtbResult.SelectionColor = color;
            rtbResult.AppendText($"==== {title} ====\n");
            rtbResult.SelectionColor = Color.Black;
            rtbResult.AppendText(content + Environment.NewLine);
        }

        private void btnClear_Click(object sender, EventArgs e)
        {
            txtB1.Clear();
            txtL1.Clear();
            txtB2.Clear();
            txtL2.Clear();
            rtbResult.Clear();
            SetExampleValues();
        }

        private void label1_Click(object sender, EventArgs e)
        {

        }
    }
}