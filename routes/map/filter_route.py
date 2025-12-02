# routes/map/filter_route.py
from flask import jsonify, request
from routes.map import map_bp
from core.database import restaurants_data, categories_data

@map_bp.route("/map/filter", methods=["POST"])
def filter_map_markers():
    """
    API lọc markers trên bản đồ theo các tiêu chí
    
    Request Body:
        - lat: float (optional) - Vĩ độ vị trí hiện tại
        - lon: float (optional) - Kinh độ vị trí hiện tại
        - radius: float (optional) - Bán kính tìm kiếm (km), default: 10
        - categories: list[int] (optional) - Danh sách category IDs
        - price_levels: list[int] (optional) - Danh sách price levels (1-4)
        - min_rating: float (optional) - Rating tối thiểu
        - max_rating: float (optional) - Rating tối đa
        - tags: list[str] (optional) - Danh sách tags cần filter
        - limit: int (optional) - Số lượng kết quả tối đa, default: 100
    
    Returns:
        JSON với danh sách markers đã lọc
    """
    try:
        data = request.get_json() or {}
        
        # Lấy filters từ request
        user_lat = data.get('lat')
        user_lon = data.get('lon')
        radius = data.get('radius', 10)  # km
        filter_categories = data.get('categories', [])
        filter_price_levels = data.get('price_levels', [])
        min_rating = data.get('min_rating', 0)
        max_rating = data.get('max_rating', 5)
        filter_tags = data.get('tags', [])
        limit = data.get('limit', 100)
        
        # Hàm tính khoảng cách (Haversine formula)
        def calculate_distance(lat1, lon1, lat2, lon2):
            import math
            R = 6371  # Bán kính trái đất (km)
            
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            
            a = (math.sin(dlat / 2) ** 2 + 
                 math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
                 math.sin(dlon / 2) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            return R * c
        
        # Lọc restaurants
        filtered_restaurants = []
        
        for restaurant in restaurants_data:
            rest_lat = restaurant.get('lat')
            rest_lon = restaurant.get('lon')
            
            if not rest_lat or not rest_lon:
                continue
            
            # Filter by radius nếu có vị trí người dùng
            if user_lat and user_lon:
                distance = calculate_distance(user_lat, user_lon, rest_lat, rest_lon)
                if distance > radius:
                    continue
            else:
                distance = None
            
            # Filter by category
            if filter_categories and restaurant.get('category_id') not in filter_categories:
                continue
            
            # Filter by price level
            if filter_price_levels and restaurant.get('price_level') not in filter_price_levels:
                continue
            
            # Filter by rating
            rating = restaurant.get('rating', 0)
            if rating < min_rating or rating > max_rating:
                continue
            
            # Filter by tags
            if filter_tags:
                restaurant_tags = restaurant.get('tags', [])
                if not any(tag in restaurant_tags for tag in filter_tags):
                    continue
            
            # Tạo marker object
            marker = {
                "id": restaurant.get('id'),
                "name": restaurant.get('name'),
                "lat": rest_lat,
                "lon": rest_lon,
                "rating": rating,
                "price_level": restaurant.get('price_level'),
                "category_id": restaurant.get('category_id'),
                "address": restaurant.get('address'),
                "phone_number": restaurant.get('phone_number'),
                "open_hours": restaurant.get('open_hours'),
                "main_image_url": restaurant.get('main_image_url'),
                "tags": restaurant.get('tags', [])
            }
            
            # Thêm khoảng cách nếu có
            if distance is not None:
                marker['distance'] = round(distance, 2)
            
            # Thêm category info
            category = next((c for c in categories_data if c['id'] == restaurant.get('category_id')), None)
            if category:
                marker['category_name'] = category.get('name')
                marker['category_icon'] = category.get('icon')
            
            filtered_restaurants.append(marker)
        
        # Sắp xếp theo khoảng cách nếu có vị trí người dùng
        if user_lat and user_lon:
            filtered_restaurants.sort(key=lambda x: x.get('distance', float('inf')))
        
        # Giới hạn số lượng kết quả
        filtered_restaurants = filtered_restaurants[:limit]
        
        return jsonify({
            "success": True,
            "total": len(filtered_restaurants),
            "filters_applied": {
                "has_location": user_lat is not None and user_lon is not None,
                "radius_km": radius if user_lat and user_lon else None,
                "categories": filter_categories,
                "price_levels": filter_price_levels,
                "min_rating": min_rating,
                "max_rating": max_rating,
                "tags": filter_tags
            },
            "data": filtered_restaurants
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Lỗi khi lọc markers: {str(e)}"
        }), 500
