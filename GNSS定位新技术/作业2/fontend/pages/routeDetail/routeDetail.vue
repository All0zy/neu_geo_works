<template>
    <view class="route-detail-container">
        <view class="native-navbar">
            <view class="native-navbar-back" @tap="goBack">〈 返回</view>
            <view class="native-navbar-title">详细路线</view>
            <view class="native-navbar-back"></view>
        </view>

        <view class="map-section">
            <map
                id="routeDetailMap"
                class="route-map"
                :longitude="mapCenter.longitude"
                :latitude="mapCenter.latitude"
                :markers="markers"
                :polyline="routePolylines"
                :scale="zoom"
            />
        </view>

        <view class="steps-section">
            <view class="steps-header">
                <view class="steps-title">
                    <text v-if="getFirstAndLastStation().first">{{ getFirstAndLastStation().first }}</text>
                    <text v-if="getFirstAndLastStation().first && getFirstAndLastStation().last"> → </text>
                    <text v-if="getFirstAndLastStation().last">{{ getFirstAndLastStation().last }}</text>
                    <text v-if="!getFirstAndLastStation().first">路线明细</text>
                </view>
                <view class="steps-subtitle">{{ getRouteModeLabel(routeMode) }} · {{ formatDistance(routeInfo.distance) }} · {{ formatDuration(routeInfo.duration) }}</view>
            </view>

            <scroll-view scroll-y class="steps-list">
                <view
                    class="step-item"
                    :class="{ active: activeStepIndex === step.index, expanded: activeStepIndex === step.index }"
                    v-for="step in routeInfo.detailSteps"
                    :key="step.index"
                    @tap="onSelectStep(step)"
                >
                    <view class="step-index">{{ step.index }}</view>
                    <view class="step-main">
                        <view class="step-instruction">{{ step.instruction || '沿道路前进' }}</view>
                        <view class="step-meta">
                            <text v-if="step.road">{{ step.road }}</text>
                            <text v-if="step.distance">{{ formatDistance(step.distance) }}</text>
                            <text v-if="step.duration">{{ formatDuration(step.duration) }}</text>
                        </view>
                        
                        <!-- 公交站点信息展开 -->
                        <view v-if="activeStepIndex === step.index && step.stations && step.stations.length > 0" class="step-stations">
                            <view v-for="(station, idx) in step.stations" :key="idx" class="station-item">
                                <view :class="['station-type', 'type-' + station.type]">
                                    <text v-if="station.type === 'departure'" class="station-icon">📍</text>
                                    <text v-else-if="station.type === 'arrival'" class="station-icon">✓</text>
                                    <text v-else-if="station.type.startsWith('train')" class="station-icon">🚆</text>
                                    <text v-else class="station-icon">→</text>
                                </view>
                                <view class="station-info">
                                    <text class="station-name">{{ station.name }}</text>
                                    <text v-if="station.time" class="station-time">{{ station.time }}</text>
                                </view>
                            </view>
                        </view>
                    </view>
                </view>

                <view class="step-empty" v-if="!routeInfo.detailSteps.length">
                    暂无详细路线信息
                </view>
            </scroll-view>
        </view>

        <view class="loading-mask" v-if="loading">
            <view class="loading-content">
                <view class="spinner"></view>
                <text>加载详细路线中...</text>
            </view>
        </view>
    </view>
</template>

<script>
import * as amapService from '@/services/amap.js';

