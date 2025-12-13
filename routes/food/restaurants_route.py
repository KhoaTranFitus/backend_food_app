# routes/food/restaurants_route.py

from flask import request, jsonify
from firebase_admin import db # <--- THÊM IMPORT NÀY
from . import food_bp
from core.database import RESTAURANTS, DB_RESTAURANTS, MENUS_BY_RESTAURANT_ID
from core.search import search_algorithm
from firebase_admin import db

@food_bp.route("/restaurants", methods=["GET"])
def get_all_restaurants():
    """
    GET /api/restaurants
    Hỗ trợ cả: 
    - Lấy tất cả (không params)
    - Tìm kiếm với params: query, province, lat, lon, radius
    - Cập nhật Rating từ Firebase cho cả hai trường hợp
    """
    # Lấy query params
    query = request.args.get('query', '').strip()
    province = request.args.get('province', '').strip()
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    radius = request.args.get('radius')
    
    # Nếu có bất kỳ search params nào -> Dùng search algorithm
    if query or province or (lat and lon):
        # Convert types
        try:
            user_lat = float(lat) if lat else None
            user_lon = float(lon) if lon else None
            # Frontend gửi radius (meters), backend dùng km
            # Nhưng search_algorithm tự xử lý bán kính theo logic
        except (ValueError, TypeError):
            user_lat = None
            user_lon = None
        
        # Gọi search algorithm
        results = search_algorithm(
            query=query,
            restaurants_db=DB_RESTAURANTS,
            menus_by_res_id=MENUS_BY_RESTAURANT_ID,
            restaurants_dict=RESTAURANTS,
            province=province,
            user_lat=user_lat,
            user_lon=user_lon
        )
        
        # Cập nhật rating từ Firebase cho kết quả tìm kiếm
        _sync_ratings_from_firebase(results)
        
        return jsonify({
            "success": True,
            "count": len(results),
            "restaurants": results
        }), 200
    
    # Không có params -> Trả về tất cả
    restaurant_list = list(RESTAURANTS.values())
    
    # Cập nhật rating từ Firebase cho toàn bộ danh sách
    _sync_ratings_from_firebase(restaurant_list)
    

    return jsonify({
        "success": True,
        "count": len(restaurant_list),
        "restaurants": restaurant_list
    }), 200


def _sync_ratings_from_firebase(restaurant_list):
    """
    Hàm helper: Đồng bộ rating từ Firebase vào danh sách nhà hàng.
    Cập nhật in-place.
    """
    try:
        # Lấy một lần toàn bộ node rating (tối ưu hơn là for loop gọi DB nhiều lần)
        ratings_ref = db.reference("restaurants_rating")
        ratings_snapshot = ratings_ref.get()  # Kết quả dạng: { "id_nha_hang": {"rating": 4.5}, ... }
        
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


@food_bp.route("/restaurants/search", methods=["GET"])
def search_restaurants():
    """Tìm kiếm nhà hàng (Cũng cần cập nhật Rating)."""
    
    query = request.args.get('q', '').lower()
    
    # Logic tìm kiếm
    all_res = list(RESTAURANTS.values())

def search_restaurants_simple():
    """Tìm kiếm đơn giản theo query string (legacy endpoint)."""
    query = request.args.get('q', '').lower()
    
    if not query:
        return get_all_restaurants()

    # Tìm kiếm đơn giản theo tên hoặc địa chỉ

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