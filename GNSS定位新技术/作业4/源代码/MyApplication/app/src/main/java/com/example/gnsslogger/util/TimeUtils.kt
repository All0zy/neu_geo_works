package com.example.gnsslogger.util

import com.example.gnsslogger.util.Constants.GPS_EPOCH
import com.example.gnsslogger.util.Constants.GPS_WEEK_SECONDS

/**
 * GNSS 时间系统转换工具
 */
object TimeUtils {

    /**
     * GPS 周内纳秒转换为 Unix 时间戳（毫秒）
     */
    fun gpsTimeToUnixTimeMillis(gpsWeek: Int, gpsTowNanos: Long): Long {
        val towSeconds = gpsTowNanos / 1.0e9
        val unixSeconds = gpsWeek * GPS_WEEK_SECONDS + towSeconds + GPS_EPOCH
        return (unixSeconds * 1000).toLong()
    }

    /**
     * 从 GnssClock 的 fullBiasNanos 和 biasNanos 计算 GPS 周和周内秒
     * 返回 Pair(gpsWeek, gpsTowSeconds)
     */
    fun gnssClockToGpsTime(fullBiasNanos: Long, biasNanos: Double, timeNanos: Long): Pair<Int, Double> {
        // 接收机时间（纳秒）
        val rxTimeNanos = timeNanos - fullBiasNanos - biasNanos
        // GPS 周
        val gpsWeek = (rxTimeNanos / (GPS_WEEK_SECONDS * 1e9)).toInt()
        // GPS 周内秒
        val gpsTowNanos = rxTimeNanos - gpsWeek * GPS_WEEK_SECONDS * 1e9
        val gpsTowSeconds = gpsTowNanos / 1e9
        return Pair(gpsWeek, gpsTowSeconds)
    }

    /**
     * 计算 GPS 周内纳秒
     */
    fun gpsWeekAndTowToNanos(gpsWeek: Int, gpsTowSeconds: Double): Long {
        return ((gpsWeek * GPS_WEEK_SECONDS + gpsTowSeconds) * 1e9).toLong()
    }

    /**
     * Unix 时间戳转换为 GPS 周和周内秒
     */
    fun unixTimeMillisToGpsTime(unixTimeMillis: Long): Pair<Int, Double> {
        val unixSeconds = unixTimeMillis / 1000.0
        val gpsSeconds = unixSeconds - GPS_EPOCH
        val gpsWeek = (gpsSeconds / GPS_WEEK_SECONDS).toInt()
        val gpsTow = gpsSeconds - gpsWeek * GPS_WEEK_SECONDS
        return Pair(gpsWeek, gpsTow)
    }

    /**
     * 格式化 GPS 时间为可读字符串
     */
    fun formatGpsTime(gpsWeek: Int, gpsTowSeconds: Double): String {
        val day = (gpsTowSeconds / 86400).toInt()
        val hour = ((gpsTowSeconds % 86400) / 3600).toInt()
        val minute = ((gpsTowSeconds % 3600) / 60).toInt()
        val second = (gpsTowSeconds % 60)
        return "W$gpsWeek D$day %02d:%02d:%06.3f".format(hour, minute, second)
    }

    /**
     * 计算两个 GPS 时间之间的差值（秒）
     */
    fun gpsTimeDifferenceSeconds(
        week1: Int, tow1: Double,
        week2: Int, tow2: Double
    ): Double {
        return (week1 - week2) * GPS_WEEK_SECONDS + (tow1 - tow2)
    }

    /**
     * 判断 ADR（累积变化量）状态是否有效
     */
    fun isAdrStateValid(adrState: Int): Boolean {
        // ADR_STATE_VALID = 1
        return (adrState and 0x1) != 0
    }

    /**
     * 判断 ADR 是否重置
     */
    fun isAdrStateReset(adrState: Int): Boolean {
        // ADR_STATE_RESET = 2
        return (adrState and 0x2) != 0
    }

    /**
     * 判断是否存在周跳
     */
    fun isAdrStateCycleSlip(adrState: Int): Boolean {
        // ADR_STATE_CYCLE_SLIP = 4
        return (adrState and 0x4) != 0
    }
}
