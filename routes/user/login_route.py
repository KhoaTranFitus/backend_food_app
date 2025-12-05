from flask import request, jsonify
from firebase_admin import auth, db
from . import user_bp
from core.auth_service import API_KEY
import requests # Cần import này để gọi REST API

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Thiếu email hoặc mật khẩu"}), 400

    try:
        user = auth.get_user_by_email(email)

        # ⭐️ ĐIỀU CHỈNH: Nếu email chưa xác thực, trả về lỗi 403 rõ ràng
        if not user.email_verified:
            return jsonify({
                "error": "Email chưa được xác thực (403). Vui lòng kiểm tra email để xác thực tài khoản."
            }), 403

        # BƯỚC NÀY CHỈ CHẠY KHI EMAIL ĐÃ ĐƯỢC XÁC THỰC
        # Kiểm tra mật khẩu bằng Firebase Auth REST API
        verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        response = requests.post(verify_url, json=payload)
        result = response.json()

        # ⭐️ LỖI CHÍNH: Nếu Firebase báo lỗi, nghĩa là sai email/mật khẩu
        if "error" in result:
            return jsonify({"error": "Sai email hoặc mật khẩu"}), 401

        # Tìm user trong Realtime Database (đã được đồng bộ qua register_route)
        users_ref = db.reference("users")
        users = users_ref.get() or {}

        user_data = None
        for uid, info in users.items():
            if info.get("email") == email:
                user_data = info
                break

        if not user_data:
            return jsonify({"error": "Email không tồn tại"}), 404

        return jsonify({
            "message": "Đăng nhập thành công!",
            "user": user_data,
            "idToken": result.get("idToken")
        }), 200

    except auth.UserNotFoundError:
        # User không tồn tại (Email sai)
        return jsonify({"error": "Email không tồn tại"}), 404
    except Exception as e:
        return jsonify({"error": f"Lỗi máy chủ: {e}"}), 500