from flask import request, jsonify
from firebase_admin import db
from . import user_bp
from core.auth_service import get_uid_from_auth_header 

@user_bp.route("/favorite/toggle-restaurant", methods=["POST"])
def favorite_toggle_restaurant():
    # 1. Lấy user_id từ token (An toàn và bảo mật hơn)
    try:
        user_id = get_uid_from_auth_header() 
    except Exception as e:
        return jsonify({"error": f"Unauthorized. Vui lòng đăng nhập lại. ({e})"}), 401

    data = request.get_json(force=True, silent=True) or {}
    restaurant_id = data.get("restaurant_id")

    if not restaurant_id:
        return jsonify({"error": "Thiếu restaurant_id"}), 400
    
    restaurant_id = str(restaurant_id).strip()

    user_ref = db.reference(f"users/{user_id}")
    user_data = user_ref.get()

    if not user_data:
        return jsonify({"error": "Không tìm thấy user"}), 404

    favorites = user_data.get("favorites", [])
    favorites = [str(r) for r in favorites]

    if restaurant_id in favorites:
        favorites = [r for r in favorites if r != restaurant_id]
        action = "removed"
        message = "Đã xóa nhà hàng khỏi danh sách yêu thích."
    else:
        favorites.append(restaurant_id)
        action = "added"
        message = "Đã thêm nhà hàng vào danh sách yêu thích."

    # ⭐️ FIX LỖI SERVER CỤC BỘ: Xóa node 'favorites' nếu danh sách rỗng ⭐️
    data_to_update = {"favorites": favorites}
    if not favorites:
        # Nếu danh sách rỗng, set giá trị là None (để Firebase tự xóa key 'favorites')
        data_to_update["favorites"] = None 

    # Cập nhật lại vào Firebase
    try:
        user_ref.update(data_to_update)
    except Exception as e:
        print(f"Lỗi cập nhật favorites: {e}")
        # Trả về lỗi 500 chi tiết hơn
        return jsonify({"error": f"Lỗi server cục bộ khi cập nhật database: {e}"}), 500

    print(f"✅ USER FAVORITES LIST: {favorites}") 

    # Trả về danh sách favorites mới
    return jsonify({
        "message": message,
        "action": action,
        "favorites": favorites if favorites is not None else []
    }), 200