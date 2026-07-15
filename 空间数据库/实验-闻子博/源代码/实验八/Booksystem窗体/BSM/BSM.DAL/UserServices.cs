using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SqlClient;
using System.Linq;
using System.Text;
using BSM.Models;
using System.Threading.Tasks;

namespace BSM.DAL
{
    public  class UserServices
    {
        public bool Register(User user)      //注册
        {
            string sqlStr = "insert into Login(账号,密码,昵称) values(@账号,@密码,@昵称)";
            SqlParameter[] param = new SqlParameter[]
             {
                new SqlParameter("@账号",user.account),
                new SqlParameter("@密码",user.password),
                new SqlParameter("@昵称",user.name),
             };
            return DBHelper.ExcuteCommand(sqlStr, param);
        }

        public bool Login(User user)      //登录
        {
            string sqlstr = "select 账号 from[Login]where(账号=@账号)and(密码=@密码)";
            SqlParameter[] param = new SqlParameter[]
             {
                new SqlParameter("@账号",user.account),
                new SqlParameter("@密码",user.password),
             };
            DataTable dt = DBHelper.GetDataTable(sqlstr, param);
            if (dt.Rows.Count != 0)
            {
                return true;
            }
            else
            {
                return false;
            }
        }



        public bool UpdatePwd(User user)      //修改密码
        {
            string sqlStr = "update Login set 密码=@密码 where 账号 = @账号";
            SqlParameter[] param = new SqlParameter[]
             {
                new SqlParameter("@账号",user.account),
                new SqlParameter("@密码",user.password),

             };
            return DBHelper.ExcuteCommand(sqlStr, param);
        }
    }
}
