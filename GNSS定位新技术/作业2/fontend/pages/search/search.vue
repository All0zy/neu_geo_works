<template>
	<AppLayout>
		<view class="search-container">
			<view class="scope-bar">
				<view
					v-for="(label, key) in scopeOptions"
					:key="key"
					class="scope-btn"
					:class="{ active: searchScope === key }"
					@tap="onScopeChange(key)"
				>
					{{ label }}
				</view>
			</view>
			<!-- 搜索框 -->
			<view class="search-box">
				<view class="search-wrapper">
					<input
						class="native-search-input"
						type="text"
						placeholder="输入地点进行查询"
						:value="searchInput"
						@input="onChangeValue"
						@confirm="onSearchSubmit"
						confirm-type="search"
						focus
					/>
					<view class="search-actions">
						<button class="search-action-btn" size="mini" @tap="onSearchSubmit">搜索</button>
						<button v-if="searchInput" class="search-action-btn search-clear-btn" size="mini" @tap="onClearSearch">清空</button>
					</view>
					<!-- 搜索加载指示 -->
					<view class="search-loading" v-if="searchLoading">
						<view class="loading-spinner"></view>
					</view>
				</view>
			</view>

			<!-- 搜索结果实时列表 -->
			<view class="results-section" v-if="resultList.length > 0">
				<scroll-view scroll-y class="results-list">
					<view 
						v-for="(item, index) in resultList"
						:key="index"
						class="result-item"
						@tap="onSelectSearchResult(item)"
					>
						<view class="result-body">
							<view class="result-main">
								<view class="result-header">
									<view class="result-name">{{ item.label }}</view>
									<view class="result-distance" v-if="Number.isFinite(item._placeData?.distance) && item._placeData.distance > 0">
										{{ formatDistance(item._placeData.distance) }}
									</view>
								</view>
								<view class="result-address">📍 {{ item.description }}</view>
							</view>
							<image
								v-if="getPoiPhotoUrl(item)"
								class="result-cover"
								:src="getPoiPhotoUrl(item)"
								mode="aspectFill"
								@error="onPoiPhotoError(item)"
							/>
						</view>
					<view class="result-tags" v-if="item._placeData?.type">
						<view 
							v-for="tag in item._placeData.type.split(';')"
							:key="tag"
							class="result-type"
						>
							{{ tag }}
						</view>
					</view>
					</view>
				</scroll-view>
			</view>

			<!-- 搜索历史 -->
			<view class="search-history" v-if="!searchInput && searchHistoryList.length > 0">
				<view class="history-title">搜索历史</view>
				<view class="history-list">
					<view 
						v-for="(item, index) in searchHistoryList"
						:key="index"
						class="history-item"
						@tap="onClickHistory(item)"
					>
						<text class="history-icon">🕐</text>
						<text class="history-text">{{ item.keyword }}</text>
						<text class="history-delete" @tap.stop="onDeleteHistory(item.keyword)">✕</text>
					</view>
				</view>
			</view>

			<!-- 空态提示 -->
			<view class="empty-state" v-if="!searchInput && resultList.length === 0 && searchHistoryList.length === 0">
				<text class="empty-text">输入地点名称进行搜索</text>
			</view>
		</view>
	</AppLayout>
</template>

