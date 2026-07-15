package com.example.gnsslogger.gnss

import android.location.GnssNavigationMessage
import android.location.LocationManager
import android.util.Log
import com.example.gnsslogger.data.model.GlonassEphemeris
import com.example.gnsslogger.data.model.GpsEphemeris
import com.example.gnsslogger.data.model.IonosphereParameters
import com.example.gnsslogger.data.model.NavigationData

/**
 * GNSS 导航电文管理器 - 解析广播星历
 */
class GnssNavigationManager(
    private val locationManager: LocationManager
) {
    companion object {
        private const val TAG = "GnssNavMgr"
        private const val TYPE_GPS_LNAV = 1
        private const val TYPE_GLO_FDMA = 4
    }

    private var callback: GnssNavigationMessage.Callback? = null
    private var listener: OnNavigationDataListener? = null
    private var isRegistered = false

    // 存储子帧数据：svid -> [subframe1, subframe2, subframe3]
    private val subframeBuffer = mutableMapOf<Int, MutableList<IntArray>>()
    private val gpsEphemerisMap = mutableMapOf<Int, GpsEphemeris>()
    private val glonassEphemerisMap = mutableMapOf<Int, GlonassEphemeris>()
    private var ionosphereParams: IonosphereParameters? = null

    // 已解析的星历（避免重复解析）
    private val parsedSvids = mutableSetOf<Int>()

    interface OnNavigationDataListener {
        fun onNavigationDataUpdated(data: NavigationData)
    }

    fun register(listener: OnNavigationDataListener) {
        if (isRegistered) return
        this.listener = listener

        callback = object : GnssNavigationMessage.Callback() {
            override fun onGnssNavigationMessageReceived(message: GnssNavigationMessage) {
                processNavigationMessage(message)
            }

            override fun onStatusChanged(status: Int) {
                Log.d(TAG, "Nav callback status: $status")
            }
        }

        try {
            locationManager.registerGnssNavigationMessageCallback({ it.run() }, callback!!)
            isRegistered = true
            Log.i(TAG, "Navigation message callback registered")
        } catch (e: SecurityException) {
            Log.e(TAG, "Security exception", e)
        }
    }

    fun unregister() {
        callback?.let {
            locationManager.unregisterGnssNavigationMessageCallback(it)
            callback = null
            isRegistered = false
            listener = null
        }
    }

    fun getCurrentNavigationData(): NavigationData {
        return NavigationData(
            gpsEphemerisMap = gpsEphemerisMap.toMap(),
            glonassEphemerisMap = glonassEphemerisMap.toMap(),
            ionoParams = ionosphereParams
        )
    }

    private fun processNavigationMessage(message: GnssNavigationMessage) {
        when (message.type) {
            TYPE_GPS_LNAV -> processGpsLNav(message)
            TYPE_GLO_FDMA -> processGlonassNav(message)
        }
    }

    /**
     * 处理 GPS LNAV 导航电文
     * 子帧 1: 时钟参数
     * 子帧 2: 星历参数 (Crs, deltaN, M0, Cuc, e, Cus, sqrtA, toe)
     * 子帧 3: 星历参数 (Cic, Omega0, Cis, i0, Crc, omega, OmegaDot, IDOT)
     */
    private fun processGpsLNav(message: GnssNavigationMessage) {
        val svid = message.svid
        val subframeId = message.submessageId

        // 只处理子帧 1-3（星历所需）
        if (subframeId > 3) return

        val data = message.data
        if (data.size < 30) {
            Log.w(TAG, "Subframe too short: ${data.size} bytes")
            return
        }

        // 转换为 32 位整数数组（10 个字）
        val words = IntArray(10)
        for (i in 0 until 10) {
            val offset = i * 3
            if (offset + 2 < data.size) {
                words[i] = (data[offset].toInt() and 0xFF) shl 16 or
                        ((data[offset + 1].toInt() and 0xFF) shl 8) or
                        (data[offset + 2].toInt() and 0xFF)
            }
        }

        // 存储子帧
        val buffer = subframeBuffer.getOrPut(svid) { mutableListOf() }
        while (buffer.size < subframeId) {
            buffer.add(IntArray(10))
        }
        buffer[subframeId - 1] = words

        // 当收集到 3 个子帧时解析星历
        if (buffer.size >= 3 && svid !in parsedSvids) {
            try {
                parseGpsEphemeris(svid, buffer[0], buffer[1], buffer[2])
                parsedSvids.add(svid)
                Log.i(TAG, "Parsed ephemeris for GPS SV $svid, total: ${gpsEphemerisMap.size}")
                listener?.onNavigationDataUpdated(getCurrentNavigationData())
            } catch (e: Exception) {
                Log.w(TAG, "Failed to parse ephemeris for SV $svid: ${e.message}")
            }
        }
    }

    /**
     * 解析 GPS 星历参数
     * 参考: IS-GPS-200, Table 20-I, 20-II, 20-III
     */
    private fun parseGpsEphemeris(svid: Int, sf1: IntArray, sf2: IntArray, sf3: IntArray) {
        // 子帧 1: 时钟参数
        val tgd = extractSigned(sf1, 6, 8, 24).toDouble() * Math.pow(2.0, -31.0)
        val toc = extractUnsigned(sf1, 7, 8, 16).toDouble() * 16.0
        val af2 = extractSigned(sf1, 8, 8, 24).toDouble() * Math.pow(2.0, -55.0)
        val af1 = extractSigned(sf1, 9, 8, 16).toDouble() * Math.pow(2.0, -43.0)
        val af0 = extractSigned(sf1, 9, 8, 24).toDouble() * Math.pow(2.0, -31.0)

        // 子帧 2: 星历参数
        val iode = extractUnsigned(sf2, 0, 8, 8)
        val crs = extractSigned(sf2, 1, 8, 16).toDouble() * Math.pow(2.0, -5.0)
        val deltaN = extractSigned(sf2, 1, 8, 24).toDouble() * Math.pow(2.0, -43.0)
        val m0 = extractSignedDouble(sf2, 2, 3, 8, 24, 32, -31.0)
        val cuc = extractSigned(sf2, 4, 8, 16).toDouble() * Math.pow(2.0, -29.0)
        val e = extractUnsignedDouble(sf2, 4, 5, 8, 24, 32, -33.0)
        val cus = extractSigned(sf2, 6, 8, 16).toDouble() * Math.pow(2.0, -29.0)
        val sqrtA = extractUnsignedDouble(sf2, 6, 7, 8, 24, 32, -19.0)
        val toe = extractUnsigned(sf2, 8, 8, 16).toDouble() * 16.0

        // 子帧 3: 星历参数
        val cic = extractSigned(sf3, 0, 8, 16).toDouble() * Math.pow(2.0, -29.0)
        val omega0 = extractSignedDouble(sf3, 0, 1, 8, 24, 32, -31.0)
        val cis = extractSigned(sf3, 2, 8, 16).toDouble() * Math.pow(2.0, -29.0)
        val i0 = extractSignedDouble(sf3, 2, 3, 8, 24, 32, -31.0)
        val crc = extractSigned(sf3, 4, 8, 16).toDouble() * Math.pow(2.0, -5.0)
        val omega = extractSignedDouble(sf3, 4, 5, 8, 24, 32, -31.0)
        val omegaDot = extractSigned(sf3, 6, 8, 24).toDouble() * Math.pow(2.0, -43.0)
        val idot = extractSigned(sf3, 8, 8, 14).toDouble() * Math.pow(2.0, -43.0)

        gpsEphemerisMap[svid] = GpsEphemeris(
            svid = svid,
            m0 = m0,
            deltaN = deltaN,
            eccentricity = e,
            sqrtA = sqrtA,
            omega0 = omega0,
            i0 = i0,
            omega = omega,
            omegaDot = omegaDot,
            idot = idot,
            cuc = cuc,
            cus = cus,
            crc = crc,
            crs = crs,
            cic = cic,
            cis = cis,
            tgd = tgd,
            toc = toc,
            af0 = af0,
            af1 = af1,
            af2 = af2,
            toe = toe,
            iode = iode,
            iodc = 0,
            week = 0,
            tlmMessage = 0,
            fitInterval = 0
        )
    }

    /**
     * 处理 GLONASS 导航电文
     */
    private fun processGlonassNav(message: GnssNavigationMessage) {
        // GLONASS 星历解析较复杂，暂时跳过
        Log.d(TAG, "GLONASS nav SV ${message.svid}, type ${message.submessageId}")
    }

    // ========== 位提取工具 ==========

    /**
     * 从两个连续字中提取无符号值
     */
    private fun extractUnsigned(words: IntArray, wordIdx1: Int, wordIdx2: Int, startBit: Int, numBits: Int): Long {
        val w1 = words[wordIdx1].toLong() and 0xFFFFFFFFL
        val w2 = words[wordIdx2].toLong() and 0xFFFFFFFFL
        val combined = (w1 shl 24) or (w2 shr 8)
        val shift = 48 - startBit - numBits
        val mask = (1L shl numBits) - 1
        return (combined shr shift) and mask
    }

    private fun extractUnsigned(words: IntArray, wordIdx: Int, startBit: Int, numBits: Int): Int {
        val w = words[wordIdx]
        val shift = 24 - startBit - numBits + 1
        if (shift < 0 || shift >= 24) return 0
        val mask = (1 shl numBits) - 1
        return (w shr shift) and mask
    }

    private fun extractSigned(words: IntArray, wordIdx: Int, startBit: Int, numBits: Int): Int {
        val unsigned = extractUnsigned(words, wordIdx, startBit, numBits)
        return toSigned(unsigned, numBits)
    }

    /**
     * 从两个字提取有符号浮点值
     */
    private fun extractSignedDouble(words: IntArray, w1: Int, w2: Int, s1: Int, n1: Int, n2: Int, scaleExp: Double): Double {
        val v1 = extractUnsigned(words, w1, s1, n1).toLong()
        val v2 = extractUnsigned(words, w2, 1, n2).toLong()
        val combined = (v1 shl n2) or v2
        val totalBits = n1 + n2
        val signed = toSignedLong(combined, totalBits)
        return signed * pow2(scaleExp)
    }

    private fun extractUnsignedDouble(words: IntArray, w1: Int, w2: Int, s1: Int, n1: Int, n2: Int, scaleExp: Double): Double {
        val v1 = extractUnsigned(words, w1, s1, n1).toLong()
        val v2 = extractUnsigned(words, w2, 1, n2).toLong()
        val combined = (v1 shl n2) or v2
        return combined * pow2(scaleExp)
    }

    private fun toSigned(value: Int, numBits: Int): Int {
        if (numBits >= 32) return value
        val signBit = 1 shl (numBits - 1)
        return if (value and signBit != 0) value - (1 shl numBits) else value
    }

    private fun toSignedLong(value: Long, numBits: Int): Long {
        if (numBits >= 64) return value
        val signBit = 1L shl (numBits - 1)
        return if (value and signBit != 0L) value - (1L shl numBits) else value
    }

    private fun pow2(exp: Double): Double = Math.pow(2.0, exp)

    fun getGpsEphemeris(svid: Int): GpsEphemeris? = gpsEphemerisMap[svid]
}
