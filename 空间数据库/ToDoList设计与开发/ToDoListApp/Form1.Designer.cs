namespace ToDoListApp
{
    partial class Form1
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        private void InitializeComponent()
        {
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.tabPagePending = new System.Windows.Forms.TabPage();
            this.panelPendingTasks = new System.Windows.Forms.FlowLayoutPanel();
            this.tabPageCompleted = new System.Windows.Forms.TabPage();
            this.panelCompletedTasks = new System.Windows.Forms.FlowLayoutPanel();
            this.btnAddNew = new System.Windows.Forms.Button();
            this.lblTotalTasks = new System.Windows.Forms.Label();
            this.label1 = new System.Windows.Forms.Label();
            this.cmbPriorityFilter = new System.Windows.Forms.ComboBox();
            this.dtpStartDate = new System.Windows.Forms.DateTimePicker();
            this.dtpEndDate = new System.Windows.Forms.DateTimePicker();
            this.btnFilter = new System.Windows.Forms.Button();
            this.btnResetFilter = new System.Windows.Forms.Button();
            this.label2 = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.tabControl1.SuspendLayout();
            this.tabPagePending.SuspendLayout();
            this.tabPageCompleted.SuspendLayout();
            this.SuspendLayout();
            // 
            // tabControl1
            // 
            this.tabControl1.Controls.Add(this.tabPagePending);
            this.tabControl1.Controls.Add(this.tabPageCompleted);
            this.tabControl1.Font = new System.Drawing.Font("宋体", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.tabControl1.Location = new System.Drawing.Point(14, 49);
            this.tabControl1.Margin = new System.Windows.Forms.Padding(5, 4, 5, 4);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(764, 534);
            this.tabControl1.TabIndex = 0;
            // 
            // tabPagePending
            // 
            this.tabPagePending.Controls.Add(this.panelPendingTasks);
            this.tabPagePending.Location = new System.Drawing.Point(4, 25);
            this.tabPagePending.Margin = new System.Windows.Forms.Padding(5, 4, 5, 4);
            this.tabPagePending.Name = "tabPagePending";
            this.tabPagePending.Padding = new System.Windows.Forms.Padding(5, 4, 5, 4);
            this.tabPagePending.Size = new System.Drawing.Size(756, 505);
            this.tabPagePending.TabIndex = 0;
            this.tabPagePending.Text = "未完成";
            this.tabPagePending.UseVisualStyleBackColor = true;
            this.tabPagePending.Click += new System.EventHandler(this.tabPagePending_Click);
            // 
            // panelPendingTasks
            // 
            this.panelPendingTasks.AutoScroll = true;
            this.panelPendingTasks.FlowDirection = System.Windows.Forms.FlowDirection.TopDown;
            this.panelPendingTasks.Font = new System.Drawing.Font("宋体", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.panelPendingTasks.Location = new System.Drawing.Point(5, 4);
            this.panelPendingTasks.Margin = new System.Windows.Forms.Padding(5, 4, 5, 4);
            this.panelPendingTasks.Name = "panelPendingTasks";
            this.panelPendingTasks.Size = new System.Drawing.Size(746, 531);
            this.panelPendingTasks.TabIndex = 0;
            this.panelPendingTasks.WrapContents = false;
            // 
            // tabPageCompleted
            // 
            this.tabPageCompleted.Controls.Add(this.panelCompletedTasks);
            this.tabPageCompleted.Location = new System.Drawing.Point(4, 25);
            this.tabPageCompleted.Margin = new System.Windows.Forms.Padding(5, 4, 5, 4);
            this.tabPageCompleted.Name = "tabPageCompleted";
            this.tabPageCompleted.Padding = new System.Windows.Forms.Padding(5, 4, 5, 4);
            this.tabPageCompleted.Size = new System.Drawing.Size(756, 505);
            this.tabPageCompleted.TabIndex = 1;
            this.tabPageCompleted.Text = "已完成";
            this.tabPageCompleted.UseVisualStyleBackColor = true;
            // 
            // panelCompletedTasks
            // 
            this.panelCompletedTasks.AutoScroll = true;
            this.panelCompletedTasks.Dock = System.Windows.Forms.DockStyle.Fill;
            this.panelCompletedTasks.FlowDirection = System.Windows.Forms.FlowDirection.TopDown;
            this.panelCompletedTasks.Location = new System.Drawing.Point(5, 4);
            this.panelCompletedTasks.Margin = new System.Windows.Forms.Padding(5, 4, 5, 4);
            this.panelCompletedTasks.Name = "panelCompletedTasks";
            this.panelCompletedTasks.Size = new System.Drawing.Size(746, 497);
            this.panelCompletedTasks.TabIndex = 0;
            this.panelCompletedTasks.WrapContents = false;
            // 
            // btnAddNew
            // 
            this.btnAddNew.BackColor = System.Drawing.Color.OrangeRed;
            this.btnAddNew.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnAddNew.Font = new System.Drawing.Font("微软雅黑", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnAddNew.ForeColor = System.Drawing.Color.White;
            this.btnAddNew.Location = new System.Drawing.Point(796, 390);
            this.btnAddNew.Margin = new System.Windows.Forms.Padding(5, 4, 5, 4);
            this.btnAddNew.Name = "btnAddNew";
            this.btnAddNew.Size = new System.Drawing.Size(191, 51);
            this.btnAddNew.TabIndex = 1;
            this.btnAddNew.Text = "添加新任务";
            this.btnAddNew.UseVisualStyleBackColor = false;
            this.btnAddNew.Click += new System.EventHandler(this.btnAddNew_Click);
            // 
            // lblTotalTasks
            // 
            this.lblTotalTasks.AutoSize = true;
            this.lblTotalTasks.Font = new System.Drawing.Font("微软雅黑", 10.8F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblTotalTasks.Location = new System.Drawing.Point(793, 456);
            this.lblTotalTasks.Margin = new System.Windows.Forms.Padding(5, 0, 5, 0);
            this.lblTotalTasks.Name = "lblTotalTasks";
            this.lblTotalTasks.Size = new System.Drawing.Size(87, 25);
            this.lblTotalTasks.TabIndex = 2;
            this.lblTotalTasks.Text = "总任务: 0";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("微软雅黑", 15F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.label1.Location = new System.Drawing.Point(12, 12);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(536, 33);
            this.label1.TabIndex = 3;
            this.label1.Text = "待办事项清单——基于C#和Access数据库开发";
            // 
            // cmbPriorityFilter
            // 
            this.cmbPriorityFilter.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmbPriorityFilter.FormattingEnabled = true;
            this.cmbPriorityFilter.Items.AddRange(new object[] {
            "所有优先级",
            "高",
            "中",
            "低"});
            this.cmbPriorityFilter.Location = new System.Drawing.Point(796, 132);
            this.cmbPriorityFilter.Name = "cmbPriorityFilter";
            this.cmbPriorityFilter.Size = new System.Drawing.Size(191, 27);
            this.cmbPriorityFilter.TabIndex = 4;
            this.cmbPriorityFilter.SelectedIndexChanged += new System.EventHandler(this.cmbPriorityFilter_SelectedIndexChanged);
            // 
            // dtpStartDate
            // 
            this.dtpStartDate.Format = System.Windows.Forms.DateTimePickerFormat.Short;
            this.dtpStartDate.Location = new System.Drawing.Point(796, 199);
            this.dtpStartDate.Name = "dtpStartDate";
            this.dtpStartDate.Size = new System.Drawing.Size(191, 27);
            this.dtpStartDate.TabIndex = 5;
            // 
            // dtpEndDate
            // 
            this.dtpEndDate.Format = System.Windows.Forms.DateTimePickerFormat.Short;
            this.dtpEndDate.Location = new System.Drawing.Point(796, 232);
            this.dtpEndDate.Name = "dtpEndDate";
            this.dtpEndDate.Size = new System.Drawing.Size(191, 27);
            this.dtpEndDate.TabIndex = 6;
            // 
            // btnFilter
            // 
            this.btnFilter.BackColor = System.Drawing.SystemColors.MenuHighlight;
            this.btnFilter.Font = new System.Drawing.Font("微软雅黑", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnFilter.ForeColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnFilter.Location = new System.Drawing.Point(796, 277);
            this.btnFilter.Name = "btnFilter";
            this.btnFilter.Size = new System.Drawing.Size(191, 50);
            this.btnFilter.TabIndex = 7;
            this.btnFilter.Text = "筛选";
            this.btnFilter.UseVisualStyleBackColor = false;
            this.btnFilter.Click += new System.EventHandler(this.btnFilter_Click);
            // 
            // btnResetFilter
            // 
            this.btnResetFilter.BackColor = System.Drawing.SystemColors.MenuHighlight;
            this.btnResetFilter.Font = new System.Drawing.Font("微软雅黑", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnResetFilter.ForeColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnResetFilter.Location = new System.Drawing.Point(796, 333);
            this.btnResetFilter.Name = "btnResetFilter";
            this.btnResetFilter.Size = new System.Drawing.Size(191, 50);
            this.btnResetFilter.TabIndex = 8;
            this.btnResetFilter.Text = "重置";
            this.btnResetFilter.UseVisualStyleBackColor = false;
            this.btnResetFilter.Click += new System.EventHandler(this.btnResetFilter_Click);
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(793, 106);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(69, 19);
            this.label2.TabIndex = 9;
            this.label2.Text = "优先级：";
            this.label2.Click += new System.EventHandler(this.label2_Click);
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(793, 177);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(84, 19);
            this.label3.TabIndex = 10;
            this.label3.Text = "日期范围：";
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(10F, 19F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1010, 599);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.cmbPriorityFilter);
            this.Controls.Add(this.dtpStartDate);
            this.Controls.Add(this.dtpEndDate);
            this.Controls.Add(this.btnFilter);
            this.Controls.Add(this.btnResetFilter);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.lblTotalTasks);
            this.Controls.Add(this.btnAddNew);
            this.Controls.Add(this.tabControl1);
            this.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.Margin = new System.Windows.Forms.Padding(5, 4, 5, 4);
            this.Name = "Form1";
            this.Text = "待办事项列表 - 张洋20232411";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.tabControl1.ResumeLayout(false);
            this.tabPagePending.ResumeLayout(false);
            this.tabPageCompleted.ResumeLayout(false);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage tabPagePending;
        private System.Windows.Forms.TabPage tabPageCompleted;
        private System.Windows.Forms.Button btnAddNew;
        private System.Windows.Forms.Label lblTotalTasks;
        private System.Windows.Forms.FlowLayoutPanel panelPendingTasks;
        private System.Windows.Forms.FlowLayoutPanel panelCompletedTasks;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label3;
    }
}