<script>
	import AppLayout from '@/pages/index/index.vue';
	import * as amapService from '@/services/amap.js';
	import * as locationService from '@/services/location.js';
	import * as storageService from '@/services/storage.js';
	import { getAuthToken } from '@/services/storage.js';

	export default {
		components: {
			AppLayout
		},
		data() {
			return {
				searchInput: '', // 搜索框输入内容
				searchScope: 'nearby', // 搜索范围：附近/全国
				scopeOptions: {
					nearby: '附近',
					nationwide: '全国'
				},
				resultList: [], // 搜索结果列表
				searchLoading: false, // 是否正在搜索
				currentLocation: null, // 当前位置
				currentCity: '', // 城市搜索回退参数
				placeDataCache: {}, // 缓存搜索结果的完整数据
				poiImageErrorMap: {}, // 加载失败图片缓存
				searchHistoryList: [], // 搜索历史
				searchTimeout: null, // 搜索防抖定时器
				searchRequestId: 0 // 搜索请求ID，用于取消过期请求
			};
		},

		onLoad() {
			this.checkLogin();
			this.initLocation();
			this.loadSearchHistory();
		},
		onShow() {
			this.checkLogin();
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
		 * 初始化位置信息
		 */
		async initLocation() {
			try {
				this.currentLocation = await locationService.getCurrentLocation();
				// 通过逆地理编码获取实时的城市编码
				try {
					const cityCode = await amapService.getCityCode(
						this.currentLocation.longitude,
						this.currentLocation.latitude
					);
					this.currentCity = cityCode;
				} catch (codeErr) {
					console.warn('获取城市编码失败，使用默认值:', codeErr);
					this.currentCity = '010'; // 默认北京
				}
			} catch (err) {
				console.warn('无法获取当前位置:', err);
				// 使用默认位置（北京）
				this.currentLocation = {
					longitude: 116.403963,
					latitude: 39.915119
				};
				this.currentCity = '010'; // 默认北京
			}
		},

			/**
			 * 搜索框内容改变
			 */
			async onChangeValue(e) {
				const value = typeof e?.detail?.value === 'string'
					? e.detail.value
					: (typeof e?.value === 'string' ? e.value : '');
				this.searchInput = value;

				// 清除之前的防抖定时器
				if (this.searchTimeout) {
					clearTimeout(this.searchTimeout);
					this.searchTimeout = null;
				}

				if (!value || value.trim() === '') {
					// 让已发出的旧请求结果失效，避免清空后结果回流
					this.searchRequestId += 1;
					this.resultList = [];
					this.searchLoading = false;
					// 显示搜索历史
					this.loadSearchHistory();
					return;
				}

				// 防抖搜索（300ms延迟）
				this.searchTimeout = setTimeout(async () => {
					await this.performSearch(value);
				}, 300);
			},

			/**
			 * 搜索范围切换
			 */
			onScopeChange(nextScope) {
				if (nextScope !== 'nearby' && nextScope !== 'nationwide') {
					return;
				}
				if (this.searchScope === nextScope) {
					return;
				}

				this.searchScope = nextScope;

				const keyword = this.searchInput?.trim();
				if (keyword) {
					if (this.searchTimeout) {
						clearTimeout(this.searchTimeout);
						this.searchTimeout = null;
					}
					this.performSearch(keyword);
				}
			},

			/**
			 * 执行搜索
			 */
			async performSearch(keyword) {
				const requestId = ++this.searchRequestId;
				this.searchLoading = true;
				this.poiImageErrorMap = {};
				try {
					let result = { pois: [] };
					const hasCurrentLocation = this.currentLocation
						&& Number.isFinite(this.currentLocation.longitude)
						&& Number.isFinite(this.currentLocation.latitude);

					if (this.searchScope === 'nearby') {
						if (hasCurrentLocation) {
							try {
								result = await amapService.searchNearbyPlace(
									keyword,
									this.currentLocation.longitude,
									this.currentLocation.latitude,
									10000
								);
							} catch (nearbyErr) {
								console.warn('附近搜索失败，回退城市搜索:', nearbyErr);
							}
						}

						if (!Array.isArray(result.pois) || result.pois.length === 0) {
							result = await amapService.searchPlace(keyword, this.currentCity || '010');
						}
					} else {
						result = await amapService.searchPlace(keyword, '');
					}
					
					// 转换结果格式为搜索框可用的格式
					const pois = Array.isArray(result?.pois) ? result.pois : [];
					if (pois.length === 0) {
						if (requestId !== this.searchRequestId) {
							return;
						}
						this.resultList = [];
						return;
					}
					
					const mappedList = pois.map((poi) => {
						const [lngStr, latStr] = (poi.location || '').split(',');
						const longitude = parseFloat(lngStr);
						const latitude = parseFloat(latStr);

						if (!Number.isFinite(longitude) || !Number.isFinite(latitude)) {
							return null;
						}

						const apiDistance = Number(poi.distance);
						const distance = Number.isFinite(apiDistance) && apiDistance > 0
							? apiDistance
							: (this.currentLocation
								? amapService.calculateDistance(
									this.currentLocation.longitude,
									this.currentLocation.latitude,
									longitude,
									latitude
								)
								: 0);

						return {
							label: `${poi.name}`,
							value: poi.id,
							description: poi.address,
							// 扩展属性，用于导航
							_placeData: {
								id: poi.id,
								name: poi.name,
								address: poi.address,
								longitude: longitude,
								latitude: latitude,
								phone: poi.phone,
								website: poi.website,
								businessHours: poi.businessHours,
								type: poi.type,
								location: poi.location,
								distance: distance,
								photos: Array.isArray(poi.photos) ? poi.photos : []
							}
						};
					}).filter(Boolean);

					// 请求过期则不再更新页面状态
					if (requestId !== this.searchRequestId) {
						return;
					}

					this.resultList = mappedList;

					// 缓存完整数据
					this.resultList.forEach(item => {
						this.placeDataCache[item.value] = item._placeData;
					});

					// 保存搜索历史
					if (this.currentLocation) {
						storageService.addSearchHistory({
							keyword: keyword,
							location: `${this.currentLocation.longitude},${this.currentLocation.latitude}`
						});
					}

					// 发送搜索结果到home.vue
					uni.$emit('updateMapSearchResults', this.resultList.map(item => item._placeData));

				} catch (err) {
					if (requestId !== this.searchRequestId) {
						return;
					}
					console.error('搜索失败:', err);
					this.resultList = [];
					uni.showToast({
						title: err.message || '搜索失败，请稍后重试',
						icon: 'none',
						duration: 2000
					});
				} finally {
					if (requestId === this.searchRequestId) {
						this.searchLoading = false;
					}
				}
			},

			/**
			 * 加载搜索历史
			 */
			loadSearchHistory() {
				try {
					this.searchHistoryList = storageService.getSearchHistory().slice(0, 8);
				} catch (err) {
					console.warn('加载搜索历史失败:', err);
					this.searchHistoryList = [];
				}
			},

			/**
			 * 点击搜索历史项
			 */
			onClickHistory(item) {
				this.searchInput = item.keyword;
				this.performSearch(item.keyword);
			},

			/**
			 * 删除搜索历史
			 */
			onDeleteHistory(keyword) {
				storageService.clearSearchHistory(keyword);
				this.loadSearchHistory();
				uni.showToast({
					title: '已删除',
					icon: 'success',
					duration: 1000
				});
			},

			/**
			 * 清除搜索框
			 */
			onClearSearch() {
				if (this.searchTimeout) {
					clearTimeout(this.searchTimeout);
					this.searchTimeout = null;
				}
				this.searchRequestId += 1;
				this.searchInput = '';
				this.resultList = [];
				this.searchLoading = false;
				this.loadSearchHistory();
			},

			/**
			 * 搜索提交（用户按回车或点击搜索）
			 */
			async onSearchSubmit() {
				const keyword = this.searchInput?.trim();
				if (!keyword) {
					uni.showToast({
						title: '请输入搜索内容',
						icon: 'none',
						duration: 1500
					});
					return;
				}
				
				// 清除防抖定时器
				if (this.searchTimeout) {
					clearTimeout(this.searchTimeout);
				}

				// 立即执行搜索（不防抖）
				await this.performSearch(keyword);
			},

			/**
			 * 格式化距离
			 */
			formatDistance(meters) {
				return amapService.formatDistance(meters || 0);
			},

			/**
			 * 取POI首图
			 */
			getPoiPhotoUrl(item) {
				const placeData = item?._placeData;
				if (!placeData) return '';

				const firstPhoto = Array.isArray(placeData.photos) && placeData.photos.length > 0
					? placeData.photos[0]
					: null;
				const url = firstPhoto?.url || '';
				if (!url) return '';

				const key = placeData.id || item.value || url;
				return this.poiImageErrorMap[key] ? '' : url;
			},

			/**
			 * 图片加载失败兜底隐藏
			 */
			onPoiPhotoError(item) {
				const placeData = item?._placeData;
				if (!placeData) return;

				const firstPhoto = Array.isArray(placeData.photos) && placeData.photos.length > 0
					? placeData.photos[0]
					: null;
				const url = firstPhoto?.url || '';
				const key = placeData.id || item.value || url;
				if (!key) return;

				this.poiImageErrorMap = {
					...this.poiImageErrorMap,
					[key]: true
				};
			},

			/**
			 * 点击搜索结果的处理
			 */
			async onSelectSearchResult(item) {
				if (!item || !item.value) return;

				const placeData = this.placeDataCache[item.value] || item._placeData;
				if (!placeData) {
					console.warn('未找到地点缓存数据');
					return;
				}

				// 显示加载提示
				uni.showLoading({
					title: '获取地点信息中...',
					mask: true
				});

				try {
					// 通过逆地理编码获取更详细的地址信息
					const geoInfo = await amapService.regeo(placeData.longitude, placeData.latitude);
					
					// 增强地点数据
					const enhancedPlaceData = {
						...placeData,
						// 扩展的地理信息
						province: geoInfo.province,
						city: geoInfo.city,
						district: geoInfo.district,
						street: geoInfo.street,
						streetNumber: geoInfo.streetNumber,
						cityCode: geoInfo.cityCode,
						adCode: geoInfo.adCode,
						areaCode: geoInfo.areaCode,
						neighborhood: geoInfo.neighborhood,
						businessAreas: geoInfo.businessAreas
					};

					uni.hideLoading();

					// 导航到详情页面
					uni.navigateTo({
						url: `/pages/detail/detail?placeData=${encodeURIComponent(JSON.stringify(enhancedPlaceData))}`,
						success: () => {
							// 清空搜索框
							this.onClearSearch();
						},
						fail: (err) => {
							console.error('页面跳转失败:', err);
						}
					});
				} catch (err) {
					uni.hideLoading();
					console.error('获取地点信息失败:', err);
					
					// 降级处理：直接使用缓存数据导航
					uni.navigateTo({
						url: `/pages/detail/detail?placeData=${encodeURIComponent(JSON.stringify(placeData))}`,
						success: () => {
							this.onClearSearch();
						},
						fail: (err) => {
							console.error('页面跳转失败:', err);
						}
					});
				}
			}
		}
	};
