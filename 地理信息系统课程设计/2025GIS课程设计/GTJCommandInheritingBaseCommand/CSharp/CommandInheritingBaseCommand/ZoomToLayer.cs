// Copyright 2013 ESRI
// 
// All rights reserved under the copyright laws of the United States
// and applicable international laws, treaties, and conventions.
// 
// You may freely redistribute and use this sample code, with or
// without modification, provided you include the original copyright
// notice and use restrictions.
// 
// See the use restrictions at <your ArcGIS install location>/DeveloperKit10.2/userestrictions.txt.
// 

using System;
using System.Drawing;
using System.Runtime.InteropServices;
using ESRI.ArcGIS.ADF.BaseClasses;
using ESRI.ArcGIS.ADF.CATIDs;
using ESRI.ArcGIS.Framework;
using ESRI.ArcGIS.ArcMapUI;

namespace CommandInheritingBaseCommand
{
    /// <summary>
    /// Summary description for ZoomToLayer.
    /// </summary>
    [Guid("46bd0933-acac-4c33-8669-1255db03ca5c")]
    [ClassInterface(ClassInterfaceType.None)]
    [ProgId("CommandInheritingBaseCommand.ZoomToLayer")]
    public sealed class ZoomToLayer : BaseCommand
    {
        #region COM Registration Function(s)
        [ComRegisterFunction()]
        [ComVisible(false)]
        static void RegisterFunction(Type registerType)
        {
            // Required for ArcGIS Component Category Registrar support
            ArcGISCategoryRegistration(registerType);

            //
            // TODO: Add any COM registration code here
            //
        }

        [ComUnregisterFunction()]
        [ComVisible(false)]
        static void UnregisterFunction(Type registerType)
        {
            // Required for ArcGIS Component Category Registrar support
            ArcGISCategoryUnregistration(registerType);

            //
            // TODO: Add any COM unregistration code here
            //
        }

        #region ArcGIS Component Category Registrar generated code
        /// <summary>
        /// Required method for ArcGIS Component Category registration -
        /// Do not modify the contents of this method with the code editor.
        /// </summary>
        private static void ArcGISCategoryRegistration(Type registerType)
        {
            string regKey = string.Format("HKEY_CLASSES_ROOT\\CLSID\\{{{0}}}", registerType.GUID);
            MxCommands.Register(regKey);

        }
        /// <summary>
        /// Required method for ArcGIS Component Category unregistration -
        /// Do not modify the contents of this method with the code editor.
        /// </summary>
        private static void ArcGISCategoryUnregistration(Type registerType)
        {
            string regKey = string.Format("HKEY_CLASSES_ROOT\\CLSID\\{{{0}}}", registerType.GUID);
            MxCommands.Unregister(regKey);

        }

        #endregion
        #endregion

        private IApplication m_application;
        public ZoomToLayer()
        {
            //
            // TODO: Define values for the public properties
            //
            base.m_category = "Developer Samples"; //localizable text
            base.m_caption = "Zoom To Layer CSharp"; //localizable text
            base.m_message = "Zoom to the extent of the active layer in the TOC"; //localizable text 
            base.m_toolTip = "Zoom To Layer CSharp"; //localizable text 
            base.m_name = "DeveloperSamples_ZoomToLayerCSharp"; //unique id, non-localizable (e.g. "MyCategory_ArcMapCommand")
            try
            {
                //
                // TODO: change bitmap name if necessary
                //
                string bitmapResourceName = GetType().Name + ".bmp";
                base.m_bitmap = new Bitmap(GetType(), bitmapResourceName);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Trace.WriteLine(ex.Message, "Invalid Bitmap");
            }
        }

        #region Overriden Class Methods

        /// <summary>
        /// Occurs when this command is created
        /// </summary>
        /// <param name="hook">Instance of the application</param>
        public override void OnCreate(object hook)
        {
            if (hook == null)
                return;

            m_application = hook as IApplication;

            //Disable if it is not ArcMap
            if (hook is IMxApplication)
                base.m_enabled = true;
            else
                base.m_enabled = false;

            // TODO:  Add other initialization code
        }

        /// <summary>
        /// Occurs when this command is clicked
        /// </summary>
        public override void OnClick()
        {
            IMxDocument mxDocument = GetMxDocument(m_application);
            //ZoomToLayerInTOC(mxDocument);
            NeuForm myform = new NeuForm();
            myform.Init(m_application);
            myform.Show();
        }

        #endregion

        #region "Zoom to Active Layer in TOC"
        // ArcGIS Snippet Title: 
        // Zoom to Active Layer in TOC
        //
        // Add the following references to the project:
        // ESRI.ArcGIS.ArcMapUI
        // ESRI.ArcGIS.Carto
        // ESRI.ArcGIS.Geometry
        // 
        // Intended ArcGIS Products for this snippet:
        // ArcGIS Desktop
        //
        // Required ArcGIS Extensions:
        // (NONE)
        //
        // Notes:
        // This snippet is intended to be inserted at the base level of a Class.
        // It is not intended to be nested within an existing Method.
        //
        // Use the following XML documentation comments to use this snippet:
        /// <summary>Zooms to the selected layer in the TOC associated with the active view.</summary>
        ///
        /// <param name="mxDocument">An IMxDocument interface</param>
        /// 
        /// <remarks></remarks>
        public void ZoomToLayerInTOC(ESRI.ArcGIS.ArcMapUI.IMxDocument mxDocument)
        {
            if (mxDocument == null)
            {
                return;
            }
            ESRI.ArcGIS.Carto.IActiveView activeView = mxDocument.ActiveView;

            // Get the TOC
            ESRI.ArcGIS.ArcMapUI.IContentsView IContentsView = mxDocument.CurrentContentsView;

            // Get the selected layer
            System.Object selectedItem = IContentsView.SelectedItem;
            if (!(selectedItem is ESRI.ArcGIS.Carto.ILayer))
            {
                return;
            }
            ESRI.ArcGIS.Carto.ILayer layer = selectedItem as ESRI.ArcGIS.Carto.ILayer;


            // Zoom to the extent of the layer and refresh the map
            activeView.Extent = layer.AreaOfInterest;
            activeView.Refresh();
        }
        #endregion

        #region "Get MxDocument from ArcMap"
        // ArcGIS Snippet Title: 
        // Get MxDocument from ArcMap
        //
        // Add the following references to the project:
        // ESRI.ArcGIS.ArcMapUI
        // ESRI.ArcGIS.Framework
        // ESRI.ArcGIS.System
        // 
        // Intended ArcGIS Products for this snippet:
        // ArcGIS Desktop
        //
        // Required ArcGIS Extensions:
        // (NONE)
        //
        // Notes:
        // This snippet is intended to be inserted at the base level of a Class.
        // It is not intended to be nested within an existing Method.
        //
        // Use the following XML documentation comments to use this snippet:
        /// <summary>Get MxDocument from ArcMap.</summary>
        ///
        /// <param name="application">An IApplication interface that is the ArcMap application.</param>
        /// 
        /// <returns>An IMxDocument interface.</returns>
        /// 
        /// <remarks></remarks>
        public ESRI.ArcGIS.ArcMapUI.IMxDocument GetMxDocument(ESRI.ArcGIS.Framework.IApplication application)
        {

            if (application == null)
            {
                return null;
            }
            ESRI.ArcGIS.ArcMapUI.IMxDocument mxDocument = ((ESRI.ArcGIS.ArcMapUI.IMxDocument)(application.Document)); // Explicit Cast

            return mxDocument;

        }
        #endregion                     
                
    }
}
