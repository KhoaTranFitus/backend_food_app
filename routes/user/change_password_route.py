from flask import request, jsonify
from firebase_admin import auth, db
from . import user_bp

@user_bp.route("/change-password", methods=["POST"])
def change_password():
    data = request.get_json(force=True, silent=True) or {}
    
    email = data.get("email", "").strip()
    code = data.get("code", "").strip()
    new_password = data.get("new_password", "")

    if not email or not code or not new_password:
        return jsonify({"error": "Vui lòng nhập đầy đủ: Email, Mã xác thực và Mật khẩu mới."}), 400
    
    if len(new_password) < 6:
        return jsonify({"error": "Mật khẩu mới phải có ít nhất 6 ký tự."}), 400

    try:
        user = auth.get_user_by_email(email)
        uid = user.uid
    except auth.UserNotFoundError:
        return jsonify({"error": "Email không tồn tại."}), 404
    except Exception as e:
        return jsonify({"error": f"Lỗi hệ thống: {e}"}), 500

    ref = db.reference("verification_codes").child(uid)
    record = ref.get()

    if not record:
        return jsonify({"error": "Yêu cầu đổi mật khẩu đã hết hạn hoặc không tồn tại."}), 400
    
    if str(record.get("code")) != str(code) or record.get("email") != email:
        return jsonify({"error": "Mã xác thực không đúng."}), 400

    try:
        auth.update_user(uid, password=new_password)
    except Exception as e:
        return jsonify({"error": f"Lỗi khi cập nhật mật khẩu: {e}"}), 500

    try:
        ref.delete()
    except:
        pass

    return jsonify({
        "message": "Đổi mật khẩu thành công! Bạn có thể đăng nhập bằng mật khẩu mới."
    }), 200

