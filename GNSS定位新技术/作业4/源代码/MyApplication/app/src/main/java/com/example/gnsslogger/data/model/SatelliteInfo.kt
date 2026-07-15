package com.example.gnsslogger.data.model

/**
 * 卫星信息数据类
 */
data class SatelliteInfo(
    val svid: Int,                    // 卫星编号
    val constellationType: Int,       // 星座类型
    val constellationName: String,    // 星座名称
    val cn0DbHz: Double,              // 载噪比
    val elevationDeg: Double,         // 仰角（度）
    val azimuthDeg: Double,           // 方位角（度）
    val usedInFix: Boolean,           // 是否用于定位
    val hasEphemeris: Boolean,        // 是否有星历
    val hasAlmanac: Boolean,          // 是否有历书
    val carrierFrequencyHz: Float,    // 载波频率
    val basebandCn0DbHz: Double,      // 基带载噪比
)
