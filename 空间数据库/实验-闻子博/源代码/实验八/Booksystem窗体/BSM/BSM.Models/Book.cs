using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BSM.Models
{
    public class Book
    {
        public int bookId { get; set; }
        public string bookName { get; set; }
        public string bookAuthor { get; set; }
        public string bookClass { get; set; }
        public string bookNumber { get; set; }
        public string bookFrom { get; set; }
        public string bookPress { get; set; }
        public byte[] bookPhoto { get; set; }
    }
}
