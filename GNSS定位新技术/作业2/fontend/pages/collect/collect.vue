<template>
	<AppLayout>
		<view class="collect-content">
			<view class="filter-bar">
				<view class="filter-btn" :class="{ active: displayMode === 'all' }" @tap="setDisplayMode('all')">全部</view>
				<view class="filter-btn" :class="{ active: displayMode === 'favorite' }" @tap="setDisplayMode('favorite')">收藏</view>
				<view class="filter-btn" :class="{ active: displayMode === 'photo' }" @tap="setDisplayMode('photo')">拍照</view>
			</view>

			<!-- 收藏列表 -->
			<view class="collect-list" v-if="filteredList.length > 0">
				<scroll-view scroll-y class="scroll-view">
					<view 
						v-for="(item, index) in filteredList"
						:key="item.id"
						class="collect-item"
						@tap="navigateToDetail(item)"
					>
						<view class="item-body">
							<!-- 地点信息 -->
							<view class="item-main">
								<view class="item-header">
									<view class="item-title">{{ item.name }}</view>
									<view class="item-distance" v-if="item.distance">
										{{ formatDistance(item.distance) }}
									</view>
								</view>

								<!-- 地址 -->
								<view class="item-address">
									📍 {{ item.address }}
								</view>

								<!-- 类型 -->
								<view class="item-type" v-if="item.type || item.sourceType === 'photo'">
									🏷️ {{ item.sourceType === 'photo' ? '拍照定位' : item.type }}
								</view>
							</view>
							<image
								v-if="getItemImageUrl(item)"
								class="item-cover"
								:src="getItemImageUrl(item)"
								mode="aspectFill"
								@error="onImageError(item)"
							/>
						</view>

						<!-- 操作按钮 -->
						<view class="item-actions">
							<button
								size="mini"
								type="primary"
								class="item-action-btn"
								@tap.stop="handleNavigation(item)"
							>
								导航
							</button>
							<button
								size="mini"
								class="item-action-btn item-action-btn-light"
								@tap.stop="handleRemove(item, index)"
							>
								{{ item.sourceType === 'photo' ? '删除拍照定位' : '取消收藏' }}
							</button>
						</view>
					</view>
				</scroll-view>
			</view>

			<!-- 空状态 -->
			<view class="empty-state" v-else>
				<view class="empty-icon">⭐</view>
				<view class="empty-text">{{ emptyText }}</view>
				<view class="empty-desc">搜索并收藏常用地点，或在首页使用拍照定位</view>
				<button
					type="primary"
					@tap="goToSearch"
					class="search-btn"
				>
					去搜索
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
	</AppLayout>
</template>

