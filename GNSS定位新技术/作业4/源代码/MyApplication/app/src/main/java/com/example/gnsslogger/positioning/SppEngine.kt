package com.example.gnsslogger.positioning

import android.util.Log
import com.example.gnsslogger.data.model.*
import com.example.gnsslogger.util.Constants
import com.example.gnsslogger.util.CoordinateUtils
import kotlin.math.*

/**
 * 单点定位引擎（SPP）
 */
class SppEngine {
    companion object {
        private const val TAG = "SppEngine"
    }

    private val satPositionCalc = SatellitePositionCalc()
    private val leastSquaresSolver = LeastSquaresSolver()

    private var lastLla: CoordinateUtils.LlaCoord? = null
    private var systemLla: CoordinateUtils.LlaCoord? = null

    /**
     * 设置初始位置（来自系统 GPS）
     */
    fun setInitialPosition(lla: CoordinateUtils.LlaCoord) {
        lastLla = lla
        systemLla = lla
        Log.d(TAG, "设置初始位置: ${lla.latitudeDeg}, ${lla.longitudeDeg}")
    }

    /**
     * 执行定位
     */
    fun solve(
        measurements: List<RawMeasurement>,
        ephemerisMap: Map<Int, GpsEphemeris>,
        satellites: List<SatelliteInfo>,
        gpsWeek: Int,
        gpsTowSeconds: Double
    ): PositionResult? {
        Log.d(TAG, "solve: ${measurements.size} 测量, ${ephemerisMap.size} 星历, ${satellites.size} 卫星")

        // 方案1: 星历定位（只有 4 颗以上有效卫星才尝试）
        if (ephemerisMap.size >= 4) {
            val result = solveWithEphemeris(measurements, ephemerisMap, satellites, gpsWeek, gpsTowSeconds)
            if (result != null) {
                Log.i(TAG, ">>> 星历定位成功: %.6f, %.6f 精度=%.1fm".format(
                    result.latitudeDeg, result.longitudeDeg, result.accuracyMeters))
                return result
            }
        }

        // 方案2: 简化的加权质心法（必须要有系统 GPS 锚定）
        val sysLla = systemLla ?: return null
        val result = solveWithSatelliteInfo(measurements, satellites, sysLla)
        if (result != null) {
            Log.i(TAG, ">>> 简化定位: %.6f, %.6f 精度=%.1fm".format(
                result.latitudeDeg, result.longitudeDeg, result.accuracyMeters))
            return result
        }

        return null
    }

    /**
     * 星历定位
     */
    private fun solveWithEphemeris(
        measurements: List<RawMeasurement>,
        ephemerisMap: Map<Int, GpsEphemeris>,
        satellites: List<SatelliteInfo>,
        gpsWeek: Int,
        gpsTowSeconds: Double
    ): PositionResult? {
        val satDataList = mutableListOf<LeastSquaresSolver.SatelliteData>()
        val satMap = satellites.associateBy { it.svid }

        for (m in measurements) {
            if (m.pseudorangeMeters <= 0) continue

            val eph = ephemerisMap[m.svid] ?: continue
            val prSec = m.pseudorangeMeters / Constants.SPEED_OF_LIGHT
            val txTime = gpsTowSeconds - prSec

            try {
                var satPos = satPositionCalc.calculateSatellitePosition(eph, txTime)

                lastLla?.let {
                    satPos = satPositionCalc.calculateElevationAzimuth(satPos, it)
                    if (satPos.elevationDeg < 5.0) continue
                }

                satDataList.add(LeastSquaresSolver.SatelliteData(
                    svid = m.svid,
                    x = satPos.xEcef,
                    y = satPos.yEcef,
                    z = satPos.zEcef,
                    pseudorange = m.pseudorangeMeters,
                    clockBiasMeters = satPos.clockBiasMeters,
                    weight = 1.0,
                ))
            } catch (e: Exception) {
                Log.w(TAG, "卫星 ${m.svid} 计算失败: ${e.message}")
            }
        }

        if (satDataList.size < 4) return null

        val initPos = (lastLla ?: systemLla)?.let {
            val ecef = CoordinateUtils.llaToEcef(it)
            Triple(ecef.x, ecef.y, ecef.z)
        } ?: Triple(0.0, 0.0, 0.0)

        val solution = leastSquaresSolver.solve(satDataList, initPos) ?: return null

        val coord = CoordinateUtils.EcefCoord(solution.x, solution.y, solution.z)
        val lla = CoordinateUtils.ecefToLla(coord)

        if (lla.latitudeDeg !in -90.0..90.0 || lla.longitudeDeg !in -180.0..180.0) return null

        // 避免 SPP 结果远离系统 GPS 锚定
        val anchor = systemLla ?: return null
        val de = CoordinateUtils.distanceBetween(anchor.latitudeDeg, anchor.longitudeDeg, lla.latitudeDeg, lla.longitudeDeg)
        if (de > 2000.0) {
            Log.w(TAG, "SPP 偏离系统 GPS %.0fm，丢弃".format(de))
            return null
        }

        lastLla = lla
        return buildResult(lla, solution, satDataList.size, satellites.size)
    }

