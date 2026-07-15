using System;
using System.Windows.Forms;
using System.Collections.Generic;
//  数据库/表格相关类
using System.Data;
// 文件和目录操作
using System.IO;
using System.ComponentModel;
using System.Drawing;
using System.Text;
using System.Linq;

using ESRI.ArcGIS.Framework;
using ESRI.ArcGIS.ArcMapUI;
using ESRI.ArcGIS.Carto;
using ESRI.ArcGIS.Geodatabase;
using ESRI.ArcGIS.Geometry;
using ESRI.ArcGIS.esriSystem;
using ESRI.ArcGIS.Display;
// 发送http get请求
using System.Net;
using System.Web.Script.Serialization;

namespace NeuSearch
{
    public partial class SearchForm : Form
    {
        private IApplication m_app;
        // List<>定义泛型列表，存储多个对象
        private List<IFeature> allFoundFeatures = new List<IFeature>();
        private List<string> allFoundLayerNames = new List<string>();
        private int currentKanbanIndex = 0;
        private IElement currentHighlightElement = null;
        // 图层-字段列表 的映射表
        private Dictionary<string, List<FieldInfo>> layerFieldCache = new Dictionary<string, List<FieldInfo>>();
        // GLM令牌
        private const string GLM_API_KEY = "e2245d9ad0f44c90b6bb519949e10550.gA9jBVhJ2dmVuh6w";
        // 存储字段信息
        private class FieldInfo
        {
            public string Name;
            public string Alias;
            public string DisplayName;   // 显示的名称

            public FieldInfo(string name, string alias)
            {
                Name = name;
                Alias = alias;
                if (!string.IsNullOrEmpty(alias) && alias != name)
                    DisplayName = alias + " (" + name + ")";
                else
                    DisplayName = name;
            }

            public override string ToString()
            {
                return this.DisplayName;
            }
        }

        // 初始化界面
        public SearchForm(IApplication app)
        {
            InitializeComponent();
            m_app = app;
            LoadLayersIntoControls();
            lstLayerSelection.ItemCheck += LstLayerSelection_ItemCheck;
            txtKeyword.KeyDown += TxtKeyword_KeyDown;
            tabControlSearchMode.SelectedIndexChanged += TabControlSearchMode_SelectedIndexChanged;
        }

        // 添加要素图层到左侧复选框
        private void LoadLayersIntoControls()
        {
            lstLayerSelection.Items.Clear();
            layerFieldCache.Clear();

            IMxDocument mxDoc = m_app.Document as IMxDocument;
            if (mxDoc == null) return;
            IMap map = mxDoc.FocusMap;
            for (int i = 0; i < map.LayerCount; i++)
            {
                ILayer layer = map.get_Layer(i);
                // 判断是否为要素图层
                if (layer is IFeatureLayer)
                {
                    lstLayerSelection.Items.Add(layer.Name);
                    CacheFieldsForLayer(layer as IFeatureLayer);
                }
            }
            if (lstLayerSelection.Items.Count > 0)
            {
                chkAllLayers.Checked = true;
                lstLayerSelection.Enabled = false;
                UpdateSimpleSearchFields();
            }
        }

        // 填充图层-字段列表 的映射表
        private void CacheFieldsForLayer(IFeatureLayer fl)
        {
            if (fl == null || layerFieldCache.ContainsKey(fl.Name)) return;

            // 字段列表
            List<FieldInfo> fields = new List<FieldInfo>();
            // 获取其底层要素类的所有字段信息
            IFields fset = fl.FeatureClass.Fields;
            for (int i = 0; i < fset.FieldCount; i++)
            {
                IField f = fset.get_Field(i);
                // 非几何字段、二进制大对象、栅格字段
                if (f.Type != esriFieldType.esriFieldTypeGeometry &&
                    f.Type != esriFieldType.esriFieldTypeBlob &&
                    f.Type != esriFieldType.esriFieldTypeRaster)
                {
                    fields.Add(new FieldInfo(f.Name, f.AliasName));
                }
            }
            layerFieldCache[fl.Name] = fields;
        }

        // 渲染字段选择列表并默认选择Name
        private void UpdateSimpleSearchFields()
        {
            lstSearchFields.Items.Clear();
            // 存储无重复的元素，并且不保证元素的顺序。
            HashSet<string> fieldSet = new HashSet<string>();
            Dictionary<string, FieldInfo> displayMap = new Dictionary<string, FieldInfo>();
            List<string> selectedLayers = GetSelectedLayers();

            foreach (string layerName in selectedLayers)
            {
                if (layerFieldCache.ContainsKey(layerName))
                {
                    foreach (FieldInfo fi in layerFieldCache[layerName])
                    {
                        if (!fieldSet.Contains(fi.Name))
                        {
                            fieldSet.Add(fi.Name);
                            displayMap[fi.Name] = fi;
                        }
                    }
                }
            }

            List<string> sortedNames = new List<string>(fieldSet);
            sortedNames.Sort();

            int nameFieldIndex = -1;
            foreach (string name in sortedNames)
            {
                FieldInfo fi = displayMap[name];
                lstSearchFields.Items.Add(fi);

                if (name == "Name")
                {
                    nameFieldIndex = lstSearchFields.Items.Count - 1;
                }
            }

            if (nameFieldIndex != -1)
            {
                lstSearchFields.SetItemChecked(nameFieldIndex, true);
            }
        }

