<script>
	import { getAuthToken } from './services/storage.js';

	export default {
		onLaunch: function() {
			this.checkLoginStatus();
		},
		onShow: function() {
		},
		onHide: function() {
		},
		methods: {
			checkLoginStatus() {
				// 获取当前页面路由
				const pages = getCurrentPages();
				const currentPage = pages[pages.length - 1];
				const currentRoute = currentPage ? currentPage.route : '';

				// 检查是否已登录
				const token = getAuthToken();
				
				// 不需要登录的页面
				const whiteList = ['pages/login/login'];

				// 如果没有token且不在登录页面，则跳转到登录页面
				if (!token && !whiteList.includes(currentRoute)) {
					uni.reLaunch({
						url: '/pages/login/login'
					});
				}
			}
		},
		onPageNotFound() {
			// 页面不存在时的处理
			uni.navigateTo({
				url: '/pages/login/login'
			});
		}
	}
</script>

<style>
	/*每个页面公共css */
</style>
