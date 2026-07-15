/**
 * 电子围栏服务
 * 处理矩形、圆形围栏的创建、判断等逻辑
 */

/**
 * 判断点是否在矩形内
 */
export function isPointInRectangle(point, rect) {
	const { latitude: lat1, longitude: lng1 } = rect.point1;
	const { latitude: lat2, longitude: lng2 } = rect.point2;
	const { latitude, longitude } = point;
	
	const minLat = Math.min(lat1, lat2);
	const maxLat = Math.max(lat1, lat2);
	const minLng = Math.min(lng1, lng2);
	const maxLng = Math.max(lng1, lng2);
	
	const result = latitude >= minLat && latitude <= maxLat && longitude >= minLng && longitude <= maxLng;
	return result;
}

/**
 * 判断点是否在圆形内
 */
export function isPointInCircle(point, circle) {
	const { latitude: lat1, longitude: lng1 } = point;
	const { latitude: lat2, longitude: lng2 } = circle.center;
	const radius = circle.radius; // 单位：米
	
	// 使用 Haversine 公式计算两点间距离（米）
	const distance = calculateDistance(lat1, lng1, lat2, lng2);
	const result = distance <= radius;
	return result;
}

/**
 * 计算两点间的距离（Haversine公式，单位：米）
 */
export function calculateDistance(lat1, lon1, lat2, lon2) {
	const R = 6371000; // 地球半径（米）
	const toRad = Math.PI / 180;
	
	const dLat = (lat2 - lat1) * toRad;
	const dLon = (lon2 - lon1) * toRad;
	
	const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
	          Math.cos(lat1 * toRad) * Math.cos(lat2 * toRad) *
	          Math.sin(dLon / 2) * Math.sin(dLon / 2);
	
	const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
	return R * c;
}

/**
 * 判断点是否在任何围栏内
 */
export function isPointInAnyFence(point, fences) {
	return fences.some(fence => {
		if (fence.type === 'rectangle') {
			return isPointInRectangle(point, fence);
		} else if (fence.type === 'circle') {
			return isPointInCircle(point, fence);
		}
		return false;
	});
}

/**
 * 获取矩形的四个顶点（用于绘制polygon）
 */
export function getRectanglePolyline(point1, point2) {
	const { latitude: lat1, longitude: lng1 } = point1;
	const { latitude: lat2, longitude: lng2 } = point2;
	
	// 返回四个顶点形成的多边形
	return [
		{ latitude: lat1, longitude: lng1 },
		{ latitude: lat1, longitude: lng2 },
		{ latitude: lat2, longitude: lng2 },
		{ latitude: lat2, longitude: lng1 },
		{ latitude: lat1, longitude: lng1 } // 闭合
	];
}

/**
 * 生成圆形的多个点来绘制circle
 */
export function getCirclePoints(center, radius, points = 30) {
	const { latitude, longitude } = center;
	const R = 6371000; // 地球半径（米）
	const lat = latitude * Math.PI / 180;
	const lng = longitude * Math.PI / 180;
	const d = radius / R;
	
	const circlePoints = [];
	
	for (let i = 0; i < points; i++) {
		const bearing = (i / points) * 2 * Math.PI;
		
		const latRadians = Math.asin(
			Math.sin(lat) * Math.cos(d) +
			Math.cos(lat) * Math.sin(d) * Math.cos(bearing)
		);
		
		const lonRadians = lng + Math.atan2(
			Math.sin(bearing) * Math.sin(d) * Math.cos(lat),
			Math.cos(d) - Math.sin(lat) * Math.sin(latRadians)
		);
		
		let latDegrees = latRadians * 180 / Math.PI;
		let lonDegrees = lonRadians * 180 / Math.PI;
		
		// 坐标范围检查和修正
		latDegrees = Math.max(-90, Math.min(90, latDegrees));
		lonDegrees = ((lonDegrees + 180) % 360) - 180; // 确保经度在 -180~180 范围内
		
		circlePoints.push({
			latitude: latDegrees,
			longitude: lonDegrees
		});
	}
	
	// 闭合多边形：添加起点到终点
	if (circlePoints.length > 0) {
		circlePoints.push(circlePoints[0]);
	}
	
	return circlePoints;
}
