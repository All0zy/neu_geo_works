using BSM.BLL;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Data.SqlClient;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace BSM
{
    public partial class frmMain : Form
    {
        public string SendAccount;
        public frmMain(string account,string pwd)
        {
            SendAccount = account;
            InitializeComponent();
        }
        BookManage bk = new BookManage();
        private void frmMain_Load(object sender, EventArgs e)
        {
            label1.Text = System.DateTime.Now.ToLongDateString();
            label3.Text = bk.SelectOne(SendAccount).DataSet.Tables[0].Rows[0]["昵称"].ToString();

        }

        private void 添加书籍ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            FrmAdd mainForm = new FrmAdd();
            mainForm.StartPosition = FormStartPosition.CenterScreen;
            mainForm.Show();
        }

        private void Del_Click(object sender, EventArgs e)
        {
            frmfel mainForm = new frmfel();
            mainForm.StartPosition = FormStartPosition.CenterScreen;
            mainForm.Show();
        }

        private void 修改密码ToolStripMenuItem1_Click(object sender, EventArgs e)
        {
            this.Close();
            frm mainForm = new frm(SendAccount);
            mainForm.StartPosition = FormStartPosition.CenterScreen;
            mainForm.Show();
        }

        private void 退出ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            this.Close();
            Form1 mainForm = new Form1();
            mainForm.StartPosition = FormStartPosition.CenterScreen;
            mainForm.Show();
        }

        private void 添加书籍ToolStripMenuItem1_Click(object sender, EventArgs e)
        {
            frmUpdate mainForm = new frmUpdate();
            mainForm.StartPosition = FormStartPosition.CenterScreen;
            mainForm.Show();
        }

        private void toolStripMenuItem1_Click(object sender, EventArgs e)
        {
            frmRe mainForm = new frmRe();
            mainForm.StartPosition = FormStartPosition.CenterScreen;
            mainForm.Show();
        }

        private void menuStrip1_ItemClicked(object sender, ToolStripItemClickedEventArgs e)
        {

        }
    }
}
