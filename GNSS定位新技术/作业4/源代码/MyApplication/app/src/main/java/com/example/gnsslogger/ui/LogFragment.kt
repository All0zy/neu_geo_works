package com.example.gnsslogger.ui

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.core.content.FileProvider
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.gnsslogger.R
import com.example.gnsslogger.data.model.RawMeasurement
import com.google.android.material.button.MaterialButton
import java.io.File

class LogFragment : Fragment() {

    private val viewModel: MainViewModel by activityViewModels()
    private lateinit var rvMeasurements: RecyclerView
    private lateinit var btnToggleLogging: MaterialButton
    private lateinit var btnClearLog: MaterialButton
    private lateinit var btnExport: MaterialButton
    private lateinit var tvLogFileInfo: TextView

    private val adapter = MeasurementAdapter()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_log, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        rvMeasurements = view.findViewById(R.id.rvMeasurements)
        btnToggleLogging = view.findViewById(R.id.btnToggleLogging)
        btnClearLog = view.findViewById(R.id.btnClearLog)
        btnExport = view.findViewById(R.id.btnExport)
        tvLogFileInfo = view.findViewById(R.id.tvLogFileInfo)

        rvMeasurements.layoutManager = LinearLayoutManager(requireContext())
        rvMeasurements.adapter = adapter

        btnToggleLogging.setOnClickListener {
            viewModel.toggleLogging()
        }

        btnClearLog.setOnClickListener {
            adapter.clearData()
            Toast.makeText(requireContext(), "显示已清除", Toast.LENGTH_SHORT).show()
        }

        btnExport.setOnClickListener {
            exportLog()
        }

        observeViewModel()
    }

    private fun observeViewModel() {
        viewModel.rawMeasurements.observe(viewLifecycleOwner) { measurements ->
            adapter.updateData(measurements)
        }

        viewModel.isLogging.observe(viewLifecycleOwner) { logging ->
            btnToggleLogging.text = if (logging) getString(R.string.stop_logging) else getString(R.string.start_logging)
        }

        viewModel.logFilePath.observe(viewLifecycleOwner) { path ->
            tvLogFileInfo.text = if (path != null) {
                "日志: ${File(path).name}"
            } else {
                "日志文件: 无"
            }
        }
    }

    private fun exportLog() {
        val path = viewModel.logFilePath.value
        if (path == null) {
            Toast.makeText(requireContext(), "没有可导出的日志", Toast.LENGTH_SHORT).show()
            return
        }

        val file = File(path)
        if (!file.exists()) {
            Toast.makeText(requireContext(), "日志文件不存在", Toast.LENGTH_SHORT).show()
            return
        }

        try {
            val uri = FileProvider.getUriForFile(
                requireContext(),
                "${requireContext().packageName}.fileprovider",
                file
            )
            val shareIntent = Intent(Intent.ACTION_SEND).apply {
                type = "text/csv"
                putExtra(Intent.EXTRA_STREAM, uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            startActivity(Intent.createChooser(shareIntent, "导出日志"))
        } catch (e: Exception) {
            Toast.makeText(requireContext(), "导出失败: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    /**
     * 测量数据适配器
     */
    class MeasurementAdapter : RecyclerView.Adapter<MeasurementAdapter.ViewHolder>() {
        private var data = listOf<RawMeasurement>()

        fun updateData(newData: List<RawMeasurement>) {
            data = newData
            notifyDataSetChanged()
        }

        fun clearData() {
            data = emptyList()
            notifyDataSetChanged()
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
            val view = LayoutInflater.from(parent.context)
                .inflate(android.R.layout.simple_list_item_2, parent, false)
            return ViewHolder(view)
        }

        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val m = data[position]
            val constellation = when (m.constellationType) {
                1 -> "GPS"
                3 -> "GLO"
                5 -> "BDS"
                6 -> "GAL"
                else -> "???"
            }
            holder.tvTitle.text = "SV ${m.svid} ($constellation) - ${String.format("%.1f", m.cn0DbHz)} dB-Hz"
            holder.tvSubtitle.text = "PR: ${String.format("%.1f", m.pseudorangeMeters)}m | " +
                    "CP: ${String.format("%.3f", m.accumulatedDeltaRangeMeters)}m | " +
                    "Freq: ${String.format("%.0f", m.carrierFrequencyHz / 1e6)}MHz"
        }

        override fun getItemCount() = data.size

        class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
            val tvTitle: TextView = view.findViewById(android.R.id.text1)
            val tvSubtitle: TextView = view.findViewById(android.R.id.text2)
        }
    }
}
