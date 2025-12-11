# routes/food/restaurants_route.py

from flask import request, jsonify
from firebase_admin import db # <--- THÊM IMPORT NÀY
from . import food_bp
from core.database import RESTAURANTS 

@food_bp.route("/restaurants", methods=["GET"])
def get_all_restaurants():
    """Trả về toàn bộ danh sách nhà hàng (Có cập nhật Rating từ Firebase)."""
    
    # 1. Lấy danh sách gốc từ dữ liệu tĩnh
    restaurant_list = list(RESTAURANTS.values())

    # 2. [MỚI] Lấy toàn bộ rating thực tế từ Firebase để ghi đè lên rating cũ
    try:
        # Lấy một lần toàn bộ node rating (tối ưu hơn là for loop gọi DB nhiều lần)
        ratings_ref = db.reference("restaurants_rating")
        ratings_snapshot = ratings_ref.get() # Kết quả dạng: { "id_nha_hang": {"rating": 4.5}, ... }
        
        if ratings_snapshot:
            for res in restaurant_list:
                res_id = str(res.get('id'))
                # Nếu nhà hàng này có rating mới trên Firebase
                if res_id in ratings_snapshot:
                    new_data = ratings_snapshot[res_id]
                    # Ghi đè rating mới vào dữ liệu trả về
                    if 'rating' in new_data:
                        res['rating'] = new_data['rating']
                        
    except Exception as e:
        print(f"⚠️ Lỗi khi đồng bộ rating từ Firebase: {e}")
        # Nếu lỗi thì vẫn trả về list cũ, không làm crash app

    return jsonify({
        "success": True,
        "count": len(restaurant_list),
        "restaurants": restaurant_list
    }), 200


@food_bp.route("/restaurants/search", methods=["GET"])
def search_restaurants():
    """Tìm kiếm nhà hàng (Cũng cần cập nhật Rating)."""
    
    query = request.args.get('q', '').lower()
    
    # Logic tìm kiếm
    all_res = list(RESTAURANTS.values())
    results = [
        r for r in all_res
        if query in r.get('name', '').lower() or query in r.get('address', '').lower()
    ]

    # [MỚI] Cập nhật rating cho kết quả tìm kiếm
    try:
        ratings_ref = db.reference("restaurants_rating")
        ratings_snapshot = ratings_ref.get()
        
        if ratings_snapshot:
            for res in results:
                res_id = str(res.get('id'))
                if res_id in ratings_snapshot:
                    res['rating'] = ratings_snapshot[res_id].get('rating', res['rating'])
    except Exception:
        pass

    return jsonify({
        "success": True,
        "count": len(results),
        "restaurants": results
    }), 200