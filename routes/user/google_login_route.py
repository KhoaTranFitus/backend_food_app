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

        uid = idinfo.get("sub")  # Firebase UID từ Google token
        email = idinfo.get("email")
        name = idinfo.get("name")
        picture = idinfo.get("picture")

        users_ref = db.reference("users")
        
        # Kiểm tra user đã tồn tại chưa (dùng uid làm key)
        user_data = users_ref.child(uid).get()

        if user_data:
            # User đã tồn tại, cập nhật thông tin nếu cần
            if user_data.get("name") != name or user_data.get("avatar_url") != picture:
                users_ref.child(uid).update({
                    "name": name,
                    "avatar_url": picture or ""
                })
                user_data["name"] = name
                user_data["avatar_url"] = picture or ""
        else:
            # Tạo user mới với uid làm key
            new_user = {
                "uid": uid,
                "name": name,
                "email": email,
                "avatar_url": picture or "",
                "favorites": [],
                "history": [],
                "location": {}
            }
            users_ref.child(uid).set(new_user)
            user_data = new_user

        return jsonify({
            "success": True,
            "message": "Đăng nhập Google thành công!",
            "user": user_data
        }), 200

    except ValueError as e:
        return jsonify({"success": False, "error": f"Token không hợp lệ hoặc đã hết hạn: {e}"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": f"Lỗi máy chủ: {e}"}), 500
