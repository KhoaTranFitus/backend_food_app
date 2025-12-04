from flask import request, jsonify, current_app
from core.database import DB_RESTAURANTS, MENUS_BY_RESTAURANT_ID
from core.search import search_algorithm
from routes.food import food_bp

@food_bp.route('/search', methods=['POST'])
def search_food():
	"""
	API endpoint để tìm kiếm nhà hàng.
	Frontend sẽ gửi: { "query": "từ khóa" }
	"""
	try:
		data = request.get_json(force=True, silent=True)
		
		if not data:
			return jsonify({"error": "Request body phải là JSON, ví dụ: { 'query': 'từ khóa', 'province': 'Quận 1', 'lat': 10.7812, 'lon': 106.6942 }"}), 400
		
		query = data.get('query', '').strip() if isinstance(data.get('query'), str) else ''
		province = data.get('province', '').strip() if isinstance(data.get('province'), str) else ''
		
		# Lấy tọa độ (nếu có)
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
			user_lon=user_lon
		)
		return jsonify(results)
	except Exception as e:
		import traceback
		print(f"Lỗi xảy ra khi tìm kiếm: {e}\n{traceback.format_exc()}")
		return jsonify({"error": "Internal server error", "detail": str(e)}), 500
