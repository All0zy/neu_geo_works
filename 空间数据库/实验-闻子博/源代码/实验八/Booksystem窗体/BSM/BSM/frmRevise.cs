using BSM.BLL;
using BSM.Models;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Data.SqlClient;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace BSM
{
    public partial class frmfel : Form
    {
        public frmfel()
        {
            InitializeComponent();
        }
        byte[] bytes;
        BookManage bk = new BookManage();
        private void button1_Click(object sender, EventArgs e)
        {
            try
            {
                if (textBox3.Text.Equals(""))
                {
                    MessageBox.Show("请输入图书编号");
                }
                else
                {
                    label5.Text = bk.SelectBookOne(textBox3.Text).DataSet.Tables[0].Rows[0]["书名"].ToString();
                    label7.Text = bk.SelectBookOne(textBox3.Text).DataSet.Tables[0].Rows[0]["主编"].ToString();
                    label9.Text = bk.SelectBookOne(textBox3.Text).DataSet.Tables[0].Rows[0]["出版社"].ToString();
                    label11.Text = bk.SelectBookOne(textBox3.Text).DataSet.Tables[0].Rows[0]["分类"].ToString();
                    label13.Text = bk.SelectBookOne(textBox3.Text).DataSet.Tables[0].Rows[0]["数量"].ToString();
                    label15.Text = bk.SelectBookOne(textBox3.Text).DataSet.Tables[0].Rows[0]["来源"].ToString();
                    if (bk.SelectBookOne(textBox3.Text).DataSet.Tables[0].Rows[0]["封面"].ToString() == "")
                    {
                        pictureBox1.Image = null;
                        label18.Text = "该图书暂无图片";
                    }
                    else
                    {
                        bytes = (byte[])bk.SelectBookOne(textBox3.Text).DataSet.Tables[0].Rows[0]["封面"];
                        pictureBox1.Image = System.Drawing.Image.FromStream(new MemoryStream(bytes));
                        pictureBox1.SizeMode = PictureBoxSizeMode.Zoom;
                    }
                }
                
            }
            catch (Exception ex)
            {
                MessageBox.Show("未找到该编号图书！！！");
            }
        }
        private void getAll()
        {
            
            dataGridView1.DataSource = bk.Select();
        }
        private void frmfel_Load(object sender, EventArgs e)
        {
            getAll();
        }

        private void dataGridView1_CellClick(object sender, DataGridViewCellEventArgs e)
        {
            
        }

        private void buttonName_Click(object sender, EventArgs e)
        {
            if (textBox1.Text.Equals(""))
            {
                MessageBox.Show("请输入书名");
            }
            else
            {
                dataGridView1.DataSource = bk.SelectNameOnes(textBox1.Text);
            }
        }

        private void buttonClass_Click(object sender, EventArgs e)
        {
            if (cbClass.Text.Equals(""))
            {
                MessageBox.Show("请选择类别");
            }
            else
            {
                dataGridView1.DataSource = bk.SelectOneBoook(cbClass.Text);
            }
            
        }

        private void buttonAll_Click(object sender, EventArgs e)
        {
            getAll();
        }

        private void button4_Click(object sender, EventArgs e)
        {
            if (textBox2.Text.Equals(""))
            {
                MessageBox.Show("请输入图书编号");
            }
            else
            {
                int no = int.Parse(textBox2.Text);
                Book book = new Book { bookId = no };
                bool result = bk.Deletebook(book);
                if (result)
                {
                    MessageBox.Show("删除成功");
                }
                else
                {
                    MessageBox.Show("删除失败");
                }
                getAll();
                textBox2.Text = "";
            }
            
        }
    }
}
