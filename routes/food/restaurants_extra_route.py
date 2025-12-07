from flask import request, jsonify
from . import food_bp
from core.database import RESTAURANTS, DB_RESTAURANTS
import math

@food_bp.route('/restaurants/nearby', methods=['GET'])
def get_nearby_restaurants():
    """
    API tìm nhà hàng quanh vị trí người dùng.
    Params:
        - latitude: float
        - longitude: float
        - radius: float (km, optional, default=5)
    """
    try:
        lat = request.args.get('latitude')
        lon = request.args.get('longitude')
        radius = float(request.args.get('radius', 5000.0)) # Default 5000m (5km)

        if not lat or not lon:
            return jsonify({"error": "Missing latitude or longitude"}), 400

        user_lat = float(lat)
        user_lon = float(lon)
        
        # ⭐️ FIX UNIT: Convert Meters -> Km
        search_radius_km = radius / 1000.0
        
        results = []
        
        for r in DB_RESTAURANTS:
            r_lat = r.get('lat')
            r_lon = r.get('lon')
            
            if r_lat is None or r_lon is None:
                continue
                
            # Haversine formula
            R = 6371 # Earth radius in km
            dLat = math.radians(r_lat - user_lat)
            dLon = math.radians(r_lon - user_lon)
            a = math.sin(dLat/2) * math.sin(dLat/2) + \
                math.cos(math.radians(user_lat)) * math.cos(math.radians(r_lat)) * \
                math.sin(dLon/2) * math.sin(dLon/2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            d = R * c
            
            if d <= search_radius_km:
                # Tạo bản sao để không ảnh hưởng DB gốc nếu muốn thêm distance
                res_copy = r.copy()
                res_copy['distance'] = round(d, 2)
                results.append(res_copy)
        
        # Sort by distance
        results.sort(key=lambda x: x['distance'])
        
        return jsonify({
            "success": True,
            "count": len(results),
            "restaurants": results
        })

    except ValueError:
        return jsonify({"error": "Invalid parameters"}), 400
    except Exception as e:
        print(f"Error in nearby search: {e}")
        return jsonify({"error": str(e)}), 500

@food_bp.route('/restaurants/category/<int:category_id>', methods=['GET'])
def get_restaurants_by_category(category_id):
    """Lấy danh sách nhà hàng theo category ID."""
    try:
        results = [
            r for r in DB_RESTAURANTS 
            if r.get('category_id') == category_id
        ]
        
        return jsonify({
            "success": True,
            "count": len(results),
            "restaurants": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