export default {
    data() {
        return {
            loading: false,
            routeMode: 'taxi',
            strategy: '0',
            startLocationName: '当前位置',
            placeName: '目的地',
            startLocation: {
                longitude: 116.403963,
                latitude: 39.915119
            },
            endLocation: {
                longitude: 116.403963,
                latitude: 39.915119
            },
            routeInfo: {
                distance: 0,
                duration: 0,
                steps: 0,
                coordinates: [],
                detailSteps: []
            },
            mapCenter: {
                longitude: 116.403963,
                latitude: 39.915119
            },
            markers: [],
            routePolylines: [],
            activeStepIndex: -1,
            zoom: 14
        };
    },

    onLoad(options) {
        this.loadRouteDetail(options);
    },

    methods: {
        async loadRouteDetail(options) {
            this.loading = true;
            try {
                if (options.detailData) {
                    const detailData = JSON.parse(decodeURIComponent(options.detailData));
                    this.startLocation = detailData.startLocation || this.startLocation;
                    this.endLocation = detailData.endLocation || this.endLocation;
                    this.startLocationName = detailData.startLocationName || '当前位置';
                    this.placeName = detailData.placeName || '目的地';
                    this.routeMode = detailData.routeMode || 'taxi';
                    this.strategy = detailData.strategy || '0';
                }

                const origin = `${this.startLocation.longitude},${this.startLocation.latitude}`;
                const destination = `${this.endLocation.longitude},${this.endLocation.latitude}`;

                let routeData;
                
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
                        routeData = await amapService.drivingRoute(origin, destination, this.strategy);
                        break;
                    case 'walking':
                        routeData = await amapService.walkingRoute(origin, destination);
                        break;
                    case 'transfer':
                        routeData = await amapService.transferRoute(
                            origin, 
                            destination, 
                            cityCode1,  // 起点城市代码（动态获取）
                            cityCode2   // 终点城市代码（动态获取）
                        );
                        break;
                    case 'riding':
                        routeData = await amapService.ridingRoute(origin, destination);
                        break;
                    default:
                        throw new Error('不支持的出行方式');
                }

                this.routeInfo = {
                    distance: routeData.distance || 0,
                    duration: routeData.duration || 0,
                    steps: routeData.steps || 0,
                    coordinates: routeData.coordinates || [],
                    detailSteps: Array.isArray(routeData.detailSteps) ? routeData.detailSteps : []
                };
                this.activeStepIndex = -1;

                this.updateMap();
            } catch (err) {
                console.error('加载详细路线失败:', err);
                uni.showToast({
                    title: err.message || '加载失败',
                    icon: 'none',
                    duration: 1800
                });
            } finally {
                this.loading = false;
            }
        },

        updateMap() {
            this.markers = [
                {
                    latitude: this.startLocation.latitude,
                    longitude: this.startLocation.longitude,
                    title: this.startLocationName,
                    iconPath: '/static/qd.png',
                    width: 30,
                    height: 30,
                    id: 'start'
                },
                {
                    latitude: this.endLocation.latitude,
                    longitude: this.endLocation.longitude,
                    title: this.placeName,
                    iconPath: '/static/zd.png',
                    width: 30,
                    height: 30,
                    id: 'end'
                }
            ];

            this.renderRoutePolylines();

            if ((this.routeInfo.coordinates || []).length > 0) {
                this.fitCenterByCoordinates(this.routeInfo.coordinates);
            }
        },

        fitCenterByCoordinates(coords) {
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

            this.mapCenter = {
                longitude: (minLng + maxLng) / 2,
                latitude: (minLat + maxLat) / 2
            };

            const maxRange = Math.max((maxLng - minLng) * 1.2 || 0.01, (maxLat - minLat) * 1.2 || 0.01);
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
            this.zoom = zoom;
        },

        renderRoutePolylines() {
            const fullPoints = this.routeInfo.coordinates || [];
            const polylines = [
                {
                    points: fullPoints,
                    color: '#9fc5f8',
                    width: 8,
                    dottedLine: false
                }
            ];

            const activeStep = (this.routeInfo.detailSteps || []).find(step => step.index === this.activeStepIndex);
            if (activeStep && Array.isArray(activeStep.coordinates) && activeStep.coordinates.length > 1) {
                polylines.push({
                    points: activeStep.coordinates,
                    color: '#0066cc',
                    width: 12,
                    dottedLine: false
                });

                const firstPoint = activeStep.coordinates[0];
                if (firstPoint) {
                    this.mapCenter = {
                        longitude: firstPoint.longitude,
                        latitude: firstPoint.latitude
                    };
                    this.zoom = Math.max(this.zoom, 16);
                }
            }

            this.routePolylines = polylines;
        },

        onSelectStep(step) {
            if (!step || !step.index) {
                return;
            }

            this.activeStepIndex = this.activeStepIndex === step.index ? -1 : step.index;
            this.renderRoutePolylines();
        },

        /**
         * 提取路线的第一个和最后一个车站
         * 用于显示"上车站-下车站"
         */
        getFirstAndLastStation() {
            const steps = this.routeInfo.detailSteps || [];
            let firstStation = null;
            let lastStation = null;

            // 遍历所有步骤，找到第一个和最后一个站点信息
            steps.forEach(step => {
                if (step.stations && step.stations.length > 0) {
                    // 找第一个上车站
                    if (!firstStation) {
                        for (const station of step.stations) {
                            if (station.type === 'departure' || station.type === 'metro_entrance' || station.type === 'train_departure') {
                                firstStation = station.name;
                                break;
                            }
                        }
                        // 如果没找到专门的departure，就取第一个station
                        if (!firstStation && step.stations[0]) {
                            firstStation = step.stations[0].name;
                        }
                    }
                    
                    // 找最后一个下车站
                    for (const station of step.stations) {
                        if (station.type === 'arrival' || station.type === 'metro_exit' || station.type === 'train_arrival') {
                            lastStation = station.name;
                        }
                    }
                    // 如果没找到专门的arrival，就取最后一个station
                    if (!lastStation && step.stations.length > 0) {
                        lastStation = step.stations[step.stations.length - 1].name;
                    }
                }
            });

            return {
                first: firstStation,
                last: lastStation
            };
        },

        formatDistance(meters) {
            return amapService.formatDistance(meters || 0);
        },

        formatDuration(seconds) {
            return amapService.formatDuration(seconds || 0);
        },

        getRouteModeLabel(mode) {
            const labels = {
                'taxi': '🚕 驾车',
                'walking': '🚶 步行',
                'transfer': '🚌 公共交通',
                'riding': '🚲 骑行'
            };
            return labels[mode] || '未知';
        },

        goBack() {
            uni.navigateBack({ delta: 1 });
        }
    }
};
</script>

