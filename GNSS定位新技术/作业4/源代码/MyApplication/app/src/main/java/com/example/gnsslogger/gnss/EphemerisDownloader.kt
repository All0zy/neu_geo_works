package com.example.gnsslogger.gnss

import android.util.Log
import com.example.gnsslogger.data.model.GpsEphemeris
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL

/**
 * 星历下载器 - 从 A-GPS 服务器下载预测星历
 * 使用 SUPL (Secure User Plane Location) 协议
 */
class EphemerisDownloader {
    companion object {
        private const val TAG = "EphemerisDownloader"

        // 公共 A-GPS 服务器
        private const val SUPL_SERVER = "https://supl.google.com"
        private const val XTRA_SERVER = "https://www.gpsassist.net"

        // RINEX 导航文件服务器（IGS）
        private const val IGS_NAV_URL = "https://cddis.nasa.gov/archive/gnss/data/daily/"
    }

    /**
     * 下载 XTRA 辅助数据（Android 使用的格式）
     * XTRA 包含预测的卫星轨道和时钟参数
     */
    suspend fun downloadXtraData(): ByteArray? = withContext(Dispatchers.IO) {
        try {
            Log.i(TAG, "正在下载 XTRA 辅助数据...")

            // 尝试从多个服务器下载
            val urls = listOf(
                "https://xtrapath1.izatcloud.net/xtra3grc.bin",
                "https://xtrapath2.izatcloud.net/xtra3grc.bin",
                "https://xtrapath3.izatcloud.net/xtra3grc.bin",
                "https://www.gpsassist.net/xtra3grc.bin"
            )

            for (url in urls) {
                try {
                    val data = downloadFile(url)
                    if (data != null && data.size > 1000) {
                        Log.i(TAG, "XTRA 数据下载成功: ${data.size} bytes from $url")
                        return@withContext data
                    }
                } catch (e: Exception) {
                    Log.w(TAG, "从 $url 下载失败: ${e.message}")
                }
            }

            Log.w(TAG, "所有 XTRA 服务器下载失败")
            null
        } catch (e: Exception) {
            Log.e(TAG, "XTRA 下载异常", e)
            null
        }
    }

    /**
     * 下载 RINEX 导航文件（包含广播星历）
     */
    suspend fun downloadRinexNav(): String? = withContext(Dispatchers.IO) {
        try {
            Log.i(TAG, "正在下载 RINEX 导航文件...")

            // 构造今天的 RINEX 文件 URL
            val cal = java.util.Calendar.getInstance()
            val year = cal.get(java.util.Calendar.YEAR)
            val dayOfYear = cal.get(java.util.Calendar.DAY_OF_YEAR)
            val yy = (year % 100).toString().padStart(2, '0')
            val doy = dayOfYear.toString().padStart(3, '0')

            // IGS 快速星历
            val url = "https://cddis.nasa.gov/archive/gnss/data/daily/${year}/brdc/brdc${doy}0.${yy}n.gz"

            val data = downloadFile(url)
            if (data != null) {
                Log.i(TAG, "RINEX 文件下载成功: ${data.size} bytes")
                return@withContext String(data)
            }

            null
        } catch (e: Exception) {
            Log.e(TAG, "RINEX 下载异常", e)
            null
        }
    }

    /**
     * 从 SUPL 服务器获取辅助数据
     */
    suspend fun requestSuplAssist(): Boolean = withContext(Dispatchers.IO) {
        try {
            Log.i(TAG, "正在请求 SUPL 辅助数据...")

            val url = URL("$SUPL_SERVER/supl/v1/assist")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/octet-stream")
            conn.connectTimeout = 5000
            conn.readTimeout = 5000

            val responseCode = conn.responseCode
            Log.i(TAG, "SUPL 响应: $responseCode")

            conn.disconnect()
            responseCode == 200
        } catch (e: Exception) {
            Log.w(TAG, "SUPL 请求失败: ${e.message}")
            false
        }
    }

    private fun downloadFile(urlStr: String): ByteArray? {
        val url = URL(urlStr)
        val conn = url.openConnection() as HttpURLConnection
        conn.requestMethod = "GET"
        conn.connectTimeout = 10000
        conn.readTimeout = 10000
        conn.setRequestProperty("User-Agent", "GNSSLogger/1.0")

        if (conn.responseCode != 200) {
            conn.disconnect()
            return null
        }

        val data = conn.inputStream.readBytes()
        conn.disconnect()
        return data
    }
}
