
namespace NeuSearch
{
    partial class SearchForm
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
            System.Windows.Forms.DataGridViewCellStyle dataGridViewCellStyle1 = new System.Windows.Forms.DataGridViewCellStyle();
            System.Windows.Forms.DataGridViewCellStyle dataGridViewCellStyle2 = new System.Windows.Forms.DataGridViewCellStyle();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(SearchForm));
            this.tabControlSearchMode = new System.Windows.Forms.TabControl();
            this.tabPageSimple = new System.Windows.Forms.TabPage();
            this.groupBoxSimple = new System.Windows.Forms.GroupBox();
            this.btnSimpleSearch = new System.Windows.Forms.Button();
            this.txtKeyword = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.labelFieldsToSearch = new System.Windows.Forms.Label();
            this.lstSearchFields = new System.Windows.Forms.CheckedListBox();
            this.radioFuzzy = new System.Windows.Forms.RadioButton();
            this.radioExact = new System.Windows.Forms.RadioButton();
            this.tabPageAdvanced = new System.Windows.Forms.TabPage();
            this.groupBoxAdvanced = new System.Windows.Forms.GroupBox();
            this.btnSemanticSQL = new System.Windows.Forms.Button();
            this.flowLayoutPanelOperators = new System.Windows.Forms.FlowLayoutPanel();
            this.btnOpEqual = new System.Windows.Forms.Button();
            this.btnOpNotEqual = new System.Windows.Forms.Button();
            this.btnOpGreater = new System.Windows.Forms.Button();
            this.btnOpLess = new System.Windows.Forms.Button();
            this.btnOpGreaterEqual = new System.Windows.Forms.Button();
            this.btnOpLessEqual = new System.Windows.Forms.Button();
            this.btnOpLeftParen = new System.Windows.Forms.Button();
            this.btnOpRightParen = new System.Windows.Forms.Button();
            this.btnOpOr = new System.Windows.Forms.Button();
            this.button2 = new System.Windows.Forms.Button();
            this.button1 = new System.Windows.Forms.Button();
            this.btnOpLike = new System.Windows.Forms.Button();
            this.btnOpAnd = new System.Windows.Forms.Button();
            this.button3 = new System.Windows.Forms.Button();
            this.txtSqlWhere = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.lstFieldsForSql = new System.Windows.Forms.ListBox();
            this.label4 = new System.Windows.Forms.Label();
            this.btnAdvancedSearch = new System.Windows.Forms.Button();
            this.btnClearSQL = new System.Windows.Forms.Button();
            this.groupBoxLayer = new System.Windows.Forms.GroupBox();
            this.chkAllLayers = new System.Windows.Forms.CheckBox();
            this.lstLayerSelection = new System.Windows.Forms.CheckedListBox();
            this.tabControlResult = new System.Windows.Forms.TabControl();
            this.tabPageList = new System.Windows.Forms.TabPage();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.panelListButtons = new System.Windows.Forms.Panel();
            this.ResultText = new System.Windows.Forms.Label();
            this.btnExportCSV = new System.Windows.Forms.Button();
            this.lblResultCount = new System.Windows.Forms.Label();
            this.tabPageKanban = new System.Windows.Forms.TabPage();
            this.panelKanbanNav = new System.Windows.Forms.Panel();
            this.btnNext = new System.Windows.Forms.Button();
            this.btnPrev = new System.Windows.Forms.Button();
            this.lblKanbanIndex = new System.Windows.Forms.Label();
            this.panelKanban = new System.Windows.Forms.Panel();
            this.tabControlSearchMode.SuspendLayout();
            this.tabPageSimple.SuspendLayout();
            this.groupBoxSimple.SuspendLayout();
            this.tabPageAdvanced.SuspendLayout();
            this.groupBoxAdvanced.SuspendLayout();
            this.flowLayoutPanelOperators.SuspendLayout();
            this.groupBoxLayer.SuspendLayout();
            this.tabControlResult.SuspendLayout();
            this.tabPageList.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            this.panelListButtons.SuspendLayout();
            this.tabPageKanban.SuspendLayout();
            this.panelKanbanNav.SuspendLayout();
            this.SuspendLayout();
            // 
            // tabControlSearchMode
            // 
            this.tabControlSearchMode.Controls.Add(this.tabPageSimple);
            this.tabControlSearchMode.Controls.Add(this.tabPageAdvanced);
            this.tabControlSearchMode.Location = new System.Drawing.Point(238, 15);
            this.tabControlSearchMode.Margin = new System.Windows.Forms.Padding(4);
            this.tabControlSearchMode.Name = "tabControlSearchMode";
            this.tabControlSearchMode.SelectedIndex = 0;
            this.tabControlSearchMode.Size = new System.Drawing.Size(584, 338);
            this.tabControlSearchMode.TabIndex = 1;
            // 
            // tabPageSimple
            // 
            this.tabPageSimple.Controls.Add(this.groupBoxSimple);
            this.tabPageSimple.Location = new System.Drawing.Point(4, 25);
            this.tabPageSimple.Margin = new System.Windows.Forms.Padding(4);
            this.tabPageSimple.Name = "tabPageSimple";
            this.tabPageSimple.Padding = new System.Windows.Forms.Padding(4);
            this.tabPageSimple.Size = new System.Drawing.Size(576, 309);
            this.tabPageSimple.TabIndex = 0;
            this.tabPageSimple.Text = "简单查询";
            this.tabPageSimple.UseVisualStyleBackColor = true;
            // 
            // groupBoxSimple
            // 
            this.groupBoxSimple.Controls.Add(this.btnSimpleSearch);
            this.groupBoxSimple.Controls.Add(this.txtKeyword);
            this.groupBoxSimple.Controls.Add(this.label2);
            this.groupBoxSimple.Controls.Add(this.labelFieldsToSearch);
            this.groupBoxSimple.Controls.Add(this.lstSearchFields);
            this.groupBoxSimple.Controls.Add(this.radioFuzzy);
            this.groupBoxSimple.Controls.Add(this.radioExact);
            this.groupBoxSimple.Location = new System.Drawing.Point(8, 8);
            this.groupBoxSimple.Margin = new System.Windows.Forms.Padding(4);
            this.groupBoxSimple.Name = "groupBoxSimple";
            this.groupBoxSimple.Padding = new System.Windows.Forms.Padding(4);
            this.groupBoxSimple.Size = new System.Drawing.Size(560, 293);
            this.groupBoxSimple.TabIndex = 0;
            this.groupBoxSimple.TabStop = false;
            // 
            // btnSimpleSearch
            // 
            this.btnSimpleSearch.BackColor = System.Drawing.SystemColors.Highlight;
            this.btnSimpleSearch.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnSimpleSearch.ForeColor = System.Drawing.SystemColors.ButtonFace;
            this.btnSimpleSearch.Location = new System.Drawing.Point(365, 133);
            this.btnSimpleSearch.Margin = new System.Windows.Forms.Padding(4);
            this.btnSimpleSearch.Name = "btnSimpleSearch";
            this.btnSimpleSearch.Size = new System.Drawing.Size(90, 42);
            this.btnSimpleSearch.TabIndex = 2;
            this.btnSimpleSearch.Text = "查询";
            this.btnSimpleSearch.UseVisualStyleBackColor = false;
            this.btnSimpleSearch.Click += new System.EventHandler(this.btnSimpleSearch_Click);
            // 
            // txtKeyword
            // 
            this.txtKeyword.Font = new System.Drawing.Font("宋体", 10.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.txtKeyword.Location = new System.Drawing.Point(85, 20);
            this.txtKeyword.Margin = new System.Windows.Forms.Padding(4);
            this.txtKeyword.Name = "txtKeyword";
            this.txtKeyword.Size = new System.Drawing.Size(463, 28);
            this.txtKeyword.TabIndex = 1;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.label2.Location = new System.Drawing.Point(8, 29);
            this.label2.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(69, 19);
            this.label2.TabIndex = 0;
            this.label2.Text = "请输入：";
            // 
            // labelFieldsToSearch
            // 
            this.labelFieldsToSearch.AutoSize = true;
            this.labelFieldsToSearch.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.labelFieldsToSearch.Location = new System.Drawing.Point(8, 60);
            this.labelFieldsToSearch.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.labelFieldsToSearch.Name = "labelFieldsToSearch";
            this.labelFieldsToSearch.Size = new System.Drawing.Size(84, 19);
            this.labelFieldsToSearch.TabIndex = 3;
            this.labelFieldsToSearch.Text = "查询字段：";
            // 
            // lstSearchFields
            // 
            this.lstSearchFields.CheckOnClick = true;
            this.lstSearchFields.Location = new System.Drawing.Point(123, 60);
            this.lstSearchFields.Margin = new System.Windows.Forms.Padding(4);
            this.lstSearchFields.Name = "lstSearchFields";
            this.lstSearchFields.Size = new System.Drawing.Size(200, 224);
            this.lstSearchFields.TabIndex = 4;
            // 
            // radioFuzzy
            // 
            this.radioFuzzy.AutoSize = true;
            this.radioFuzzy.Checked = true;
            this.radioFuzzy.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.radioFuzzy.Location = new System.Drawing.Point(365, 63);
            this.radioFuzzy.Name = "radioFuzzy";
            this.radioFuzzy.Size = new System.Drawing.Size(90, 24);
            this.radioFuzzy.TabIndex = 5;
            this.radioFuzzy.TabStop = true;
            this.radioFuzzy.Text = "模糊匹配";
            // 
            // radioExact
            // 
            this.radioExact.AutoSize = true;
            this.radioExact.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.radioExact.Location = new System.Drawing.Point(365, 93);
            this.radioExact.Name = "radioExact";
            this.radioExact.Size = new System.Drawing.Size(90, 24);
            this.radioExact.TabIndex = 6;
            this.radioExact.Text = "精确匹配";
            // 
            // tabPageAdvanced
            // 
            this.tabPageAdvanced.Controls.Add(this.groupBoxAdvanced);
            this.tabPageAdvanced.Location = new System.Drawing.Point(4, 25);
            this.tabPageAdvanced.Margin = new System.Windows.Forms.Padding(4);
            this.tabPageAdvanced.Name = "tabPageAdvanced";
            this.tabPageAdvanced.Padding = new System.Windows.Forms.Padding(4);
            this.tabPageAdvanced.Size = new System.Drawing.Size(576, 309);
            this.tabPageAdvanced.TabIndex = 1;
            this.tabPageAdvanced.Text = "SQL高级查询";
            this.tabPageAdvanced.UseVisualStyleBackColor = true;
            // 
            // groupBoxAdvanced
            // 
            this.groupBoxAdvanced.Controls.Add(this.btnSemanticSQL);
            this.groupBoxAdvanced.Controls.Add(this.flowLayoutPanelOperators);
            this.groupBoxAdvanced.Controls.Add(this.txtSqlWhere);
            this.groupBoxAdvanced.Controls.Add(this.btnClearSQL);
            this.groupBoxAdvanced.Controls.Add(this.label3);
            this.groupBoxAdvanced.Controls.Add(this.lstFieldsForSql);
            this.groupBoxAdvanced.Controls.Add(this.label4);
            this.groupBoxAdvanced.Controls.Add(this.btnAdvancedSearch);
            this.groupBoxAdvanced.Location = new System.Drawing.Point(8, 0);
            this.groupBoxAdvanced.Margin = new System.Windows.Forms.Padding(4);
            this.groupBoxAdvanced.Name = "groupBoxAdvanced";
            this.groupBoxAdvanced.Padding = new System.Windows.Forms.Padding(4);
            this.groupBoxAdvanced.Size = new System.Drawing.Size(560, 301);
            this.groupBoxAdvanced.TabIndex = 0;
            this.groupBoxAdvanced.TabStop = false;
            // 
            // btnSemanticSQL
            // 
            this.btnSemanticSQL.BackColor = System.Drawing.SystemColors.Highlight;
            this.btnSemanticSQL.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnSemanticSQL.ForeColor = System.Drawing.SystemColors.HighlightText;
            this.btnSemanticSQL.Location = new System.Drawing.Point(98, 246);
            this.btnSemanticSQL.Name = "btnSemanticSQL";
            this.btnSemanticSQL.Size = new System.Drawing.Size(165, 39);
            this.btnSemanticSQL.TabIndex = 15;
            this.btnSemanticSQL.Text = "语义构建SQL";
            this.btnSemanticSQL.UseVisualStyleBackColor = false;
            this.btnSemanticSQL.Click += new System.EventHandler(this.btnSemanticSQL_Click);
            // 
            // flowLayoutPanelOperators
            // 
            this.flowLayoutPanelOperators.Controls.Add(this.btnOpEqual);
            this.flowLayoutPanelOperators.Controls.Add(this.btnOpNotEqual);
            this.flowLayoutPanelOperators.Controls.Add(this.btnOpGreater);
            this.flowLayoutPanelOperators.Controls.Add(this.btnOpLess);
            this.flowLayoutPanelOperators.Controls.Add(this.btnOpGreaterEqual);
            this.flowLayoutPanelOperators.Controls.Add(this.btnOpLessEqual);
            this.flowLayoutPanelOperators.Controls.Add(this.btnOpLeftParen);
            this.flowLayoutPanelOperators.Controls.Add(this.btnOpRightParen);
            this.flowLayoutPanelOperators.Controls.Add(this.btnOpOr);
            this.flowLayoutPanelOperators.Controls.Add(this.button2);
            this.flowLayoutPanelOperators.Controls.Add(this.button1);
            this.flowLayoutPanelOperators.Controls.Add(this.btnOpLike);
            this.flowLayoutPanelOperators.Controls.Add(this.btnOpAnd);
            this.flowLayoutPanelOperators.Controls.Add(this.button3);
            this.flowLayoutPanelOperators.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.flowLayoutPanelOperators.Location = new System.Drawing.Point(11, 133);
            this.flowLayoutPanelOperators.Name = "flowLayoutPanelOperators";
            this.flowLayoutPanelOperators.Size = new System.Drawing.Size(359, 107);
            this.flowLayoutPanelOperators.TabIndex = 6;
            // 
            // btnOpEqual
            // 
            this.btnOpEqual.BackColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnOpEqual.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnOpEqual.Location = new System.Drawing.Point(3, 3);
            this.btnOpEqual.Name = "btnOpEqual";
            this.btnOpEqual.Size = new System.Drawing.Size(50, 29);
            this.btnOpEqual.TabIndex = 0;
            this.btnOpEqual.Text = "=";
            this.btnOpEqual.UseVisualStyleBackColor = false;
            this.btnOpEqual.Click += new System.EventHandler(this.InsertOperatorToSql);
            // 
            // btnOpNotEqual
            // 
            this.btnOpNotEqual.BackColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnOpNotEqual.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnOpNotEqual.Location = new System.Drawing.Point(59, 3);
            this.btnOpNotEqual.Name = "btnOpNotEqual";
            this.btnOpNotEqual.Size = new System.Drawing.Size(50, 29);
            this.btnOpNotEqual.TabIndex = 1;
            this.btnOpNotEqual.Text = "<>";
            this.btnOpNotEqual.UseVisualStyleBackColor = false;
            this.btnOpNotEqual.Click += new System.EventHandler(this.InsertOperatorToSql);
            // 
            // btnOpGreater
            // 
            this.btnOpGreater.BackColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnOpGreater.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnOpGreater.Location = new System.Drawing.Point(115, 3);
            this.btnOpGreater.Name = "btnOpGreater";
            this.btnOpGreater.Size = new System.Drawing.Size(50, 29);
            this.btnOpGreater.TabIndex = 2;
            this.btnOpGreater.Text = ">";
            this.btnOpGreater.UseVisualStyleBackColor = false;
            this.btnOpGreater.Click += new System.EventHandler(this.InsertOperatorToSql);
            // 
            // btnOpLess
            // 
            this.btnOpLess.BackColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnOpLess.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnOpLess.Location = new System.Drawing.Point(171, 3);
            this.btnOpLess.Name = "btnOpLess";
            this.btnOpLess.Size = new System.Drawing.Size(50, 29);
            this.btnOpLess.TabIndex = 3;
            this.btnOpLess.Text = "<";
            this.btnOpLess.UseVisualStyleBackColor = false;
            this.btnOpLess.Click += new System.EventHandler(this.InsertOperatorToSql);
            // 
            // btnOpGreaterEqual
            // 
            this.btnOpGreaterEqual.BackColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnOpGreaterEqual.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnOpGreaterEqual.Location = new System.Drawing.Point(227, 3);
            this.btnOpGreaterEqual.Name = "btnOpGreaterEqual";
            this.btnOpGreaterEqual.Size = new System.Drawing.Size(50, 29);
            this.btnOpGreaterEqual.TabIndex = 4;
            this.btnOpGreaterEqual.Text = ">=";
            this.btnOpGreaterEqual.UseVisualStyleBackColor = false;
            this.btnOpGreaterEqual.Click += new System.EventHandler(this.InsertOperatorToSql);
            // 
            // btnOpLessEqual
            // 
            this.btnOpLessEqual.BackColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnOpLessEqual.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnOpLessEqual.Location = new System.Drawing.Point(283, 3);
            this.btnOpLessEqual.Name = "btnOpLessEqual";
            this.btnOpLessEqual.Size = new System.Drawing.Size(50, 29);
            this.btnOpLessEqual.TabIndex = 5;
            this.btnOpLessEqual.Text = "<=";
            this.btnOpLessEqual.UseVisualStyleBackColor = false;
            this.btnOpLessEqual.Click += new System.EventHandler(this.InsertOperatorToSql);
            // 
            // btnOpLeftParen
            // 
            this.btnOpLeftParen.BackColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnOpLeftParen.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnOpLeftParen.Location = new System.Drawing.Point(3, 38);
            this.btnOpLeftParen.Name = "btnOpLeftParen";
            this.btnOpLeftParen.Size = new System.Drawing.Size(50, 29);
            this.btnOpLeftParen.TabIndex = 11;
            this.btnOpLeftParen.Text = "(";
            this.btnOpLeftParen.UseVisualStyleBackColor = false;
            this.btnOpLeftParen.Click += new System.EventHandler(this.InsertOperatorToSql);
            // 
            // btnOpRightParen
            // 
            this.btnOpRightParen.BackColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnOpRightParen.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnOpRightParen.Location = new System.Drawing.Point(59, 38);
            this.btnOpRightParen.Name = "btnOpRightParen";
            this.btnOpRightParen.Size = new System.Drawing.Size(50, 29);
            this.btnOpRightParen.TabIndex = 12;
            this.btnOpRightParen.Text = ")";
            this.btnOpRightParen.UseVisualStyleBackColor = false;
            this.btnOpRightParen.Click += new System.EventHandler(this.InsertOperatorToSql);
            // 
            // btnOpOr
            // 
            this.btnOpOr.BackColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnOpOr.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnOpOr.Location = new System.Drawing.Point(115, 38);
            this.btnOpOr.Name = "btnOpOr";
            this.btnOpOr.Size = new System.Drawing.Size(50, 29);
            this.btnOpOr.TabIndex = 10;
            this.btnOpOr.Text = "OR";
            this.btnOpOr.UseVisualStyleBackColor = false;
            this.btnOpOr.Click += new System.EventHandler(this.InsertOperatorToSql);
            // 
            // button2
            // 
            this.button2.BackColor = System.Drawing.SystemColors.ButtonHighlight;
            this.button2.Location = new System.Drawing.Point(171, 38);
            this.button2.Name = "button2";
            this.button2.Size = new System.Drawing.Size(50, 29);
            this.button2.TabIndex = 14;
            this.button2.Text = "IN";
            this.button2.UseVisualStyleBackColor = false;
            // 
            // button1
            // 
            this.button1.BackColor = System.Drawing.SystemColors.ButtonHighlight;
            this.button1.Location = new System.Drawing.Point(227, 38);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(106, 29);
            this.button1.TabIndex = 13;
            this.button1.Text = "BETWEEN";
            this.button1.UseVisualStyleBackColor = false;
            // 
            // btnOpLike
            // 
            this.btnOpLike.BackColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnOpLike.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnOpLike.Location = new System.Drawing.Point(3, 73);
            this.btnOpLike.Name = "btnOpLike";
            this.btnOpLike.Size = new System.Drawing.Size(106, 29);
            this.btnOpLike.TabIndex = 8;
            this.btnOpLike.Text = "LIKE";
            this.btnOpLike.UseVisualStyleBackColor = false;
            this.btnOpLike.Click += new System.EventHandler(this.InsertOperatorToSql);
            // 
            // btnOpAnd
            // 
            this.btnOpAnd.BackColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnOpAnd.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnOpAnd.Location = new System.Drawing.Point(115, 73);
            this.btnOpAnd.Name = "btnOpAnd";
            this.btnOpAnd.Size = new System.Drawing.Size(106, 29);
            this.btnOpAnd.TabIndex = 9;
            this.btnOpAnd.Text = "AND";
            this.btnOpAnd.UseVisualStyleBackColor = false;
            this.btnOpAnd.Click += new System.EventHandler(this.InsertOperatorToSql);
            // 
            // button3
            // 
            this.button3.BackColor = System.Drawing.SystemColors.ButtonHighlight;
            this.button3.Location = new System.Drawing.Point(227, 73);
            this.button3.Name = "button3";
            this.button3.Size = new System.Drawing.Size(106, 29);
            this.button3.TabIndex = 15;
            this.button3.Text = "NOT";
            this.button3.UseVisualStyleBackColor = false;
            // 
            // txtSqlWhere
            // 
            this.txtSqlWhere.Location = new System.Drawing.Point(11, 41);
            this.txtSqlWhere.Margin = new System.Windows.Forms.Padding(4);
            this.txtSqlWhere.Multiline = true;
            this.txtSqlWhere.Name = "txtSqlWhere";
            this.txtSqlWhere.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtSqlWhere.Size = new System.Drawing.Size(359, 85);
            this.txtSqlWhere.TabIndex = 5;
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.label3.Location = new System.Drawing.Point(9, 16);
            this.label3.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(114, 19);
            this.label3.TabIndex = 4;
            this.label3.Text = "WHERE 条件：";
            // 
            // lstFieldsForSql
            // 
            this.lstFieldsForSql.FormattingEnabled = true;
            this.lstFieldsForSql.ItemHeight = 15;
            this.lstFieldsForSql.Location = new System.Drawing.Point(377, 41);
            this.lstFieldsForSql.Margin = new System.Windows.Forms.Padding(4);
            this.lstFieldsForSql.Name = "lstFieldsForSql";
            this.lstFieldsForSql.Size = new System.Drawing.Size(171, 244);
            this.lstFieldsForSql.TabIndex = 3;
            this.lstFieldsForSql.MouseDoubleClick += new System.Windows.Forms.MouseEventHandler(this.lstFieldsForSql_MouseDoubleClick);
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(374, 16);
            this.label4.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(82, 15);
            this.label4.TabIndex = 2;
            this.label4.Text = "字段列表：";
            // 
            // btnAdvancedSearch
            // 
            this.btnAdvancedSearch.BackColor = System.Drawing.SystemColors.Highlight;
            this.btnAdvancedSearch.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnAdvancedSearch.ForeColor = System.Drawing.SystemColors.ButtonHighlight;
            this.btnAdvancedSearch.Location = new System.Drawing.Point(270, 246);
            this.btnAdvancedSearch.Margin = new System.Windows.Forms.Padding(4);
            this.btnAdvancedSearch.Name = "btnAdvancedSearch";
            this.btnAdvancedSearch.Size = new System.Drawing.Size(100, 39);
            this.btnAdvancedSearch.TabIndex = 1;
            this.btnAdvancedSearch.Text = "查询";
            this.btnAdvancedSearch.UseVisualStyleBackColor = false;
            this.btnAdvancedSearch.Click += new System.EventHandler(this.btnAdvancedSearch_Click);
            // 
            // btnClearSQL
            // 
            this.btnClearSQL.BackColor = System.Drawing.Color.Crimson;
            this.btnClearSQL.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnClearSQL.ForeColor = System.Drawing.SystemColors.ControlLightLight;
            this.btnClearSQL.Location = new System.Drawing.Point(11, 246);
            this.btnClearSQL.Name = "btnClearSQL";
            this.btnClearSQL.Size = new System.Drawing.Size(81, 39);
            this.btnClearSQL.TabIndex = 14;
            this.btnClearSQL.Text = "清空";
            this.btnClearSQL.UseVisualStyleBackColor = false;
            this.btnClearSQL.Click += new System.EventHandler(this.btnClearSQL_Click);
            // 
            // groupBoxLayer
            // 
            this.groupBoxLayer.Controls.Add(this.chkAllLayers);
            this.groupBoxLayer.Controls.Add(this.lstLayerSelection);
            this.groupBoxLayer.Location = new System.Drawing.Point(16, 15);
            this.groupBoxLayer.Margin = new System.Windows.Forms.Padding(4);
            this.groupBoxLayer.Name = "groupBoxLayer";
            this.groupBoxLayer.Padding = new System.Windows.Forms.Padding(4);
            this.groupBoxLayer.Size = new System.Drawing.Size(214, 338);
            this.groupBoxLayer.TabIndex = 0;
            this.groupBoxLayer.TabStop = false;
            this.groupBoxLayer.Text = "选择图层";
            // 
            // chkAllLayers
            // 
            this.chkAllLayers.AutoSize = true;
            this.chkAllLayers.Checked = true;
            this.chkAllLayers.CheckState = System.Windows.Forms.CheckState.Checked;
            this.chkAllLayers.Location = new System.Drawing.Point(12, 22);
            this.chkAllLayers.Margin = new System.Windows.Forms.Padding(4);
            this.chkAllLayers.Name = "chkAllLayers";
            this.chkAllLayers.Size = new System.Drawing.Size(89, 19);
            this.chkAllLayers.TabIndex = 1;
            this.chkAllLayers.Text = "全部图层";
            this.chkAllLayers.UseVisualStyleBackColor = true;
            this.chkAllLayers.CheckedChanged += new System.EventHandler(this.chkAllLayers_CheckedChanged);
            // 
            // lstLayerSelection
            // 
            this.lstLayerSelection.CheckOnClick = true;
            this.lstLayerSelection.Location = new System.Drawing.Point(9, 62);
            this.lstLayerSelection.Margin = new System.Windows.Forms.Padding(4);
            this.lstLayerSelection.Name = "lstLayerSelection";
            this.lstLayerSelection.Size = new System.Drawing.Size(197, 264);
            this.lstLayerSelection.TabIndex = 0;
            // 
            // tabControlResult
            // 
            this.tabControlResult.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.tabControlResult.Controls.Add(this.tabPageList);
            this.tabControlResult.Controls.Add(this.tabPageKanban);
            this.tabControlResult.Location = new System.Drawing.Point(16, 362);
            this.tabControlResult.Margin = new System.Windows.Forms.Padding(4);
            this.tabControlResult.Name = "tabControlResult";
            this.tabControlResult.SelectedIndex = 0;
            this.tabControlResult.Size = new System.Drawing.Size(798, 353);
            this.tabControlResult.TabIndex = 3;
            this.tabControlResult.SelectedIndexChanged += new System.EventHandler(this.tabControlResult_SelectedIndexChanged);
            // 
            // tabPageList
            // 
            this.tabPageList.Controls.Add(this.dataGridView1);
            this.tabPageList.Controls.Add(this.panelListButtons);
            this.tabPageList.Location = new System.Drawing.Point(4, 25);
            this.tabPageList.Margin = new System.Windows.Forms.Padding(4);
            this.tabPageList.Name = "tabPageList";
            this.tabPageList.Padding = new System.Windows.Forms.Padding(4);
            this.tabPageList.Size = new System.Drawing.Size(790, 324);
            this.tabPageList.TabIndex = 0;
            this.tabPageList.Text = "列表视图";
            this.tabPageList.UseVisualStyleBackColor = true;
            // 
            // dataGridView1
            // 
            this.dataGridView1.AllowUserToAddRows = false;
            this.dataGridView1.AllowUserToDeleteRows = false;
            this.dataGridView1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.dataGridView1.BackgroundColor = System.Drawing.SystemColors.ControlLight;
            dataGridViewCellStyle1.Alignment = System.Windows.Forms.DataGridViewContentAlignment.MiddleLeft;
            dataGridViewCellStyle1.BackColor = System.Drawing.SystemColors.Control;
            dataGridViewCellStyle1.Font = new System.Drawing.Font("宋体", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            dataGridViewCellStyle1.ForeColor = System.Drawing.SystemColors.WindowText;
            dataGridViewCellStyle1.SelectionBackColor = System.Drawing.SystemColors.Highlight;
            dataGridViewCellStyle1.SelectionForeColor = System.Drawing.SystemColors.HighlightText;
            dataGridViewCellStyle1.WrapMode = System.Windows.Forms.DataGridViewTriState.True;
            this.dataGridView1.ColumnHeadersDefaultCellStyle = dataGridViewCellStyle1;
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            dataGridViewCellStyle2.Alignment = System.Windows.Forms.DataGridViewContentAlignment.MiddleLeft;
            dataGridViewCellStyle2.BackColor = System.Drawing.SystemColors.Window;
            dataGridViewCellStyle2.Font = new System.Drawing.Font("宋体", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            dataGridViewCellStyle2.ForeColor = System.Drawing.SystemColors.ControlText;
            dataGridViewCellStyle2.SelectionBackColor = System.Drawing.SystemColors.Highlight;
            dataGridViewCellStyle2.SelectionForeColor = System.Drawing.SystemColors.HighlightText;
            dataGridViewCellStyle2.WrapMode = System.Windows.Forms.DataGridViewTriState.False;
            this.dataGridView1.DefaultCellStyle = dataGridViewCellStyle2;
            this.dataGridView1.Location = new System.Drawing.Point(8, 8);
            this.dataGridView1.Margin = new System.Windows.Forms.Padding(4);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.ReadOnly = true;
            this.dataGridView1.RowTemplate.Height = 23;
            this.dataGridView1.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dataGridView1.Size = new System.Drawing.Size(774, 229);
            this.dataGridView1.TabIndex = 0;
            this.dataGridView1.SelectionChanged += new System.EventHandler(this.dataGridView1_SelectionChanged);
            // 
            // panelListButtons
            // 
            this.panelListButtons.Controls.Add(this.ResultText);
            this.panelListButtons.Controls.Add(this.btnExportCSV);
            this.panelListButtons.Controls.Add(this.lblResultCount);
            this.panelListButtons.Dock = System.Windows.Forms.DockStyle.Bottom;
            this.panelListButtons.Location = new System.Drawing.Point(4, 245);
            this.panelListButtons.Margin = new System.Windows.Forms.Padding(4);
            this.panelListButtons.Name = "panelListButtons";
            this.panelListButtons.Size = new System.Drawing.Size(782, 75);
            this.panelListButtons.TabIndex = 1;
            // 
            // ResultText
            // 
            this.ResultText.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.ResultText.Location = new System.Drawing.Point(7, 6);
            this.ResultText.Name = "ResultText";
            this.ResultText.Size = new System.Drawing.Size(632, 63);
            this.ResultText.TabIndex = 2;
            this.ResultText.Text = "查询合计：";
            // 
            // btnExportCSV
            // 
            this.btnExportCSV.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.btnExportCSV.BackColor = System.Drawing.SystemColors.Highlight;
            this.btnExportCSV.Font = new System.Drawing.Font("微软雅黑", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.btnExportCSV.ForeColor = System.Drawing.SystemColors.ControlLightLight;
            this.btnExportCSV.Location = new System.Drawing.Point(646, 15);
            this.btnExportCSV.Margin = new System.Windows.Forms.Padding(4);
            this.btnExportCSV.Name = "btnExportCSV";
            this.btnExportCSV.Size = new System.Drawing.Size(128, 41);
            this.btnExportCSV.TabIndex = 1;
            this.btnExportCSV.Text = "导出 CSV";
            this.btnExportCSV.UseVisualStyleBackColor = false;
            this.btnExportCSV.Click += new System.EventHandler(this.btnExportCSV_Click);
            // 
            // lblResultCount
            // 
            this.lblResultCount.AutoSize = true;
            this.lblResultCount.Location = new System.Drawing.Point(8, 12);
            this.lblResultCount.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.lblResultCount.Name = "lblResultCount";
            this.lblResultCount.Size = new System.Drawing.Size(0, 15);
            this.lblResultCount.TabIndex = 0;
            // 
            // tabPageKanban
            // 
            this.tabPageKanban.Controls.Add(this.panelKanbanNav);
            this.tabPageKanban.Controls.Add(this.panelKanban);
            this.tabPageKanban.Location = new System.Drawing.Point(4, 25);
            this.tabPageKanban.Margin = new System.Windows.Forms.Padding(4);
            this.tabPageKanban.Name = "tabPageKanban";
            this.tabPageKanban.Padding = new System.Windows.Forms.Padding(4);
            this.tabPageKanban.Size = new System.Drawing.Size(790, 324);
            this.tabPageKanban.TabIndex = 1;
            this.tabPageKanban.Text = "看板视图";
            this.tabPageKanban.UseVisualStyleBackColor = true;
            // 
            // panelKanbanNav
            // 
            this.panelKanbanNav.Controls.Add(this.btnNext);
            this.panelKanbanNav.Controls.Add(this.btnPrev);
            this.panelKanbanNav.Controls.Add(this.lblKanbanIndex);
            this.panelKanbanNav.Dock = System.Windows.Forms.DockStyle.Bottom;
            this.panelKanbanNav.Location = new System.Drawing.Point(4, 284);
            this.panelKanbanNav.Margin = new System.Windows.Forms.Padding(4);
            this.panelKanbanNav.Name = "panelKanbanNav";
            this.panelKanbanNav.Size = new System.Drawing.Size(782, 36);
            this.panelKanbanNav.TabIndex = 1;
            // 
            // btnNext
            // 
            this.btnNext.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.btnNext.Location = new System.Drawing.Point(694, 4);
            this.btnNext.Margin = new System.Windows.Forms.Padding(4);
            this.btnNext.Name = "btnNext";
            this.btnNext.Size = new System.Drawing.Size(80, 29);
            this.btnNext.TabIndex = 2;
            this.btnNext.Text = ">";
            this.btnNext.UseVisualStyleBackColor = true;
            this.btnNext.Click += new System.EventHandler(this.btnNext_Click);
            // 
            // btnPrev
            // 
            this.btnPrev.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.btnPrev.Location = new System.Drawing.Point(606, 4);
            this.btnPrev.Margin = new System.Windows.Forms.Padding(4);
            this.btnPrev.Name = "btnPrev";
            this.btnPrev.Size = new System.Drawing.Size(80, 29);
            this.btnPrev.TabIndex = 1;
            this.btnPrev.Text = "<";
            this.btnPrev.UseVisualStyleBackColor = true;
            this.btnPrev.Click += new System.EventHandler(this.btnPrev_Click);
            // 
            // lblKanbanIndex
            // 
            this.lblKanbanIndex.AutoSize = true;
            this.lblKanbanIndex.Location = new System.Drawing.Point(8, 10);
            this.lblKanbanIndex.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.lblKanbanIndex.Name = "lblKanbanIndex";
            this.lblKanbanIndex.Size = new System.Drawing.Size(0, 15);
            this.lblKanbanIndex.TabIndex = 0;
            // 
            // panelKanban
            // 
            this.panelKanban.AutoScroll = true;
            this.panelKanban.Dock = System.Windows.Forms.DockStyle.Fill;
            this.panelKanban.Location = new System.Drawing.Point(4, 4);
            this.panelKanban.Margin = new System.Windows.Forms.Padding(4);
            this.panelKanban.Name = "panelKanban";
            this.panelKanban.Size = new System.Drawing.Size(782, 316);
            this.panelKanban.TabIndex = 0;
            // 
            // SearchForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.AutoValidate = System.Windows.Forms.AutoValidate.EnablePreventFocusChange;
            this.ClientSize = new System.Drawing.Size(830, 728);
            this.Controls.Add(this.tabControlResult);
            this.Controls.Add(this.tabControlSearchMode);
            this.Controls.Add(this.groupBoxLayer);
            this.Font = new System.Drawing.Font("宋体", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.Fixed3D;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Margin = new System.Windows.Forms.Padding(4);
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "SearchForm";
            this.Text = "要素查询工具 - 张洋20232411";
            this.tabControlSearchMode.ResumeLayout(false);
            this.tabPageSimple.ResumeLayout(false);
            this.groupBoxSimple.ResumeLayout(false);
            this.groupBoxSimple.PerformLayout();
            this.tabPageAdvanced.ResumeLayout(false);
            this.groupBoxAdvanced.ResumeLayout(false);
            this.groupBoxAdvanced.PerformLayout();
            this.flowLayoutPanelOperators.ResumeLayout(false);
            this.groupBoxLayer.ResumeLayout(false);
            this.groupBoxLayer.PerformLayout();
            this.tabControlResult.ResumeLayout(false);
            this.tabPageList.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.panelListButtons.ResumeLayout(false);
            this.panelListButtons.PerformLayout();
            this.tabPageKanban.ResumeLayout(false);
            this.panelKanbanNav.ResumeLayout(false);
            this.panelKanbanNav.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.GroupBox groupBoxLayer;
        private System.Windows.Forms.CheckedListBox lstLayerSelection;
        private System.Windows.Forms.CheckBox chkAllLayers;
        private System.Windows.Forms.TabControl tabControlResult;
        private System.Windows.Forms.TabPage tabPageList;
        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.TabPage tabPageKanban;
        private System.Windows.Forms.Panel panelKanban;
        private System.Windows.Forms.Panel panelKanbanNav;
        private System.Windows.Forms.Button btnNext;
        private System.Windows.Forms.Button btnPrev;
        private System.Windows.Forms.Label lblKanbanIndex;
        private System.Windows.Forms.Panel panelListButtons;
        private System.Windows.Forms.Button btnExportCSV;
        private System.Windows.Forms.Label lblResultCount;
        private System.Windows.Forms.TabControl tabControlSearchMode;
        private System.Windows.Forms.TabPage tabPageSimple;
        private System.Windows.Forms.GroupBox groupBoxSimple;
        private System.Windows.Forms.Button btnSimpleSearch;
        private System.Windows.Forms.TextBox txtKeyword;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TabPage tabPageAdvanced;
        private System.Windows.Forms.GroupBox groupBoxAdvanced;
        private System.Windows.Forms.Button btnAdvancedSearch;
        private System.Windows.Forms.ListBox lstFieldsForSql;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.TextBox txtSqlWhere;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.FlowLayoutPanel flowLayoutPanelOperators;
        private System.Windows.Forms.Button btnOpEqual;
        private System.Windows.Forms.Button btnOpNotEqual;
        private System.Windows.Forms.Button btnOpLike;
        private System.Windows.Forms.Button btnOpAnd;
        private System.Windows.Forms.Button btnOpOr;
        private System.Windows.Forms.Button btnOpLeftParen;
        private System.Windows.Forms.Button btnOpRightParen;
        private System.Windows.Forms.Button btnClearSQL;
        // 新增的比较运算符按钮
        private System.Windows.Forms.Button btnOpGreater;
        private System.Windows.Forms.Button btnOpLess;
        private System.Windows.Forms.Button btnOpGreaterEqual;
        private System.Windows.Forms.Button btnOpLessEqual;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.Button button2;
        private System.Windows.Forms.Button button3;
        private System.Windows.Forms.Label ResultText;

        // 新增：字段选择列表
        private System.Windows.Forms.Label labelFieldsToSearch;
        private System.Windows.Forms.CheckedListBox lstSearchFields;

        // 新增：匹配方式单选框
        private System.Windows.Forms.RadioButton radioFuzzy;
        private System.Windows.Forms.RadioButton radioExact;
        private System.Windows.Forms.Button btnSemanticSQL;
    }
}