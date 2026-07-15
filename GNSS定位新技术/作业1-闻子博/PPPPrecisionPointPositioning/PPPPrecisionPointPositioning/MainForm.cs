using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Drawing;
using System.Windows.Forms;

namespace PPPPrecisionPointPositioning
{
    public partial class MainForm : Form
    {
        private readonly Dictionary<string, TextBox> _fileBoxes = new Dictionary<string, TextBox>();

        public MainForm()
        {
            InitializeComponent();
            BindFileBoxes();
        }

        private void BindFileBoxes()
        {
            _fileBoxes["sp3b"] = textBoxSp3Prev;
            _fileBoxes["sp3"] = textBoxSp3Today;
            _fileBoxes["sp3a"] = textBoxSp3Next;
            _fileBoxes["clk"] = textBoxClk;
            _fileBoxes["atx"] = textBoxAtx;
            _fileBoxes["obs"] = textBoxObs;
        }

        private void buttonSp3Prev_Click(object sender, EventArgs e) { SelectFile("sp3b"); }
        private void buttonSp3Today_Click(object sender, EventArgs e) { SelectFile("sp3"); }
        private void buttonSp3Next_Click(object sender, EventArgs e) { SelectFile("sp3a"); }
        private void buttonClk_Click(object sender, EventArgs e) { SelectFile("clk"); }
        private void buttonAtx_Click(object sender, EventArgs e) { SelectFile("atx"); }
        private void buttonObs_Click(object sender, EventArgs e) { SelectFile("obs"); }

        private void buttonAutoLoad_Click(object sender, EventArgs e)
        {
            AutoLoadDataFolder();
        }

        private void buttonRun_Click(object sender, EventArgs e)
        {
            RunProcessing();
        }

        private void SelectFile(string key)
        {
            using (OpenFileDialog ofd = new OpenFileDialog())
            {
                ofd.Filter = "All Files|*.*";
                if (ofd.ShowDialog(this) == DialogResult.OK)
                {
                    _fileBoxes[key].Text = ofd.FileName;
                    Log("已选择文件: " + ofd.FileName);
                }
            }
        }

        private void AutoLoadDataFolder()
        {
            using (FolderBrowserDialog fbd = new FolderBrowserDialog())
            {
                fbd.Description = "选择包含 6 个 Data 文件的目录";
                if (fbd.ShowDialog(this) != DialogResult.OK)
                    return;

                string folder = fbd.SelectedPath;

                SetIfExists("sp3b", Path.Combine(folder, "gfz22001.sp3"));
                SetIfExists("sp3", Path.Combine(folder, "gfz22002.sp3"));
                SetIfExists("sp3a", Path.Combine(folder, "gfz22003.sp3"));
                SetIfExists("clk", Path.Combine(folder, "gfz22002.clk"));
                SetIfExists("atx", Path.Combine(folder, "igs14.atx"));
                SetIfExists("obs", Path.Combine(folder, "algo0670.22o"));

                Log("已尝试从目录自动装载: " + folder);
            }
        }

        private void SetIfExists(string key, string path)
        {
            if (File.Exists(path))
                _fileBoxes[key].Text = path;
        }

