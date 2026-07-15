/**
 * API服务 - 处理所有后端API请求
 */

const API_BASE_URL = 'http://39.104.209.252:3007/api';

/**
 * 发送HTTP请求的通用方法
 * @param {string} url 请求URL
 * @param {string} method 请求方法 GET/POST/PUT/DELETE
 * @param {object} data 请求数据
 * @param {object} headers 请求头
 * @returns {Promise}
 */
function request(url, method = 'GET', data = null, headers = {}) {
	return new Promise((resolve, reject) => {
		uni.request({
			url: url,
			method: method,
			data: data,
			header: {
				'Content-Type': 'application/x-www-form-urlencoded',
				...headers
			},
			success: (res) => {
				if (res.statusCode === 200 || res.statusCode === 201) {
					resolve(res.data);
				} else {
					reject({
						code: res.statusCode,
						message: res.data?.message || '请求失败'
					});
				}
			},
			fail: (err) => {
				console.error('请求失败:', err);
				reject({
					code: -1,
					message: err.errMsg || '网络连接失败'
				});
			}
		});
	});
}

/**
 * 用户登录
 * @param {string} username 用户名
 * @param {string} password 密码
 * @returns {Promise} 返回 {status, message, token}
 */
export function login(username, password) {
	const url = `${API_BASE_URL}/login`;
	const data = {
		username: username,
		password: password
	};
	return request(url, 'POST', data);
}

/**
 * 获取用户信息
 * @param {string} token 认证token
 * @returns {Promise} 返回 {status, message, data: {id, username, nickname, email, usericon, intro, status}}
 */
export function getUserInfo(token) {
	const url = 'http://39.104.209.252:3007/my/userinfo';
	return request(url, 'GET', null, {
		'authorization': token
	});
}

/**
 * 用户登出
 * @returns {Promise}
 */
export function logout() {
	// 仅做客户端登出处理，清除本地token
	return Promise.resolve({ message: '已登出' });
}
