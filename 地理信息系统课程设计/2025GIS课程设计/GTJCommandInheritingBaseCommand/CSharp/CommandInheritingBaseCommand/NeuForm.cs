using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using ESRI.ArcGIS.ADF.BaseClasses;
using ESRI.ArcGIS.ADF.CATIDs;
using ESRI.ArcGIS.Framework;
using ESRI.ArcGIS.ArcMapUI;
using ESRI.ArcGIS.Geometry;
using ESRI.ArcGIS.Carto;
using ESRI.ArcGIS.Geodatabase;
using ESRI.ArcGIS.Display;



namespace CommandInheritingBaseCommand
{
      public partial class NeuForm : Form
    {
        private IApplication m_application;
        private IMxDocument m_pDoc;
        private IActiveView m_pAV;
        private IFeature m_pFeature;
        private ESRI.ArcGIS.Carto.IActiveViewEvents_ViewRefreshedEventHandler m_ActiveViewEventsViewRefreshed;
        public NeuForm()
        {
            InitializeComponent();
        }

        private void NeuForm_Load(object sender, EventArgs e)
        {

        }
        public void Init(IApplication application)
        {
            if (application == null)
                return;
            m_application = application;
            m_pDoc = application.Document as IMxDocument;
            m_pAV = m_pDoc.ActiveView;
        }
           
        public IFeature SelectMapFeaturesByAttributeQuery(ESRI.ArcGIS.Carto.IActiveView activeView, ESRI.ArcGIS.Carto.IFeatureLayer featureLayer, System.String whereClause)
        {
            if (activeView == null || featureLayer == null || whereClause == null)
            {
                return null;
            }
            ESRI.ArcGIS.Carto.IFeatureSelection featureSelection = featureLayer as ESRI.ArcGIS.Carto.IFeatureSelection; // Dynamic Cast

            // Set up the query
            ESRI.ArcGIS.Geodatabase.IQueryFilter queryFilter = new ESRI.ArcGIS.Geodatabase.QueryFilterClass();
            queryFilter.WhereClause = whereClause;

            // Invalidate only the selection cache. Flag the original selection
            activeView.PartialRefresh(ESRI.ArcGIS.Carto.esriViewDrawPhase.esriViewGeoSelection, null, null);

            // Perform the selection,原始特效选择结果加入选择集
           // featureSelection.SelectFeatures(queryFilter, ESRI.ArcGIS.Carto.esriSelectionResultEnum.esriSelectionResultNew, false);
            // Flag the new selection

            //IMap pmap=m_pDoc.FocusMap;
			
            IFeatureCursor featureCursor=featureLayer.Search(queryFilter,false);
           
            IFeature feature = featureCursor.NextFeature();
            if (feature != null)
			{
                featureSelection.Add(feature);
				activeView.PartialRefresh(ESRI.ArcGIS.Carto.esriViewDrawPhase.esriViewGeoSelection, null, null);
                return feature;
			}
            else
                return null;
        }

      

        private void button1_Click(object sender, EventArgs e)
        {
            IMap pMap=m_pDoc.FocusMap;
            if (pMap.LayerCount <= 0)
            {
                return;
            }
            ILayer pLayer= pMap.get_Layer(0);
           
            IFeatureLayer pFeatureLayer=null;
            if (pLayer is IFeatureLayer)
            {
                pFeatureLayer=pLayer as IFeatureLayer;
            }
            else
            {
              return;
            }
            if (textBox1.Text=="")
            {
                return;
            }
            string strWhere = "OBJECTID=" + textBox1.Text;
            IFeature pFeature = SelectMapFeaturesByAttributeQuery(m_pAV, pFeatureLayer, strWhere);
            if(pFeature != null)
            {
                FlashFeature(pFeature);
               
            }
          

            //MessageBox.Show(m_application.Caption);
        }
        private void FlashFeature(IFeature pFeature)
        {
            IActiveView activeView = m_pDoc.ActiveView;
            IGeometry geom = pFeature.ShapeCopy;
            IDisplay display = activeView.ScreenDisplay;
            display.SetSymbol(new SimpleFillSymbolClass { Color = new RgbColorClass { Red = 255 } });
            for (int i = 0; i < 4; i++)
            {
                display.DrawPolygon(geom);
                System.Threading.Thread.Sleep(200);
                activeView.PartialRefresh(esriViewDrawPhase.esriViewGraphics, null, null);
            }
        }
       

        private void button2_Click(object sender, EventArgs e)
        {
            IMap map = m_pDoc.FocusMap;
            ESRI.ArcGIS.Carto.IGraphicsContainer graphicsContainer = (ESRI.ArcGIS.Carto.IGraphicsContainer)map; // Explicit Cast
            graphicsContainer.DeleteAllElements();
            IActiveView pAV = m_pDoc.ActiveView;
            pAV.Refresh();
            this.Close();

        }
    }
}