        // 所有被用户选中的要素图层
        private List<string> GetSelectedLayers()
        {
            List<string> layers = new List<string>();
            if (chkAllLayers.Checked)
            {
                for (int i = 0; i < lstLayerSelection.Items.Count; i++)
                    layers.Add(lstLayerSelection.Items[i].ToString());
            }
            else
            {
                foreach (object item in lstLayerSelection.CheckedItems)
                    layers.Add(item.ToString());
            }
            return layers;
        }

        // 全部选择按钮变化时触发
        private void chkAllLayers_CheckedChanged(object sender, EventArgs e)
        {
            lstLayerSelection.Enabled = !chkAllLayers.Checked;
            if (tabControlSearchMode.SelectedTab == tabPageAdvanced)
            {
                LoadFieldsForSelectedLayers();
            }
            else if (tabControlSearchMode.SelectedTab == tabPageSimple)
            {
                UpdateSimpleSearchFields();
            }
        }

        // 渲染sql字段选择列表
        private void LoadFieldsForSelectedLayers()
        {
            lstFieldsForSql.Items.Clear();
            HashSet<string> fieldSet = new HashSet<string>();
            Dictionary<string, FieldInfo> displayMap = new Dictionary<string, FieldInfo>();
            List<string> selectedLayers = GetSelectedLayers();

            foreach (string layerName in selectedLayers)
            {
                List<FieldInfo> cachedFields;

                // TryGetValue 如果字典中存在指定的key，则将对应的value赋给out参数
                if (layerFieldCache.TryGetValue(layerName, out cachedFields))
                {
                    foreach (FieldInfo fi in cachedFields)
                    {
                        if (!fieldSet.Contains(fi.Name))
                        {
                            fieldSet.Add(fi.Name);
                            displayMap[fi.Name] = fi;
                        }
                    }
                }
            }

            List<string> sorted = new List<string>(fieldSet);
            sorted.Sort();
            foreach (string name in sorted)
            {
                lstFieldsForSql.Items.Add(displayMap[name].DisplayName);
            }
        }

        // 简单/sql 查询模式切换时渲染变化
        private void TabControlSearchMode_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (tabControlSearchMode.SelectedTab == tabPageAdvanced)
            {
                LoadFieldsForSelectedLayers();
            }
            else if (tabControlSearchMode.SelectedTab == tabPageSimple)
            {
                UpdateSimpleSearchFields();
            }
        }

        // 图层选择变化时调用重新渲染字段
        private void LstLayerSelection_ItemCheck(object sender, ItemCheckEventArgs e)
        {
            if (tabControlSearchMode.SelectedTab == tabPageAdvanced)
            {
                // BeginInvoke异步 切换完成后执行
                this.BeginInvoke(new Action(LoadFieldsForSelectedLayers));
            }
            else if (tabControlSearchMode.SelectedTab == tabPageSimple)
            {
                this.BeginInvoke(new Action(UpdateSimpleSearchFields));
            }
        }

        // sql字段列表双击插入原始名
        private void lstFieldsForSql_MouseDoubleClick(object sender, MouseEventArgs e)
        {
            if (lstFieldsForSql.SelectedItem != null)
            {
                string displayName = lstFieldsForSql.SelectedItem.ToString();
                // 提取原始字段名
                string originalName = ExtractOriginalFieldName(displayName);
                InsertTextToSql(originalName);
            }
        }

        // 提取字段原名
        private string ExtractOriginalFieldName(string displayName)
        {
            if (displayName.EndsWith(")"))
            {
                int lastOpen = displayName.LastIndexOf(" (");
                if (lastOpen > 0)
                {
                    return displayName.Substring(lastOpen + 2, displayName.Length - lastOpen - 3);
                }
            }
            return displayName;
        }

        // 光标处插入字段名
        private void InsertTextToSql(string text)
        {
            // 当前光标位置
            int selStart = txtSqlWhere.SelectionStart;
            txtSqlWhere.Text = txtSqlWhere.Text.Insert(selStart, text);
            txtSqlWhere.SelectionStart = selStart + text.Length;
            txtSqlWhere.Focus();
        }

        // 处理sql符号的点击和插入
        private void InsertOperatorToSql(object sender, EventArgs e)
        {
            var btn = sender as System.Windows.Forms.Button;
            if (btn != null)
            {
                InsertTextToSql(" " + btn.Text + " ");
            }
        }

        // sql清空
        private void btnClearSQL_Click(object sender, EventArgs e)
        {
            txtSqlWhere.Clear();
        }

