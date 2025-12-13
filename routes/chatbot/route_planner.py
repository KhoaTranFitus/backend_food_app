"""
Route Planner - Tạo lộ trình từ danh sách yêu thích
"""
from flask import request, jsonify
from . import chatbot_bp
from firebase_admin import db
from core.auth_service import get_uid_from_auth_header
from core.database import RESTAURANTS
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Tính khoảng cách giữa 2 điểm (km)"""
    R = 6371
    phi1, phi2 = map(math.radians, [lat1, lat2])
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def optimize_route(start_lat, start_lon, restaurants):
    """
    Thuật toán Nearest Neighbor để tối ưu lộ trình
    Tìm quán gần nhất từ vị trí hiện tại, lặp lại
    """
    if not restaurants:
        return []
    
    route = []
    visited = set()
    current_lat, current_lon = start_lat, start_lon
    
    while len(visited) < len(restaurants):
        nearest = None
        min_dist = float('inf')
        
        for r in restaurants:
            rid = r['id']
            if rid in visited:
                continue
            
            dist = calculate_distance(current_lat, current_lon, r['lat'], r['lon'])
            if dist < min_dist:
                min_dist = dist
                nearest = r
        
        if nearest:
            visited.add(nearest['id'])
            route.append({
                **nearest,
                'distance_from_previous': round(min_dist, 2),
                'order': len(route) + 1
            })
            current_lat = nearest['lat']
            current_lon = nearest['lon']
    
    return route

@chatbot_bp.route("/chat/plan-route", methods=["POST"])
def plan_route_from_favorites():
    """
    Tạo lộ trình từ danh sách yêu thích
    
    Request Body:
    {
        "user_lat": 10.7769,
        "user_lon": 106.7009,
        "selected_ids": ["place_id_1", "place_id_2"] // Optional, nếu không có thì lấy tất cả favorites
    }
    
    Response:
    {
        "success": true,
        "route": [
            {
                "order": 1,
                "id": "...",
                "name": "Quán A",
                "address": "...",
                "lat": 10.77,
                "lon": 106.70,
                "distance_from_previous": 1.5,
                "rating": 4.5,
                "price_range": "50,000đ-150,000đ"
            }
        ],
        "total_distance": 5.2,
        "estimated_time": "30 phút"
    }
    """
    try:
        # Xác thực user
        try:
            user_id = get_uid_from_auth_header()
        except ValueError as e:
            return jsonify({"error": f"Unauthorized. {e}"}), 401
        
        data = request.get_json() or {}
        user_lat = data.get('user_lat')
        user_lon = data.get('user_lon')
        selected_ids = data.get('selected_ids')  # Optional
        
        if not user_lat or not user_lon:
            return jsonify({"error": "Missing user_lat or user_lon"}), 400
        
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid coordinates"}), 400
        
        # Lấy danh sách yêu thích từ Firebase
        user_ref = db.reference(f"users/{user_id}")
        user_data = user_ref.get()
        
        if not user_data:
            return jsonify({"error": "User not found"}), 404
        
        favorite_ids = user_data.get('favorites', [])
        
        if not favorite_ids:
            return jsonify({
                "success": True,
                "route": [],
                "message": "Bạn chưa có địa điểm yêu thích nào"
            }), 200
        
        # Nếu có selected_ids, chỉ lấy những quán được chọn
        if selected_ids:
            favorite_ids = [fid for fid in favorite_ids if fid in selected_ids]
        
        # Lấy thông tin chi tiết nhà hàng
        restaurants = []
        for fid in favorite_ids:
            if fid in RESTAURANTS:
                r = RESTAURANTS[fid]
                if r.get('lat') and r.get('lon'):
                    restaurants.append({
                        'id': fid,
                        'name': r.get('name'),
                        'address': r.get('address'),
                        'lat': r.get('lat'),
                        'lon': r.get('lon'),
                        'rating': r.get('rating'),
                        'price_range': r.get('price_range'),
                        'phone_number': r.get('phone_number'),
                        'main_image_url': r.get('main_image_url')
                    })
        
        if not restaurants:
            return jsonify({
                "success": True,
                "route": [],
                "message": "Không tìm thấy thông tin cho các quán yêu thích"
            }), 200
        
        # Tối ưu lộ trình
        optimized_route = optimize_route(user_lat, user_lon, restaurants)
        
        # Tính tổng khoảng cách
        total_distance = sum(r['distance_from_previous'] for r in optimized_route)
        
        # Ước tính thời gian (giả sử tốc độ di chuyển 20km/h trong thành phố)
        estimated_time_hours = total_distance / 20
        estimated_time_minutes = int(estimated_time_hours * 60)
        
        return jsonify({
            "success": True,
            "route": optimized_route,
            "total_distance_km": round(total_distance, 2),
            "estimated_time": f"{estimated_time_minutes} phút",
            "total_stops": len(optimized_route)
        }), 200
        
    except Exception as e:
        import traceback
        print(f"❌ Error planning route: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@chatbot_bp.route("/chat/suggest-route", methods=["POST"])
def suggest_route_via_chat():
    """
    Gợi ý lộ trình qua chatbot (tích hợp OpenAI)
    
    Request Body:
    {
        "user_lat": 10.7769,
        "user_lon": 106.7009,
        "preferences": "Muốn ăn phở và cà phê",
        "budget": 500000,
        "conversation_id": "uuid"
    }
    """
    try:
        from . import agent
        
        user_id = get_uid_from_auth_header()
        data = request.get_json() or {}
        
        user_lat = data.get('user_lat')
        user_lon = data.get('user_lon')
        preferences = data.get('preferences', '')
        budget = data.get('budget')
        
        # Lấy favorites
        user_ref = db.reference(f"users/{user_id}")
        user_data = user_ref.get()
        favorite_ids = user_data.get('favorites', []) if user_data else []
        
        # Build context cho GPT
        favorites_context = ""
        if favorite_ids:
            favorites_context = "\n\n🌟 Danh sách yêu thích của user:\n"
            for fid in favorite_ids[:5]:
                if fid in RESTAURANTS:
                    r = RESTAURANTS[fid]
                    favorites_context += f"- {r.get('name')} ({r.get('address')})\n"
        
        # Tạo prompt cho GPT
        prompt = f"""Người dùng đang ở tọa độ ({user_lat}, {user_lon}).
{favorites_context}

Sở thích: {preferences}
Ngân sách: {budget:,}đ

Hãy gợi ý một lộ trình ăn uống hợp lý (2-3 quán), ưu tiên các quán trong danh sách yêu thích nếu phù hợp."""

        # Call GPT để tạo gợi ý
        import requests
        from datetime import datetime
        
        API_KEY = agent.API_KEY
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Bạn là chuyên gia tư vấn ẩm thực, tạo lộ trình ăn uống tối ưu."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        bot_response = result["choices"][0]["message"]["content"]
        
        return jsonify({
            "success": True,
            "suggestion": bot_response,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        import traceback
        print(f"❌ Error suggesting route: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500
