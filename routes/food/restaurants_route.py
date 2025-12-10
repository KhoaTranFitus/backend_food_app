# routes/food/restaurants_route.py

from flask import request, jsonify
from . import food_bp
# ⭐️ IMPORT ĐÃ ĐƯỢC KHẮC PHỤC ⭐️
from core.database import RESTAURANTS 

@food_bp.route("/restaurants", methods=["GET"])
def get_all_restaurants():
    """Trả về toàn bộ danh sách nhà hàng đã load từ restaurants.json."""
    
    # Lấy toàn bộ giá trị (data) từ dictionary RESTAURANTS
    restaurant_list = list(RESTAURANTS.values())

    return jsonify({
        "success": True,
        "count": len(restaurant_list),
        "restaurants": restaurant_list
    }), 200


@food_bp.route("/restaurants/search", methods=["GET"])
def search_restaurants():
    """Tìm kiếm nhà hàng theo query (dành cho thanh search)."""
    
    query = request.args.get('q', '').lower()
    
    # Nếu không có query, trả về tất cả
    if not query:
        return get_all_restaurants()

    # Logic tìm kiếm đơn giản (lọc theo tên hoặc địa chỉ)
    results = [
        r for r in list(RESTAURANTS.values())
        if query in r.get('name', '').lower() or query in r.get('address', '').lower()
    ]

    return jsonify({
        "success": True,
        "count": len(results),
        "restaurants": results
    }), 200