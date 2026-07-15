/**
 * 高德地图API服务
 * 文档: https://lbs.amap.com/api/webservice/guide/api/newroute
 */

// 高德API Key（从manifest.json中配置）
const AMAP_KEY = '79b16ec633ea0ef97dc5a4efcf8a2615';
const AMAP_BASE_URL = 'https://restapi.amap.com/v3';  // 使用 v3 基础 API

/**
 * 发送HTTP请求到高德API
 * @private
 * @param {string} endpoint API端点（不含base url）
 * @param {object} params 请求参数
 * @returns {Promise}
 */
function request(endpoint, params = {}) {
	return new Promise((resolve, reject) => {
		const url = `${AMAP_BASE_URL}${endpoint}`;
		const requestParams = {
			key: AMAP_KEY,
			...params
		};

		uni.request({
			url: url,
			data: requestParams,
			method: 'GET',
			timeout: 10000,
			success: (res) => {
				if (res.statusCode === 200) {
					const data = res.data;
					if (data.status === '1') {
						resolve(data);
					} else {
						reject({
							code: data.infocode,
							message: data.info || '请求失败'
						});
					}
				} else {
					reject({
						code: res.statusCode,
						message: '网络请求失败'
					});
				}
			},
			fail: (err) => {
				reject({
					code: -1,
					message: '网络错误: ' + (err.errMsg || '未知错误')
				});
			}
		});
	});
}

/**
 * 地名搜索 - 按关键词搜索地点
 * 文档: https://lbs.amap.com/api/webservice/guide/api/search
 * @param {string} keywords 搜索关键词
 * @param {string} city 搜索城市
 * @param {number} page 分页（1-100）
 * @returns {Promise} 返回搜索结果
 */
export function searchPlace(keywords, city = '010', page = 1) {
	return request('/place/text', {
		keywords: keywords,
		city: city,
		page: page,
		pagesize: 50,
		extensions: 'all'
	}).then(res => {
		return {
			count: res.count,
			pois: (res.pois || []).map(poi => ({
				id: poi.id,
				name: poi.name,
				address: poi.address,
				location: poi.location,
				type: poi.type,
				phone: poi.tel || '',
				website: poi.website || '',
				businessHours: poi.businessarea || '',
				distance: poi.distance || 0,
				photos: Array.isArray(poi.photos)
					? poi.photos.map(photo => ({
						title: photo?.title || '',
						url: photo?.url || ''
					})).filter(photo => photo.url)
					: []
			}))
		};
	});
}

/**
 * 地名搜索 - 附近搜索（按距离优先）
 * 文档: https://lbs.amap.com/api/webservice/guide/api/search
 * @param {string} keywords 搜索关键词
 * @param {number} longitude 中心点经度
 * @param {number} latitude 中心点纬度
 * @param {number} radius 搜索半径（米）
 * @param {number} page 分页（1-100）
 * @returns {Promise} 返回搜索结果
 */
export function searchNearbyPlace(keywords, longitude, latitude, radius = 5000, page = 1) {
	return request('/place/around', {
		keywords: keywords,
		location: `${longitude},${latitude}`,
		radius: radius,
		sortrule: 'distance',
		page: page,
		pagesize: 50,
		extensions: 'all'
	}).then(res => {
		return {
			count: res.count,
			pois: (res.pois || []).map(poi => ({
				id: poi.id,
				name: poi.name,
				address: poi.address,
				location: poi.location,
				type: poi.type,
				phone: poi.tel || '',
				website: poi.website || '',
				businessHours: poi.businessarea || '',
				distance: Number(poi.distance) || 0,
				photos: Array.isArray(poi.photos)
					? poi.photos.map(photo => ({
						title: photo?.title || '',
						url: photo?.url || ''
					})).filter(photo => photo.url)
					: []
			}))
		};
	});
}

/**
 * 逆地理编码 - 根据坐标获取地址信息
 * 文档: https://lbs.amap.com/api/webservice/guide/api/georegeo
 * @param {number} longitude 经度
 * @param {number} latitude 纬度
 * @returns {Promise} 返回地址信息，包括城市编码
 */
