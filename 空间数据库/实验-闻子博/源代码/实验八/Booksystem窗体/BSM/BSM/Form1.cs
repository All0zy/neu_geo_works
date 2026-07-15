using BSM.BLL;
using BSM.Models;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace BSM
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }
        UserManage ma = new UserManage();
        private void btnLogin_Click(object sender, EventArgs e)
        {
            if (textBox1.Text == "" || textBox2.Text == "")
            {
                MessageBox.Show("请输入完整信息！！！");
                return;
            }
            string count = textBox1.Text;
            string pwd = textBox2.Text;
            User user = new User { account = count, password = pwd };
            bool result = ma.Login(user);
            if (result)
            {
                this.Hide();
                frmMain mainForm = new frmMain(textBox1.Text, pwd);
                mainForm.StartPosition = FormStartPosition.CenterScreen;
                mainForm.Show();
            }
            else
            {
                MessageBox.Show("账号或密码错误！！！");
            }
        }

        public static string ToMD5(string source)
        {

            StringBuilder sb = new StringBuilder();
            MD5 md5 = MD5.Create();
            byte[] data = Encoding.UTF8.GetBytes(source);
            data = md5.ComputeHash(data);
            foreach (var item in data)
            {
                sb.Append(item.ToString("x2"));
            }
            return sb.ToString();

        }

        private void btnRegister_Click(object sender, EventArgs e)
        {
            this.Hide();
            frmRegister mainForm = new frmRegister();
            mainForm.StartPosition = FormStartPosition.CenterScreen;
            mainForm.Show();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            textBox2.PasswordChar = '*';
        }

        private void button1_Click(object sender, EventArgs e)
        {
            frmRegister mainForm = new frmRegister();
            mainForm.StartPosition = FormStartPosition.CenterScreen;
            mainForm.ShowDialog();
        }
    }
}
