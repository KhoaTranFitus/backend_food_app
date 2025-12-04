from flask import request, jsonify, current_app
from core.database import DB_RESTAURANTS, MENUS_BY_RESTAURANT_ID
from core.search import search_algorithm
from routes.food import food_bp

@food_bp.route('/search', methods=['POST'])
def search_food():
	"""
	API endpoint để tìm kiếm và lọc nhà hàng.
	
	Request Body:
		- query: string (optional) - Từ khóa tìm kiếm
		- province: string (optional) - Lọc theo tỉnh/thành phố
		- lat, lon: float (optional) - Vị trí người dùng
		- radius: float (optional) - Bán kính tìm kiếm (km)
		- categories: list[int] (optional) - Lọc theo category IDs
		- min_price, max_price: int (optional) - Khoảng giá (VND)
		- min_rating, max_rating: float (optional) - Khoảng rating
		- tags: list[str] (optional) - Lọc theo tags
	"""
	try:
		data = request.get_json(force=True, silent=True)
		if not data:
			data = {}
		
		# Parse search parameters
		query = data.get('query', '').strip() if isinstance(data.get('query'), str) else ''
		province = data.get('province', '').strip() if isinstance(data.get('province'), str) else ''
		
		# Parse location
		user_lat = data.get('lat')
		user_lon = data.get('lon')
		if user_lat is not None:
			try:
				user_lat = float(user_lat)
			except (ValueError, TypeError):
				user_lat = None
		if user_lon is not None:
			try:
				user_lon = float(user_lon)
			except (ValueError, TypeError):
				user_lon = None
		
		# Parse filter parameters
		radius = data.get('radius')
		if radius is not None:
			try:
				radius = float(radius)
			except (ValueError, TypeError):
				radius = None
		
		categories = data.get('categories')  # None or list[int]
		
		min_price = data.get('min_price')
		if min_price is not None:
			try:
				min_price = int(min_price)
			except (ValueError, TypeError):
				min_price = None
		
		max_price = data.get('max_price')
		if max_price is not None:
			try:
				max_price = int(max_price)
			except (ValueError, TypeError):
				max_price = None
		
		min_rating = data.get('min_rating')
		if min_rating is not None:
			try:
				min_rating = float(min_rating)
			except (ValueError, TypeError):
				min_rating = None
		
		max_rating = data.get('max_rating')
		if max_rating is not None:
			try:
				max_rating = float(max_rating)
			except (ValueError, TypeError):
				max_rating = None
		
		tags = data.get('tags', [])
		if not isinstance(tags, list):
			tags = []
		
		# Gọi search algorithm với tất cả tham số
		results = search_algorithm(
			query, 
			DB_RESTAURANTS, 
			MENUS_BY_RESTAURANT_ID,
			province=province,
			user_lat=user_lat,
			user_lon=user_lon,
			radius=radius,
			categories=categories,
			min_price=min_price,
			max_price=max_price,
			min_rating=min_rating,
			max_rating=max_rating,
			tags=tags
		)
		
		# Format results để match frontend expect
		category_map = {
			1: {"dishType": "dry", "pinColor": "red"},
			2: {"dishType": "soup", "pinColor": "blue"},
			3: {"dishType": "vegetarian", "pinColor": "green"},
			4: {"dishType": "salty", "pinColor": "orange"},
			5: {"dishType": "seafood", "pinColor": "purple"}
		}
		
		formatted_results = []
		for r in results:
			category_id = r.get('category_id', 1)
			category_info = category_map.get(category_id, {"dishType": "dry", "pinColor": "red"})
			
			formatted = {
				"id": r.get('id'),
				"name": r.get('name'),
				"address": r.get('address'),
				"position": {
					"lat": r.get('lat'),
					"lon": r.get('lon')
				},
				"dishType": category_info["dishType"],
				"pinColor": category_info["pinColor"],
				"rating": r.get('rating', 0),
				"price_range": r.get('price_range'),
				"phone_number": r.get('phone_number'),
				"open_hours": r.get('open_hours'),
				"main_image_url": r.get('main_image_url'),
				"tags": r.get('tags', [])
			}
			
			# Thêm distance nếu có
			if 'distance' in r:
				formatted['distance'] = r['distance']
			
			formatted_results.append(formatted)
		
		return jsonify({
			"success": True,
			"total": len(formatted_results),
			"places": formatted_results
		})
	except Exception as e:
		import traceback
		print(f"Lỗi xảy ra khi tìm kiếm: {e}\n{traceback.format_exc()}")
		return jsonify({"error": "Internal server error", "detail": str(e)}), 500