export function regeo(longitude, latitude) {
	return request('/geocode/regeo', {
		location: `${longitude},${latitude}`,
		extensions: 'all'
	}).then(res => {
		const regeocode = res.regeocode || {};
		const addressComponent = regeocode.addressComponent || {};
		
		return {
			address: regeocode.formatted_address || '',
			province: addressComponent.province || '',
			city: addressComponent.city || '',
			district: addressComponent.district || '',
			street: addressComponent.street || '',
			streetNumber: addressComponent.streetNumber || '',
			cityCode: addressComponent.citycode || '', // 城市编码
			adCode: addressComponent.adcode || '', // 行政区编码
			areaCode: addressComponent.areacode || '',
			neighborhood: regeocode.aois?.[0]?.name || '',
			businessAreas: regeocode.businessAreas || []
		};
	});
}

/**
 * 获取坐标所在城市的城市编码
 * @param {number} longitude 经度
 * @param {number} latitude 纬度
 * @returns {Promise} 返回城市编码 (如: 010 表示北京)
 */
export async function getCityCode(longitude, latitude) {
	try {
		const geoInfo = await regeo(longitude, latitude);
		return geoInfo.cityCode || '010'; // 默认北京
	} catch (err) {
		return '010'; // 默认北京
	}
}

/**
 * 批量获取城市编码
 * @param {number} lng1 起点经度
 * @param {number} lat1 起点纬度
 * @param {number} lng2 终点经度
 * @param {number} lat2 终点纬度
 * @returns {Promise} 返回 {cityCode1, cityCode2}
 */
export async function getCityCodes(lng1, lat1, lng2, lat2) {
	try {
		const [geo1, geo2] = await Promise.all([
			regeo(lng1, lat1),
			regeo(lng2, lat2)
		]);
		return {
			cityCode1: geo1.cityCode || '010',
			cityCode2: geo2.cityCode || '010'
		};
	} catch (err) {
		return {
			cityCode1: '010',
			cityCode2: '010'
		};
	}
}

/**
 * 地名搜索 - 驾车路线规划
 */
export function drivingRoute(origin, destination, strategy = '0') {
	return request('/direction/driving', {
		origin: origin,
		destination: destination,
		strategy: strategy
	}).then(res => {
		const route = res.route || {};
		const paths = route.paths || [];
		
		if (paths.length === 0) {
			throw new Error('未找到可用路线');
		}

		// 返回所有路线方案（通常按优化策略从优到劣排序）
		const routes = paths.map((path, index) => {
			const steps = path.steps || [];
			const coordinates = buildRouteCoordinates(steps);

			return {
				id: index, // 路线方案ID
				distance: Number(path.distance) || 0, // 单位：米
				duration: Number(path.duration) || 0, // 单位：秒
				steps: steps.length,
				coordinates: coordinates,
				strategy: strategy,
				detailSteps: normalizeRouteSteps(steps),
				traffic: path.traffic_lights || 0,
				toll: path.toll_distance || 0, // 收费道路距离（米）
				tolls: path.tolls || [] // 收费信息数组
			};
		});

		// 为了向后兼容，返回第一个方案作为主方案，同时返回所有方案
		return {
			...routes[0], // 展开第一个方案的所有字段作为主方案
			alternatives: routes // 包含所有备选方案，按顺序排列
		};
	}).catch(err => {
		// 返回更详细的错误信息
		throw new Error(err.message || '驾车路线规划失败');
	});
}

/**
 * 路线规划 - 步行路线规划
 * 文档: https://lbs.amap.com/api/webservice/guide/api/direction
 * @param {string} origin 起点坐标 "经度,纬度"
 * @param {string} destination 终点坐标 "经度,纬度"
 * @returns {Promise}
 */
export function walkingRoute(origin, destination) {
	return request('/direction/walking', {
		origin: origin,
		destination: destination
	}).then(res => {
		const route = res.route || {};
		const paths = route.paths || [];

		if (paths.length === 0) {
			throw new Error('未找到可用步行路线');
		}

		const path = paths[0];
		const steps = path.steps || [];
		const coordinates = buildRouteCoordinates(steps);

		return {
			distance: Number(path.distance) || 0,
			duration: Number(path.duration) || 0,
			steps: steps.length,
			coordinates: coordinates,
			strategy: 'walking',
			detailSteps: normalizeRouteSteps(steps),
			traffic: 0,
			toll: 0,
			tolls: []
		};
	}).catch(err => {
		// 返回更详细的错误信息
		throw new Error(err.message || '步行路线规划失败');
	});
}

