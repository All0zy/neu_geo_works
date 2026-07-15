<template>
    <view class="navigation-container">
        <!-- 顶部导航栏 -->
        <view class="native-navbar">
            <view class="native-navbar-back" @tap="goBack">〈 返回</view>
            <view class="native-navbar-title">导航</view>
            <view class="native-navbar-back"></view>
        </view>

        <!-- 出行方式切换 -->
        <view class="mode-bar">
            <view
                v-for="(label, key) in routeModeOptions"
                :key="key"
                class="mode-btn"
                :class="{ active: routeMode === key }"
                @tap="switchRouteMode(key)"
            >
                {{ label }}
            </view>
        </view>

        <!-- 路线策略按钮组 -->
        <view class="strategy-bar" v-if="routeMode === 'taxi'">
            <view 
                v-for="(label, key) in strategyOptions"
                :key="key"
                class="strategy-btn"
                :class="{ active: routeInfo.strategy === key }"
                @tap="switchStrategy(key)"
            >
                {{ label }}
            </view>
        </view>

        <!-- 全屏地图 -->
        <view class="map-section">
            <map id="navigationMap" class="navigation-map" :longitude="mapCenter.longitude"
                :latitude="mapCenter.latitude" :markers="markers" :polyline="routePolylines" :scale="zoom"
                @markertap="onMarkerTap" />
        </view>

        <!-- 路线信息底部卡片 -->
        <view class="route-info-card">
            <view class="route-header">
                <view class="route-stat">
                    <view class="stat-icon">📏</view>
                    <view class="stat-content">
                        <view class="stat-label">距离</view>
                        <view class="stat-value">{{ formatDistance(routeInfo.distance) }}</view>
                    </view>
                </view>
                <view class="route-divider"></view>
                <view class="route-stat">
                    <view class="stat-icon">⏱️</view>
                    <view class="stat-content">
                        <view class="stat-label">耗时</view>
                        <view class="stat-value">{{ formatDuration(routeInfo.duration) }}</view>
                    </view>
                </view>
                <view class="route-divider"></view>
                <view class="route-stat">
                    <view class="stat-icon">📍</view>
                    <view class="stat-content">
                        <view class="stat-label">路段</view>
                        <view class="stat-value">{{ routeInfo.steps }}</view>
                    </view>
                </view>
            </view>

            <!-- 并行路线选项（仅驾车模式显示） -->
            <view class="parallel-routes" v-if="routeMode === 'taxi' && routeAlternatives && routeAlternatives.length > 1">
                <view class="parallel-routes-title">其他方案</view>
                <scroll-view scroll-x class="routes-scroll">
                    <view 
                        v-for="(alt, index) in routeAlternatives"
                        :key="index"
                        class="route-option"
                        :class="{ active: selectedRouteIndex === index }"
                        @tap="selectRouteAlternative(index)"
                    >
                        <view class="route-option-label">方案 {{ index + 1 }}</view>
                        <view class="route-option-time">{{ formatDuration(alt.duration) }}</view>
                        <view class="route-option-distance">{{ formatDistance(alt.distance) }}</view>
                    </view>
                </scroll-view>
            </view>

            <!-- 详情列表 -->
            <view class="route-details">
                <scroll-view scroll-y class="details-list">
                    <view class="detail-item">
                        <view class="detail-label">出发地</view>
                        <view class="detail-value">{{ startLocationName }}</view>
                    </view>
                    <view class="detail-item">
                        <view class="detail-label">目的地</view>
                        <view class="detail-value">{{ placeName }}</view>
                    </view>
                    <view class="detail-item" v-if="routeMode === 'taxi'">
                        <view class="detail-label">红绿灯</view>
                        <view class="detail-value">{{ routeInfo.traffic }} 个</view>
                    </view>
                </scroll-view>
            </view>

            <view class="route-action-bar">
                <button class="route-detail-btn" type="primary" size="mini" @tap="openRouteDetailPage">
                    详细路线
                </button>
            </view>
        </view>

        <!-- 定位按钮 -->
        <view class="location-btn" @tap="locateCurrentPosition">
            📍
        </view>

        <!-- 加载提示 -->
        <view class="loading-mask" v-if="loading">
            <view class="loading-content">
                <view class="spinner"></view>
                <text>加载导航中...</text>
            </view>
        </view>
    </view>
