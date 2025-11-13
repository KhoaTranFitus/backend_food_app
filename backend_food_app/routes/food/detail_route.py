# routes/food/detail_route.py
from flask import jsonify
from . import food_bp
from core.database import DB_RESTAURANTS, DB_MENUS

@food_bp.route('/<int:restaurant_id>', methods=['GET'])
def get_restaurant_detail(restaurant_id):
    # 1. Tìm nhà hàng có ID tương ứng
    restaurant = next((r for r in DB_RESTAURANTS if r['id'] == restaurant_id), None)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    # 2. Lấy menu tương ứng (nếu có)
    menu_info = DB_MENUS.get(str(restaurant_id), {}).get('menu', [])

    # 3. Gộp dữ liệu lại
    detail = {
        **restaurant,
        "menu": menu_info
    }

    return jsonify(detail)