/**
 * 路线规划 - 公交路线规划
 * 文档: https://lbs.amap.com/api/webservice/guide/api/direction
 * @param {string} origin 起点坐标 "经度,纬度"
 * @param {string} destination 终点坐标 "经度,纬度"
 * @param {string} city 起点城市代码或城市名称 (如：010 或 北京)
 * @param {string} cityd 终点城市代码或城市名称 (如：010 或 北京，跨城时必填)
 * @param {number} strategy 公交换乘策略 0-最快捷 1-最经济 2-最少换乘 3-最少步行 5-不乘地铁
 * @returns {Promise}
 */
export function transferRoute(origin, destination, city = '010', cityd = '010', strategy = 0) {
	return request('/direction/transit/integrated', {
		origin: origin,
		destination: destination,
		city: city,  // 起点城市
		cityd: cityd,  // 终点城市（跨城必填）
		strategy: strategy
	}).then(res => {
		const route = res.route || {};
		const transits = route.transits || [];

		if (transits.length === 0) {
			throw new Error('未找到可用公交路线');
		}

		const transit = transits[0];
		const segments = transit.segments || [];
		const coordinates = buildTransitCoordinates(segments);

		return {
			distance: Number(transit.distance) || 0, // 总距离（米）
			duration: Number(transit.duration) || 0, // 总耗时（秒）
			steps: segments.length,
			coordinates: coordinates,
			strategy: 'transfer',
			detailSteps: normalizeTransitSteps(segments),
			traffic: 0,
			toll: 0,
			tolls: []
		};
	}).catch(err => {
		// 返回更详细的错误信息
		throw new Error(err.message || '公交路线规划失败');
	});
}

/**
 * 路线规划 - 骑行路线规划
 * 文档: https://lbs.amap.com/api/webservice/guide/api/direction
 * @param {string} origin 起点坐标 "经度,纬度"
 * @param {string} destination 终点坐标 "经度,纬度"
 * @returns {Promise}
 */
export function ridingRoute(origin, destination) {
	// 注：v3 骑行使用 v4 版本 API
	const bikeUrl = 'https://restapi.amap.com/v4/direction/bicycling';
	return new Promise((resolve, reject) => {
		uni.request({
			url: bikeUrl,
			data: {
				key: AMAP_KEY,
				origin: origin,
				destination: destination
			},
			method: 'GET',
			timeout: 10000,
			success: (res) => {
				if (res.statusCode === 200) {
					const data = res.data;
					if (data.errcode === 0) {
						resolve(data);
					} else {
						reject({
							code: data.errcode,
							message: data.errmsg || '请求失败'
						});
					}
				} else {
					reject({
						code: res.statusCode,
						message: '网络请求失败'
					});
				}
			},
			fail: (err) => {

				reject({
					code: -1,
					message: '网络错误: ' + (err.errMsg || '未知错误')
				});
			}
		});
	}).then(res => {
		// v4 响应格式与 v3 不同，直接返回 data
		const data = res.data || res;
		const paths = data.paths || [];

		if (paths.length === 0) {
			throw new Error('未找到可用骑行路线');
		}

		const path = paths[0];
		const steps = path.steps || [];
		const coordinates = buildRouteCoordinates(steps);

		return {
			distance: Number(path.distance) || 0,
			duration: Number(path.duration) || 0,
			steps: steps.length,
			coordinates: coordinates,
			strategy: 'riding',
			detailSteps: normalizeRouteSteps(steps),
			traffic: 0,
			toll: 0,
			tolls: []
		};
	}).catch(err => {
		// 返回更详细的错误信息
		throw new Error(err.message || '骑行路线规划失败');
	});
}

/**
 * 从路线步骤中提取坐标
 * @param {Array} steps 路线步骤
 * @returns {Array}
 */
function buildRouteCoordinates(steps = []) {
	const coordinates = [];
	steps.forEach(step => {
		const polyline = typeof step?.polyline === 'string' ? step.polyline.split(';') : [];
		polyline.forEach(point => {
			if (!point) {
				return;
			}
			const [lng, lat] = point.split(',');
			const longitude = parseFloat(lng);
			const latitude = parseFloat(lat);
			if (Number.isFinite(longitude) && Number.isFinite(latitude)) {
				coordinates.push({ longitude, latitude });
			}
		});
	});
	return coordinates;
}

