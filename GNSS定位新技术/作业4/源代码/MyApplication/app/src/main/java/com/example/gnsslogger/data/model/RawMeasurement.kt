package com.example.gnsslogger.data.model

/**
 * GNSS 原始观测量数据类
 * 对应 Android GnssMeasurement 的关键字段
 */
data class RawMeasurement(
    val timeNanos: Long,                    // 测量时间（GPS 周内纳秒）
    val timeOffsetNanos: Double,            // 时间偏移
    val receivedSvTimeNanos: Long,          // 接收到的卫星时间（纳秒）
    val receivedSvTimeUncertaintyNanos: Long,// 卫星时间不确定度
    val state: Int,                         // 卫星信号状态
    val svid: Int,                          // 卫星编号
    val constellationType: Int,             // 星座类型（GPS/GLONASS/BDS等）
    val cn0DbHz: Double,                    // 载噪比（dB-Hz）
    val pseudorangeRateMetersPerSecond: Double, // 伪距率（m/s）
    val pseudorangeRateUncertaintyMetersPerSecond: Double,
    val accumulatedDeltaRangeState: Int,    // 载波相位累积变化量状态
    val accumulatedDeltaRangeMeters: Double,// 载波相位累积变化量（米）
    val accumulatedDeltaRangeUncertaintyMeters: Double,
    val carrierFrequencyHz: Float,          // 载波频率（Hz）
    val codeType: String,                   // 码类型（C/A, L1C, L5等）
    val multipathIndicator: Int,            // 多径指示
    val snrInDb: Double,                    // 信噪比
    val basebandCn0DbHz: Double,            // 基带载噪比
    val fullInterSignalBiasNanos: Double,   // 全信号间偏差
    val satelliteInterSignalBiasNanos: Double,
    // 计算字段
    val pseudorangeMeters: Double = 0.0,    // 计算的伪距（米）
    val satelliteElevationDeg: Double = 0.0,// 卫星仰角（度）
    val satelliteAzimuthDeg: Double = 0.0,  // 卫星方位角（度）
)
