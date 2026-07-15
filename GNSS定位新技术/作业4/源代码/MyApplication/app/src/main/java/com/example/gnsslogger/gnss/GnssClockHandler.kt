package com.example.gnsslogger.gnss

import android.location.GnssClock
import com.example.gnsslogger.util.Constants
import com.example.gnsslogger.util.TimeUtils

/**
 * GNSS 时钟信息处理器
 * 负责解析和管理 GNSS 时钟状态
 */
class GnssClockHandler {

    /**
     * 时钟状态信息
     */
    data class ClockState(
        val timeNanos: Long,
        val fullBiasNanos: Long?,
        val biasNanos: Double?,
        val biasUncertaintyNanos: Double?,
        val driftNanosPerSecond: Double?,
        val driftUncertaintyNanosPerSecond: Double?,
        val leapSecond: Int?,
        val hardwareClockDiscontinuityCount: Int,
        val gpsWeek: Int?,
        val gpsTowSeconds: Double?,
        val timeUncertaintyNanos: Double?,
    ) {
        val isValid: Boolean
            get() = fullBiasNanos != null && timeNanos > 0

        val receiverClockBiasMeters: Double
            get() {
                val bias = (fullBiasNanos ?: 0).toDouble() + (biasNanos ?: 0.0)
                return bias * Constants.SPEED_OF_LIGHT / 1e9
            }
    }

    private var lastClockState: ClockState? = null
    private var discontinuityCount = 0

    /**
     * 从 GnssClock 提取时钟状态
     */
    fun extractClockState(clock: GnssClock): ClockState {
        val fullBias = if (clock.hasFullBiasNanos()) clock.fullBiasNanos else null
        val bias = if (clock.hasBiasNanos()) clock.biasNanos else null

        // 计算 GPS 时间
        var gpsWeek: Int? = null
        var gpsTow: Double? = null
        if (fullBias != null) {
            val rxTimeNanos = clock.timeNanos - fullBias - (bias ?: 0.0)
            gpsWeek = (rxTimeNanos / (Constants.GPS_WEEK_SECONDS * 1e9)).toInt()
            gpsTow = (rxTimeNanos % (Constants.GPS_WEEK_SECONDS * 1e9)) / 1e9
        }

        val state = ClockState(
            timeNanos = clock.timeNanos,
            fullBiasNanos = fullBias,
            biasNanos = bias,
            biasUncertaintyNanos = if (clock.hasBiasUncertaintyNanos()) clock.biasUncertaintyNanos else null,
            driftNanosPerSecond = if (clock.hasDriftNanosPerSecond()) clock.driftNanosPerSecond else null,
            driftUncertaintyNanosPerSecond = if (clock.hasDriftUncertaintyNanosPerSecond()) clock.driftUncertaintyNanosPerSecond else null,
            leapSecond = if (clock.hasLeapSecond()) clock.leapSecond else null,
            hardwareClockDiscontinuityCount = clock.hardwareClockDiscontinuityCount,
            gpsWeek = gpsWeek,
            gpsTowSeconds = gpsTow,
            timeUncertaintyNanos = if (clock.hasTimeUncertaintyNanos()) clock.timeUncertaintyNanos else null,
        )

        // 检测时钟不连续
        lastClockState?.let { last ->
            if (clock.hardwareClockDiscontinuityCount != last.hardwareClockDiscontinuityCount) {
                discontinuityCount++
            }
        }

        lastClockState = state
        return state
    }

    /**
     * 获取时钟不连续次数
     */
    fun getDiscontinuityCount(): Int = discontinuityCount

    /**
     * 获取上一次有效的时钟状态
     */
    fun getLastClockState(): ClockState? = lastClockState

    /**
     * 重置状态
     */
    fun reset() {
        lastClockState = null
        discontinuityCount = 0
    }
}
