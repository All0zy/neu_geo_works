package com.example.gnsslogger.util

import com.example.gnsslogger.util.Constants.DEG_TO_RAD
import com.example.gnsslogger.util.Constants.EARTH_ECCENTRICITY_SQ
import com.example.gnsslogger.util.Constants.EARTH_SEMI_MAJOR_AXIS
import com.example.gnsslogger.util.Constants.RAD_TO_DEG
import kotlin.math.*

/**
 * 坐标转换工具
 * ECEF（地心地固坐标系）↔ LLA（经纬度高程）↔ ENU（东北天坐标系）
 */
object CoordinateUtils {

    data class LlaCoord(val latitudeDeg: Double, val longitudeDeg: Double, val altitudeMeters: Double)
    data class EcefCoord(val x: Double, val y: Double, val z: Double)
    data class EnuCoord(val east: Double, val north: Double, val up: Double)

    /**
     * ECEF → LLA（经纬度高程）
     * 使用 Bowring 迭代法
     */
    fun ecefToLla(ecef: EcefCoord): LlaCoord {
        val x = ecef.x
        val y = ecef.y
        val z = ecef.z

        val a = EARTH_SEMI_MAJOR_AXIS
        val e2 = EARTH_ECCENTRICITY_SQ
        val b = a * sqrt(1 - e2)

        val p = sqrt(x * x + y * y)
        val theta = atan2(z * a, p * b)

        val lon = atan2(y, x)
        val lat = atan2(
            z + e2 / (1 - e2) * b * sin(theta).pow(3),
            p - e2 * a * cos(theta).pow(3)
        )

        val sinLat = sin(lat)
        val cosLat = cos(lat)
        val N = a / sqrt(1 - e2 * sinLat * sinLat)

        val alt = p / cosLat - N

        return LlaCoord(
            latitudeDeg = lat * RAD_TO_DEG,
            longitudeDeg = lon * RAD_TO_DEG,
            altitudeMeters = alt
        )
    }

    /**
     * LLA → ECEF
     */
    fun llaToEcef(lla: LlaCoord): EcefCoord {
        val lat = lla.latitudeDeg * DEG_TO_RAD
        val lon = lla.longitudeDeg * DEG_TO_RAD
        val alt = lla.altitudeMeters

        val sinLat = sin(lat)
        val cosLat = cos(lat)
        val sinLon = sin(lon)
        val cosLon = cos(lon)

        val N = EARTH_SEMI_MAJOR_AXIS / sqrt(1 - EARTH_ECCENTRICITY_SQ * sinLat * sinLat)

        val x = (N + alt) * cosLat * cosLon
        val y = (N + alt) * cosLat * sinLon
        val z = (N * (1 - EARTH_ECCENTRICITY_SQ) + alt) * sinLat

        return EcefCoord(x, y, z)
    }

    /**
     * ECEF 坐标差 → ENU 坐标差
     * @param refLatDeg 参考点纬度（度）
     * @param refLonDeg 参考点经度（度）
     */
    fun ecefToEnu(
        dx: Double, dy: Double, dz: Double,
        refLatDeg: Double, refLonDeg: Double
    ): EnuCoord {
        val lat = refLatDeg * DEG_TO_RAD
        val lon = refLonDeg * DEG_TO_RAD

        val sinLat = sin(lat)
        val cosLat = cos(lat)
        val sinLon = sin(lon)
        val cosLon = cos(lon)

        val east = -sinLon * dx + cosLon * dy
        val north = -sinLat * cosLon * dx - sinLat * sinLon * dy + cosLat * dz
        val up = cosLat * cosLon * dx + cosLat * sinLon * dy + sinLat * dz

        return EnuCoord(east, north, up)
    }

    /**
     * ENU 坐标差 → ECEF 坐标差
     */
    fun enuToEcef(
        east: Double, north: Double, up: Double,
        refLatDeg: Double, refLonDeg: Double
    ): EcefCoord {
        val lat = refLatDeg * DEG_TO_RAD
        val lon = refLonDeg * DEG_TO_RAD

        val sinLat = sin(lat)
        val cosLat = cos(lat)
        val sinLon = sin(lon)
        val cosLon = cos(lon)

        val dx = -sinLon * east - sinLat * cosLon * north + cosLat * cosLon * up
        val dy = cosLon * east - sinLat * sinLon * north + cosLat * sinLon * up
        val dz = cosLat * north + sinLat * up

        return EcefCoord(dx, dy, dz)
    }

    /**
     * 计算两个 LLA 坐标之间的距离（米）
     * 使用 Haversine 公式
     */
    fun distanceBetween(
        lat1: Double, lon1: Double,
        lat2: Double, lon2: Double
    ): Double {
        val dLat = (lat2 - lat1) * DEG_TO_RAD
        val dLon = (lon2 - lon1) * DEG_TO_RAD
        val a = sin(dLat / 2).pow(2) +
                cos(lat1 * DEG_TO_RAD) * cos(lat2 * DEG_TO_RAD) * sin(dLon / 2).pow(2)
        val c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return Constants.EARTH_RADIUS * c
    }

    /**
     * 计算方位角（度）
     */
    fun bearingBetween(
        lat1: Double, lon1: Double,
        lat2: Double, lon2: Double
    ): Double {
        val lat1Rad = lat1 * DEG_TO_RAD
        val lat2Rad = lat2 * DEG_TO_RAD
        val dLon = (lon2 - lon1) * DEG_TO_RAD

        val y = sin(dLon) * cos(lat2Rad)
        val x = cos(lat1Rad) * sin(lat2Rad) - sin(lat1Rad) * cos(lat2Rad) * cos(dLon)
        val bearing = atan2(y, x) * RAD_TO_DEG
        return (bearing + 360) % 360
    }
}