/**
 * 从公交路线段中提取坐标
 * @param {Array} segments 公交路线段
 * @returns {Array}
 */
function buildTransitCoordinates(segments = []) {
	const coordinates = [];
	
	if (!Array.isArray(segments)) {
		return coordinates;
	}

	/**
	 * 提取 polyline 坐标的辅助函数
	 */
	const extractPolylineCoordinates = (polylineStr) => {
		const coords = [];
		if (!polylineStr) return coords;
		
		const polyline = typeof polylineStr === 'string' ? polylineStr.split(';') : [];
		polyline.forEach(point => {
			if (!point) return;
			const [lng, lat] = point.split(',');
			const longitude = parseFloat(lng);
			const latitude = parseFloat(lat);
			if (Number.isFinite(longitude) && Number.isFinite(latitude)) {
				coords.push({ longitude, latitude });
			}
		});
		return coords;
	};
	
	
	segments.forEach((segment, segIdx) => {
		// 处理步行部分
		if (segment.walking && Array.isArray(segment.walking)) {
			segment.walking.forEach(walk => {
				if (walk.polyline) {
					const polyline = typeof walk.polyline === 'string' ? walk.polyline.split(';') : [];
					polyline.forEach(point => {
						if (!point) return;
						const [lng, lat] = point.split(',');
						const longitude = parseFloat(lng);
						const latitude = parseFloat(lat);
						if (Number.isFinite(longitude) && Number.isFinite(latitude)) {
							coordinates.push({ longitude, latitude });
						}
					});
				}
			});
		}
		
		// 处理公交部分 - 只提取第一条公交线的polyline来避免重复显示
		if (segment.bus && segment.bus.buslines && segment.bus.buslines.length > 0) {
			const firstBusline = segment.bus.buslines[0];
			if (firstBusline.polyline) {
				const polyline = typeof firstBusline.polyline === 'string' ? firstBusline.polyline.split(';') : [];
				polyline.forEach(point => {
					if (!point) return;
					const [lng, lat] = point.split(',');
					const longitude = parseFloat(lng);
					const latitude = parseFloat(lat);
					if (Number.isFinite(longitude) && Number.isFinite(latitude)) {
						coordinates.push({ longitude, latitude });
					}
				});
			}
		}
		
		// 注：地铁段不提取坐标，仅在详情中显示站点信息

		// 处理高铁/火车部分（segment.railway）
		if (segment.railway) {
			// 1. 首先尝试提取 polyline 坐标（完整路线）
			if (segment.railway.polyline) {
				const polylineCoords = extractPolylineCoordinates(segment.railway.polyline);
				coordinates.push(...polylineCoords);
			}
			
			// 2. 如果没有 polyline，尝试从 departure_stop 和 arrival_stop 提取坐标
			if ((!segment.railway.polyline || coordinates.length < 10) && segment.railway.departure_stop && segment.railway.departure_stop.location) {
				const depCoord = segment.railway.departure_stop.location.split(',');
				if (depCoord.length === 2) {
					const [lng, lat] = depCoord;
					const longitude = parseFloat(lng);
					const latitude = parseFloat(lat);
					if (Number.isFinite(longitude) && Number.isFinite(latitude)) {
						coordinates.push({ longitude, latitude });
					}
				}
			}
			
			if ((!segment.railway.polyline || coordinates.length < 10) && segment.railway.arrival_stop && segment.railway.arrival_stop.location) {
				const arrCoord = segment.railway.arrival_stop.location.split(',');
				if (arrCoord.length === 2) {
					const [lng, lat] = arrCoord;
					const longitude = parseFloat(lng);
					const latitude = parseFloat(lat);
					if (Number.isFinite(longitude) && Number.isFinite(latitude)) {
						coordinates.push({ longitude, latitude });
					}
				}
			}
		}
	});
	
	return coordinates;
}

/**
 * 归一化路线步骤信息
 * @param {Array} steps 原始步骤
 * @returns {Array}
 */
function normalizeRouteSteps(steps = []) {
	return steps.map((step, index) => ({
		index: index + 1,
		instruction: step?.instruction || '',
		road: step?.road || '',
		orientation: step?.orientation || '',
		action: step?.action || '',
		assistantAction: step?.assistant_action || '',
		distance: Number(step?.distance) || 0,
		duration: Number(step?.duration) || 0,
		coordinates: buildStepCoordinates(step)
	}));
}

