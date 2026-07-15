package com.example.gnsslogger.ui

import android.annotation.SuppressLint
import android.app.Application
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import android.os.Looper
import android.util.Log
import androidx.core.content.ContextCompat
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.example.gnsslogger.data.model.*
import com.example.gnsslogger.data.repository.GnssRepository
import com.example.gnsslogger.gnss.*
import com.example.gnsslogger.log.CsvLogger
import com.example.gnsslogger.log.LogFileManager
import com.example.gnsslogger.positioning.SppEngine
import com.example.gnsslogger.util.CoordinateUtils

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/**
 * 主 ViewModel - 深度调试版本
 */
class MainViewModel(application: Application) : AndroidViewModel(application) {
    companion object {
        private const val TAG = "GNSS_DEBUG"
    }

    private val locationManager = application.getSystemService(LocationManager::class.java)
    private val repository = GnssRepository()

    private var measurementManager: GnssMeasurementManager? = null
    private var navigationManager: GnssNavigationManager? = null
    private var statusManager: GnssStatusManager? = null

    private val csvLogger = CsvLogger(application)
    private val logFileManager = LogFileManager(application)
    private val sppEngine = SppEngine()

    private var systemLocationListener: LocationListener? = null
    private var hasSystemLocation = false
    private var systemLocation: Location? = null

    val rawMeasurements: LiveData<List<RawMeasurement>> = repository.rawMeasurements
    val satellites: LiveData<List<SatelliteInfo>> = repository.satellites
    val navigationData: LiveData<NavigationData> = repository.navigationData
    val positionResult: LiveData<PositionResult?> = repository.positionResult
    val isLogging: LiveData<Boolean> = repository.isLogging
    val logFilePath: LiveData<String?> = repository.logFilePath
    val measurementCount: LiveData<Int> = repository.measurementCount

    private val _statusMessage = MutableLiveData("")
    val statusMessage: LiveData<String> = _statusMessage

    private val _ttff = MutableLiveData(0)
    val ttff: LiveData<Int> = _ttff

    private val _ephemerisStatus = MutableLiveData("未下载")
    val ephemerisStatus: LiveData<String> = _ephemerisStatus

    private val _isDownloading = MutableLiveData(false)
    val isDownloading: LiveData<Boolean> = _isDownloading

    private var isInitialized = false
    private var measurementCount_ = 0
    private var positionAttemptCount = 0
    private var lastSppResultTimeMs = 0L

    fun initializeIfPermitted() {
        if (isInitialized) return

        val context = getApplication<Application>()
        if (ContextCompat.checkSelfPermission(context, android.Manifest.permission.ACCESS_FINE_LOCATION)
            != PackageManager.PERMISSION_GRANTED
        ) {
            Log.e(TAG, "没有位置权限!")
            return
        }

        isInitialized = true
        Log.i(TAG, "开始初始化 GNSS...")

        measurementManager = GnssMeasurementManager(locationManager)
        navigationManager = GnssNavigationManager(locationManager)
        statusManager = GnssStatusManager(locationManager)

        registerCallbacks()
        startSystemLocationUpdates()

        Log.i(TAG, "GNSS 初始化完成")
    }

    @SuppressLint("MissingPermission")
    private fun startSystemLocationUpdates() {
        Log.i(TAG, "启动系统 GPS...")
        systemLocationListener = object : LocationListener {
            override fun onLocationChanged(location: Location) {
                systemLocation = location
                val accuracy = location.accuracy.toDouble()
                if (!hasSystemLocation) {
                    hasSystemLocation = true
                    Log.i(TAG, "★ 系统 GPS 位置: ${location.latitude}, ${location.longitude}, 精度: ${accuracy}m")
                    sppEngine.setInitialPosition(
                        CoordinateUtils.LlaCoord(location.latitude, location.longitude, location.altitude)
                    )
                    updatePositionFromSystem(location)
                }
                // 持续刷新精度值（手机系统 GPS 实时精度）
                repository.updateAccuracy(location.accuracy.toDouble())
            }
            override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {
                Log.d(TAG, "GPS 状态: $status")
            }
            override fun onProviderEnabled(provider: String) {
                Log.d(TAG, "GPS 已启用: $provider")
            }
            override fun onProviderDisabled(provider: String) {
                Log.w(TAG, "GPS 已禁用: $provider")
            }
        }

        try {
            locationManager.requestLocationUpdates(
                LocationManager.GPS_PROVIDER,
                1000L,
                0f,
                systemLocationListener!!,
                Looper.getMainLooper()
            )
            Log.i(TAG, "系统 GPS 监听已启动")
        } catch (e: Exception) {
            Log.e(TAG, "系统 GPS 启动失败", e)
        }
    }