<script>
	import AppLayout from '@/pages/index/index.vue';
	import * as storageService from '@/services/storage.js';
	import * as locationService from '@/services/location.js';
	import * as amapService from '@/services/amap.js';
	import { getAuthToken } from '@/services/storage.js';

	export default {
		components: {
			AppLayout
		},
		data() {
			return {
					favoriteList: [],
					photoList: [],
				loading: false,
					currentLocation: null,
					imageErrorMap: {},
					displayMode: 'all'
			};
		},
			computed: {
				filteredList() {
					if (this.displayMode === 'favorite') {
						return this.favoriteList;
					}
					if (this.displayMode === 'photo') {
						return this.photoList;
					}
					const merged = [...this.favoriteList, ...this.photoList];
					return merged.sort((a, b) => (a.distance || 0) - (b.distance || 0));
				},
				emptyText() {
					if (this.displayMode === 'photo') {
						return '暂无拍照定位';
					}
					if (this.displayMode === 'favorite') {
						return '暂无收藏';
					}
					return '暂无地点数据';
				}
			},
		onLoad() {
			this.checkLogin();
				this.loadFavorites();
		},
		onShow() {
			this.checkLogin();
			// 每次显示时重新加载收藏列表
			this.loadFavorites();
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
			 * 加载收藏列表
			 */
			async loadFavorites() {
				this.loading = true;
				this.imageErrorMap = {};
				try {
					// 获取收藏列表
					this.favoriteList = (storageService.getFavoritePlaces() || []).map(item => ({
						...item,
						sourceType: 'favorite'
					}));
					this.photoList = (storageService.getPhotoLocations() || []).map(item => ({
						...item,
						sourceType: 'photo'
					}));

					// 获取当前位置用于计算距离
					try {
						this.currentLocation = await locationService.getCurrentLocation();
						
						// 计算每个收藏地点的距离
						[...this.favoriteList, ...this.photoList].forEach(place => {
							const meters = amapService.calculateDistance(
								this.currentLocation.longitude,
								this.currentLocation.latitude,
								place.longitude,
								place.latitude
							);
							place.distance = meters;
						});

						// 按距离排序
						this.favoriteList.sort((a, b) => (a.distance || 0) - (b.distance || 0));
						this.photoList.sort((a, b) => (a.distance || 0) - (b.distance || 0));
					} catch (err) {
						console.warn('无法获取当前位置，不计算距离:', err);
					}

				} catch (err) {
					console.error('加载收藏失败:', err);
					uni.showToast({
						title: '加载失败',
						icon: 'error',
						duration: 2000
					});
				} finally {
					this.loading = false;
				}
			},

			setDisplayMode(mode) {
				this.displayMode = mode;
			},

			/**
			 * 导航到地点详情页
			 */
			navigateToDetail(place) {
				uni.navigateTo({
					url: `/pages/detail/detail?placeData=${encodeURIComponent(JSON.stringify(place))}`,
					fail: (err) => {
						console.error('页面跳转失败:', err);
						uni.showToast({
							title: '跳转失败',
							icon: 'error',
							duration: 2000
						});
					}
				});
			},

			/**
			 * 处理导航
			 */
			async handleNavigation(place) {
				if (!this.currentLocation) {
					uni.showToast({
						title: '请先获取当前位置',
						icon: 'error',
						duration: 2000
					});
					return;
				}

				this.loading = true;
				try {
					// 规划路线
					const routeData = await amapService.drivingRoute(
						`${this.currentLocation.longitude},${this.currentLocation.latitude}`,
						`${place.longitude},${place.latitude}`,
						'0'
					);

					// 准备导航页面数据
					const navigationData = {
						routeInfo: routeData,
						placeName: place.name,
						startLocationName: '当前位置',
						routeMode: 'taxi',
						strategy: '0',
						startLocation: {
							longitude: this.currentLocation.longitude,
							latitude: this.currentLocation.latitude
						},
						endLocation: {
							longitude: place.longitude,
							latitude: place.latitude
						}
					};

					// 跳转到导航页面
					uni.navigateTo({
						url: `/pages/navigation/navigation?routeData=${encodeURIComponent(JSON.stringify(navigationData))}`,
						fail: (err) => {
							console.error('导航页面打开失败:', err);
							uni.showToast({
								title: '打开导航失败',
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
					this.loading = false;
				}
			},

			/**
			 * 移除收藏
			 */
			handleRemove(item, index) {
				if (item.sourceType === 'photo') {
					this.handleRemovePhoto(item.id);
					return;
				}

				uni.showModal({
					title: '确认删除',
					content: '确定要取消收藏这个地点吗？',
					success: (res) => {
						if (res.confirm) {
							const success = storageService.removeFavoritePlace(item.id);
							if (success) {
								this.favoriteList = this.favoriteList.filter(place => place.id !== item.id);
								uni.showToast({
									title: '已取消收藏',
									icon: 'success',
									duration: 1500
								});
							}
						}
					}
				});
			},

			handleRemovePhoto(photoId) {
				uni.showModal({
					title: '确认删除',
					content: '确定删除该拍照定位吗？',
					success: (res) => {
						if (!res.confirm) {
							return;
						}

						const success = storageService.removePhotoLocation(photoId);
						if (!success) {
							uni.showToast({
								title: '删除失败',
								icon: 'none',
								duration: 1500
							});
							return;
						}

						this.photoList = this.photoList.filter(place => place.id !== photoId);
						uni.showToast({
							title: '已删除拍照定位',
							icon: 'success',
							duration: 1500
						});
					}
				});
			},

			/**
			 * 格式化距离
			 */
			formatDistance(meters) {
				return amapService.formatDistance(meters);
			},

			getItemImageUrl(item) {
				if (!item) {
					return '';
				}

				let url = '';
				if (item.sourceType === 'photo' && item.photoPath) {
					url = item.photoPath;
				} else if (Array.isArray(item.photos) && item.photos.length > 0) {
					url = item.photos[0]?.url || '';
				}

				if (!url) {
					return '';
				}

				const key = item.id || url;
				return this.imageErrorMap[key] ? '' : url;
			},

			onImageError(item) {
				if (!item) {
					return;
				}
				const key = item.id;
				if (!key) {
					return;
				}

				this.imageErrorMap = {
					...this.imageErrorMap,
					[key]: true
				};
			},

			/**
			 * 去搜索页面
			 */
			goToSearch() {
				const app = getApp();
				if (!app.globalData) {
					app.globalData = {};
				}
				app.globalData.activeTabValue = 'label_1';
				
				uni.reLaunch({
					url: '/pages/home/home'
				});
			}
		}
	};
</script>

<style scoped>
.collect-content {
	flex: 1;
	display: flex;
	flex-direction: column;
	height: 100%;
	padding-bottom: 100rpx;
}

.filter-bar {
	display: flex;
	gap: 12rpx;
	padding: 16rpx 20rpx 8rpx;
	background-color: #fff;
	border-bottom: 1rpx solid #f0f0f0;
}

.filter-btn {
	flex: 1;
	text-align: center;
	font-size: 24rpx;
	padding: 10rpx 12rpx;
	border-radius: 16rpx;
	background-color: #f4f4f4;
	color: #444;
	border: 1rpx solid #e7e7e7;
}

.filter-btn.active {
	background-color: #0066cc;
	color: #fff;
	border-color: #0066cc;
}

/* 收藏列表 */
.collect-list {
	flex: 1;
	overflow: hidden;
}

.scroll-view {
	height: 100%;
	padding: 16rpx 0;
}

.collect-item {
	background-color: #fff;
	margin: 0 20rpx 12rpx 20rpx;
	padding: 20rpx;
	border-radius: 12rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
	transition: box-shadow 0.2s;
}

.item-body {
	display: flex;
	align-items: flex-start;
	gap: 14rpx;
}

.item-main {
	flex: 1;
	min-width: 0;
}

.item-cover {
	width: 132rpx;
	height: 132rpx;
	border-radius: 10rpx;
	background-color: #f2f4f7;
	flex-shrink: 0;
}

.collect-item:active {
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

/* 地点标题 */
.item-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 12rpx;
}

.item-title {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
	flex: 1;
}

.item-distance {
	font-size: 24rpx;
	color: #0066cc;
	font-weight: 500;
	margin-left: 12rpx;
}

/* 地址 */
.item-address {
	font-size: 24rpx;
	color: #666;
	margin-bottom: 8rpx;
	line-height: 1.5;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

/* 类型 */
.item-type {
	font-size: 22rpx;
	color: #999;
	margin-bottom: 12rpx;
}

/* 操作按钮 */
.item-actions {
	display: flex;
	gap: 12rpx;
	margin-top: 12rpx;
}

.item-action-btn {
	flex: 1;
	font-size: 24rpx;
	line-height: 1.8;
}

.item-action-btn-light {
	background-color: #f2f2f2;
	color: #666;
}

/* 空状态 */
.empty-state {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 60rpx 40rpx;
}

.empty-icon {
	font-size: 80rpx;
	margin-bottom: 20rpx;
	opacity: 0.5;
}

.empty-text {
	font-size: 32rpx;
	color: #333;
	margin-bottom: 12rpx;
	font-weight: 500;
}

.empty-desc {
	font-size: 24rpx;
	color: #999;
	margin-bottom: 40rpx;
	text-align: center;
}

.search-btn {
	width: 100%;
	max-width: 300rpx;
	font-size: 28rpx;
}

/* 加载状态 */
.loading-mask {
	position: fixed;
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
	animation: spin 0.8s linear infinite;
	margin-bottom: 20rpx;
}

@keyframes spin {
	to {
		transform: rotate(360deg);
	}
}

.loading-content text {
	font-size: 24rpx;
	color: #666;
	margin-top: 12rpx;
}
</style>
