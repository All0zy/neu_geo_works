package com.example.gnsslogger.ui

import android.graphics.Color
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import com.example.gnsslogger.R
import com.example.gnsslogger.data.model.SatelliteInfo

class SecurityFragment : Fragment() {

    private val viewModel: MainViewModel by activityViewModels()

    private lateinit var viewIntegrityIndicator: View
    private lateinit var tvIntegrityStatus: TextView
    private lateinit var tvIntegrityDetail: TextView
    private lateinit var pbPseudorangeResidual: ProgressBar
    private lateinit var tvPseudorangeResidual: TextView
    private lateinit var pbCarrierJump: ProgressBar
    private lateinit var tvCarrierJump: TextView
    private lateinit var pbMultipath: ProgressBar
    private lateinit var tvMultipath: TextView
    private lateinit var llDetectionItems: LinearLayout

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_security, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewIntegrityIndicator = view.findViewById(R.id.viewIntegrityIndicator)
        tvIntegrityStatus = view.findViewById(R.id.tvIntegrityStatus)
        tvIntegrityDetail = view.findViewById(R.id.tvIntegrityDetail)
        pbPseudorangeResidual = view.findViewById(R.id.pbPseudorangeResidual)
        tvPseudorangeResidual = view.findViewById(R.id.tvPseudorangeResidual)
        pbCarrierJump = view.findViewById(R.id.pbCarrierJump)
        tvCarrierJump = view.findViewById(R.id.tvCarrierJump)
        pbMultipath = view.findViewById(R.id.pbMultipath)
        tvMultipath = view.findViewById(R.id.tvMultipath)
        llDetectionItems = view.findViewById(R.id.llDetectionItems)