</script>

<style scoped>
.search-container {
	flex: 1;
	display: flex;
	flex-direction: column;
	height: 100%;
	padding-bottom: 100rpx;
	position: relative;
}

/* 搜索框区域 */
.search-box {
	flex-shrink: 0;
	padding: 16rpx 32rpx;
	background-color: #fff;
	position: relative;
	z-index: 200;
	border-bottom: 1rpx solid #f0f0f0;
}

.scope-bar {
	display: flex;
	justify-content: center;
	gap: 12rpx;
	padding: 12rpx 24rpx;
	background-color: #fff;
	border-bottom: 1rpx solid #f0f0f0;
	z-index: 180;
	flex-shrink: 0;
}

.scope-bar .scope-btn {
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

.scope-bar .scope-btn:active {
	transform: scale(0.95);
}

.scope-bar .scope-btn.active {
	background-color: #0066cc;
	color: #fff;
	border-color: #0066cc;
}

.search-wrapper {
	position: relative;
}

.native-search-input {
	height: 72rpx;
	padding: 0 20rpx;
	border: 1rpx solid #d9d9d9;
	border-radius: 12rpx;
	font-size: 28rpx;
	background-color: #fff;
}

.search-actions {
	display: flex;
	gap: 12rpx;
	margin-top: 12rpx;
}

.search-action-btn {
	flex: 1;
	line-height: 1.8;
	font-size: 24rpx;
	background-color: #0066cc;
	color: #fff;
}

.search-clear-btn {
	background-color: #f2f2f2;
	color: #666;
}

.search-loading {
	position: absolute;
	right: 20rpx;
	top: 36rpx;
	transform: translateY(-50%);
	width: 24rpx;
	height: 24rpx;
	z-index: 10;
}

.loading-spinner {
	width: 20rpx;
	height: 20rpx;
	border: 2rpx solid #e0e0e0;
	border-top-color: #0066cc;
	border-radius: 50%;
	animation: spin 0.8s linear infinite;
}

@keyframes spin {
	to { transform: rotate(360deg); }
}

/* 搜索结果实时列表 */
.results-section {
	flex: 1;
	display: flex;
	flex-direction: column;
	overflow: hidden;
	border-top: 1rpx solid #f0f0f0;
}

.results-list {
	flex: 1;
	overflow-y: auto;
}

.result-item {
	padding: 24rpx 32rpx;
	border-bottom: 1rpx solid #f5f5f5;
	display: flex;
	flex-direction: column;
	gap: 8rpx;
	cursor: pointer;
	transition: background-color 0.2s;
}

.result-body {
	display: flex;
	align-items: flex-start;
	gap: 16rpx;
}

.result-item:active {
	background-color: #f9f9f9;
}

.result-main {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 8rpx;
}

.result-cover {
	width: 140rpx;
	height: 140rpx;
	border-radius: 12rpx;
	background-color: #f2f4f7;
	flex-shrink: 0;
}

.result-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 12rpx;
}

