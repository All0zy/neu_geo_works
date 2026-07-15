namespace CoordinateTransformation
{
    partial class Form1
    {
        /// <summary>
        /// 必需的设计器变量。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 清理所有正在使用的资源。
        /// </summary>
        /// <param name="disposing">如果应释放托管资源，为 true；否则为 false。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Form1));
            this.btnLoadOldPoints = new System.Windows.Forms.Button();
            this.btnLoadNewPoints = new System.Windows.Forms.Button();
            this.btnCalculate = new System.Windows.Forms.Button();
            this.btnTransform = new System.Windows.Forms.Button();
            this.txtOldPointsPath = new System.Windows.Forms.TextBox();
            this.txtNewPointsPath = new System.Windows.Forms.TextBox();
            this.txtTransformPoints = new System.Windows.Forms.TextBox();
            this.lblOldPointsPath = new System.Windows.Forms.Label();
            this.lblNewPointsPath = new System.Windows.Forms.Label();
            this.lblTransformPoints = new System.Windows.Forms.Label();
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.tabPage1 = new System.Windows.Forms.TabPage();
            this.lvOldPoints = new System.Windows.Forms.ListView();
            this.columnHeader1 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader2 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader3 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader4 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.tabPage2 = new System.Windows.Forms.TabPage();
            this.lvNewPoints = new System.Windows.Forms.ListView();
            this.columnHeader5 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader6 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader7 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader8 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.tabPage3 = new System.Windows.Forms.TabPage();
            this.lvResult = new System.Windows.Forms.ListView();
            this.columnHeader9 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader10 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader11 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader12 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.tabPage4 = new System.Windows.Forms.TabPage();
            this.lvParameters = new System.Windows.Forms.ListView();
            this.columnHeader13 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader14 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.tabPage5 = new System.Windows.Forms.TabPage();
            this.lvError = new System.Windows.Forms.ListView();
            this.columnHeader15 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader16 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.openFileDialog1 = new System.Windows.Forms.OpenFileDialog();
            this.label1 = new System.Windows.Forms.Label();
            this.tabControl1.SuspendLayout();
            this.tabPage1.SuspendLayout();
            this.tabPage2.SuspendLayout();
            this.tabPage3.SuspendLayout();
            this.tabPage4.SuspendLayout();
            this.tabPage5.SuspendLayout();
            this.SuspendLayout();
            // 
            // btnLoadOldPoints
            // 
            this.btnLoadOldPoints.BackColor = System.Drawing.SystemColors.Highlight;
            this.btnLoadOldPoints.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnLoadOldPoints.ForeColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnLoadOldPoints.Location = new System.Drawing.Point(12, 99);
            this.btnLoadOldPoints.Name = "btnLoadOldPoints";
            this.btnLoadOldPoints.Size = new System.Drawing.Size(206, 36);
            this.btnLoadOldPoints.TabIndex = 0;
            this.btnLoadOldPoints.Text = "加载旧点";
            this.btnLoadOldPoints.UseVisualStyleBackColor = false;
            this.btnLoadOldPoints.Click += new System.EventHandler(this.btnLoadOldPoints_Click);
            // 
            // btnLoadNewPoints
            // 
            this.btnLoadNewPoints.BackColor = System.Drawing.SystemColors.Highlight;
            this.btnLoadNewPoints.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnLoadNewPoints.ForeColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnLoadNewPoints.Location = new System.Drawing.Point(234, 99);
            this.btnLoadNewPoints.Name = "btnLoadNewPoints";
            this.btnLoadNewPoints.Size = new System.Drawing.Size(206, 36);
            this.btnLoadNewPoints.TabIndex = 1;
            this.btnLoadNewPoints.Text = "加载新点";
            this.btnLoadNewPoints.UseVisualStyleBackColor = false;
            this.btnLoadNewPoints.Click += new System.EventHandler(this.btnLoadNewPoints_Click);
            // 
            // btnCalculate
            // 
            this.btnCalculate.BackColor = System.Drawing.SystemColors.Highlight;
            this.btnCalculate.Font = new System.Drawing.Font("微软雅黑", 10.8F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnCalculate.ForeColor = System.Drawing.SystemColors.ControlLightLight;
            this.btnCalculate.Location = new System.Drawing.Point(12, 139);
            this.btnCalculate.Name = "btnCalculate";
            this.btnCalculate.Size = new System.Drawing.Size(428, 42);
            this.btnCalculate.TabIndex = 2;
            this.btnCalculate.Text = "计算参数";
            this.btnCalculate.UseVisualStyleBackColor = false;
            this.btnCalculate.Click += new System.EventHandler(this.btnCalculate_Click);
            // 
            // btnTransform
            // 
            this.btnTransform.BackColor = System.Drawing.SystemColors.Highlight;
            this.btnTransform.Font = new System.Drawing.Font("微软雅黑", 10.8F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnTransform.ForeColor = System.Drawing.SystemColors.ControlLightLight;
            this.btnTransform.Location = new System.Drawing.Point(464, 139);
            this.btnTransform.Name = "btnTransform";
            this.btnTransform.Size = new System.Drawing.Size(563, 42);
            this.btnTransform.TabIndex = 3;
            this.btnTransform.Text = "坐标转换";
            this.btnTransform.UseVisualStyleBackColor = false;
            this.btnTransform.Click += new System.EventHandler(this.btnTransform_Click);
            // 
            // txtOldPointsPath
            // 
            this.txtOldPointsPath.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.txtOldPointsPath.Location = new System.Drawing.Point(105, 37);
            this.txtOldPointsPath.Name = "txtOldPointsPath";
            this.txtOldPointsPath.Size = new System.Drawing.Size(335, 27);
            this.txtOldPointsPath.TabIndex = 4;
            // 
            // txtNewPointsPath
            // 
            this.txtNewPointsPath.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.txtNewPointsPath.Location = new System.Drawing.Point(105, 68);
            this.txtNewPointsPath.Name = "txtNewPointsPath";
            this.txtNewPointsPath.Size = new System.Drawing.Size(335, 27);
            this.txtNewPointsPath.TabIndex = 5;
            // 
            // txtTransformPoints
            // 
            this.txtTransformPoints.Font = new System.Drawing.Font("微软雅黑", 10.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.txtTransformPoints.Location = new System.Drawing.Point(464, 37);
            this.txtTransformPoints.Multiline = true;
            this.txtTransformPoints.Name = "txtTransformPoints";
            this.txtTransformPoints.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtTransformPoints.Size = new System.Drawing.Size(563, 95);
            this.txtTransformPoints.TabIndex = 6;
            this.txtTransformPoints.Text = resources.GetString("txtTransformPoints.Text");
            // 
            // lblOldPointsPath
            // 
            this.lblOldPointsPath.AutoSize = true;
            this.lblOldPointsPath.Font = new System.Drawing.Font("微软雅黑", 10.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.lblOldPointsPath.Location = new System.Drawing.Point(17, 37);
            this.lblOldPointsPath.Name = "lblOldPointsPath";
            this.lblOldPointsPath.Size = new System.Drawing.Size(82, 24);
            this.lblOldPointsPath.TabIndex = 7;
            this.lblOldPointsPath.Text = "旧点路径";
            // 
            // lblNewPointsPath
            // 
            this.lblNewPointsPath.AutoSize = true;
            this.lblNewPointsPath.Font = new System.Drawing.Font("微软雅黑", 10.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.lblNewPointsPath.Location = new System.Drawing.Point(17, 68);
            this.lblNewPointsPath.Name = "lblNewPointsPath";
            this.lblNewPointsPath.Size = new System.Drawing.Size(82, 24);
            this.lblNewPointsPath.TabIndex = 8;
            this.lblNewPointsPath.Text = "新点路径";
            // 
            // lblTransformPoints
            // 
            this.lblTransformPoints.AutoSize = true;
            this.lblTransformPoints.Font = new System.Drawing.Font("微软雅黑", 10.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.lblTransformPoints.Location = new System.Drawing.Point(464, 7);
            this.lblTransformPoints.Name = "lblTransformPoints";
            this.lblTransformPoints.Size = new System.Drawing.Size(118, 24);
            this.lblTransformPoints.TabIndex = 9;
            this.lblTransformPoints.Text = "待转换点数据";
            // 
            // tabControl1
            // 
            this.tabControl1.Controls.Add(this.tabPage1);
            this.tabControl1.Controls.Add(this.tabPage2);
            this.tabControl1.Controls.Add(this.tabPage3);
            this.tabControl1.Controls.Add(this.tabPage4);
            this.tabControl1.Controls.Add(this.tabPage5);
            this.tabControl1.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.tabControl1.Location = new System.Drawing.Point(12, 187);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(1015, 349);
            this.tabControl1.TabIndex = 10;
            // 
            // tabPage1
            // 
            this.tabPage1.Controls.Add(this.lvOldPoints);
            this.tabPage1.Location = new System.Drawing.Point(4, 28);
            this.tabPage1.Name = "tabPage1";
            this.tabPage1.Padding = new System.Windows.Forms.Padding(3, 3, 3, 3);
            this.tabPage1.Size = new System.Drawing.Size(1007, 317);
            this.tabPage1.TabIndex = 0;
            this.tabPage1.Text = "旧点数据";
            this.tabPage1.UseVisualStyleBackColor = true;
            // 
            // lvOldPoints
            // 
            this.lvOldPoints.Columns.AddRange(new System.Windows.Forms.ColumnHeader[] {
            this.columnHeader1,
            this.columnHeader2,
            this.columnHeader3,
            this.columnHeader4});
            this.lvOldPoints.Dock = System.Windows.Forms.DockStyle.Fill;
            this.lvOldPoints.FullRowSelect = true;
            this.lvOldPoints.GridLines = true;
            this.lvOldPoints.HideSelection = false;
            this.lvOldPoints.Location = new System.Drawing.Point(3, 3);
            this.lvOldPoints.Name = "lvOldPoints";
            this.lvOldPoints.Size = new System.Drawing.Size(1001, 311);
            this.lvOldPoints.TabIndex = 0;
            this.lvOldPoints.UseCompatibleStateImageBehavior = false;
            this.lvOldPoints.View = System.Windows.Forms.View.Details;
            // 
            // columnHeader1
            // 
            this.columnHeader1.Text = "点号";
            this.columnHeader1.Width = 100;
            // 
            // columnHeader2
            // 
            this.columnHeader2.Text = "X";
            this.columnHeader2.Width = 150;
            // 
            // columnHeader3
            // 
            this.columnHeader3.Text = "Y";
            this.columnHeader3.Width = 150;
            // 
            // columnHeader4
            // 
            this.columnHeader4.Text = "Z";
            this.columnHeader4.Width = 150;
            // 
            // tabPage2
            // 
            this.tabPage2.Controls.Add(this.lvNewPoints);
            this.tabPage2.Location = new System.Drawing.Point(4, 28);
            this.tabPage2.Name = "tabPage2";
            this.tabPage2.Padding = new System.Windows.Forms.Padding(3, 3, 3, 3);
            this.tabPage2.Size = new System.Drawing.Size(1007, 317);
            this.tabPage2.TabIndex = 1;
            this.tabPage2.Text = "新点数据";
            this.tabPage2.UseVisualStyleBackColor = true;
            // 
            // lvNewPoints
            // 
            this.lvNewPoints.Columns.AddRange(new System.Windows.Forms.ColumnHeader[] {
            this.columnHeader5,
            this.columnHeader6,
            this.columnHeader7,
            this.columnHeader8});
            this.lvNewPoints.Dock = System.Windows.Forms.DockStyle.Fill;
            this.lvNewPoints.FullRowSelect = true;
            this.lvNewPoints.GridLines = true;
            this.lvNewPoints.HideSelection = false;
            this.lvNewPoints.Location = new System.Drawing.Point(3, 3);
            this.lvNewPoints.Name = "lvNewPoints";
            this.lvNewPoints.Size = new System.Drawing.Size(1001, 311);
            this.lvNewPoints.TabIndex = 0;
            this.lvNewPoints.UseCompatibleStateImageBehavior = false;
            this.lvNewPoints.View = System.Windows.Forms.View.Details;
            // 
            // columnHeader5
            // 
            this.columnHeader5.Text = "点号";
            this.columnHeader5.Width = 100;
            // 
            // columnHeader6
            // 
            this.columnHeader6.Text = "X";
            this.columnHeader6.Width = 150;
            // 
            // columnHeader7
            // 
            this.columnHeader7.Text = "Y";
            this.columnHeader7.Width = 150;
            // 
            // columnHeader8
            // 
            this.columnHeader8.Text = "Z";
            this.columnHeader8.Width = 150;
            // 
            // tabPage3
            // 
            this.tabPage3.Controls.Add(this.lvResult);
            this.tabPage3.Location = new System.Drawing.Point(4, 28);
            this.tabPage3.Name = "tabPage3";
            this.tabPage3.Padding = new System.Windows.Forms.Padding(3, 3, 3, 3);
            this.tabPage3.Size = new System.Drawing.Size(1007, 317);
            this.tabPage3.TabIndex = 2;
            this.tabPage3.Text = "转换结果";
            this.tabPage3.UseVisualStyleBackColor = true;
            // 
            // lvResult
            // 
            this.lvResult.Columns.AddRange(new System.Windows.Forms.ColumnHeader[] {
            this.columnHeader9,
            this.columnHeader10,
            this.columnHeader11,
            this.columnHeader12});
            this.lvResult.Dock = System.Windows.Forms.DockStyle.Fill;
            this.lvResult.FullRowSelect = true;
            this.lvResult.GridLines = true;
            this.lvResult.HideSelection = false;
            this.lvResult.Location = new System.Drawing.Point(3, 3);
            this.lvResult.Name = "lvResult";
            this.lvResult.Size = new System.Drawing.Size(1001, 311);
            this.lvResult.TabIndex = 0;
            this.lvResult.UseCompatibleStateImageBehavior = false;
            this.lvResult.View = System.Windows.Forms.View.Details;
            // 
            // columnHeader9
            // 
            this.columnHeader9.Text = "点号";
            this.columnHeader9.Width = 100;
            // 
            // columnHeader10
            // 
            this.columnHeader10.Text = "X";
            this.columnHeader10.Width = 150;
            // 
            // columnHeader11
            // 
            this.columnHeader11.Text = "Y";
            this.columnHeader11.Width = 150;
            // 
            // columnHeader12
            // 
            this.columnHeader12.Text = "Z";
            this.columnHeader12.Width = 150;
            // 
            // tabPage4
            // 
            this.tabPage4.Controls.Add(this.lvParameters);
            this.tabPage4.Location = new System.Drawing.Point(4, 28);
            this.tabPage4.Name = "tabPage4";
            this.tabPage4.Padding = new System.Windows.Forms.Padding(3, 3, 3, 3);
            this.tabPage4.Size = new System.Drawing.Size(1007, 317);
            this.tabPage4.TabIndex = 3;
            this.tabPage4.Text = "转换参数";
            this.tabPage4.UseVisualStyleBackColor = true;
            // 
            // lvParameters
            // 
            this.lvParameters.Columns.AddRange(new System.Windows.Forms.ColumnHeader[] {
            this.columnHeader13,
            this.columnHeader14});
            this.lvParameters.Dock = System.Windows.Forms.DockStyle.Fill;
            this.lvParameters.FullRowSelect = true;
            this.lvParameters.GridLines = true;
            this.lvParameters.HideSelection = false;
            this.lvParameters.Location = new System.Drawing.Point(3, 3);
            this.lvParameters.Name = "lvParameters";
            this.lvParameters.Size = new System.Drawing.Size(1001, 311);
            this.lvParameters.TabIndex = 0;
            this.lvParameters.UseCompatibleStateImageBehavior = false;
            this.lvParameters.View = System.Windows.Forms.View.Details;
            // 
            // columnHeader13
            // 
            this.columnHeader13.Text = "参数";
            this.columnHeader13.Width = 150;
            // 
            // columnHeader14
            // 
            this.columnHeader14.Text = "值";
            this.columnHeader14.Width = 450;
            // 
            // tabPage5
            // 
            this.tabPage5.Controls.Add(this.lvError);
            this.tabPage5.Location = new System.Drawing.Point(4, 28);
            this.tabPage5.Name = "tabPage5";
            this.tabPage5.Padding = new System.Windows.Forms.Padding(3, 3, 3, 3);
            this.tabPage5.Size = new System.Drawing.Size(1007, 317);
            this.tabPage5.TabIndex = 4;
            this.tabPage5.Text = "转换误差";
            this.tabPage5.UseVisualStyleBackColor = true;
            // 
            // lvError
            // 
            this.lvError.Columns.AddRange(new System.Windows.Forms.ColumnHeader[] {
            this.columnHeader15,
            this.columnHeader16});
            this.lvError.Dock = System.Windows.Forms.DockStyle.Fill;
            this.lvError.FullRowSelect = true;
            this.lvError.GridLines = true;
            this.lvError.HideSelection = false;
            this.lvError.Location = new System.Drawing.Point(3, 3);
            this.lvError.Name = "lvError";
            this.lvError.Size = new System.Drawing.Size(1001, 311);
            this.lvError.TabIndex = 0;
            this.lvError.UseCompatibleStateImageBehavior = false;
            this.lvError.View = System.Windows.Forms.View.Details;
            // 
            // columnHeader15
            // 
            this.columnHeader15.Text = "指标";
            this.columnHeader15.Width = 150;
            // 
            // columnHeader16
            // 
            this.columnHeader16.Text = "值";
            this.columnHeader16.Width = 450;
            // 
            // openFileDialog1
            // 
            this.openFileDialog1.Filter = "文本文件|*.txt|所有文件|*.*";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("微软雅黑", 10.8F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.label1.ForeColor = System.Drawing.SystemColors.HotTrack;
            this.label1.Location = new System.Drawing.Point(16, 7);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(120, 25);
            this.label1.TabIndex = 11;
            this.label1.Text = "七参数计算：";
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1039, 548);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.tabControl1);
            this.Controls.Add(this.lblTransformPoints);
            this.Controls.Add(this.lblNewPointsPath);
            this.Controls.Add(this.lblOldPointsPath);
            this.Controls.Add(this.txtTransformPoints);
            this.Controls.Add(this.txtNewPointsPath);
            this.Controls.Add(this.txtOldPointsPath);
            this.Controls.Add(this.btnTransform);
            this.Controls.Add(this.btnCalculate);
            this.Controls.Add(this.btnLoadNewPoints);
            this.Controls.Add(this.btnLoadOldPoints);
            this.Name = "Form1";
            this.Text = "七参数坐标转换 - 张洋20232411";
            this.tabControl1.ResumeLayout(false);
            this.tabPage1.ResumeLayout(false);
            this.tabPage2.ResumeLayout(false);
            this.tabPage3.ResumeLayout(false);
            this.tabPage4.ResumeLayout(false);
            this.tabPage5.ResumeLayout(false);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        private System.Windows.Forms.Button btnLoadOldPoints;
        private System.Windows.Forms.Button btnLoadNewPoints;
        private System.Windows.Forms.Button btnCalculate;
        private System.Windows.Forms.Button btnTransform;
        private System.Windows.Forms.TextBox txtOldPointsPath;
        private System.Windows.Forms.TextBox txtNewPointsPath;
        private System.Windows.Forms.TextBox txtTransformPoints;
        private System.Windows.Forms.Label lblOldPointsPath;
        private System.Windows.Forms.Label lblNewPointsPath;
        private System.Windows.Forms.Label lblTransformPoints;
        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage tabPage1;
        private System.Windows.Forms.ListView lvOldPoints;
        private System.Windows.Forms.ColumnHeader columnHeader1;
        private System.Windows.Forms.ColumnHeader columnHeader2;
        private System.Windows.Forms.ColumnHeader columnHeader3;
        private System.Windows.Forms.ColumnHeader columnHeader4;
        private System.Windows.Forms.TabPage tabPage2;
        private System.Windows.Forms.ListView lvNewPoints;
        private System.Windows.Forms.ColumnHeader columnHeader5;
        private System.Windows.Forms.ColumnHeader columnHeader6;
        private System.Windows.Forms.ColumnHeader columnHeader7;
        private System.Windows.Forms.ColumnHeader columnHeader8;
        private System.Windows.Forms.TabPage tabPage3;
        private System.Windows.Forms.ListView lvResult;
        private System.Windows.Forms.ColumnHeader columnHeader9;
        private System.Windows.Forms.ColumnHeader columnHeader10;
        private System.Windows.Forms.ColumnHeader columnHeader11;
        private System.Windows.Forms.ColumnHeader columnHeader12;
        private System.Windows.Forms.TabPage tabPage4;
        private System.Windows.Forms.ListView lvParameters;
        private System.Windows.Forms.ColumnHeader columnHeader13;
        private System.Windows.Forms.ColumnHeader columnHeader14;
        private System.Windows.Forms.TabPage tabPage5;
        private System.Windows.Forms.ListView lvError;
        private System.Windows.Forms.ColumnHeader columnHeader15;
        private System.Windows.Forms.ColumnHeader columnHeader16;
        private System.Windows.Forms.OpenFileDialog openFileDialog1;
        private System.Windows.Forms.Label label1;
    }
}