/**
 * 归一化公交路线步骤信息
 * @param {Array} segments 公交路线段
 * @returns {Array}
 */
function normalizeTransitSteps(segments = []) {
	return segments.map((segment, index) => {
		let instruction = '';
		let distance = 0;
		let duration = 0;
		let coordinates = [];
		let stations = [];

		// 处理公交车部分 - v3 API 结构: segment.bus.buslines
		if (segment.bus && segment.bus.buslines && Array.isArray(segment.bus.buslines) && segment.bus.buslines.length > 0) {
			const buslines = segment.bus.buslines;
			
			buslines.forEach((bus, busIdx) => {
				// 收集站点信息用于展开显示
				let departureStop = null;
				let arrivalStop = null;
				
				if (bus.departure_stop) {
					departureStop = bus.departure_stop.name;
					stations.push({
						type: 'departure',
						name: bus.departure_stop.name,
						time: bus.departure_stop.time
					});
				}
				if (bus.via_stops && Array.isArray(bus.via_stops)) {
					bus.via_stops.forEach(via => {
						stations.push({
							type: 'via',
							name: via.name,
							time: via.time
						});
					});
				}
				if (bus.arrival_stop) {
					arrivalStop = bus.arrival_stop.name;
					stations.push({
						type: 'arrival',
						name: bus.arrival_stop.name,
						time: bus.arrival_stop.time
					});
				}
				
				// 构建指令：乘坐 线路名 上车站 - 下车站
				const busName = bus.name || '未知线路';
				let busInstruction = `乘坐 ${busName}`;
				if (departureStop && arrivalStop) {
					busInstruction += ` ${departureStop} - ${arrivalStop}`;
				}
				
				if (!instruction) {
					instruction = busInstruction;
				} else {
					instruction += `; ${busInstruction}`;
				}
				
				distance += Number(bus.distance) || 0;
				duration += Number(bus.duration) || 0;
				
				// 注意：公交的坐标已在 buildTransitCoordinates 中提取（仅第一条线），
				// 这里仅在 step 级别坐标为空时才用第一条线填充（用于步骤高亮）
				if (coordinates.length === 0 && busIdx === 0 && bus.polyline) {
					const polyline = typeof bus.polyline === 'string' ? bus.polyline.split(';') : [];
					polyline.forEach(point => {
						if (!point) return;
						const [lng, lat] = point.split(',');
						const longitude = parseFloat(lng);
						const latitude = parseFloat(lat);
						if (Number.isFinite(longitude) && Number.isFinite(latitude)) {
							coordinates.push({ longitude, latitude });
						}
					});
				}
			});
		}

		// 处理步行部分
		if (segment.walking && Array.isArray(segment.walking) && segment.walking.length > 0) {
			const walking = segment.walking;
			const walkDist = walking.reduce((sum, w) => sum + (Number(w.distance) || 0), 0);
			const walkDur = walking.reduce((sum, w) => sum + (Number(w.duration) || 0), 0);
			
			if (instruction) {
				instruction += ` → 步行 ${walkDist} 米`;
			} else {
				instruction = `步行 ${walkDist} 米`;
			}
			
			distance += walkDist;
			duration += walkDur;
			
			// 提取步行部分的坐标
			walking.forEach(walk => {
				const polyline = typeof walk?.polyline === 'string' ? walk.polyline.split(';') : [];
				polyline.forEach(point => {
					if (!point) return;
					const [lng, lat] = point.split(',');
					const longitude = parseFloat(lng);
					const latitude = parseFloat(lat);
					if (Number.isFinite(longitude) && Number.isFinite(latitude)) {
						coordinates.push({ longitude, latitude });
					}
				});
			});
		}

		// 处理轨道交通部分（地铁）
		if (segment.entrance && segment.exit && segment.entrance.name && segment.exit.name) {
			const entranceName = segment.entrance.name;
			const exitName = segment.exit.name;
			
			if (instruction) {
				instruction += ` → 地铁`;
			} else {
				instruction = `地铁`;
			}
			
			// 保存地铁入出口信息
			stations.push({
				type: 'metro_entrance',
				name: entranceName
			});
			stations.push({
				type: 'metro_exit',
				name: exitName
			});
		}

		// 处理铁路/火车部分（跨城重点处理）
		// 确保 railway 有实际的线路信息才显示
		if (segment.railway && (segment.railway.name || segment.railway.departure_stop || segment.railway.arrival_stop)) {
			const railway = segment.railway;
			const railwayName = railway.name || '轨道交通';
			const tripInfo = railway.trip ? ` ${railway.trip}` : '';
			
			// 收集火车站点信息用于展开显示
			let departureStopName = null;
			let arrivalStopName = null;
			
			if (railway.departure_stop) {
				departureStopName = railway.departure_stop.name;
				stations.push({
					type: 'train_departure',
					name: railway.departure_stop.name,
					time: railway.departure_stop.time
				});
			}
			if (railway.via_stop && Array.isArray(railway.via_stop)) {
				railway.via_stop.forEach(via => {
					stations.push({
						type: 'train_via',
						name: via.name,
						time: via.time
					});
				});
			}
			if (railway.arrival_stop) {
				arrivalStopName = railway.arrival_stop.name;
				stations.push({
					type: 'train_arrival',
					name: railway.arrival_stop.name,
					time: railway.arrival_stop.time
				});
			}
			
			// 构建指令：乘坐 线路名 列车号 上车站 - 下车站
			let railwayInstruction = `乘坐 ${railwayName}${tripInfo}`;
			if (departureStopName && arrivalStopName) {
				railwayInstruction += ` ${departureStopName} - ${arrivalStopName}`;
			}
			
			if (instruction) {
				instruction += ` → ${railwayInstruction}`;
			} else {
				instruction = railwayInstruction;
			}
			
			distance += Number(railway.distance) || 0;
			duration += Number(railway.duration) || 0;
			
			// 注意：火车的坐标已在 buildTransitCoordinates 中提取，这里不再重复提取
		}

		return {
			index: index + 1,
			instruction: instruction || ('路线段 ' + (index + 1)),
			distance: distance,
			duration: duration,
			coordinates: coordinates,
			stations: stations  // 新增站点详细信息
		};
	});
}

