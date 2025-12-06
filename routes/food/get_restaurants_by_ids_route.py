# routes/food/get_restaurants_by_ids_route.py

from flask import request, jsonify
from . import food_bp
from core.database import RESTAURANTS 

@food_bp.route("/restaurants/details-by-ids", methods=["POST"])
def get_restaurants_by_ids():
    data = request.get_json(force=True, silent=True) or {}
    restaurant_ids = data.get("ids", []) # Frontend gửi list IDs trong body

    # 1. Kiểm tra format
    if not isinstance(restaurant_ids, list):
        return jsonify({"error": "Invalid 'ids' list format. Must be a list."}), 400

    # ⭐️ FIX LỖI: CHẤP NHẬN DANH SÁCH RỖNG VÀ TRẢ VỀ THÀNH CÔNG (200 OK) ⭐️
    if not restaurant_ids:
        return jsonify({
            "success": True,
            "restaurants": [],
            "count": 0
        }), 200

    results = []
    
    # 2. Xử lý các IDs còn lại (không rỗng)
    for res_id in restaurant_ids:
        res_data = RESTAURANTS.get(str(res_id).strip())
        if res_data:
            results.append(res_data)

    return jsonify({
        "success": True,
        "restaurants": results,
        "count": len(results)
    }), 200