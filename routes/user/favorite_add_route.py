from flask import request, jsonify
from firebase_admin import db
from . import user_bp

@user_bp.route("/favorite/add", methods=["POST"])
def favorite_add():
    data = request.get_json(force=True, silent=True) or {}
    user_id = data.get("user_id")
    restaurant_id = data.get("restaurant_id")

    if not user_id or not restaurant_id:
        return jsonify({"error": "Thiếu user_id hoặc restaurant_id"}), 400
    try:
        restaurant_id = int(restaurant_id)
    except Exception:
        return jsonify({"error": "restaurant_id phải là số nguyên"}), 400

    user_ref = db.reference(f"users/{user_id}")
    user_data = user_ref.get()

    if not user_data:
        return jsonify({"error": "Không tìm thấy user"}), 404

    favorites = user_data.get("favorites", [])
    normalized = []
    for it in favorites:
        try:
            normalized.append(int(it)) 
        except Exception:
            pass
    favorites = normalized # -> Cái đoạn normalized này là để chuyển cái id restaurant thành số nguyên, theo như trong cái restaurants.json

    if restaurant_id in favorites:
        favorites = [r for r in favorites if r != restaurant_id]
        user_ref.update({"favorites": favorites})
        return jsonify({
            "message": "Đã xóa khỏi danh sách yêu thích.",
            "action": "removed",
            "favorites": favorites
        }), 200
    else:
        favorites.append(restaurant_id)
        user_ref.update({"favorites": favorites})
        return jsonify({
            "message": "Đã thêm vào danh sách yêu thích.",
            "action": "added",
            "favorites": favorites
        }), 200