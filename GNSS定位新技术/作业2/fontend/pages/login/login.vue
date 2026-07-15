<template>
	<view
		class="login-page"
		:style="{
			'--safe-top': safeAreaTop + 'px',
			'--nav-height': navBarHeight + 'px'
		}"
	>
		<!-- 顶部导航栏 -->
		<view class="login-navbar">
			<text class="login-navbar-title">登录</text>
		</view>

		<!-- 登录表单容器 -->
		<view class="login-container">
			<!-- 登录表单 -->
			<view class="login-form">
				<!-- 用户名输入框 -->
				<view class="form-group">
					<view class="field-label">用户名</view>
					<input
						class="native-input"
						placeholder="请输入用户名"
						:value="loginForm.username"
						@input="onUsernameInput"
					/>
					<view class="field-error" v-if="errors.username">{{ errors.username }}</view>
				</view>

				<!-- 密码输入框 -->
				<view class="form-group">
					<view class="field-label">密码</view>
					<input
						class="native-input"
						type="password"
						password
						placeholder="请输入密码"
						:value="loginForm.password"
						@input="onPasswordInput"
					/>
					<view class="field-error" v-if="errors.password">{{ errors.password }}</view>
				</view>

				<!-- 登录按钮 -->
				<view class="button-group">
					<button
						type="primary"
						:loading="isLoading"
						:disabled="isLoading"
						@click="handleLogin"
						class="login-btn"
					>
						{{ isLoading ? '登录中...' : '登录' }}
					</button>
				</view>

				<!-- 错误提示 -->
				<view v-if="loginError" class="error-alert">
					<view class="error-icon">⚠</view>
					<view class="error-text">{{ loginError }}</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import safeAreaMixin from '@/mixins/safe-area.js';
import { login } from '../../services/api.js';
import { setAuthToken, setUserInfo } from '../../services/storage.js';

export default {
	mixins: [safeAreaMixin],
	data() {
		return {
			loginForm: {
				username: '',
				password: ''
			},
			errors: {
				username: '',
				password: ''
			},
			loginError: '',
			isLoading: false
		};
	},
	methods: {
		onUsernameInput(e) {
			const value = typeof e?.detail?.value === 'string'
				? e.detail.value
				: (typeof e?.value === 'string' ? e.value : '');
			this.loginForm.username = value;
			this.validateUsername();
		},
		onPasswordInput(e) {
			const value = typeof e?.detail?.value === 'string'
				? e.detail.value
				: (typeof e?.value === 'string' ? e.value : '');
			this.loginForm.password = value;
			this.validatePassword();
		},
		validateUsername() {
			this.errors.username = '';
			const username = String(this.loginForm.username || '').trim();
			if (!username) {
				this.errors.username = '请输入用户名';
				return false;
			}
			return true;
		},
		validatePassword() {
			this.errors.password = '';
			const password = String(this.loginForm.password || '');
			if (!password) {
				this.errors.password = '请输入密码';
				return false;
			}
			if (password.length < 6) {
				this.errors.password = '密码长度至少为6位';
				return false;
			}
			return true;
		},
		validateForm() {
			const usernameValid = this.validateUsername();
			const passwordValid = this.validatePassword();
			return usernameValid && passwordValid;
		},
		async handleLogin() {
			
			this.loginError = '';

			if (!this.validateForm()) {
				return;
			}

			this.isLoading = true;
			try {
				const username = String(this.loginForm.username || '').trim();
				const password = String(this.loginForm.password || '');
				
				const response = await login(username, password);

				if (response.status === 0 && response.token) {
					setAuthToken(response.token);
					setUserInfo({
						username: username,
						loginTime: new Date().getTime()
					});

					uni.showToast({
						title: '登录成功',
						icon: 'success',
						duration: 1500
					});

					setTimeout(() => {
						uni.reLaunch({
							url: '/pages/home/home'
						});
					}, 1500);
				} else {
					this.loginError = response.message || '登录失败，请检查用户名和密码';
				}
			} catch (error) {
				console.error('登录错误:', error);
				this.loginError = error.message || '网络连接失败，请检查网络设置';
				uni.showToast({
					title: '登录失败',
					icon: 'error',
					duration: 2000
				});
			} finally {
				this.isLoading = false;
			}
		}
	},
	onShow() {
		this.loginForm.username = '';
		this.loginForm.password = '';
		this.loginError = '';
	}
};
</script>

<style scoped lang="scss">
.login-page {
	display: flex;
	flex-direction: column;
	height: 100vh;
	background-color: #f5f5f5;
	overflow: hidden;
}

.login-navbar {
	height: var(--nav-height);
	padding-top: var(--safe-top);
	box-sizing: border-box;
	background-color: #fff;
	display: flex;
	align-items: center;
	justify-content: center;
	border-bottom: 1rpx solid #eee;
}

.login-navbar-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #222;
}

.login-container {
	flex: 1;
    margin-top: 300rpx;
	padding: 30px 20px;
	display: flex;
	flex-direction: column;
	justify-content: flex-start;
	overflow: hidden;
}

.login-form {
	display: flex;
	flex-direction: column;
	gap: 20px;
	margin-top: 20px;
}

.form-group {
	display: flex;
	flex-direction: column;
	gap: 8px;

	.field-label {
		font-size: 14px;
		font-weight: 500;
		color: #333;
	}

	.native-input {
		height: 44px;
		padding: 0 12px;
		border: 1px solid #ddd;
		border-radius: 8px;
		background: #fff;
		font-size: 14px;
	}

	.field-error {
		font-size: 12px;
		color: #ff6b6b;
	}
}



.button-group {
	margin-top: 10px;

	.login-btn {
		width: 100%;
	}
}

.error-alert {
	display: flex;
	align-items: center;
	gap: 10px;
	padding: 12px 16px;
	background-color: #fff5f5;
	border-left: 4px solid #ff6b6b;
	border-radius: 4px;
	margin-top: 10px;

	.error-icon {
		font-size: 18px;
		color: #ff6b6b;
		font-weight: bold;
	}

	.error-text {
		font-size: 13px;
		color: #ff6b6b;
		flex: 1;
	}
}

</style>