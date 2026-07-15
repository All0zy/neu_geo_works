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
    public partial class frmRegister : Form
    {
        public frmRegister()
        {
            InitializeComponent();
        }
        Verification ver = new Verification();
        UserManage ma = new UserManage();
        private void btnSubmit_Click(object sender, EventArgs e)
        {

            
            string count = txt_count.Text;
            string pwd = txt_pwd.Text;
            string nc = txt_name.Text;
            string rePwd = txt_submit.Text;
            if (count == "" || pwd == "" || nc == "" || rePwd == "")
            {
                MessageBox.Show("请输入完整信息！！！");
                return;
            }
            if (!ver.IsCode(txt_count.Text))//验证账号是否正确
            {
                MessageBox.Show("请输入4位数字账号！！！");
                return;
            }

            if (!ver.IsChinese(txt_name.Text))//验证账号是否正确
            {
                MessageBox.Show("请输入中文昵称！！！");
                return;
            }

            if (pwd == rePwd)
            {
                User user = new User { account = count, password = pwd, name = nc };
                bool result = ma.Register(user);

                if (result)
                {
                    MessageBox.Show("注册成功！！！");
                }
                else
                {
                    MessageBox.Show("账号已存在！！！");
                }
            }
            else
            {
                MessageBox.Show("两次输入不一致！！！");
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

        private void btnBack_Click(object sender, EventArgs e)
        {
            this.Close();
            Form1 mainForm = new Form1();
            mainForm.StartPosition = FormStartPosition.CenterScreen;
            mainForm.Show();

        }

        private void frmRegister_Load(object sender, EventArgs e)
        {
            txt_pwd.PasswordChar = '*';
            txt_submit.PasswordChar = '*';
        }
    }
}
