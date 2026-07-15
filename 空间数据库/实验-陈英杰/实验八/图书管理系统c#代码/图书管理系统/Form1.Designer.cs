namespace 图书管理系统
{
    partial class MainForm
    {
        private System.ComponentModel.IContainer components = null;
        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage tabPageReader;
        private System.Windows.Forms.TabPage tabPageBook;
        private System.Windows.Forms.TabPage tabPageBorrow;
        private System.Windows.Forms.DataGridView readerDataGridView;
        private System.Windows.Forms.DataGridView bookDataGridView;
        private System.Windows.Forms.DataGridView borrowDataGridView;
        private System.Windows.Forms.Button btnAdd;
        private System.Windows.Forms.Button btnModify;
        private System.Windows.Forms.Button btnDelete;
        private System.Windows.Forms.Button btnRefresh;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows 窗体设计器生成的代码

        private void InitializeComponent()
        {
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.tabPageReader = new System.Windows.Forms.TabPage();
            this.readerDataGridView = new System.Windows.Forms.DataGridView();
            this.tabPageBook = new System.Windows.Forms.TabPage();
            this.bookDataGridView = new System.Windows.Forms.DataGridView();
            this.tabPageBorrow = new System.Windows.Forms.TabPage();
            this.borrowDataGridView = new System.Windows.Forms.DataGridView();
            this.btnAdd = new System.Windows.Forms.Button();
            this.btnModify = new System.Windows.Forms.Button();
            this.btnDelete = new System.Windows.Forms.Button();
            this.btnRefresh = new System.Windows.Forms.Button();
            this.tabControl1.SuspendLayout();
            this.tabPageReader.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.readerDataGridView)).BeginInit();
            this.tabPageBook.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.bookDataGridView)).BeginInit();
            this.tabPageBorrow.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.borrowDataGridView)).BeginInit();
            this.SuspendLayout();
            // 
            // tabControl1
            // 
            this.tabControl1.Controls.Add(this.tabPageReader);
            this.tabControl1.Controls.Add(this.tabPageBook);
            this.tabControl1.Controls.Add(this.tabPageBorrow);
            this.tabControl1.Location = new System.Drawing.Point(12, 12);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(776, 340);
            this.tabControl1.TabIndex = 0;
            this.tabControl1.SelectedIndexChanged += new System.EventHandler(this.tabControl1_SelectedIndexChanged);
            // 
            // tabPageReader
            // 
            this.tabPageReader.Controls.Add(this.readerDataGridView);
            this.tabPageReader.Location = new System.Drawing.Point(4, 22);
            this.tabPageReader.Name = "tabPageReader";
            this.tabPageReader.Padding = new System.Windows.Forms.Padding(3);
            this.tabPageReader.Size = new System.Drawing.Size(768, 314);
            this.tabPageReader.TabIndex = 0;
            this.tabPageReader.Text = "读者表";
            this.tabPageReader.UseVisualStyleBackColor = true;
            // 
            // readerDataGridView
            // 
            this.readerDataGridView.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.readerDataGridView.Dock = System.Windows.Forms.DockStyle.Fill;
            this.readerDataGridView.Location = new System.Drawing.Point(3, 3);
            this.readerDataGridView.Name = "readerDataGridView";
            this.readerDataGridView.Size = new System.Drawing.Size(762, 308);
            this.readerDataGridView.TabIndex = 0;
            // 
            // tabPageBook
            // 
            this.tabPageBook.Controls.Add(this.bookDataGridView);
            this.tabPageBook.Location = new System.Drawing.Point(4, 22);
            this.tabPageBook.Name = "tabPageBook";
            this.tabPageBook.Padding = new System.Windows.Forms.Padding(3);
            this.tabPageBook.Size = new System.Drawing.Size(768, 314);
            this.tabPageBook.TabIndex = 1;
            this.tabPageBook.Text = "图书表";
            this.tabPageBook.UseVisualStyleBackColor = true;
            // 
            // bookDataGridView
            // 
            this.bookDataGridView.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.bookDataGridView.Dock = System.Windows.Forms.DockStyle.Fill;
            this.bookDataGridView.Location = new System.Drawing.Point(3, 3);
            this.bookDataGridView.Name = "bookDataGridView";
            this.bookDataGridView.Size = new System.Drawing.Size(762, 308);
            this.bookDataGridView.TabIndex = 0;
            // 
            // tabPageBorrow
            // 
            this.tabPageBorrow.Controls.Add(this.borrowDataGridView);
            this.tabPageBorrow.Location = new System.Drawing.Point(4, 22);
            this.tabPageBorrow.Name = "tabPageBorrow";
            this.tabPageBorrow.Padding = new System.Windows.Forms.Padding(3);
            this.tabPageBorrow.Size = new System.Drawing.Size(768, 314);
            this.tabPageBorrow.TabIndex = 2;
            this.tabPageBorrow.Text = "借书登记表";
            this.tabPageBorrow.UseVisualStyleBackColor = true;
            // 
            // borrowDataGridView
            // 
            this.borrowDataGridView.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.borrowDataGridView.Dock = System.Windows.Forms.DockStyle.Fill;
            this.borrowDataGridView.Location = new System.Drawing.Point(3, 3);
            this.borrowDataGridView.Name = "borrowDataGridView";
            this.borrowDataGridView.Size = new System.Drawing.Size(762, 308);
            this.borrowDataGridView.TabIndex = 0;
            // 
            // btnAdd
            // 
            this.btnAdd.Location = new System.Drawing.Point(12, 368);
            this.btnAdd.Name = "btnAdd";
            this.btnAdd.Size = new System.Drawing.Size(75, 23);
            this.btnAdd.TabIndex = 1;
            this.btnAdd.Text = "添加";
            this.btnAdd.UseVisualStyleBackColor = true;
            this.btnAdd.Click += new System.EventHandler(this.btnAdd_Click);
            // 
            // btnModify
            // 
            this.btnModify.Location = new System.Drawing.Point(93, 368);
            this.btnModify.Name = "btnModify";
            this.btnModify.Size = new System.Drawing.Size(75, 23);
            this.btnModify.TabIndex = 2;
            this.btnModify.Text = "修改";
            this.btnModify.UseVisualStyleBackColor = true;
            this.btnModify.Click += new System.EventHandler(this.btnModify_Click);
            // 
            // btnDelete
            // 
            this.btnDelete.Location = new System.Drawing.Point(174, 368);
            this.btnDelete.Name = "btnDelete";
            this.btnDelete.Size = new System.Drawing.Size(75, 23);
            this.btnDelete.TabIndex = 3;
            this.btnDelete.Text = "删除";
            this.btnDelete.UseVisualStyleBackColor = true;
            this.btnDelete.Click += new System.EventHandler(this.btnDelete_Click);
            // 
            // btnRefresh
            // 
            this.btnRefresh.Location = new System.Drawing.Point(255, 368);
            this.btnRefresh.Name = "btnRefresh";
            this.btnRefresh.Size = new System.Drawing.Size(75, 23);
            this.btnRefresh.TabIndex = 4;
            this.btnRefresh.Text = "刷新";
            this.btnRefresh.UseVisualStyleBackColor = true;
            this.btnRefresh.Click += new System.EventHandler(this.btnRefresh_Click);
            // 
            // MainForm
            // 
            this.ClientSize = new System.Drawing.Size(800, 403);
            this.Controls.Add(this.btnRefresh);
            this.Controls.Add(this.btnDelete);
            this.Controls.Add(this.btnModify);
            this.Controls.Add(this.btnAdd);
            this.Controls.Add(this.tabControl1);
            this.Name = "MainForm";
            this.Text = "图书管理系统";
            this.Load += new System.EventHandler(this.MainForm_Load);
            this.tabControl1.ResumeLayout(false);
            this.tabPageReader.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.readerDataGridView)).EndInit();
            this.tabPageBook.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.bookDataGridView)).EndInit();
            this.tabPageBorrow.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.borrowDataGridView)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion
    }
}