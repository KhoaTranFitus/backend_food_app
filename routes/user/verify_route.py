from flask import request, jsonify
from firebase_admin import auth, db
from . import user_bp

@user_bp.route("/verify", methods=["POST"])
def verify_email():
    data = request.get_json()

    email = data.get("email")
    code = data.get("code")

    if not email or not code:
        return jsonify({"error": "Thiếu email hoặc mã xác thực."}), 400

    try:
        user = auth.get_user_by_email(email)
    except:
        return jsonify({"error": "Email không tồn tại."}), 400

    uid = user.uid

    ref = db.reference("verification_codes").child(uid)
    record = ref.get()

    if not record or record.get("code") != code:
        return jsonify({"error": "Mã xác thực không đúng."}), 400

    try:
        auth.update_user(uid, email_verified=True)
    except Exception as e:
        return jsonify({"error": f"Lỗi khi cập nhật trạng thái xác thực: {e}"}), 500

    ref.delete()

    return jsonify({"message": "Xác thực email thành công!"}), 200