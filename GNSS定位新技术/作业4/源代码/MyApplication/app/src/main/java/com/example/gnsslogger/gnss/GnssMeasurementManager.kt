package com.example.gnsslogger.gnss

import android.location.GnssClock
import android.location.GnssMeasurement
import android.location.GnssMeasurementsEvent
import android.location.LocationManager
import android.os.Build
import android.util.Log
import com.example.gnsslogger.data.model.RawMeasurement
import com.example.gnsslogger.util.Constants
import com.example.gnsslogger.util.TimeUtils

/**
 * GNSS 原始观测量采集管理器
 * 封装 GnssMeasurementsEvent.Callback，将系统回调转换为应用数据模型
 */
class GnssMeasurementManager(
    private val locationManager: LocationManager
) {
    companion object {
        private const val TAG = "GnssMeasurementMgr"
    }

    private var callback: GnssMeasurementsEvent.Callback? = null
    private var listener: OnMeasurementsReceivedListener? = null
    private var isRegistered = false

    /**
     * 原始观测量接收回调接口
     */
    interface OnMeasurementsReceivedListener {
        fun onMeasurementsReceived(measurements: List<RawMeasurement>, clockInfo: GnssClockInfo)
    }

    /**
     * GNSS 时钟信息
     */
    data class GnssClockInfo(
        val timeNanos: Long,
        val fullBiasNanos: Long?,
        val biasNanos: Double?,
        val biasUncertaintyNanos: Double?,
        val driftNanosPerSecond: Double?,
        val driftUncertaintyNanosPerSecond: Double?,
        val hardwareClockDiscontinuityCount: Int,
        val leapSecond: Int?,
    ) {
        /**
         * 计算 GPS 周内秒
         */
        fun getGpsTowSeconds(): Double? {
            val fullBias = fullBiasNanos ?: return null
            val bias = biasNanos ?: 0.0
            val rxTimeNanos = timeNanos - fullBias - bias
            return (rxTimeNanos % (Constants.GPS_WEEK_SECONDS * 1e9)) / 1e9
        }
    }

    /**
     * 注册 GNSS 测量回调
     */
    fun register(listener: OnMeasurementsReceivedListener) {
        if (isRegistered) {
            Log.w(TAG, "Callback already registered")
            return
        }

        this.listener = listener

        callback = object : GnssMeasurementsEvent.Callback() {
            override fun onGnssMeasurementsReceived(event: GnssMeasurementsEvent) {
                processMeasurements(event)
            }

            override fun onStatusChanged(status: Int) {
                Log.d(TAG, "Measurement callback status: $status")
            }
        }

        try {
            locationManager.registerGnssMeasurementsCallback(
                { it.run() },  // executor
                callback!!
            )
            isRegistered = true
            Log.i(TAG, "GNSS measurement callback registered")
        } catch (e: SecurityException) {
            Log.e(TAG, "Security exception registering callback", e)
        }
    }

    /**
     * 注销回调
     */
    fun unregister() {
        callback?.let {
            locationManager.unregisterGnssMeasurementsCallback(it)
            callback = null
            isRegistered = false
            listener = null
            Log.i(TAG, "GNSS measurement callback unregistered")
        }
    }

    /**
     * 处理原始测量数据
     */
    private fun processMeasurements(event: GnssMeasurementsEvent) {
        val clock = event.clock
        val clockInfo = extractClockInfo(clock)

        val measurements = event.measurements.mapNotNull { measurement ->
            try {
                convertMeasurement(measurement, clock)
            } catch (e: Exception) {
                Log.w(TAG, "Failed to convert measurement for SV ${measurement.svid}", e)
                null
            }
        }

        listener?.onMeasurementsReceived(measurements, clockInfo)
    }

    /**
     * 提取时钟信息
     */
    private fun extractClockInfo(clock: GnssClock): GnssClockInfo {
        return GnssClockInfo(
            timeNanos = clock.timeNanos,
            fullBiasNanos = if (clock.hasFullBiasNanos()) clock.fullBiasNanos else null,
            biasNanos = if (clock.hasBiasNanos()) clock.biasNanos else null,
            biasUncertaintyNanos = if (clock.hasBiasUncertaintyNanos()) clock.biasUncertaintyNanos else null,
            driftNanosPerSecond = if (clock.hasDriftNanosPerSecond()) clock.driftNanosPerSecond else null,
            driftUncertaintyNanosPerSecond = if (clock.hasDriftUncertaintyNanosPerSecond()) clock.driftUncertaintyNanosPerSecond else null,
            hardwareClockDiscontinuityCount = clock.hardwareClockDiscontinuityCount,
            leapSecond = if (clock.hasLeapSecond()) clock.leapSecond else null,
        )
    }

    /**
     * 转换 GnssMeasurement 到 RawMeasurement
     */
    private fun convertMeasurement(
        measurement: GnssMeasurement,
        clock: GnssClock
    ): RawMeasurement {
        // 计算伪距
        val pseudorangeMeters = calculatePseudorange(measurement, clock)

        // 调试：记录伪距值
        if (pseudorangeMeters > 0) {
            Log.d(TAG, "SV${measurement.svid}: PR=${pseudorangeMeters}m, CN0=${measurement.cn0DbHz}dB")
        }

        return RawMeasurement(
            timeNanos = clock.timeNanos,
            timeOffsetNanos = measurement.timeOffsetNanos,
            receivedSvTimeNanos = measurement.receivedSvTimeNanos,
            receivedSvTimeUncertaintyNanos = measurement.receivedSvTimeUncertaintyNanos,
            state = measurement.state,
            svid = measurement.svid,
            constellationType = measurement.constellationType,
            cn0DbHz = measurement.cn0DbHz,
            pseudorangeRateMetersPerSecond = measurement.pseudorangeRateMetersPerSecond,
            pseudorangeRateUncertaintyMetersPerSecond = measurement.pseudorangeRateUncertaintyMetersPerSecond,
            accumulatedDeltaRangeState = measurement.accumulatedDeltaRangeState,
            accumulatedDeltaRangeMeters = measurement.accumulatedDeltaRangeMeters,
            accumulatedDeltaRangeUncertaintyMeters = measurement.accumulatedDeltaRangeUncertaintyMeters,
            carrierFrequencyHz = measurement.carrierFrequencyHz,
            codeType = measurement.codeType,
            multipathIndicator = measurement.multipathIndicator,
            snrInDb = measurement.snrInDb,
            basebandCn0DbHz = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) measurement.basebandCn0DbHz else 0.0,
            fullInterSignalBiasNanos = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) measurement.fullInterSignalBiasNanos else 0.0,
            satelliteInterSignalBiasNanos = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) measurement.satelliteInterSignalBiasNanos else 0.0,
            pseudorangeMeters = pseudorangeMeters,
        )
    }

    /**
     * 计算伪距
     */
    private fun calculatePseudorange(
        measurement: GnssMeasurement,
        clock: GnssClock
    ): Double {
        // 检查时钟数据
        if (!clock.hasFullBiasNanos()) {
            if (measurement.svid <= 3) {
                Log.w(TAG, "SV${measurement.svid}: 没有 fullBiasNanos")
            }
            return 0.0
        }

        // 接收机 GPS 时间（纳秒，自 GPS 纪元 1980-01-06）
        val fullBias = clock.fullBiasNanos
        val bias = if (clock.hasBiasNanos()) clock.biasNanos else 0.0
        val timeNanos = clock.timeNanos
        val rxTimeNanos = timeNanos - fullBias - bias

        // 卫星时间
        val svTime = measurement.receivedSvTimeNanos
        val timeOffset = measurement.timeOffsetNanos

        // rxTimeNanos 是完整 GPS 时间（~10^18 ns），receivedSvTimeNanos 是周期内时间
        // 按星座取模对齐到同一周期
        val periodNanos = when (measurement.constellationType) {
            Constants.CONSTELLATION_GLONASS -> (86400.0 * 1e9).toLong()   // GLONASS 一天
            else -> (Constants.GPS_WEEK_SECONDS * 1e9).toLong()           // GPS/北斗/伽利略一周
        }

        var pseudorangeNanos = (rxTimeNanos - svTime - timeOffset) % periodNanos
        if (pseudorangeNanos < 0) pseudorangeNanos += periodNanos

        val pseudorangeMeters = pseudorangeNanos * Constants.SPEED_OF_LIGHT / 1e9

        if (measurement.svid <= 3) {
            Log.d(TAG, "SV${measurement.svid}: rxTimeNanos=$rxTimeNanos, svTime=$svTime, " +
                    "PR=${"%.1f".format(pseudorangeMeters)}m")
        }

        return if (pseudorangeMeters > 0 && pseudorangeMeters < 100000000) {
            pseudorangeMeters
        } else {
            0.0
        }
    }

    /**
     * 获取星座名称
     */
    fun getConstellationName(constellationType: Int): String {
        return when (constellationType) {
            Constants.CONSTELLATION_GPS -> "GPS"
            Constants.CONSTELLATION_GLONASS -> "GLONASS"
            Constants.CONSTELLATION_BDS -> "BDS"
            Constants.CONSTELLATION_GALILEO -> "GALILEO"
            Constants.CONSTELLATION_QZSS -> "QZSS"
            Constants.CONSTELLATION_SBAS -> "SBAS"
            Constants.CONSTELLATION_IRNSS -> "IRNSS"
            else -> "Unknown"
        }
    }
}
