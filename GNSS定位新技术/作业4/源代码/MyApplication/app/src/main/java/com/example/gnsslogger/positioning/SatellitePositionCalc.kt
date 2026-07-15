package com.example.gnsslogger.positioning

import com.example.gnsslogger.data.model.GpsEphemeris
import com.example.gnsslogger.data.model.IonosphereParameters
import com.example.gnsslogger.util.Constants
import com.example.gnsslogger.util.CoordinateUtils
import kotlin.math.*

/**
 * 卫星位置计算器
 * 根据广播星历计算卫星 ECEF 坐标
 */
class SatellitePositionCalc {

    companion object {
        private const val MU = Constants.EARTH_GRAVITATIONAL_CONSTANT  // 地球引力常数 m^3/s^2
        private const val OMEGA_E = Constants.EARTH_ROTATION_RATE     // 地球自转角速度 rad/s
    }

    /**
     * 计算结果
     */
    data class SatellitePosition(
        val svid: Int,
        val xEcef: Double,      // X 坐标 (m)
        val yEcef: Double,      // Y 坐标 (m)
        val zEcef: Double,      // Z 坐标 (m)
        val clockBiasMeters: Double,  // 卫星钟差 (m)
        val elevationDeg: Double,     // 仰角 (度)
        val azimuthDeg: Double,       // 方位角 (度)
        val isValid: Boolean = true,
    )

    /**
     * 根据星历计算卫星位置
     * @param ephemeris GPS 广播星历
     * @param transmitTimeSeconds 信号发射时间（GPS 周内秒）
     * @return 卫星位置（ECEF）
     */
    fun calculateSatellitePosition(
        ephemeris: GpsEphemeris,
        transmitTimeSeconds: Double
    ): SatellitePosition {
        // 计算轨道参数
        val a = ephemeris.sqrtA * ephemeris.sqrtA  // 半长轴
        val n0 = sqrt(MU / (a * a * a))            // 平均角速度
        val n = n0 + ephemeris.deltaN               // 修正平均角速度

        // 时间差
        val tk = transmitTimeSeconds - ephemeris.toe
        // 处理周跨越
        val tkAdjusted = when {
            tk > 302400.0 -> tk - 604800.0
            tk < -302400.0 -> tk + 604800.0
            else -> tk
        }

        // 平近点角
        val mk = ephemeris.m0 + n * tkAdjusted

        // 偏近点角（开普勒方程迭代求解）
        var ek = mk
        for (i in 0 until 10) {
            val ekNew = mk + ephemeris.eccentricity * sin(ek)
            if (abs(ekNew - ek) < 1e-14) break
            ek = ekNew
        }

        // 真近点角
        val sinVk = sqrt(1 - ephemeris.eccentricity * ephemeris.eccentricity) * sin(ek) / (1 - ephemeris.eccentricity * cos(ek))
        val cosVk = (cos(ek) - ephemeris.eccentricity) / (1 - ephemeris.eccentricity * cos(ek))
        val vk = atan2(sinVk, cosVk)

        // 升交角距
        val phik = vk + ephemeris.omega

        // 二阶修正
        val sin2Phi = sin(2 * phik)
        val cos2Phi = cos(2 * phik)
        val deltaUk = ephemeris.cus * sin2Phi + ephemeris.cuc * cos2Phi
        val deltaRk = ephemeris.crs * sin2Phi + ephemeris.crc * cos2Phi
        val deltaIk = ephemeris.cis * sin2Phi + ephemeris.cic * cos2Phi

        val uk = phik + deltaUk
        val rk = a * (1 - ephemeris.eccentricity * cos(ek)) + deltaRk
        val ik = ephemeris.i0 + ephemeris.idot * tkAdjusted + deltaIk

        // 轨道平面坐标
        val xkPrime = rk * cos(uk)
        val ykPrime = rk * sin(uk)

        // 升交点赤经
        val omegaK = ephemeris.omega0 +
                (ephemeris.omegaDot - OMEGA_E) * tkAdjusted -
                OMEGA_E * ephemeris.toe

        // ECEF 坐标
        val cosOmega = cos(omegaK)
        val sinOmega = sin(omegaK)
        val cosIk = cos(ik)
        val sinIk = sin(ik)

        val x = xkPrime * cosOmega - ykPrime * cosIk * sinOmega
        val y = xkPrime * sinOmega + ykPrime * cosIk * cosOmega
        val z = ykPrime * sinIk

        // 地球自转修正（信号传播时间约 0.07s）
        val travelTime = rk / Constants.SPEED_OF_LIGHT
        val omegaTau = OMEGA_E * travelTime
        val xRot = x * cos(omegaTau) + y * sin(omegaTau)
        val yRot = -x * sin(omegaTau) + y * cos(omegaTau)

        // 卫星钟差（米）
        val dt = transmitTimeSeconds - ephemeris.toc
        val clockBiasSeconds = ephemeris.af0 + ephemeris.af1 * dt + ephemeris.af2 * dt * dt
        val clockBiasMeters = clockBiasSeconds * Constants.SPEED_OF_LIGHT
        // 相对论修正
        val relativity = -2 * sqrt(MU) / (Constants.SPEED_OF_LIGHT * Constants.SPEED_OF_LIGHT) *
                ephemeris.eccentricity * ephemeris.sqrtA * sin(ek)
        val totalClockBiasMeters = clockBiasMeters + relativity * Constants.SPEED_OF_LIGHT

        return SatellitePosition(
            svid = ephemeris.svid,
            xEcef = xRot,
            yEcef = yRot,
            zEcef = z,
            clockBiasMeters = totalClockBiasMeters,
            elevationDeg = 0.0,  // 需要接收机位置后计算
            azimuthDeg = 0.0,
        )
    }

