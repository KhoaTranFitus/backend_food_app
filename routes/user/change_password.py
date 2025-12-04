from flask import request, jsonify
from firebase_admin import auth
from . import user_bp

@user_bp.route("/change-password", methods=["POST"])
def change_password():
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("new_password")

    if not email or not new_password:
        return jsonify({"error": "Thiếu dữ liệu"}), 400

    try:
        user = auth.get_user_by_email(email)
        auth.update_user(user.uid, password=new_password)
        return jsonify({"message": "Đổi mật khẩu thành công!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
