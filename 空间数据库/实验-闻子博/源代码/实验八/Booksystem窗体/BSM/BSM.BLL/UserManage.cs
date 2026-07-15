using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using BSM.DAL;
using BSM.Models;
using System.Threading.Tasks;

namespace BSM.BLL
{
    public  class UserManage
    {
        UserServices service = new UserServices();

        public bool Register(User user)
        {
            return service.Register(user);
        }

        public bool Login(User user)
        {
            return service.Login(user);
        }
        //public bool update(user user)
        //{
        //    return service.update(user);
        //}

        public bool UpdatePwd(User user)
        {
            return service.UpdatePwd(user);
        }
    }
}
