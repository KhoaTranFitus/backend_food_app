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

		# Gọi search algorithm với các tham số mới
		print("--- BẮT ĐẦU DEBUG REQUEST ---")
		print(f"1. Tổng số quán trong DB: {len(DB_RESTAURANTS)}")
		print(f"2. Input nhận được: Query={query}, Province={province}")
        
        # In thử quán đầu tiên để xem cấu trúc
		if len(DB_RESTAURANTS) > 0:
			print(f"3. Quán mẫu đầu tiên: {DB_RESTAURANTS[0].get('name')} - ID: {DB_RESTAURANTS[0].get('id')}")
		else:
			print("3. CẢNH BÁO: DB_RESTAURANTS đang rỗng! Kiểm tra lại file json.")

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
