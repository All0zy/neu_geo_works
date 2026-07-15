using System.ComponentModel;
using System.Drawing;
using System.Windows.Forms;

namespace PPPPrecisionPointPositioning
{
    partial class MainForm
    {
        private IContainer components = null;

        private TableLayoutPanel tableLayoutPanelMain;
        private Label labelSp3Prev;
        private TextBox textBoxSp3Prev;
        private Button buttonSp3Prev;
        private Label labelSp3Today;
        private TextBox textBoxSp3Today;
        private Button buttonSp3Today;
        private Label labelSp3Next;
        private TextBox textBoxSp3Next;
        private Button buttonSp3Next;
        private Label labelClk;
        private TextBox textBoxClk;
        private Button buttonClk;
        private Label labelAtx;
        private TextBox textBoxAtx;
        private Button buttonAtx;
        private Label labelObs;
        private TextBox textBoxObs;
        private Button buttonObs;
        private Button buttonAutoLoad;
        private Button buttonRun;
        private Label labelTotal;
        private TextBox textBoxTotal;
        private Label labelN;
        private TextBox textBoxN;
        private Label labelE;
        private TextBox textBoxE;
        private Label labelU;
        private TextBox textBoxU;
        private SplitContainer splitContainerMain;
        private TextBox textBoxLog;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
                components.Dispose();
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.tableLayoutPanelMain = new System.Windows.Forms.TableLayoutPanel();
            this.labelSp3Prev = new System.Windows.Forms.Label();
            this.textBoxSp3Prev = new System.Windows.Forms.TextBox();
            this.buttonSp3Prev = new System.Windows.Forms.Button();
            this.labelSp3Today = new System.Windows.Forms.Label();
            this.textBoxSp3Today = new System.Windows.Forms.TextBox();
            this.buttonSp3Today = new System.Windows.Forms.Button();
            this.labelSp3Next = new System.Windows.Forms.Label();
            this.textBoxSp3Next = new System.Windows.Forms.TextBox();
            this.buttonSp3Next = new System.Windows.Forms.Button();
            this.labelClk = new System.Windows.Forms.Label();
            this.textBoxClk = new System.Windows.Forms.TextBox();
            this.buttonClk = new System.Windows.Forms.Button();
            this.labelAtx = new System.Windows.Forms.Label();
            this.textBoxAtx = new System.Windows.Forms.TextBox();
            this.buttonAtx = new System.Windows.Forms.Button();
            this.labelObs = new System.Windows.Forms.Label();
            this.textBoxObs = new System.Windows.Forms.TextBox();
            this.buttonObs = new System.Windows.Forms.Button();
            this.buttonAutoLoad = new System.Windows.Forms.Button();
            this.buttonRun = new System.Windows.Forms.Button();
            this.labelTotal = new System.Windows.Forms.Label();
            this.textBoxTotal = new System.Windows.Forms.TextBox();
            this.labelN = new System.Windows.Forms.Label();
            this.textBoxN = new System.Windows.Forms.TextBox();
            this.labelE = new System.Windows.Forms.Label();
            this.textBoxE = new System.Windows.Forms.TextBox();
            this.labelU = new System.Windows.Forms.Label();
            this.textBoxU = new System.Windows.Forms.TextBox();
            this.splitContainerMain = new System.Windows.Forms.SplitContainer();
            this.textBoxLog = new System.Windows.Forms.TextBox();
            this.tableLayoutPanelMain.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.splitContainerMain)).BeginInit();
            this.splitContainerMain.Panel2.SuspendLayout();
            this.splitContainerMain.SuspendLayout();
            this.SuspendLayout();
            // 
            // tableLayoutPanelMain
            // 
            this.tableLayoutPanelMain.ColumnCount = 3;
            this.tableLayoutPanelMain.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 150F));
            this.tableLayoutPanelMain.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.tableLayoutPanelMain.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 110F));
            this.tableLayoutPanelMain.Controls.Add(this.labelSp3Prev, 0, 0);
            this.tableLayoutPanelMain.Controls.Add(this.textBoxSp3Prev, 1, 0);
            this.tableLayoutPanelMain.Controls.Add(this.buttonSp3Prev, 2, 0);
            this.tableLayoutPanelMain.Controls.Add(this.labelSp3Today, 0, 1);
            this.tableLayoutPanelMain.Controls.Add(this.textBoxSp3Today, 1, 1);
            this.tableLayoutPanelMain.Controls.Add(this.buttonSp3Today, 2, 1);
            this.tableLayoutPanelMain.Controls.Add(this.labelSp3Next, 0, 2);
            this.tableLayoutPanelMain.Controls.Add(this.textBoxSp3Next, 1, 2);
            this.tableLayoutPanelMain.Controls.Add(this.buttonSp3Next, 2, 2);
            this.tableLayoutPanelMain.Controls.Add(this.labelClk, 0, 3);
            this.tableLayoutPanelMain.Controls.Add(this.textBoxClk, 1, 3);
            this.tableLayoutPanelMain.Controls.Add(this.buttonClk, 2, 3);
            this.tableLayoutPanelMain.Controls.Add(this.labelAtx, 0, 4);
            this.tableLayoutPanelMain.Controls.Add(this.textBoxAtx, 1, 4);
            this.tableLayoutPanelMain.Controls.Add(this.buttonAtx, 2, 4);
            this.tableLayoutPanelMain.Controls.Add(this.labelObs, 0, 5);
            this.tableLayoutPanelMain.Controls.Add(this.textBoxObs, 1, 5);
            this.tableLayoutPanelMain.Controls.Add(this.buttonObs, 2, 5);
            this.tableLayoutPanelMain.Controls.Add(this.buttonAutoLoad, 0, 6);
            this.tableLayoutPanelMain.Controls.Add(this.buttonRun, 0, 7);
            this.tableLayoutPanelMain.Controls.Add(this.labelTotal, 0, 8);
            this.tableLayoutPanelMain.Controls.Add(this.textBoxTotal, 1, 8);
            this.tableLayoutPanelMain.Controls.Add(this.labelN, 0, 9);
            this.tableLayoutPanelMain.Controls.Add(this.textBoxN, 1, 9);
            this.tableLayoutPanelMain.Controls.Add(this.labelE, 0, 10);
            this.tableLayoutPanelMain.Controls.Add(this.textBoxE, 1, 10);
            this.tableLayoutPanelMain.Controls.Add(this.labelU, 0, 11);
            this.tableLayoutPanelMain.Controls.Add(this.textBoxU, 1, 11);
            this.tableLayoutPanelMain.Dock = System.Windows.Forms.DockStyle.Fill;
            this.tableLayoutPanelMain.Location = new System.Drawing.Point(0, 0);
            this.tableLayoutPanelMain.Name = "tableLayoutPanelMain";
            this.tableLayoutPanelMain.Padding = new System.Windows.Forms.Padding(12, 11, 12, 11);
            this.tableLayoutPanelMain.RowCount = 12;
            this.tableLayoutPanelMain.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 34F));
            this.tableLayoutPanelMain.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 34F));
            this.tableLayoutPanelMain.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 34F));
            this.tableLayoutPanelMain.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 34F));
            this.tableLayoutPanelMain.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 34F));
            this.tableLayoutPanelMain.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 34F));
            this.tableLayoutPanelMain.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 41F));
            this.tableLayoutPanelMain.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 41F));
            this.tableLayoutPanelMain.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 34F));
            this.tableLayoutPanelMain.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 34F));
            this.tableLayoutPanelMain.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 34F));
            this.tableLayoutPanelMain.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 34F));
            this.tableLayoutPanelMain.Size = new System.Drawing.Size(980, 451);
            this.tableLayoutPanelMain.TabIndex = 0;
            // 
            // labelSp3Prev
            // 
            this.labelSp3Prev.AutoSize = true;
            this.labelSp3Prev.Dock = System.Windows.Forms.DockStyle.Fill;
            this.labelSp3Prev.Location = new System.Drawing.Point(15, 11);
            this.labelSp3Prev.Name = "labelSp3Prev";
            this.labelSp3Prev.Size = new System.Drawing.Size(144, 34);
            this.labelSp3Prev.TabIndex = 0;
            this.labelSp3Prev.Text = "SP3 前一天文件";
            this.labelSp3Prev.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // textBoxSp3Prev
            // 
            this.textBoxSp3Prev.Dock = System.Windows.Forms.DockStyle.Fill;
            this.textBoxSp3Prev.Location = new System.Drawing.Point(165, 14);
            this.textBoxSp3Prev.Name = "textBoxSp3Prev";
            this.textBoxSp3Prev.ReadOnly = true;
            this.textBoxSp3Prev.Size = new System.Drawing.Size(690, 28);
            this.textBoxSp3Prev.TabIndex = 1;
            // 
            // buttonSp3Prev
            // 
            this.buttonSp3Prev.Dock = System.Windows.Forms.DockStyle.Fill;
            this.buttonSp3Prev.Location = new System.Drawing.Point(861, 14);
            this.buttonSp3Prev.Name = "buttonSp3Prev";
            this.buttonSp3Prev.Size = new System.Drawing.Size(104, 28);
            this.buttonSp3Prev.TabIndex = 2;
            this.buttonSp3Prev.Text = "选择文件";
            this.buttonSp3Prev.Click += new System.EventHandler(this.buttonSp3Prev_Click);
            // 
            // labelSp3Today
            // 
            this.labelSp3Today.AutoSize = true;
            this.labelSp3Today.Dock = System.Windows.Forms.DockStyle.Fill;
            this.labelSp3Today.Location = new System.Drawing.Point(15, 45);
            this.labelSp3Today.Name = "labelSp3Today";
            this.labelSp3Today.Size = new System.Drawing.Size(144, 34);
            this.labelSp3Today.TabIndex = 3;
            this.labelSp3Today.Text = "SP3 当天文件";
            this.labelSp3Today.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // textBoxSp3Today
            // 
            this.textBoxSp3Today.Dock = System.Windows.Forms.DockStyle.Fill;
            this.textBoxSp3Today.Location = new System.Drawing.Point(165, 48);
            this.textBoxSp3Today.Name = "textBoxSp3Today";
            this.textBoxSp3Today.ReadOnly = true;
            this.textBoxSp3Today.Size = new System.Drawing.Size(690, 28);
            this.textBoxSp3Today.TabIndex = 4;
            // 
            // buttonSp3Today
            // 
            this.buttonSp3Today.Dock = System.Windows.Forms.DockStyle.Fill;
            this.buttonSp3Today.Location = new System.Drawing.Point(861, 48);
            this.buttonSp3Today.Name = "buttonSp3Today";
            this.buttonSp3Today.Size = new System.Drawing.Size(104, 28);
            this.buttonSp3Today.TabIndex = 5;
            this.buttonSp3Today.Text = "选择文件";
            this.buttonSp3Today.Click += new System.EventHandler(this.buttonSp3Today_Click);
            // 
            // labelSp3Next
            // 
            this.labelSp3Next.AutoSize = true;
            this.labelSp3Next.Dock = System.Windows.Forms.DockStyle.Fill;
            this.labelSp3Next.Location = new System.Drawing.Point(15, 79);
            this.labelSp3Next.Name = "labelSp3Next";
            this.labelSp3Next.Size = new System.Drawing.Size(144, 34);
            this.labelSp3Next.TabIndex = 6;
            this.labelSp3Next.Text = "SP3 后一天文件";
            this.labelSp3Next.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // textBoxSp3Next
            // 
            this.textBoxSp3Next.Dock = System.Windows.Forms.DockStyle.Fill;
            this.textBoxSp3Next.Location = new System.Drawing.Point(165, 82);
            this.textBoxSp3Next.Name = "textBoxSp3Next";
            this.textBoxSp3Next.ReadOnly = true;
            this.textBoxSp3Next.Size = new System.Drawing.Size(690, 28);
            this.textBoxSp3Next.TabIndex = 7;
            // 
            // buttonSp3Next
            // 
            this.buttonSp3Next.Dock = System.Windows.Forms.DockStyle.Fill;
            this.buttonSp3Next.Location = new System.Drawing.Point(861, 82);
            this.buttonSp3Next.Name = "buttonSp3Next";
            this.buttonSp3Next.Size = new System.Drawing.Size(104, 28);
            this.buttonSp3Next.TabIndex = 8;
            this.buttonSp3Next.Text = "选择文件";
            this.buttonSp3Next.Click += new System.EventHandler(this.buttonSp3Next_Click);
            // 
            // labelClk
            // 
            this.labelClk.AutoSize = true;
            this.labelClk.Dock = System.Windows.Forms.DockStyle.Fill;
            this.labelClk.Location = new System.Drawing.Point(15, 113);
            this.labelClk.Name = "labelClk";
            this.labelClk.Size = new System.Drawing.Size(144, 34);
            this.labelClk.TabIndex = 9;
            this.labelClk.Text = "CLK 文件";
            this.labelClk.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // textBoxClk
            // 
            this.textBoxClk.Dock = System.Windows.Forms.DockStyle.Fill;
            this.textBoxClk.Location = new System.Drawing.Point(165, 116);
            this.textBoxClk.Name = "textBoxClk";
            this.textBoxClk.ReadOnly = true;
            this.textBoxClk.Size = new System.Drawing.Size(690, 28);
            this.textBoxClk.TabIndex = 10;
            // 
            // buttonClk
            // 
            this.buttonClk.Dock = System.Windows.Forms.DockStyle.Fill;
            this.buttonClk.Location = new System.Drawing.Point(861, 116);
            this.buttonClk.Name = "buttonClk";
            this.buttonClk.Size = new System.Drawing.Size(104, 28);
            this.buttonClk.TabIndex = 11;
            this.buttonClk.Text = "选择文件";
            this.buttonClk.Click += new System.EventHandler(this.buttonClk_Click);
            // 
            // labelAtx
            // 
            this.labelAtx.AutoSize = true;
            this.labelAtx.Dock = System.Windows.Forms.DockStyle.Fill;
            this.labelAtx.Location = new System.Drawing.Point(15, 147);
            this.labelAtx.Name = "labelAtx";
            this.labelAtx.Size = new System.Drawing.Size(144, 34);
            this.labelAtx.TabIndex = 12;
            this.labelAtx.Text = "ATX 文件";
            this.labelAtx.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // textBoxAtx
            // 
            this.textBoxAtx.Dock = System.Windows.Forms.DockStyle.Fill;
            this.textBoxAtx.Location = new System.Drawing.Point(165, 150);
            this.textBoxAtx.Name = "textBoxAtx";
            this.textBoxAtx.ReadOnly = true;
            this.textBoxAtx.Size = new System.Drawing.Size(690, 28);
            this.textBoxAtx.TabIndex = 13;
            // 
            // buttonAtx
            // 
            this.buttonAtx.Dock = System.Windows.Forms.DockStyle.Fill;
            this.buttonAtx.Location = new System.Drawing.Point(861, 150);
            this.buttonAtx.Name = "buttonAtx";
            this.buttonAtx.Size = new System.Drawing.Size(104, 28);
            this.buttonAtx.TabIndex = 14;
            this.buttonAtx.Text = "选择文件";
            this.buttonAtx.Click += new System.EventHandler(this.buttonAtx_Click);
            // 
            // labelObs
            // 
            this.labelObs.AutoSize = true;
            this.labelObs.Dock = System.Windows.Forms.DockStyle.Fill;
            this.labelObs.Location = new System.Drawing.Point(15, 181);
            this.labelObs.Name = "labelObs";
            this.labelObs.Size = new System.Drawing.Size(144, 34);
            this.labelObs.TabIndex = 15;
            this.labelObs.Text = "OBS 文件";
            this.labelObs.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // textBoxObs
            // 
            this.textBoxObs.Dock = System.Windows.Forms.DockStyle.Fill;
            this.textBoxObs.Location = new System.Drawing.Point(165, 184);
            this.textBoxObs.Name = "textBoxObs";
            this.textBoxObs.ReadOnly = true;
            this.textBoxObs.Size = new System.Drawing.Size(690, 28);
            this.textBoxObs.TabIndex = 16;
            // 
            // buttonObs
            // 
            this.buttonObs.Dock = System.Windows.Forms.DockStyle.Fill;
            this.buttonObs.Location = new System.Drawing.Point(861, 184);
            this.buttonObs.Name = "buttonObs";
            this.buttonObs.Size = new System.Drawing.Size(104, 28);
            this.buttonObs.TabIndex = 17;
            this.buttonObs.Text = "选择文件";
            this.buttonObs.Click += new System.EventHandler(this.buttonObs_Click);
            // 
            // buttonAutoLoad
            // 
            this.tableLayoutPanelMain.SetColumnSpan(this.buttonAutoLoad, 3);
            this.buttonAutoLoad.Dock = System.Windows.Forms.DockStyle.Fill;
            this.buttonAutoLoad.Location = new System.Drawing.Point(15, 218);
            this.buttonAutoLoad.Name = "buttonAutoLoad";
            this.buttonAutoLoad.Size = new System.Drawing.Size(950, 35);
            this.buttonAutoLoad.TabIndex = 18;
            this.buttonAutoLoad.Text = "自动装载 Data 目录";
            this.buttonAutoLoad.Click += new System.EventHandler(this.buttonAutoLoad_Click);
            // 
            // buttonRun
            // 
            this.tableLayoutPanelMain.SetColumnSpan(this.buttonRun, 3);
            this.buttonRun.Dock = System.Windows.Forms.DockStyle.Fill;
            this.buttonRun.Location = new System.Drawing.Point(15, 259);
            this.buttonRun.Name = "buttonRun";
            this.buttonRun.Size = new System.Drawing.Size(950, 35);
            this.buttonRun.TabIndex = 19;
            this.buttonRun.Text = "开始计算";
            this.buttonRun.Click += new System.EventHandler(this.buttonRun_Click);
            // 
            // labelTotal
            // 
            this.labelTotal.AutoSize = true;
            this.labelTotal.Dock = System.Windows.Forms.DockStyle.Fill;
            this.labelTotal.Location = new System.Drawing.Point(15, 297);
            this.labelTotal.Name = "labelTotal";
            this.labelTotal.Size = new System.Drawing.Size(144, 34);
            this.labelTotal.TabIndex = 20;
            this.labelTotal.Text = "总 RMS";
            this.labelTotal.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // textBoxTotal
            // 
            this.tableLayoutPanelMain.SetColumnSpan(this.textBoxTotal, 2);
            this.textBoxTotal.Dock = System.Windows.Forms.DockStyle.Fill;
            this.textBoxTotal.Location = new System.Drawing.Point(165, 300);
            this.textBoxTotal.Name = "textBoxTotal";
            this.textBoxTotal.ReadOnly = true;
            this.textBoxTotal.Size = new System.Drawing.Size(800, 28);
            this.textBoxTotal.TabIndex = 21;
            this.textBoxTotal.TextChanged += new System.EventHandler(this.textBoxTotal_TextChanged);
            // 
            // labelN
            // 
            this.labelN.AutoSize = true;
            this.labelN.Dock = System.Windows.Forms.DockStyle.Fill;
            this.labelN.Location = new System.Drawing.Point(15, 331);
            this.labelN.Name = "labelN";
            this.labelN.Size = new System.Drawing.Size(144, 34);
            this.labelN.TabIndex = 22;
            this.labelN.Text = "N方向 RMS";
            this.labelN.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // textBoxN
            // 
            this.tableLayoutPanelMain.SetColumnSpan(this.textBoxN, 2);
            this.textBoxN.Dock = System.Windows.Forms.DockStyle.Fill;
            this.textBoxN.Location = new System.Drawing.Point(165, 334);
            this.textBoxN.Name = "textBoxN";
            this.textBoxN.ReadOnly = true;
            this.textBoxN.Size = new System.Drawing.Size(800, 28);
            this.textBoxN.TabIndex = 23;
            this.textBoxN.TextChanged += new System.EventHandler(this.textBoxN_TextChanged);
            // 
            // labelE
            // 
            this.labelE.AutoSize = true;
            this.labelE.Dock = System.Windows.Forms.DockStyle.Fill;
            this.labelE.Location = new System.Drawing.Point(15, 365);
            this.labelE.Name = "labelE";
            this.labelE.Size = new System.Drawing.Size(144, 34);
            this.labelE.TabIndex = 24;
            this.labelE.Text = "E方向 RMS";
            this.labelE.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // textBoxE
            // 
            this.tableLayoutPanelMain.SetColumnSpan(this.textBoxE, 2);
            this.textBoxE.Dock = System.Windows.Forms.DockStyle.Fill;
            this.textBoxE.Location = new System.Drawing.Point(165, 368);
            this.textBoxE.Name = "textBoxE";
            this.textBoxE.ReadOnly = true;
            this.textBoxE.Size = new System.Drawing.Size(800, 28);
            this.textBoxE.TabIndex = 25;
            // 
            // labelU
            // 
            this.labelU.AutoSize = true;
            this.labelU.Dock = System.Windows.Forms.DockStyle.Fill;
            this.labelU.Location = new System.Drawing.Point(15, 399);
            this.labelU.Name = "labelU";
            this.labelU.Size = new System.Drawing.Size(144, 41);
            this.labelU.TabIndex = 26;
            this.labelU.Text = "U方向 RMS";
            this.labelU.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // textBoxU
            // 
            this.tableLayoutPanelMain.SetColumnSpan(this.textBoxU, 2);
            this.textBoxU.Dock = System.Windows.Forms.DockStyle.Fill;
            this.textBoxU.Location = new System.Drawing.Point(165, 402);
            this.textBoxU.Name = "textBoxU";
            this.textBoxU.ReadOnly = true;
            this.textBoxU.Size = new System.Drawing.Size(800, 28);
            this.textBoxU.TabIndex = 27;
            this.textBoxU.TextChanged += new System.EventHandler(this.textBoxU_TextChanged);
            // 
            // splitContainerMain
            // 
            this.splitContainerMain.Dock = System.Windows.Forms.DockStyle.Bottom;
            this.splitContainerMain.Location = new System.Drawing.Point(0, 451);
            this.splitContainerMain.Name = "splitContainerMain";
            this.splitContainerMain.Orientation = System.Windows.Forms.Orientation.Horizontal;
            // 
            // splitContainerMain.Panel1
            // 
            this.splitContainerMain.Panel1.Paint += new System.Windows.Forms.PaintEventHandler(this.splitContainerMain_Panel1_Paint);
            // 
            // splitContainerMain.Panel2
            // 
            this.splitContainerMain.Panel2.Controls.Add(this.textBoxLog);
            this.splitContainerMain.Size = new System.Drawing.Size(980, 197);
            this.splitContainerMain.SplitterDistance = 25;
            this.splitContainerMain.TabIndex = 1;
            // 
            // textBoxLog
            // 
            this.textBoxLog.Dock = System.Windows.Forms.DockStyle.Fill;
            this.textBoxLog.Location = new System.Drawing.Point(0, 0);
            this.textBoxLog.Multiline = true;
            this.textBoxLog.Name = "textBoxLog";
            this.textBoxLog.ReadOnly = true;
            this.textBoxLog.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.textBoxLog.Size = new System.Drawing.Size(980, 168);
            this.textBoxLog.TabIndex = 0;
            // 
            // MainForm
            // 
            this.ClientSize = new System.Drawing.Size(980, 648);
            this.Controls.Add(this.tableLayoutPanelMain);
            this.Controls.Add(this.splitContainerMain);
            this.Name = "MainForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "PPP精密单点定位 - WinForms (.NET Framework 4.6.1)";
            this.tableLayoutPanelMain.ResumeLayout(false);
            this.tableLayoutPanelMain.PerformLayout();
            this.splitContainerMain.Panel2.ResumeLayout(false);
            this.splitContainerMain.Panel2.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.splitContainerMain)).EndInit();
            this.splitContainerMain.ResumeLayout(false);
            this.ResumeLayout(false);

        }
    }
}
