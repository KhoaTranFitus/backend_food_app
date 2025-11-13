from flask import Blueprint, request, jsonify
import json
import os
from . import user_bp

@user_bp.route("/logout", methods=["POST"])
def logout():
    try:
        data = request.get_json()
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"success": False, "message": "Thiếu ID người dùng"}), 400

        users_path = os.path.join("data", "users.json")

        with open(users_path, "r", encoding="utf-8") as f:
            users = json.load(f)

        user = next((u for u in users if u["id"] == user_id), None)
        if not user:
            return jsonify({"success": False, "message": "Người dùng không tồn tại"}), 404

        return jsonify({"success": True, "message": "Đăng xuất thành công!"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500