package com.example.gnsslogger.ui

import android.graphics.Color
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import com.example.gnsslogger.R
import com.example.gnsslogger.data.model.SatelliteInfo

class SkyPlotFragment : Fragment() {

    private val viewModel: MainViewModel by activityViewModels()
    private lateinit var skyPlotView: SkyPlotView
    private lateinit var llSatelliteList: LinearLayout

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_sky_plot, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        skyPlotView = view.findViewById(R.id.skyPlotView)
        llSatelliteList = view.findViewById(R.id.llSatelliteList)

        observeViewModel()
    }

    private fun observeViewModel() {
        viewModel.satellites.observe(viewLifecycleOwner) { satellites ->
            skyPlotView.updateSatellites(satellites)
            updateSatelliteList(satellites)
        }
    }

    /**
     * 显示所有卫星详细信息
     */
    private fun updateSatelliteList(satellites: List<SatelliteInfo>) {
        llSatelliteList.removeAllViews()

        val sorted = satellites.sortedByDescending { it.cn0DbHz }

        for ((index, sat) in sorted.withIndex()) {
            val row = createSatelliteRow(sat)
            llSatelliteList.addView(row)

            // 分隔线
            if (index < sorted.size - 1) {
                val divider = View(requireContext()).apply {
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        1
                    ).apply {
                        topMargin = 6.dp
                        bottomMargin = 6.dp
                    }
                    setBackgroundColor(Color.parseColor("#ECECEC"))
                }
                llSatelliteList.addView(divider)
            }
        }
    }

    private fun createSatelliteRow(sat: SatelliteInfo): View {
        val context = requireContext()

        return LinearLayout(context).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = 4.dp
                bottomMargin = 4.dp
            }
            orientation = LinearLayout.VERTICAL

            // 第一行：卫星名称 + 信号强度
            addView(LinearLayout(context).apply {
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                )
                orientation = LinearLayout.HORIZONTAL
                gravity = android.view.Gravity.CENTER_VERTICAL

                // 卫星名称 + 定位标记
                addView(TextView(context).apply {
                    layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
                    text = if (sat.usedInFix) "● ${sat.constellationName} SV${sat.svid} [定位中]"
                           else "○ ${sat.constellationName} SV${sat.svid}"
                    textSize = 14f
                    setTextColor(if (sat.usedInFix) Color.parseColor("#07C160") else Color.parseColor("#191919"))
                })

                // 信号强度条
                addView(View(context).apply {
                    layoutParams = LinearLayout.LayoutParams(50.dp, 6.dp).apply {
                        marginEnd = 8.dp
                    }
                    setBackgroundColor(getSignalColor(sat.cn0DbHz))
                })

                // 信号强度数值
                addView(TextView(context).apply {
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT
                    )
                    text = "${String.format("%.0f", sat.cn0DbHz)} dB"
                    textSize = 12f
                    setTextColor(getSignalColor(sat.cn0DbHz))
                })
            })

            // 第二行：仰角、方位角、频率
            addView(TextView(context).apply {
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).apply {
                    topMargin = 2.dp
                }
                text = "仰角: ${String.format("%.1f", sat.elevationDeg)}°  |  " +
                       "方位: ${String.format("%.1f", sat.azimuthDeg)}°  |  " +
                       "频率: ${String.format("%.1f", sat.carrierFrequencyHz / 1e6)} MHz"
                textSize = 11f
                setTextColor(Color.parseColor("#999999"))
            })
        }
    }

    private fun getSignalColor(cn0: Double): Int {
        return when {
            cn0 >= 40 -> Color.parseColor("#07C160")  // 强信号 - 绿色
            cn0 >= 30 -> Color.parseColor("#1989FA")  // 中信号 - 蓝色
            cn0 >= 20 -> Color.parseColor("#FF9500")  // 弱信号 - 橙色
            else -> Color.parseColor("#FA5151")        // 极弱 - 红色
        }
    }

    private val Int.dp: Int
        get() = (this * resources.displayMetrics.density).toInt()
}
