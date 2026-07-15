package com.example.gnsslogger.data.model

/**
 * GPS 广播星历参数
 * 从 GnssNavigationMessage 解析得到
 */
data class GpsEphemeris(
    val svid: Int,
    // 轨道参数
    val m0: Double,           // 平近点角（rad）
    val deltaN: Double,       // 平均角速度修正（rad/s）
    val eccentricity: Double, // 轨道离心率
    val sqrtA: Double,        // 轨道半长轴平方根（m^0.5）
    val omega0: Double,       // 升交点赤经（rad）
    val i0: Double,           // 轨道倾角（rad）
    val omega: Double,        // 近地点角距（rad）
    val omegaDot: Double,     // 升交点赤经变化率（rad/s）
    val idot: Double,         // 轨道倾角变化率（rad/s）
    // 修正参数
    val cuc: Double,          // 纬度幅角余弦修正（rad）
    val cus: Double,          // 纬度幅角正弦修正（rad）
    val crc: Double,          // 轨道半径余弦修正（m）
    val crs: Double,          // 轨道半径正弦修正（m）
    val cic: Double,          // 轨道倾角余弦修正（rad）
    val cis: Double,          // 轨道倾角正弦修正（rad）
    // 时间参数
    val tgd: Double,          // 群延迟（s）
    val toc: Double,          // 星钟参考时间（s）
    val af0: Double,          // 星钟偏差（s）
    val af1: Double,          // 星钟漂移（s/s）
    val af2: Double,          // 星钟漂移率（s/s^2）
    val toe: Double,          // 星历参考时间（s）
    val iode: Int,            // 星历数据期
    val iodc: Int,            // 时钟数据期
    val week: Int,            // GPS 周
    val tlmMessage: Int,      // 遥测信息
    val fitInterval: Int,     // 拟合间隔
)

/**
 * GLONASS 广播星历参数
 */
data class GlonassEphemeris(
    val svid: Int,
    val taud: Double,         // 相对于 GPS 的时间偏差（s）
    val gamma: Double,        // 频率偏差
    val tb: Double,           // 星历参考时间（s）
    // 位置（km → m）
    val x: Double,            // X 位置（m）
    val y: Double,            // Y 位置（m）
    val z: Double,            // Z 位置（m）
    // 速度（km/s → m/s）
    val vx: Double,           // X 速度（m/s）
    val vy: Double,           // Y 速度（m/s）
    val vz: Double,           // Z 速度（m/s）
    // 加速度（km/s^2 → m/s^2）
    val ax: Double,           // X 加速度（m/s^2）
    val ay: Double,           // Y 加速度（m/s^2）
    val az: Double,           // Z 加速度（m/s^2）
    val health: Int,          // 健康状态
    val frequencyOffset: Double, // 频道号偏移
)

/**
 * 导航电文解析结果
 */
data class NavigationData(
    val gpsEphemerisMap: Map<Int, GpsEphemeris> = emptyMap(),
    val glonassEphemerisMap: Map<Int, GlonassEphemeris> = emptyMap(),
    val ionoParams: IonosphereParameters? = null,
)

/**
 * Klobuchar 电离层模型参数
 */
data class IonosphereParameters(
    val alpha0: Double,
    val alpha1: Double,
    val alpha2: Double,
    val alpha3: Double,
    val beta0: Double,
    val beta1: Double,
    val beta2: Double,
    val beta3: Double,
)
