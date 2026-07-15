package com.example.gnsslogger.ui

import android.content.Context
import android.graphics.*
import android.util.AttributeSet
import android.view.View
import com.example.gnsslogger.data.model.SatelliteInfo
import com.example.gnsslogger.util.Constants
import kotlin.math.cos
import kotlin.math.min
import kotlin.math.sin

/**
 * 卫星天空图 - 微信风格
 */
class SkyPlotView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val satPaint = Paint(Paint.ANTI_ALIAS_FLAG)

    private var satellites = listOf<SatelliteInfo>()
    private var centerX = 0f
    private var centerY = 0f
    private var radius = 0f

    // 微信风格颜色
    private val bgColor = Color.WHITE
    private val gridColor = Color.parseColor("#F0F0F0")
    private val gridLineColor = Color.parseColor("#E0E0E0")
    private val textColor = Color.parseColor("#B0B0B0")
    private val labelColor = Color.parseColor("#333333")

    // 星座颜色
    private val constellationColors = mapOf(
        "GPS" to Color.parseColor("#1989FA"),
        "GLO" to Color.parseColor("#FA5151"),
        "BDS" to Color.parseColor("#FF9500"),
        "GAL" to Color.parseColor("#07C160"),
        "QZS" to Color.parseColor("#6467F0"),
        "SBAS" to Color.parseColor("#999999"),
        "IRN" to Color.parseColor("#AA6CFF"),
    )

    init {
        textPaint.textAlign = Paint.Align.CENTER
    }

    fun updateSatellites(sats: List<SatelliteInfo>) {
        satellites = sats
        invalidate()
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        centerX = w / 2f
        centerY = h / 2f
        radius = min(w, h) / 2f - 24f
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        // 背景
        canvas.drawColor(bgColor)

        // 同心圆（仰角圈）
        paint.style = Paint.Style.STROKE
        paint.strokeWidth = 1f

        for (elev in intArrayOf(0, 30, 60, 90)) {
            val r = radius * (90 - elev) / 90f
            paint.color = if (elev == 0) gridLineColor else gridColor
            canvas.drawCircle(centerX, centerY, r, paint)

            // 仰角标注
            if (elev > 0 && elev < 90) {
                textPaint.textSize = 18f
                textPaint.color = textColor
                canvas.drawText("${elev}°", centerX + 6, centerY - r + 16, textPaint)
            }
        }

        // 方向线
        paint.color = gridColor
        for (angle in intArrayOf(0, 90, 180, 270)) {
            val rad = angle * Constants.DEG_TO_RAD.toFloat()
            val endX = centerX + radius * sin(rad)
            val endY = centerY - radius * cos(rad)
            canvas.drawLine(centerX, centerY, endX, endY, paint)
        }

        // 方向标注
        textPaint.textSize = 22f
        textPaint.color = labelColor
        textPaint.isFakeBoldText = true
        canvas.drawText("N", centerX, centerY - radius - 8, textPaint)
        canvas.drawText("S", centerX, centerY + radius + 24, textPaint)
        canvas.drawText("E", centerX + radius + 16, centerY + 8, textPaint)
        canvas.drawText("W", centerX - radius - 16, centerY + 8, textPaint)
        textPaint.isFakeBoldText = false

        // 绘制卫星
        for (sat in satellites) {
            drawSatellite(canvas, sat)
        }
    }

    private fun drawSatellite(canvas: Canvas, sat: SatelliteInfo) {
        val elevRad = (sat.elevationDeg * Constants.DEG_TO_RAD).toFloat()
        val azimRad = (sat.azimuthDeg * Constants.DEG_TO_RAD).toFloat()

        val r = radius * (90 - sat.elevationDeg.toFloat()) / 90f
        val x = centerX + r * sin(azimRad)
        val y = centerY - r * cos(azimRad)

        val color = constellationColors[sat.constellationName] ?: Color.GRAY

        val size = when {
            sat.cn0DbHz >= 40 -> 14f
            sat.cn0DbHz >= 30 -> 11f
            sat.cn0DbHz >= 20 -> 8f
            else -> 6f
        }

        // 绘制卫星
        satPaint.color = color
        if (sat.usedInFix) {
            satPaint.style = Paint.Style.FILL
            canvas.drawCircle(x, y, size, satPaint)
            // 白色边框
            satPaint.style = Paint.Style.STROKE
            satPaint.strokeWidth = 1.5f
            satPaint.color = Color.WHITE
            canvas.drawCircle(x, y, size + 1, satPaint)
        } else {
            satPaint.style = Paint.Style.STROKE
            satPaint.strokeWidth = 1.5f
            canvas.drawCircle(x, y, size, satPaint)
        }

        // 卫星编号
        textPaint.textSize = 18f
        textPaint.color = color
        textPaint.isFakeBoldText = sat.usedInFix
        canvas.drawText("${sat.svid}", x, y - size - 4, textPaint)
        textPaint.isFakeBoldText = false
    }
}
