using System;
using System.Data;
using System.Data.OleDb;
using System.Drawing;
using System.Windows.Forms;

namespace ToDoListApp
{
    public partial class Form1 : Form
    {
        private ComboBox cmbPriorityFilter;
        private DateTimePicker dtpStartDate;
        private DateTimePicker dtpEndDate;
        private Button btnFilter;
        private Button btnResetFilter;
        private string connectionString = @"Provider=Microsoft.ACE.OLEDB.12.0;Data Source=./todolistDB.accdb";

        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            cmbPriorityFilter.SelectedIndex = 0;
            dtpStartDate.Value = DateTime.Now.AddMonths(-1); 
            dtpEndDate.Value = DateTime.Now.AddMonths(1);    

            LoadTasks();
        }


        private void LoadTasks()
        {
            try
            {
                panelPendingTasks.Controls.Clear();
                panelCompletedTasks.Controls.Clear();

                string query = "SELECT ID, Title, Description, DueDate, IsCompleted, Priority FROM Tasks WHERE 1=1";

                if (cmbPriorityFilter.SelectedIndex > 0)
                {
                    int priorityValue = 4 - cmbPriorityFilter.SelectedIndex; 
                    query += $" AND Priority = {priorityValue}";
                }

                // 添加时间范围筛选条件
                query += $" AND DueDate BETWEEN #{dtpStartDate.Value:yyyy-MM-dd}# AND #{dtpEndDate.Value:yyyy-MM-dd}#";

                // 添加排序
                query += " ORDER BY Priority DESC, DueDate";

                using (OleDbConnection connection = new OleDbConnection(connectionString))
                {
                    OleDbDataAdapter adapter = new OleDbDataAdapter(query, connection);
                    DataTable dt = new DataTable();
                    adapter.Fill(dt);

                    int totalTasks = 0;
                    int pendingTasks = 0;
                    int completedTasks = 0;

                    foreach (DataRow row in dt.Rows)
                    {
                        bool isCompleted = Convert.ToBoolean(row["IsCompleted"]);
                        TaskItem taskItem = CreateTaskItem(row);

                        if (isCompleted)
                        {
                            panelCompletedTasks.Controls.Add(taskItem);
                            completedTasks++;
                        }
                        else
                        {
                            panelPendingTasks.Controls.Add(taskItem);
                            pendingTasks++;
                        }

                        totalTasks++;
                    }

                    lblTotalTasks.Text = $"待办: {pendingTasks} | 已完成: {completedTasks}";
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("加载任务时出错: " + ex.Message);
            }
        }

        private void btnFilter_Click(object sender, EventArgs e)
        {
            LoadTasks();
        }

        private void btnResetFilter_Click(object sender, EventArgs e)
        {
            cmbPriorityFilter.SelectedIndex = 0;
            dtpStartDate.Value = DateTime.Now.AddMonths(-1);
            dtpEndDate.Value = DateTime.Now.AddMonths(1);
            LoadTasks();
        }

        private TaskItem CreateTaskItem(DataRow row)
        {
            TaskItem taskItem = new TaskItem(
                Convert.ToInt32(row["ID"]),
                row["Title"].ToString(),
                row["Description"].ToString(),
                Convert.ToDateTime(row["DueDate"]),
                Convert.ToBoolean(row["IsCompleted"]),
                Convert.ToInt32(row["Priority"])
            );

            taskItem.EditClicked += (sender, e) => ShowEditDialog(taskItem);
            taskItem.DeleteClicked += (sender, e) => DeleteTask(taskItem.TaskId);
            taskItem.StatusChanged += (sender, e) => UpdateTaskStatus(taskItem.TaskId, taskItem.IsCompleted);

            return taskItem;
        }


        private void ShowEditDialog(TaskItem taskItem)
        {
            using (var editForm = new TaskEditForm())
            {
                editForm.SetTaskData(
                    taskItem.TaskId,
                    taskItem.Title,
                    taskItem.Description,
                    taskItem.DueDate,
                    taskItem.Priority
                );

                if (editForm.ShowDialog() == DialogResult.OK)
                {
                    UpdateTask(
                        taskItem.TaskId,
                        editForm.GetTitle(),
                        editForm.GetDescription(),
                        editForm.GetDueDate(),
                        editForm.GetPriority()
                    );
                }
            }
        }

        private void btnAddNew_Click(object sender, EventArgs e)
        {
            using (var addForm = new TaskEditForm())
            {
                if (addForm.ShowDialog() == DialogResult.OK)
                {
                    AddTask(
                        addForm.GetTitle(),
                        addForm.GetDescription(),
                        addForm.GetDueDate(),
                        addForm.GetPriority()
                    );
                }
            }
        }

        private void AddTask(string title, string description, DateTime dueDate, int priority)
        {
            if (string.IsNullOrWhiteSpace(title))
            {
                MessageBox.Show("请输入任务标题");
                return;
            }

            try
            {
                string query = "INSERT INTO Tasks (Title, Description, DueDate, IsCompleted, Priority, CreatedDate) " +
                               "VALUES (@Title, @Description, @DueDate, @IsCompleted, @Priority, @CreatedDate)";

                using (OleDbConnection connection = new OleDbConnection(connectionString))
                {
                    connection.Open();
                    OleDbCommand command = new OleDbCommand(query, connection);

                    command.Parameters.Add("@Title", OleDbType.VarChar).Value = title;
                    command.Parameters.Add("@Description", OleDbType.LongVarChar).Value = description;
                    command.Parameters.Add("@DueDate", OleDbType.Date).Value = dueDate;
                    command.Parameters.Add("@IsCompleted", OleDbType.Boolean).Value = false;
                    command.Parameters.Add("@Priority", OleDbType.Integer).Value = priority;
                    command.Parameters.Add("@CreatedDate", OleDbType.Date).Value = DateTime.Now;

                    command.ExecuteNonQuery();
                }

                LoadTasks();
            }
            catch (Exception ex)
            {
                MessageBox.Show("添加任务时出错: " + ex.Message);
            }
        }

        private void UpdateTask(int taskId, string title, string description, DateTime dueDate, int priority)
        {
            try
            {
                string query = "UPDATE Tasks SET Title = @Title, Description = @Description, " +
                               "DueDate = @DueDate, Priority = @Priority WHERE ID = @ID";

                using (OleDbConnection connection = new OleDbConnection(connectionString))
                {
                    connection.Open();
                    OleDbCommand command = new OleDbCommand(query, connection);

                    command.Parameters.Add("@Title", OleDbType.VarChar).Value = title;
                    command.Parameters.Add("@Description", OleDbType.LongVarChar).Value = description;
                    command.Parameters.Add("@DueDate", OleDbType.Date).Value = dueDate;
                    command.Parameters.Add("@Priority", OleDbType.Integer).Value = priority;
                    command.Parameters.Add("@ID", OleDbType.Integer).Value = taskId;

                    command.ExecuteNonQuery();
                }

                LoadTasks();
            }
            catch (Exception ex)
            {
                MessageBox.Show("更新任务时出错: " + ex.Message);
            }
        }

        private void UpdateTaskStatus(int taskId, bool isCompleted)
        {
            try
            {
                string query = "UPDATE Tasks SET IsCompleted = @IsCompleted WHERE ID = @ID";

                using (OleDbConnection connection = new OleDbConnection(connectionString))
                {
                    connection.Open();
                    OleDbCommand command = new OleDbCommand(query, connection);
                    command.Parameters.Add("@IsCompleted", OleDbType.Boolean).Value = isCompleted;
                    command.Parameters.Add("@ID", OleDbType.Integer).Value = taskId;
                    command.ExecuteNonQuery();
                }

                LoadTasks();
            }
            catch (Exception ex)
            {
                MessageBox.Show("更新任务状态时出错: " + ex.Message);
            }
        }

        private void DeleteTask(int taskId)
        {
            if (MessageBox.Show("确定要删除这个任务吗？", "确认删除", MessageBoxButtons.YesNo) == DialogResult.Yes)
            {
                try
                {
                    string query = "DELETE FROM Tasks WHERE ID = @ID";

                    using (OleDbConnection connection = new OleDbConnection(connectionString))
                    {
                        connection.Open();
                        OleDbCommand command = new OleDbCommand(query, connection);
                        command.Parameters.Add("@ID", OleDbType.Integer).Value = taskId;
                        command.ExecuteNonQuery();
                    }

                    LoadTasks();
                }
                catch (Exception ex)
                {
                    MessageBox.Show("删除任务时出错: " + ex.Message);
                }
            }
        }

        private void tabPagePending_Click(object sender, EventArgs e)
        {

        }

        private void cmbPriorityFilter_SelectedIndexChanged(object sender, EventArgs e)
        {

        }

        private void label2_Click(object sender, EventArgs e)
        {

        }
    }