        private void RunProcessing()
        {
            try
            {
                ClearOutputs();
                textBoxLog.Clear();

                PppInputFiles input = new PppInputFiles();
                input.Sp3PrevPath = textBoxSp3Prev.Text.Trim();
                input.Sp3TodayPath = textBoxSp3Today.Text.Trim();
                input.Sp3NextPath = textBoxSp3Next.Text.Trim();
                input.ClkPath = textBoxClk.Text.Trim();
                input.AtxPath = textBoxAtx.Text.Trim();
                input.ObsPath = textBoxObs.Text.Trim();
                input.Validate();

                PppEvaluationOptions evaluationOptions;
                using (EvaluationSettingsDialog dlg = new EvaluationSettingsDialog())
                {
                    if (dlg.ShowDialog(this) != DialogResult.OK)
                    {
                        Log("用户取消了计算。");
                        return;
                    }
                    evaluationOptions = dlg.BuildOptions();
                }

                Log("文件校验通过，开始执行 PPP 流程...");
                PppProcessingService service = new PppProcessingService(new Action<string>(Log));
                PppResult result = service.Run(input, evaluationOptions);

                textBoxTotal.Text = ToMillimeterText(result.TotalRms);
                textBoxN.Text = ToMillimeterText(result.NRms);
                textBoxE.Text = ToMillimeterText(result.ERms);
                textBoxU.Text = ToMillimeterText(result.URms);

                Log("主显示指标: " + result.PrimaryMetricName);
                Log("参考坐标模式: " + result.ReferenceMode);
                Log("统计起始历元索引: " + result.StatisticsStartEpoch.ToString(CultureInfo.InvariantCulture));
                Log("有效输出历元: " + result.UsedEpochCount.ToString(CultureInfo.InvariantCulture));
                Log("收敛历元数: " + result.ConvergedEpochCount.ToString(CultureInfo.InvariantCulture));
                Log("参与统计历元: " + result.StatisticsEpochCount.ToString(CultureInfo.InvariantCulture));

                Log("主参考坐标 XYZ = "
                    + result.ReferenceXyz[0].ToString("F4", CultureInfo.InvariantCulture) + ", "
                    + result.ReferenceXyz[1].ToString("F4", CultureInfo.InvariantCulture) + ", "
                    + result.ReferenceXyz[2].ToString("F4", CultureInfo.InvariantCulture));

                Log("内部散布参考 XYZ = "
                    + result.ScatterReferenceXyz[0].ToString("F4", CultureInfo.InvariantCulture) + ", "
                    + result.ScatterReferenceXyz[1].ToString("F4", CultureInfo.InvariantCulture) + ", "
                    + result.ScatterReferenceXyz[2].ToString("F4", CultureInfo.InvariantCulture));

                Log("内部散布 RMS: 总=" + ToMillimeterText(result.ScatterTotalRms)
                    + ", N=" + ToMillimeterText(result.ScatterNRms)
                    + ", E=" + ToMillimeterText(result.ScatterERms)
                    + ", U=" + ToMillimeterText(result.ScatterURms));

                if (result.HasAbsoluteReference)
                {
                    Log("绝对参考 XYZ = "
                        + result.AbsoluteReferenceXyz[0].ToString("F4", CultureInfo.InvariantCulture) + ", "
                        + result.AbsoluteReferenceXyz[1].ToString("F4", CultureInfo.InvariantCulture) + ", "
                        + result.AbsoluteReferenceXyz[2].ToString("F4", CultureInfo.InvariantCulture));

                    Log("绝对 NEU RMS: 总=" + ToMillimeterText(result.AbsoluteTotalRms)
                        + ", N=" + ToMillimeterText(result.AbsoluteNRms)
                        + ", E=" + ToMillimeterText(result.AbsoluteERms)
                        + ", U=" + ToMillimeterText(result.AbsoluteURms));
                }
                else
                {
                    Log("当前未提供外部参考坐标，因此界面显示的是内部散布 RMS，不是绝对定位误差。");
                }

                Log(result.Summary);
                Log("计算完成。");
            }
            catch (Exception ex)
            {
                MessageBox.Show(this, ex.Message, "运行失败", MessageBoxButtons.OK, MessageBoxIcon.Error);
                Log("错误: " + ex.Message);
            }
        }

        private static string ToMillimeterText(double meters)
        {
            return (meters/10000.0).ToString("F3", CultureInfo.InvariantCulture) + " mm";
        }

        private void ClearOutputs()
        {
            textBoxTotal.Clear();
            textBoxN.Clear();
            textBoxE.Clear();
            textBoxU.Clear();
        }

        private void Log(string message)
        {
            textBoxLog.AppendText("[" + DateTime.Now.ToString("HH:mm:ss") + "] " + message + Environment.NewLine);
        }

        private void splitContainerMain_Panel1_Paint(object sender, PaintEventArgs e)
        {
        }

        private void textBoxN_TextChanged(object sender, EventArgs e)
        {

        }

        private void textBoxTotal_TextChanged(object sender, EventArgs e)
        {

        }

        private void textBoxU_TextChanged(object sender, EventArgs e)
        {

        }
    }

    internal sealed class EvaluationSettingsDialog : Form
    {
        private readonly ComboBox _comboMode;
        private readonly TextBox _textStartEpoch;
        private readonly TextBox _textX;
        private readonly TextBox _textY;
        private readonly TextBox _textZ;
        private readonly Label _labelHint;

