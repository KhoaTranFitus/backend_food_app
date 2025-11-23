from flask import request, jsonify
from firebase_admin import auth, db
from . import user_bp
from core.auth_service import API_KEY

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Thiếu email hoặc mật khẩu"}), 400

    try:
        user = auth.get_user_by_email(email)

        if not user.email_verified:
            return jsonify({"error": "Email chưa được xác thực. Vui lòng kiểm tra email của bạn."}), 403

        # Kiểm tra mật khẩu bằng Firebase Auth REST API
        import requests

        verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        response = requests.post(verify_url, json=payload)
        result = response.json()

        if "error" in result:
            return jsonify({"error": "Sai email hoặc mật khẩu"}), 401

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
        return jsonify({"error": "Email không tồn tại"}), 404
    except Exception as e:
        return jsonify({"error": f"Lỗi máy chủ: {e}"}), 500

