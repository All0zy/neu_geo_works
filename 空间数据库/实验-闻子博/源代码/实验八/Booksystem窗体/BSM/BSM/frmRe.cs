using BSM.BLL;
using BSM.Models;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace BSM
{
    public partial class frmRe : Form
    {
        public frmRe()
        {
            InitializeComponent();
        }
        BookManage bk = new BookManage();
        Verification ver = new Verification();
        byte[] bytes;
        string num;
        private void dataGridView1_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {

        }
        private void getAll()
        {

            dataGridView1.DataSource = bk.Select();
        }
        private void button3_Click(object sender, EventArgs e)
        {
            try
            {
                if (textBox3.Text.Equals(""))
                {
                    MessageBox.Show("请输入图书编号");
                }
                else
                {
                    label18.Text = "";
                    //int bID= int.Parse(textBox3.Text);
                    dataGridView1.DataSource = bk.SelectBookOne(textBox3.Text);
                    MyBook(textBox3.Text);
                }

            }
            catch (Exception ex)
            {
                MessageBox.Show("未找到该编号图书！！！");
            }
        }

        public void MyBook(string a)
        {
            textBox1.Text = textBox3.Text;
            label19.Text = bk.SelectBookOne(a).DataSet.Tables[0].Rows[0]["书名"].ToString();
            label8.Text = bk.SelectBookOne(a).DataSet.Tables[0].Rows[0]["主编"].ToString();
            label9.Text = bk.SelectBookOne(a).DataSet.Tables[0].Rows[0]["出版社"].ToString();
            label11.Text = bk.SelectBookOne(a).DataSet.Tables[0].Rows[0]["分类"].ToString();
            label13.Text = bk.SelectBookOne(a).DataSet.Tables[0].Rows[0]["数量"].ToString();
            label15.Text = bk.SelectBookOne(a).DataSet.Tables[0].Rows[0]["来源"].ToString();
            if (bk.SelectBookOne(a).DataSet.Tables[0].Rows[0]["封面"].ToString() == "")
            {
                pictureBox1.Image = null;
                label18.Text = "该图书暂无图片";
            }
            else
            {
                bytes = (byte[])bk.SelectBookOne(a).DataSet.Tables[0].Rows[0]["封面"];
                pictureBox1.Image = System.Drawing.Image.FromStream(new MemoryStream(bytes));
                pictureBox1.SizeMode = PictureBoxSizeMode.Zoom;
            }
            num = bk.SelectBookOne(textBox3.Text).DataSet.Tables[0].Rows[0]["数量"].ToString();
            label6.Text = num;
        }

        private void button1_Click(object sender, EventArgs e)
        {
           
            if (textBox1.Text == "")
            {
                MessageBox.Show("出库失败！！！");
            }
            else
            {
                int i = int.Parse(num);
                if (i <= 0)
                {
                    MessageBox.Show("对不起！库存不足");
                }
                else
                {
                    int no = int.Parse(textBox3.Text);
                    i= i - 1;
                    num = i.ToString();
                    Book book = new Book { bookId = no,bookNumber=i.ToString() };
                    bool result = bk.UpdateNum(book);
                    if (result)
                    {
                        MessageBox.Show("出库成功！！！");
                        label6.Text = num;
                        label13.Text = num;
                        getAll();
                    }
                    else
                    {
                        MessageBox.Show("出库失败");
                    }
                }
            }
        }

        private void frmRe_Load(object sender, EventArgs e)
        {
            getAll();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            
            if (textBox2.Text=="")
            {
                MessageBox.Show("编号为空！！！");
                return;
            }
            if (!ver.IsCode(textBox2.Text))//验证编号号是否正确
            {
                MessageBox.Show("编号格式有误！！！");
                return;
            }
            try
            {
                num = bk.SelectBookOne(textBox2.Text).DataSet.Tables[0].Rows[0]["数量"].ToString();
            }
            catch
            {
                MessageBox.Show("没有该图书！！！");
                return;
            }


            
            
                try
                {
                    int i = int.Parse(num);
                    int no = int.Parse(textBox2.Text);
                    i = i + 1;
                    num = i.ToString();
                    Book book = new Book { bookId = no, bookNumber = i.ToString() };
                    bool result = bk.UpdateNum(book);
                    if (result)
                    {
                        textBox3.Text = textBox2.Text;
                        MyBook(textBox2.Text);
                        MessageBox.Show("入库成功！！！");
                        getAll();
                    }
                    else
                    {
                        MessageBox.Show("入库失败");
                    }
                }
                catch
                {
                    MessageBox.Show("入库失败！！！");
                }

                    
                
            
        }

        private void button4_Click(object sender, EventArgs e)
        {
            getAll();
            textBox3.Text = "";
            textBox1.Text = "";
            label19.Text = "";
            label8.Text = "";
            label9.Text = "";
            label11.Text = "";
            label13.Text = "";
            label15.Text = "";
            label18.Text = "";
            pictureBox1.Image = null;

            
        }
    }
}
