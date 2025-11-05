from flask import request, jsonify
from firebase_admin import auth, db
from . import user_bp

@user_bp.route("/verify", methods=["POST"])
def verify():
    # ... (Copy y hệt code hàm verify() từ file của bạn ấy vào đây)
    # Đảm bảo nó dùng @user_bp.route
    data = request.get_json()
    email = data.get("email")
    # ... (phần còn lại của code)
    return jsonify({"message": "Xác thực thành công!"}), 200