    /**
     * 使用系统定位结果
     */
    private fun updatePositionFromSystem(location: Location) {
        // SPP 已有最近结果时不覆盖
        if (System.currentTimeMillis() - lastSppResultTimeMs < 3000) return

        val nSat = statusManager?.getVisibleSatelliteCount() ?: 0
        val position = PositionResult(
            latitudeDeg = location.latitude,
            longitudeDeg = location.longitude,
            altitudeMeters = location.altitude,
            accuracyMeters = location.accuracy.toDouble(),
            speedMps = location.speed.toDouble(),
            bearingDeg = location.bearing.toDouble(),
            timestampMs = location.time,
            gdop = 0.0,
            pdop = 0.0,
            hdop = 0.0,
            vdop = 0.0,
            tdop = 0.0,
            satellitesUsed = location.extras?.getInt("satellites") ?: nSat,
            satellitesVisible = nSat,
            velocityEast = 0.0,
            velocityNorth = 0.0,
            velocityUp = 0.0,
            xEcef = 0.0,
            yEcef = 0.0,
            zEcef = 0.0,
            receiverClockBiasMeters = 0.0,
        )
        Log.i(TAG, "★ 更新定位结果: ${position.latitudeDeg}, ${position.longitudeDeg} 精度=${position.accuracyMeters}m")
        repository.updatePosition(position)
    }

    private fun registerCallbacks() {
        Log.i(TAG, "注册 GNSS 回调...")

        measurementManager?.register(object : GnssMeasurementManager.OnMeasurementsReceivedListener {
            override fun onMeasurementsReceived(
                measurements: List<RawMeasurement>,
                clockInfo: GnssMeasurementManager.GnssClockInfo
            ) {
                measurementCount_++
                if (measurementCount_ % 10 == 0) {
                    Log.d(TAG, "收到测量数据: #${measurementCount_}, ${measurements.size} 颗卫星")
                }

                repository.updateMeasurements(measurements)

                if (csvLogger.isLoggingActive()) {
                    csvLogger.logMeasurements(measurements, clockInfo)
                }

                // 尝试定位
                viewModelScope.launch(Dispatchers.Default) {
                    trySolvePosition(measurements, clockInfo)
                }
            }
        })

        navigationManager?.register(object : GnssNavigationManager.OnNavigationDataListener {
            override fun onNavigationDataUpdated(data: NavigationData) {
                Log.d(TAG, "星历更新: GPS=${data.gpsEphemerisMap.size}")
                repository.updateNavigationData(data)
            }
        })

        statusManager?.register(object : GnssStatusManager.OnStatusChangedListener {
            override fun onSatelliteStatusChanged(satellites: List<SatelliteInfo>) {
                repository.updateSatellites(satellites)
            }

            override fun onFirstFix(ttff: Int) {
                Log.i(TAG, "首次定位: ${ttff}ms")
                _ttff.postValue(ttff)
            }

            override fun onSatelliteStatusChanged() {
                statusManager?.getCurrentSatellites()?.let {
                    repository.updateSatellites(it)
                }
            }
        })

        Log.i(TAG, "GNSS 回调注册完成")
    }

    fun toggleLogging() {
        if (csvLogger.isLoggingActive()) {
            stopLogging()
        } else {
            startLogging()
        }
    }

    private fun startLogging() {
        val file = csvLogger.startLogging()
        if (file != null) {
            repository.setLoggingState(true, file.absolutePath)
            repository.resetMeasurementCount()
            _statusMessage.value = "开始记录: ${file.name}"
        }
    }

    private fun stopLogging() {
        csvLogger.stopLogging()
        repository.setLoggingState(false)
        _statusMessage.value = "日志已保存"
    }

    fun getLogFileManager(): LogFileManager = logFileManager

