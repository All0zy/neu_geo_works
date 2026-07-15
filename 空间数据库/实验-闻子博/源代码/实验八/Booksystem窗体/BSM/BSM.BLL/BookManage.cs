using BSM.DAL;
using BSM.Models;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BSM.BLL
{
     public class BookManage
    {

        BookServices bk = new BookServices();

        public bool Addbook(Book book)
        {
            return bk.Addbook(book);
        }

        public bool Updatebook(Book book)
        {
            return bk.Updatebook(book);
        }

        public bool Deletebook(Book book)
        {
            return bk.Deletebook(book);
        }

        public bool UpdateNum(Book book)
        {
            return bk.BookOutAndIn(book);
        }

        public DataTable Select()//BLL
        {
            return bk.GetAll();
        }

        public DataTable SelectOne(string str)
        {
            return bk.GetOne(str);
        }
        public DataTable SelectBookOne(string str)
        {
            return bk.GetBookOne(str);
        }

        public DataTable SelectOneBoook(string str)
        {
            return bk.GetOneBook(str);
        }

        public DataTable SelectNameOnes(string str)
        {
            return bk.GetNameOnes(str);
        }
    }
}
