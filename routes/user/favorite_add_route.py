from flask import request, jsonify
import json, os
from . import user_bp
from core.auth_service import load_users, save_users

@user_bp.route("/favorite/add", methods=["POST"])
def favorite_add():
    data = request.get_json()
    user_id = data.get("user_id")
    restaurant_id = data.get("restaurant_id")

    if not user_id or not restaurant_id:
        return jsonify({"error": "Thiếu user_id hoặc restaurant_id"}), 400

    users = load_users()
    for user in users:
        if user["id"] == user_id:
            favorites = user.get("favorites", [])
            if restaurant_id in favorites:
                favorites.remove(restaurant_id)
                action = "removed"
                message = "Đã xóa khỏi danh sách yêu thích."
            else:
                favorites.append(restaurant_id)
                action = "added"
                message = "Đã thêm vào danh sách yêu thích."
            user["favorites"] = favorites
            save_users(users)
            return jsonify({"message": message, "action": action}), 200

    return jsonify({"error": "Không tìm thấy user_id"}), 404