using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BSM.BLL
{
    public class Verification
    {
        

        public bool IsCode(string str_postalcode)
        {
            return System.Text.RegularExpressions.Regex.
                IsMatch(str_postalcode, @"^\d{4}$");
        }
        
        public bool IsPwdCode(string str_postalcode)
        {
            return System.Text.RegularExpressions.Regex.
                IsMatch(str_postalcode, @"^[A-Za-z0-9]$");
        }
        public bool IsHandset(string str_handset)
        {
            return System.Text.RegularExpressions.Regex.
                IsMatch(str_handset, @"^[1]+[3,4,5,6,7,8,9]+\d{9}$");
        }
        public bool IsChinese(string str_chinese)
        {
            return System.Text.RegularExpressions.Regex.
                IsMatch(str_chinese, @"^[\u4e00-\u9fa5]{0,}$");
        }

        public bool IsIDcard(string str_postalcode)
        {
            return System.Text.RegularExpressions.Regex.
                IsMatch(str_postalcode, @"^[1,2,3,4,5,6,7,8,9]+\d{17}$");
        }

        public bool IsAccountCode(string str_postalcode)
        {
            return System.Text.RegularExpressions.Regex.
                IsMatch(str_postalcode, @"^\d{4}$");
        }

        public bool IsNumber(string str_postalcode)
        {
            return System.Text.RegularExpressions.Regex.
                IsMatch(str_postalcode, @"^[0-9]*$");
        }
    }
}