        observeViewModel()
    }

    private fun observeViewModel() {
        viewModel.satellites.observe(viewLifecycleOwner) { satellites ->
            updateSecurityAnalysis(satellites)
        }
    }

    private fun updateSecurityAnalysis(satellites: List<SatelliteInfo>) {
        if (satellites.isEmpty()) {
            showNoData()
            return
        }

        // 分析信号异常
        val anomalies = mutableListOf<String>()
        var suspiciousCount = 0

        // 检测1: C/N0 异常（所有卫星信号强度相似可能是欺骗）
        val cn0Values = satellites.map { it.cn0DbHz }
        val cn0Std = cn0Values.let { values ->
            val avg = values.average()
            kotlin.math.sqrt(values.map { (it - avg) * (it - avg) }.average())
        }

        val cn0Residual = (cn0Std * 10).toInt().coerceIn(0, 100)
        pbPseudorangeResidual.progress = cn0Residual
        tvPseudorangeResidual.text = "${String.format("%.1f", cn0Std)} dB"

        if (cn0Std < 3 && satellites.size > 6) {
            anomalies.add("所有卫星信号强度过于一致 (σ=${String.format("%.1f", cn0Std)} dB)")
            suspiciousCount++
        }

        // 检测2: 卫星数量异常
        val satCountResidual = when {
            satellites.size > 30 -> 80
            satellites.size > 25 -> 60
            satellites.size > 20 -> 40
            else -> 20
        }
        pbCarrierJump.progress = satCountResidual
        tvCarrierJump.text = "${satellites.size}颗"

        if (satellites.size > 25) {
            anomalies.add("可见卫星数量异常多 (${satellites.size}颗)")
            suspiciousCount++
        }

        // 检测3: 多径检测（低仰角高信号强度可能是反射信号）
        val multipathSuspects = satellites.filter {
            it.elevationDeg < 15 && it.cn0DbHz > 35
        }
        val multipathIndex = (multipathSuspects.size * 20).toInt().coerceIn(0, 100)
        pbMultipath.progress = multipathIndex
        tvMultipath.text = "${multipathSuspects.size}颗"

        if (multipathSuspects.isNotEmpty()) {
            anomalies.add("${multipathSuspects.size}颗低仰角卫星信号异常强")
            suspiciousCount++
        }

        // 更新完整性状态
        when {
            suspiciousCount == 0 -> {
                viewIntegrityIndicator.setBackgroundColor(Color.parseColor("#07C160"))
                tvIntegrityStatus.text = "信号正常"
                tvIntegrityStatus.setTextColor(Color.parseColor("#07C160"))
                tvIntegrityDetail.text = "未检测到异常，信号质量良好"
            }
            suspiciousCount <= 1 -> {
                viewIntegrityIndicator.setBackgroundColor(Color.parseColor("#FF9500"))
                tvIntegrityStatus.text = "轻微异常"
                tvIntegrityStatus.setTextColor(Color.parseColor("#FF9500"))
                tvIntegrityDetail.text = "检测到轻微异常，建议关注"
            }
            else -> {
                viewIntegrityIndicator.setBackgroundColor(Color.parseColor("#FA5151"))
                tvIntegrityStatus.text = "警告"
                tvIntegrityStatus.setTextColor(Color.parseColor("#FA5151"))
                tvIntegrityDetail.text = "检测到多项异常，可能存在欺骗"
            }
        }

        // 更新检测项列表
        updateDetectionItems(satellites, anomalies)
    }

    private fun updateDetectionItems(satellites: List<SatelliteInfo>, anomalies: List<String>) {
        llDetectionItems.removeAllViews()

        val items = listOf(
            DetectionItem("信号强度一致性", cn0ConsistencyCheck(satellites)),
            DetectionItem("卫星数量合理性", satCountCheck(satellites)),
            DetectionItem("低仰角信号", lowElevationCheck(satellites)),
            DetectionItem("星座完整性", constellationCheck(satellites)),
            DetectionItem("频率一致性", frequencyCheck(satellites))
        )

        for (item in items) {
            val row = createDetectionItemRow(item)
            llDetectionItems.addView(row)
        }
    }

    private fun createDetectionItemRow(item: DetectionItem): View {
        val context = requireContext()

        return LinearLayout(context).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = 8.dp
                bottomMargin = 8.dp
            }
            orientation = LinearLayout.HORIZONTAL
            gravity = android.view.Gravity.CENTER_VERTICAL

            // 状态指示
            addView(View(context).apply {
                layoutParams = LinearLayout.LayoutParams(12.dp, 12.dp).apply {
                    marginEnd = 12.dp
                }
                setBackgroundColor(when (item.status) {
                    "正常" -> Color.parseColor("#07C160")
                    "警告" -> Color.parseColor("#FF9500")
                    "异常" -> Color.parseColor("#FA5151")
                    else -> Color.parseColor("#999999")
                })
            })

            // 检测项名称
            addView(TextView(context).apply {
                layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
                text = item.name
                textSize = 14f
                setTextColor(Color.parseColor("#191919"))
            })

            // 检测结果
            addView(TextView(context).apply {
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                )
                text = item.status
                textSize = 13f
                setTextColor(when (item.status) {
                    "正常" -> Color.parseColor("#07C160")
                    "警告" -> Color.parseColor("#FF9500")
                    "异常" -> Color.parseColor("#FA5151")
                    else -> Color.parseColor("#999999")
                })
            })
        }
    }

    private fun cn0ConsistencyCheck(satellites: List<SatelliteInfo>): String {
        if (satellites.size < 4) return "数据不足"
        val std = satellites.map { it.cn0DbHz }.let { values ->
            val avg = values.average()
            kotlin.math.sqrt(values.map { (it - avg) * (it - avg) }.average())
        }
        return if (std < 3 && satellites.size > 6) "警告" else "正常"
    }

    private fun satCountCheck(satellites: List<SatelliteInfo>): String {
        return when {
            satellites.size > 30 -> "异常"
            satellites.size > 25 -> "警告"
            else -> "正常"
        }
    }

    private fun lowElevationCheck(satellites: List<SatelliteInfo>): String {
        val suspects = satellites.count { it.elevationDeg < 15 && it.cn0DbHz > 35 }
        return if (suspects > 2) "警告" else "正常"
    }

    private fun constellationCheck(satellites: List<SatelliteInfo>): String {
        val constellations = satellites.groupBy { it.constellationType }.size
        return if (constellations >= 2) "正常" else "数据不足"
    }

    private fun frequencyCheck(satellites: List<SatelliteInfo>): String {
        val frequencies = satellites.map { it.carrierFrequencyHz }.distinct().size
        return if (frequencies <= 5) "正常" else "警告"
    }

    private fun showNoData() {
        viewIntegrityIndicator.setBackgroundColor(Color.parseColor("#999999"))
        tvIntegrityStatus.text = "等待数据"
        tvIntegrityStatus.setTextColor(Color.parseColor("#999999"))
        tvIntegrityDetail.text = "正在等待卫星数据..."
        pbPseudorangeResidual.progress = 0
        tvPseudorangeResidual.text = "--"
        pbCarrierJump.progress = 0
        tvCarrierJump.text = "--"
        pbMultipath.progress = 0
        tvMultipath.text = "--"
    }

    private val Int.dp: Int
        get() = (this * resources.displayMetrics.density).toInt()

    data class DetectionItem(val name: String, val status: String)
}
