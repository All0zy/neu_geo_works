/**
 * 本地存储服务 - 管理地点收藏等数据
 */

const STORAGE_KEYS = {
	FAVORITE_PLACES: 'favorite_places', // 收藏的地点
	PHOTO_LOCATIONS: 'photo_locations', // 拍照定位
	SEARCH_HISTORY: 'search_history', // 搜索历史
	AUTH_TOKEN: 'auth_token', // 认证token
	USER_INFO: 'user_info', // 用户信息
	FENCES: 'fences' // 围栏数据
};

/**
 * 保存地点到收藏
 * @param {object} place 地点信息 {id, name, address, longitude, latitude, phone, website}
 * @returns {boolean} 是否保存成功
 */
export function addFavoritePlace(place) {
	try {
		let favorites = getFavoritePlaces();
		
		// 检查是否已存在
		const exists = favorites.some(p => p.id === place.id);
		if (exists) {
			return false; // 已存在则不重复添加
		}
		const newPlace = {
			...place,
			favoritedAt: new Date().getTime()
		};

		favorites.unshift(newPlace); // 新添加的放在最前面
		uni.setStorageSync(STORAGE_KEYS.FAVORITE_PLACES, favorites);
		return true;
	} catch (err) {
		return false;
	}
}

/**
 * 获取所有收藏的地点
 * @returns {array} 收藏地点列表
 */
export function getFavoritePlaces() {
	try {
		const data = uni.getStorageSync(STORAGE_KEYS.FAVORITE_PLACES);
		return data ? JSON.parse(JSON.stringify(data)) : [];
	} catch (err) {
		return [];
	}
}

/**
 * 保存拍照定位点
 * @param {object} location 拍照定位信息
 * @returns {boolean} 是否保存成功
 */
export function addPhotoLocation(location) {
	try {
		let photoLocations = getPhotoLocations();
		const exists = photoLocations.some(item => item.id === location.id);
		if (exists) {
			return false;
		}

		const newLocation = {
			...location,
			sourceType: 'photo',
			createdAt: location.createdAt || new Date().getTime()
		};

		photoLocations.unshift(newLocation);
		uni.setStorageSync(STORAGE_KEYS.PHOTO_LOCATIONS, photoLocations);
		return true;
	} catch (err) {
		return false;
	}
}

/**
 * 获取拍照定位点
 * @returns {array}
 */
export function getPhotoLocations() {
	try {
		const data = uni.getStorageSync(STORAGE_KEYS.PHOTO_LOCATIONS);
		return data ? JSON.parse(JSON.stringify(data)) : [];
	} catch (err) {
		return [];
	}
}

/**
 * 删除拍照定位点
 * @param {string} photoId 拍照定位ID
 * @returns {boolean}
 */
export function removePhotoLocation(photoId) {
	try {
		let photoLocations = getPhotoLocations();
		const originalLength = photoLocations.length;
		photoLocations = photoLocations.filter(item => item.id !== photoId);

		if (photoLocations.length < originalLength) {
			uni.setStorageSync(STORAGE_KEYS.PHOTO_LOCATIONS, photoLocations);
			return true;
		}
		return false;
	} catch (err) {
		return false;
	}
}

/**
 * 检查地点是否已收藏
 * @param {string} placeId 地点ID
 * @returns {boolean}
 */
export function isFavorite(placeId) {
	const favorites = getFavoritePlaces();
	return favorites.some(p => p.id === placeId);
}

/**
 * 添加搜索历史记录
 * @param {object} item {keyword, location, timestamp}
 * @returns {void}
 */
export function addSearchHistory(item) {
	try {
		let history = getSearchHistory();
		
		// 移除重复的相同关键词
		history = history.filter(h => h.keyword !== item.keyword);
		
		const newItem = {
			...item,
			timestamp: new Date().getTime()
		};
		
		history.unshift(newItem);
		
		// 只保留最近100条
		history = history.slice(0, 100);
		uni.setStorageSync(STORAGE_KEYS.SEARCH_HISTORY, history);
	} catch (err) {
	}
}

/**
 * 获取搜索历史
 * @returns {array}
 */
export function getSearchHistory() {
	try {
		const data = uni.getStorageSync(STORAGE_KEYS.SEARCH_HISTORY);
		return data ? JSON.parse(JSON.stringify(data)) : [];
	} catch (err) {
		return [];
	}
}

/**
 * 清除搜索历史
 * @param {string} keyword 要删除的关键词，如不提供则清空全部
 * @returns {void}
 */
export function clearSearchHistory(keyword) {
	try {
		if (keyword) {
			let history = getSearchHistory();
			history = history.filter(h => h.keyword !== keyword);
			uni.setStorageSync(STORAGE_KEYS.SEARCH_HISTORY, history);
		} else {
			uni.removeStorageSync(STORAGE_KEYS.SEARCH_HISTORY);
		}
	} catch (err) {
	}
}

/**
 * 保存认证token
 * @param {string} token 认证token
 * @returns {boolean}
 */
export function setAuthToken(token) {
	try {
		uni.setStorageSync(STORAGE_KEYS.AUTH_TOKEN, token);
		return true;
	} catch (err) {
		return false;
	}
}

/**
 * 获取认证token
 * @returns {string} token值，如不存在返回空字符串
 */
export function getAuthToken() {
	try {
		const token = uni.getStorageSync(STORAGE_KEYS.AUTH_TOKEN);
		return token || '';
	} catch (err) {
		return '';
	}
}

/**
 * 清除认证token
 * @returns {boolean}
 */
export function clearAuthToken() {
	try {
		uni.removeStorageSync(STORAGE_KEYS.AUTH_TOKEN);
		return true;
	} catch (err) {
		return false;
	}
}

/**
 * 保存用户信息
 * @param {object} userInfo 用户信息
 * @returns {boolean}
 */
export function setUserInfo(userInfo) {
	try {
		uni.setStorageSync(STORAGE_KEYS.USER_INFO, userInfo);
		return true;
	} catch (err) {
		return false;
	}
}

/**
 * 清除用户信息（登出时使用）
 * @returns {boolean}
 */
export function clearUserInfo() {
	try {
		clearAuthToken();
		uni.removeStorageSync(STORAGE_KEYS.USER_INFO);
		return true;
	} catch (err) {
		return false;
	}
}

/**
 * 保存围栏数据到本地
 * @param {array} fences 围栏数据数组
 * @returns {boolean}
 */
export function saveFences(fences) {
	try {
		uni.setStorageSync(STORAGE_KEYS.FENCES, fences);
		return true;
	} catch (err) {
		console.error('保存围栏数据失败:', err);
		return false;
	}
}

/**
 * 从本地读取围栏数据
 * @returns {array} 围栏数组，如不存在返回空数组
 */
export function getFences() {
	try {
		const data = uni.getStorageSync(STORAGE_KEYS.FENCES);
		return data ? JSON.parse(JSON.stringify(data)) : [];
	} catch (err) {
		console.error('读取围栏数据失败:', err);
		return [];
	}
}

/**
 * 清除所有围栏数据
 * @returns {boolean}
 */
export function clearFences() {
	try {
		uni.removeStorageSync(STORAGE_KEYS.FENCES);
		return true;
	} catch (err) {
		console.error('清除围栏数据失败:', err);
		return false;
	}
}