    /**
     * 简化定位：基于伪距偏差的加权质心法（锚定系统 GPS 位置）
     */
    private fun solveWithSatelliteInfo(
        measurements: List<RawMeasurement>,
        satellites: List<SatelliteInfo>,
        anchor: CoordinateUtils.LlaCoord
    ): PositionResult? {
        val satMap = satellites.associateBy { it.svid }
        val validMeasurements = measurements.filter { it.pseudorangeMeters > 0 }

        val withDirection = validMeasurements.mapNotNull { m ->
            val sat = satMap[m.svid]
            if (sat != null && sat.elevationDeg > 0) Pair(m, sat) else null
        }

        if (withDirection.size < 4) return null

        val refLat = anchor.latitudeDeg
        val refLon = anchor.longitudeDeg
        val refLatRad = refLat * Constants.DEG_TO_RAD

        var sumLat = 0.0
        var sumLon = 0.0
        var sumWeight = 0.0
        val metersPerDeg = 111320.0

        for ((m, sat) in withDirection) {
            val elevRad = sat.elevationDeg * Constants.DEG_TO_RAD
            val azimRad = sat.azimuthDeg * Constants.DEG_TO_RAD

            val prNominal = 22000000.0
            val prBias = (m.pseudorangeMeters - prNominal) / 1000000.0
            val weight = sin(elevRad) * (m.cn0DbHz / 40.0)

            val latOffset = -prBias * cos(azimRad) * 0.001
            val lonOffset = -prBias * sin(azimRad) * 0.001 / cos(refLatRad)

            sumLat += latOffset * weight
            sumLon += lonOffset * weight
            sumWeight += weight
        }

        if (sumWeight == 0.0) return null

        val estLat = refLat + sumLat / sumWeight
        val estLon = refLon + sumLon / sumWeight

        if (estLat !in -90.0..90.0 || estLon !in -180.0..180.0) return null

        // 精度估算：伪距一致性 + 锚定偏差
        // 1) 伪距残差一致性（去除公共钟差后衡量测量噪声）
        val allPr = withDirection.map { it.first.pseudorangeMeters }
        val meanPr = allPr.average()
        val rmsResidual = sqrt(allPr.sumOf { (it - meanPr).pow(2) } / allPr.size)
        val noiseEstimate = rmsResidual / sqrt(withDirection.size.toDouble())

        // 2) 锚定偏差：位置偏离系统 GPS 的距离
        val dLat = (estLat - refLat) * metersPerDeg
        val dLon = (estLon - refLon) * metersPerDeg * cos(refLatRad)
        val distanceFromAnchor = sqrt(dLat * dLat + dLon * dLon)

        val accuracy = maxOf(noiseEstimate, distanceFromAnchor / 2.0, 8.0).coerceAtMost(200.0)

        // 从卫星仰角/方位角计算近似 DOP（无需星历）
        val eastArr = DoubleArray(withDirection.size)
        val northArr = DoubleArray(withDirection.size)
        val upArr = DoubleArray(withDirection.size)
        for (i in withDirection.indices) {
            val el = withDirection[i].second.elevationDeg * Constants.DEG_TO_RAD
            val az = withDirection[i].second.azimuthDeg * Constants.DEG_TO_RAD
            eastArr[i] = cos(el) * sin(az)
            northArr[i] = cos(el) * cos(az)
            upArr[i] = sin(el)
        }
        val dop = LeastSquaresSolver.computeDopFromEnuDirections(eastArr, northArr, upArr)

        return PositionResult(
            latitudeDeg = estLat,
            longitudeDeg = estLon,
            altitudeMeters = 0.0,
            accuracyMeters = accuracy,
            speedMps = 0.0,
            bearingDeg = 0.0,
            timestampMs = System.currentTimeMillis(),
            gdop = dop.gdop,
            pdop = dop.pdop,
            hdop = dop.hdop,
            vdop = dop.vdop,
            tdop = dop.tdop,
            satellitesUsed = withDirection.size,
            satellitesVisible = satellites.size,
            velocityEast = 0.0,
            velocityNorth = 0.0,
            velocityUp = 0.0,
            xEcef = 0.0,
            yEcef = 0.0,
            zEcef = 0.0,
            receiverClockBiasMeters = 0.0,
        )
    }

    private fun buildResult(
        lla: CoordinateUtils.LlaCoord,
        solution: LeastSquaresSolver.Solution,
        used: Int,
        visible: Int
    ): PositionResult {
        // 从残差 RMS 估算实际精度
        val residualRms = if (solution.residuals.isNotEmpty()) {
            sqrt(solution.residuals.sumOf { it * it } / solution.residuals.size)
        } else {
            10.0
        }
        val accuracy = maxOf(solution.hdop * 5.0, residualRms * 2.0).coerceIn(5.0, 200.0)

        return PositionResult(
            latitudeDeg = lla.latitudeDeg,
            longitudeDeg = lla.longitudeDeg,
            altitudeMeters = lla.altitudeMeters,
            accuracyMeters = accuracy,
            speedMps = 0.0,
            bearingDeg = 0.0,
            timestampMs = System.currentTimeMillis(),
            gdop = solution.gdop,
            pdop = solution.pdop,
            hdop = solution.hdop,
            vdop = solution.vdop,
            tdop = solution.tdop,
            satellitesUsed = used,
            satellitesVisible = visible,
            velocityEast = 0.0,
            velocityNorth = 0.0,
            velocityUp = 0.0,
            xEcef = solution.x,
            yEcef = solution.y,
            zEcef = solution.z,
            receiverClockBiasMeters = solution.clockBiasMeters,
        )
    }

    fun reset() {
        lastLla = null
        systemLla = null
    }
}
