using BSM.Models;
using BSM.BLL;
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
using System.Data.SqlClient;

namespace BSM
{
    public partial class frmUpdate : Form
    {
        public frmUpdate()
        {
            InitializeComponent();
        }
        byte[] bytes;
        public string bookId;
        BookManage bk = new BookManage();
        private void getAll()
        {
            dataGridView1.DataSource = bk.Select();
        }

        public bool checkNull()
        {
            bool a = true;
            if (txtName.Text.Trim().Equals("") &&
               txtAuthor.Text.Trim().Equals("") &&
               txtPress.Text.Trim().Equals("") &&
               cbClass.Text.Trim().Equals("") &&
               txtNumber.Text.Trim().Equals("") &&
               txtFrom.Text.Trim().Equals(""))
            {
                a = false;
            }
            return a;
        }
        private void label8_Click(object sender, EventArgs e)
        {

        }
        private void btnPhoto_Click(object sender, EventArgs e)
        {
            OpenFileDialog openfile = new OpenFileDialog();
            openfile.Title = "请选择客户端longin的图片";
            openfile.Filter = "Login图片(*.jpg;*.bmp;*png)|*.jpeg;*.jpg;*.bmp;*.png|AllFiles(*.*)|*.*";
            if (DialogResult.OK == openfile.ShowDialog())
            {
                try
                {
                    //读成二进制
                    bytes = File.ReadAllBytes(openfile.FileName);
                    //直接返这个存储到数据就行了cmd.Parameters.Add("@image", SqlDbType.Image).Value = bytes;
                    //输出二进制 在这里把数据中取到的值放在这里byte[] bytes=(byte[])model.image;
                    pictureBox1.Image = System.Drawing.Image.FromStream(new MemoryStream(bytes));
                    pictureBox1.SizeMode = PictureBoxSizeMode.Zoom;
                }
                catch { }
            }
        }

        private void btnRevise_Click(object sender, EventArgs e)
        {
            if (checkNull())
            {
                int no = int.Parse(bookId);
                string name = txtName.Text;
                string author = txtAuthor.Text;
                string press = txtPress.Text;
                string bClass = cbClass.Text;
                string number = txtNumber.Text;
                string bfrom = txtFrom.Text;
                Book book = new Book
                {
                    bookId = no,
                    bookName = name,
                    bookAuthor = author,
                    bookPress = press,
                    bookClass = bClass,
                    bookNumber = number,
                    bookFrom = bfrom,
                    bookPhoto = bytes
                };
                bool result = bk.Updatebook(book);
                if (result)
                {
                    MessageBox.Show("修改成功");
                    getAll();
                    ClearAll();
                }
                else
                {
                    MessageBox.Show("修改失败");
                }
            }
            else
            {
                MessageBox.Show("请输入完整信息");
            }



        }

        private void dataGridView1_CellClick(object sender, DataGridViewCellEventArgs e)
        {
            if (dataGridView1.SelectedRows.Count <= 0)		//用于判断是否选中了DataGridView中的一行
            {
                MessageBox.Show("请选中一行进行操作");
                return;
            }
            bookId = dataGridView1.SelectedRows[0].Cells[0].Value.ToString();
            txtName.Text = dataGridView1.SelectedRows[0].Cells[1].Value.ToString();
            txtAuthor.Text = dataGridView1.SelectedRows[0].Cells[2].Value.ToString();
            txtPress.Text = dataGridView1.SelectedRows[0].Cells[3].Value.ToString();
            cbClass.Text = dataGridView1.SelectedRows[0].Cells[4].Value.ToString();
            txtNumber.Text = dataGridView1.SelectedRows[0].Cells[5].Value.ToString();
            txtFrom.Text = dataGridView1.SelectedRows[0].Cells[6].Value.ToString();
            if (dataGridView1.SelectedRows[0].Cells[7].Value.ToString() == "")
            {
                pictureBox1.Image = null;
            }
            else
            {
                bytes = (byte[])dataGridView1.SelectedRows[0].Cells[7].Value;
                pictureBox1.Image = System.Drawing.Image.FromStream(new MemoryStream(bytes));
                pictureBox1.SizeMode = PictureBoxSizeMode.Zoom;
            }

        }

        private void btnClear_Click(object sender, EventArgs e)
        {
            ClearAll();
        }

        public void ClearAll()
        {
            txtName.Text = "";
            txtAuthor.Text = "";
            txtPress.Text = "";
            cbClass.Text = "";
            txtNumber.Text = "";
            txtFrom.Text = "";
            pictureBox1.Image = null;
        }

        private void frmUpdate_Load(object sender, EventArgs e)
        {
            getAll();
        }
    }
}
