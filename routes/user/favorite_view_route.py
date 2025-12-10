from flask import request, jsonify
from firebase_admin import db
from . import user_bp
from core.auth_service import get_uid_from_auth_header # Cần import

# ⭐️ ROUTE ĐÃ SỬA: Lấy UID từ Token và dùng GET ⭐️
@user_bp.route("/favorite/view", methods=["GET"])
def favorite_view():
    # 1. Lấy user_id từ token (An toàn)
    try:
        user_id = get_uid_from_auth_header() 
    except Exception as e:
        # Nếu token không hợp lệ hoặc thiếu
        return jsonify({"error": "Unauthorized. Vui lòng đăng nhập."}), 401

    user_ref = db.reference(f"users/{user_id}")
    user_data = user_ref.get()

    if not user_data:
        return jsonify({"error": "Không tìm thấy user"}), 404

    # Lấy danh sách yêu thích
    favorites = user_data.get("favorites", [])
    
    # Đảm bảo trả về ID dưới dạng chuỗi (đồng bộ với ID trong restaurants.json)
    favorites_list = [str(item).strip() for item in favorites]

    return jsonify({
        "user_id": user_id,
        "favorites": favorites_list # Trả về list ID chuỗi
    }), 200