</template>

<script>
import * as amapService from '@/services/amap.js';
import * as locationService from '@/services/location.js';
import { getAuthToken } from '@/services/storage.js';

export default {
    data() {
        return {
            // 路线信息
            routeInfo: {
                distance: 0,
                duration: 0,
                steps: 0,
                coordinates: [],
                strategy: '0',
                traffic: 0
            },

            // 多个路线方案及选择
            routeAlternatives: [], // 所有路线备选方案
            selectedRouteIndex: 0, // 当前选中的方案索引

            routeMode: 'taxi',
            routeModeOptions: {
                taxi: '🚕驾车',
                walking: '🚶步行',
                transfer: '🚌公共交通',
                riding: '🚲骑乘'
            },

            // 位置信息
            startLocation: {
                longitude: 116.403963,
                latitude: 39.915119
            },
            mapCenter: {
                longitude: 116.403963,
                latitude: 39.915119
            },
            endLocation: {
                longitude: 116.403963,
                latitude: 39.915119
            },
            startLocationName: '当前位置',
            placeName: '目的地',
            
            // 策略选项
            strategyOptions: {
                '0': '⚡ 速度优先',
                '1': '💰 费用最低',
                '2': '📏 距离最短'
            },

            // 地图相关
            markers: [],
            routePolylines: [],
            mapContext: null,
            zoom: 15, // 地图缩放级别
            
            // UI相关
            loading: false, // 是否加载中
            locationUpdateInterval: null
        };
    },

    onLoad(options) {
        this.checkLogin();
        this.loadNavigationData(options);
    },

    onReady() {
        // 获取地图实例
        this.mapContext = uni.createMapContext('navigationMap', this);
    },

    onUnload() {
        this.stopRealtimeLocationUpdate();
    },

    methods: {
        checkLogin() {
            const token = getAuthToken();
            if (!token) {
                uni.reLaunch({
                    url: '/pages/login/login'
                });
            }
        },
        /**
         * 加载导航数据
         */
        async loadNavigationData(options) {
            this.loading = true;
            try {
                // 解析路由参数
                if (options.routeData) {
                    const data = JSON.parse(decodeURIComponent(options.routeData));
                    this.routeInfo = data.routeInfo;
                    this.placeName = data.placeName || '目的地';
                    this.startLocationName = data.startLocationName || '当前位置';
                    this.routeMode = data.routeMode || 'taxi';
					if (data.startLocation && Number.isFinite(data.startLocation.longitude) && Number.isFinite(data.startLocation.latitude)) {
						this.startLocation = {
							longitude: data.startLocation.longitude,
							latitude: data.startLocation.latitude
						};
					}
					if (data.endLocation && Number.isFinite(data.endLocation.longitude) && Number.isFinite(data.endLocation.latitude)) {
						this.endLocation = {
							longitude: data.endLocation.longitude,
							latitude: data.endLocation.latitude
						};
					}
					if (data.strategy && this.strategyOptions[data.strategy]) {
						this.routeInfo.strategy = data.strategy;
					}
                    
                    // 注意：不再使用路线末点作为终点备选，因为对于长距离路线（特别是公交）
                    // 路线末点可能是中间站点而非真正的目的地。应由调用方确保传递正确的终点。
                }

                // 获取当前位置
                try {
                    this.startLocation = await locationService.getCurrentLocation();
                } catch (err) {
                    console.warn('获取位置失败，使用默认位置');
                }

				// 使用当前定位与终点重新规划，避免沿用旧页面传入的过期路线
				await this.updateRouteByMode({
					strategy: this.routeMode === 'taxi' ? this.routeInfo.strategy : 'walking',
					silent: true
				});

                // 更新地图标记
                this.updateMarkers();

                // 启动实时位置更新
                this.startRealtimeLocationUpdate();

                // 绘制路线
                this.drawRoute();

            } catch (err) {
                console.error('加载导航数据失败:', err);
                uni.showToast({
                    title: '加载失败',
                    icon: 'error',
                    duration: 2000
                });
            } finally {
                this.loading = false;
            }
        },

        /**
         * 更新地图标记
         */
        updateMarkers() {
            this.markers = [];

            // 添加起点标记
            this.markers.push({
                latitude: this.startLocation.latitude,
                longitude: this.startLocation.longitude,
                title: this.startLocationName,
                iconPath: '/static/qd.png',
                width: 32,
                height: 32,
                id: 'start'
            });

            // 添加终点标记 - 使用明确的终点坐标而不是路线末点，避免长距离路线中终点偏离
            if (Number.isFinite(this.endLocation.longitude) && Number.isFinite(this.endLocation.latitude)) {
                this.markers.push({
                    latitude: this.endLocation.latitude,
                    longitude: this.endLocation.longitude,
                    title: this.placeName,
                    iconPath: '/static/zd.png',
                    width: 32,
                    height: 32,
                    id: 'end'
                });
            }

            // 最后添加当前实时位置，使其显示在最上层
            this.markers.push({
                latitude: this.startLocation.latitude,
                longitude: this.startLocation.longitude,
                title: '当前位置',
                iconPath: '/static/location.png',
                width: 32,
                height: 32,
                id: 'current-location'
            });
        },

        /**
         * 开启实时位置刷新
         */
        startRealtimeLocationUpdate() {
            this.stopRealtimeLocationUpdate();
            this.locationUpdateInterval = setInterval(() => {
                this.refreshCurrentLocation();
            }, 1000);
        },

        /**
         * 停止实时位置刷新
         */
        stopRealtimeLocationUpdate() {
            if (this.locationUpdateInterval) {
                clearInterval(this.locationUpdateInterval);
                this.locationUpdateInterval = null;
            }
        },

        /**
         * 刷新当前位置并更新地图标记
         */
        async refreshCurrentLocation() {
            try {
                const location = await locationService.getCurrentLocation();
                this.startLocation = location;
                this.updateMarkers();
            } catch (err) {
                console.warn('实时位置更新失败:', err);
            }
        },

        /**
         * 绘制路线
         */
        drawRoute() {
            if (!this.routeInfo.coordinates || this.routeInfo.coordinates.length === 0) {
                console.warn('没有路线坐标');
                return;
            }

            const polyline = {
                points: this.routeInfo.coordinates,
                color: '#0066cc',
                width: 10, // 增加线路粗度
                dottedLine: false
            };

            this.routePolylines = [polyline];

            // 计算路线范围并自动缩放
            this.autoFitRoute();
        },

        /**
         * 自动缩放地图以展示整个路线
         */
        autoFitRoute() {
            if (!this.routeInfo.coordinates || this.routeInfo.coordinates.length < 2) {
                return;
            }

            const coords = this.routeInfo.coordinates;
            
            // 计算完整的边界框（包含所有路线点）
            let minLng = coords[0].longitude;
            let maxLng = coords[0].longitude;
            let minLat = coords[0].latitude;
            let maxLat = coords[0].latitude;

            coords.forEach(coord => {
                minLng = Math.min(minLng, coord.longitude);
                maxLng = Math.max(maxLng, coord.longitude);
                minLat = Math.min(minLat, coord.latitude);
                maxLat = Math.max(maxLat, coord.latitude);
            });

            // 使用边界框的中点作为地图中心
            const centerLng = (minLng + maxLng) / 2;
            const centerLat = (minLat + maxLat) / 2;

            // 计算整个路线的范围，增加15%边距确保完整显示所有点
            let lngRange = maxLng - minLng;
            let latRange = maxLat - minLat;
            
            // 增加边距（15%）
            lngRange = lngRange * 1.15 || 0.01; // 如果为0则设为最小值
            latRange = latRange * 1.15 || 0.01;
            
            // 取较大的范围作为参考
            const maxRange = Math.max(lngRange, latRange);
            
            // 根据范围精确计算缩放级别
            let zoom = 18;
            if (maxRange > 0.001) zoom = 17;
            if (maxRange > 0.002) zoom = 16;
            if (maxRange > 0.005) zoom = 15;
            if (maxRange > 0.01) zoom = 14;
            if (maxRange > 0.02) zoom = 13;
            if (maxRange > 0.05) zoom = 12;
            if (maxRange > 0.1) zoom = 11;
            if (maxRange > 0.2) zoom = 10;
            if (maxRange > 0.5) zoom = 9;
            if (maxRange > 1) zoom = 8;
            if (maxRange > 2) zoom = 7;
            if (maxRange > 5) zoom = 6;
            
            // 更新地图中心点和缩放
            this.mapCenter = {
                longitude: centerLng,
                latitude: centerLat
            };
            this.zoom = zoom;
        },

        /**
         * 定位到当前位置
         */
        locateCurrentPosition() {
            this.refreshCurrentLocation().finally(() => {
                if (this.mapContext) {
                    this.mapContext.moveToLocation({
                        longitude: this.startLocation.longitude,
                        latitude: this.startLocation.latitude,
                    });
                }
            });
        },

        /**
         * 点击地图标记
         */
        onMarkerTap(e) {
            const markerId = e.detail.markerId;
            const marker = this.markers.find(m => m.id === markerId);
            if (marker) {
                uni.showToast({
                    title: marker.title,
                    icon: 'none',
                    duration: 1000
                });
            }
        },

        /**
         * 返回上一页
         */
        goBack() {
            uni.navigateBack({
                delta: 1
            });
        },

        /**
         * 格式化距离显示
         */
        formatDistance(meters) {
            return amapService.formatDistance(meters);
        },

        /**
         * 格式化时间显示
         */
        formatDuration(seconds) {
            return amapService.formatDuration(seconds);
        },

        /**
         * 切换路线策略
         */
        async switchStrategy(strategy) {
            if (this.routeMode !== 'taxi') {
                return;
            }
            if (this.routeInfo.strategy === strategy) {
                return; // 同一策略，不需要切换
            }
            await this.updateRouteByMode({ strategy });
        },

        /**
         * 切换步行/打车/公交/骑乘
         */
        async switchRouteMode(mode) {
            if (!this.routeModeOptions[mode] || this.routeMode === mode) {
                return;
            }

            this.routeMode = mode;
            
            // 根据出行方式设置策略
            if (mode === 'taxi') {
                this.routeInfo.strategy = '0'; // 驾车默认速度优先
            } else {
                this.routeInfo.strategy = mode; // 其他模式存储模式名称
            }

            await this.updateRouteByMode({
                strategy: this.routeInfo.strategy
            });
        },

        /**
         * 根据出行方式刷新路线
         */
        async updateRouteByMode({ strategy, silent = false } = {}) {
            if (!this.endLocation || !Number.isFinite(this.endLocation.longitude) || !Number.isFinite(this.endLocation.latitude)) {
                if (!silent) {
                    uni.showToast({ title: '终点信息缺失', icon: 'none', duration: 1500 });
                }
                return;
            }

            const origin = `${this.startLocation.longitude},${this.startLocation.latitude}`;
            const destination = `${this.endLocation.longitude},${this.endLocation.latitude}`;

            this.loading = true;
            try {
                let routeData;
                let modeLabel = '';
                
                // 对于公共交通，需要获取实时城市编码
                let cityCode1 = '010';
                let cityCode2 = '010';
                if (this.routeMode === 'transfer') {
                    try {
                        const codes = await amapService.getCityCodes(
                            this.startLocation.longitude,
                            this.startLocation.latitude,
                            this.endLocation.longitude,
                            this.endLocation.latitude
                        );
                        cityCode1 = codes.cityCode1;
                        cityCode2 = codes.cityCode2;
                    } catch (codeErr) {
                        console.warn('获取城市编码失败，使用默认值:', codeErr);
                    }
                }

                // 根据不同的出行方式调用对应的服务
                switch (this.routeMode) {
                    case 'taxi':
                        modeLabel = '驾车';
                        const routeStrategy = this.strategyOptions[strategy] ? strategy : '0';
                        routeData = await amapService.drivingRoute(origin, destination, routeStrategy);
                        break;
                    case 'walking':
                        modeLabel = '步行';
                        routeData = await amapService.walkingRoute(origin, destination);
                        break;
                    case 'transfer':
                        modeLabel = '公共交通';
                        routeData = await amapService.transferRoute(
                            origin, 
                            destination, 
                            cityCode1,  // 起点城市代码（动态获取）
                            cityCode2   // 终点城市代码（动态获取）
                        );
                        break;
                    case 'riding':
                        modeLabel = '骑行';
                        routeData = await amapService.ridingRoute(origin, destination);
                        break;
                    default:
                        throw new Error('不支持的出行方式');
                }

                if (!routeData) {
                    return;
                }

                // 如果是驾车且有多个方案，存储所有方案
                if (this.routeMode === 'taxi' && routeData.alternatives && routeData.alternatives.length > 0) {
                    this.routeAlternatives = routeData.alternatives;
                    this.selectedRouteIndex = 0;
                } else {
                    this.routeAlternatives = [];
                    this.selectedRouteIndex = 0;
                }

                this.routeInfo = {
                    distance: routeData.distance || 0,
                    duration: routeData.duration || 0,
                    steps: routeData.steps || 0,
                    coordinates: routeData.coordinates || [],
                    strategy: this.routeMode === 'taxi' ? strategy : this.routeMode,
                    traffic: this.routeMode === 'taxi' ? (routeData.traffic || 0) : 0
                };

                this.updateMarkers();
                this.drawRoute();

                if (!silent) {
                    uni.showToast({
                        title: `已切换${modeLabel}路线`,
                        icon: 'success',
                        duration: 900
                    });
                }
            } catch (err) {
                console.error('切换路线失败:', err);
                if (!silent) {
                    uni.showToast({
                        title: err.message || '切换路线失败',
                        icon: 'none',
                        duration: 1800
                    });
                }
            } finally {
                this.loading = false;
            }
        },

        /**
         * 选择不同的路线方案
         */
        selectRouteAlternative(index) {
            if (!this.routeAlternatives || index < 0 || index >= this.routeAlternatives.length) {
                return;
            }

            if (this.selectedRouteIndex === index) {
                return; // 已经选中该方案
            }

            this.selectedRouteIndex = index;
            const selectedRoute = this.routeAlternatives[index];

            // 更新主路线信息为选中的方案
            this.routeInfo = {
                distance: selectedRoute.distance || 0,
                duration: selectedRoute.duration || 0,
                steps: selectedRoute.steps || 0,
                coordinates: selectedRoute.coordinates || [],
                strategy: this.routeInfo.strategy,
                traffic: selectedRoute.traffic || 0
            };

            // 刷新地图标记和路线绘制
            this.updateMarkers();
            this.drawRoute();

            uni.showToast({
                title: `已切换至方案 ${index + 1}`,
                icon: 'none',
                duration: 800
            });
        },

        /**
         * 打开详细路线页面
         */
        openRouteDetailPage() {
            if (!this.endLocation || !Number.isFinite(this.endLocation.longitude) || !Number.isFinite(this.endLocation.latitude)) {
                uni.showToast({
                    title: '终点信息缺失',
                    icon: 'none',
                    duration: 1500
                });
                return;
            }

            const detailData = {
                startLocation: {
                    longitude: this.startLocation.longitude,
                    latitude: this.startLocation.latitude
                },
                endLocation: {
                    longitude: this.endLocation.longitude,
                    latitude: this.endLocation.latitude
                },
                placeName: this.placeName,
                startLocationName: this.startLocationName,
                routeMode: this.routeMode,
                strategy: this.routeMode === 'taxi' ? this.routeInfo.strategy : this.routeMode
            };

            uni.navigateTo({
                url: `/pages/routeDetail/routeDetail?detailData=${encodeURIComponent(JSON.stringify(detailData))}`,
                fail: (err) => {
                    console.error('打开详细路线页面失败:', err);
                    uni.showToast({
                        title: '打开失败',
                        icon: 'none',
                        duration: 1500
                    });
                }
            });
        },
    }
};
</script>

