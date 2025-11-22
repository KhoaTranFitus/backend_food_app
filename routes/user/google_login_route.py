from flask import Blueprint, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from firebase_admin import db
from core.auth_service import CLIENT_ID
from . import user_bp


@user_bp.route("/google-login", methods=["POST"])
def google_login():
    data = request.get_json()
    token = data.get("idToken")

    if not token:
        return jsonify({"success": False, "error": "Thiếu idToken"}), 400

    try:
        idinfo = id_token.verify_oauth2_token(token, grequests.Request(), CLIENT_ID)

        email = idinfo.get("email")
        name = idinfo.get("name")
        picture = idinfo.get("picture")

        users_ref = db.reference("users")
        users = users_ref.get() or {}

        existing_user = None
        for user_id, user_data in users.items():
            if user_data.get("email") == email:
                existing_user = (user_id, user_data)
                break

        if existing_user:
            user_id, user_data = existing_user
        else:
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
            users_ref.child(new_id).set(new_user)
            user_data = new_user
            user_id = new_id

        return jsonify({
            "success": True,
            "message": "Đăng nhập Google thành công!",
            "user": user_data
        }), 200

    except ValueError as e:
        return jsonify({"success": False, "error": f"Token không hợp lệ hoặc đã hết hạn: {e}"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": f"Lỗi máy chủ: {e}"}), 500
