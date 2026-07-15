<template>
	<AppLayout>
		<!-- 围栏操作栏 -->
		<view class="fence-bar">
						<view v-if="fences.length > 0" class="fence-status" :class="{ 'danger-bg-bar': showAlertMask, 'safe-bg-bar': !showAlertMask }">
				<text v-if="showAlertMask" class="status-text">⚠️ 不在围栏内</text>
				<text v-else class="status-text">✓ 在围栏内</text>
			</view>
			<view class="fence-buttons">
				<view class="fence-btn" @tap="handleTakePhotoLocation">
					拍照定位
				</view>
				<view class="fence-btn" :class="{ active: editMode === 'rectangle' }" @tap="toggleRectangleMode">
					矩形围栏
				</view>
				<view class="fence-btn" :class="{ active: editMode === 'circle' }" @tap="toggleCircleMode">
					圆形围栏
				</view>
				<view class="fence-btn delete-btn" @tap="clearAllFences">
					清除围栏
				</view>
			</view>
		</view>

		<view class="map-container">
			<map id="miniMap" class="map" :longitude="currentLocation.longitude" :latitude="currentLocation.latitude"
				:markers="markers" :polyline="polylines" :scale="scale" @markertap="handleMarkerTap"
				@click="handleMapClick"></map>
		</view>
	</AppLayout>
</template>

