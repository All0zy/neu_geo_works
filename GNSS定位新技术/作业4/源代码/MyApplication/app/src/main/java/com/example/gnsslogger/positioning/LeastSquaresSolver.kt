package com.example.gnsslogger.positioning

import com.example.gnsslogger.util.Constants
import kotlin.math.abs
import kotlin.math.sqrt

/**
 * 最小二乘法定位解算器
 * 使用线性化迭代法求解 4 个未知数：X, Y, Z, 接收机钟差
 */
class LeastSquaresSolver {

    companion object {
        private const val MAX_ITERATIONS = 10
        private const val CONVERGENCE_THRESHOLD = 0.01
        private const val MAX_DOP = 50.0

        fun solveLinearSystem(a: Array<DoubleArray>, b: DoubleArray): DoubleArray? {
            val n = b.size
            val augmented = Array(n) { i ->
                DoubleArray(n + 1) { j ->
                    if (j < n) a[i][j] else b[i]
                }
            }

            for (col in 0 until n) {
                var maxRow = col
                var maxVal = abs(augmented[col][col])
                for (row in col + 1 until n) {
                    if (abs(augmented[row][col]) > maxVal) {
                        maxVal = abs(augmented[row][col])
                        maxRow = row
                    }
                }

                if (maxRow != col) {
                    val temp = augmented[col]
                    augmented[col] = augmented[maxRow]
                    augmented[maxRow] = temp
                }

                if (abs(augmented[col][col]) < 1e-12) return null

                for (row in col + 1 until n) {
                    val factor = augmented[row][col] / augmented[col][col]
                    for (j in col..n) {
                        augmented[row][j] -= factor * augmented[col][j]
                    }
                }
            }

            val x = DoubleArray(n)
            for (i in n - 1 downTo 0) {
                var sum = augmented[i][n]
                for (j in i + 1 until n) {
                    sum -= augmented[i][j] * x[j]
                }
                x[i] = sum / augmented[i][i]
            }
            return x
        }

        fun computeDopFromEnuDirections(
            eastComponents: DoubleArray,
            northComponents: DoubleArray,
            upComponents: DoubleArray
        ): DOPValues {
            val n = eastComponents.size
            if (n < 4) return DOPValues(0.0, 0.0, 0.0, 0.0, 0.0)

            val m = 4
            val ntm = Array(m) { DoubleArray(m) { 0.0 } }
            for (i in 0 until n) {
                val row = doubleArrayOf(eastComponents[i], northComponents[i], upComponents[i], 1.0)
                for (r in 0 until m) {
                    for (c in r until m) {
                        ntm[r][c] += row[r] * row[c]
                    }
                }
            }
            for (r in 0 until m) {
                for (c in 0 until r) {
                    ntm[r][c] = ntm[c][r]
                }
            }

            val q = Array(m) { DoubleArray(m) }
            for (col in 0 until m) {
                val e = DoubleArray(m) { if (it == col) 1.0 else 0.0 }
                val qcol = solveLinearSystem(ntm, e) ?: return DOPValues(0.0, 0.0, 0.0, 0.0, 0.0)
                for (row in 0 until m) {
                    q[row][col] = qcol[row]
                }
            }

            val gdop = sqrt(abs(q[0][0] + q[1][1] + q[2][2] + q[3][3]))
            val pdop = sqrt(abs(q[0][0] + q[1][1] + q[2][2]))
            val hdop = sqrt(abs(q[0][0] + q[1][1]))
            val vdop = sqrt(abs(q[2][2]))
            val tdop = sqrt(abs(q[3][3]))
            return DOPValues(gdop, pdop, hdop, vdop, tdop)
        }
    }

    /**
     * 解算结果
     */
    data class Solution(
        val x: Double,              // ECEF X (m)
        val y: Double,              // ECEF Y (m)
        val z: Double,              // ECEF Z (m)
        val clockBiasMeters: Double,// 接收机钟差 (m)
        val gdop: Double,           // 几何精度因子
        val pdop: Double,           // 位置精度因子
        val hdop: Double,           // 水平精度因子
        val vdop: Double,           // 垂直精度因子
        val tdop: Double,           // 时间精度因子
        val residuals: List<Double>,// 残差
        val converged: Boolean,     // 是否收敛
        val iterations: Int,        // 迭代次数
    )