    public class TaskItem : Panel
    {
        public int TaskId { get; private set; }
        public string Title { get; private set; }
        public string Description { get; private set; }
        public DateTime DueDate { get; private set; }
        public bool IsCompleted { get; private set; }
        public int Priority { get; private set; }

        public event EventHandler EditClicked;
        public event EventHandler DeleteClicked;
        public event EventHandler StatusChanged;

        public TaskItem(int taskId, string title, string description, DateTime dueDate, bool isCompleted, int priority)
        {
            TaskId = taskId;
            Title = title;
            Description = description;
            DueDate = dueDate;
            IsCompleted = isCompleted;
            Priority = priority;

            InitializeComponents();
        }



        private void InitializeComponents()
        {
            this.Width = 700;
            this.Height = 60;
            this.Margin = new Padding(5);
            this.BorderStyle = BorderStyle.FixedSingle;

            Color backColor = GetPriorityColor(Priority);
            this.BackColor = backColor;

 
            CheckBox chkCompleted = new CheckBox
            {
                Checked = IsCompleted,
                AutoSize = true,
                Location = new Point(10, 20)
            };
            chkCompleted.CheckedChanged += (sender, e) =>
            {
                IsCompleted = chkCompleted.Checked;
                StatusChanged?.Invoke(this, EventArgs.Empty);
            };

            Label lblTitle = new Label
            {
                Text = Title,
                AutoSize = false,
                Width = 300,
                Location = new Point(40, 10),
                Font = new Font("Microsoft Sans Serif", 10, FontStyle.Bold)
            };

            Label lblDueDate = new Label
            {
                Text = DueDate.ToString("yyyy-MM-dd"),
                AutoSize = true,
                Location = new Point(350, 10),
                Font = new Font("Microsoft Sans Serif", 10, FontStyle.Bold)
            };

            string shortDescription = Description.Length > 30 ?
                Description.Substring(0, 30) + "..." : Description;

            Label lblDescription = new Label
            {
                Text = shortDescription,
                AutoSize = false,
                Width = 400,
                Location = new Point(40, 33),
                Font = new Font("Microsoft Sans Serif", 8)
            };

            Button btnEdit = new Button
            {
                Text = "编辑",
                Size = new Size(60, 25),
                Location = new Point(550, 15),
                FlatStyle = FlatStyle.Flat
            };
            btnEdit.Click += (sender, e) => EditClicked?.Invoke(this, EventArgs.Empty);

            Button btnDelete = new Button
            {
                Text = "删除",
                Size = new Size(60, 25),
                Location = new Point(620, 15),
                FlatStyle = FlatStyle.Flat
            };
            btnDelete.Click += (sender, e) => DeleteClicked?.Invoke(this, EventArgs.Empty);

            this.Controls.Add(chkCompleted);
            this.Controls.Add(lblTitle);
            this.Controls.Add(lblDueDate);
            this.Controls.Add(lblDescription);
            this.Controls.Add(btnEdit);
            this.Controls.Add(btnDelete);
        }