    /**
     * 计算卫星仰角和方位角
     * @param satPos 卫星 ECEF 坐标
     * @param receiverPos 接收机 LLA 坐标
     */
    fun calculateElevationAzimuth(
        satPos: SatellitePosition,
        receiverPos: CoordinateUtils.LlaCoord
    ): SatellitePosition {
        val receiverEcef = CoordinateUtils.llaToEcef(receiverPos)

        // 接收机到卫星的向量
        val dx = satPos.xEcef - receiverEcef.x
        val dy = satPos.yEcef - receiverEcef.y
        val dz = satPos.zEcef - receiverEcef.z

        // 转换到 ENU 坐标系
        val enu = CoordinateUtils.ecefToEnu(dx, dy, dz, receiverPos.latitudeDeg, receiverPos.longitudeDeg)

        // 计算仰角和方位角
        val horizDist = sqrt(enu.east * enu.east + enu.north * enu.north)
        val elevationDeg = atan2(enu.up, horizDist) * Constants.RAD_TO_DEG
        val azimuthDeg = (atan2(enu.east, enu.north) * Constants.RAD_TO_DEG + 360) % 360

        return satPos.copy(
            elevationDeg = elevationDeg,
            azimuthDeg = azimuthDeg,
        )
    }

    /**
     * 计算 Klobuchar 电离层延迟
     * @param ionoParams 电离层参数
     * @param userLatDeg 用户纬度（度）
     * @param userLonDeg 用户经度（度）
     * @param elevationDeg 卫星仰角（度）
     * @param azimuthDeg 卫星方位角（度）
     * @param gpsTowSeconds GPS 周内秒
     * @return 电离层延迟（米）
     */
    fun calculateIonosphereDelay(
        ionoParams: IonosphereParameters,
        userLatDeg: Double,
        userLonDeg: Double,
        elevationDeg: Double,
        azimuthDeg: Double,
        gpsTowSeconds: Double
    ): Double {
        val lat = userLatDeg * Constants.DEG_TO_RAD
        val lon = userLonDeg * Constants.DEG_TO_RAD
        val elev = elevationDeg * Constants.DEG_TO_RAD
        val azim = azimuthDeg * Constants.DEG_TO_RAD

        // 电离层穿刺点纬度
        val psi = 0.0137 / (elev / Constants.PI + 0.11) - 0.022
        val latI = lat + psi * cos(azim)
        val latIClamp = latI.coerceIn(-1.57, 1.57)  // ±90°

        // 电离层穿刺点经度
        val lonI = lon + psi * sin(azim) / cos(latIClamp)

        // 地磁纬度
        val latM = latIClamp + 0.064 * cos(lonI - 1.617)

        // 地方时
        var localTime = gpsTowSeconds / 3600.0 + lonI * 43200.0 / Constants.PI
        localTime = localTime % 86400.0
        if (localTime < 0) localTime += 86400.0

        // 电离层延迟（秒）
        val alpha = ionoParams
        val slatM = sin(latM)
        val ionoF = 1.0 + 16.0 * (0.53 - elev / Constants.PI).pow(3)

        var ionoT = 5e-9 + alpha.alpha0 * slatM +
                (alpha.alpha1 * slatM + alpha.alpha2 * slatM * slatM + alpha.alpha3 * slatM * slatM * slatM) *
                cos(2 * Constants.PI * (localTime - 50400) / alpha.beta0.coerceAtLeast(1.0))

        // 确保非负
        ionoT = max(5e-9, ionoT)

        return ionoT * Constants.SPEED_OF_LIGHT * ionoF  // 转换为米
    }

    /**
     * 计算对流层延迟（Saastamoinen 模型）
     * @param elevationDeg 卫星仰角（度）
     * @param altitudeMeters 用户海拔（米）
     * @param userLatDeg 用户纬度（度）
     * @return 对流层延迟（米）
     */
    fun calculateTroposphereDelay(
        elevationDeg: Double,
        altitudeMeters: Double,
        userLatDeg: Double = 45.0
    ): Double {
        // 简化的 Saastamoinen 模型
        // 标准大气参数
        val pressure = 1013.25 * (1 - 2.2557e-5 * altitudeMeters).pow(5.2568)  // hPa

        val elevRad = elevationDeg * Constants.DEG_TO_RAD
        val sinElev = sin(elevRad)
        val userLatRad = userLatDeg * Constants.DEG_TO_RAD

        // 对流层延迟
        val zenithDelay = 0.0022768 * pressure / (1 - 0.00266 * cos(2 * userLatRad) - 0.00028 * altitudeMeters / 1000)

        // 映射函数（简单形式）
        val mappingFunction = 1.0 / (sinElev + 0.00143 / (tan(elevRad) + 0.0445))

        return zenithDelay * mappingFunction
    }
}
