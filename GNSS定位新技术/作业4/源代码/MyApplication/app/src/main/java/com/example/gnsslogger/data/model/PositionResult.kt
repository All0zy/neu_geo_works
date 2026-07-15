package com.example.gnsslogger.data.model

/**
 * 定位结果数据类
 */
data class PositionResult(
    val latitudeDeg: Double,          // 纬度（度）
    val longitudeDeg: Double,         // 经度（度）
    val altitudeMeters: Double,       // 海拔（米）
    val accuracyMeters: Double,       // 定位精度（米）
    val speedMps: Double,             // 速度（m/s）
    val bearingDeg: Double,           // 方位角（度）
    val timestampMs: Long,            // 时间戳（毫秒）
    // DOP 值
    val gdop: Double,                 // 几何精度因子
    val pdop: Double,                 // 位置精度因子
    val hdop: Double,                 // 水平精度因子
    val vdop: Double,                 // 垂直精度因子
    val tdop: Double,                 // 时间精度因子
    // 卫星信息
    val satellitesUsed: Int,          // 使用的卫星数
    val satellitesVisible: Int,       // 可见卫星数
    // 速度分量（ENU）
    val velocityEast: Double = 0.0,   // 东向速度（m/s）
    val velocityNorth: Double = 0.0,  // 北向速度（m/s）
    val velocityUp: Double = 0.0,     // 天向速度（m/s）
    // 坐标（ECEF）
    val xEcef: Double = 0.0,         // X 坐标（m）
    val yEcef: Double = 0.0,         // Y 坐标（m）
    val zEcef: Double = 0.0,         // Z 坐标（m）
    // 接收机钟差
    val receiverClockBiasMeters: Double = 0.0, // 接收机钟差（米）
)
