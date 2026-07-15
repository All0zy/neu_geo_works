package com.example.gnsslogger.util

/**
 * GNSS 相关常量定义
 */
object Constants {
    // 物理常量
    const val SPEED_OF_LIGHT = 299792458.0          // 光速（m/s）
    const val SPEED_OF_LIGHT_MPS = 299792458.0      // 光速（m/s）

    // 数学常量
    const val PI = 3.14159265358979323846

    // GPS 系统参数
    const val GPS_L1_FREQUENCY = 1575.42e6          // GPS L1 频率（Hz）
    const val GPS_L5_FREQUENCY = 1176.45e6          // GPS L5 频率（Hz）
    const val GPS_L1_WAVELENGTH = SPEED_OF_LIGHT / GPS_L1_FREQUENCY  // GPS L1 波长（m）
    const val GPS_L5_WAVELENGTH = SPEED_OF_LIGHT / GPS_L5_FREQUENCY  // GPS L5 波长（m）
    const val GPS_EPOCH = 315964800.0               // GPS 纪元（1980-01-06 00:00:00 UTC）相对 Unix 时间
    const val GPS_WEEK_SECONDS = 604800.0           // 一周秒数
    const val GPS_LEAP_SECONDS = 18                 // GPS-UTC 闰秒差

    // GLONASS 系统参数
    const val GLONASS_L1_FREQUENCY_BASE = 1602.0e6  // GLONASS L1 基础频率（Hz）
    const val GLONASS_L1_FREQUENCY_STEP = 0.5625e6  // GLONASS L1 频率步进（Hz）
    const val GLONASS_L2_FREQUENCY_BASE = 1246.0e6  // GLONASS L2 基础频率（Hz）
    const val GLONASS_L2_FREQUENCY_STEP = 0.4375e6  // GLONASS L2 频率步进（Hz）

    // BDS 系统参数
    const val BDS_B1C_FREQUENCY = 1575.42e6         // BDS B1C 频率（Hz）
    const val BDS_B2A_FREQUENCY = 1176.45e6         // BDS B2A 频率（Hz）

    // 地球参数 (WGS-84)
    const val EARTH_RADIUS = 6371000.0              // 地球平均半径（m）
    const val EARTH_SEMI_MAJOR_AXIS = 6378137.0     // WGS-84 椭球长半轴（m）
    const val EARTH_FLATTENING = 1.0 / 298.257223563 // WGS-84 扁率
    const val EARTH_ECCENTRICITY_SQ = 2.0 * EARTH_FLATTENING - EARTH_FLATTENING * EARTH_FLATTENING
    const val EARTH_ROTATION_RATE = 7.2921151467e-5 // 地球自转角速度（rad/s）
    const val EARTH_GRAVITATIONAL_CONSTANT = 3.986005e14  // 地球引力常数（m^3/s^2）

    // 角度转换
    const val DEG_TO_RAD = PI / 180.0
    const val RAD_TO_DEG = 180.0 / PI

    // 星座类型（对应 GnssStatus.CONSTELLATION_*）
    const val CONSTELLATION_GPS = 1
    const val CONSTELLATION_SBAS = 2
    const val CONSTELLATION_GLONASS = 3
    const val CONSTELLATION_QZSS = 4
    const val CONSTELLATION_BDS = 5
    const val CONSTELLATION_GALILEO = 6
    const val CONSTELLATION_IRNSS = 7

    // 最小仰角（度）- 低于此值的卫星不用于定位
    const val MIN_ELEVATION_DEG = 5.0

    // 最大可接受伪距残差（米）
    const val MAX_PSEUDORANGE_RESIDUAL = 100.0

    // 最小可见卫星数（用于定位）
    const val MIN_SATELLITES_FOR_FIX = 4
}
