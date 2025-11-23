# routes/user/register_route.py
from flask import request, jsonify
from firebase_admin import auth, db
from . import user_bp
from core.auth_service import send_verification_email

import random
import re

EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    name = data.get("name", "").strip()

    if not email or not password or not name:
        return jsonify({"error": "Thiếu thông tin người dùng."}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Email không hợp lệ."}), 400
    if len(password) < 6:
        return jsonify({"error": "Mật khẩu phải có ít nhất 6 ký tự."}), 400

    try:
        auth.get_user_by_email(email)
        return jsonify({"error": "Email đã tồn tại!"}), 400
    except auth.UserNotFoundError:
        pass
    except Exception as e:
        return jsonify({"error": f"Lỗi khi kiểm tra user: {e}"}), 500

    try:
        firebase_user = auth.create_user(email=email, password=password, email_verified=False)
    except Exception as e:
        return jsonify({"error": f"Tạo user thất bại: {e}"}), 500

    uid = firebase_user.uid

    # Tạo user mới với uid làm key (đồng bộ với google_login)
    new_user = {
        "uid": uid,
        "name": name,
        "email": email,
        "avatar_url": "",
        "favorites": [],
        "history": [],
        "location": {}
    }
    
    users_ref = db.reference("users")
    try:
        users_ref.child(uid).set(new_user)
    except Exception as e:
        try:
            auth.delete_user(uid)
        except Exception:
            pass
        return jsonify({"error": f"Lỗi khi ghi user vào database: {e}"}), 500

    verification_code = str(random.randint(100000, 999999))
    db.reference("verification_codes").child(uid).set({
        "email": email,
        "code": verification_code,
        "timestamp": int(__import__("time").time())
    })

    # Nếu gửi mail thất bại thì trả về, xóa user, xóa mã xác thực
    try:
        send_verification_email(email, verification_code)
    except Exception as e:
        try:
            auth.delete_user(uid)
        except Exception:
            pass
        try:
            users_ref.child(uid).delete()
        except Exception:
            pass
        try:
            db.reference("verification_codes").child(uid).delete()
        except Exception:
            pass
        return jsonify({"error": "Email không tồn tại hoặc gửi mã thất bại. Vui lòng kiểm tra lại."}), 400

    return jsonify({
        "message": "Đăng ký thành công! Mã xác thực đã được gửi đến email của bạn.",
        "user": {"uid": uid, **new_user}
    }), 200

