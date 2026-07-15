package com.example.gnsslogger.ui

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.updateLayoutParams
import androidx.core.view.updatePadding
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.setupWithNavController
import com.example.gnsslogger.R
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.google.android.material.card.MaterialCardView

class MainActivity : AppCompatActivity() {

    private val viewModel: MainViewModel by viewModels()

    private lateinit var tvSatelliteCount: TextView
    private lateinit var tvMeasurementCount: TextView
    private lateinit var tvLoggingStatus: TextView

    private val locationPermissionRequest = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val fineGranted = permissions[Manifest.permission.ACCESS_FINE_LOCATION] ?: false
        if (fineGranted) {
            Toast.makeText(this, "位置权限已授予", Toast.LENGTH_SHORT).show()
            viewModel.initializeIfPermitted()
        } else {
            Toast.makeText(this, "需要位置权限才能使用 GNSS 功能", Toast.LENGTH_LONG).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // 启用 Edge-to-Edge 全面屏
        WindowCompat.setDecorFitsSystemWindows(window, false)

        setContentView(R.layout.activity_main)

        // 处理 WindowInsets（全面屏适配）
        setupWindowInsets()

        // 初始化状态栏控件
        tvSatelliteCount = findViewById(R.id.tvSatelliteCount)
        tvMeasurementCount = findViewById(R.id.tvMeasurementCount)
        tvLoggingStatus = findViewById(R.id.tvLoggingStatus)

        // 设置导航
        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        val navController = navHostFragment.navController
        val bottomNav = findViewById<BottomNavigationView>(R.id.bottomNav)
        bottomNav.setupWithNavController(navController)

        // 检查权限
        checkPermissions()

        // 观察 ViewModel 数据
        observeViewModel()
    }

    private fun setupWindowInsets() {
        val rootLayout = findViewById<android.view.View>(R.id.container)
        val toolbar = findViewById<android.view.View>(R.id.toolbar)
        val bottomSpacer = findViewById<android.view.View>(R.id.bottomInsetSpacer)

        ViewCompat.setOnApplyWindowInsetsListener(rootLayout) { view, windowInsets ->
            val insets = windowInsets.getInsets(
                WindowInsetsCompat.Type.systemBars() or
                WindowInsetsCompat.Type.displayCutout()
            )

            // 工具栏顶部留出状态栏空间
            toolbar.setPadding(0, insets.top, 0, 0)

            // 底部占位 View 高度 = 系统导航栏高度
            bottomSpacer.updateLayoutParams {
                height = insets.bottom
            }

            // 左右留出刘海屏空间
            view.updatePadding(left = insets.left, right = insets.right)

            windowInsets
        }
    }

    private fun checkPermissions() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
            != PackageManager.PERMISSION_GRANTED
        ) {
            locationPermissionRequest.launch(
                arrayOf(
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION
                )
            )
        } else {
            viewModel.initializeIfPermitted()
        }
    }

    private fun observeViewModel() {
        viewModel.satellites.observe(this) { satellites ->
            val visible = satellites.size
            val used = satellites.count { it.usedInFix }
            tvSatelliteCount.text = "卫星 $used/$visible"
        }

        viewModel.measurementCount.observe(this) { count ->
            tvMeasurementCount.text = "测量 $count"
        }

        viewModel.isLogging.observe(this) { logging ->
            if (logging) {
                tvLoggingStatus.text = "● 记录中"
                tvLoggingStatus.setTextColor(0xFF00E5FF.toInt())
            } else {
                tvLoggingStatus.text = "○ 待机"
                tvLoggingStatus.setTextColor(0xFF9E9E9E.toInt())
            }
        }
    }
}
