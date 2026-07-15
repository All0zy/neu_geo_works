package com.example.gnsslogger.data.repository

import android.location.Location
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import com.example.gnsslogger.data.model.*

/**
 * GNSS 数据仓库
 * 集中管理所有 GNSS 相关数据，供 ViewModel 和 UI 层访问
 */
class GnssRepository {
    // 原始测量数据
    private val _rawMeasurements = MutableLiveData<List<RawMeasurement>>()
    val rawMeasurements: LiveData<List<RawMeasurement>> = _rawMeasurements

    // 卫星信息
    private val _satellites = MutableLiveData<List<SatelliteInfo>>()
    val satellites: LiveData<List<SatelliteInfo>> = _satellites

    // 导航数据
    private val _navigationData = MutableLiveData<NavigationData>()
    val navigationData: LiveData<NavigationData> = _navigationData

    // 定位结果
    private val _positionResult = MutableLiveData<PositionResult?>()
    val positionResult: LiveData<PositionResult?> = _positionResult

    // 原始位置（系统 LocationManager）
    private val _rawLocation = MutableLiveData<Location?>()
    val rawLocation: LiveData<Location?> = _rawLocation

    // 日志状态
    private val _isLogging = MutableLiveData(false)
    val isLogging: LiveData<Boolean> = _isLogging

    private val _logFilePath = MutableLiveData<String?>()
    val logFilePath: LiveData<String?> = _logFilePath

    // 测量计数
    private val _measurementCount = MutableLiveData(0)
    val measurementCount: LiveData<Int> = _measurementCount

    /**
     * 更新原始测量数据
     */
    fun updateMeasurements(measurements: List<RawMeasurement>) {
        _rawMeasurements.postValue(measurements)
        _measurementCount.postValue((_measurementCount.value ?: 0) + measurements.size)
    }

    /**
     * 更新卫星信息
     */
    fun updateSatellites(satellites: List<SatelliteInfo>) {
        _satellites.postValue(satellites)
    }

    /**
     * 更新导航数据
     */
    fun updateNavigationData(data: NavigationData) {
        _navigationData.postValue(data)
    }

    /**
     * 更新定位结果
     */
    fun updatePosition(position: PositionResult?) {
        _positionResult.postValue(position)
    }

    /**
     * 更新精度值（来自手机系统 GPS）
     */
    fun updateAccuracy(accuracyMeters: Double) {
        val current = _positionResult.value
        if (current != null) {
            _positionResult.postValue(current.copy(accuracyMeters = accuracyMeters))
        }
    }

    /**
     * 更新原始位置
     */
    fun updateRawLocation(location: Location?) {
        _rawLocation.postValue(location)
    }

    /**
     * 设置日志状态
     */
    fun setLoggingState(logging: Boolean, filePath: String? = null) {
        _isLogging.postValue(logging)
        _logFilePath.postValue(filePath)
    }

    /**
     * 重置测量计数
     */
    fun resetMeasurementCount() {
        _measurementCount.postValue(0)
    }
}
