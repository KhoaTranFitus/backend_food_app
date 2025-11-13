from flask import request, jsonify, current_app
from core.database import DB_RESTAURANTS, DB_MENUS
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
			return jsonify({"error": "Request body phải là JSON, ví dụ: { 'query': 'từ khóa' }"}), 400
		query = data.get('query')
		if not isinstance(query, str) or not query.strip():
			return jsonify({"error": "Missing or invalid 'query' in request body"}), 400
		results = search_algorithm(query, DB_RESTAURANTS, DB_MENUS)
		return jsonify(results)
	except Exception as e:
		import traceback
		print(f"Lỗi xảy ra khi tìm kiếm: {e}\n{traceback.format_exc()}")
		return jsonify({"error": "Internal server error", "detail": str(e)}), 500