<script>
import AppLayout from '@/pages/index/index.vue';
import * as locationService from '@/services/location.js';
import { getAuthToken, getFavoritePlaces, getPhotoLocations, addPhotoLocation, getFences, saveFences, clearFences } from '@/services/storage.js';
import * as fenceService from '@/services/fence.js';
export default {
	components: {
		AppLayout
	},
	data() {
		return {
			// 地图相关
			currentLocation: {
				longitude: 116.403963,
				latitude: 39.915119
			},
			markers: [],
			mapContext: null,
			scale: 16, // 地图缩放级别

			// 围栏相关
			fences: [],
			polylines: [],
			editMode: null, // 'rectangle' 或 'circle'
			rectanglePoints: [], // 用于矩形围栏的点
			circleCenter: null, // 用于圆形围栏的中心点
			photoLocations: [],

			// 警告相关
			showAlertMask: false,
			positionCheckInterval: null
		};
	},
	onLoad() {
		this.checkLogin();
		this.initLocation();
		this.loadFavorites();
		this.loadPhotoLocations();
		this.loadCachedFences();
		this.startPositionCheck();
	},
	onShow() {
		this.loadFavorites();
		this.loadPhotoLocations();
	},
	onReady() {
		this.mapContext = uni.createMapContext('miniMap', this);
	},
	onUnload() {
		this.stopPositionCheck();
		this.saveCachedFences();
	},
	methods: {
		checkLogin() {
			const token = getAuthToken();
			if (!token) {
				uni.reLaunch({ url: '/pages/login/login' });
			}
		},

		async initLocation() {
			try {
				this.currentLocation = await locationService.getCurrentLocation();
			} catch (err) {
				console.warn('获取位置失败:', err);
				this.currentLocation = { longitude: 116.403963, latitude: 39.915119 };
			}
			this.addCurrentLocationMarker();
		},

		loadFavorites() {
			try {
				const favorites = getFavoritePlaces();
				const favMarkers = (favorites || []).map(place => ({
					id: `fav-${place.id}`,
					latitude: place.latitude,
					longitude: place.longitude,
					title: place.name,
					iconPath: '/static/collect.png',
					width: 12,
					height: 12,
					customData: { ...place, sourceType: place.sourceType || 'favorite' }
				}));
				this.markers = [
					...favMarkers,
					...this.markers.filter(marker => !(marker.customData && marker.customData.sourceType === 'favorite'))
				];
			} catch (err) {
				console.error('加载收藏地点失败:', err);
			}
		},

		loadPhotoLocations() {
			try {
				const photoLocations = getPhotoLocations();
				this.photoLocations = photoLocations;
				const photoMarkers = photoLocations.map(item => this.createPhotoMarker(item));
				this.markers = [
					...photoMarkers,
					...this.markers.filter(marker => !(marker.customData && marker.customData.sourceType === 'photo'))
				];
			} catch (err) {
				console.error('加载拍照定位失败:', err);
			}
		},

		createPhotoMarker(photoItem) {
			return {
				id: photoItem.id,
				latitude: photoItem.latitude,
				longitude: photoItem.longitude,
				title: photoItem.name || '拍照定位',
				iconPath: '/static/photo.png',
				width: 24,
				height: 24,
				customData: {
					...photoItem,
					sourceType: 'photo'
				}
			};
		},

		loadCachedFences() {
			try {
				const cachedFences = getFences();
				if (cachedFences && cachedFences.length > 0) {
					this.fences = cachedFences;
					this.drawFences();
				}
			} catch (err) {
				console.error('加载缓存围栏失败:', err);
			}
		},

		saveCachedFences() {
			try {
				if (this.fences && this.fences.length > 0) {
					saveFences(this.fences);
				}
			} catch (err) {
				console.error('保存围栏数据失败:', err);
			}
		},

		addCurrentLocationMarker() {
			const exists = this.markers.some(m => m.id === 'current-location');
			if (!exists) {
				this.markers.push({
					id: 'current-location',
					latitude: this.currentLocation.latitude,
					longitude: this.currentLocation.longitude,
					title: '我的位置',
					iconPath: '/static/location.png',
					width: 36,
					height: 36,
					customData: {
						sourceType: 'current-location',
						name: '我的位置',
						latitude: this.currentLocation.latitude,
						longitude: this.currentLocation.longitude
					}
				});
			} else {
				this.markers = this.markers.map(marker => {
					if (marker.id !== 'current-location') {
						return marker;
					}

					return {
						...marker,
						latitude: this.currentLocation.latitude,
						longitude: this.currentLocation.longitude,
						customData: {
							...(marker.customData || {}),
							sourceType: 'current-location',
							name: '我的位置',
							latitude: this.currentLocation.latitude,
							longitude: this.currentLocation.longitude
						}
					};
				});
			}
		},

		async handleTakePhotoLocation() {
			try {
				const chooseResult = await new Promise((resolve, reject) => {
					uni.chooseImage({
						count: 1,
						sourceType: ['camera'],
						sizeType: ['compressed'],
						success: resolve,
						fail: reject
					});
				});

				const tempFilePath = chooseResult.tempFilePaths && chooseResult.tempFilePaths[0];
				if (!tempFilePath) {
					uni.showToast({ title: '未获取到照片', icon: 'none' });
					return;
				}

				const location = await locationService.getCurrentLocation();
				this.currentLocation = location;
				this.addCurrentLocationMarker();

				const saveResult = await new Promise((resolve, reject) => {
					uni.saveFile({
						tempFilePath,
						success: resolve,
						fail: reject
					});
				});

				const now = Date.now();
				const date = new Date(now);
				const pad2 = (num) => String(num).padStart(2, '0');
				const photoName = `${date.getFullYear()}年${pad2(date.getMonth() + 1)}月${pad2(date.getDate())}日 ${pad2(date.getHours())}:${pad2(date.getMinutes())}:${pad2(date.getSeconds())}`;
				const photoRecord = {
					id: `photo-${now}`,
					name: photoName,
					address: '拍照定位',
					longitude: location.longitude,
					latitude: location.latitude,
					location: `${location.longitude},${location.latitude}`,
					photoPath: saveResult.savedFilePath || tempFilePath,
					type: '拍照定位',
					sourceType: 'photo',
					createdAt: now
				};

				const saveSuccess = addPhotoLocation(photoRecord);
				if (!saveSuccess) {
					uni.showToast({ title: '保存拍照定位失败', icon: 'none' });
					return;
				}

				this.photoLocations.unshift(photoRecord);
				this.markers = [
					this.createPhotoMarker(photoRecord),
					...this.markers.filter(marker => marker.id !== photoRecord.id)
				];

				uni.showToast({ title: '拍照定位已保存', icon: 'success' });
			} catch (err) {
				if (err && err.errMsg && err.errMsg.includes('cancel')) {
					return;
				}
				console.error('拍照定位失败:', err);
				uni.showToast({ title: '拍照定位失败', icon: 'none' });
			}
		},

		handleMarkerTap(e) {
			const markerId = e.detail.markerId;
			const marker = this.markers.find(m => m.id === markerId);
			
			if (!marker || !marker.customData) {
				return;
			}
			
			// 所有marker点击都跳转到详情页
			uni.navigateTo({
				url: `/pages/detail/detail?placeData=${encodeURIComponent(JSON.stringify(marker.customData))}`
			});
		},

		/* ============ 围栏功能 ============ */

		/**
		 * 切换矩形围栏编辑模式
		 */
		toggleRectangleMode() {
			if (this.editMode === 'rectangle') {
				this.editMode = null;
				this.rectanglePoints = [];
				uni.showToast({ title: '取消矩形模式', icon: 'none' });
			} else {
				this.editMode = 'rectangle';
				this.rectanglePoints = [];
				this.circleCenter = null;
				uni.showToast({ title: '请点击地图选择两个点', icon: 'none' });
			}
		},

		/**
		 * 切换圆形围栏编辑模式
		 */
		toggleCircleMode() {
			if (this.editMode === 'circle') {
				this.editMode = null;
				this.circleCenter = null;
				uni.showToast({ title: '取消圆形模式', icon: 'none' });
			} else {
				this.editMode = 'circle';
				this.circleCenter = null;
				this.rectanglePoints = [];
				uni.showToast({ title: '请点击地图选择圆心', icon: 'none' });
			}
		},

		/**
		 * 地图点击事件处理
		 */
		handleMapClick(e) {
			if (!this.editMode) return;

			// 立即反馈
			uni.vibrateLong(); // 长振动反馈

			const { latitude, longitude } = e.detail;

			if (this.editMode === 'rectangle') {
				this.handleRectangleClick(latitude, longitude);
			} else if (this.editMode === 'circle') {
				this.handleCircleClick(latitude, longitude);
			}
		},

		/**
		 * 处理矩形围栏点击
		 */
		handleRectangleClick(latitude, longitude) {
			this.rectanglePoints.push({ latitude, longitude });
			this.updateSelectionMarkers();

			if (this.rectanglePoints.length === 1) {
				uni.showToast({ title: '✓ 已记录第一个点，请选择第二个点', icon: 'none', duration: 1500 });
			} else if (this.rectanglePoints.length === 2) {
				const fence = {
					id: `rect-${Date.now()}`,
					type: 'rectangle',
					point1: {
						latitude: this.rectanglePoints[0].latitude,
						longitude: this.rectanglePoints[0].longitude
					},
					point2: {
						latitude: latitude,
						longitude: longitude
					}
				};

				this.fences.push(fence);
				this.drawFences();
				this.clearSelectionMarkers();
				this.editMode = null;
				this.rectanglePoints = [];
				uni.showToast({ title: '✓ 矩形围栏已创建', icon: 'success', duration: 1500 });
			}
		},

		/**
		 * 处理圆形围栏点击
		 */
		handleCircleClick(latitude, longitude) {
			this.circleCenter = { latitude, longitude };
			this.updateSelectionMarkers();

			uni.showModal({
				title: '输入圆形半径',
				content: '单位：米（例如：100）',
				editable: true,
				placeholderText: '请输入半径',
				success: (res) => {
					if (res.confirm) {
						const radius = parseInt(res.content || '0');
						if (radius > 0) {
							const fence = {
								id: `circle-${Date.now()}`,
								type: 'circle',
								center: this.circleCenter,
								radius: radius
							};

							this.fences.push(fence);
							this.drawFences();
							this.clearSelectionMarkers();
							this.editMode = null;
							this.circleCenter = null;
							uni.showToast({ title: '✓ 圆形围栏已创建', icon: 'success', duration: 1500 });
						} else {
							uni.showToast({ title: '⚠️ 请输入有效的半径（大于0）', icon: 'none' });
						}
					} else {
						this.editMode = null;
						this.circleCenter = null;
						this.clearSelectionMarkers();
					}
				}
			});
		},

		/**
		 * 绘制所有围栏
		 */
		drawFences() {
			this.polylines = [];

			this.fences.forEach((fence) => {
				if (fence.type === 'rectangle') {
					const points = fenceService.getRectanglePolyline(
						{ latitude: fence.point1.latitude, longitude: fence.point1.longitude },
						{ latitude: fence.point2.latitude, longitude: fence.point2.longitude }
					);
					this.polylines.push({
						points: points,
						color: '#FF6347',
						width: 4
					});
				} else if (fence.type === 'circle') {
					let points = fenceService.getCirclePoints(fence.center, fence.radius);
					
					// 验证所有点的有效性，过滤掉南极/北极周围的异常点
					points = points.filter(point => {
						const isValidLat = point.latitude >= -85 && point.latitude <= 85;
						const isValidLon = point.longitude >= -180 && point.longitude <= 180;
						return isValidLat && isValidLon;
					});
					
					// 如果有有效点，才添加到polylines
					if (points.length >= 3) {
						// 确保闭合
						if (points[0].latitude !== points[points.length - 1].latitude ||
							points[0].longitude !== points[points.length - 1].longitude) {
							points.push(points[0]);
						}
						
						this.polylines.push({
							points: points,
							color: '#FF6347',
							width: 4
						});
					}
				}
			});
		},

		/**
		 * 清除所有围栏
		 */
		clearAllFences() {
			this.fences = [];
			this.polylines = [];
			this.editMode = null;
			this.rectanglePoints = [];
			this.circleCenter = null;
			clearFences(); // 同时清除本地缓存中的围栏数据
			uni.showToast({ title: '已清除所有围栏', icon: 'success' });
		},

		/**
		 * 开始位置检测
		 */
		startPositionCheck() {
			this.checkPosition(); // 初始检查一次
			this.positionCheckInterval = setInterval(() => {
				this.checkPosition();
			}, 1000); // 每秒检查一次
		},

		/**
		 * 停止位置检测
		 */
		stopPositionCheck() {
			if (this.positionCheckInterval) {
				clearInterval(this.positionCheckInterval);
			}
		},

		/**
		 * 检查是否在围栏内
		 */
		async checkPosition() {
			// 实时获取最新位置
			try {
				const location = await locationService.getCurrentLocation();
				this.currentLocation = location;
				this.addCurrentLocationMarker();
			} catch (err) {
				console.warn('获取位置失败:', err);
				// 继续使用旧位置
			}

			if (this.fences.length === 0) {
				// 没有围栏时，显示警告
				this.showAlertMask = true;
				return;
			}

			// 使用最新的位置进行判断
			const isInFence = fenceService.isPointInAnyFence(this.currentLocation, this.fences);

			if (!isInFence) {
				// 不在围栏内，显示警告
				this.showAlertMask = true;
			} else {
				// 在围栏内，隐藏遮罩
				this.showAlertMask = false;
			}
		},

		/**
		 * 更新选择点的标记
		 */
		updateSelectionMarkers() {
			const tempMarkers = [];

			if (this.editMode === 'rectangle') {
				this.rectanglePoints.forEach((point, index) => {
					tempMarkers.push({
						id: `temp-rect-${index}`,
						latitude: point.latitude,
						longitude: point.longitude,
						title: `点 ${index + 1}`,
						iconPath: '/static/set.png',
						width: 24,
						height: 24
					});
				});
			} else if (this.editMode === 'circle' && this.circleCenter) {
				tempMarkers.push({
					id: 'temp-circle-center',
					latitude: this.circleCenter.latitude,
					longitude: this.circleCenter.longitude,
					title: '圆心',
					iconPath: '/static/set.png',
					width: 24,
					height: 24
				});
			}

			// 合并原有markers和临时选择marker
			this.markers = this.markers.filter(m => !m.id.startsWith('temp-')).concat(tempMarkers);
		},

		/**
		 * 清除选择点的标记
		 */
		clearSelectionMarkers() {
			this.markers = this.markers.filter(m => !m.id.startsWith('temp-'));
		}
	}
};
</script>