    /**
     * 执行最小二乘定位解算
     */
    fun solve(
        satellites: List<SatelliteData>,
        initialPosition: Triple<Double, Double, Double> = Triple(0.0, 0.0, 0.0)
    ): Solution? {
        if (satellites.size < 4) return null

        // 初始估计
        var x = initialPosition.first
        var y = initialPosition.second
        var z = initialPosition.third
        var clockBias = 0.0

        var converged = false
        var iterations = 0
        val n = satellites.size
        var h = Array(n) { DoubleArray(4) }
        var weights = DoubleArray(n)

        for (iter in 0 until MAX_ITERATIONS) {
            // 构建设计矩阵 H 和观测向量 deltaRho
            h = Array(n) { DoubleArray(4) }
            val deltaRho = DoubleArray(n)
            weights = DoubleArray(n)

            for (i in satellites.indices) {
                val sat = satellites[i]
                // 计算到卫星的距离
                val dx = sat.x - x
                val dy = sat.y - y
                val dz = sat.z - z
                val range = sqrt(dx * dx + dy * dy + dz * dz)

                if (range < 1.0) continue  // 避免除零

                // 设计矩阵行（方向余弦）
                h[i][0] = -dx / range
                h[i][1] = -dy / range
                h[i][2] = -dz / range
                h[i][3] = 1.0  // 钟差系数

                // 观测残差
                val predictedRange = range + clockBias - sat.clockBiasMeters
                deltaRho[i] = sat.pseudorange - predictedRange

                // 权重
                weights[i] = sat.weight
            }

            // 加权最小二乘
            val solution = solveWeightedLeastSquares(h, deltaRho, weights) ?: return null

            // 更新估计
            x += solution[0]
            y += solution[1]
            z += solution[2]
            clockBias += solution[3]

            iterations = iter + 1

            // 检查收敛
            val positionChange = sqrt(solution[0] * solution[0] + solution[1] * solution[1] + solution[2] * solution[2])
            if (positionChange < CONVERGENCE_THRESHOLD) {
                converged = true
                break
            }
        }

        // 计算 DOP 值
        val dopValues = calculateDOP(h, weights)

        // 计算最终残差
        val residuals = satellites.map { sat ->
            val dx = sat.x - x
            val dy = sat.y - y
            val dz = sat.z - z
            val range = sqrt(dx * dx + dy * dy + dz * dz)
            val predicted = range + clockBias - sat.clockBiasMeters
            sat.pseudorange - predicted
        }

        // 检查 DOP 是否合理
        if (dopValues.gdop > MAX_DOP) return null

        return Solution(
            x = x,
            y = y,
            z = z,
            clockBiasMeters = clockBias,
            gdop = dopValues.gdop,
            pdop = dopValues.pdop,
            hdop = dopValues.hdop,
            vdop = dopValues.vdop,
            tdop = dopValues.tdop,
            residuals = residuals,
            converged = converged,
            iterations = iterations,
        )
    }

    /**
     * 加权最小二乘求解
     */
    private fun solveWeightedLeastSquares(
        h: Array<DoubleArray>,
        deltaRho: DoubleArray,
        weights: DoubleArray
    ): DoubleArray? {
        val n = h.size
        val m = 4

        // 计算 H'W 和 H'WH
        val htw = Array(m) { DoubleArray(n) }
        val htwH = Array(m) { DoubleArray(m) }
        val htwDeltaRho = DoubleArray(m)

        // H'W
        for (i in 0 until m) {
            for (j in 0 until n) {
                htw[i][j] = h[j][i] * weights[j]
            }
        }

        // H'WH
        for (i in 0 until m) {
            for (j in 0 until m) {
                var sum = 0.0
                for (k in 0 until n) {
                    sum += htw[i][k] * h[k][j]
                }
                htwH[i][j] = sum
            }
        }

        // H'W * deltaRho
        for (i in 0 until m) {
            var sum = 0.0
            for (j in 0 until n) {
                sum += htw[i][j] * deltaRho[j]
            }
            htwDeltaRho[i] = sum
        }

        return solveLinearSystem(htwH, htwDeltaRho)
    }

    /** 计算 DOP 值
     * Q = (HᵀWH)⁻¹, 通过逐列求解 HᵀWH · qⱼ = eⱼ 得到
     */
    private fun calculateDOP(h: Array<DoubleArray>, weights: DoubleArray): DOPValues {
        val m = 4
        val n = h.size

        // 过滤零权重的卫星行
        val validIndices = (0 until n).filter { weights[it] > 0 && h[it][3] != 0.0 }
        if (validIndices.size < 4) return DOPValues(99.0, 99.0, 99.0, 99.0, 99.0)

        val nc = validIndices.size

        // 仅用有效行计算 N = HᵀWH
        val ntm = Array(m) { DoubleArray(m) { 0.0 } }
        for (idx in validIndices) {
            val w = weights[idx]
            val hi = h[idx]
            for (i in 0 until m) {
                for (j in i until m) {
                    ntm[i][j] += hi[i] * w * hi[j]
                }
            }
        }
        // 填充下三角
        for (i in 0 until m) {
            for (j in 0 until i) {
                ntm[i][j] = ntm[j][i]
            }
        }

        // 逐列求解 N · q = e 得到 Q = N⁻¹
        val q = Array(m) { DoubleArray(m) }
        for (col in 0 until m) {
            val e = DoubleArray(m) { if (it == col) 1.0 else 0.0 }
            val qcol = solveLinearSystem(ntm, e) ?: return DOPValues(99.0, 99.0, 99.0, 99.0, 99.0)
            for (row in 0 until m) {
                q[row][col] = qcol[row]
            }
        }

        val gdop = sqrt(abs(q[0][0] + q[1][1] + q[2][2] + q[3][3]))
        val pdop = sqrt(abs(q[0][0] + q[1][1] + q[2][2]))
        val hdop = sqrt(abs(q[0][0] + q[1][1]))
        val vdop = sqrt(abs(q[2][2]))
        val tdop = sqrt(abs(q[3][3]))

        return DOPValues(gdop, pdop, hdop, vdop, tdop)
    }

    data class DOPValues(
        val gdop: Double,
        val pdop: Double,
        val hdop: Double,
        val vdop: Double,
        val tdop: Double,
    )

    /**
     * 卫星数据
     */
    data class SatelliteData(
        val svid: Int,
        val x: Double,               // ECEF X (m)
        val y: Double,               // ECEF Y (m)
        val z: Double,               // ECEF Z (m)
        val pseudorange: Double,     // 伪距 (m)
        val clockBiasMeters: Double, // 卫星钟差 (m)
        val weight: Double = 1.0,    // 权重
    )
}
