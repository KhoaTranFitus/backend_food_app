# Chứa các hàm normalize_text, search_algorithm
import unicodedata
from math import radians, sin, cos, sqrt, atan2

def normalize_text(text):
	"""Normalize text - giữ nguyên dấu tiếng Việt để search chính xác hơn"""
	if not text:
		return ""
	return text.lower().strip()

# Mapping từ tiếng Anh sang tiếng Việt cho tags
ENGLISH_TO_VIETNAMESE_TAGS = {
	# Provinces - Ho Chi Minh City variations
	"ho chi minh": "TP. Hồ Chí Minh",
	"saigon": "TP. Hồ Chí Minh",
	"hcmc": "TP. Hồ Chí Minh",
	"tp.hcm": "TP. Hồ Chí Minh",
	"tp hcm": "TP. Hồ Chí Minh",
	"tp. hcm": "TP. Hồ Chí Minh",
	"tphcm": "TP. Hồ Chí Minh",
	"tp.ho chi minh": "TP. Hồ Chí Minh",
	"sai gon": "TP. Hồ Chí Minh",
	"sài gòn": "TP. Hồ Chí Minh",
	
	# Hanoi variations
	"hanoi": "Hà Nội",
	"ha noi": "Hà Nội",
	"hà nội": "Hà Nội",
	
	# Da Nang variations
	"da nang": "Đà Nẵng",
	"danang": "Đà Nẵng",
	"đà nẵng": "Đà Nẵng",
	"da lat": "Lâm Đồng",
	"dalat": "Lâm Đồng",
	"nha trang": "Khánh Hòa",
	"vung tau": "Bà Rịa - Vũng Tàu",
	"hoi an": "Quảng Nam",
	"hue": "Thừa Thiên Huế",
	"can tho": "Cần Thơ",
	"phu quoc": "Kiên Giang",
	"quy nhon": "Bình Định",
	"ha long": "Quảng Ninh",
	"phan thiet": "Bình Thuận",
	"buon ma thuot": "Đắk Lắk",
	"sapa": "Lào Cai",
	"sa pa": "Lào Cai",
	"hai phong": "Hải Phòng",
	"ninh binh": "Ninh Bình",
	
	# Food types
	"seafood": "Hải Sản",
	"vegetarian": "Chay",
	"vegan": "Chay",
	"bbq": "BBQ",
	"hotpot": "Lẩu",
	"noodles": "Phở/Bún",
	"pho": "Phở/Bún",
	"rice": "Cơm",
	"coffee": "Cà Phê",
	"cafe": "Cà Phê",
	"dessert": "Tráng Miệng",
	"cake": "Tráng Miệng",
	"pizza": "Pizza",
	"sushi": "Sushi",
	"ramen": "Ramen",
	"burger": "Burger",
	"fast food": "Fast Food",
	"steak": "Bít Tết",
	"buffet": "Buffet",
	"dimsum": "Dimsum",
	"bar": "Quán Bar",
	"restaurant": "Nhà Hàng",
	
	# Cuisine
	"chinese": "Món Trung",
	"japanese": "Món Nhật",
	"korean": "Món Hàn",
	"vietnamese": "Món Việt",
	"thai": "Món Thái",
	"american": "Món Mỹ",
	"italian": "Món Ý",
	"french": "Món Pháp",
	"indian": "Món Ấn",
	
	# Price
	"cheap": "Giá Rẻ",
	"expensive": "Sang Trọng",
	"luxury": "Sang Trọng",
	"fine dining": "Cao Cấp",
}

def translate_query(query):
	"""Translate English query to Vietnamese tags if possible"""
	normalized = normalize_text(query)
	return ENGLISH_TO_VIETNAMESE_TAGS.get(normalized, query)

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

def parse_price_range(price_range_str):
	"""
	Parse "50,000đ-150,000đ" -> (50000, 150000)
	Parse "300,000đ+" -> (300000, float('inf'))
	"""
	if not price_range_str:
		return (0, float('inf'))
	
	try:
		# Remove "đ" và spaces
		price_str = price_range_str.replace('đ', '').replace(' ', '').replace(',', '')
		
		if '+' in price_str:
			# "300000+" -> min=300000, max=inf
			min_val = int(price_str.replace('+', ''))
			return (min_val, float('inf'))
		elif '-' in price_str:
			# "50000-150000" -> (50000, 150000)
			parts = price_str.split('-')
			return (int(parts[0]), int(parts[1]))
		else:
			# Single value
			val = int(price_str)
			return (val, val)
	except:
		return (0, float('inf'))

