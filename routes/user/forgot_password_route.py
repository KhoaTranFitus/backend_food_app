from flask import request, jsonify
from firebase_admin import auth, db
from . import user_bp
from core.auth_service import send_verification_email
import random
import time

@user_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    # Lấy dữ liệu an toàn như cách bạn làm ở register_route
    data = request.get_json(force=True, silent=True) or {}
    email = data.get("email", "").strip()

    if not email:
        return jsonify({"error": "Vui lòng nhập email."}), 400

    # 1. Kiểm tra xem email có tồn tại trong hệ thống (Firebase Auth) không
    try:
        user = auth.get_user_by_email(email)
        uid = user.uid
    except auth.UserNotFoundError:
        # Để bảo mật, dù email không tồn tại ta cũng nên báo lỗi khéo hoặc báo thẳng tùy logic nhóm
        return jsonify({"error": "Email này chưa được đăng ký."}), 404
    except Exception as e:
        return jsonify({"error": f"Lỗi hệ thống: {e}"}), 500

    # 2. Tạo mã xác thực ngẫu nhiên (6 số)
    verification_code = str(random.randint(100000, 999999))

    # 3. Lưu mã vào Realtime Database (ghi đè nếu đã có mã cũ)
    # Mình dùng chung nhánh "verification_codes" để nhất quán với phần register
    try:
        db.reference("verification_codes").child(uid).set({
            "email": email,
            "code": verification_code,
            "timestamp": int(time.time()),
            "type": "reset_password" # Đánh dấu đây là mã đổi pass (nếu cần phân biệt sau này)
        })
    except Exception as e:
        return jsonify({"error": f"Lỗi khi lưu mã xác thực: {e}"}), 500

    # 4. Gửi email
    try:
        send_verification_email(email, verification_code)
    except Exception as e:
        return jsonify({"error": "Không thể gửi email. Vui lòng thử lại sau."}), 500

    return jsonify({
        "message": "Mã xác thực đã được gửi đến email của bạn. Vui lòng kiểm tra hộp thư."
    }), 200

