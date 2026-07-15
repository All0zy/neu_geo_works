namespace ITRFCoordinateTransformation
{
    partial class ITRFTransformForm
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

        #region Windows 窗体设计器生成的代码

        /// <summary>
        /// 设计器支持所需的方法 - 不要修改
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent()
        {
            this.lblTitle = new System.Windows.Forms.Label();
            this.lblTargetFrame = new System.Windows.Forms.Label();
            this.cboTargetFrame = new System.Windows.Forms.ComboBox();
            this.lblEpoch = new System.Windows.Forms.Label();
            this.txtEpoch = new System.Windows.Forms.TextBox();
            this.btnTransform = new System.Windows.Forms.Button();
            this.lblResult = new System.Windows.Forms.Label();
            this.dgvInput = new System.Windows.Forms.DataGridView();
            this.dataGridViewTextBoxColumn4 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewTextBoxColumn5 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewTextBoxColumn6 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewTextBoxColumn7 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dgvOutput = new System.Windows.Forms.DataGridView();
            this.dataGridViewTextBoxColumn1 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewTextBoxColumn2 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewTextBoxColumn3 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewTextBoxColumn8 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.btnClear = new System.Windows.Forms.Button();
            ((System.ComponentModel.ISupportInitialize)(this.dgvInput)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.dgvOutput)).BeginInit();
            this.SuspendLayout();
            // 
            // lblTitle
            // 
            this.lblTitle.AutoSize = true;
            this.lblTitle.Font = new System.Drawing.Font("微软雅黑", 16.2F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.lblTitle.ForeColor = System.Drawing.SystemColors.Highlight;
            this.lblTitle.Location = new System.Drawing.Point(22, 19);
            this.lblTitle.Margin = new System.Windows.Forms.Padding(6, 0, 6, 0);
            this.lblTitle.Name = "lblTitle";
            this.lblTitle.Size = new System.Drawing.Size(456, 37);
            this.lblTitle.TabIndex = 0;
            this.lblTitle.Text = "ITRF2020到历史框架坐标转换工具";
            this.lblTitle.Click += new System.EventHandler(this.lblTitle_Click);
            // 
            // lblTargetFrame
            // 
            this.lblTargetFrame.AutoSize = true;
            this.lblTargetFrame.Location = new System.Drawing.Point(24, 87);
            this.lblTargetFrame.Margin = new System.Windows.Forms.Padding(6, 0, 6, 0);
            this.lblTargetFrame.Name = "lblTargetFrame";
            this.lblTargetFrame.Size = new System.Drawing.Size(143, 27);
            this.lblTargetFrame.TabIndex = 7;
            this.lblTargetFrame.Text = "目标ITRF框架:";
            // 
            // cboTargetFrame
            // 
            this.cboTargetFrame.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cboTargetFrame.FormattingEnabled = true;
            this.cboTargetFrame.Items.AddRange(new object[] {
            "ITRF2014",
            "ITRF2008",
            "ITRF2005",
            "ITRF2000",
            "ITRF97",
            "ITRF96",
            "ITRF94",
            "ITRF93",
            "ITRF92",
            "ITRF91",
            "ITRF90",
            "ITRF89",
            "ITRF88"});
            this.cboTargetFrame.Location = new System.Drawing.Point(173, 79);
            this.cboTargetFrame.Margin = new System.Windows.Forms.Padding(6, 7, 6, 7);
            this.cboTargetFrame.Name = "cboTargetFrame";
            this.cboTargetFrame.Size = new System.Drawing.Size(258, 35);
            this.cboTargetFrame.TabIndex = 8;
            // 
            // lblEpoch
            // 
            this.lblEpoch.AutoSize = true;
            this.lblEpoch.Location = new System.Drawing.Point(501, 86);
            this.lblEpoch.Margin = new System.Windows.Forms.Padding(6, 0, 6, 0);
            this.lblEpoch.Name = "lblEpoch";
            this.lblEpoch.Size = new System.Drawing.Size(58, 27);
            this.lblEpoch.TabIndex = 9;
            this.lblEpoch.Text = "历元:";
            // 
            // txtEpoch
            // 
            this.txtEpoch.Location = new System.Drawing.Point(565, 79);
            this.txtEpoch.Margin = new System.Windows.Forms.Padding(6, 7, 6, 7);
            this.txtEpoch.Name = "txtEpoch";
            this.txtEpoch.Size = new System.Drawing.Size(258, 34);
            this.txtEpoch.TabIndex = 10;
            this.txtEpoch.Text = "2020.0";
            // 
            // btnTransform
            // 
            this.btnTransform.BackColor = System.Drawing.SystemColors.Highlight;
            this.btnTransform.Font = new System.Drawing.Font("微软雅黑", 13.8F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnTransform.ForeColor = System.Drawing.SystemColors.HighlightText;
            this.btnTransform.Location = new System.Drawing.Point(29, 128);
            this.btnTransform.Margin = new System.Windows.Forms.Padding(6, 7, 6, 7);
            this.btnTransform.Name = "btnTransform";
            this.btnTransform.Size = new System.Drawing.Size(402, 47);
            this.btnTransform.TabIndex = 11;
            this.btnTransform.Text = "开    始    转    换";
            this.btnTransform.UseVisualStyleBackColor = false;
            this.btnTransform.Click += new System.EventHandler(this.btnTransform_Click);
            // 
            // lblResult
            // 
            this.lblResult.AutoSize = true;
            this.lblResult.Font = new System.Drawing.Font("微软雅黑", 13.8F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.lblResult.ForeColor = System.Drawing.SystemColors.Highlight;
            this.lblResult.Location = new System.Drawing.Point(500, 197);
            this.lblResult.Margin = new System.Windows.Forms.Padding(6, 0, 6, 0);
            this.lblResult.Name = "lblResult";
            this.lblResult.Size = new System.Drawing.Size(0, 31);
            this.lblResult.TabIndex = 12;
            this.lblResult.Click += new System.EventHandler(this.lblResult_Click);
            // 
            // dgvInput
            // 
            this.dgvInput.ColumnHeadersHeight = 29;
            this.dgvInput.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.dataGridViewTextBoxColumn4,
            this.dataGridViewTextBoxColumn5,
            this.dataGridViewTextBoxColumn6,
            this.dataGridViewTextBoxColumn7});
            this.dgvInput.Location = new System.Drawing.Point(29, 197);
            this.dgvInput.Name = "dgvInput";
            this.dgvInput.RowHeadersWidth = 51;
            this.dgvInput.Size = new System.Drawing.Size(794, 171);
            this.dgvInput.TabIndex = 13;
            // 
            // dataGridViewTextBoxColumn4
            // 
            this.dataGridViewTextBoxColumn4.HeaderText = "点号";
            this.dataGridViewTextBoxColumn4.MinimumWidth = 6;
            this.dataGridViewTextBoxColumn4.Name = "dataGridViewTextBoxColumn4";
            this.dataGridViewTextBoxColumn4.Width = 125;
            // 
            // dataGridViewTextBoxColumn5
            // 
            this.dataGridViewTextBoxColumn5.HeaderText = "X";
            this.dataGridViewTextBoxColumn5.MinimumWidth = 6;
            this.dataGridViewTextBoxColumn5.Name = "dataGridViewTextBoxColumn5";
            this.dataGridViewTextBoxColumn5.Width = 125;
            // 
            // dataGridViewTextBoxColumn6
            // 
            this.dataGridViewTextBoxColumn6.HeaderText = "Y";
            this.dataGridViewTextBoxColumn6.MinimumWidth = 6;
            this.dataGridViewTextBoxColumn6.Name = "dataGridViewTextBoxColumn6";
            this.dataGridViewTextBoxColumn6.Width = 125;
            // 
            // dataGridViewTextBoxColumn7
            // 
            this.dataGridViewTextBoxColumn7.HeaderText = "Z";
            this.dataGridViewTextBoxColumn7.MinimumWidth = 6;
            this.dataGridViewTextBoxColumn7.Name = "dataGridViewTextBoxColumn7";
            this.dataGridViewTextBoxColumn7.Width = 125;
            // 
            // dgvOutput
            // 
            this.dgvOutput.ColumnHeadersHeight = 29;
            this.dgvOutput.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.dataGridViewTextBoxColumn1,
            this.dataGridViewTextBoxColumn2,
            this.dataGridViewTextBoxColumn3,
            this.dataGridViewTextBoxColumn8});
            this.dgvOutput.Location = new System.Drawing.Point(29, 393);
            this.dgvOutput.Name = "dgvOutput";
            this.dgvOutput.ReadOnly = true;
            this.dgvOutput.RowHeadersWidth = 51;
            this.dgvOutput.Size = new System.Drawing.Size(794, 171);
            this.dgvOutput.TabIndex = 14;
            // 
            // dataGridViewTextBoxColumn1
            // 
            this.dataGridViewTextBoxColumn1.HeaderText = "点号";
            this.dataGridViewTextBoxColumn1.MinimumWidth = 6;
            this.dataGridViewTextBoxColumn1.Name = "dataGridViewTextBoxColumn1";
            this.dataGridViewTextBoxColumn1.ReadOnly = true;
            this.dataGridViewTextBoxColumn1.Width = 125;
            // 
            // dataGridViewTextBoxColumn2
            // 
            this.dataGridViewTextBoxColumn2.HeaderText = "X";
            this.dataGridViewTextBoxColumn2.MinimumWidth = 6;
            this.dataGridViewTextBoxColumn2.Name = "dataGridViewTextBoxColumn2";
            this.dataGridViewTextBoxColumn2.ReadOnly = true;
            this.dataGridViewTextBoxColumn2.Width = 125;
            // 
            // dataGridViewTextBoxColumn3
            // 
            this.dataGridViewTextBoxColumn3.HeaderText = "Y";
            this.dataGridViewTextBoxColumn3.MinimumWidth = 6;
            this.dataGridViewTextBoxColumn3.Name = "dataGridViewTextBoxColumn3";
            this.dataGridViewTextBoxColumn3.ReadOnly = true;
            this.dataGridViewTextBoxColumn3.Width = 125;
            // 
            // dataGridViewTextBoxColumn8
            // 
            this.dataGridViewTextBoxColumn8.HeaderText = "Z";
            this.dataGridViewTextBoxColumn8.MinimumWidth = 6;
            this.dataGridViewTextBoxColumn8.Name = "dataGridViewTextBoxColumn8";
            this.dataGridViewTextBoxColumn8.ReadOnly = true;
            this.dataGridViewTextBoxColumn8.Width = 125;
            // 
            // btnClear
            // 
            this.btnClear.BackColor = System.Drawing.SystemColors.Highlight;
            this.btnClear.Font = new System.Drawing.Font("微软雅黑", 13.8F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnClear.ForeColor = System.Drawing.SystemColors.HighlightText;
            this.btnClear.Location = new System.Drawing.Point(506, 127);
            this.btnClear.Margin = new System.Windows.Forms.Padding(6, 7, 6, 7);
            this.btnClear.Name = "btnClear";
            this.btnClear.Size = new System.Drawing.Size(317, 48);
            this.btnClear.TabIndex = 15;
            this.btnClear.Text = "清    空";
            this.btnClear.UseVisualStyleBackColor = false;
            this.btnClear.Click += new System.EventHandler(this.btnClear_Click);
            // 
            // ITRFTransformForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(13F, 27F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(855, 598);
            this.Controls.Add(this.btnClear);
            this.Controls.Add(this.dgvOutput);
            this.Controls.Add(this.dgvInput);
            this.Controls.Add(this.lblResult);
            this.Controls.Add(this.btnTransform);
            this.Controls.Add(this.txtEpoch);
            this.Controls.Add(this.lblEpoch);
            this.Controls.Add(this.cboTargetFrame);
            this.Controls.Add(this.lblTargetFrame);
            this.Controls.Add(this.lblTitle);
            this.Font = new System.Drawing.Font("微软雅黑", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.Margin = new System.Windows.Forms.Padding(6, 7, 6, 7);
            this.Name = "ITRFTransformForm";
            this.Text = "ITRF坐标转换工具 - 张洋20232411";
            this.Load += new System.EventHandler(this.ITRFTransformForm_Load);
            ((System.ComponentModel.ISupportInitialize)(this.dgvInput)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.dgvOutput)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label lblTitle;
        private System.Windows.Forms.Label lblTargetFrame;
        private System.Windows.Forms.ComboBox cboTargetFrame;
        private System.Windows.Forms.Label lblEpoch;
        private System.Windows.Forms.TextBox txtEpoch;
        private System.Windows.Forms.Button btnTransform;
        private System.Windows.Forms.Label lblResult;
        private System.Windows.Forms.DataGridView dgvInput;
        private System.Windows.Forms.DataGridView dgvOutput;
        private System.Windows.Forms.Button btnClear;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn4;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn5;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn6;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn7;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn1;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn2;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn3;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn8; // 新增 Z 列声明
    }
}