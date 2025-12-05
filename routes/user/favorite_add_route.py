from flask import request, jsonify
from firebase_admin import db
from . import user_bp
from core.auth_service import get_uid_from_auth_header 

# ⭐️ ROUTE ĐÃ SỬA LỖI VÀ TỐI ƯU ⭐️
@user_bp.route("/favorite/toggle-restaurant", methods=["POST"])
def favorite_toggle_restaurant():
    # 1. Lấy user_id từ token (An toàn và bảo mật hơn)
    try:
        user_id = get_uid_from_auth_header() 
    except Exception as e:
        # Nếu token không hợp lệ hoặc thiếu
        return jsonify({"error": f"Unauthorized. {e}"}), 401

    data = request.get_json(force=True, silent=True) or {}
    restaurant_id = data.get("restaurant_id")

    if not restaurant_id:
        return jsonify({"error": "Thiếu restaurant_id"}), 400
    
    # ⭐️ FIX LỖI: SỬ DỤNG ID DƯỚI DẠNG CHUỖI (STRING) ⭐️
    restaurant_id = str(restaurant_id).strip()

    user_ref = db.reference(f"users/{user_id}")
    user_data = user_ref.get()

    if not user_data:
        return jsonify({"error": "Không tìm thấy user"}), 404

    # Lấy danh sách yêu thích hiện tại
    favorites = user_data.get("favorites", [])
    
    # Đảm bảo các ID trong favorites cũng là string
    favorites = [str(r) for r in favorites]

    if restaurant_id in favorites:
        # Xóa khỏi danh sách yêu thích
        favorites = [r for r in favorites if r != restaurant_id]
        action = "removed"
        message = "Đã xóa nhà hàng khỏi danh sách yêu thích."
    else:
        # Thêm vào danh sách yêu thích
        favorites.append(restaurant_id)
        action = "added"
        message = "Đã thêm nhà hàng vào danh sách yêu thích."

    # Cập nhật lại vào Firebase
    try:
        user_ref.update({"favorites": favorites}) 
    except Exception as e:
        return jsonify({"error": f"Lỗi khi cập nhật Firebase: {e}"}), 500

    return jsonify({
        "message": message,
        "action": action,
        "restaurant_id": restaurant_id,
        "favorites": favorites 
    }), 200