def search_algorithm(query, restaurants_db, menus_db, province=None, user_lat=None, user_lon=None, 
                     radius=None, categories=None, min_price=None, max_price=None, 
                     min_rating=None, max_rating=None, tags=None):
	"""
	Tìm kiếm và lọc nhà hàng với đầy đủ tham số
	
	Args:
		query: Từ khóa tìm kiếm (tên, món ăn, tags)
		restaurants_db: Database nhà hàng
		menus_db: Database menu
		province: Lọc theo tỉnh/thành phố
		user_lat, user_lon: Tọa độ người dùng
		radius: Bán kính tìm kiếm (km), None = không giới hạn
		categories: List category IDs để lọc, None = không lọc
		min_price, max_price: Khoảng giá (VND)
		min_rating, max_rating: Khoảng rating
		tags: List tags để lọc
	"""
	normalized_query = normalize_text(query) if query else ""
	
	# Translate English query to Vietnamese if possible
	if normalized_query:
		translated = translate_query(normalized_query)
		if translated != normalized_query:
			normalized_query = normalize_text(translated)
	
	scores = {}  # restaurant_id: score
	distances = {}  # restaurant_id: distance (km)
	
	# 1. Áp dụng tất cả filters trước
	filtered_restaurants = []
	for r in restaurants_db:
		# Filter by province
		if province:
			province_tag = translate_query(province)
			normalized_province = normalize_text(province_tag)
			restaurant_tags = [normalize_text(tag) for tag in r.get('tags', [])]
			if not any(normalized_province in tag or tag in normalized_province for tag in restaurant_tags):
				continue
		
		# Filter by distance/radius
		if user_lat is not None and user_lon is not None and radius is not None:
			rest_lat = r.get('lat')
			rest_lon = r.get('lon')
			if rest_lat and rest_lon:
				dist = calculate_distance(user_lat, user_lon, rest_lat, rest_lon)
				if dist is not None:
					if dist > radius:
						continue
					distances[str(r['id'])] = dist
		
		# Filter by category
		if categories is not None:
			if r.get('category_id') not in categories:
				continue
		
		# Filter by price range
		if min_price is not None or max_price is not None:
			price_range = r.get('price_range', '')
			rest_min, rest_max = parse_price_range(price_range)
			
			if min_price is not None and rest_max < min_price:
				continue
			if max_price is not None and rest_min > max_price:
				continue
		
		# Filter by rating
		rating = r.get('rating', 0)
		if min_rating is not None and rating < min_rating:
			continue
		if max_rating is not None and rating > max_rating:
			continue
		
		# Filter by tags
		if tags:
			restaurant_tags = r.get('tags', [])
			if not any(tag in restaurant_tags for tag in tags):
				continue
		
		# Passed all filters
		filtered_restaurants.append(r)
	
	# 2. Tính khoảng cách cho tất cả nhà hàng đã lọc (nếu có tọa độ)
	if user_lat is not None and user_lon is not None:
		for r in filtered_restaurants:
			rid = str(r['id'])
			if rid not in distances:  # Chưa tính trong filter radius
				rest_lat = r.get('lat')
				rest_lon = r.get('lon')
				if rest_lat and rest_lon:
					dist = calculate_distance(user_lat, user_lon, rest_lat, rest_lon)
					if dist is not None:
						distances[rid] = dist
	
	# 3. Tính điểm cho từng nhà hàng
	# Nếu không có query text, tất cả đều có điểm cơ bản
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
		# Tìm trong Tên nhà hàng (ưu tiên cao nhất)
		for restaurant in filtered_restaurants:
			rid = str(restaurant['id'])
			normalized_name = normalize_text(restaurant.get('name'))
			# Tìm từ chính xác (word boundary)
			words = normalized_name.split()
			if normalized_query in words or normalized_query in normalized_name:
				scores[rid] = scores.get(rid, 0) + 10  # match name: +10

		# Tìm trong Tags nhà hàng (ưu tiên vừa)
		for restaurant in filtered_restaurants:
			rid = str(restaurant['id'])
			normalized_tags = [normalize_text(tag) for tag in restaurant.get('tags', [])]
			# Match exact tag hoặc tag chứa query
			if any(normalized_query == tag or normalized_query in tag or tag in normalized_query for tag in normalized_tags):
				scores[rid] = scores.get(rid, 0) + 5  # match tag: +5

		# Tìm trong Tên món ăn (ưu tiên thấp hơn)
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

	# 4. Cộng thêm điểm theo rating cho tất cả nhà hàng
	for restaurant in filtered_restaurants:
		rid = str(restaurant['id'])
		if rid not in scores:
			scores[rid] = 0
		
		rating = restaurant.get('rating')
		if isinstance(rating, (int, float)):
			scores[rid] += rating * 2  # mỗi 1 điểm rating = +2 điểm

	# 5. Biên soạn kết quả, sắp xếp theo điểm giảm dần, sau đó theo khoảng cách tăng dần
	restaurants_dict = {str(r['id']): r for r in filtered_restaurants}
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
