<template>
	<view
		class="detail-container"
		:style="{
			'--safe-top': safeAreaTop + 'px',
			'--nav-height': navBarHeight + 'px'
		}"
	>
		<!-- 顶部导航栏 -->
		<view class="detail-navbar nav-bar">
			<view class="detail-navbar-side" @tap="goBack">〈 返回</view>
			<view class="detail-navbar-title">{{ isPhotoLocation ? '拍照定位' : (place.name || '地点详情') }}</view>
			<view class="detail-navbar-side"></view>
		</view>

		<!-- 地图显示区域 -->
		<view class="map-section">
			<image
				v-if="isPhotoLocation && place.photoPath"
				class="photo-preview"
				:src="place.photoPath"
				mode="aspectFill"
				@tap="openPhotoPreview"
			/>
			<map 
				v-else
				id="miniMap"
				class="mini-map"
				:longitude="place.longitude"
				:latitude="place.latitude"
				:markers="markers"
				:polyline="routePolylines"
				:zoom="17"
			/>
		</view>

		<!-- 详情信息区域 -->
		<view class="info-section">
			<view class="info-card">
				<!-- 基础信息 -->
				<view class="info-item">
					<view class="info-label">📍 地址</view>
					<view class="info-value">{{ place.address }}</view>
				</view>

				<!-- 坐标 -->
				<view class="info-item">
					<view class="info-label">🧭 坐标</view>
					<view class="info-value">{{ place.longitude }}, {{ place.latitude }}</view>
				</view>

				<!-- 距离 -->
				<view class="info-item" v-if="distance">
					<view class="info-label">📏 距离</view>
					<view class="info-value">{{ distance }}</view>
				</view>

				<!-- 电话 -->
				<view class="info-item" v-if="place.phone">
					<view class="info-label">☎️ 电话</view>
					<view class="info-value">
						<text @tap="callPhone" class="phone-link">{{ place.phone }}</text>
					</view>
				</view>

				<!-- 网站 -->
				<view class="info-item" v-if="place.website">
					<view class="info-label">🌐 网站</view>
					<view class="info-value">
						<text @tap="openWebsite" class="link">{{ place.website }}</text>
					</view>
				</view>

				<!-- 营业时间 -->
				<view class="info-item" v-if="place.businessHours">
					<view class="info-label">🕐 营业时间</view>
					<view class="info-value">{{ place.businessHours }}</view>
				</view>

				<!-- 类型 -->
				<view class="info-item" v-if="place.type">
					<view class="info-label">🏷️ 类型</view>
					<view class="info-value">{{ place.type }}</view>
				</view>
			</view>
		</view>

		<!-- 操作栏 -->
		<view class="action-bar">
			<button
				v-if="isPhotoLocation"
				class="btn-collect"
				type="warn"
				@tap="deletePhotoLocation"
			>
				删除拍照定位
			</button>
			<button
				v-else
				class="btn-collect"
				:type="isFavorited ? 'primary' : 'default'"
				@tap="toggleFavorite"
			>
				{{ isFavorited ? '★ 已收藏' : '☆ 收藏' }}
			</button>
			<button
				class="btn-navigate"
				type="primary"
				@tap="startNavigation"
				:loading="navigating"
				:disabled="navigating"
			>
				🗺️ 导航
			</button>
		</view>

		<!-- 加载提示 -->
		<view class="loading-mask" v-if="loading">
			<view class="loading-content">
				<view class="spinner"></view>
				<text>加载中...</text>
			</view>
		</view>
	</view>
</template>

