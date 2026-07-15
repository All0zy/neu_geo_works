package com.example.gnsslogger.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import com.example.gnsslogger.R
import com.example.gnsslogger.data.model.PositionResult
import com.google.android.material.button.MaterialButton

class PositionFragment : Fragment() {

    private val viewModel: MainViewModel by activityViewModels()

    private lateinit var tvPositionStatus: TextView
    private lateinit var tvLatitude: TextView
    private lateinit var btnDownloadEphemeris: MaterialButton
    private lateinit var tvEphemerisStatus: TextView
    private lateinit var tvLongitude: TextView
    private lateinit var tvAccuracy: TextView
    private lateinit var tvHdop: TextView
    private lateinit var tvPdop: TextView
    private lateinit var tvGdop: TextView
    private lateinit var tvSatellitesUsed: TextView
    private lateinit var tvSatellitesVisible: TextView

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_position, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        tvPositionStatus = view.findViewById(R.id.tvPositionStatus)
        tvLatitude = view.findViewById(R.id.tvLatitude)
        btnDownloadEphemeris = view.findViewById(R.id.btnDownloadEphemeris)
        tvEphemerisStatus = view.findViewById(R.id.tvEphemerisStatus)
        tvLongitude = view.findViewById(R.id.tvLongitude)
        tvAccuracy = view.findViewById(R.id.tvAccuracy)
        tvHdop = view.findViewById(R.id.tvHdop)
        tvPdop = view.findViewById(R.id.tvPdop)
        tvGdop = view.findViewById(R.id.tvGdop)
        tvSatellitesUsed = view.findViewById(R.id.tvSatellitesUsed)
        tvSatellitesVisible = view.findViewById(R.id.tvSatellitesVisible)

        btnDownloadEphemeris.setOnClickListener {
            viewModel.downloadEphemeris()
        }

        observeViewModel()
    }

    private fun observeViewModel() {
        viewModel.ephemerisStatus.observe(viewLifecycleOwner) { status ->
            tvEphemerisStatus.text = status
        }

        viewModel.isDownloading.observe(viewLifecycleOwner) { downloading ->
            btnDownloadEphemeris.isEnabled = !downloading
            btnDownloadEphemeris.text = if (downloading) "下载中..." else "下载星历加速定位"
        }

        viewModel.positionResult.observe(viewLifecycleOwner) { result ->
            if (result != null) {
                updatePosition(result)
            } else {
                showNoPosition()
            }
        }

        viewModel.satellites.observe(viewLifecycleOwner) { satellites ->
            val visible = satellites.size
            val used = satellites.count { it.usedInFix }
            tvSatellitesUsed.text = "$used 颗"
            tvSatellitesVisible.text = "$visible 颗"
        }
    }

    private fun updatePosition(result: PositionResult) {
        tvPositionStatus.text = "已定位"
        tvPositionStatus.setTextColor(resources.getColor(R.color.success, null))

        tvLatitude.text = String.format("%.6f°", result.latitudeDeg)
        tvLongitude.text = String.format("%.6f°", result.longitudeDeg)
        tvAccuracy.text = String.format("%.1f 米", result.accuracyMeters)
        tvHdop.text = String.format("%.1f", result.hdop)
        tvPdop.text = String.format("%.1f", result.pdop)
        tvGdop.text = String.format("%.1f", result.gdop)
        tvSatellitesUsed.text = "${result.satellitesUsed} 颗"
        tvSatellitesVisible.text = "${result.satellitesVisible} 颗"
    }

    private fun showNoPosition() {
        tvPositionStatus.text = getString(R.string.no_location)
        tvPositionStatus.setTextColor(resources.getColor(R.color.error, null))

        tvLatitude.text = "--"
        tvLongitude.text = "--"
        tvAccuracy.text = "--"
        tvHdop.text = "--"
        tvPdop.text = "--"
        tvGdop.text = "--"
    }
}
