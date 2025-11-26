from flask import request, jsonify
import requests
from . import food_bp

# Không cần import API Key nữa vì OSRM miễn phí công khai

@food_bp.route('/direction', methods=['POST'])
def get_direction():
    """
    API chỉ đường dùng OSRM (OpenStreetMap).
    Frontend gửi: {
        "origin": { "lat": 10.762, "lon": 106.682 },
        "destination": { "lat": 10.755, "lon": 106.671 },
        "mode": "driving" (tùy chọn: driving, walking, cycling)
    }
    """
    try:
        data = request.get_json()
        origin = data.get("origin")
        destination = data.get("destination")
        # OSRM hỗ trợ: 'driving' (xe hơi), 'foot' (đi bộ), 'bike' (xe đạp)
        # Map 'walking' -> 'foot', 'bicycling' -> 'bike'
        mode_input = data.get("mode", "driving")
        mode_map = {
            "driving": "driving",
            "walking": "foot",
            "bicycling": "bike"
        }
        mode = mode_map.get(mode_input, "driving")

        if not origin or not destination:
            return jsonify({"error": "Thiếu tọa độ origin hoặc destination"}), 400

        # 1. Chuẩn bị URL cho OSRM
        # LƯU Ý QUAN TRỌNG: OSRM dùng format {Longitude},{Latitude} (Ngược với Google)
        start_coords = f"{origin['lon']},{origin['lat']}"
        end_coords = f"{destination['lon']},{destination['lat']}"
        
        # URL: http://router.project-osrm.org/route/v1/{profile}/{coordinates}
        osrm_url = f"http://router.project-osrm.org/route/v1/{mode}/{start_coords};{end_coords}"
        
        params = {
            "overview": "full",       # Lấy toàn bộ hình dạng đường đi
            "geometries": "polyline", # Trả về chuỗi mã hóa (giống Google để dễ vẽ)
            "steps": "true"           # Lấy chi tiết từng bước đi
        }

        # 2. Gọi OSRM API
        # (Vì là server public miễn phí nên đôi khi có thể chậm hoặc timeout)
        response = requests.get(osrm_url, params=params, timeout=5) 
        
        if response.status_code != 200:
            return jsonify({"error": "Lỗi kết nối đến OSRM"}), 502
            
        result = response.json()

        if result.get("code") != "Ok":
            return jsonify({
                "error": "Không tìm thấy đường đi",
                "detail": result.get("message")
            }), 400

        # 3. Chuẩn hóa dữ liệu trả về (Để Frontend dễ dùng)
        # OSRM trả về cấu trúc khác Google, ta nên map lại một chút cho đẹp
        route = result["routes"][0]
        formatted_result = {
            "distance_meters": route["distance"],
            "duration_seconds": route["duration"],
            "overview_polyline": route["geometry"], # Chuỗi để vẽ lên bản đồ
            "legs": [{
                "steps": route["legs"][0]["steps"],
                "start_address": "Vị trí xuất phát", # OSRM không trả về tên đường chính xác
                "end_address": "Điểm đến"
            }]
        }

        return jsonify(formatted_result), 200

    except Exception as e:
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500