.result-name {
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
	line-height: 1.4;
}

.result-distance {
	font-size: 24rpx;
	color: #0066cc;
	font-weight: 500;
	white-space: nowrap;
}

.result-address {
	font-size: 24rpx;
	color: #999;
	line-height: 1.4;
}

.result-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 8rpx;
	margin-top: 4rpx;
}

.result-type {
	font-size: 22rpx;
	color: #fff;
	background-color: #0066cc;
	padding: 6rpx 12rpx;
	border-radius: 4rpx;
	display: inline-flex;
	flex-shrink: 0;
}

/* 搜索历史 */
.search-history {
	flex: 1;
	padding: 32rpx;
	overflow-y: auto;
}

.history-title {
	font-size: 24rpx;
	color: #999;
	margin-bottom: 16rpx;
	font-weight: 500;
}

.history-list {
	display: flex;
	flex-wrap: wrap;
	gap: 12rpx;
}

.history-item {
	display: flex;
	align-items: center;
	gap: 6rpx;
	padding: 12rpx 16rpx;
	background-color: #f5f5f5;
	border-radius: 20rpx;
	font-size: 26rpx;
	color: #666;
	transition: background-color 0.2s;
}

.history-item:active {
	background-color: #efefef;
}

.history-icon {
	font-size: 20rpx;
}

.history-text {
	flex: 1;
	max-width: 150rpx;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.history-delete {
	font-size: 18rpx;
	color: #ccc;
	margin-left: 4rpx;
	padding: 0 4rpx;
}

/* 空态提示 */
.empty-state {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	color: #ccc;
}

.empty-text {
	font-size: 28rpx;
}
</style>
