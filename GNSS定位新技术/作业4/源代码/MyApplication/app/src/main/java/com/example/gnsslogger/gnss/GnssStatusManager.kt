package com.example.gnsslogger.gnss

import android.location.GnssStatus
import android.location.LocationManager
import android.os.Build
import android.util.Log
import com.example.gnsslogger.data.model.SatelliteInfo
import com.example.gnsslogger.util.Constants

/**
 * GNSS 卫星状态管理器
 * 管理卫星状态回调，提供可见卫星列表、仰角、方位角、C/N0 等信息
 */
class GnssStatusManager(
    private val locationManager: LocationManager
) {
    companion object {
        private const val TAG = "GnssStatusMgr"
    }

    private var callback: GnssStatus.Callback? = null
    private var listener: OnStatusChangedListener? = null
    private var isRegistered = false

    // 当前卫星状态缓存
    private var currentSatellites = listOf<SatelliteInfo>()
    private var satellitesUsedInFix = setOf<Int>() // svid * 100 + constellation

    interface OnStatusChangedListener {
        fun onSatelliteStatusChanged(satellites: List<SatelliteInfo>)
        fun onFirstFix(ttff: Int)
        fun onSatelliteStatusChanged()
    }

    fun register(listener: OnStatusChangedListener) {
        if (isRegistered) return
        this.listener = listener

        callback = object : GnssStatus.Callback() {
            override fun onStarted() {
                Log.d(TAG, "GNSS status started")
            }

            override fun onStopped() {
                Log.d(TAG, "GNSS status stopped")
            }

            override fun onFirstFix(ttff: Int) {
                Log.i(TAG, "First fix in ${ttff}ms")
                listener.onFirstFix(ttff)
            }

            override fun onSatelliteStatusChanged(status: GnssStatus) {
                processSatelliteStatus(status)
            }
        }

        try {
            locationManager.registerGnssStatusCallback(callback!!, null)
            isRegistered = true
            Log.i(TAG, "GNSS status callback registered")
        } catch (e: SecurityException) {
            Log.e(TAG, "Security exception registering status callback", e)
        }
    }

    fun unregister() {
        callback?.let {
            locationManager.unregisterGnssStatusCallback(it)
            callback = null
            isRegistered = false
            listener = null
        }
    }

    fun getCurrentSatellites(): List<SatelliteInfo> = currentSatellites

    fun getSatellitesUsedInFix(): Set<Int> = satellitesUsedInFix

    /**
     * 处理卫星状态变化
     */
    private fun processSatelliteStatus(status: GnssStatus) {
        val satellites = mutableListOf<SatelliteInfo>()
        val usedInFix = mutableSetOf<Int>()

        for (i in 0 until status.satelliteCount) {
            val svid = status.getSvid(i)
            val constellation = status.getConstellationType(i)
            val cn0 = status.getCn0DbHz(i)
            val elevation = status.getElevationDegrees(i)
            val azimuth = status.getAzimuthDegrees(i)
            val usedInFixFlag = status.usedInFix(i)
            val hasEphemeris = status.hasEphemerisData(i)
            val hasAlmanac = status.hasAlmanacData(i)

            // 获取载波频率
            val carrierFreq = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                status.getCarrierFrequencyHz(i)
            } else {
                0f
            }

            // 获取基带 C/N0
            val basebandCn0 = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                status.getBasebandCn0DbHz(i)
            } else {
                0f
            }

            val satInfo = SatelliteInfo(
                svid = svid,
                constellationType = constellation,
                constellationName = getConstellationName(constellation),
                cn0DbHz = cn0.toDouble(),
                elevationDeg = elevation.toDouble(),
                azimuthDeg = azimuth.toDouble(),
                usedInFix = usedInFixFlag,
                hasEphemeris = hasEphemeris,
                hasAlmanac = hasAlmanac,
                carrierFrequencyHz = carrierFreq,
                basebandCn0DbHz = basebandCn0.toDouble(),
            )

            satellites.add(satInfo)

            if (usedInFixFlag) {
                usedInFix.add(svid * 100 + constellation)
            }
        }

        currentSatellites = satellites
        satellitesUsedInFix = usedInFix
        listener?.onSatelliteStatusChanged(satellites)
    }

    /**
     * 获取星座名称
     */
    private fun getConstellationName(constellationType: Int): String {
        return when (constellationType) {
            Constants.CONSTELLATION_GPS -> "GPS"
            Constants.CONSTELLATION_GLONASS -> "GLO"
            Constants.CONSTELLATION_BDS -> "BDS"
            Constants.CONSTELLATION_GALILEO -> "GAL"
            Constants.CONSTELLATION_QZSS -> "QZS"
            Constants.CONSTELLATION_SBAS -> "SBAS"
            Constants.CONSTELLATION_IRNSS -> "IRN"
            else -> "???"
        }
    }

    /**
     * 获取用于定位的卫星数
     */
    fun getUsedSatelliteCount(): Int = satellitesUsedInFix.size

    /**
     * 获取可见卫星数
     */
    fun getVisibleSatelliteCount(): Int = currentSatellites.size
}
