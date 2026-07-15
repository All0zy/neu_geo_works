package com.example.gnsslogger.log

import android.content.Context
import android.util.Log
import com.example.gnsslogger.data.model.PositionResult
import com.example.gnsslogger.data.model.RawMeasurement
import com.example.gnsslogger.gnss.GnssClockHandler
import com.example.gnsslogger.gnss.GnssMeasurementManager
import java.io.BufferedWriter
import java.io.File
import java.io.FileWriter
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.*

/**
 * CSV 格式日志记录器
 * 兼容 Google GnssLoggerApp 输出格式
 * 参考：https://github.com/google/gps-measurement-tools
 */
class CsvLogger(private val context: Context) {
    companion object {
        private const val TAG = "CsvLogger"
        private const val CSV_VERSION = "2.41"
        private const val HEADER_COMMENT = "# Raw GNSS Measurements Log"
    }

    private var writer: BufferedWriter? = null
    private var currentFile: File? = null
    private var isLogging = false
    private var measurementCount = 0

    private val dateFormat = SimpleDateFormat("yyyy-MM-dd_HH-mm-ss", Locale.US)

    /**
     * 开始新的日志文件
     */
    fun startLogging(): File? {
        if (isLogging) {
            Log.w(TAG, "Already logging, stop first")
            return currentFile
        }

        try {
            val dir = File(context.getExternalFilesDir(null), "gnss_logs")
            if (!dir.exists()) dir.mkdirs()

            val fileName = "gnss_log_${dateFormat.format(Date())}.csv"
            val file = File(dir, fileName)

            writer = BufferedWriter(FileWriter(file))
            currentFile = file
            isLogging = true
            measurementCount = 0

            // 写入头部信息
            writeHeader()

            Log.i(TAG, "Started logging to ${file.absolutePath}")
            return file
        } catch (e: IOException) {
            Log.e(TAG, "Failed to start logging", e)
            return null
        }
    }

    /**
     * 停止日志记录
     */
    fun stopLogging() {
        if (!isLogging) return

        try {
            writer?.flush()
            writer?.close()
            Log.i(TAG, "Stopped logging. $measurementCount measurements recorded")
        } catch (e: IOException) {
            Log.e(TAG, "Error stopping logger", e)
        } finally {
            writer = null
            isLogging = false
        }
    }

    /**
     * 是否正在记录
     */
    fun isLoggingActive(): Boolean = isLogging

    /**
     * 获取当前日志文件
     */
    fun getCurrentFile(): File? = currentFile

    /**
     * 获取记录的测量数
     */
    fun getMeasurementCount(): Int = measurementCount

    /**
     * 写入头部信息
     */
    private fun writeHeader() {
        writer?.apply {
            write(HEADER_COMMENT)
            newLine()
            write("Version,$CSV_VERSION")
            newLine()
            write("ApplicationName,GNSSLogger")
            newLine()
            write("DeviceModel,${android.os.Build.MODEL}")
            newLine()
            write("AndroidVersion,${android.os.Build.VERSION.RELEASE}")
            newLine()
            write("StartTimestampMillis,${System.currentTimeMillis()}")
            newLine()
            newLine()
            // Fix 头
            write("Fix,Provider,Latitude,Longitude,Altitude,Speed,Bearing,Accuracy,UnixTimeMillis")
            newLine()
            // Raw 头
            write("Raw,TimeNanos,TimeOffsetNanos,ReceivedSvTimeNanos,ReceivedSvTimeUncertaintyNanos," +
                    "State,Svid,ConstellationType,Cn0DbHz," +
                    "PseudorangeRateMetersPerSecond,PseudorangeRateUncertaintyMetersPerSecond," +
                    "AccumulatedDeltaRangeState,AccumulatedDeltaRangeMeters," +
                    "AccumulatedDeltaRangeUncertaintyMeters,CarrierFrequencyHz,CodeType," +
                    "MultipathIndicator,SnrInDb,BasebandCn0DbHz," +
                    "FullInterSignalBiasNanos,SatelliteInterSignalBiasNanos," +
                    "PseudorangeMeters")
            newLine()
            // Clock 头
            write("Clock,TimeNanos,FullBiasNanos,BiasNanos,BiasUncertaintyNanos," +
                    "DriftNanosPerSecond,DriftUncertaintyNanosPerSecond," +
                    "HardwareClockDiscontinuityCount,LeapSecond")
            newLine()
            flush()
        }
    }

    /**
     * 记录 GNSS 测量数据
     */
    fun logMeasurements(
        measurements: List<RawMeasurement>,
        clockInfo: GnssMeasurementManager.GnssClockInfo
    ) {
        if (!isLogging) return

        try {
            // 写入 Clock 行
            writer?.apply {
                write("Clock,${clockInfo.timeNanos}," +
                        "${clockInfo.fullBiasNanos ?: ""}," +
                        "${clockInfo.biasNanos ?: ""}," +
                        "${clockInfo.biasUncertaintyNanos ?: ""}," +
                        "${clockInfo.driftNanosPerSecond ?: ""}," +
                        "${clockInfo.driftUncertaintyNanosPerSecond ?: ""}," +
                        "${clockInfo.hardwareClockDiscontinuityCount}," +
                        "${clockInfo.leapSecond ?: ""}")
                newLine()
            }

            // 写入 Raw 行
            for (m in measurements) {
                writer?.apply {
                    write("Raw,${m.timeNanos}," +
                            "${m.timeOffsetNanos}," +
                            "${m.receivedSvTimeNanos}," +
                            "${m.receivedSvTimeUncertaintyNanos}," +
                            "${m.state}," +
                            "${m.svid}," +
                            "${m.constellationType}," +
                            "${m.cn0DbHz}," +
                            "${m.pseudorangeRateMetersPerSecond}," +
                            "${m.pseudorangeRateUncertaintyMetersPerSecond}," +
                            "${m.accumulatedDeltaRangeState}," +
                            "${m.accumulatedDeltaRangeMeters}," +
                            "${m.accumulatedDeltaRangeUncertaintyMeters}," +
                            "${m.carrierFrequencyHz}," +
                            "${m.codeType}," +
                            "${m.multipathIndicator}," +
                            "${m.snrInDb}," +
                            "${m.basebandCn0DbHz}," +
                            "${m.fullInterSignalBiasNanos}," +
                            "${m.satelliteInterSignalBiasNanos}," +
                            "${m.pseudorangeMeters}")
                    newLine()
                }
                measurementCount++
            }

            writer?.flush()
        } catch (e: IOException) {
            Log.e(TAG, "Error writing measurements", e)
        }
    }

    /**
     * 记录定位结果
     */
    fun logFix(position: PositionResult) {
        if (!isLogging) return

        try {
            writer?.apply {
                write("Fix,Fused," +
                        "${position.latitudeDeg}," +
                        "${position.longitudeDeg}," +
                        "${position.altitudeMeters}," +
                        "${position.speedMps}," +
                        "${position.bearingDeg}," +
                        "${position.accuracyMeters}," +
                        "${position.timestampMs}")
                newLine()
                flush()
            }
        } catch (e: IOException) {
            Log.e(TAG, "Error writing fix", e)
        }
    }

    /**
     * 写入自定义注释行
     */
    fun logComment(comment: String) {
        if (!isLogging) return
        try {
            writer?.apply {
                write("# $comment")
                newLine()
                flush()
            }
        } catch (e: IOException) {
            Log.e(TAG, "Error writing comment", e)
        }
    }
}