<style scoped>
.navigation-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background-color: #f0f0f0;
    position: relative;
    z-index: 1;
    overflow: hidden;
}

/* 导航栏 */
.native-navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 170rpx;
    padding: 76rpx 24rpx 0;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: #fff;
    border-bottom: 1rpx solid #f0f0f0;
    z-index: 200;
}

.native-navbar-back {
    width: 140rpx;
    font-size: 28rpx;
    color: #0066cc;
}

.native-navbar-title {
    flex: 1;
    text-align: center;
    font-size: 30rpx;
    font-weight: 600;
    color: #222;
}

/* 路线策略按钮组 */
.mode-bar {
    margin-top: 170rpx;
    display: flex;
    justify-content: center;
    gap: 12rpx;
    padding: 12rpx 24rpx;
    background-color: #fff;
    border-bottom: 1rpx solid #f0f0f0;
    z-index: 150;
    flex-shrink: 0;
}

.mode-bar .mode-btn {
    font-size: 24rpx;
    padding: 10rpx 20rpx;
    border-radius: 20rpx;
    background-color: #f0f0f0;
    color: #666;
    border: 1rpx solid #ddd;
    transition: all 0.2s;
    flex: 1;
    text-align: center;
}

.mode-bar .mode-btn:active {
    transform: scale(0.95);
}