        // 简单查询按钮点击
        private void btnSimpleSearch_Click(object sender, EventArgs e)
        {
            string keyword = txtKeyword.Text.Trim();
            if (string.IsNullOrEmpty(keyword))
            {
                MessageBox.Show("请输入关键词。");
                return;
            }

            List<string> selectedLayers = GetSelectedLayers();
            if (selectedLayers.Count == 0)
            {
                MessageBox.Show("请至少选择一个图层进行搜索。");
                return;
            }

            // 获取选中的字段
            List<string> selectedFieldNames = new List<string>();

            foreach (object item in lstSearchFields.CheckedItems)
            {
                FieldInfo fi = item as FieldInfo;
                if (fi != null)
                {
                    selectedFieldNames.Add(fi.Name);
                }
            }

            if (selectedFieldNames.Count == 0)
            {
                MessageBox.Show("请至少选择一个查询字段。");
                return;
            }

            bool isFuzzy = radioFuzzy.Checked;
            PerformSearchOnLayers(selectedLayers, keyword, isFuzzy, selectedFieldNames);
            tabControlResult.SelectedTab = tabPageList;
            UpdateResultSummary();
        }

        // 键盘 enter 行为
        private void TxtKeyword_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter)
            {
                btnSimpleSearch_Click(sender, e);
                // 阻止当前按键产生进一步的字符输入或系统默认行为
                e.SuppressKeyPress = true;
            }
        }

        // sql高级查询按钮点击
        private void btnAdvancedSearch_Click(object sender, EventArgs e)
        {
            string whereClause = txtSqlWhere.Text.Trim();
            if (string.IsNullOrEmpty(whereClause))
            {
                MessageBox.Show("请输入 WHERE 条件。");
                return;
            }

            List<string> selectedLayers = GetSelectedLayers();
            if (selectedLayers.Count == 0)
            {
                MessageBox.Show("请至少选择一个图层进行搜索。");
                return;
            }

            PerformSearchOnLayers(selectedLayers, whereClause, false, null);
            tabControlResult.SelectedTab = tabPageList;
            UpdateResultSummary();
        }

        // 语义构建SQL点击事件
        private void btnSemanticSQL_Click(object sender, EventArgs e)
        {
            string userRequirement = Microsoft.VisualBasic.Interaction.InputBox(
                "请输入您的查询需求（GLM-4.6V-Flash）:",
                "语义构建SQL",
                "",
                -1,
                -1
            );

            if (string.IsNullOrEmpty(userRequirement) || userRequirement.Trim().Length == 0)
            {
                return;
            }

            List<string> selectedLayers = GetSelectedLayers();
            if (selectedLayers.Count == 0)
            {
                MessageBox.Show("请至少选择一个图层。", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            HashSet<string> fieldSet = new HashSet<string>();
            IMxDocument mxDoc = m_app.Document as IMxDocument;
            IMap map = mxDoc.FocusMap;

            foreach (string layerName in selectedLayers)
            {
                for (int i = 0; i < map.LayerCount; i++)
                {
                    var lyr = map.get_Layer(i) as IFeatureLayer;
                    if (lyr != null && lyr.Name == layerName)
                    {
                        IFields fields = lyr.FeatureClass.Fields;
                        for (int j = 0; j < fields.FieldCount; j++)
                        {
                            IField f = fields.get_Field(j);
                            if (f.Type != esriFieldType.esriFieldTypeGeometry &&
                                f.Type != esriFieldType.esriFieldTypeBlob &&
                                f.Type != esriFieldType.esriFieldTypeRaster)
                            {
                                fieldSet.Add(f.Name + "(别名" + f.AliasName + ")");
                            }
                        }
                        break;
                    }
                }
            }

            if (fieldSet.Count == 0)
            {
                MessageBox.Show("所选图层没有可用的查询字段。", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            List<string> availableFields = new List<string>(fieldSet);
            this.Enabled = false;
            try
            {
                string generatedCondition = GenerateSqlConditionWithGLM(availableFields, userRequirement);
                if (!string.IsNullOrEmpty(generatedCondition))
                {
                    txtSqlWhere.Text = generatedCondition;
                }
            }
            finally
            {
                this.Enabled = true;
            }
        }

        // 核心搜索逻辑
        private void PerformSearchOnLayers(List<string> layerNames, string condition, bool isFuzzy, List<string> fieldNames)
        {
            allFoundFeatures.Clear();
            allFoundLayerNames.Clear();
            IMxDocument mxDoc = m_app.Document as IMxDocument;
            if (mxDoc == null || mxDoc.FocusMap == null) return;

            IMap map = mxDoc.FocusMap;
            IEnvelope unionEnvelope = null;

            foreach (string layerName in layerNames)
            {
                IFeatureLayer fl = null;
                for (int i = 0; i < map.LayerCount; i++)
                {
                    ILayer lyr = map.get_Layer(i);
                    IFeatureLayer featureLyr = lyr as IFeatureLayer;
                    if (featureLyr != null && featureLyr.Name == layerName)
                    {
                        fl = featureLyr;
                        break;
                    }
                }
                if (fl == null) continue;

                // 查询条件
                IQueryFilter filter = new QueryFilterClass();

                if (fieldNames != null)
                {
                    if (fieldNames.Count == 0) continue;

                    List<string> clauses = new List<string>();
                    foreach (string fieldName in fieldNames)
                    {
                        int idx = fl.FeatureClass.Fields.FindField(fieldName);
                        if (idx == -1) continue;

                        IField f = fl.FeatureClass.Fields.get_Field(idx);
                        if (f.Type == esriFieldType.esriFieldTypeString)
                        {
                            string safeKeyword = condition.Replace("'", "''");
                            if (isFuzzy)
                            {
                                clauses.Add(string.Format("{0} LIKE '%{1}%'", fieldName, safeKeyword));
                            }
                            else
                            {
                                clauses.Add(string.Format("{0} = '{1}'", fieldName, safeKeyword));
                            }
                        }
                        else if (f.Type == esriFieldType.esriFieldTypeInteger ||
                                 f.Type == esriFieldType.esriFieldTypeSingle ||
                                 f.Type == esriFieldType.esriFieldTypeDouble ||
                                 f.Type == esriFieldType.esriFieldTypeOID)
                        {
                            if (!isFuzzy)
                            {
                                double temp;
                                // 将字符串转换为数字
                                if (double.TryParse(condition, out temp))
                                {
                                    clauses.Add(string.Format("{0} = {1}", fieldName, condition));
                                }
                            }
                        }
                    }
                    if (clauses.Count == 0) continue;
                    filter.WhereClause = string.Join(" OR ", clauses.ToArray());
                }
                else
                {
                    filter.WhereClause = condition;
                }

                // 遍历查询结果中的地理要素
                IFeatureCursor cursor = null;
                try
                {
                    try
                    {
                        cursor = fl.FeatureClass.Search(filter, false);
                    }
                    catch (System.Runtime.InteropServices.COMException comEx)
                    {
                        // 跳过不存在字段的报错 错误代码0x80040653
                        const int FDO_E_FIELD_NOT_FOUND = unchecked((int)0x80040653);
                        if (comEx.ErrorCode == FDO_E_FIELD_NOT_FOUND)
                        {
                            continue;
                        }
                        // 格式化为 8 位十六进制字符串的方法调用
                        string msg = string.Format("图层 \"{0}\" 查询失败（错误 {1}）：\n{2}", layerName, comEx.ErrorCode.ToString("X8"), comEx.Message);
                        MessageBox.Show(msg, "SQL 查询错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                        continue;
                    }
                    catch (Exception ex)
                    {
                        string msg = string.Format("图层 \"{0}\" 查询失败：\n{1}", layerName, ex.Message);
                        MessageBox.Show(msg, "SQL 查询错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                        continue;
                    }

                    IFeature feat;
                    // 切换到下一个游标
                    while ((feat = cursor.NextFeature()) != null)
                    {
                        allFoundFeatures.Add(feat);
                        allFoundLayerNames.Add(layerName);
                        IGeometry geom = feat.ShapeCopy;
                        if (geom != null && !geom.IsEmpty)
                        {
                            IEnvelope env = geom.Envelope;
                            if (unionEnvelope == null) unionEnvelope = env;
                            else unionEnvelope.Union(env);
                        }
                    }
                }
                finally
                {
                    // 手动释放 ArcObjects 中的 COM 游标对象
                    if (cursor != null) System.Runtime.InteropServices.Marshal.ReleaseComObject(cursor);
                }
            }

            ClearAllSelections(map);
            HighlightAllResults();
            DisplayResultsInGrid();
            ShowKanbanCard(0);

            if (unionEnvelope != null && !unionEnvelope.IsEmpty)
            {
                double expandFactor = allFoundFeatures.Count == 1 ? 1.2 : 1.3;
                unionEnvelope.Expand(expandFactor, expandFactor, true);
                mxDoc.ActiveView.Extent = unionEnvelope;
                mxDoc.ActiveView.Refresh();
            }
            currentKanbanIndex = 0;
        }

        // GLM-4.6V-FLASH 调用
        private string GenerateSqlConditionWithGLM(List<string> availableFields, string userRequirement)
        {
            try
            {
                string fieldList = string.Join(", ", availableFields.ToArray());

                string rawPrompt = "根据用户提供的字段名和需求，生成能在ArcMap 10.2中直接使用的SQL条件。" +
                                   "核心规则：" +
                                   "1. 字符串连接符必须使用双竖线||。" +
                                   "2. 通配符必须使用百分号%。" +
                                   "3. 字段引用绝对不要给字段名添加双引号\"或方括号[]。直接使用字段名原样输出。" +
                                   "4. 日期格式必须使用 date 'YYYY-MM-DD' 格式。" +
                                   "输出要求：" +
                                   "1. 只返回WHERE子句后面的具体条件逻辑，绝对不要包含WHERE这个单词。" +
                                   "2. 必须严格输出标准的JSON格式，**不要有```json ```包裹**。" +
                                   "3. JSON中仅包含一个键值对，键名为\"where_condition\"。" +
                                   "示例参考：" +
                                   "需求：查找名字叫张三或者名字叫李四的人 输出：{\"where_condition\": \"NAME = '张三' OR NAME = '李四'\"}" +
                                   "现在开始生成，请根据以下信息输出：" +
                                   "可用字段：" + fieldList +
                                   "需求文本：" + userRequirement +
                                   "**不要有```json ```包裹**";

                string escapedPrompt = rawPrompt
                    .Replace("\\", "\\\\")
                    .Replace("\"", "\\\"")
                    .Replace("\n", "\\n")
                    .Replace("\r", "\\r")
                    .Replace("\t", "\\t");

                string jsonPayload = "{"
                    + "\"model\":\"glm-4.6v-flash\","
                    + "\"messages\":[{"
                        + "\"role\":\"user\","
                        + "\"content\":[{"
                            + "\"type\":\"text\","
                            + "\"text\":" + "\"" + escapedPrompt + "\""
                        + "}]"
                    + "}],"
                    + "\"thinking\":{\"type\":\"enabled\"}"
                    + "}";

                System.Net.HttpWebRequest request = (System.Net.HttpWebRequest)System.Net.WebRequest.Create("https://open.bigmodel.cn/api/paas/v4/chat/completions");
                request.Method = "POST";
                request.Headers.Add("Authorization", "Bearer " + GLM_API_KEY);
                request.ContentType = "application/json";

                // 编码为UTF-8格式的字节数组
                byte[] postData = System.Text.Encoding.UTF8.GetBytes(jsonPayload);
                request.ContentLength = postData.Length;

                // 发送请求，使用后被正确关闭
                System.IO.Stream reqStream = null;
                try
                {
                    reqStream = request.GetRequestStream();
                    reqStream.Write(postData, 0, postData.Length);
                }
                finally
                {
                    if (reqStream != null)
                        reqStream.Close();
                }

                // 从HTTP响应中读取返回的JSON数据，正确释放网络资源
                System.Net.HttpWebResponse response = null;
                System.IO.StreamReader reader = null;
                string jsonResponse = "";
                try
                {
                    response = (System.Net.HttpWebResponse)request.GetResponse();
                    reader = new System.IO.StreamReader(response.GetResponseStream(), System.Text.Encoding.UTF8);
                    jsonResponse = reader.ReadToEnd();
                }
                finally
                {
                    if (reader != null) reader.Close();
                    if (response != null) response.Close();
                }

                // JSON 字符串解析为一个可操作的字典对象
                // {
                //  "choices": [
                //    {
                //      "message": {
                //        "content": "{\"where_condition\": \"CITY = '北京'\"}"
                //      }
                //    }
                //  ]
                //}
                System.Web.Script.Serialization.JavaScriptSerializer serializer = new System.Web.Script.Serialization.JavaScriptSerializer();
                System.Collections.Generic.Dictionary<string, object> responseObject =
                    (System.Collections.Generic.Dictionary<string, object>)serializer.DeserializeObject(jsonResponse);

                if (responseObject != null && responseObject.ContainsKey("choices"))
                {
                    object[] choices = (object[])responseObject["choices"];
                    if (choices.Length > 0)
                    {
                        System.Collections.Generic.Dictionary<string, object> firstChoice =
                            (System.Collections.Generic.Dictionary<string, object>)choices[0];

                        if (firstChoice != null && firstChoice.ContainsKey("message"))
                        {
                            System.Collections.Generic.Dictionary<string, object> message =
                                (System.Collections.Generic.Dictionary<string, object>)firstChoice["message"];

                            if (message != null && message.ContainsKey("content"))
                            {
                                string content = (string)message["content"];
                                try
                                {
                                    System.Collections.Generic.Dictionary<string, object> sqlResult =
                                        (System.Collections.Generic.Dictionary<string, object>)serializer.DeserializeObject(content);

                                    if (sqlResult != null && sqlResult.ContainsKey("where_condition"))
                                    {
                                        return (string)sqlResult["where_condition"];
                                    }
                                }
                                catch (System.Exception)
                                {
                                    System.Windows.Forms.MessageBox.Show(
                                        "模型返回内容无法解析为有效 JSON。\n原始内容：\n" + content,
                                        "解析错误",
                                        System.Windows.Forms.MessageBoxButtons.OK,
                                        System.Windows.Forms.MessageBoxIcon.Error);
                                    return null;
                                }
                            }
                        }
                    }
                }
                System.Windows.Forms.MessageBox.Show("模型未返回有效结果。", "提示", System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Warning);
                return null;
            }
            catch (System.Net.WebException)
            {
                System.Windows.Forms.MessageBox.Show("网络发生错误: ", "网络错误", System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Error);
            }
            catch (System.Exception ex)
            {
                System.Windows.Forms.MessageBox.Show("发生未知错误：" + ex.Message, "错误", System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Error);
            }

            return null;
        }

        // 显示查询结果的文本
        private void UpdateResultSummary()
        {
            if (allFoundFeatures.Count == 0)
            {
                ResultText.Text = "查询合计：无结果";
                return;
            }

            Dictionary<string, int> layerCount = new Dictionary<string, int>();
            foreach (string layerName in allFoundLayerNames)
            {
                if (layerCount.ContainsKey(layerName))
                    layerCount[layerName]++;
                else
                    layerCount[layerName] = 1;
            }

            List<KeyValuePair<string, int>> list = new List<KeyValuePair<string, int>>(layerCount);
            list.Sort((x, y) => x.Value.CompareTo(y.Value));

            StringBuilder sb = new StringBuilder();
            sb.Append("查询合计：");
            int sum = 0;
            for (int i = 0; i < list.Count; i++)
            {
                if (i > 0) sb.Append("、");
                sb.AppendFormat("{0}图层{1}个", list[i].Key, list[i].Value);
                sum += list[i].Value;
            }
            sb.AppendFormat("，合计{0}个。", sum);
            ResultText.Text = sb.ToString();
        }

        // 清除所有选中的图层要素
        private void ClearAllSelections(IMap map)
        {
            for (int i = 0; i < map.LayerCount; i++)
            {
                ILayer layer = map.get_Layer(i);
                if (layer is IFeatureLayer)
                {
                    IFeatureLayer fl = (IFeatureLayer)layer;
                    IFeatureSelection sel = fl as IFeatureSelection;
                    if (sel != null)
                    {
                        sel.Clear();
                    }
                }
            }
        }

        // 按图层分组，进行高亮选择
        private void HighlightAllResults()
        {
            Dictionary<string, List<int>> layerOids = new Dictionary<string, List<int>>();
            for (int i = 0; i < allFoundFeatures.Count; i++)
            {
                string layerName = allFoundLayerNames[i];
                int oid = allFoundFeatures[i].OID;
                if (!layerOids.ContainsKey(layerName))
                    layerOids[layerName] = new List<int>();
                layerOids[layerName].Add(oid);
            }

            IMxDocument mxDoc = m_app.Document as IMxDocument;
            if (mxDoc == null) return;
            IMap map = mxDoc.FocusMap;
            if (map == null) return;

            foreach (var pair in layerOids)
            {
                // 获取图层对象
                IFeatureLayer layer = null;
                for (int i = 0; i < map.LayerCount; i++)
                {
                    ILayer lyr = map.get_Layer(i);
                    if (lyr is IFeatureLayer && lyr.Name == pair.Key)
                    {
                        layer = lyr as IFeatureLayer;
                        break;
                    }
                }
                if (layer != null)
                {
                    IFeatureSelection featureSel = layer as IFeatureSelection;
                    if (featureSel == null) continue;
                    featureSel.Clear();
                    List<int> oids = pair.Value;
                    if (oids == null || oids.Count == 0) continue;
                    // 获取当前图层要素类中 ObjectID 字段的实际字段名称
                    string oidFieldName = layer.FeatureClass.OIDFieldName;
                    string[] oidStrings = new string[oids.Count];
                    for (int j = 0; j < oids.Count; j++)
                    {
                        oidStrings[j] = oids[j].ToString();
                    }
                    string oidList = string.Join(",", oidStrings);
                    IQueryFilter queryFilter = new QueryFilterClass();
                    queryFilter.WhereClause = string.Format("{0} IN ({1})", oidFieldName, oidList);
                    // 构建查询集
                    // 定义要选择哪些要素, 返回类型为ID集合,使用“普通”选择方式,一次性获取(不分页)
                    ISelectionSet selSet = layer.FeatureClass.Select(
                        queryFilter, esriSelectionType.esriSelectionTypeIDSet, esriSelectionOption.esriSelectionOptionNormal, null);
                    featureSel.SelectionSet = selSet;
                }
            }
            // 重绘地图的特定部分内容
            // 选择状态,全部图层，全部范围
            mxDoc.ActiveView.PartialRefresh(esriViewDrawPhase.esriViewGeoSelection, null, null);
        }

        // 展示表格数据
        private void DisplayResultsInGrid()
        {
            dataGridView1.Rows.Clear();
            dataGridView1.Columns.Clear();
            if (allFoundFeatures.Count == 0)
            {
                // 清空子控件
                panelKanban.Controls.Clear();
                lblKanbanIndex.Text = "";
                return;
            }

            dataGridView1.Columns.Add("__LayerName__", "所在图层");

            Dictionary<string, string> aliasMap = new Dictionary<string, string>();
            foreach (IFeature feat in allFoundFeatures)
            {
                IFields fields = feat.Fields;
                for (int i = 0; i < fields.FieldCount; i++)
                {
                    IField field = fields.get_Field(i);
                    if (field.Type != esriFieldType.esriFieldTypeGeometry)
                    {
                        if (!aliasMap.ContainsKey(field.Name))
                        {
                            aliasMap[field.Name] = field.AliasName ?? field.Name;
                        }
                    }
                }
            }

            // 添加字段列
            List<string> fieldNames = new List<string>(aliasMap.Keys);
            fieldNames.Sort();
            foreach (string fieldName in fieldNames)
            {
                string header = aliasMap[fieldName];
                dataGridView1.Columns.Add(fieldName, header);
            }

            for (int rowIdx = 0; rowIdx < allFoundFeatures.Count; rowIdx++)
            {
                IFeature feat = allFoundFeatures[rowIdx];
                string layerName = allFoundLayerNames[rowIdx];
                IFields fields = feat.Fields;

                DataGridViewRow row = new DataGridViewRow();
                row.CreateCells(dataGridView1);
                row.Cells[0].Value = layerName;

                for (int colIdx = 1; colIdx < dataGridView1.Columns.Count; colIdx++)
                {
                    string fieldName = dataGridView1.Columns[colIdx].Name;
                    // 获取index
                    int fieldIndex = fields.FindField(fieldName);
                    if (fieldIndex != -1)
                    {
                        object val = feat.get_Value(fieldIndex);
                        row.Cells[colIdx].Value = val != null ? val.ToString() : "";
                    }
                }
                dataGridView1.Rows.Add(row);
            }
        }

        // 显示看板视图
        private void ShowKanbanCard(int index)
        {
            if (allFoundFeatures.Count == 0) return;

            panelKanban.Controls.Clear();
            lblKanbanIndex.Text = string.Format("{0} / {1}", index + 1, allFoundFeatures.Count);

            IFeature feat = allFoundFeatures[index];
            string layerName = allFoundLayerNames[index];

            Label infoLabel = new Label();
            infoLabel.AutoSize = true;
            infoLabel.Font = new Font(FontFamily.GenericSansSerif, 9, FontStyle.Regular);
            infoLabel.Margin = new Padding(10);

            var lines = new List<string>();
            lines.Add("所在图层:" + layerName);

            var fields = new List<KeyValuePair<string, string>>();
            IFields fset = feat.Fields;
            for (int i = 0; i < fset.FieldCount; i++)
            {
                IField f = fset.get_Field(i);
                if (f.Type != esriFieldType.esriFieldTypeGeometry)
                {
                    string alias = f.AliasName ?? f.Name;
                    object val = feat.get_Value(i);
                    string valStr = (val ?? "").ToString();
                    fields.Add(new KeyValuePair<string, string>(alias, valStr));
                }
            }

            // 按字段名排序
            fields.Sort((x, y) => x.Key.CompareTo(y.Key));

            foreach (var field in fields)
            {
                lines.Add(field.Key + ": " + field.Value);
            }

            infoLabel.Text = string.Join("\r\n", lines.ToArray());
            panelKanban.Controls.Add(infoLabel);

            ZoomToFeature(index);
        }

        // 缩放窗口并高亮
        private void ZoomToFeature(int index)
        {
            if (index < 0 || index >= allFoundFeatures.Count) return;
            IFeature feat = allFoundFeatures[index];
            IGeometry geom = feat.ShapeCopy;
            if (geom == null || geom.IsEmpty) return;

            IMxDocument mxDoc = m_app.Document as IMxDocument;
            IActiveView av = mxDoc.ActiveView;
            IEnvelope env = geom.Envelope;
            double expandFactor = 1.2;
            // 点
            if (env.Width < 1e-6 || env.Height < 1e-6)
            {
                double size = 5.0;
                env.XMin -= size;
                env.YMin -= size;
                env.XMax += size;
                env.YMax += size;
            }
            else
            {
                env.Expand(expandFactor, expandFactor, true);
            }
            av.Extent = env;
            av.Refresh();
            ClearTemporaryHighlight();

            try
            {
                // 定义线符号及其属性
                ISimpleLineSymbol lineSymbol = new SimpleLineSymbolClass();
                lineSymbol.Style = esriSimpleLineStyle.esriSLSSolid; // 实线
                lineSymbol.Width = 10.0;
                IRgbColor color = new RgbColorClass();
                color.Red = 255;
                color.Green = 0;
                color.Blue = 0;
                lineSymbol.Color = color;

                IElement highlightElement = null;
                if (geom.GeometryType == esriGeometryType.esriGeometryPolygon)
                {
                    ITopologicalOperator topo = geom as ITopologicalOperator;
                    IGeometry boundary = topo.Boundary;
                    ILineElement lineElement = new LineElementClass();
                    lineElement.Symbol = lineSymbol;
                    ((IElement)lineElement).Geometry = boundary;
                    highlightElement = (IElement)lineElement;
                }
                else if (geom.GeometryType == esriGeometryType.esriGeometryPolyline)
                {
                    ILineElement lineElement = new LineElementClass();
                    lineElement.Symbol = lineSymbol;
                    ((IElement)lineElement).Geometry = geom;
                    highlightElement = (IElement)lineElement;
                }
                else if (geom.GeometryType == esriGeometryType.esriGeometryPoint)
                {
                    IPoint point = geom as IPoint;
                    double radius = Math.Max(env.Width, env.Height) * 0.05;
                    if (radius < 1e-6) radius = 10.0;
                    ITopologicalOperator topo = point as ITopologicalOperator;
                    IPolygon circle = topo.Buffer(radius) as IPolygon;
                    IGeometry circleBoundary = (circle as ITopologicalOperator).Boundary;
                    ILineElement lineElement = new LineElementClass();
                    lineElement.Symbol = lineSymbol;
                    ((IElement)lineElement).Geometry = circleBoundary;
                    highlightElement = (IElement)lineElement;
                }

                if (highlightElement != null)
                {
                    // 获取当前视图的图形容器
                    IGraphicsContainer gc = av as IGraphicsContainer;
                    gc.AddElement(highlightElement, 0);
                    currentHighlightElement = highlightElement;
                    // // 选择状态,全部图层，全部范围
                    av.PartialRefresh(esriViewDrawPhase.esriViewGraphics, null, null);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine("高亮绘制失败: " + ex.Message);
            }
        }

        // 清除高亮元素
        private void ClearTemporaryHighlight()
        {
            if (currentHighlightElement != null)
            {
                IMxDocument mxDoc = m_app.Document as IMxDocument;
                IActiveView av = mxDoc.ActiveView;
                IGraphicsContainer gc = av as IGraphicsContainer;
                gc.DeleteElement(currentHighlightElement);
                currentHighlightElement = null;
                av.PartialRefresh(esriViewDrawPhase.esriViewGraphics, null, null);
            }
        }

        // 看板向左
        private void btnPrev_Click(object sender, EventArgs e)
        {
            if (currentKanbanIndex > 0)
            {
                currentKanbanIndex--;
                ShowKanbanCard(currentKanbanIndex);
            }
        }

        // 看板向右
        private void btnNext_Click(object sender, EventArgs e)
        {
            if (currentKanbanIndex < allFoundFeatures.Count - 1)
            {
                currentKanbanIndex++;
                ShowKanbanCard(currentKanbanIndex);
            }
        }

        // 表格选择
        private void dataGridView1_SelectionChanged(object sender, EventArgs e)
        {
            if (dataGridView1.SelectedRows.Count > 0)
            {
                int rowIndex = dataGridView1.SelectedRows[0].Index;
                ZoomToFeature(rowIndex);
            }
        }

        // 列表/看板 tab切换
        private void tabControlResult_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (tabControlResult.SelectedTab == tabPageKanban)
            {
                ShowKanbanCard(currentKanbanIndex);
            }
        }

        // csv导出
        private void btnExportCSV_Click(object sender, EventArgs e)
        {
            if (allFoundFeatures.Count == 0)
            {
                MessageBox.Show("没有数据可导出。");
                return;
            }

            SaveFileDialog sfd = new SaveFileDialog
            {
                Filter = "CSV 文件|*.csv",
                FileName = "search_result.csv"
            };

            if (sfd.ShowDialog() != DialogResult.OK) return;

            try
            {
                using (StreamWriter sw = new StreamWriter(sfd.FileName, false, Encoding.UTF8))
                {
                    // 构建表头（不含 __LayerName__ 列）
                    List<string> headers = new List<string> { "所在图层" };
                    foreach (DataGridViewColumn col in dataGridView1.Columns)
                    {
                        if (col.Name != "__LayerName__")
                            headers.Add(col.HeaderText ?? "");
                    }
                    sw.WriteLine(string.Join(",", headers.ToArray()));

                    // 写入数据行
                    foreach (DataGridViewRow row in dataGridView1.Rows)
                    {
                        if (row.IsNewRow) continue;

                        List<string> cells = new List<string>();

                        cells.Add((row.Cells["__LayerName__"].Value ?? "").ToString());


                        foreach (DataGridViewCell cell in row.Cells)
                        {
                            if (cell.OwningColumn.Name == "__LayerName__") continue;
                            cells.Add((cell.Value ?? "").ToString());
                        }

                        sw.WriteLine(string.Join(",", cells.ToArray()));
                    }
                }
                MessageBox.Show("导出成功！");
            }
            catch (Exception ex)
            {
                MessageBox.Show("导出失败：" + ex.Message);
            }
        }

        // 关闭窗口，清除选择
        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            ClearTemporaryHighlight();
            IMxDocument mxDoc = m_app.Document as IMxDocument;
            if (mxDoc != null)
            {
                IMap focusMap = mxDoc.FocusMap;
                ClearAllSelections(focusMap);
                IActiveView activeView = mxDoc.ActiveView;
                if (activeView != null)
                {
                    activeView.PartialRefresh(esriViewDrawPhase.esriViewGeography, null, null);
                }
            }
            base.OnFormClosing(e);
        }
    }
}