        private Color GetPriorityColor(int priority)
        {
            switch (priority)
            {
                case 3: return Color.LightPink;    // 高优先级
                case 2: return Color.LightYellow;   // 中优先级
                default: return Color.LightGray;   // 低优先级
            }
        }
    }

    public class TaskEditForm : Form
    {
        private int _taskId;
        private string _title;
        private string _description;
        private DateTime _dueDate;
        private int _priority;

        private TextBox txtTitle;
        private TextBox txtDescription;
        private DateTimePicker dtpDueDate;
        private ComboBox cmbPriority;
        private Button btnSave;
        private Button btnCancel;

        public TaskEditForm()
        {
            InitializeComponents();
        }

        public void SetTaskData(int taskId, string title, string description, DateTime dueDate, int priority)
        {
            _taskId = taskId;
            _title = title;
            _description = description;
            _dueDate = dueDate;
            _priority = priority;

            txtTitle.Text = title;
            txtDescription.Text = description;
            dtpDueDate.Value = dueDate;
            cmbPriority.SelectedIndex = priority - 1;
        }

        public string GetTitle() => _title;
        public string GetDescription() => _description;
        public DateTime GetDueDate() => _dueDate;
        public int GetPriority() => _priority;

        private void InitializeComponents()
        {
            this.Text = _taskId > 0 ? "编辑任务" : "添加新任务";
            this.Size = new Size(400, 300);
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.StartPosition = FormStartPosition.CenterParent;
            this.MaximizeBox = false;
            this.MinimizeBox = false;

            Label lblTitle = new Label
            {
                Text = "标题:",
                Location = new Point(20, 20),
                AutoSize = true
            };

            txtTitle = new TextBox
            {
                Location = new Point(80, 20),
                Size = new Size(280, 20)
            };

            Label lblDescription = new Label
            {
                Text = "描述:",
                Location = new Point(20, 60),
                AutoSize = true
            };

            txtDescription = new TextBox
            {
                Location = new Point(80, 60),
                Size = new Size(280, 60),
                Multiline = true,
                ScrollBars = ScrollBars.Vertical
            };

            Label lblDueDate = new Label
            {
                Text = "截止日期:",
                Location = new Point(20, 130),
                AutoSize = true
            };

            dtpDueDate = new DateTimePicker
            {
                Location = new Point(80, 130),
                Size = new Size(150, 20),
                Format = DateTimePickerFormat.Short
            };

            Label lblPriority = new Label
            {
                Text = "优先级:",
                Location = new Point(20, 170),
                AutoSize = true
            };

            cmbPriority = new ComboBox
            {
                Location = new Point(80, 170),
                Size = new Size(100, 21),
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            cmbPriority.Items.AddRange(new object[] { "低", "中", "高" });
            cmbPriority.SelectedIndex = 1;

            btnSave = new Button
            {
                Text = "保存",
                DialogResult = DialogResult.OK,
                Location = new Point(200, 220),
                Size = new Size(75, 30),
                BackColor = Color.LightGreen
            };
            btnSave.Click += (sender, e) =>
            {
                _title = txtTitle.Text;
                _description = txtDescription.Text;
                _dueDate = dtpDueDate.Value;
                _priority = cmbPriority.SelectedIndex + 1;
            };

            btnCancel = new Button
            {
                Text = "取消",
                DialogResult = DialogResult.Cancel,
                Location = new Point(285, 220),
                Size = new Size(75, 30),
                BackColor = Color.LightPink
            };

            this.Controls.Add(lblTitle);
            this.Controls.Add(txtTitle);
            this.Controls.Add(lblDescription);
            this.Controls.Add(txtDescription);
            this.Controls.Add(lblDueDate);
            this.Controls.Add(dtpDueDate);
            this.Controls.Add(lblPriority);
            this.Controls.Add(cmbPriority);
            this.Controls.Add(btnSave);
            this.Controls.Add(btnCancel);
        }
    }
}