.mode-bar .mode-btn.active {
    background-color: #0066cc;
    color: #fff;
    border-color: #0066cc;
}

.strategy-bar {
    display: flex;
    justify-content: center;
    gap: 12rpx;
    padding: 12rpx 24rpx;
    background-color: #fff;
    border-bottom: 1rpx solid #f0f0f0;
    z-index: 150;
    flex-shrink: 0;
}

.strategy-bar .strategy-btn {
    font-size: 24rpx;
    padding: 10rpx 20rpx;
    border-radius: 20rpx;
    background-color: #f0f0f0;
    color: #666;
    border: 1rpx solid #ddd;
    transition: all 0.2s;
    flex: 1;
    text-align: center;
}

.strategy-bar .strategy-btn:active {
    transform: scale(0.95);
}

.strategy-bar .strategy-btn.active {
    background-color: #0066cc;
    color: #fff;
    border-color: #0066cc;
}

.map-section{
    flex: 1;
    width: 100%;
    margin-bottom: 390rpx;
    overflow: hidden;
    z-index: 10;
}

/* 全屏地图 */
.navigation-map {
    flex: 1;
    width: 100%;
    height: 100%;
    z-index: 10;
}

/* 路线信息卡片 */
.route-info-card {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #fff;
    border-radius: 20rpx 20rpx 0 0;
    box-shadow: 0 -4rpx 12rpx rgba(0, 0, 0, 0.1);
    z-index: 100;
    height: 390rpx;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.route-header {
    display: flex;
    justify-content: space-around;
    align-items: center;
    padding: 24rpx;
    border-bottom: 1rpx solid #f0f0f0;
    flex-shrink: 0;
}

.route-stat {
    display: flex;
    align-items: center;
    gap: 8rpx;
    flex: 1;
}

.stat-icon {
    font-size: 32rpx;
}

.stat-content {
    display: flex;
    flex-direction: column;
}

.stat-label {
    font-size: 20rpx;
    color: #999;
}

.stat-value {
    font-size: 28rpx;
    font-weight: bold;
    color: #0066cc;
}

.route-divider {
    width: 1rpx;
    height: 40rpx;
    background-color: #eee;
    margin: 0 4rpx;
}

/* 展开/收起按钮 */
.route-toggle {
    text-align: center;
    padding: 12rpx;
    border-bottom: 1rpx solid #f0f0f0;
    font-size: 24rpx;
    color: #0066cc;
    cursor: pointer;
    flex-shrink: 0;
}

/* 详情列表 */
.route-details {
    flex: 1;
    overflow: hidden;
}

.route-action-bar {
    padding: 14rpx 24rpx 18rpx;
    border-top: 1rpx solid #f0f0f0;
    background-color: #fff;
}

.route-detail-btn {
    width: 100%;
    line-height: 1.9;
    font-size: 24rpx;
}

.details-list {
    height: 100%;
    overflow-y: auto;
}

.detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12rpx 24rpx;
    border-bottom: 1rpx solid #f5f5f5;
}

