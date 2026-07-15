<template>
	<AppLayout>
		<view class="my-page">
			<!-- 头像区域 -->
			<view class="avatar-section">
				<image
					src="/static/avatar1.png"
					class="user-avatar"
				/>
			</view>

			<!-- 昵称显示 -->
			<view class="nickname-section" v-if="userDetail.nickname">
				<text class="nickname-text">{{ userDetail.nickname }}</text>
			</view>

			<!-- 用户信息列表 -->
			<view class="info-section">
				<view v-if="userDetail.username" class="info-cell">
					<text class="info-cell-title">用户名</text>
					<text class="info-cell-desc">{{ userDetail.username }}</text>
				</view>
				<view v-if="userDetail.email" class="info-cell">
					<text class="info-cell-title">邮箱</text>
					<text class="info-cell-desc">{{ userDetail.email }}</text>
				</view>
				<view v-if="userDetail.intro" class="info-cell">
					<text class="info-cell-title">个人简介</text>
					<text class="info-cell-desc">{{ userDetail.intro }}</text>
				</view>
			</view>

			<!-- 操作按钮 -->
			<view class="action-section">
				<button
					@click="handleLogout"
					class="logout-btn"
				>
					退出登录
				</button>
			</view>
		</view>
	</AppLayout>
</template>

<script>
	import AppLayout from '@/pages/index/index.vue';
	import { getAuthToken, clearUserInfo, clearAuthToken } from '@/services/storage.js';
	import { getUserInfo } from '@/services/api.js';

	export default {
		components: {
			AppLayout
		},
		data() {
			return {
				userDetail: {},
				isLoading: false
			}
		},
		onLoad() {
			this.checkLogin();
			this.fetchUserInfo();
		},
		onShow() {
			this.checkLogin();
			this.fetchUserInfo();
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
			async fetchUserInfo() {
				const token = getAuthToken();
				if (!token) return;

				this.isLoading = true;
				try {
					const response = await getUserInfo(token);
					
					if (response.status === 0 && response.data) {
						this.userDetail = response.data;
					} else {
						uni.showToast({
							title: '加载用户信息失败',
							icon: 'error'
						});
					}
				} catch (error) {
					console.error('获取用户信息错误:', error);
					uni.showToast({
						title: '网络连接失败',
						icon: 'error'
					});
				} finally {
					this.isLoading = false;
				}
			},
			handleLogout() {
				uni.showModal({
					title: '确认退出',
					content: '确定要退出登录吗？',
					confirmText: '确认',
					cancelText: '取消',
					success: (res) => {
						if (res.confirm) {
							clearAuthToken();
							clearUserInfo();
							uni.showToast({
								title: '已退出登录',
								icon: 'success',
								duration: 1500
							});
							
							setTimeout(() => {
								uni.reLaunch({
									url: '/pages/login/login'
								});
							}, 1500);
						}
					}
				});
			}
		}
	}

</script>

<style scoped lang="scss">
.my-page {
	display: flex;
	flex-direction: column;
	min-height: 100vh;
	background-color: #ffffff;
}

.avatar-section {
	display: flex;
	justify-content: center;
	align-items: center;
	padding: 40rpx 0;
	background-color: #ffffff;
	border-bottom: 1rpx solid #f0f0f0;
}

.user-avatar {
	width: 120rpx;
	height: 120rpx;
	border-radius: 50%;
	background-color: #f5f5f5;
	object-fit: cover;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.nickname-section {
	display: flex;
	justify-content: center;
	align-items: center;
	padding: 20rpx 0;
	background-color: #ffffff;
}

.nickname-text {
	font-size: 36rpx;
	font-weight: bold;
	color: #333;
}

.info-section {
	background-color: #ffffff;
	margin-top: 20rpx;
	margin-bottom: 20rpx;
}

.info-cell {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	padding: 24rpx 30rpx;
	border-bottom: 1rpx solid #f0f0f0;
	gap: 8rpx;
}

.info-cell:last-child {
	border-bottom: none;
}

.info-cell-title {
	font-size: 26rpx;
	color: #666;
}

.info-cell-desc {
	font-size: 26rpx;
	color: #222;
	text-align: left;
	width: 100%;
	word-break: break-all;
}

.action-section {
	padding: 30rpx;
	background-color: #ffffff;
	display: flex;
	gap: 15rpx;
	position: relative;
	z-index: 10;
}

.logout-btn {
	width: 100%;
	line-height: 2;
	background-color: #ff4444 !important;
	color: #ffffff !important;
}
</style>

