using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SqlClient;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Transactions;
namespace BSM.DAL
{
    public class DBHelper
    {
        public static string connString = @"Data Source=localhost;Initial Catalog=Database1;Integrated Security=True";

        //定义数据库连接对象
        public static SqlConnection conn = new SqlConnection(connString);

        //获取数据的方法，返回DataTable对象，参数为一个select语句
        public static DataTable GetDataTable(string sqlStr)
        {
            try
            {
                conn.Open();
                SqlCommand cmd = new SqlCommand(sqlStr, conn);
                SqlDataAdapter dapt = new SqlDataAdapter(cmd);
                DataTable dt = new DataTable();
                dapt.Fill(dt);
                return dt;
            }
            catch
            {
                return null;
            }
            finally
            {
                conn.Close();
            }
        }

        //获取数据的重载方法，返回DataTable对象，参数为一个参数化的select语句和参数对象数组
        public static DataTable GetDataTable(string sqlStr, SqlParameter[] param)
        {
            try
            {
                conn.Open();
                SqlCommand cmd = new SqlCommand(sqlStr, conn);
                cmd.Parameters.AddRange(param);
                SqlDataAdapter dapt = new SqlDataAdapter(cmd);
                DataTable dt = new DataTable();
                dapt.Fill(dt);
                return dt;
            }
            catch
            {
                return null;
            }
            finally
            {
                conn.Close();
            }
        }

        //执行更新的方法，返回一个布尔值，参数为一个insert|update|delete语句
        public static bool ExcuteCommand(string sqlStr)
        {
            try
            {
                conn.Open();
                SqlCommand cmd = new SqlCommand(sqlStr, conn);
                cmd.ExecuteNonQuery();
                return true;
            }
            catch
            {
                return false;
            }
            finally
            {
                conn.Close();
            }
        }

        //执行更新的重载方法，返回一个布尔值，参数为一个参数化的insert|update|delete语句和参数对象数组
        public static bool ExcuteCommand(string sqlStr, SqlParameter[] param)
        {
            try
            {
                conn.Open();
                SqlCommand cmd = new SqlCommand(sqlStr, conn);
                cmd.Parameters.AddRange(param);
                cmd.ExecuteNonQuery();
                return true;
            }
            catch
            {
                return false;
            }
            finally
            {
                conn.Close();
            }
        }

        public static bool ExcuteCommand(List<String> sqlStr, List<SqlParameter[]> param)
        {
            int i = 0;
            SqlCommand cmd = new SqlCommand();
            using (TransactionScope ts = new TransactionScope())
            {
                cmd.Connection = conn;
                conn.Open();
                try
                {
                    foreach (string item in sqlStr)
                    {
                        cmd.CommandType = CommandType.Text;//设置命令类型为SQL文本命令
                        cmd.CommandText = item;//设置要对数据源执行的SQL语句                                          
                        cmd.Parameters.AddRange(param[i]);
                        i++;
                        cmd.ExecuteNonQuery();//执行SQL语句并返回受影响的行数                       
                    }
                    ts.Complete();
                    return true;
                }
                catch
                {
                    return false;
                }
                finally
                {
                    conn.Close();
                    sqlStr.Clear();
                }
            }
        }

    }
}