/**
 * 提取单个步骤的坐标点
 * @param {Object} step 路线步骤
 * @returns {Array}
 */
function buildStepCoordinates(step) {
	const polyline = typeof step?.polyline === 'string' ? step.polyline.split(';') : [];
	const coordinates = [];
	polyline.forEach(point => {
		if (!point) {
			return;
		}
		const [lng, lat] = point.split(',');
		const longitude = parseFloat(lng);
		const latitude = parseFloat(lat);
		if (Number.isFinite(longitude) && Number.isFinite(latitude)) {
			coordinates.push({ longitude, latitude });
		}
	});
	return coordinates;
}

/**
 * 计算两点间距离
 * @param {number} lng1 点1经度
 * @param {number} lat1 点1纬度
 * @param {number} lng2 点2经度
 * @param {number} lat2 点2纬度
 * @returns {number} 距离（单位：米）
 */
export function calculateDistance(lng1, lat1, lng2, lat2) {
	const EARTH_RADIUS = 6371000; // 地球半径（米）
	
	function toRad(deg) {
		return deg * Math.PI / 180;
	}
	
	const radLat1 = toRad(lat1);
	const radLat2 = toRad(lat2);
	const deltaLat = toRad(lat2 - lat1);
	const deltaLng = toRad(lng2 - lng1);
	
	const a = Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
			  Math.cos(radLat1) * Math.cos(radLat2) *
			  Math.sin(deltaLng / 2) * Math.sin(deltaLng / 2);
	
	const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
	const distance = EARTH_RADIUS * c;
	
	return Math.round(distance);
}

/**
 * 格式化距离显示
 * @param {number} meters 距离（米）
 * @returns {string}
 */
export function formatDistance(meters) {
	if (meters < 1000) {
		return Math.round(meters) + 'm';
	} else {
		return (meters / 1000).toFixed(1) + 'km';
	}
}

/**
 * 格式化时间显示
 * @param {number} seconds 时间（秒）
 * @returns {string}
 */
export function formatDuration(seconds) {
	if (seconds < 60) {
		return Math.round(seconds) + 's';
	} else if (seconds < 3600) {
		return Math.round(seconds / 60) + 'min';
	} else {
		const hours = Math.floor(seconds / 3600);
		const mins = Math.round((seconds % 3600) / 60);
		return hours + 'h ' + mins + 'min';
	}
}
