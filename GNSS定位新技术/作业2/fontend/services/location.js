/**
 * 位置服务 - 获取当前用户位置信息
 */

/**
 * 获取当前位置坐标
 * @returns {Promise} 返回 {longitude, latitude, accuracy, address}
 */
export function getCurrentLocation() {
	return new Promise((resolve, reject) => {
		uni.getLocation({
			type: 'gcj02', // 使用高德坐标系
			success: (res) => {
				resolve({
					longitude: res.longitude,
					latitude: res.latitude,
					accuracy: res.accuracy,
					address: res.address || ''
				});
			},
			fail: (err) => {
				console.error('获取位置失败:', err);
				reject({
					code: err.code || -1,
					message: '获取位置信息失败，请检查位置权限'
				});
			}
		});
	});
}

