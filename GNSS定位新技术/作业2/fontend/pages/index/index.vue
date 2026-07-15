<template>
	<view
		class="layout-container"
		:style="{
			'--safe-top': safeAreaTop + 'px',
			'--safe-bottom': safeAreaBottom + 'px',
			'--nav-height': navBarHeight + 'px',
			'--tab-height': tabBarHeight + 'px'
		}"
	>
		<!-- 导航栏 -->
		<view class="navbar-box">
			<view class="native-navbar">
				<text class="native-navbar-title">{{ currentTabName }}</text>
			</view>
		</view>

		<!-- 中间内容（不会被遮挡） -->
		<view class="content">
			<slot />
		</view>

		<!-- 底部 tabbar -->
		<view class="tabbar">
			<view class="native-tabbar">
				<view
					v-for="(item, index) in list"
					:key="index"
					class="native-tab-item"
					:class="{ active: value === item.value }"
					@tap="onChange(item.value)"
				>
					<text class="tab-icon">{{ item.iconText }}</text>
					<text class="tab-label">{{ item.ariaLabel }}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import safeAreaMixin from '@/mixins/safe-area.js';

	export default {
		mixins: [safeAreaMixin],
		data() {
			return {
				value: 'label_1',
				list: [
					{
						value: 'label_1',
						iconText: '🏠',
						ariaLabel: '首页',
						path: 'pages/home/home',
					},
					{
						value: 'label_search',
						iconText: '🔍',
						ariaLabel: '搜索',
						path: 'pages/search/search',
					},
					{
						value: 'label_2',
						iconText: '⭐',
						ariaLabel: '标记地点',
						path: 'pages/collect/collect',
					},
					{
						value: 'label_4',
						iconText: '👤',
						ariaLabel: '个人中心',
						path: 'pages/my/my',
					},
				],
			};
		},
		created() {
			// 从全局变量读取要设置的tabbar值
			const app = getApp();
			if (app.globalData && app.globalData.activeTabValue) {
				this.value = app.globalData.activeTabValue;
				// 清空全局变量
				app.globalData.activeTabValue = null;
			}
		},
		computed: {
			/**
			 * 获取当前选中标签页的名字
			 */
			currentTabName() {
				const currentTab = this.list.find(item => item.value === this.value);
				return currentTab ? currentTab.ariaLabel : '首页';
			}
		},
		methods: {
			onChange(e) {
				const selectedValue = e && e.value ? e.value : e;
				if (!selectedValue) return;
				
				const targetTab = this.list.find(item => item && item.value === selectedValue);
				if (!targetTab || !targetTab.path) return;
				
				// 立即更新高亮状态
				this.value = selectedValue;
				
				// 执行页面跳转
				this.performNavigation(targetTab);
			},

			performNavigation(targetTab) {
				if (!targetTab || !targetTab.path) return;
				
				// 将要设置的tabbar值存到全局变量
				const app = getApp();
				if (!app.globalData) {
					app.globalData = {};
				}
				app.globalData.activeTabValue = targetTab.value;
				
				// 使用reLaunch实现类似原生tabBar的黑屏切换效果
				uni.reLaunch({
					url: '/' + targetTab.path
				});
			}
		},
	};
</script>

<style scoped>
/* 外层布局容器（关键） */
.layout-container {
	display: flex;
	flex-direction: column;
	height: 100vh;
	box-sizing: border-box;
}

/* 导航栏 */
.navbar-box {
	width: 100%;
	flex-shrink: 0;
}

.native-navbar {
	height: var(--nav-height);
	padding-top: var(--safe-top);
	box-sizing: border-box;
	background: #ffffff;
	display: flex;
	align-items: center;
	justify-content: center;
	border-bottom: 1rpx solid #f0f0f0;
}

.native-navbar-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #222;
}

/* 内容区域 */
.content {
	display: flex;
	flex-direction: column;
	flex: 1;
	min-height: 0;
}

/* 底部tabbar */
.tabbar {
	width: 100%;
	flex-shrink: 0;
	background: #fff;
	z-index: 100;
}

.native-tabbar {
	display: flex;
	align-items: center;
	justify-content: space-around;
	height: var(--tab-height);
	padding-bottom: var(--safe-bottom);
	box-sizing: border-box;
	border-top: 1rpx solid #f0f0f0;
}

.native-tab-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 6rpx;
	color: #7a7a7a;
}

.native-tab-item.active {
	color: #0066cc;
}

.tab-icon {
	font-size: 28rpx;
	line-height: 1;
}

.tab-label {
	font-size: 22rpx;
	line-height: 1;
}
</style>