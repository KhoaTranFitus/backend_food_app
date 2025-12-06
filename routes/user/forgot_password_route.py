from flask import request, jsonify
from firebase_admin import auth, db
from . import user_bp
from core.auth_service import send_verification_email
import random
import time

@user_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json(force=True, silent=True) or {}
    email = data.get("email", "").strip()

    if not email:
        return jsonify({"error": "Vui lòng nhập email."}), 400

    try:
        user = auth.get_user_by_email(email)
        uid = user.uid
    except auth.UserNotFoundError:
        return jsonify({"error": "Email này chưa được đăng ký."}), 404
    except Exception as e:
        return jsonify({"error": f"Lỗi hệ thống: {e}"}), 500

    verification_code = str(random.randint(100000, 999999))

    try:
        db.reference("verification_codes").child(uid).set({
            "email": email,
            "code": verification_code,
            "timestamp": int(time.time()),
            "type": "reset_password"
        })
    except Exception as e:
        return jsonify({"error": f"Lỗi khi lưu mã xác thực: {e}"}), 500

    try:
        send_verification_email(email, verification_code)
    except Exception as e:
        return jsonify({"error": "Không thể gửi email. Vui lòng thử lại sau."}), 500

    return jsonify({
        "message": "Mã xác thực đã được gửi đến email của bạn. Vui lòng kiểm tra hộp thư."
    }), 200

