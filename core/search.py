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
	# Provinces
	"ho chi minh": "TP. Hồ Chí Minh",
	"saigon": "TP. Hồ Chí Minh",
	"hcmc": "TP. Hồ Chí Minh",
	"hanoi": "Hà Nội",
	"ha noi": "Hà Nội",
	"da nang": "Đà Nẵng",
	"danang": "Đà Nẵng",
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

def search_algorithm(query, restaurants_db, menus_db, province=None, user_lat=None, user_lon=None):
	"""Tìm kiếm nhà hàng theo query, province, và sắp xếp theo khoảng cách nếu có tọa độ."""
	normalized_query = normalize_text(query) if query else ""
	
	# Translate English query to Vietnamese if possible
	if normalized_query:
		translated = translate_query(normalized_query)
		if translated != normalized_query:
			normalized_query = normalize_text(translated)
	
	scores = {}  # restaurant_id: score
	distances = {}  # restaurant_id: distance (km)
	
	# 1. Lọc theo province trước (nếu có) - FILTER BY TAGS
	filtered_restaurants = restaurants_db
	if province:
		# Translate province từ tiếng Anh sang tiếng Việt nếu cần
		province_tag = translate_query(province)
		normalized_province = normalize_text(province_tag)
		
		# Lọc theo province tag (chính xác hơn là lọc theo address)
		filtered_restaurants = []
		for r in restaurants_db:
			# Kiểm tra trong tags
			restaurant_tags = [normalize_text(tag) for tag in r.get('tags', [])]
			if any(normalized_province in tag or tag in normalized_province for tag in restaurant_tags):
				filtered_restaurants.append(r)
	
	# Nếu không có query text, trả về tất cả nhà hàng đã lọc theo province
	if not normalized_query:
		for restaurant in filtered_restaurants:
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
			# Match exact tag hoặc tag chứa query
			if any(normalized_query == tag or normalized_query in tag or tag in normalized_query for tag in normalized_tags):
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
