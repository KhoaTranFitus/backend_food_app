from flask import request, jsonify
from firebase_admin import auth, db
from . import user_bp  # Import blueprint 'user_bp' từ file __init__.py

@user_bp.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")

    if not email or not code:
        return jsonify({"error": "Thiếu email hoặc mã xác nhận."}), 400

    try:
        user = auth.get_user_by_email(email)
    except:
        return jsonify({"error": "Email không tồn tại."}), 400

    ref = db.reference("verification_codes").child(user.uid).get()
    if not ref:
        return jsonify({"error": "Không tìm thấy mã xác nhận cho email này."}), 400

    saved_code = ref.get("code")

    if str(code) == str(saved_code):
        auth.update_user(user.uid, email_verified=True)
        db.reference("verification_codes").child(user.uid).delete()
        return jsonify({"message": "Xác thực thành công! Bạn có thể đăng nhập ngay bây giờ."}), 200
    else:
        return jsonify({"error": "Mã xác thực không chính xác."}), 400