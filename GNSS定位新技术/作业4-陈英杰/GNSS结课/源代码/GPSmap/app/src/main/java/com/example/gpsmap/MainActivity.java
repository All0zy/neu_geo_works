/*
 * GPSmap 主功能代码文件（详细注释版）
 * ============================================================
 * 文件作用：
 * 1. 作为 App 的主 Activity，统一管理地图显示、定位回调、POI 搜索、路线规划、电子围栏、轨迹记录、拍照定位等基础功能。
 * 2. 在原有导航定位 App 基础上扩展“任务二”相关功能，包括坐标转换、GNSS 定位质量评估、定位精度评价、导航误差源分析、GNSS 异常/欺骗初筛、GNSS+惯性传感器组合导航展示。
 * 3. 采用“顶部摘要卡片 + 可展开功能模块”的交互方式，避免所有结果文字堆叠在主界面，提高界面清晰度和答辩展示效果。
 *
 * 注释阅读建议：
 * - 先看 onCreate()：理解 Activity 启动时如何依次完成隐私合规、布局加载、地图初始化、事件绑定、传感器初始化和权限申请。
 * - 再看 onLocationChanged()：理解定位结果如何驱动界面刷新、围栏判断、轨迹记录和扩展 GNSS 功能更新。
 * - 然后看“任务二功能面板显示控制”“坐标转换”“GNSS 定位质量评估”“异常检测”“传感器融合”等分区。
 * - 最后看搜索、路线、围栏、轨迹和拍照模块，理解原 App 功能如何与新扩展功能共同工作。
 *
 * 注意事项：
 * - 本注释版只增加说明性注释，不改变原有代码逻辑。
 * - GNSS 卫星数、C/N0、DOP 等数据依赖真机 GNSS 芯片和室外信号环境，模拟器通常无法提供真实卫星观测数据。
 */
package com.example.gpsmap;

// 权限相关常量，例如定位权限、相机权限
import android.Manifest;
// 用于获取系统服务，例如 GNSS 状态服务
import android.content.Context;
// 用于动态改变功能标签按钮的背景颜色
import android.content.res.ColorStateList;
// 用于启动系统组件，例如相机
import android.content.Intent;
// 用于权限检查结果判断
import android.content.pm.PackageManager;
// 用于保存拍照返回的缩略图
import android.graphics.Bitmap;
// 惯性传感器相关类，用于实现 GNSS + 手机传感器辅助航向判断
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
// GNSS 卫星状态对象，用于统计可见卫星数、参与定位卫星数、信噪比和卫星几何分布
import android.location.GnssStatus;
// 系统定位服务管理器，用于注册 GNSS 卫星状态回调
import android.location.LocationManager;
// 用于设置文本字体样式
import android.graphics.Typeface;
// 用于动态创建圆角、描边背景
import android.graphics.drawable.GradientDrawable;
// Activity 状态保存与恢复用的 Bundle
import android.os.Bundle;
// 系统相机拍照接口
import android.provider.MediaStore;
// 尺寸单位转换工具
import android.util.TypedValue;
// 控件内容对齐方式
import android.view.Gravity;
// 视图基类
import android.view.View;
// 视图容器相关类
import android.view.ViewGroup;
// 列表适配器基类
import android.widget.BaseAdapter;
// 按钮控件
import android.widget.Button;
// 输入框控件
import android.widget.EditText;
// 图片控件
import android.widget.ImageView;
// 线性布局控件
import android.widget.LinearLayout;
// 列表控件
import android.widget.ListView;
// 滑动条控件
import android.widget.SeekBar;
// 文本控件
import android.widget.TextView;
// 短提示控件
import android.widget.Toast;

// 非空注解
import androidx.annotation.NonNull;
// 对话框
import androidx.appcompat.app.AlertDialog;
// 兼容版 Activity
import androidx.appcompat.app.AppCompatActivity;
// 动态申请权限
import androidx.core.app.ActivityCompat;
// 兼容权限检查
import androidx.core.content.ContextCompat;

// 高德定位结果对象
import com.amap.api.location.AMapLocation;
// 高德定位客户端
import com.amap.api.location.AMapLocationClient;
// 高德定位参数配置
import com.amap.api.location.AMapLocationClientOption;
// 高德定位监听器
import com.amap.api.location.AMapLocationListener;
// 高德地图主对象
import com.amap.api.maps.AMap;
// 高德地图工具类，主要用于测距
import com.amap.api.maps.AMapUtils;
// 地图镜头更新工厂
import com.amap.api.maps.CameraUpdateFactory;
// 地图定位源接口
import com.amap.api.maps.LocationSource;
// 地图视图控件
import com.amap.api.maps.MapView;
// 高德隐私合规初始化工具
import com.amap.api.maps.MapsInitializer;
// Marker 图标工厂
import com.amap.api.maps.model.BitmapDescriptorFactory;
// 圆形覆盖物对象
import com.amap.api.maps.model.Circle;
// 圆形覆盖物配置
import com.amap.api.maps.model.CircleOptions;
// 经纬度对象
import com.amap.api.maps.model.LatLng;
// 地图范围对象，用于让路线整体显示在屏幕内
import com.amap.api.maps.model.LatLngBounds;
// Marker 对象
import com.amap.api.maps.model.Marker;
// Marker 配置对象
import com.amap.api.maps.model.MarkerOptions;
// 我的位置蓝点样式
import com.amap.api.maps.model.MyLocationStyle;
// 折线对象
import com.amap.api.maps.model.Polyline;
// 折线配置对象
import com.amap.api.maps.model.PolylineOptions;
// 高德服务异常
import com.amap.api.services.core.AMapException;
// 高德服务使用的经纬度点
import com.amap.api.services.core.LatLonPoint;
// POI 单个搜索结果
import com.amap.api.services.core.PoiItem;
// POI 搜索结果集合
import com.amap.api.services.poisearch.PoiResult;
// POI 搜索类
import com.amap.api.services.poisearch.PoiSearch;
// 公交路线结果，这里没有真正使用
import com.amap.api.services.route.BusRouteResult;
// 驾车路径对象
import com.amap.api.services.route.DrivePath;
// 驾车路线结果
import com.amap.api.services.route.DriveRouteResult;
// 骑行路线结果，这里没有真正使用
import com.amap.api.services.route.RideRouteResult;
// 路线搜索主类
import com.amap.api.services.route.RouteSearch;
// 步行路径对象
import com.amap.api.services.route.WalkPath;
// 步行路线结果
import com.amap.api.services.route.WalkRouteResult;
// 步行单步路径
import com.amap.api.services.route.WalkStep;

// 时间格式化
import java.text.SimpleDateFormat;
// 动态数组
import java.util.ArrayList;
// 键值映射
import java.util.HashMap;
// 列表接口
import java.util.List;
// 日期类
import java.util.Date;
// 数学数组工具，用于临时保存 DOP 计算矩阵
import java.util.Arrays;
// 本地化格式工具
import java.util.Locale;

/**
 * 主界面 Activity
 * 负责完成以下功能：
 * 1. 地图显示与定位
 * 2. 搜索地点与路线规划
 * 3. 电子围栏设置与状态判断
 * 4. 轨迹记录与清除
 * 5. 拍照定位与照片查看
 * 6. 坐标转换：GCJ-02、WGS84、BD-09 三套坐标联动显示
 * 7. GNSS 定位质量评估：可见卫星数、参与定位卫星数、C/N0、DOP 估算和质量等级
 * 8. GNSS 定位精度评价：水平精度、定位方式、速度和航向综合判断
 * 9. GNSS 导航误差源分析：根据信号、卫星几何和定位方式推断主要误差来源
 * 10. GNSS 异常/欺骗初筛：检测位置跳变、速度异常和卫星状态矛盾
 * 11. GNSS + 惯性传感器辅助导航：融合 GNSS 航向与手机姿态航向进行一致性判断
 */