<script>
	import safeAreaMixin from '@/mixins/safe-area.js';
	import * as amapService from '@/services/amap.js';
	import * as locationService from '@/services/location.js';
	import * as storageService from '@/services/storage.js';
	import { getAuthToken, removePhotoLocation } from '@/services/storage.js';

	export default {
		mixins: [safeAreaMixin],
		data() {
			return {
				place: {
					id: '',
					name: '',
					address: '',
					longitude: 116.403963,
					latitude: 39.915119,
					phone: '',
					website: '',
					businessHours: '',
					type: '',
					location: ''
				},
				markers: [], // 地图标记
				routePolylines: [], // 地图路线
				distance: '', // 到当前位置的距离
				isFavorited: false, // 是否已收藏
				loading: false,
				navigating: false,
				currentLocation: null, // 当前位置
				isPhotoLocation: false
			};
		},
		onLoad(options) {
			this.checkLogin();
			this.loadPlaceData(options);
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
			 * 加载地点数据
			 */
			async loadPlaceData(options) {
				this.loading = true;
				try {
					// 1. 从路由参数解析地点信息
					if (options.placeData) {
						const placeData = JSON.parse(decodeURIComponent(options.placeData));
						this.isPhotoLocation = placeData.sourceType === 'photo';
						this.place = {
							...this.place,
							...placeData,
							location: placeData.location || `${placeData.longitude},${placeData.latitude}`
						};
					}

					// 2. 检查是否已收藏
					this.isFavorited = this.isPhotoLocation ? false : storageService.isFavorite(this.place.id);

					// 3. 获取当前位置并计算距离
					try {
						this.currentLocation = await locationService.getCurrentLocation();
						this.updateDistance();
					} catch (err) {
						console.warn('无法获取当前位置:', err);
					}

					// 4. 更新地图标记
					this.updateMapMarkers();

				} catch (err) {
					uni.showToast({
						title: '加载失败: ' + err.message,
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
			updateMapMarkers() {
				const lng = Number(this.place.longitude);
				const lat = Number(this.place.latitude);
				this.markers = [
					{
						latitude: lat,
						longitude: lng,
						title: this.place.name,
						iconPath: this.isPhotoLocation ? '/static/photo.png' : '/static/marker.png',
						width: 32,
						height: 32
					}
				];
			},

			/**
			 * 计算和显示距离
			 */
			updateDistance() {
				if (this.currentLocation && this.place.longitude && this.place.latitude) {
					const meters = amapService.calculateDistance(
						this.currentLocation.longitude,
						this.currentLocation.latitude,
						this.place.longitude,
						this.place.latitude
					);
					this.distance = amapService.formatDistance(meters);
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
			 * 切换收藏状态
			 */
			toggleFavorite() {
				if (this.isPhotoLocation) {
					return;
				}
				if (this.isFavorited) {
					const success = storageService.removeFavoritePlace(this.place.id);
					if (success) {
						this.isFavorited = false;
						uni.showToast({
							title: '已取消收藏',
							icon: 'success',
							duration: 1500
						});
					}
				} else {
					const success = storageService.addFavoritePlace({
						id: this.place.id,
						name: this.place.name,
						address: this.place.address,
						longitude: this.place.longitude,
						latitude: this.place.latitude,
						phone: this.place.phone,
						website: this.place.website,
						businessHours: this.place.businessHours,
						type: this.place.type,
						location: this.place.location,
						photos: Array.isArray(this.place.photos) ? this.place.photos : []
					});
					if (success) {
						this.isFavorited = true;
						uni.showToast({
							title: '已收藏',
							icon: 'success',
							duration: 1500
						});
					} else {
						uni.showToast({
							title: '已存在该收藏',
							icon: 'warning',
							duration: 1500
						});
					}
				}
			},

			/**
			 * 拨打电话
			 */
			callPhone() {
				if (!this.place.phone) return;
				uni.makePhoneCall({
					phoneNumber: this.place.phone,
					fail: (err) => {
						console.error('拨号失败:', err);
					}
				});
			},

			/**
			 * 打开网站
			 */
			openWebsite() {
				if (!this.place.website) return;
				let url = this.place.website;
				if (!url.startsWith('http')) {
					url = 'http://' + url;
				}
				uni.openURL({
					url: url,
					fail: (err) => {
						console.error('打开失败:', err);
					}
				});
			},

			openPhotoPreview() {
				if (!this.place.photoPath) {
					return;
				}
				uni.previewImage({
					current: this.place.photoPath,
					urls: [this.place.photoPath]
				});
			},

			deletePhotoLocation() {
				if (!this.isPhotoLocation) {
					return;
				}

				uni.showModal({
					title: '确认删除',
					content: '确定删除该拍照定位吗？',
					success: (res) => {
						if (!res.confirm) {
							return;
						}

						const success = removePhotoLocation(this.place.id);
						if (!success) {
							uni.showToast({
								title: '删除失败',
								icon: 'none',
								duration: 1500
							});
							return;
						}

						uni.showToast({
							title: '已删除拍照定位',
							icon: 'success',
							duration: 1500
						});
						setTimeout(() => {
							uni.navigateBack({ delta: 1 });
						}, 300);
					}
				});
			},

			/**
			 * 开始导航
			 */
			async startNavigation() {
				if (!this.currentLocation) {
					uni.showToast({
						title: '请先获取当前位置',
						icon: 'error',
						duration: 2000
					});
					return;
				}

				this.navigating = true;
				try {
					// 调用驾车路线规划
					const routeData = await amapService.drivingRoute(
						`${this.currentLocation.longitude},${this.currentLocation.latitude}`,
						`${this.place.longitude},${this.place.latitude}`,
						'0'
					);

					// 准备导航页面的数据
					const navigationData = {
						routeInfo: routeData,
						placeName: this.place.name,
						startLocationName: '当前位置',
						routeMode: 'taxi',
						strategy: '0',
						startLocation: {
							longitude: this.currentLocation.longitude,
							latitude: this.currentLocation.latitude
						},
						endLocation: {
							longitude: this.place.longitude,
							latitude: this.place.latitude
						}
					};

					// 跳转到导航页面
					uni.navigateTo({
						url: `/pages/navigation/navigation?routeData=${encodeURIComponent(JSON.stringify(navigationData))}`,
						fail: (err) => {
							console.error('导航页面打开失败:', err);
							uni.showToast({
								title: '打开导航页面失败',
								icon: 'error',
								duration: 2000
							});
						}
					});

				} catch (err) {
					console.error('路线规划失败:', err);
					uni.showToast({
						title: err.message || '路线规划失败',
						icon: 'error',
						duration: 2000
					});
				} finally {
					this.navigating = false;
				}
			}
		}
	};
</script>

<style scoped>
.detail-container {
	display: flex;
	flex-direction: column;
	height: 100vh;
	background-color: #f8f8f8;
	position: relative;
}

.detail-navbar {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	height: var(--nav-height);
	padding: var(--safe-top) 24rpx 0;
	box-sizing: border-box;
	display: flex;
	align-items: center;
	justify-content: space-between;
	background-color: #fff;
	border-bottom: 1rpx solid #f0f0f0;
}

.detail-navbar-side {
	width: 140rpx;
	font-size: 28rpx;
	color: #0066cc;
}

.detail-navbar-title {
	flex: 1;
	text-align: center;
	font-size: 30rpx;
	font-weight: 600;
	color: #222;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

/* 地图部分 */
.map-section {
    /*上边距留一个navbar的高度*/ 
	margin-top: var(--nav-height);
	flex-shrink: 0;
	height: 600rpx;
	overflow: hidden;
	background-color: #f0f0f0;
}

.mini-map {
	width: 100%;
	height: 100%;
}

.photo-preview {
	width: 100%;
	height: 100%;
}

/* 信息卡片 */
.info-section {
	flex: 1;
	overflow-y: auto;
	padding: 24rpx;
	box-sizing: border-box;
}

.info-card {
	background-color: #fff;
	border-radius: 12rpx;
	padding: 24rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.08);
}

.info-item {
	margin-bottom: 20rpx;
	padding-bottom: 20rpx;
	border-bottom: 1rpx solid #f0f0f0;
}

.info-item:last-child {
	margin-bottom: 0;
	padding-bottom: 0;
	border-bottom: none;
}

.info-label {
	font-size: 28rpx;
	color: #666;
	font-weight: 500;
	margin-bottom: 8rpx;
}

.info-value {
	font-size: 28rpx;
	color: #333;
	line-height: 1.5;
	word-wrap: break-word;
}

.phone-link,
.link {
	color: #0066cc;
	text-decoration: underline;
}

/* 操作栏 */
.action-bar {
	flex-shrink: 0;
	display: flex;
	gap: 16rpx;
	padding: 20rpx 24rpx;
	background-color: #fff;
	border-top: 1rpx solid #eee;
	box-sizing: border-box;
}

.btn-collect,
.btn-navigate {
	flex: 1;
	margin: 0;
	font-size: 28rpx;
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
	z-index: 100;
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
	to { transform: rotate(360deg); }
}

.loading-content text {
	color: #333;
	font-size: 28rpx;
}
.nav-bar{
    z-index: 999;
}
</style>
