using System;
using System.Collections.Generic;
using System.Data;
using System.Data.OleDb;
using System.Windows.Forms;

namespace 图书管理系统
{
    public partial class MainForm : Form
    {
        private OleDbConnection connection;
        private string connectionString;
        private string currentTableName;

        // 表配置信息
        private readonly Dictionary<string, string> tableConfig = new Dictionary<string, string>
        {
            { "读者", "读者" },
            { "图书", "图书" },
            { "借书登记", "借书登记" }
        };

        public MainForm()
        {
            InitializeComponent();
            connectionString = @"Provider=Microsoft.ACE.OLEDB.12.0;Data Source=C:\Users\15338\Desktop\空间数据库20232673陈英杰\实验\实验八\图书管理.accdb";
            connection = new OleDbConnection(connectionString);
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            currentTableName = "读者";
            LoadData(currentTableName);
        }

        private void tabControl1_SelectedIndexChanged(object sender, EventArgs e)
        {
            switch (tabControl1.SelectedIndex)
            {
                case 0:
                    currentTableName = "读者";
                    break;
                case 1:
                    currentTableName = "图书";
                    break;
                case 2:
                    currentTableName = "借书登记";
                    break;
            }
            LoadData(currentTableName);
        }

        private void LoadData(string tableName)
        {
            try
            {
                if (connection.State != ConnectionState.Open)
                    connection.Open();

                string actualTableName = tableConfig[tableName];
                string query = $"SELECT * FROM [{actualTableName}]";
                OleDbDataAdapter adapter = new OleDbDataAdapter(query, connection);
                DataTable dataTable = new DataTable();
                adapter.Fill(dataTable);

                switch (tableName)
                {
                    case "读者":
                        readerDataGridView.DataSource = dataTable;
                        FormatReaderTable(dataTable);
                        break;
                    case "图书":
                        bookDataGridView.DataSource = dataTable;
                        FormatBookTable(dataTable);
                        break;
                    case "借书登记":
                        borrowDataGridView.DataSource = dataTable;
                        FormatBorrowTable(dataTable);
                        break;
                }

                connection.Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"加载{tableName}表时出错: {ex.Message}");
                if (connection.State == ConnectionState.Open)
                    connection.Close();
            }
        }

        private void FormatReaderTable(DataTable dataTable)
        {
            if (readerDataGridView.Columns.Contains("部门"))
            {
                
                DataGridViewColumn existingColumn = readerDataGridView.Columns["部门"];
                DataGridViewComboBoxColumn comboBoxColumn = new DataGridViewComboBoxColumn();
                comboBoxColumn.DataSource = new string[] { "法律系", "英语系", "中文系", "科研处", "人事处", "教务处" };
                comboBoxColumn.DisplayMember = "";
                comboBoxColumn.ValueMember = "";
                comboBoxColumn.Name = existingColumn.Name;
                comboBoxColumn.HeaderText = existingColumn.HeaderText;
                comboBoxColumn.DataPropertyName = existingColumn.DataPropertyName; 
                comboBoxColumn.DefaultCellStyle = existingColumn.DefaultCellStyle; 
                int columnIndex = existingColumn.Index;
                readerDataGridView.Columns.Remove(existingColumn);
                readerDataGridView.Columns.Insert(columnIndex, comboBoxColumn);
            }

            if (readerDataGridView.Columns.Contains("办证时间"))
            {
                readerDataGridView.Columns["办证时间"].DefaultCellStyle.Format = "yyyy-MM-dd";
            }
        }

        private void FormatBookTable(DataTable dataTable)
        {
            if (bookDataGridView.Columns.Contains("价格"))
            {
                bookDataGridView.Columns["价格"].DefaultCellStyle.Format = "0.00";
            }
        }

        private void FormatBorrowTable(DataTable dataTable)
        {
            if (borrowDataGridView.Columns.Contains("借书日期"))
            {
                borrowDataGridView.Columns["借书日期"].DefaultCellStyle.Format = "yyyy-MM-dd";
            }

            if (borrowDataGridView.Columns.Contains("还书日期"))
            {
                borrowDataGridView.Columns["还书日期"].DefaultCellStyle.Format = "yyyy-MM-dd";
            }
        }

