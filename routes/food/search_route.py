from flask import request, jsonify
from routes.food import food_bp
# Import các biến dữ liệu
from core.database import DB_RESTAURANTS, MENUS_BY_RESTAURANT_ID, RESTAURANTS
# Import thuật toán
from core.search import search_algorithm

@food_bp.route('/search', methods=['POST'])
def search_food():
    """
    API Tìm kiếm Nhà hàng.
    Input: { "query": "...", "province": "...", "lat": 10.1, "lon": 106.2 }
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        
        query = data.get('query')
        province = data.get('province')
        user_lat = data.get('lat')
        user_lon = data.get('lon')
        
        # Chuyển đổi lat/lon sang float
        if user_lat: user_lat = float(user_lat)
        if user_lon: user_lon = float(user_lon)

        # Gọi thuật toán với các tham số đúng logic
        results = search_algorithm(
            query=query, 
            restaurants_db=DB_RESTAURANTS, 
            menus_by_res_id=MENUS_BY_RESTAURANT_ID,
            restaurants_dict=RESTAURANTS,
            province=province,
            user_lat=user_lat,
            user_lon=user_lon
        )
        
        # --- FORMAT LẠI KẾT QUẢ ĐỂ TRẢ VỀ FRONTEND (GIỮ ĐÚNG CẤU TRÚC CŨ) ---
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
                "tags": r.get('tags', []),
                # Các trường bổ sung từ thuật toán mới
                "score": r.get('score'),
                "distance_km": r.get('distance_km')
            }
            
            # Giữ field 'distance' nếu frontend cũ dùng (có thể map từ distance_km hoặc để nguyên logic cũ)
            # Ở đây ta ưu tiên distance_km vừa tính được
            if r.get('distance_km') is not None:
                 formatted['distance'] = r.get('distance_km')

            formatted_results.append(formatted)

        return jsonify({
            "success": True,
            "total": len(formatted_results),
            "places": formatted_results
        })

    except Exception as e:
        import traceback
        print(f"Lỗi Search: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500