.detail-label {
    font-size: 24rpx;
    color: #666;
    font-weight: 500;
}

.detail-value {
    font-size: 26rpx;
    color: #333;
    text-align: right;
    max-width: 50%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* 并行路线选项 */
.parallel-routes {
    flex-shrink: 0;
    padding: 12rpx 0;
    background-color: #f9f9f9;
    border-bottom: 1rpx solid #f0f0f0;
}

.parallel-routes-title {
    font-size: 22rpx;
    color: #999;
    padding: 8rpx 24rpx 4rpx;
}

.routes-scroll {
    display: flex;
    width: 100%;
    padding: 0 24rpx;
}

.route-option {
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4rpx;
    margin-right: 12rpx;
    padding: 10rpx 14rpx;
    border-radius: 8rpx;
    background-color: #fff;
    border: 2rpx solid #ddd;
    min-width: 120rpx;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
}

.route-option.active {
    background-color: #0066cc;
    border-color: #0066cc;
}

.route-option:active {
    transform: scale(0.95);
}

.route-option-label {
    font-size: 20rpx;
    font-weight: bold;
    color: #333;
}

.route-option.active .route-option-label {
    color: #fff;
}

.route-option-time {
    font-size: 24rpx;
    color: #0066cc;
    font-weight: bold;
}

.route-option.active .route-option-time {
    color: #fff;
}

.route-option-distance {
    font-size: 18rpx;
    color: #999;
}

.route-option.active .route-option-distance {
    color: #ddd;
}

/* 定位按钮 */
.location-btn {
    position: fixed;
    bottom: 410rpx;
    right: 16rpx;
    width: 56rpx;
    height: 56rpx;
    background-color: #fff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32rpx;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.15);
    z-index: 50;
    transition: transform 0.2s;
}

.location-btn:active {
    transform: scale(0.95);
}

/* 加载状态 */
.loading-mask {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 200;
}

.loading-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    background-color: #fff;
    border-radius: 16rpx;
    padding: 40rpx;
}

.spinner {
    width: 50rpx;
    height: 50rpx;
    border: 4rpx solid #e0e0e0;
    border-top-color: #0066cc;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16rpx;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.loading-content text {
    color: #333;
    font-size: 28rpx;
}
</style>
