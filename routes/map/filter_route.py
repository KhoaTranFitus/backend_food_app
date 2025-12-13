# routes/map/filter_route.py
from flask import jsonify, request
from routes.map import map_bp
from core.database import DB_RESTAURANTS, DB_CATEGORIES

@map_bp.route("/map/filter", methods=["POST"])
def filter_map_markers():
    """
    API lọc markers trên bản đồ theo các tiêu chí
    
    Request Body:
        - lat: float (optional) - Vĩ độ vị trí hiện tại
        - lon: float (optional) - Kinh độ vị trí hiện tại
        - radius: float (optional) - Bán kính tìm kiếm (km), default: 5
        - categories: list[int] (optional) - Danh sách category IDs (None=no filter, []=empty result, [1,2,3]=strict filter)
        - min_price: int (optional) - Giá tối thiểu (VND)
        - max_price: int (optional) - Giá tối đa (VND)
        - min_rating: float (optional) - Rating tối thiểu
        - max_rating: float (optional) - Rating tối đa
        - tags: list[str] (optional) - Danh sách tags cần filter
        - limit: int (optional) - Số lượng kết quả tối đa, default: None (không giới hạn)
    
    Returns:
        JSON với danh sách markers đã lọc
    """
    try:
        data = request.get_json() or {}
        
        # Lấy filters từ request
        user_lat = data.get('lat')
        user_lon = data.get('lon')
        radius = data.get('radius', 5)  # km - default 5km (tăng từ 2km)
        filter_categories = data.get('categories')  # None=no filter, []=strict filter (empty), [1,2,3]=strict filter
        min_price = data.get('min_price')  # VND
        max_price = data.get('max_price')  # VND
        min_rating = data.get('min_rating', 0)
        max_rating = data.get('max_rating', 5)
        filter_tags = data.get('tags', [])
        limit = data.get('limit', None)  # None = không giới hạn
        
        # 🔍 LOGGING REQUEST
        print(f"\n{'='*60}")
        print(f"🗺️  MAP FILTER REQUEST")
        print(f"{'='*60}")
        print(f"📍 User Location: ({user_lat}, {user_lon})")
        print(f"📏 Radius: {radius} km")
        print(f"📂 Categories: {filter_categories}")
        print(f"💰 Price: {min_price} - {max_price}")
        print(f"⭐ Rating: {min_rating} - {max_rating}")
        print(f"🏷️  Tags: {filter_tags}")
        print(f"{'='*60}\n")
        
        # Hàm parse price_range string thành số
        def parse_price_range(price_range_str):
            """
            Parse "50,000đ-150,000đ" -> (50000, 150000)
            Parse "300,000đ+" -> (300000, float('inf'))
            """
            if not price_range_str:
                return (0, float('inf'))
            
            try:
                # Remove "đ" và spaces
                price_str = price_range_str.replace('đ', '').replace(' ', '').replace(',', '')
                
                if '+' in price_str:
                    # "300000+" -> min=300000, max=inf
                    min_val = int(price_str.replace('+', ''))
                    return (min_val, float('inf'))
                elif '-' in price_str:
                    # "50000-150000" -> (50000, 150000)
                    parts = price_str.split('-')
                    return (int(parts[0]), int(parts[1]))
                else:
                    # Single value
                    val = int(price_str)
                    return (val, val)
            except:
                return (0, float('inf'))
        
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
        total_checked = 0
        skipped_no_coords = 0
        skipped_distance = 0
        skipped_category = 0
        skipped_price = 0
        skipped_rating = 0
        skipped_tags = 0
        
        for restaurant in DB_RESTAURANTS:
            total_checked += 1
            rest_lat = restaurant.get('lat')
            rest_lon = restaurant.get('lon')
            
            # Skip nếu không có tọa độ
            if not rest_lat or not rest_lon:
                skipped_no_coords += 1
                continue
            
            # Filter by radius nếu có vị trí người dùng
            if user_lat and user_lon:
                distance = calculate_distance(user_lat, user_lon, rest_lat, rest_lon)
                if distance > radius:
                    skipped_distance += 1
                    continue
            else:
                distance = None
            
            # Filter by category (cải tiến: xử lý null/undefined category_id)
            # If filter_categories is explicitly set (empty list or values), apply strict filtering
            # If filter_categories is None, don't filter by category (show all)
            if filter_categories is not None and len(filter_categories) > 0:
                rest_category = restaurant.get('category_id')
                # Cho phép null/undefined category qua filter nếu không có category filter
                if rest_category is not None and rest_category not in filter_categories:
                    skipped_category += 1
                    continue
            
            # Filter by price range
            if min_price is not None or max_price is not None:
                price_range = restaurant.get('price_range', '')
                rest_min, rest_max = parse_price_range(price_range)
                
                # Kiểm tra overlap: restaurant price range có giao với filter range không
                if min_price is not None and rest_max < min_price:
                    skipped_price += 1
                    continue
                if max_price is not None and rest_min > max_price:
                    skipped_price += 1
                    continue
            
            # Filter by rating
            rating = restaurant.get('rating', 0)
            if rating < min_rating or rating > max_rating:
                skipped_rating += 1
                continue
            
            # Filter by tags
            if filter_tags and len(filter_tags) > 0:
                restaurant_tags = restaurant.get('tags', [])
                if not any(tag in restaurant_tags for tag in filter_tags):
                    skipped_tags += 1
                    continue
            
            # Tạo marker object với format frontend expect
            category_id = restaurant.get('category_id', 1)
            
            # Map category_id sang dishType và pinColor
            category_map = {
                1: {"dishType": "dry", "pinColor": "red"},
                2: {"dishType": "soup", "pinColor": "blue"},
                3: {"dishType": "vegetarian", "pinColor": "green"},
                4: {"dishType": "salty", "pinColor": "orange"},
                5: {"dishType": "seafood", "pinColor": "purple"}
            }
            category_info = category_map.get(category_id, {"dishType": "dry", "pinColor": "red"})
            
            marker = {
                "id": restaurant.get('id'),
                "name": restaurant.get('name'),
                "address": restaurant.get('address'),
                "position": {
                    "lat": rest_lat,
                    "lon": rest_lon
                },
                "dishType": category_info["dishType"],
                "pinColor": category_info["pinColor"],
                "rating": rating,
                "price_range": restaurant.get('price_range'),
                "phone_number": restaurant.get('phone_number'),
                "open_hours": restaurant.get('open_hours'),
                "main_image_url": restaurant.get('main_image_url'),
                "tags": restaurant.get('tags', [])
            }
            
            # Thêm khoảng cách nếu có
            if distance is not None:
                marker['distance'] = round(distance, 2)
            
            filtered_restaurants.append(marker)
        
        # Sắp xếp theo khoảng cách nếu có vị trí người dùng
        if user_lat and user_lon:
            filtered_restaurants.sort(key=lambda x: x.get('distance', float('inf')))
        
        # Giới hạn số lượng kết quả nếu có limit
        if limit is not None:
            filtered_restaurants = filtered_restaurants[:limit]
        
        # 📊 LOGGING RESULTS
        print(f"📊 FILTER RESULTS:")
        print(f"   ✅ Matched: {len(filtered_restaurants)} restaurants")
        print(f"   📝 Total checked: {total_checked}")
        print(f"   ❌ Skipped breakdown:")
        print(f"      - No coordinates: {skipped_no_coords}")
        print(f"      - Outside radius: {skipped_distance}")
        print(f"      - Category mismatch: {skipped_category}")
        print(f"      - Price mismatch: {skipped_price}")
        print(f"      - Rating mismatch: {skipped_rating}")
        print(f"      - Tags mismatch: {skipped_tags}")
        
        if len(filtered_restaurants) > 0:
            print(f"   🏆 Top 3 results:")
            for i, r in enumerate(filtered_restaurants[:3]):
                dist_str = f"{r.get('distance', 'N/A')} km" if r.get('distance') else "N/A"
                print(f"      {i+1}. {r['name']} - {dist_str} - ⭐{r['rating']}")
        else:
            print(f"   ⚠️  No results found! Check filters.")
        print(f"{'='*60}\n")
        
        return jsonify({
            "success": True,
            "total": len(filtered_restaurants),
            "places": filtered_restaurants,
            "filters_applied": {
                "has_location": user_lat is not None and user_lon is not None,
                "radius_km": radius if user_lat and user_lon else None,
                "categories": filter_categories,
                "min_price": min_price,
                "max_price": max_price,
                "min_rating": min_rating,
                "max_rating": max_rating,
                "tags": filter_tags
            },
            "debug_stats": {
                "total_checked": total_checked,
                "skipped_no_coords": skipped_no_coords,
                "skipped_distance": skipped_distance,
                "skipped_category": skipped_category,
                "skipped_price": skipped_price,
                "skipped_rating": skipped_rating,
                "skipped_tags": skipped_tags
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Lỗi khi lọc markers: {str(e)}"
        }), 500
