# routes/food/restaurants_route.py

from flask import request, jsonify
from . import food_bp
from core.database import RESTAURANTS, DB_RESTAURANTS, MENUS_BY_RESTAURANT_ID
from core.search import search_algorithm

@food_bp.route("/restaurants", methods=["GET"])
def get_all_restaurants():
    """
    GET /api/restaurants
    Hỗ trợ cả: 
    - Lấy tất cả (không params)
    - Tìm kiếm với params: query, province, lat, lon, radius
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
        
        return jsonify({
            "success": True,
            "count": len(results),
            "restaurants": results
        }), 200
    
    # Không có params -> Trả về tất cả
    restaurant_list = list(RESTAURANTS.values())
    return jsonify({
        "success": True,
        "count": len(restaurant_list),
        "restaurants": restaurant_list
    }), 200


@food_bp.route("/restaurants/search", methods=["GET"])
def search_restaurants_simple():
    """Tìm kiếm đơn giản theo query string (legacy endpoint)."""
    query = request.args.get('q', '').lower()
    
    if not query:
        return get_all_restaurants()

    # Tìm kiếm đơn giản theo tên hoặc địa chỉ
    results = [
        r for r in list(RESTAURANTS.values())
        if query in r.get('name', '').lower() or query in r.get('address', '').lower()
    ]

    return jsonify({
        "success": True,
        "count": len(results),
        "restaurants": results
    }), 200