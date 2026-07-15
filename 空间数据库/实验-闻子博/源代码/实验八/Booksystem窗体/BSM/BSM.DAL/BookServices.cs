using BSM.Models;
using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SqlClient;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BSM.DAL
{
    public class BookServices
    {
        public bool Addbook(Book book)
        {
            string sqlStr = "insert into Book (书名,主编,出版社,分类,数量,来源,封面) values(@书名,@主编,@出版社,@分类,@数量,@来源,@封面)";
            SqlParameter[] param = new SqlParameter[]
            {
                new SqlParameter("@书名",book.bookName),
                new SqlParameter("@主编",book.bookAuthor),
                new SqlParameter("@出版社",book.bookPress),
                new SqlParameter("@分类",book.bookClass),
                new SqlParameter("@数量",book.bookNumber),
                new SqlParameter("@来源",book.bookFrom),
                new SqlParameter("@封面",book.bookPhoto)

            };
            return DBHelper.ExcuteCommand(sqlStr, param);
        }

        public bool Updatebook(Book book)
        {
            string sqlStr = "update Book set 书名=@书名,主编=@主编,出版社=@出版社,分类=@分类,数量=@数量,来源=@来源,封面=@封面 where 图书编号=@图书编号";

            SqlParameter[] param = new SqlParameter[]
            {
                 new SqlParameter("@图书编号",book.bookId),
                new SqlParameter("@书名",book.bookName),
                new SqlParameter("@主编",book.bookAuthor),
                new SqlParameter("@出版社",book.bookPress),
                new SqlParameter("@分类",book.bookClass),
                new SqlParameter("@数量",book.bookNumber),
                new SqlParameter("@来源",book.bookFrom),
                new SqlParameter("@封面",book.bookPhoto)
            };
            return DBHelper.ExcuteCommand(sqlStr, param);
        }

        public bool BookOutAndIn(Book book)
        {
            string sqlStr = "update Book set 数量=@数量 where 图书编号=@图书编号";

            SqlParameter[] param = new SqlParameter[]
            {
                 new SqlParameter("@图书编号",book.bookId),
                new SqlParameter("@数量",book.bookNumber),
                
            };
            return DBHelper.ExcuteCommand(sqlStr, param);
        }


        public bool Deletebook(Book book)
        {

            string str = "delete From Book where 图书编号 = @图书编号";

            SqlParameter[] param = new SqlParameter[]
            {
                new SqlParameter("@图书编号",book.bookId)
            };

            return DBHelper.ExcuteCommand(str, param);
        }


        public DataTable GetOne(string a)   //精确查找
        {
            string strsql = string.Format("select * from Login where 账号='{0}'", a);
            SqlDataAdapter da = new SqlDataAdapter(strsql, DBHelper.connString);
            DataSet dt = new DataSet();
            da.Fill(dt);
            return dt.Tables[0];
        }

        public DataTable GetBookOne(string a)   //精确查找
        {
            string strsql = string.Format("select * from Book where 图书编号='{0}'", a);
            SqlDataAdapter da = new SqlDataAdapter(strsql, DBHelper.connString);
            DataSet dt = new DataSet();
            da.Fill(dt);
            return dt.Tables[0];
        }
        public DataTable GetOneBook(string a)   //模糊查找
        {
            string strsql = string.Format("select * from Book where 分类 like N'%{0}%'", a);
            SqlDataAdapter da = new SqlDataAdapter(strsql, DBHelper.connString);
            DataSet dt = new DataSet();
            da.Fill(dt);
            return dt.Tables[0];
        }

        public DataTable GetNameOnes(string a)  //模糊查找
        {
            string strsql = string.Format("select * from Book where 书名 like N'%{0}%'", a);
            SqlDataAdapter da = new SqlDataAdapter(strsql, DBHelper.connString);
            DataSet dt = new DataSet();
            da.Fill(dt);
            return dt.Tables[0];
        }

        public DataTable GetAll()   //全部查找
        {
            string strsql = "select * from Book";
            SqlDataAdapter da = new SqlDataAdapter(strsql, DBHelper.connString);
            DataSet dt = new DataSet();
            da.Fill(dt);
            return dt.Tables[0];
        }

    }
}