    fun downloadEphemeris() {
        if (_isDownloading.value == true) return

        viewModelScope.launch {
            _isDownloading.value = true
            _ephemerisStatus.value = "正在下载..."

            try {
                val downloader = EphemerisDownloader()
                val xtraData = downloader.downloadXtraData()
                if (xtraData != null) {
                    _ephemerisStatus.value = "XTRA 下载成功 (${xtraData.size} bytes)"
                    Log.i(TAG, "XTRA 下载成功: ${xtraData.size} bytes")
                } else {
                    val suplResult = downloader.requestSuplAssist()
                    _ephemerisStatus.value = if (suplResult) "SUPL 请求成功" else "下载失败"
                }
            } catch (e: Exception) {
                _ephemerisStatus.value = "下载失败: ${e.message}"
                Log.e(TAG, "下载异常", e)
            } finally {
                _isDownloading.value = false
            }
        }
    }

    /**
     * GNSS 定位解算
     */
    private fun trySolvePosition(
        measurements: List<RawMeasurement>,
        clockInfo: GnssMeasurementManager.GnssClockInfo
    ) {
        positionAttemptCount++

        // 检查伪距数据
        val validMeasurements = measurements.filter { it.pseudorangeMeters > 0 }
        if (validMeasurements.isEmpty()) {
            if (positionAttemptCount % 30 == 0) {
                Log.w(TAG, "没有有效伪距数据! 总测量: ${measurements.size}")
            }
            return
        }

        if (positionAttemptCount % 30 == 0) {
            Log.d(TAG, "定位尝试 #${positionAttemptCount}: ${validMeasurements.size} 有效伪距")
            // 打印前几个伪距值
            for (i in 0 until minOf(3, validMeasurements.size)) {
                val m = validMeasurements[i]
                Log.d(TAG, "  SV${m.svid}: PR=${m.pseudorangeMeters}m, CN0=${m.cn0DbHz}dB")
            }
        }

        // 检查时钟数据
        if (clockInfo.fullBiasNanos == null) {
            if (positionAttemptCount % 30 == 0) {
                Log.w(TAG, "没有时钟数据 (fullBiasNanos=null)")
            }
            return
        }

        // 计算 GPS 时间
        val gpsWeek: Int
        val gpsTow: Double
        try {
            val rxTimeNanos = clockInfo.timeNanos - clockInfo.fullBiasNanos - (clockInfo.biasNanos ?: 0.0)
            gpsWeek = (rxTimeNanos / (604800.0 * 1e9)).toInt()
            gpsTow = (rxTimeNanos % (604800.0 * 1e9)) / 1e9
        } catch (e: Exception) {
            Log.e(TAG, "GPS 时间计算失败", e)
            return
        }

        val navData = navigationManager?.getCurrentNavigationData()
        val satellites = statusManager?.getCurrentSatellites() ?: emptyList()

        if (positionAttemptCount % 30 == 0) {
            Log.d(TAG, "星历: ${navData?.gpsEphemerisMap?.size ?: 0}, 卫星: ${satellites.size}")
        }

        try {
            val result = sppEngine.solve(
                measurements = validMeasurements,
                ephemerisMap = navData?.gpsEphemerisMap ?: emptyMap(),
                satellites = satellites,
                gpsWeek = gpsWeek,
                gpsTowSeconds = gpsTow
            )

            if (result != null) {
                lastSppResultTimeMs = System.currentTimeMillis()
                val displayResult = result.copy(
                    accuracyMeters = systemLocation?.accuracy?.toDouble() ?: result.accuracyMeters
                )
                Log.i(TAG, "★★★ GNSS 定位成功: ${displayResult.latitudeDeg}, ${displayResult.longitudeDeg}, 精度: ${displayResult.accuracyMeters}m")
                repository.updatePosition(displayResult)
                if (csvLogger.isLoggingActive()) {
                    csvLogger.logFix(result)
                }
            } else {
                if (positionAttemptCount % 30 == 0) {
                    Log.w(TAG, "定位返回 null")
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "定位异常", e)
        }
    }

    fun getCurrentSatellites(): List<SatelliteInfo> {
        return statusManager?.getCurrentSatellites() ?: emptyList()
    }

    override fun onCleared() {
        super.onCleared()
        measurementManager?.unregister()
        navigationManager?.unregister()
        statusManager?.unregister()
        systemLocationListener?.let {
            locationManager.removeUpdates(it)
        }
        if (csvLogger.isLoggingActive()) {
            csvLogger.stopLogging()
        }
    }
}