<style scoped>
.map-container {
	flex: 1;
	width: 100%;
	position: relative;
	overflow: hidden;
	z-index: 1;
}

.map {
	width: 100%;
	height: 100%;
}

/* 围栏操作栏 */
.fence-bar {
	background-color: #fff;
	border-bottom: 1rpx solid #f0f0f0;
	display: flex;
	flex-direction: column;
	z-index: 100;
	flex-shrink: 0;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

/* 围栏状态显示 */
.fence-status {
	padding: 12rpx 24rpx;
	text-align: center;
	border-bottom: 1rpx solid #f0f0f0;
	flex-shrink: 0;
	transition: background-color 0.3s ease;
}

.fence-status.danger-bg-bar {
	background-color: #ff4444;
}

.fence-status.safe-bg-bar {
	background-color: #00aa00;
}

.status-text {
	font-size: 24rpx;
	font-weight: 500;
	color: #fff;
}

/* 围栏控制按钮组 */
.fence-buttons {
	display: flex;
	justify-content: space-around;
	gap: 8rpx;
	padding: 12rpx 12rpx;
	flex-shrink: 0;
}

/* 围栏按钮 */
.fence-btn {
	flex: 1;
	font-size: 22rpx;
	padding: 12rpx 16rpx;
	border-radius: 20rpx;
	background-color: #f0f0f0;
	color: #333;
	border: 1rpx solid #ddd;
	text-align: center;
	transition: all 0.2s;
	display: flex;
	align-items: center;
	justify-content: center;
}

.fence-btn:active {
	transform: scale(0.95);
}

.fence-btn.active {
	background-color: #0066cc;
	color: #fff;
	border-color: #0066cc;
}

.fence-btn.delete-btn {
	background-color: #ffeeee;
	color: #ff4444;
	border-color: #ffcccc;
}

.fence-btn.delete-btn:active {
	background-color: #ffdddd;
}
</style>