<style scoped>
.route-detail-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background-color: #f5f7fb;
    position: relative;
    overflow: hidden;
}

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
    z-index: 100;
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

.map-section {
    margin-top: 170rpx;
    flex: 1;
    min-height: 240rpx;
    width: 100%;
}

.route-map {
    width: 100%;
    height: 100%;
}

.steps-section {
    height: 800rpx;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    background-color: #fff;
    border-top-left-radius: 22rpx;
    border-top-right-radius: 22rpx;
    margin-top: -12rpx;
    overflow: hidden;
}

.steps-header {
    padding: 20rpx 24rpx 14rpx;
    border-bottom: 1rpx solid #f0f0f0;
}

.steps-title {
    font-size: 30rpx;
    font-weight: 600;
    color: #1f2a37;
}

.steps-subtitle {
    margin-top: 8rpx;
    font-size: 24rpx;
    color: #5e6b7a;
}

.steps-list {
    height: 100%;
    padding: 0 18rpx;
}

.step-item {
    display: flex;
    gap: 14rpx;
    padding: 16rpx 6rpx;
    border-bottom: 1rpx solid #f3f4f6;
    transition: background-color 0.2s;
}

.step-item.active {
    background-color: #eef5ff;
}

.step-index {
    width: 40rpx;
    height: 40rpx;
    border-radius: 20rpx;
    background-color: #e8f1ff;
    color: #0066cc;
    font-size: 22rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2rpx;
}

.step-main {
    flex: 1;
    min-width: 0;
}

.step-instruction {
    font-size: 26rpx;
    color: #222;
    line-height: 1.5;
}

.step-meta {
    margin-top: 8rpx;
    display: flex;
    flex-wrap: wrap;
    gap: 14rpx;
    font-size: 22rpx;
    color: #6b7280;
}

.step-empty {
    text-align: center;
    color: #9ca3af;
    font-size: 24rpx;
    padding: 40rpx 0;
}

.step-stations {
    margin-top: 12rpx;
    padding: 12rpx;
    background-color: #f9fafb;
    border-radius: 8rpx;
    border-left: 3rpx solid #0066cc;
}

.station-item {
    display: flex;
    align-items: center;
    gap: 10rpx;
    padding: 8rpx 0;
    font-size: 22rpx;
}

.station-type {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 30rpx;
    height: 30rpx;
    border-radius: 50%;
    background-color: #e8f1ff;
    flex-shrink: 0;
}

.station-type.type-departure {
    background-color: #dbeafe;
    color: #0066cc;
}

.station-type.type-arrival {
    background-color: #dcfce7;
    color: #16a34a;
}

.station-type.type-train_departure,
.station-type.type-train_arrival,
.station-type.type-train_via {
    background-color: #fed7aa;
    color: #ea580c;
}

.station-icon {
    font-size: 18rpx;
}

.station-info {
    flex: 1;
    min-width: 0;
    display: flex;
    align-items: center;
    gap: 8rpx;
}

.station-name {
    color: #1f2a37;
    font-weight: 500;
}

.station-time {
    color: #9ca3af;
    font-size: 20rpx;
}

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
