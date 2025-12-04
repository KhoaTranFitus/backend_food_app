# Chứa các hàm normalize_text, search_algorithm
import unicodedata
from math import radians, sin, cos, sqrt, atan2

def normalize_text(text):
	if not text:
		return ""
	text = text.lower()
	text = unicodedata.normalize('NFD', text)\
					  .encode('ascii', 'ignore')\
					  .decode('utf-8')
	return text

def calculate_distance(lat1, lon1, lat2, lon2):
	"""Tính khoảng cách giữa 2 điểm (km) dùng Haversine formula."""
	if not all([lat1, lon1, lat2, lon2]):
		return None
	try:
		R = 6371  # Bán kính Trái Đất (km)
		lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
		dlat = lat2 - lat1
		dlon = lon2 - lon1
		a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
		c = 2 * atan2(sqrt(a), sqrt(1-a))
		return R * c
	except:
		return None

def search_algorithm(query, restaurants_db, menus_db, province=None, user_lat=None, user_lon=None):
	"""Tìm kiếm nhà hàng theo query, province, và sắp xếp theo khoảng cách nếu có tọa độ."""
	normalized_query = normalize_text(query) if query else ""
	normalized_province = normalize_text(province) if province else ""
	
	scores = {}  # restaurant_id: score
	distances = {}  # restaurant_id: distance (km)
	# 1. Lọc theo province trước (nếu có)
	filtered_restaurants = restaurants_db
	if normalized_province:
		# Lọc theo tên thành phố trong địa chỉ
		# VD: "Thành phố Hồ Chí Minh", "Hà Nội", "Đà Nẵng"
		filtered_restaurants = []
		for r in restaurants_db:
			address = normalize_text(r.get('address', ''))
			# Kiểm tra nếu province xuất hiện trong địa chỉ
			if normalized_province in address:
				filtered_restaurants.append(r)
	
	# Nếu không có query text, trả về tất cả nhà hàng đã lọc theo province
	if not normalized_query:
		for restaurant in filtered_restaurants:
			# 🔥 LỌC THEO BÁN KÍNH (2km)
			if user_lat and user_lon:
				d = calculate_distance(
					user_lat,
					user_lon,
					restaurant.get('lat'),
					restaurant.get('lon')
				)
				if d is None or d > 2:   # 🔥 chỉ giữ quán trong bán kính 2km
					continue
			rid = str(restaurant['id'])
			scores[rid] = 1  # điểm cơ bản
	else:
		# 2. Tìm trong Tên nhà hàng (ưu tiên cao nhất)
		for restaurant in filtered_restaurants:
			rid = str(restaurant['id'])
			normalized_name = normalize_text(restaurant.get('name'))
			# Tìm từ chính xác (word boundary)
			words = normalized_name.split()
			if normalized_query in words or normalized_query in normalized_name:
				scores[rid] = scores.get(rid, 0) + 10  # match name: +10

		# 3. Tìm trong Tags nhà hàng (ưu tiên vừa)
		for restaurant in filtered_restaurants:
			rid = str(restaurant['id'])
			normalized_tags = [normalize_text(tag) for tag in restaurant.get('tags', [])]
			if any(normalized_query in tag for tag in normalized_tags):
				scores[rid] = scores.get(rid, 0) + 5  # match tag: +5

		# 4. Tìm trong Tên món ăn (ưu tiên thấp hơn)
		# menus_db bây giờ là MENUS_BY_RESTAURANT_ID (dict: restaurant_id -> [menu items])
		filtered_ids = {str(r['id']) for r in filtered_restaurants}
		for restaurant_id, menu_items in menus_db.items():
			if restaurant_id not in filtered_ids:
				continue
			for item in menu_items:
				normalized_dish = normalize_text(item.get('dish_name'))
				if normalized_query in normalized_dish:
					scores[restaurant_id] = scores.get(restaurant_id, 0) + 2  # match dish: +2
					break

	# 5. Cộng thêm điểm theo rating (nếu có)
	restaurants_dict = {str(r['id']): r for r in restaurants_db}
	for rid in scores:
		res = restaurants_dict.get(rid)
		if res:
			rating = res.get('rating')
			if isinstance(rating, (int, float)):
				scores[rid] += rating * 2  # mỗi 1 điểm rating = +2 điểm
			
			# Tính khoảng cách nếu có tọa độ user
			if user_lat is not None and user_lon is not None:
				res_lat = res.get('lat')
				res_lon = res.get('lon')
				dist = calculate_distance(user_lat, user_lon, res_lat, res_lon)
				if dist is not None:
					distances[rid] = dist

	# 6. Biên soạn kết quả, sắp xếp theo điểm giảm dần, sau đó theo khoảng cách tăng dần
	if distances:
		# Nếu có khoảng cách, sắp xếp theo score trước, rồi distance
		sorted_results = sorted(
			scores.items(), 
			key=lambda x: (-x[1], distances.get(x[0], float('inf')))
		)
	else:
		# Chỉ sắp xếp theo score
		sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
	
	final_results = []
	for res_id, score in sorted_results:
		if res_id in restaurants_dict:
			res = dict(restaurants_dict[res_id])
			res['score'] = score
			if res_id in distances:
				res['distance'] = round(distances[res_id], 2)  # km, làm tròn 2 chữ số
			final_results.append(res)
	return final_results
