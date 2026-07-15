/*
 Copyright 1995-2004 ESRI

 All rights reserved under the copyright laws of the United States.

 You may freely redistribute and use this sample code, with or without modification.

 Disclaimer: THE SAMPLE CODE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED 
 WARRANTIES, INCLUDING THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
 FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ESRI OR 
 CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, 
 OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
 SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
 INTERRUPTION) SUSTAINED BY YOU OR A THIRD PARTY, HOWEVER CAUSED AND ON ANY 
 THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT ARISING IN ANY 
 WAY OUT OF THE USE OF THIS SAMPLE CODE, EVEN IF ADVISED OF THE POSSIBILITY OF 
 SUCH DAMAGE.

 For additional information contact: Environmental Systems Research Institute, Inc.

 Attn: Contracts Dept.

 380 New York Street

 Redlands, California, U.S.A. 92373 

 Email: contracts@esri.com
*/
using System;
using ESRI.ArcGIS.Carto;
using ESRI.ArcGIS.Display;
using ESRI.ArcGIS.Geometry;
using ESRI.ArcGIS.ControlCommands;
using ESRI.ArcGIS.Utility.BaseClasses;
using ESRI.ArcGIS.Utility.CATIDs;
using System.Runtime.InteropServices;

namespace SelectCommands
{
  [ClassInterface(ClassInterfaceType.None)]
  [Guid("3362ba66-bf63-442a-a639-d18d583a028d")]
  public sealed class SelectFeatures : BaseTool
  {

    //Windows API functions to capture mouse and keyboard input to a window when the mouse is outside the window
    [DllImport("user32.dll")] public static extern long SetCapture(int hwnd);
    [DllImport("user32.dll")] public static extern long ReleaseCapture();

    private IHookHelper m_HookHelper = new HookHelperClass();
    bool m_InUse;
    System.Windows.Forms.Cursor m_Cursor;
    System.Windows.Forms.Cursor m_CursorMove;
    INewEnvelopeFeedback m_Feedback;
    ESRI.ArcGIS.Geometry.IPoint m_Point;
    
    #region Component Category Registration
    [ComRegisterFunction()]
    [ComVisible(false)]
    static void RegisterFunction(String regKey)
    {
      ControlsCommands.Register(regKey);
    }
  
    [ComUnregisterFunction()]
    [ComVisible(false)]
    static void UnregisterFunction(String regKey)
    {
      ControlsCommands.Unregister(regKey);
    }
    #endregion#  
                                    
    public SelectFeatures()
    {
      //Create an IHookHelper object
      m_HookHelper = new HookHelperClass();

      //Set the tool properties
      base.m_caption = "Select Features";
      base.m_category = "Sample_Select(C#)";
      base.m_name = "Sample_Select(C#)_Select Features";
      base.m_message = "Selects Features By Rectangle Or Single Click";
      base.m_toolTip = "Selects Features";
      base.m_deactivate = true;
      base.m_bitmap = new System.Drawing.Bitmap(GetType().Assembly.GetManifestResourceStream(GetType(), "SelectFeatures.bmp"));
      m_Cursor = base.m_cursor;
      m_CursorMove = new System.Windows.Forms.Cursor(GetType().Assembly.GetManifestResourceStream(GetType(), "SelectFeatures.cur"));
    }

    //Destructor
    ~SelectFeatures()
    {
      m_HookHelper = null;
      m_Cursor = null;
      m_CursorMove = null;
      m_Point = null;
      m_Feedback = null;
    }
  
    public override void OnCreate(object hook)
    {
      m_HookHelper.Hook = hook;
    }
  
    public override bool Enabled
    {
      get
      {
        if (m_HookHelper.FocusMap == null) return false;
        return (m_HookHelper.FocusMap.LayerCount > 0);
      }
    }
  
    public override void OnMouseDown(int Button, int Shift, int X, int Y)
    {
      //If the ActiveView is a PageLayout
      if (m_HookHelper.ActiveView is IPageLayout)
      {
        ESRI.ArcGIS.Geometry.IPoint point = m_HookHelper.ActiveView.ScreenDisplay.DisplayTransformation.ToMapPoint(X, Y);

        //See whether the mouse has been clicked over a Map
        IMap map = m_HookHelper.ActiveView.HitTestMap(point);
        //If mouse click isn't over a Map exit
        if (map == null) return; 
        //Ensure the Map is the FocusMap
        if (map != m_HookHelper.FocusMap)
        {
          m_HookHelper.ActiveView.FocusMap = map;
          m_HookHelper.ActiveView.PartialRefresh(esriViewDrawPhase.esriViewGraphics, null, null);
        }
      }

      //Get the focus map 
      IActiveView activeView = (IActiveView) m_HookHelper.FocusMap;
      //Get the point to start the feedback with
      m_Point = activeView.ScreenDisplay.DisplayTransformation.ToMapPoint(X, Y);

      m_InUse = true;
      SetCapture(m_HookHelper.ActiveView.ScreenDisplay.hWnd);
    }
  
    public override void OnMouseMove(int Button, int Shift, int X, int Y)
    {
      if (m_InUse == false) return;

      IActiveView activeView = (IActiveView) m_HookHelper.FocusMap;
      //Start the feedback if this is the first mouse move event
      if (m_Feedback == null )
      {
        m_Feedback = new NewEnvelopeFeedbackClass();
        m_Feedback.Display = activeView.ScreenDisplay;
        m_Feedback.Start(m_Point);
      }
      //Move the feedback to the new mouse coordinates
      m_Feedback.MoveTo(activeView.ScreenDisplay.DisplayTransformation.ToMapPoint(X, Y));
    }

    public override void OnMouseUp(int Button, int Shift, int X, int Y)
    {
      if (m_InUse == false) return;
      ReleaseCapture();

      //Get the search geometry
      IGeometry geom;
      if (m_Feedback == null) 
      {
        geom = m_Point;
      }
      else
      {
        geom = m_Feedback.Stop();
        if (geom.IsEmpty) geom = m_Point;
      }

      //Set the spatial reference of the search geometry to that of the Map
      IMap map = m_HookHelper.FocusMap;
      ISpatialReference spatialReference = map.SpatialReference;
      geom.SpatialReference = spatialReference;

      //Refresh the active view
      IActiveView activeView = (IActiveView) map;
      map.SelectByShape(geom, null, false);
      activeView.PartialRefresh(esriViewDrawPhase.esriViewGeoSelection, null, activeView.Extent);

      m_Feedback = null;
      m_InUse = false;
    }
  
    public override void OnKeyDown(int keyCode, int Shift)
    {
      if (m_InUse == true)
      {
        if (keyCode == 27)  //ESC key
        {
          ReleaseCapture();
          m_Feedback = null;
          m_InUse = false;
          m_HookHelper.ActiveView.PartialRefresh(esriViewDrawPhase.esriViewForeground, null, null);
        }
      }
    }
  
    public override int Cursor
    {
      get
      {
        if (m_InUse == true) 
        {
          return m_CursorMove.Handle.ToInt32();
        }
        else
        {
          return m_Cursor.Handle.ToInt32();
        }
      }
    }
  }
}