public class MainActivity extends AppCompatActivity implements
        LocationSource,
        AMapLocationListener,
        AMap.OnMapLongClickListener,
        AMap.OnMarkerClickListener,
        PoiSearch.OnPoiSearchListener,
        RouteSearch.OnRouteSearchListener,
        SensorEventListener {

    // 定位权限请求码
    private static final int REQUEST_LOCATION_PERMISSION = 1001;
    // 相机权限请求码
    private static final int REQUEST_CAMERA_PERMISSION = 1002;
    // 调用系统相机的请求码
    private static final int REQUEST_IMAGE_CAPTURE = 2001;

    // 地图控件
    private MapView mapView;
    // 高德地图对象
    private AMap aMap;

    // 搜索关键字输入框
    private EditText etKeyword;
    // 搜索结果列表
    private ListView lvSearchResults;

    // 地址显示文本
    private TextView tvAddress;
    // 经纬度与精度显示文本
    private TextView tvCoord;
    // 坐标转换结果显示文本
    private TextView tvCoordConverted;
    // GNSS 定位质量评估显示文本
    private TextView tvGnssQuality;
    // GNSS 定位精度评价显示文本
    private TextView tvAccuracyEval;
    // GNSS 导航误差源分析显示文本
    private TextView tvErrorAnalysis;
    // GNSS 异常与欺骗初筛显示文本
    private TextView tvAnomalyDetect;
    // GNSS + 惯性传感器辅助导航显示文本
    private TextView tvSensorFusion;
    // 顶部摘要卡片：GNSS 质量摘要
    private TextView tvQuickGnss;
    // 顶部摘要卡片：定位精度摘要
    private TextView tvQuickAccuracy;
    // 顶部摘要卡片：异常检测摘要
    private TextView tvQuickAnomaly;
    // 当前选中的任务二功能标题
    private TextView tvFeatureTitle;
    // 当前选中的任务二功能详情
    private TextView tvFeatureContent;
    // 功能切换按钮：坐标转换
    private Button btnShowCoord;
    // 功能切换按钮：卫星质量
    private Button btnShowGnss;
    // 功能切换按钮：精度评价
    private Button btnShowAccuracy;
    // 功能切换按钮：误差源分析
    private Button btnShowError;
    // 功能切换按钮：异常检测
    private Button btnShowAnomaly;
    // 功能切换按钮：组合导航
    private Button btnShowSensor;
    // 功能模块内容区，默认收起，点击“展开”后显示具体功能按钮和详情卡片
    private LinearLayout layoutFeatureModuleContent;
    // 功能模块展开收起按钮
    private Button btnToggleFeatureModule;
    // 功能模块是否展开
    private boolean isFeatureModuleExpanded = false;
    // 当前详情卡片正在显示的功能类型
    private String activeFeaturePanel = "gnss";
    // 围栏状态显示文本
    private TextView tvFenceStatus;
    // 轨迹状态显示文本
    private TextView tvTrackStatus;
    // 路线状态显示文本
    private TextView tvRouteStatus;
    // 围栏半径显示文本
    private TextView tvFenceRadius;
    // 已选目的地显示文本
    private TextView tvSelectedDestination;

    // 顶部可展开的信息区
    private LinearLayout layoutSearchExtras;
    // 路线按钮区域
    private LinearLayout layoutRouteActions;
    // 围栏半径布局
    private LinearLayout layoutFenceRadius;
    // 围栏半径卡片
    private View cardFenceRadius;

    // 顶部展开收起按钮
    private Button btnToggleInfo;
    // 搜索按钮
    private Button btnSearch;
    // 步行路线按钮
    private Button btnWalkRoute;
    // 驾车路线按钮
    private Button btnDriveRoute;
    // 清除路线按钮
    private Button btnClearRoute;

    // 围栏按钮
    private Button btnFenceMode;
    // 清除围栏按钮
    private Button btnClearFence;

    // 拍照按钮
    private Button btnTakePhoto;
    // 清除拍照点按钮
    private Button btnClearPhotos;

    // 轨迹按钮
    private Button btnTrack;
    // 清除轨迹按钮
    private Button btnClearTrack;

    // 回到当前位置按钮
    private Button btnCenterMe;

    // 围栏半径滑动条
    private SeekBar seekFenceRadius;

    // 顶部信息区是否展开
    private boolean isInfoExpanded = true;

    // 地图蓝点定位回调监听器
    private OnLocationChangedListener mListener;
    // 高德定位客户端
    private AMapLocationClient aMapLocationClient;
    // 定位参数配置
    private AMapLocationClientOption aMapLocationClientOption;

    // 系统 GNSS 状态服务，用于读取原始卫星状态
    private LocationManager locationManager;
    // GNSS 卫星状态回调
    private GnssStatus.Callback gnssStatusCallback;
    // 是否已经注册 GNSS 监听，避免重复注册
    private boolean isGnssStatusRegistered = false;
    // 当前可见卫星数
    private int gnssVisibleCount = 0;
    // 当前参与定位解算的卫星数
    private int gnssUsedCount = 0;
    // 当前平均载噪比 C/N0，单位 dB-Hz
    private double gnssAvgCn0 = 0.0;
    // 当前最大载噪比 C/N0，单位 dB-Hz
    private double gnssMaxCn0 = 0.0;
    // 当前平均卫星高度角，单位度
    private double gnssAvgElevation = 0.0;
    // 估算 GDOP、PDOP、HDOP、VDOP
    private double gnssGdop = Double.NaN;
    private double gnssPdop = Double.NaN;
    private double gnssHdop = Double.NaN;
    private double gnssVdop = Double.NaN;
    // 各星座卫星数量统计
    private int gpsCount = 0;
    private int beidouCount = 0;
    private int glonassCount = 0;
    private int galileoCount = 0;
    // GNSS 综合质量等级
    private String gnssQualityLevel = "等待卫星数据";

    // 系统传感器管理器，用于读取加速度计和磁力计
    private SensorManager sensorManager;
    // 加速度计传感器
    private Sensor accelerometerSensor;
    // 磁力计传感器
    private Sensor magneticSensor;
    // 加速度计最近一次读数
    private final float[] accelerometerValues = new float[3];
    // 磁力计最近一次读数
    private final float[] magneticValues = new float[3];
    // 是否已经获得加速度计读数
    private boolean hasAccelerometerValue = false;
    // 是否已经获得磁力计读数
    private boolean hasMagneticValue = false;
    // 由惯性/磁传感器估计的手机航向角，单位度
    private float sensorHeadingDeg = Float.NaN;
    // 当前 GNSS 速度，单位 m/s
    private float currentGnssSpeed = 0f;
    // 当前 GNSS 航向角，单位度
    private float currentGnssBearing = Float.NaN;
    // 当前水平定位精度，单位 m，用于顶部摘要卡片
    private float currentHorizontalAccuracy = -1f;
    // 当前精度等级，用于顶部摘要卡片
    private String currentAccuracyLevel = "等待定位";
    // 上一次用于异常检测的位置
    private LatLng lastAnomalyLatLng;
    // 上一次用于异常检测的时间
    private long lastAnomalyTimeMillis = 0L;
    // 最近两次定位间的位置跳变量，单位 m
    private double lastJumpDistance = 0.0;
    // 最近两次定位间推算的移动速度，单位 m/s
    private double lastJumpSpeed = 0.0;
    // 最近一次异常检测结论
    private String anomalyLevel = "待检测";
    // 最近一次异常检测原因
    private String anomalyReason = "等待连续定位数据";

    // 是否是首次定位
    private boolean isFirstLocate = true;
    // 当前经纬度
    private LatLng currentLatLng;
    // 当前地址
    private String currentAddress = "未知地址";
    // 当前城市
    private String currentCity = "";

    // 围栏模式是否开启
    private boolean isFenceModeEnabled = false;
    // 围栏中心点
    private LatLng fenceCenter;
    // 围栏圆对象
    private Circle fenceCircle;
    // 围栏中心 Marker
    private Marker fenceMarker;
    // 围栏半径，默认 100 米
    private float fenceRadius = 100f;
    // 上一次是否在围栏内，用于判断进入和离开
    private Boolean lastInsideState = null;

    // 是否正在记录轨迹
    private boolean isTracking = false;
    // 轨迹点集合
    private final ArrayList<LatLng> trackPoints = new ArrayList<>();
    // 轨迹折线对象
    private Polyline trackPolyline;
    // 轨迹累计长度
    private float trackDistance = 0f;

    // 路线搜索对象
    private RouteSearch routeSearch;
    // 目的地 Marker
    private Marker destinationMarker;
    // 目的地坐标
    private LatLng routeDestination;
    // 目的地名称
    private String routeDestinationName = "";
    // 路线折线
    private Polyline routePolyline;

    // 搜索结果集合
    private final ArrayList<PoiItem> searchPoiList = new ArrayList<>();
    // 搜索结果适配器
    private SearchResultAdapter searchAdapter;

    // 拍照前暂存的拍照点位置
    private LatLng pendingPhotoLatLng;
    // 拍照前暂存的时间
    private String pendingPhotoTime;
    // 拍照前暂存的地址
    private String pendingPhotoAddress;
    // 用 Marker 的 id 关联 Bitmap
    private final HashMap<String, Bitmap> photoBitmapMap = new HashMap<>();
    // 用 Marker 的 id 关联拍照说明信息
    private final HashMap<String, String> photoInfoMap = new HashMap<>();
    // 所有拍照点 Marker 的集合，便于统一清除
    private final ArrayList<Marker> photoMarkers = new ArrayList<>();
    // 时间格式化器
    private final SimpleDateFormat timeFormat =
            new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());

    /**
     * Activity 创建入口
     * 完成布局加载、地图初始化、事件绑定、权限申请等工作
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // 隐藏默认标题栏，让地图界面更完整
        if (getSupportActionBar() != null) {
            getSupportActionBar().hide();
        }

        // 高德地图与定位 SDK 的隐私合规初始化
        MapsInitializer.updatePrivacyShow(this, true, true);
        MapsInitializer.updatePrivacyAgree(this, true);
        AMapLocationClient.updatePrivacyShow(this, true, true);
        AMapLocationClient.updatePrivacyAgree(this, true);

        // 加载主布局文件
        setContentView(R.layout.activity_main);

        // 绑定界面控件
        initViews();

        // 初始化 MapView 生命周期
        mapView.onCreate(savedInstanceState);

        // 获取 AMap 对象
        if (aMap == null) {
            aMap = mapView.getMap();
        }

        try {
            // 创建路线搜索对象
            routeSearch = new RouteSearch(this);
            // 设置路线回调监听器
            routeSearch.setRouteSearchListener(this);
        } catch (AMapException e) {
            e.printStackTrace();
        }

        // 初始化地图样式与地图监听
        initMap();
        // 初始化按钮和控件事件
        initEvents();
        // 初始化惯性传感器监听对象，用于 GNSS + 惯性辅助导航展示
        initSensorFusion();
        // 检查并申请定位权限
        requestLocationPermissionIfNeeded();

        // 初始化顶部状态文字
        updateFenceStatusNoFence();
        updateTrackStatus();
        updateGnssQualityText();
        updateAccuracyEvalText(null);
        updateErrorAnalysisText(null);
        updateAnomalyDetectText();
        updateSensorFusionText();
        updateQuickStatusCards(null);
        refreshFeaturePanel();
        tvRouteStatus.setText("路线：未规划");
    }

    /**
     * 绑定布局中的所有控件
     */
    private void initViews() {
        mapView = findViewById(R.id.mapView);

        etKeyword = findViewById(R.id.etKeyword);
        lvSearchResults = findViewById(R.id.lvSearchResults);

        tvAddress = findViewById(R.id.tvAddress);
        tvCoord = findViewById(R.id.tvCoord);
        tvCoordConverted = findViewById(R.id.tvCoordConverted);
        tvGnssQuality = findViewById(R.id.tvGnssQuality);
        tvAccuracyEval = findViewById(R.id.tvAccuracyEval);
        tvErrorAnalysis = findViewById(R.id.tvErrorAnalysis);
        tvAnomalyDetect = findViewById(R.id.tvAnomalyDetect);
        tvSensorFusion = findViewById(R.id.tvSensorFusion);
        tvQuickGnss = findViewById(R.id.tvQuickGnss);
        tvQuickAccuracy = findViewById(R.id.tvQuickAccuracy);
        tvQuickAnomaly = findViewById(R.id.tvQuickAnomaly);
        tvFeatureTitle = findViewById(R.id.tvFeatureTitle);
        tvFeatureContent = findViewById(R.id.tvFeatureContent);
        tvFenceStatus = findViewById(R.id.tvFenceStatus);
        tvTrackStatus = findViewById(R.id.tvTrackStatus);
        tvRouteStatus = findViewById(R.id.tvRouteStatus);
        tvFenceRadius = findViewById(R.id.tvFenceRadius);
        tvSelectedDestination = findViewById(R.id.tvSelectedDestination);

        layoutSearchExtras = findViewById(R.id.layoutSearchExtras);
        layoutFeatureModuleContent = findViewById(R.id.layoutFeatureModuleContent);
        layoutRouteActions = findViewById(R.id.layoutRouteActions);
        layoutFenceRadius = findViewById(R.id.layoutFenceRadius);
        cardFenceRadius = findViewById(R.id.cardFenceRadius);

        btnToggleInfo = findViewById(R.id.btnToggleInfo);
        btnToggleFeatureModule = findViewById(R.id.btnToggleFeatureModule);
        btnSearch = findViewById(R.id.btnSearch);
        btnWalkRoute = findViewById(R.id.btnWalkRoute);
        btnDriveRoute = findViewById(R.id.btnDriveRoute);
        btnClearRoute = findViewById(R.id.btnClearRoute);

        btnFenceMode = findViewById(R.id.btnFenceMode);
        btnClearFence = findViewById(R.id.btnClearFence);

        btnTakePhoto = findViewById(R.id.btnTakePhoto);
        btnClearPhotos = findViewById(R.id.btnClearPhotos);

        btnTrack = findViewById(R.id.btnTrack);
        btnClearTrack = findViewById(R.id.btnClearTrack);

        btnShowCoord = findViewById(R.id.btnShowCoord);
        btnShowGnss = findViewById(R.id.btnShowGnss);
        btnShowAccuracy = findViewById(R.id.btnShowAccuracy);
        btnShowError = findViewById(R.id.btnShowError);
        btnShowAnomaly = findViewById(R.id.btnShowAnomaly);
        btnShowSensor = findViewById(R.id.btnShowSensor);

        btnCenterMe = findViewById(R.id.btnCenterMe);

        seekFenceRadius = findViewById(R.id.seekFenceRadius);

        // 创建并设置搜索结果适配器
        searchAdapter = new SearchResultAdapter();
        lvSearchResults.setAdapter(searchAdapter);
    }

    /**
     * 初始化地图外观与地图事件监听
     */
    private void initMap() {
        // 开启比例尺
        aMap.getUiSettings().setScaleControlsEnabled(true);
        // 关闭默认定位按钮，使用自定义按钮
        aMap.getUiSettings().setMyLocationButtonEnabled(false);
        // 关闭默认缩放按钮
        aMap.getUiSettings().setZoomControlsEnabled(false);

        // 地图长按监听，用于设置围栏中心
        aMap.setOnMapLongClickListener(this);
        // Marker 点击监听，用于拍照点点击查看
        aMap.setOnMarkerClickListener(this);

        // 自定义定位蓝点样式
        MyLocationStyle myLocationStyle = new MyLocationStyle();
        // 只旋转蓝点，不强制地图始终居中
        myLocationStyle.myLocationType(MyLocationStyle.LOCATION_TYPE_LOCATION_ROTATE_NO_CENTER);
        // 定位刷新间隔 2 秒
        myLocationStyle.interval(2000);
        // 蓝圈填充颜色
        myLocationStyle.radiusFillColor(0x180EA5E9);
        // 蓝圈边框颜色
        myLocationStyle.strokeColor(0x440EA5E9);
        // 蓝圈边框宽度
        myLocationStyle.strokeWidth(1f);
        // 应用蓝点样式
        aMap.setMyLocationStyle(myLocationStyle);
    }

    /**
     * 初始化所有控件事件
     */
    private void initEvents() {
        // SeekBar 最大值 450，对应实际半径 50 到 500 米
        seekFenceRadius.setMax(450);
        // 默认进度 50，对应半径 100 米
        seekFenceRadius.setProgress(50);
        tvFenceRadius.setText("围栏半径：100m");

        // 围栏半径滑动监听
        seekFenceRadius.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                // 实际半径 = progress + 50
                fenceRadius = progress + 50;
                tvFenceRadius.setText("围栏半径：" + (int) fenceRadius + "m");

                // 如果地图上已经有围栏圆，则同步更新半径
                if (fenceCircle != null) {
                    fenceCircle.setRadius(fenceRadius);
                }

                // 如果当前位置和围栏中心都存在，则实时重新判断围栏状态
                if (currentLatLng != null && fenceCenter != null) {
                    checkFenceState(currentLatLng, false);
                }
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        // 展开收起顶部信息区
        btnToggleInfo.setOnClickListener(v -> toggleInfoPanel());

        // 展开收起功能模块详情区，默认只保留摘要卡片，降低顶部展示栏高度
        btnToggleFeatureModule.setOnClickListener(v -> toggleFeatureModule());

        // 搜索地点
        btnSearch.setOnClickListener(v -> searchLocation());

        // 点击某条搜索结果后选中目的地
        lvSearchResults.setOnItemClickListener((parent, view, position, id) -> selectSearchResult(position));

        // 步行路线规划
        btnWalkRoute.setOnClickListener(v -> planWalkRoute());
        // 驾车路线规划
        btnDriveRoute.setOnClickListener(v -> planDriveRoute());
        // 清除路线
        btnClearRoute.setOnClickListener(v -> clearRoute());

        // 任务二功能详情切换按钮：默认只展示一个功能详情，避免顶部出现大段文字
        btnShowCoord.setOnClickListener(v -> showFeaturePanel("coord"));
        btnShowGnss.setOnClickListener(v -> showFeaturePanel("gnss"));
        btnShowAccuracy.setOnClickListener(v -> showFeaturePanel("accuracy"));
        btnShowError.setOnClickListener(v -> showFeaturePanel("error"));
        btnShowAnomaly.setOnClickListener(v -> showFeaturePanel("anomaly"));
        btnShowSensor.setOnClickListener(v -> showFeaturePanel("sensor"));
        showFeaturePanel("gnss");

        // 围栏模式开关
        btnFenceMode.setOnClickListener(v -> toggleFenceMode());
        // 清除围栏
        btnClearFence.setOnClickListener(v -> clearFence());

        // 拍照定位
        btnTakePhoto.setOnClickListener(v -> takePhotoWithLocation());
        // 清除拍照点
        btnClearPhotos.setOnClickListener(v -> clearPhotoMarkers());

        // 轨迹记录开关
        btnTrack.setOnClickListener(v -> toggleTrackRecording());
        // 清除轨迹
        btnClearTrack.setOnClickListener(v -> clearTrack());

        // 回到当前位置
        btnCenterMe.setOnClickListener(v -> {
            if (currentLatLng != null) {
                // 有定位时把地图移动到当前位置
                aMap.animateCamera(CameraUpdateFactory.newLatLngZoom(currentLatLng, 18f));
            } else {
                // 没拿到定位时给提示
                Toast.makeText(this, "当前位置未获取到", Toast.LENGTH_SHORT).show();
            }
        });
    }

    /**
     * 切换顶部信息区的展开和收起状态
     */
    private void toggleInfoPanel() {
        isInfoExpanded = !isInfoExpanded;
        layoutSearchExtras.setVisibility(isInfoExpanded ? View.VISIBLE : View.GONE);
        btnToggleInfo.setText(isInfoExpanded ? "收起" : "展开");
    }

    /**
     * 展开或收起功能模块区。
     * 默认状态下只保留三项摘要卡片，点击展开后再显示具体功能标签和详情卡片。
     */
    private void toggleFeatureModule() {
        isFeatureModuleExpanded = !isFeatureModuleExpanded;
        layoutFeatureModuleContent.setVisibility(isFeatureModuleExpanded ? View.VISIBLE : View.GONE);
        btnToggleFeatureModule.setText(isFeatureModuleExpanded ? "收起" : "展开");
    }

    // ==================== 任务二功能面板显示控制 ====================

    /**
     * 切换任务二详情卡片展示内容。顶部只保留摘要，具体功能通过标签按钮按需展开。
     */
    private void showFeaturePanel(String featureName) {
        if (featureName != null && !featureName.trim().isEmpty()) {
            activeFeaturePanel = featureName;
        }
        updateFeatureButtonStyle();
        refreshFeaturePanel();
    }

    /**
     * 根据当前选择的功能，把对应文字放入统一详情卡片。
     */
    private void refreshFeaturePanel() {
        if (tvFeatureTitle == null || tvFeatureContent == null) {
            return;
        }

        String title;
        String content;
        switch (activeFeaturePanel) {
            case "coord":
                title = "坐标转换";
                content = getTextFromView(tvCoordConverted, "坐标转换：等待定位数据");
                break;
            case "accuracy":
                title = "GNSS定位精度评价";
                content = getTextFromView(tvAccuracyEval, "定位精度评价：等待定位数据");
                break;
            case "error":
                title = "GNSS导航误差源分析";
                content = getTextFromView(tvErrorAnalysis, "误差源分析：等待定位数据");
                break;
            case "anomaly":
                title = "GNSS欺骗与异常检测初筛";
                content = getTextFromView(tvAnomalyDetect, "异常/欺骗初筛：待检测");
                break;
            case "sensor":
                title = "GNSS+惯性传感器组合导航";
                content = getTextFromView(tvSensorFusion, "组合导航：等待传感器数据");
                break;
            case "gnss":
            default:
                title = "GNSS定位质量评估";
                content = getTextFromView(tvGnssQuality, "GNSS质量：等待卫星数据");
                break;
        }

        tvFeatureTitle.setText(title);
        tvFeatureContent.setText(content);
    }

    /**
     * 让当前选中的功能标签更醒目，其余标签保持浅色。
     */
    private void updateFeatureButtonStyle() {
        setFeatureButtonSelected(btnShowGnss, "gnss".equals(activeFeaturePanel));
        setFeatureButtonSelected(btnShowAccuracy, "accuracy".equals(activeFeaturePanel));
        setFeatureButtonSelected(btnShowCoord, "coord".equals(activeFeaturePanel));
        setFeatureButtonSelected(btnShowError, "error".equals(activeFeaturePanel));
        setFeatureButtonSelected(btnShowAnomaly, "anomaly".equals(activeFeaturePanel));
        setFeatureButtonSelected(btnShowSensor, "sensor".equals(activeFeaturePanel));
    }

    /**
     * 设置功能标签按钮的选中/未选中样式。
     */
    private void setFeatureButtonSelected(Button button, boolean selected) {
        if (button == null) {
            return;
        }
        button.setTextColor(selected ? 0xFFFFFFFF : 0xFF334155);
        button.setBackgroundTintList(ColorStateList.valueOf(selected ? 0xFF475569 : 0xFFE2E8F0));
    }

    /**
     * 安全读取隐藏 TextView 中的功能结果。
     */
    private String getTextFromView(TextView textView, String defaultText) {
        if (textView == null || textView.getText() == null || textView.getText().toString().trim().isEmpty()) {
            return defaultText;
        }
        return textView.getText().toString();
    }

    /**
     * 刷新顶部三个摘要卡片，只显示最关键结论，避免主界面信息过载。
     */
    private void updateQuickStatusCards(AMapLocation location) {
        if (location != null) {
            currentHorizontalAccuracy = location.getAccuracy();
            currentAccuracyLevel = evaluateAccuracyLevel(currentHorizontalAccuracy);
        }

        if (tvQuickGnss != null) {
            if (gnssVisibleCount == 0) {
                tvQuickGnss.setText("等待卫星");
                tvQuickGnss.setTextColor(0xFF64748B);
            } else {
                tvQuickGnss.setText(String.format(
                        Locale.getDefault(),
                        "%s %d/%d颗",
                        gnssQualityLevel,
                        gnssUsedCount,
                        gnssVisibleCount
                ));
                tvQuickGnss.setTextColor(getQualityColor(gnssQualityLevel));
            }
        }

        if (tvQuickAccuracy != null) {
            if (currentHorizontalAccuracy < 0f) {
                tvQuickAccuracy.setText("等待定位");
                tvQuickAccuracy.setTextColor(0xFF64748B);
            } else {
                tvQuickAccuracy.setText(String.format(
                        Locale.getDefault(),
                        "%s %.1fm",
                        currentAccuracyLevel,
                        currentHorizontalAccuracy
                ));
                tvQuickAccuracy.setTextColor(getAccuracyColor(currentHorizontalAccuracy));
            }
        }

        if (tvQuickAnomaly != null) {
            tvQuickAnomaly.setText(anomalyLevel == null ? "待检测" : anomalyLevel);
            tvQuickAnomaly.setTextColor(getAnomalyColor(anomalyLevel));
        }
    }

    /**
     * 根据 GNSS 质量等级设置摘要文字颜色。
     */
    private int getQualityColor(String level) {
        if ("优".equals(level) || "良".equals(level)) {
            return 0xFF166534;
        }
        if ("中".equals(level)) {
            return 0xFF92400E;
        }
        if ("差".equals(level)) {
            return 0xFFB45309;
        }
        return 0xFF64748B;
    }

    /**
     * 根据系统水平精度设置摘要文字颜色。
     */
    private int getAccuracyColor(float accuracy) {
        if (accuracy <= 15f) {
            return 0xFF166534;
        }
        if (accuracy <= 30f) {
            return 0xFF92400E;
        }
        return 0xFFB45309;
    }

    /**
     * 根据异常检测等级设置摘要文字颜色。
     */
    private int getAnomalyColor(String level) {
        if ("正常".equals(level)) {
            return 0xFF166534;
        }
        if ("轻微异常".equals(level)) {
            return 0xFF92400E;
        }
        if ("疑似异常".equals(level)) {
            return 0xFFB91C1C;
        }
        return 0xFF64748B;
    }

    /**
     * 检查是否已有定位权限，没有则申请
     */
    private void requestLocationPermissionIfNeeded() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
                == PackageManager.PERMISSION_GRANTED) {
            enableLocation();
        } else {
            ActivityCompat.requestPermissions(
                    this,
                    new String[]{
                            Manifest.permission.ACCESS_FINE_LOCATION,
                            Manifest.permission.ACCESS_COARSE_LOCATION
                    },
                    REQUEST_LOCATION_PERMISSION
            );
        }
    }

    /**
     * 启用地图定位
     */
    private void enableLocation() {
        aMap.setLocationSource(this);
        aMap.setMyLocationEnabled(true);
        // 同步启动 GNSS 原始卫星状态监听，用于完成任务二中的定位质量评估
        startGnssStatusMonitor();
    }

    /**
     * 地图需要定位时会调用这里
     * 初始化定位客户端并启动定位
     */
    @Override
    public void activate(OnLocationChangedListener onLocationChangedListener) {
        mListener = onLocationChangedListener;

        if (aMapLocationClient == null) {
            try {
                aMapLocationClient = new AMapLocationClient(getApplicationContext());
            } catch (Exception e) {
                e.printStackTrace();
                return;
            }

            aMapLocationClientOption = new AMapLocationClientOption();
            aMapLocationClient.setLocationListener(this);

            // 使用高精度定位模式
            aMapLocationClientOption.setLocationMode(
                    AMapLocationClientOption.AMapLocationMode.Hight_Accuracy
            );
            // 需要返回地址信息
            aMapLocationClientOption.setNeedAddress(true);
            // 持续定位
            aMapLocationClientOption.setOnceLocation(false);
            // 定位间隔 2 秒
            aMapLocationClientOption.setInterval(2000);

            aMapLocationClient.setLocationOption(aMapLocationClientOption);
        }

        if (aMapLocationClient != null) {
            aMapLocationClient.startLocation();
        }
    }

    /**
     * 地图不再需要定位时调用
     */
    @Override
    public void deactivate() {
        mListener = null;

        if (aMapLocationClient != null) {
            aMapLocationClient.stopLocation();
            aMapLocationClient.onDestroy();
            aMapLocationClient = null;
        }
        stopGnssStatusMonitor();
    }

    /**
     * 定位结果回调
     * 每次定位刷新都会进入这里
     */
    @Override
    public void onLocationChanged(AMapLocation aMapLocation) {
        if (mListener != null && aMapLocation != null) {
            // errorCode 为 0 代表定位成功
            if (aMapLocation.getErrorCode() == 0) {
                // 把定位结果传给地图蓝点层
                mListener.onLocationChanged(aMapLocation);

                // 更新当前位置
                currentLatLng = new LatLng(aMapLocation.getLatitude(), aMapLocation.getLongitude());
                // 更新地址
                currentAddress = aMapLocation.getAddress() == null ? "未知地址" : aMapLocation.getAddress();
                // 更新城市
                currentCity = aMapLocation.getCity() == null ? "" : aMapLocation.getCity();

                // 刷新顶部定位信息
                updateLocationInfo(aMapLocation);
                // 刷新定位精度评价、误差源分析、异常检测和组合导航状态
                updateExtendedGnssFunctions(aMapLocation);

                // 首次定位成功后自动移动到当前位置
                if (isFirstLocate && currentLatLng != null) {
                    aMap.animateCamera(CameraUpdateFactory.newLatLngZoom(currentLatLng, 17f));
                    isFirstLocate = false;
                }

                // 每次定位更新都重新判断围栏状态
                checkFenceState(currentLatLng, true);

                // 如果正在记录轨迹，则加入新点
                if (isTracking) {
                    addTrackPoint(currentLatLng);
                }
            }
        }
    }

    /**
     * 更新地址、经纬度、精度和坐标转换结果显示
     */
    private void updateLocationInfo(AMapLocation aMapLocation) {
        double gcjLat = aMapLocation.getLatitude();
        double gcjLon = aMapLocation.getLongitude();
        float accuracy = aMapLocation.getAccuracy();

        tvAddress.setText("地址：" + currentAddress);
        tvCoord.setText(String.format(
                Locale.getDefault(),
                "GCJ-02：纬度 %.6f  经度 %.6f  精度 %.1fm | 精度等级：%s",
                gcjLat,
                gcjLon,
                accuracy,
                evaluateAccuracyLevel(accuracy)
        ));

        updateCoordinateConversionText(gcjLat, gcjLon);
    }

    // ==================== 坐标转换 ====================

    /**
     * 根据高德地图返回的 GCJ-02 坐标，换算 WGS84 和 BD-09 坐标并显示
     */
    private void updateCoordinateConversionText(double gcjLat, double gcjLon) {
        double[] wgs84 = gcj02ToWgs84(gcjLat, gcjLon);
        double[] bd09 = gcj02ToBd09(gcjLat, gcjLon);

        tvCoordConverted.setText(String.format(
                Locale.getDefault(),
                "坐标转换：WGS84[%.6f, %.6f]  BD-09[%.6f, %.6f]",
                wgs84[0],
                wgs84[1],
                bd09[0],
                bd09[1]
        ));
        if ("coord".equals(activeFeaturePanel)) {
            refreshFeaturePanel();
        }
    }

    /**
     * 将 GCJ-02 坐标近似反算为 WGS84 坐标
     */
    private double[] gcj02ToWgs84(double lat, double lon) {
        if (outOfChina(lat, lon)) {
            return new double[]{lat, lon};
        }

        double[] delta = transformLatLon(lat, lon);
        double dLat = delta[0];
        double dLon = delta[1];
        double mgLat = lat + dLat;
        double mgLon = lon + dLon;

        return new double[]{lat * 2 - mgLat, lon * 2 - mgLon};
    }

    /**
     * 将 GCJ-02 坐标转换为百度地图常用的 BD-09 坐标
     */
    private double[] gcj02ToBd09(double lat, double lon) {
        double x = lon;
        double y = lat;
        double z = Math.sqrt(x * x + y * y) + 0.00002 * Math.sin(y * Math.PI * 3000.0 / 180.0);
        double theta = Math.atan2(y, x) + 0.000003 * Math.cos(x * Math.PI * 3000.0 / 180.0);
        double bdLon = z * Math.cos(theta) + 0.0065;
        double bdLat = z * Math.sin(theta) + 0.006;
        return new double[]{bdLat, bdLon};
    }

    /**
     * GCJ-02 与 WGS84 之间的经纬度偏移计算
     */
    private double[] transformLatLon(double lat, double lon) {
        double a = 6378245.0;
        double ee = 0.00669342162296594323;
        double dLat = transformLat(lon - 105.0, lat - 35.0);
        double dLon = transformLon(lon - 105.0, lat - 35.0);
        double radLat = lat / 180.0 * Math.PI;
        double magic = Math.sin(radLat);
        magic = 1 - ee * magic * magic;
        double sqrtMagic = Math.sqrt(magic);
        dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * Math.PI);
        dLon = (dLon * 180.0) / (a / sqrtMagic * Math.cos(radLat) * Math.PI);
        return new double[]{dLat, dLon};
    }

    /**
     * 纬度方向偏移函数
     */
    private double transformLat(double x, double y) {
        double ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y
                + 0.1 * x * y + 0.2 * Math.sqrt(Math.abs(x));
        ret += (20.0 * Math.sin(6.0 * x * Math.PI)
                + 20.0 * Math.sin(2.0 * x * Math.PI)) * 2.0 / 3.0;
        ret += (20.0 * Math.sin(y * Math.PI)
                + 40.0 * Math.sin(y / 3.0 * Math.PI)) * 2.0 / 3.0;
        ret += (160.0 * Math.sin(y / 12.0 * Math.PI)
                + 320 * Math.sin(y * Math.PI / 30.0)) * 2.0 / 3.0;
        return ret;
    }

    /**
     * 经度方向偏移函数
     */
    private double transformLon(double x, double y) {
        double ret = 300.0 + x + 2.0 * y + 0.1 * x * x
                + 0.1 * x * y + 0.1 * Math.sqrt(Math.abs(x));
        ret += (20.0 * Math.sin(6.0 * x * Math.PI)
                + 20.0 * Math.sin(2.0 * x * Math.PI)) * 2.0 / 3.0;
        ret += (20.0 * Math.sin(x * Math.PI)
                + 40.0 * Math.sin(x / 3.0 * Math.PI)) * 2.0 / 3.0;
        ret += (150.0 * Math.sin(x / 12.0 * Math.PI)
                + 300.0 * Math.sin(x / 30.0 * Math.PI)) * 2.0 / 3.0;
        return ret;
    }

    /**
     * 判断坐标是否位于中国大陆坐标偏移适用范围外
     */
    private boolean outOfChina(double lat, double lon) {
        return lon < 72.004 || lon > 137.8347 || lat < 0.8293 || lat > 55.8271;
    }

    /**
     * 根据系统定位精度给出简明等级，便于课堂展示 GNSS 定位精度评价
     */
    private String evaluateAccuracyLevel(float accuracy) {
        if (accuracy <= 5f) {
            return "优";
        } else if (accuracy <= 15f) {
            return "良";
        } else if (accuracy <= 30f) {
            return "中";
        } else {
            return "差";
        }
    }

    // ==================== GNSS 定位质量评估 ====================

    /**
     * 启动 GNSS 卫星状态监听，读取可见卫星数、参与定位卫星数、C/N0 和卫星几何信息
     */
    private void startGnssStatusMonitor() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
                != PackageManager.PERMISSION_GRANTED) {
            return;
        }

        if (locationManager == null) {
            locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
        }

        if (locationManager == null || isGnssStatusRegistered) {
            return;
        }

        if (gnssStatusCallback == null) {
            gnssStatusCallback = new GnssStatus.Callback() {
                @Override
                public void onSatelliteStatusChanged(@NonNull GnssStatus status) {
                    updateGnssStatus(status);
                }
            };
        }

        try {
            isGnssStatusRegistered = locationManager.registerGnssStatusCallback(gnssStatusCallback);
            updateGnssQualityText();
        } catch (SecurityException e) {
            isGnssStatusRegistered = false;
            e.printStackTrace();
        }
    }

    /**
     * 停止 GNSS 卫星状态监听，避免 Activity 销毁后继续回调
     */
    private void stopGnssStatusMonitor() {
        if (locationManager != null && gnssStatusCallback != null && isGnssStatusRegistered) {
            locationManager.unregisterGnssStatusCallback(gnssStatusCallback);
            isGnssStatusRegistered = false;
        }
    }

    /**
     * 统计 GNSS 卫星状态，并根据卫星几何分布估算 DOP
     */
    private void updateGnssStatus(GnssStatus status) {
        int visible = status.getSatelliteCount();
        int used = 0;
        int cn0Count = 0;
        int elevationCount = 0;
        double cn0Sum = 0.0;
        double cn0Max = 0.0;
        double elevationSum = 0.0;

        int gps = 0;
        int beidou = 0;
        int glonass = 0;
        int galileo = 0;

        ArrayList<double[]> usedRows = new ArrayList<>();
        ArrayList<double[]> allRows = new ArrayList<>();

        for (int i = 0; i < visible; i++) {
            boolean usedInFix = status.usedInFix(i);
            if (usedInFix) {
                used++;
            }

            double cn0 = status.getCn0DbHz(i);
            if (cn0 > 0) {
                cn0Sum += cn0;
                cn0Max = Math.max(cn0Max, cn0);
                cn0Count++;
            }

            double elevation = status.getElevationDegrees(i);
            double azimuth = status.getAzimuthDegrees(i);
            elevationSum += elevation;
            elevationCount++;

            double[] dopRow = buildDopRow(elevation, azimuth);
            allRows.add(dopRow);
            if (usedInFix) {
                usedRows.add(dopRow);
            }

            switch (status.getConstellationType(i)) {
                case GnssStatus.CONSTELLATION_GPS:
                    gps++;
                    break;
                case GnssStatus.CONSTELLATION_BEIDOU:
                    beidou++;
                    break;
                case GnssStatus.CONSTELLATION_GLONASS:
                    glonass++;
                    break;
                case GnssStatus.CONSTELLATION_GALILEO:
                    galileo++;
                    break;
                default:
                    break;
            }
        }

        gnssVisibleCount = visible;
        gnssUsedCount = used;
        gnssAvgCn0 = cn0Count == 0 ? 0.0 : cn0Sum / cn0Count;
        gnssMaxCn0 = cn0Max;
        gnssAvgElevation = elevationCount == 0 ? 0.0 : elevationSum / elevationCount;
        gpsCount = gps;
        beidouCount = beidou;
        glonassCount = glonass;
        galileoCount = galileo;

        // DOP 需要至少 4 颗卫星。优先使用参与定位的卫星；不足 4 颗时退回全部可见卫星估算。
        ArrayList<double[]> dopRows = usedRows.size() >= 4 ? usedRows : allRows;
        calculateDop(dopRows);

        gnssQualityLevel = evaluateGnssQualityLevel();

        runOnUiThread(this::updateGnssQualityText);
    }

    /**
     * 根据卫星高度角、方位角构造 DOP 计算矩阵的一行
     */
    private double[] buildDopRow(double elevationDeg, double azimuthDeg) {
        double elevation = Math.toRadians(elevationDeg);
        double azimuth = Math.toRadians(azimuthDeg);
        double cosEl = Math.cos(elevation);

        // 行向量包含东、北、天三个方向分量和接收机钟差项
        return new double[]{
                cosEl * Math.sin(azimuth),
                cosEl * Math.cos(azimuth),
                Math.sin(elevation),
                1.0
        };
    }

    /**
     * 由卫星几何矩阵估算 GDOP、PDOP、HDOP、VDOP
     */
    private void calculateDop(ArrayList<double[]> rows) {
        if (rows.size() < 4) {
            gnssGdop = Double.NaN;
            gnssPdop = Double.NaN;
            gnssHdop = Double.NaN;
            gnssVdop = Double.NaN;
            return;
        }

        double[][] normal = new double[4][4];
        for (double[] row : rows) {
            for (int i = 0; i < 4; i++) {
                for (int j = 0; j < 4; j++) {
                    normal[i][j] += row[i] * row[j];
                }
            }
        }

        double[][] inv = invert4x4(normal);
        if (inv == null) {
            gnssGdop = Double.NaN;
            gnssPdop = Double.NaN;
            gnssHdop = Double.NaN;
            gnssVdop = Double.NaN;
            return;
        }

        gnssGdop = safeSqrt(inv[0][0] + inv[1][1] + inv[2][2] + inv[3][3]);
        gnssPdop = safeSqrt(inv[0][0] + inv[1][1] + inv[2][2]);
        gnssHdop = safeSqrt(inv[0][0] + inv[1][1]);
        gnssVdop = safeSqrt(inv[2][2]);
    }

    /**
     * 4 阶矩阵求逆，采用高斯-约旦消元，避免引入额外数学库
     */
    private double[][] invert4x4(double[][] matrix) {
        int n = 4;
        double[][] aug = new double[n][n * 2];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                aug[i][j] = matrix[i][j];
            }
            aug[i][i + n] = 1.0;
        }

        for (int col = 0; col < n; col++) {
            int pivot = col;
            for (int row = col + 1; row < n; row++) {
                if (Math.abs(aug[row][col]) > Math.abs(aug[pivot][col])) {
                    pivot = row;
                }
            }

            if (Math.abs(aug[pivot][col]) < 1e-10) {
                return null;
            }

            if (pivot != col) {
                double[] temp = aug[col];
                aug[col] = aug[pivot];
                aug[pivot] = temp;
            }

            double pivotValue = aug[col][col];
            for (int j = 0; j < n * 2; j++) {
                aug[col][j] /= pivotValue;
            }

            for (int row = 0; row < n; row++) {
                if (row == col) {
                    continue;
                }
                double factor = aug[row][col];
                for (int j = 0; j < n * 2; j++) {
                    aug[row][j] -= factor * aug[col][j];
                }
            }
        }

        double[][] inv = new double[n][n];
        for (int i = 0; i < n; i++) {
            inv[i] = Arrays.copyOfRange(aug[i], n, n * 2);
        }
        return inv;
    }

    /**
     * 避免由于数值误差导致根号内出现很小的负数
     */
    private double safeSqrt(double value) {
        if (Double.isNaN(value) || value < -1e-8) {
            return Double.NaN;
        }
        return Math.sqrt(Math.max(0.0, value));
    }

    /**
     * 综合可见卫星数、参与定位卫星数、C/N0 和 PDOP 给出 GNSS 定位质量等级
     */
    private String evaluateGnssQualityLevel() {
        boolean pdopGood = Double.isNaN(gnssPdop) || gnssPdop <= 2.5;
        boolean pdopMiddle = Double.isNaN(gnssPdop) || gnssPdop <= 5.0;

        if (gnssUsedCount >= 8 && gnssAvgCn0 >= 35.0 && pdopGood) {
            return "优";
        } else if (gnssUsedCount >= 6 && gnssAvgCn0 >= 30.0 && pdopMiddle) {
            return "良";
        } else if (gnssUsedCount >= 4 && gnssAvgCn0 >= 20.0) {
            return "中";
        } else if (gnssVisibleCount > 0) {
            return "差";
        } else {
            return "等待卫星数据";
        }
    }

    /**
     * 刷新 GNSS 质量状态文字
     */
    private void updateGnssQualityText() {
        if (tvGnssQuality == null) {
            return;
        }

        if (gnssVisibleCount == 0) {
            tvGnssQuality.setText("GNSS质量：等待卫星数据");
            updateQuickStatusCards(null);
            if ("gnss".equals(activeFeaturePanel)) {
                refreshFeaturePanel();
            }
            return;
        }

        tvGnssQuality.setText(String.format(
                Locale.getDefault(),
                "GNSS质量：%s | 可见%d颗/参与%d颗 | 平均C/N0 %.1fdB-Hz | PDOP%s HDOP%s VDOP%s\n星座：GPS%d 北斗%d GLONASS%d Galileo%d | 平均高度角%.1f°",
                gnssQualityLevel,
                gnssVisibleCount,
                gnssUsedCount,
                gnssAvgCn0,
                formatDop(gnssPdop),
                formatDop(gnssHdop),
                formatDop(gnssVdop),
                gpsCount,
                beidouCount,
                glonassCount,
                galileoCount,
                gnssAvgElevation
        ));
        updateQuickStatusCards(null);
        if ("gnss".equals(activeFeaturePanel)) {
            refreshFeaturePanel();
        }
    }

    /**
     * DOP 显示格式化
     */
    private String formatDop(double value) {
        if (Double.isNaN(value) || Double.isInfinite(value)) {
            return "--";
        }
        return String.format(Locale.getDefault(), "%.1f", value);
    }


    // ==================== 定位精度评价、误差源分析、异常检测、组合导航 ====================

    /**
     * 初始化加速度计和磁力计，用于给出手机姿态航向，辅助 GNSS 航向判断
     */
    private void initSensorFusion() {
        sensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        if (sensorManager != null) {
            accelerometerSensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
            magneticSensor = sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
        }
        updateSensorFusionText();
    }

    /**
     * 页面显示时注册传感器监听
     */
    private void startSensorMonitor() {
        if (sensorManager == null) {
            return;
        }
        if (accelerometerSensor != null) {
            sensorManager.registerListener(this, accelerometerSensor, SensorManager.SENSOR_DELAY_UI);
        }
        if (magneticSensor != null) {
            sensorManager.registerListener(this, magneticSensor, SensorManager.SENSOR_DELAY_UI);
        }
    }

    /**
     * 页面暂停或销毁时停止传感器监听，避免资源占用
     */
    private void stopSensorMonitor() {
        if (sensorManager != null) {
            sensorManager.unregisterListener(this);
        }
    }

    /**
     * 传感器数据刷新回调，用加速度计和磁力计估计手机朝向
     */
    @Override
    public void onSensorChanged(SensorEvent event) {
        if (event == null || event.sensor == null) {
            return;
        }

        if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
            lowPass(event.values, accelerometerValues);
            hasAccelerometerValue = true;
        } else if (event.sensor.getType() == Sensor.TYPE_MAGNETIC_FIELD) {
            lowPass(event.values, magneticValues);
            hasMagneticValue = true;
        }

        if (hasAccelerometerValue && hasMagneticValue) {
            float[] rotationMatrix = new float[9];
            float[] orientation = new float[3];
            boolean success = SensorManager.getRotationMatrix(
                    rotationMatrix,
                    null,
                    accelerometerValues,
                    magneticValues
            );
            if (success) {
                SensorManager.getOrientation(rotationMatrix, orientation);
                float azimuth = (float) Math.toDegrees(orientation[0]);
                sensorHeadingDeg = normalizeAngle(azimuth);
                updateSensorFusionText();
            }
        }
    }

    /**
     * 传感器精度变化回调，当前仅保留接口实现
     */
    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        // 当前功能只用于课堂展示辅助航向，不单独处理传感器精度等级
    }

    /**
     * 对传感器数据做简单低通滤波，减少航向文字跳动
     */
    private void lowPass(float[] input, float[] output) {
        final float alpha = 0.15f;
        for (int i = 0; i < output.length && i < input.length; i++) {
            output[i] = output[i] + alpha * (input[i] - output[i]);
        }
    }

    /**
     * 定位成功后统一刷新新增的任务二扩展功能
     */
    private void updateExtendedGnssFunctions(AMapLocation location) {
        if (location == null) {
            return;
        }

        currentGnssSpeed = Math.max(0f, location.getSpeed());
        currentGnssBearing = normalizeAngle(location.getBearing());

        updateAccuracyEvalText(location);
        updateErrorAnalysisText(location);
        updateAnomalyState(location);
        updateAnomalyDetectText();
        updateSensorFusionText();
    }

    /**
     * 显示定位精度评价：系统水平精度、定位方式、速度、航向和使用建议
     */
    private void updateAccuracyEvalText(AMapLocation location) {
        if (tvAccuracyEval == null) {
            return;
        }
        if (location == null) {
            tvAccuracyEval.setText("定位精度评价：等待定位数据");
            updateQuickStatusCards(null);
            if ("accuracy".equals(activeFeaturePanel)) {
                refreshFeaturePanel();
            }
            return;
        }

        float accuracy = location.getAccuracy();
        String level = evaluateAccuracyLevel(accuracy);
        String typeName = getLocationTypeName(location.getLocationType());
        String suggestion;
        if (accuracy <= 5f) {
            suggestion = "可用于精细导航/轨迹记录";
        } else if (accuracy <= 15f) {
            suggestion = "可用于普通导航";
        } else if (accuracy <= 30f) {
            suggestion = "适合粗略定位";
        } else {
            suggestion = "建议移动到开阔区域";
        }

        tvAccuracyEval.setText(String.format(
                Locale.getDefault(),
                "定位精度评价：%s | 水平精度%.1fm | 定位方式%s | 速度%.1fm/s | 航向%.0f° | %s",
                level,
                accuracy,
                typeName,
                Math.max(0f, location.getSpeed()),
                normalizeAngle(location.getBearing()),
                suggestion
        ));
        updateQuickStatusCards(location);
        if ("accuracy".equals(activeFeaturePanel)) {
            refreshFeaturePanel();
        }
    }

    /**
     * 根据 GNSS 信号、卫星几何和定位方式推断可能的误差来源
     */
    private void updateErrorAnalysisText(AMapLocation location) {
        if (tvErrorAnalysis == null) {
            return;
        }
        if (location == null) {
            tvErrorAnalysis.setText("误差源分析：等待定位数据");
            if ("error".equals(activeFeaturePanel)) {
                refreshFeaturePanel();
            }
            return;
        }

        ArrayList<String> reasons = new ArrayList<>();
        float accuracy = location.getAccuracy();
        int locationType = location.getLocationType();

        if (accuracy > 30f) {
            reasons.add("水平精度较差");
        }
        if (gnssVisibleCount == 0) {
            reasons.add("暂未获取卫星状态，可能为网络/融合定位");
        } else {
            if (gnssUsedCount > 0 && gnssUsedCount < 4) {
                reasons.add("参与解算卫星不足");
            }
            if (gnssAvgCn0 > 0 && gnssAvgCn0 < 25.0) {
                reasons.add("C/N0偏低，疑似遮挡或信号弱");
            }
            if (!Double.isNaN(gnssPdop) && gnssPdop > 5.0) {
                reasons.add("PDOP偏大，卫星几何构型较差");
            }
            if (gnssAvgElevation > 0 && gnssAvgElevation < 25.0) {
                reasons.add("平均高度角低，易受多路径影响");
            }
        }
        if (locationType != 1) {
            reasons.add("定位方式非纯GPS，可能受WiFi/基站环境影响");
        }
        if (reasons.isEmpty()) {
            reasons.add("卫星信号和几何条件较正常");
        }

        tvErrorAnalysis.setText("误差源分析：" + joinReasons(reasons));
        if ("error".equals(activeFeaturePanel)) {
            refreshFeaturePanel();
        }
    }

    /**
     * 更新异常/欺骗初筛状态：位置跳变、速度异常、卫星状态与定位精度矛盾
     */
    private void updateAnomalyState(AMapLocation location) {
        LatLng now = new LatLng(location.getLatitude(), location.getLongitude());
        long nowTime = System.currentTimeMillis();
        float accuracy = location.getAccuracy();
        ArrayList<String> reasons = new ArrayList<>();

        if (lastAnomalyLatLng != null && lastAnomalyTimeMillis > 0L) {
            double dt = (nowTime - lastAnomalyTimeMillis) / 1000.0;
            if (dt > 0.2) {
                lastJumpDistance = AMapUtils.calculateLineDistance(lastAnomalyLatLng, now);
                lastJumpSpeed = lastJumpDistance / dt;

                if (lastJumpDistance > Math.max(50.0, accuracy * 3.0) && lastJumpSpeed > 35.0) {
                    reasons.add("短时间位置跳变明显");
                }
                if (lastJumpSpeed > 80.0 && location.getSpeed() < 15.0) {
                    reasons.add("坐标推算速度与系统速度不一致");
                }
            }
        }

        if (gnssVisibleCount > 0 && gnssUsedCount < 4 && accuracy <= 10f) {
            reasons.add("卫星不足但系统精度很高，需复核定位来源");
        }
        if (gnssAvgCn0 > 0 && gnssAvgCn0 < 18.0 && accuracy <= 10f) {
            reasons.add("弱信号下仍给出高精度，需警惕异常定位");
        }
        if (!Float.isNaN(sensorHeadingDeg) && location.getSpeed() > 2.0f) {
            double headingDiff = angleDifference(sensorHeadingDeg, normalizeAngle(location.getBearing()));
            if (headingDiff > 120.0) {
                reasons.add("GNSS航向与手机姿态航向差异过大");
            }
        }

        if (reasons.isEmpty()) {
            anomalyLevel = "正常";
            anomalyReason = String.format(
                    Locale.getDefault(),
                    "未发现明显跳变，最近跳变%.1fm/%.1fm/s",
                    lastJumpDistance,
                    lastJumpSpeed
            );
        } else if (reasons.size() == 1) {
            anomalyLevel = "轻微异常";
            anomalyReason = joinReasons(reasons);
        } else {
            anomalyLevel = "疑似异常";
            anomalyReason = joinReasons(reasons);
        }

        lastAnomalyLatLng = now;
        lastAnomalyTimeMillis = nowTime;
    }

    /**
     * 显示异常/欺骗初筛结果
     */
    private void updateAnomalyDetectText() {
        if (tvAnomalyDetect == null) {
            return;
        }
        tvAnomalyDetect.setText("异常/欺骗初筛：" + anomalyLevel + " | " + anomalyReason);
        updateQuickStatusCards(null);
        if ("anomaly".equals(activeFeaturePanel)) {
            refreshFeaturePanel();
        }
    }

    /**
     * 显示 GNSS + 惯性传感器辅助导航状态
     */
    private void updateSensorFusionText() {
        if (tvSensorFusion == null) {
            return;
        }

        if (accelerometerSensor == null || magneticSensor == null) {
            tvSensorFusion.setText("组合导航：本机缺少加速度计或磁力计，无法显示惯性辅助航向");
            if ("sensor".equals(activeFeaturePanel)) {
                refreshFeaturePanel();
            }
            return;
        }
        if (Float.isNaN(sensorHeadingDeg)) {
            tvSensorFusion.setText("组合导航：等待传感器航向数据");
            if ("sensor".equals(activeFeaturePanel)) {
                refreshFeaturePanel();
            }
            return;
        }

        String state;
        if (currentLatLng == null) {
            state = "等待GNSS定位";
        } else if (currentGnssSpeed < 0.8f) {
            state = "低速/静止，航向以手机传感器为参考";
        } else {
            double diff = angleDifference(sensorHeadingDeg, currentGnssBearing);
            if (diff <= 45.0) {
                state = String.format(Locale.getDefault(), "航向一致，差值%.0f°", diff);
            } else {
                state = String.format(Locale.getDefault(), "航向差异%.0f°，可能处于转弯或磁干扰环境", diff);
            }
        }

        tvSensorFusion.setText(String.format(
                Locale.getDefault(),
                "组合导航：传感器航向%.0f° | GNSS速度%.1fm/s | GNSS航向%s | %s",
                sensorHeadingDeg,
                currentGnssSpeed,
                Float.isNaN(currentGnssBearing) ? "--" : String.format(Locale.getDefault(), "%.0f°", currentGnssBearing),
                state
        ));
        if ("sensor".equals(activeFeaturePanel)) {
            refreshFeaturePanel();
        }
    }

    /**
     * 角度归一化到 0~360 度
     */
    private float normalizeAngle(float angle) {
        if (Float.isNaN(angle) || Float.isInfinite(angle)) {
            return Float.NaN;
        }
        float normalized = angle % 360f;
        if (normalized < 0) {
            normalized += 360f;
        }
        return normalized;
    }

    /**
     * 两个方向角的最小夹角差，范围 0~180 度
     */
    private double angleDifference(double a, double b) {
        if (Double.isNaN(a) || Double.isNaN(b)) {
            return 0.0;
        }
        double diff = Math.abs(a - b) % 360.0;
        return diff > 180.0 ? 360.0 - diff : diff;
    }

    /**
     * 将若干原因拼接成适合界面展示的文字
     */
    private String joinReasons(ArrayList<String> reasons) {
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < reasons.size(); i++) {
            if (i > 0) {
                builder.append("；");
            }
            builder.append(reasons.get(i));
        }
        return builder.toString();
    }

    /**
     * 高德定位类型转为可读文字，避免界面只显示数字
     */
    private String getLocationTypeName(int type) {
        switch (type) {
            case 1:
                return "GPS";
            case 2:
                return "前次定位";
            case 4:
                return "缓存定位";
            case 5:
                return "WiFi定位";
            case 6:
                return "基站定位";
            case 8:
                return "离线定位";
            case 9:
                return "末次缓存";
            default:
                return "融合定位" + type;
        }
    }

    // ==================== 围栏 ====================

    /**
     * 开关围栏模式
     */
    private void toggleFenceMode() {
        isFenceModeEnabled = !isFenceModeEnabled;

        if (isFenceModeEnabled) {
            btnFenceMode.setText("围栏中");
            cardFenceRadius.setVisibility(View.VISIBLE);
            Toast.makeText(this, "围栏模式已开启，请长按地图设置围栏中心", Toast.LENGTH_SHORT).show();
        } else {
            btnFenceMode.setText("围栏");
            if (fenceCenter == null) {
                cardFenceRadius.setVisibility(View.GONE);
            }
            Toast.makeText(this, "围栏模式已关闭", Toast.LENGTH_SHORT).show();
        }
    }

    /**
     * 地图长按事件
     * 在围栏模式下，长按地图设置围栏中心
     */
    @Override
    public void onMapLongClick(LatLng latLng) {
        if (!isFenceModeEnabled) {
            return;
        }

        // 记录新的围栏中心
        fenceCenter = latLng;
        // 重置围栏内外状态
        lastInsideState = null;

        // 如果旧围栏存在则先移除
        if (fenceCircle != null) {
            fenceCircle.remove();
        }
        if (fenceMarker != null) {
            fenceMarker.remove();
        }

        // 添加围栏中心点
        fenceMarker = aMap.addMarker(new MarkerOptions()
                .position(fenceCenter)
                .title("电子围栏中心")
                .icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_AZURE)));

        // 添加围栏圆形区域
        fenceCircle = aMap.addCircle(new CircleOptions()
                .center(fenceCenter)
                .radius(fenceRadius)
                .strokeWidth(4)
                .strokeColor(0xAA64748B)
                .fillColor(0x2264748B));

        cardFenceRadius.setVisibility(View.VISIBLE);
        Toast.makeText(this, "电子围栏已设置", Toast.LENGTH_SHORT).show();

        // 如果已有当前位置，则立刻更新围栏状态
        if (currentLatLng != null) {
            checkFenceState(currentLatLng, false);
        }
    }

    /**
     * 判断某个位置点是否在围栏内
     * allowToast 为 true 时允许弹出进入或离开提示
     */
    private void checkFenceState(LatLng locationLatLng, boolean allowToast) {
        if (fenceCenter == null) {
            updateFenceStatusNoFence();
            return;
        }

        // 计算当前位置到围栏中心的距离
        float distance = AMapUtils.calculateLineDistance(locationLatLng, fenceCenter);
        // 小于等于围栏半径则认为在围栏内
        boolean isInside = distance <= fenceRadius;

        // 组织状态显示文本
        String statusText = String.format(
                Locale.getDefault(),
                "围栏：%s | 距中心 %.1fm | 半径 %.0fm",
                isInside ? "围栏内" : "围栏外",
                distance,
                fenceRadius
        );

        tvFenceStatus.setText(statusText);
        tvFenceStatus.setTextColor(isInside ? 0xFF475569 : 0xFF78716C);

        // 第一次判断时仅记录状态，不弹进入或离开提示
        if (lastInsideState == null) {
            lastInsideState = isInside;
            return;
        }

        // 仅在状态发生变化时处理提示
        if (isInside != lastInsideState) {
            if (allowToast) {
                if (isInside) {
                    Toast.makeText(this, "已进入电子围栏", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(this, "已离开电子围栏", Toast.LENGTH_SHORT).show();
                }
            }
            lastInsideState = isInside;
        }
    }

    /**
     * 显示“围栏未设置”的默认状态
     */
    private void updateFenceStatusNoFence() {
        tvFenceStatus.setText("围栏：未设置");
        tvFenceStatus.setTextColor(0xFF64748B);
    }

    /**
     * 清除当前围栏
     */
    private void clearFence() {
        if (fenceCircle != null) {
            fenceCircle.remove();
            fenceCircle = null;
        }
        if (fenceMarker != null) {
            fenceMarker.remove();
            fenceMarker = null;
        }

        fenceCenter = null;
        lastInsideState = null;
        cardFenceRadius.setVisibility(View.GONE);
        btnFenceMode.setText("围栏");
        isFenceModeEnabled = false;
        updateFenceStatusNoFence();

        Toast.makeText(this, "围栏已清除", Toast.LENGTH_SHORT).show();
    }

    // ==================== 轨迹 ====================

    /**
     * 开始或停止轨迹记录
     */
    private void toggleTrackRecording() {
        isTracking = !isTracking;

        if (isTracking) {
            btnTrack.setText("停轨");
            Toast.makeText(this, "开始记录轨迹", Toast.LENGTH_SHORT).show();
        } else {
            btnTrack.setText("轨迹");
            Toast.makeText(this, "已停止记录轨迹", Toast.LENGTH_SHORT).show();
        }

        updateTrackStatus();
    }

    /**
     * 向轨迹中加入一个新点
     * 只有与上一个点距离至少达到 2 米时才真正加入
     */
    private void addTrackPoint(LatLng point) {
        if (trackPoints.isEmpty()) {
            trackPoints.add(point);
        } else {
            LatLng lastPoint = trackPoints.get(trackPoints.size() - 1);
            float distance = AMapUtils.calculateLineDistance(lastPoint, point);

            if (distance >= 2f) {
                trackDistance += distance;
                trackPoints.add(point);
            }
        }

        // 首次绘制轨迹时创建折线，否则更新点集合
        if (trackPolyline == null) {
            trackPolyline = aMap.addPolyline(new PolylineOptions()
                    .addAll(trackPoints)
                    .width(10f)
                    .color(0xFF64748B));
        } else {
            trackPolyline.setPoints(new ArrayList<>(trackPoints));
        }

        updateTrackStatus();
    }

    /**
     * 清除轨迹
     */
    private void clearTrack() {
        isTracking = false;
        btnTrack.setText("轨迹");

        trackPoints.clear();
        trackDistance = 0f;

        if (trackPolyline != null) {
            trackPolyline.remove();
            trackPolyline = null;
        }

        updateTrackStatus();
        Toast.makeText(this, "轨迹已清除", Toast.LENGTH_SHORT).show();
    }

    /**
     * 更新顶部轨迹状态文字
     */
    private void updateTrackStatus() {
        if (trackPoints.isEmpty()) {
            tvTrackStatus.setText("轨迹：未记录");
            return;
        }

        if (isTracking) {
            tvTrackStatus.setText(String.format(
                    Locale.getDefault(),
                    "轨迹：记录中 | 点数 %d | 距离 %.1fm",
                    trackPoints.size(),
                    trackDistance
            ));
        } else {
            tvTrackStatus.setText(String.format(
                    Locale.getDefault(),
                    "轨迹：已停止 | 点数 %d | 总长 %.1fm",
                    trackPoints.size(),
                    trackDistance
            ));
        }
    }

    // ==================== 搜索与路线 ====================

    /**
     * 根据输入框关键字搜索地点
     */
    private void searchLocation() {
        String keyword = etKeyword.getText().toString().trim();
        if (keyword.isEmpty()) {
            Toast.makeText(this, "请输入要搜索的位置", Toast.LENGTH_SHORT).show();
            return;
        }

        // 搜索时确保顶部信息区展开
        isInfoExpanded = true;
        layoutSearchExtras.setVisibility(View.VISIBLE);
        btnToggleInfo.setText("收起");

        // 构造 POI 查询对象
        PoiSearch.Query query = new PoiSearch.Query(keyword, "", "");
        query.setPageSize(20);
        query.setPageNum(1);

        try {
            PoiSearch poiSearch = new PoiSearch(this, query);
            poiSearch.setOnPoiSearchListener(this);
            poiSearch.searchPOIAsyn();
            tvRouteStatus.setText("路线：正在搜索位置...");
        } catch (AMapException e) {
            e.printStackTrace();
            tvRouteStatus.setText("路线：位置搜索初始化失败");
            Toast.makeText(this, "位置搜索初始化失败", Toast.LENGTH_SHORT).show();
        }
    }

    /**
     * POI 搜索结果回调
     */
    @Override
    public void onPoiSearched(PoiResult pageResult, int errorCode) {
        searchPoiList.clear();

        if (errorCode == 1000 && pageResult != null && pageResult.getPois() != null
                && !pageResult.getPois().isEmpty()) {

            searchPoiList.addAll(pageResult.getPois());
            searchAdapter.notifyDataSetChanged();

            lvSearchResults.setVisibility(View.VISIBLE);
            tvRouteStatus.setText("路线：请选择一个搜索结果");
        } else {
            lvSearchResults.setVisibility(View.GONE);
            layoutRouteActions.setVisibility(View.GONE);
            tvRouteStatus.setText("路线：未搜索到结果");
            Toast.makeText(this, "未搜索到结果", Toast.LENGTH_SHORT).show();
        }
    }

    /**
     * 点击某条搜索结果后，设置目的地并在地图上添加目的地 Marker
     */
    private void selectSearchResult(int position) {
        if (position < 0 || position >= searchPoiList.size()) {
            return;
        }

        PoiItem item = searchPoiList.get(position);
        LatLonPoint point = item.getLatLonPoint();

        if (point == null) {
            Toast.makeText(this, "该结果没有有效坐标", Toast.LENGTH_SHORT).show();
            return;
        }

        routeDestination = new LatLng(point.getLatitude(), point.getLongitude());
        routeDestinationName = item.getTitle() == null ? "目的地" : item.getTitle();

        if (destinationMarker != null) {
            destinationMarker.remove();
        }

        destinationMarker = aMap.addMarker(new MarkerOptions()
                .position(routeDestination)
                .title(routeDestinationName)
                .snippet(item.getSnippet())
                .icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_ORANGE)));

        aMap.animateCamera(CameraUpdateFactory.newLatLngZoom(routeDestination, 16f));
        lvSearchResults.setVisibility(View.GONE);

        layoutRouteActions.setVisibility(View.VISIBLE);
        tvSelectedDestination.setText("已选目的地：" + routeDestinationName);
        tvRouteStatus.setText("路线：已选目的地，未规划");
        Toast.makeText(this, "已选择：" + routeDestinationName, Toast.LENGTH_SHORT).show();
    }

    /**
     * 单个 POI 搜索回调
     * 当前代码没有使用
     */
    @Override
    public void onPoiItemSearched(PoiItem poiItem, int errorCode) {
        // 未使用
    }

    /**
     * 规划步行路线
     */
    private void planWalkRoute() {
        if (currentLatLng == null) {
            Toast.makeText(this, "当前位置未获取到", Toast.LENGTH_SHORT).show();
            return;
        }

        if (routeDestination == null) {
            Toast.makeText(this, "请先搜索并选择一个目的地", Toast.LENGTH_SHORT).show();
            return;
        }

        if (routeSearch == null) {
            Toast.makeText(this, "路线服务初始化失败", Toast.LENGTH_SHORT).show();
            return;
        }

        RouteSearch.FromAndTo fromAndTo = new RouteSearch.FromAndTo(
                new LatLonPoint(currentLatLng.latitude, currentLatLng.longitude),
                new LatLonPoint(routeDestination.latitude, routeDestination.longitude)
        );

        RouteSearch.WalkRouteQuery query = new RouteSearch.WalkRouteQuery(fromAndTo);
        routeSearch.calculateWalkRouteAsyn(query);

        tvRouteStatus.setText("路线：正在规划步行路线...");
    }

    /**
     * 规划驾车路线
     */
    private void planDriveRoute() {
        if (currentLatLng == null) {
            Toast.makeText(this, "当前位置未获取到", Toast.LENGTH_SHORT).show();
            return;
        }

        if (routeDestination == null) {
            Toast.makeText(this, "请先搜索并选择一个目的地", Toast.LENGTH_SHORT).show();
            return;
        }

        if (routeSearch == null) {
            Toast.makeText(this, "路线服务初始化失败", Toast.LENGTH_SHORT).show();
            return;
        }

        RouteSearch.FromAndTo fromAndTo = new RouteSearch.FromAndTo(
                new LatLonPoint(currentLatLng.latitude, currentLatLng.longitude),
                new LatLonPoint(routeDestination.latitude, routeDestination.longitude)
        );

        RouteSearch.DriveRouteQuery query = new RouteSearch.DriveRouteQuery(
                fromAndTo,
                RouteSearch.DRIVING_SINGLE_DEFAULT,
                null,
                null,
                ""
        );

        routeSearch.calculateDriveRouteAsyn(query);
        tvRouteStatus.setText("路线：正在规划驾车路线...");
    }

    /**
     * 步行路线结果回调
     */
    @Override
    public void onWalkRouteSearched(WalkRouteResult walkRouteResult, int errorCode) {
        if (errorCode == 1000
                && walkRouteResult != null
                && walkRouteResult.getPaths() != null
                && !walkRouteResult.getPaths().isEmpty()) {

            WalkPath walkPath = walkRouteResult.getPaths().get(0);
            List<LatLng> latLngs = new ArrayList<>();

            if (currentLatLng != null) {
                latLngs.add(currentLatLng);
            }

            // 把每一步的折线点拼接成整条路线
            for (WalkStep step : walkPath.getSteps()) {
                List<LatLonPoint> points = step.getPolyline();
                if (points != null) {
                    for (LatLonPoint p : points) {
                        latLngs.add(new LatLng(p.getLatitude(), p.getLongitude()));
                    }
                }
            }

            drawRoutePolyline(latLngs, 0xFF1D4ED8);

            tvRouteStatus.setText(String.format(
                    Locale.getDefault(),
                    "路线：步行 %.0fm | 约 %.0f 分钟",
                    walkPath.getDistance(),
                    walkPath.getDuration() / 60f
            ));

            Toast.makeText(this, "步行路线规划成功", Toast.LENGTH_SHORT).show();
        } else {
            tvRouteStatus.setText("路线：步行路线规划失败");
            Toast.makeText(this, "步行路线规划失败", Toast.LENGTH_SHORT).show();
        }
    }

    /**
     * 驾车路线结果回调
     */
    @Override
    public void onDriveRouteSearched(DriveRouteResult driveRouteResult, int errorCode) {
        if (errorCode == 1000
                && driveRouteResult != null
                && driveRouteResult.getPaths() != null
                && !driveRouteResult.getPaths().isEmpty()) {

            DrivePath drivePath = driveRouteResult.getPaths().get(0);
            List<LatLng> latLngs = new ArrayList<>();

            if (currentLatLng != null) {
                latLngs.add(currentLatLng);
            }

            // 把每一步驾车路线点拼接成整条路线
            for (com.amap.api.services.route.DriveStep step : drivePath.getSteps()) {
                List<LatLonPoint> points = step.getPolyline();
                if (points != null) {
                    for (LatLonPoint p : points) {
                        latLngs.add(new LatLng(p.getLatitude(), p.getLongitude()));
                    }
                }
            }

            drawRoutePolyline(latLngs, 0xFFFF6B00);

            tvRouteStatus.setText(String.format(
                    Locale.getDefault(),
                    "路线：驾车 %.0fm | 约 %.0f 分钟",
                    drivePath.getDistance(),
                    drivePath.getDuration() / 60f
            ));

            Toast.makeText(this, "驾车路线规划成功", Toast.LENGTH_SHORT).show();
        } else {
            tvRouteStatus.setText("路线：驾车路线规划失败");
            Toast.makeText(this, "驾车路线规划失败", Toast.LENGTH_SHORT).show();
        }
    }

    /**
     * 绘制路线折线，并自动缩放地图让整条路线完整显示
     */
    private void drawRoutePolyline(List<LatLng> latLngs, int color) {
        if (routePolyline != null) {
            routePolyline.remove();
        }

        routePolyline = aMap.addPolyline(new PolylineOptions()
                .addAll(latLngs)
                .width(14f)
                .color(color));

        if (!latLngs.isEmpty()) {
            LatLngBounds.Builder builder = new LatLngBounds.Builder();
            for (LatLng latLng : latLngs) {
                builder.include(latLng);
            }
            aMap.animateCamera(CameraUpdateFactory.newLatLngBounds(builder.build(), 120));
        }
    }

    /**
     * 公交路线回调
     * 当前未使用
     */
    @Override
    public void onBusRouteSearched(BusRouteResult busRouteResult, int errorCode) {
        // 未使用
    }

    /**
     * 骑行路线回调
     * 当前未使用
     */
    @Override
    public void onRideRouteSearched(RideRouteResult rideRouteResult, int errorCode) {
        // 未使用
    }

    /**
     * 清除当前路线
     */
    private void clearRoute() {
        if (routePolyline != null) {
            routePolyline.remove();
            routePolyline = null;
        }
        tvRouteStatus.setText("路线：已清除");
        Toast.makeText(this, "路线已清除", Toast.LENGTH_SHORT).show();
    }

    // ==================== 拍照 ====================

    /**
     * 在当前位置调用相机拍照，并准备后续生成拍照定位点
     */
    private void takePhotoWithLocation() {
        if (currentLatLng == null) {
            Toast.makeText(this, "当前位置未获取到，稍后再试", Toast.LENGTH_SHORT).show();
            return;
        }

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(
                    this,
                    new String[]{Manifest.permission.CAMERA},
                    REQUEST_CAMERA_PERMISSION
            );
            return;
        }

        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        if (takePictureIntent.resolveActivity(getPackageManager()) != null) {
            // 先记录拍照发生时的位置、时间、地址
            pendingPhotoLatLng = currentLatLng;
            pendingPhotoTime = timeFormat.format(new Date());
            pendingPhotoAddress = currentAddress;
            startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE);
        } else {
            Toast.makeText(this, "未找到可用相机应用", Toast.LENGTH_SHORT).show();
        }
    }

    /**
     * 接收系统相机返回结果
     * 成功后在地图上创建拍照定位点
     */
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQUEST_IMAGE_CAPTURE && resultCode == RESULT_OK && data != null) {
            Bundle extras = data.getExtras();
            if (extras != null && extras.get("data") instanceof Bitmap) {
                Bitmap bitmap = (Bitmap) extras.get("data");

                if (pendingPhotoLatLng != null) {
                    Marker marker = aMap.addMarker(new MarkerOptions()
                            .position(pendingPhotoLatLng)
                            .title("拍照定位点")
                            .snippet("点击查看照片")
                            .icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_ROSE)));

                    if (marker != null) {
                        String info = "时间：" + pendingPhotoTime
                                + "\n地址：" + pendingPhotoAddress
                                + "\n经度：" + pendingPhotoLatLng.longitude
                                + "\n纬度：" + pendingPhotoLatLng.latitude;

                        // 保存 Marker id 与照片、说明信息的对应关系
                        photoBitmapMap.put(marker.getId(), bitmap);
                        photoInfoMap.put(marker.getId(), info);
                        photoMarkers.add(marker);

                        // 把地图移动到拍照点位置
                        aMap.animateCamera(CameraUpdateFactory.newLatLngZoom(pendingPhotoLatLng, 18f));
                        Toast.makeText(this, "拍照定位成功", Toast.LENGTH_SHORT).show();
                    }
                }
            }
        }
    }

    /**
     * 清除所有拍照定位点
     */
    private void clearPhotoMarkers() {
        for (Marker marker : photoMarkers) {
            if (marker != null) {
                marker.remove();
            }
        }
        photoMarkers.clear();
        photoBitmapMap.clear();
        photoInfoMap.clear();
        Toast.makeText(this, "拍照点已清除", Toast.LENGTH_SHORT).show();
    }

    /**
     * Marker 点击事件
     * 如果点击的是拍照点，就弹出照片信息对话框
     */
    @Override
    public boolean onMarkerClick(Marker marker) {
        if (photoBitmapMap.containsKey(marker.getId())) {
            showPhotoDialog(photoBitmapMap.get(marker.getId()), photoInfoMap.get(marker.getId()));
            return true;
        }
        return false;
    }

    /**
     * 弹出拍照定位信息对话框
     */
    private void showPhotoDialog(Bitmap bitmap, String info) {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(dp(20), dp(20), dp(20), dp(10));

        ImageView imageView = new ImageView(this);
        imageView.setImageBitmap(bitmap);
        imageView.setAdjustViewBounds(true);

        TextView textView = new TextView(this);
        textView.setText(info);
        textView.setTextSize(15f);
        textView.setPadding(0, dp(16), 0, 0);

        layout.addView(imageView);
        layout.addView(textView);

        new AlertDialog.Builder(this)
                .setTitle("拍照定位信息")
                .setView(layout)
                .setPositiveButton("确定", null)
                .show();
    }

    // ==================== 生命周期 ====================

    /**
     * 页面恢复显示时同步恢复 MapView
     */
    @Override
    protected void onResume() {
        super.onResume();
        mapView.onResume();
        startSensorMonitor();
    }

    /**
     * 页面暂停时同步暂停 MapView
     */
    @Override
    protected void onPause() {
        super.onPause();
        mapView.onPause();
        stopSensorMonitor();
    }

    /**
     * 保存页面状态时同步保存 MapView 状态
     */
    @Override
    protected void onSaveInstanceState(@NonNull Bundle outState) {
        super.onSaveInstanceState(outState);
        mapView.onSaveInstanceState(outState);
    }

    /**
     * 页面销毁时释放定位和地图资源
     */
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (aMapLocationClient != null) {
            aMapLocationClient.stopLocation();
            aMapLocationClient.onDestroy();
        }
        stopGnssStatusMonitor();
        stopSensorMonitor();
        mapView.onDestroy();
    }

    // ==================== 权限回调 ====================

    /**
     * 动态权限申请结果回调
     */
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                           @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        // 处理定位权限结果
        if (requestCode == REQUEST_LOCATION_PERMISSION) {
            boolean granted = true;
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    granted = false;
                    break;
                }
            }
            if (granted) {
                enableLocation();
            } else {
                Toast.makeText(this, "未授予定位权限", Toast.LENGTH_SHORT).show();
            }
        }

        // 处理相机权限结果
        if (requestCode == REQUEST_CAMERA_PERMISSION) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                takePhotoWithLocation();
            } else {
                Toast.makeText(this, "未授予相机权限", Toast.LENGTH_SHORT).show();
            }
        }
    }

    // ==================== 工具方法 ====================

    /**
     * dp 转 px
     * 方便在代码中动态创建控件时统一设置尺寸
     */
    private int dp(int value) {
        return (int) TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP,
                value,
                getResources().getDisplayMetrics()
        );
    }

    // ==================== 自定义搜索结果适配器 ====================

    /**
     * 搜索结果适配器
     * 不额外新建 XML 布局文件，而是在代码里动态生成列表项视图
     */
    private class SearchResultAdapter extends BaseAdapter {

        @Override
        public int getCount() {
            return searchPoiList.size();
        }

        @Override
        public Object getItem(int position) {
            return searchPoiList.get(position);
        }

        @Override
        public long getItemId(int position) {
            return position;
        }

        /**
         * 生成每一项搜索结果的显示视图
         */
        @Override
        public View getView(int position, View convertView, ViewGroup parent) {
            ViewHolder holder;

            if (convertView == null) {
                // 外层卡片式根布局
                LinearLayout root = new LinearLayout(MainActivity.this);
                root.setOrientation(LinearLayout.HORIZONTAL);
                root.setGravity(Gravity.CENTER_VERTICAL);
                root.setMinimumHeight(dp(62));
                root.setPadding(dp(12), dp(10), dp(12), dp(10));

                // 创建圆角浅色背景
                GradientDrawable bg = new GradientDrawable();
                bg.setColor(0xFFF8FAFC);
                bg.setCornerRadius(dp(14));
                bg.setStroke(dp(1), 0xFFE2E8F0);
                root.setBackground(bg);

                // 左侧文字区域
                LinearLayout textContainer = new LinearLayout(MainActivity.this);
                textContainer.setOrientation(LinearLayout.VERTICAL);
                LinearLayout.LayoutParams textParams =
                        new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
                textContainer.setLayoutParams(textParams);

                // 标题文本
                TextView title = new TextView(MainActivity.this);
                title.setTextColor(0xFF0F172A);
                title.setTextSize(TypedValue.COMPLEX_UNIT_SP, 14);
                title.setTypeface(Typeface.DEFAULT_BOLD);
                title.setMaxLines(1);

                // 地址或说明文本
                TextView snippet = new TextView(MainActivity.this);
                snippet.setTextColor(0xFF64748B);
                snippet.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12);
                snippet.setMaxLines(2);
                LinearLayout.LayoutParams snippetLp =
                        new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
                snippetLp.topMargin = dp(4);
                snippet.setLayoutParams(snippetLp);

                textContainer.addView(title);
                textContainer.addView(snippet);

                // 右侧箭头提示
                TextView arrow = new TextView(MainActivity.this);
                arrow.setText("›");
                arrow.setTextColor(0xFF94A3B8);
                arrow.setTextSize(TypedValue.COMPLEX_UNIT_SP, 18);

                // 把左右内容加到根布局中
                root.addView(textContainer);
                root.addView(arrow);

                // 使用 ViewHolder 缓存控件
                holder = new ViewHolder();
                holder.title = title;
                holder.snippet = snippet;
                holder.arrow = arrow;

                convertView = root;
                convertView.setTag(holder);
            } else {
                // 复用旧视图，提升列表滚动性能
                holder = (ViewHolder) convertView.getTag();
            }

            PoiItem item = searchPoiList.get(position);

            // 如果标题为空，则显示默认值
            String title = item.getTitle() == null ? "未知地点" : item.getTitle();
            // 如果地址为空，则显示默认说明
            String snippet = item.getSnippet() == null || item.getSnippet().trim().isEmpty()
                    ? "暂无详细地址"
                    : item.getSnippet();

            holder.title.setText(title);
            holder.snippet.setText(snippet);

            return convertView;
        }

        /**
         * ViewHolder 用于缓存每一项中的子控件引用
         */
        class ViewHolder {
            TextView title;
            TextView snippet;
            TextView arrow;
        }
    }
}