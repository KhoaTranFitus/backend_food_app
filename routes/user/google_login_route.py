from flask import Blueprint, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
import json
import os
from . import user_bp
from core.auth_service import CLIENT_ID, load_users, save_users

@user_bp.route("/google-login", methods=["POST"])
def google_login():
    data = request.get_json()
    token = data.get("idToken")

    if not token:
        return jsonify({"success": False, "error": "Thiếu idToken"}), 400

    try:
        # Xác thực token với Google
        idinfo = id_token.verify_oauth2_token(token, grequests.Request(), CLIENT_ID)

        email = idinfo.get("email")
        name = idinfo.get("name")
        picture = idinfo.get("picture")
        google_id = idinfo.get("sub")

        users = load_users()

        # Tìm xem user đã tồn tại chưa
        existing_user = next((u for u in users if u["email"] == email), None)

        if existing_user:
            user_data = existing_user
        else:
            # Ghi user mới vào users.json
            new_id = f"U{len(users) + 1:03d}" # Lấy id cuối +1
            new_user = {
                "id": new_id,
                "name": name,
                "email": email,
                "avatar_url": picture or "",
                "favorites": [],
                "history": [],
                "location": {}
            }
            users.append(new_user)
            save_users(users)
            user_data = new_user

        # Trả thông tin user về frontend
        return jsonify({
            "success": True,
            "message": "Đăng nhập Google thành công!",
            "user": user_data
        }), 200

    except ValueError as e:
        # Token sai hoặc hết hạn
        return jsonify({"success": False, "error": f"Token không hợp lệ hoặc đã hết hạn: {e}"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": f"Lỗi máy chủ: {e}"}), 500