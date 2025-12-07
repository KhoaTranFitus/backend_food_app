# routes/food/detail_route.py
from flask import jsonify
from routes.food import food_bp

from core.database import RESTAURANTS, MENUS_BY_RESTAURANT_ID

@food_bp.route('/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant_detail(restaurant_id):
	"""Lấy chi tiết nhà hàng và menu của nhà hàng đó."""
	# 1. Tìm nhà hàng có ID tương ứng (dùng RESTAURANTS_DICT index)
	rid = str(restaurant_id)
	restaurant = RESTAURANTS_DICT.get(rid)
	
	if not restaurant:
		return jsonify({"error": "Restaurant not found"}), 404

	# 2. Lấy menu tương ứng (nếu có) - dùng MENUS_BY_RESTAURANT_ID index
	menu_items = MENUS_BY_RESTAURANT_ID.get(rid, [])

	# 3. Gộp dữ liệu lại
	detail = {
		**restaurant,
		"menu": menu_items
	}

	return jsonify(detail)