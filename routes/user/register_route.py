from flask import request, jsonify
from firebase_admin import auth, db
from . import user_bp
from core.auth_service import send_verification_email, load_users, save_users
import random
import json, os

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name", "")

    if not email or not password or not name:
        return jsonify({"error": "Thiếu thông tin người dùng."}), 400

    try:
        auth.get_user_by_email(email)
        return jsonify({"error": "Email đã tồn tại!"}), 400
    except:
        pass

    # Tạo user trong Firebase Authentication
    user = auth.create_user(email=email, password=password, email_verified=False)

    # Tạo mã xác thực
    verification_code = str(random.randint(100000, 999999))
    db.reference("verification_codes").child(user.uid).set({
        "email": email,
        "code": verification_code
    })

    # Ghi user mới vào users.json
    users = load_users()

    if users:
        last_id = int(users[-1]["id"][1:])  
        new_id = f"U{last_id + 1:03d}" # Lấy id cuối +1
    else:
        new_id = "U001"

    new_user = {
        "id": new_id,
        "name": name,
        "email": email,
        "password": password,
        "avatar_url": "",
        "favorites": [],
        "history": [],
        "location": {}
    }
    users.append(new_user)
    save_users(users)

    # Gửi email xác thực
    try:
        send_verification_email(email, verification_code)
        return jsonify({
            "message": "Đăng ký thành công! Mã xác thực đã được gửi đến email của bạn."
        }), 200
    # Xóa user vừa thêm khỏi users.json nếu như gmail vừa nhập ko tồn tại
    except Exception as e:
        print(f"❌ Lỗi khi gửi mã xác thực: {e}")
        auth.delete_user(user.uid)
        db.reference("verification_codes").child(user.uid).delete()
        users = [u for u in users if u["email"] != email]
        save_users(users)
        return jsonify({"error": "Email không hợp lệ hoặc không tồn tại. Vui lòng kiểm tra lại."}), 400
