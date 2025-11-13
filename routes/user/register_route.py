from flask import request, jsonify
#from firebase_admin import auth, db
from . import user_bp  # Import blueprint từ file __init__.py
#from core.auth_service import send_verification_email # Import hàm gửi mail
import random

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email và mật khẩu không được để trống."}), 400

    try:
        user = auth.get_user_by_email(email)
        return jsonify({"error": "Email đã tồn tại!"}), 400
    except:
        pass
    
    user = auth.create_user(email=email, password=password, email_verified=False)

    # Tạo mã xác thực
    verification_code = str(random.randint(100000, 999999))
    db.reference("verification_codes").child(user.uid).set({
        "email": email,
        "code": verification_code
    })
    
    send_verification_email(email, verification_code)
    return jsonify({"message": "Đăng ký thành công! Mã xác thực đã được gửi đến email của bạn."}), 200