        private void btnAdd_Click(object sender, EventArgs e)
        {
            try
            {
                if (connection.State != ConnectionState.Open)
                    connection.Open();

                string actualTableName = tableConfig[currentTableName];
                DataGridView dataGridView = GetCurrentDataGridView();
                if (dataGridView.DataSource == null || !(dataGridView.DataSource is DataTable))
                {
                    MessageBox.Show("数据加载异常，请刷新后重试");
                    return;
                }

                DataTable dataTable = (DataTable)dataGridView.DataSource;
                DataGridViewRow newDataRow = dataGridView.Rows[dataGridView.Rows.Count - 2];
                string fields = "";
                string values = "";

                foreach (DataGridViewColumn column in dataGridView.Columns)
                {
                    if (column.Visible)
                    {
                        fields += $"[{column.Name}], ";
                        values += $"@{column.Name}, ";
                    }
                }

                fields = fields.TrimEnd(',', ' ');
                values = values.TrimEnd(',', ' ');

                string insertQuery = $"INSERT INTO [{actualTableName}] ({fields}) VALUES ({values})";
                OleDbCommand command = new OleDbCommand(insertQuery, connection);
                foreach (DataGridViewColumn column in dataGridView.Columns)
                {
                    if (column.Visible)
                    {
                        object value = newDataRow.Cells[column.Name].Value;
                        command.Parameters.AddWithValue($"@{column.Name}", value ?? DBNull.Value);
                    }
                }
                int rowsAffected = command.ExecuteNonQuery();

                if (rowsAffected > 0)
                {
                    MessageBox.Show("添加成功！");
                    LoadData(currentTableName);
                }
                else
                {
                    MessageBox.Show("添加失败！");
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("添加数据时出错: " + ex.Message);
            }
            finally
            {
                if (connection.State == ConnectionState.Open)
                    connection.Close();
            }
        }

        private void btnModify_Click(object sender, EventArgs e)
        {
            try
            {
                if (connection.State != ConnectionState.Open)
                    connection.Open();

                DataGridView dataGridView = GetCurrentDataGridView();
                if (dataGridView.SelectedRows.Count == 0)
                {
                    MessageBox.Show("请选择要修改的行！");
                    return;
                }

                DataGridViewRow selectedRow = dataGridView.SelectedRows[0];
                string actualTableName = tableConfig[currentTableName];
                string primaryKey = GetPrimaryKey(actualTableName);

                string setClause = "";
                foreach (DataGridViewColumn column in dataGridView.Columns)
                {
                    if (column.Visible && column.Name != primaryKey)
                    {
                        setClause += $"[{column.Name}] = @{column.Name}, ";
                    }
                }

                setClause = setClause.TrimEnd(',', ' ');

                string updateQuery = $"UPDATE [{actualTableName}] SET {setClause} WHERE [{primaryKey}] = @PrimaryKey";
                OleDbCommand command = new OleDbCommand(updateQuery, connection);

                foreach (DataGridViewColumn column in dataGridView.Columns)
                {
                    if (column.Visible && column.Name != primaryKey)
                    {
                        command.Parameters.AddWithValue($"@{column.Name}", selectedRow.Cells[column.Name].Value ?? DBNull.Value);
                    }
                }

                command.Parameters.AddWithValue("@PrimaryKey", selectedRow.Cells[primaryKey].Value);

                int rowsAffected = command.ExecuteNonQuery();
                if (rowsAffected > 0)
                {
                    MessageBox.Show("修改成功！");
                    LoadData(currentTableName);
                }
                else
                {
                    MessageBox.Show("修改失败！");
                }

                connection.Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show("修改数据时出错: " + ex.Message);
                if (connection.State == ConnectionState.Open)
                    connection.Close();
            }
        }

        private void btnDelete_Click(object sender, EventArgs e)
        {
            try
            {
                if (connection.State != ConnectionState.Open)
                    connection.Open();

                DataGridView dataGridView = GetCurrentDataGridView();
                if (dataGridView.SelectedRows.Count == 0)
                {
                    MessageBox.Show("请选择要删除的行！");
                    return;
                }

                if (MessageBox.Show("确定要删除选中的记录吗？", "确认删除", MessageBoxButtons.YesNo) != DialogResult.Yes)
                    return;

                DataGridViewRow selectedRow = dataGridView.SelectedRows[0];
                string actualTableName = tableConfig[currentTableName];
                string primaryKey = GetPrimaryKey(actualTableName);

                string deleteQuery = $"DELETE FROM [{actualTableName}] WHERE [{primaryKey}] = @PrimaryKey";
                OleDbCommand command = new OleDbCommand(deleteQuery, connection);
                command.Parameters.AddWithValue("@PrimaryKey", selectedRow.Cells[primaryKey].Value);

                int rowsAffected = command.ExecuteNonQuery();
                if (rowsAffected > 0)
                {
                    MessageBox.Show("删除成功！");
                    LoadData(currentTableName);
                }
                else
                {
                    MessageBox.Show("删除失败！");
                }

                connection.Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show("删除数据时出错: " + ex.Message);
                if (connection.State == ConnectionState.Open)
                    connection.Close();
            }
        }

        private void btnRefresh_Click(object sender, EventArgs e)
        {
            LoadData(currentTableName);
        }

        private DataGridView GetCurrentDataGridView()
        {
            switch (currentTableName)
            {
                case "读者":
                    return readerDataGridView;
                case "图书":
                    return bookDataGridView;
                case "借书登记":
                    return borrowDataGridView;
                default:
                    return null;
            }
        }

        private string GetPrimaryKey(string tableName)
        {
            switch (tableName)
            {
                case "读者":
                    return "借书证号";
                case "图书":
                    return "书号";
                case "借书登记":
                    return "流水号";
                default:
                    return "";
            }
        }
    }
}