        public EvaluationSettingsDialog()
        {
            Text = "评估方式";
            FormBorderStyle = FormBorderStyle.FixedDialog;
            StartPosition = FormStartPosition.CenterParent;
            MaximizeBox = false;
            MinimizeBox = false;
            ClientSize = new Size(470, 260);

            Label labelMode = new Label();
            labelMode.Text = "参考坐标来源：";
            labelMode.AutoSize = true;
            labelMode.Location = new Point(20, 20);
            Controls.Add(labelMode);

            _comboMode = new ComboBox();
            _comboMode.DropDownStyle = ComboBoxStyle.DropDownList;
            _comboMode.Items.Add("仅看收敛后均值（内部散布，不是绝对误差）");
            _comboMode.Items.Add("使用 RINEX 头近似坐标");
            _comboMode.Items.Add("手动输入真值 XYZ");
            _comboMode.SelectedIndex = 0;
            _comboMode.Location = new Point(150, 16);
            _comboMode.Size = new Size(290, 24);
            _comboMode.SelectedIndexChanged += ComboMode_SelectedIndexChanged;
            Controls.Add(_comboMode);

            Label labelStart = new Label();
            labelStart.Text = "统计起始历元：";
            labelStart.AutoSize = true;
            labelStart.Location = new Point(20, 60);
            Controls.Add(labelStart);

            _textStartEpoch = new TextBox();
            _textStartEpoch.Text = "120";
            _textStartEpoch.Location = new Point(150, 56);
            _textStartEpoch.Size = new Size(90, 23);
            Controls.Add(_textStartEpoch);

            Label labelX = new Label();
            labelX.Text = "参考 X：";
            labelX.AutoSize = true;
            labelX.Location = new Point(20, 100);
            Controls.Add(labelX);

            _textX = new TextBox();
            _textX.Location = new Point(150, 96);
            _textX.Size = new Size(180, 23);
            Controls.Add(_textX);

            Label labelY = new Label();
            labelY.Text = "参考 Y：";
            labelY.AutoSize = true;
            labelY.Location = new Point(20, 135);
            Controls.Add(labelY);

            _textY = new TextBox();
            _textY.Location = new Point(150, 131);
            _textY.Size = new Size(180, 23);
            Controls.Add(_textY);

            Label labelZ = new Label();
            labelZ.Text = "参考 Z：";
            labelZ.AutoSize = true;
            labelZ.Location = new Point(20, 170);
            Controls.Add(labelZ);

            _textZ = new TextBox();
            _textZ.Location = new Point(150, 166);
            _textZ.Size = new Size(180, 23);
            Controls.Add(_textZ);

            _labelHint = new Label();
            _labelHint.Text = "若不提供外部参考，界面显示的是内部散布 RMS。";
            _labelHint.AutoSize = false;
            _labelHint.Size = new Size(420, 36);
            _labelHint.Location = new Point(20, 198);
            Controls.Add(_labelHint);

            Button buttonOk = new Button();
            buttonOk.Text = "确定";
            buttonOk.DialogResult = DialogResult.OK;
            buttonOk.Location = new Point(260, 225);
            buttonOk.Size = new Size(80, 26);
            Controls.Add(buttonOk);

            Button buttonCancel = new Button();
            buttonCancel.Text = "取消";
            buttonCancel.DialogResult = DialogResult.Cancel;
            buttonCancel.Location = new Point(355, 225);
            buttonCancel.Size = new Size(80, 26);
            Controls.Add(buttonCancel);

            AcceptButton = buttonOk;
            CancelButton = buttonCancel;

            UpdateManualInputState();
        }

        private void ComboMode_SelectedIndexChanged(object sender, EventArgs e)
        {
            UpdateManualInputState();
        }

        private void UpdateManualInputState()
        {
            bool manual = _comboMode.SelectedIndex == 2;
            _textX.Enabled = manual;
            _textY.Enabled = manual;
            _textZ.Enabled = manual;

            if (_comboMode.SelectedIndex == 0)
                _labelHint.Text = "仅统计收敛后坐标对自身均值的散布，不代表绝对定位误差。";
            else if (_comboMode.SelectedIndex == 1)
                _labelHint.Text = "使用 RINEX 头近似坐标作为参考，可得到相对该近似坐标的误差。";
            else
                _labelHint.Text = "请输入外部真值 XYZ，界面将显示相对该参考坐标的绝对 NEU RMS。";
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            if (DialogResult == DialogResult.OK)
            {
                try
                {
                    BuildOptions();
                }
                catch (Exception ex)
                {
                    MessageBox.Show(this, ex.Message, "输入有误", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    e.Cancel = true;
                    return;
                }
            }

            base.OnFormClosing(e);
        }

        public PppEvaluationOptions BuildOptions()
        {
            PppEvaluationOptions options = new PppEvaluationOptions();

            int startEpoch;
            if (!int.TryParse(_textStartEpoch.Text.Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out startEpoch) || startEpoch < 0)
                throw new InvalidOperationException("统计起始历元必须是大于等于 0 的整数。");
            options.StatisticsStartEpoch = startEpoch;

            if (_comboMode.SelectedIndex == 1)
            {
                options.ReferenceMode = PppReferenceMode.RinexApprox;
            }
            else if (_comboMode.SelectedIndex == 2)
            {
                options.ReferenceMode = PppReferenceMode.ManualXyz;
                options.ManualReferenceXyz = new double[3];
                options.ManualReferenceXyz[0] = ParseDouble(_textX.Text, "参考 X");
                options.ManualReferenceXyz[1] = ParseDouble(_textY.Text, "参考 Y");
                options.ManualReferenceXyz[2] = ParseDouble(_textZ.Text, "参考 Z");
            }
            else
            {
                options.ReferenceMode = PppReferenceMode.ConvergedMean;
            }

            return options;
        }

        private static double ParseDouble(string text, string name)
        {
            double value;
            if (!double.TryParse(text.Trim(), NumberStyles.Float | NumberStyles.AllowThousands, CultureInfo.InvariantCulture, out value))
                throw new InvalidOperationException(name + "不是有效数字。");
            return value;
        }
    }
}
