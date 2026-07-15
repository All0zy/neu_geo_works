package com.example.gnsslogger.log

import android.content.Context
import android.util.Log
import java.io.File
import java.text.SimpleDateFormat
import java.util.*

/**
 * 日志文件管理器
 * 管理日志文件的创建、列表、删除、导出
 */
class LogFileManager(private val context: Context) {
    companion object {
        private const val TAG = "LogFileManager"
        private const val LOG_DIR_NAME = "gnss_logs"
    }

    private val logDir: File by lazy {
        File(context.getExternalFilesDir(null), LOG_DIR_NAME).also {
            if (!it.exists()) it.mkdirs()
        }
    }

    /**
     * 获取所有日志文件列表
     */
    fun getLogFiles(): List<File> {
        return logDir.listFiles { file -> file.extension == "csv" }
            ?.sortedByDescending { it.lastModified() }
            ?: emptyList()
    }

    /**
     * 获取日志文件数量
     */
    fun getLogFileCount(): Int = getLogFiles().size

    /**
     * 获取日志目录总大小（字节）
     */
    fun getTotalSize(): Long {
        return getLogFiles().sumOf { it.length() }
    }

    /**
     * 格式化的总大小
     */
    fun getTotalSizeFormatted(): String {
        val bytes = getTotalSize()
        return when {
            bytes < 1024 -> "$bytes B"
            bytes < 1024 * 1024 -> "${bytes / 1024} KB"
            else -> String.format("%.1f MB", bytes / (1024.0 * 1024.0))
        }
    }

    /**
     * 删除指定文件
     */
    fun deleteFile(file: File): Boolean {
        return if (file.exists() && file.parentFile == logDir) {
            file.delete()
        } else {
            false
        }
    }

    /**
     * 删除所有日志文件
     */
    fun deleteAllFiles(): Int {
        val files = getLogFiles()
        var deleted = 0
        for (file in files) {
            if (file.delete()) deleted++
        }
        return deleted
    }

    /**
     * 获取日志目录路径
     */
    fun getLogDirectory(): File = logDir

    /**
     * 生成导出文件名
     */
    fun getExportFileName(originalName: String): String {
        return originalName
    }

    /**
     * 创建新的日志文件（不打开）
     */
    fun createNewLogFile(): File {
        val dateFormat = SimpleDateFormat("yyyy-MM-dd_HH-mm-ss", Locale.US)
        val fileName = "gnss_log_${dateFormat.format(Date())}.csv"
        return File(logDir, fileName)
    }
}
