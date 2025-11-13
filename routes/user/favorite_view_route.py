from flask import request, jsonify
import json, os
from . import user_bp
from core.auth_service import load_users

@user_bp.route("/favorite/view", methods=["POST"])
def favorite_view():
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"success": False, "error": "Thiếu user_id"}), 400

    users = load_users()

    for user in users:
        if user["id"] == user_id:
            favorites = user.get("favorites", [])
            return jsonify({
                "success": True,
                "user_id": user_id,
                "favorites": favorites
            }), 200

    return jsonify({"success": False, "error": "Không tìm thấy user_id"}), 404