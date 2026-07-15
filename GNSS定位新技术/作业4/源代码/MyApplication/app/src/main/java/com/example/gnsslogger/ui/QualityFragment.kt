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

class QualityFragment : Fragment() {

    private val viewModel: MainViewModel by activityViewModels()

    private lateinit var pbGdop: ProgressBar
    private lateinit var pbPdop: ProgressBar
    private lateinit var pbHdop: ProgressBar
    private lateinit var pbVdop: ProgressBar
    private lateinit var tvGdopValue: TextView
    private lateinit var tvPdopValue: TextView
    private lateinit var tvHdopValue: TextView
    private lateinit var tvVdopValue: TextView
    private lateinit var tvDopQuality: TextView
    private lateinit var tvCn0Avg: TextView
    private lateinit var tvCn0Max: TextView
    private lateinit var tvCn0Min: TextView
    private lateinit var tvCn0Strong: TextView
    private lateinit var tvCn0Medium: TextView
    private lateinit var tvCn0Weak: TextView
    private lateinit var llConstellationStats: LinearLayout

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_quality, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        pbGdop = view.findViewById(R.id.pbGdop)
        pbPdop = view.findViewById(R.id.pbPdop)
        pbHdop = view.findViewById(R.id.pbHdop)
        pbVdop = view.findViewById(R.id.pbVdop)
        tvGdopValue = view.findViewById(R.id.tvGdopValue)
        tvPdopValue = view.findViewById(R.id.tvPdopValue)
        tvHdopValue = view.findViewById(R.id.tvHdopValue)
        tvVdopValue = view.findViewById(R.id.tvVdopValue)
        tvDopQuality = view.findViewById(R.id.tvDopQuality)
        tvCn0Avg = view.findViewById(R.id.tvCn0Avg)
        tvCn0Max = view.findViewById(R.id.tvCn0Max)
        tvCn0Min = view.findViewById(R.id.tvCn0Min)
        tvCn0Strong = view.findViewById(R.id.tvCn0Strong)
        tvCn0Medium = view.findViewById(R.id.tvCn0Medium)
        tvCn0Weak = view.findViewById(R.id.tvCn0Weak)
        llConstellationStats = view.findViewById(R.id.llConstellationStats)

        observeViewModel()
    }

    private fun observeViewModel() {
        viewModel.positionResult.observe(viewLifecycleOwner) { result ->
            if (result != null) {
                updateDopDisplay(result.gdop, result.pdop, result.hdop, result.vdop)
            }
        }

        viewModel.satellites.observe(viewLifecycleOwner) { satellites ->
            updateCn0Stats(satellites)
            updateConstellationStats(satellites)
        }
    }

    private fun updateDopDisplay(gdop: Double, pdop: Double, hdop: Double, vdop: Double) {
        updateDopBar(pbGdop, tvGdopValue, gdop)
        updateDopBar(pbPdop, tvPdopValue, pdop)
        updateDopBar(pbHdop, tvHdopValue, hdop)
        updateDopBar(pbVdop, tvVdopValue, vdop)

        val quality = when {
            hdop <= 1 -> "理想"
            hdop <= 2 -> "优秀"
            hdop <= 5 -> "良好"
            hdop <= 10 -> "一般"
            else -> "较差"
        }
        tvDopQuality.text = "DOP 质量: $quality (HDOP=${String.format("%.1f", hdop)})"
    }

    private fun updateDopBar(bar: ProgressBar, tv: TextView, value: Double) {
        val progress = (value * 10).toInt().coerceIn(0, 100)
        bar.progress = progress
        tv.text = String.format("%.1f", value)
    }

    private fun updateCn0Stats(satellites: List<SatelliteInfo>) {
        if (satellites.isEmpty()) {
            tvCn0Avg.text = "--"
            tvCn0Max.text = "--"
            tvCn0Min.text = "--"
            tvCn0Strong.text = "0"
            tvCn0Medium.text = "0"
            tvCn0Weak.text = "0"
            return
        }

        val cn0Values = satellites.map { it.cn0DbHz }
        val avg = cn0Values.average()
        val max = cn0Values.maxOrNull() ?: 0.0
        val min = cn0Values.minOrNull() ?: 0.0

        tvCn0Avg.text = String.format("%.0f", avg)
        tvCn0Max.text = String.format("%.0f", max)
        tvCn0Min.text = String.format("%.0f", min)

        val strong = satellites.count { it.cn0DbHz >= 40 }
        val medium = satellites.count { it.cn0DbHz in 30.0..39.99 }
        val weak = satellites.count { it.cn0DbHz < 30 }

        tvCn0Strong.text = "$strong"
        tvCn0Medium.text = "$medium"
        tvCn0Weak.text = "$weak"
    }

    private fun updateConstellationStats(satellites: List<SatelliteInfo>) {
        llConstellationStats.removeAllViews()

        val grouped = satellites.groupBy { it.constellationName }

        for ((name, sats) in grouped.entries.sortedByDescending { it.value.size }) {
            val avgCn0 = sats.map { it.cn0DbHz }.average()
            val usedCount = sats.count { it.usedInFix }

            val row = LinearLayout(requireContext()).apply {
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).apply {
                    topMargin = 4.dp
                    bottomMargin = 4.dp
                }
                orientation = LinearLayout.HORIZONTAL
                gravity = android.view.Gravity.CENTER_VERTICAL
            }

            row.addView(TextView(requireContext()).apply {
                layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
                text = "$name (${sats.size}颗)"
                textSize = 14f
                setTextColor(Color.parseColor("#191919"))
            })

            row.addView(TextView(requireContext()).apply {
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                )
                text = "平均 ${String.format("%.0f", avgCn0)} dB | 定位 $usedCount 颗"
                textSize = 12f
                setTextColor(Color.parseColor("#999999"))
            })

            llConstellationStats.addView(row)
        }
    }

    private val Int.dp: Int
        get() = (this * resources.displayMetrics.density).toInt()
}
