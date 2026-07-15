// Class1.cs
using System;
using System.Runtime.InteropServices; // 注册插件到系统
using ESRI.ArcGIS.ADF.BaseClasses;
using ESRI.ArcGIS.ADF.CATIDs;
using ESRI.ArcGIS.Framework;
using ESRI.ArcGIS.ArcMapUI;

namespace NeuSearch
{
    /// <summary>
    /// 要素查询工具命令
    /// </summary>
    [Guid("2e21e7db-dae8-49cb-92a6-5f5cd7a7e822")]
    [ClassInterface(ClassInterfaceType.None)]
    [ProgId("NeuSearch.Class1")]
    public sealed class Class1 : BaseCommand
    {
        #region COM Registration

        [ComRegisterFunction()]
        [ComVisible(false)]
        static void RegisterFunction(Type registerType)
        {
            ArcGISCategoryRegistration(registerType);
        }

        [ComUnregisterFunction()]
        [ComVisible(false)]
        static void UnregisterFunction(Type registerType)
        {
            ArcGISCategoryUnregistration(registerType);
        }

        private static void ArcGISCategoryRegistration(Type registerType)
        {
            string regKey = string.Format("HKEY_CLASSES_ROOT\\CLSID\\{{{0}}}", registerType.GUID);
            MxCommands.Register(regKey);
        }

        private static void ArcGISCategoryUnregistration(Type registerType)
        {
            string regKey = string.Format("HKEY_CLASSES_ROOT\\CLSID\\{{{0}}}", registerType.GUID);
            MxCommands.Unregister(regKey);
        }

        #endregion

        private IApplication m_application;

        public Class1()
        {
            base.m_category = "Neu Tools";           // 分类名称
            base.m_caption = "要素查询工具";          // 显示名称
            base.m_message = "打开要素属性查询窗口";   // 状态栏提示
            base.m_toolTip = "要素查询工具";          // 鼠标悬停提示
            base.m_name = "NeuSearch_SearchCommand"; // 唯一内部名称

            // 加载图标
            try
            {
                base.m_bitmap = new System.Drawing.Bitmap(GetType(), "neu.bmp");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Trace.WriteLine(ex.Message, "Invalid Bitmap");
            }
        }

        public override void OnCreate(object hook)
        {
            if (hook == null) return;
            // 把 hook 转成标准接口
            m_application = hook as IApplication;

            if (hook is IMxApplication)
                base.m_enabled = true;
            else
                base.m_enabled = false;
        }

        public override void OnClick()
        {
            try
            {
                SearchForm form = new SearchForm(m_application);
                form.Show();
            }
            catch (Exception ex)
            {
                System.Windows.Forms.MessageBox.Show("启动查询工具失败：" + ex.Message);
            }
        }
    }
}