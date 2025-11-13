from flask import request, jsonify
from firebase_admin import auth, db
from . import user_bp  # Import blueprint từ __init__.py


@user_bp.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")

    # Kiểm tra đầu vào
    if not email or not code:
        return jsonify({"error": "Thiếu email hoặc mã xác nhận."}), 400

    try:
        # Lấy thông tin người dùng từ Firebase
        user = auth.get_user_by_email(email)
    except auth.UserNotFoundError:
        return jsonify({"error": "Email không tồn tại."}), 400
    except Exception as e:
        return jsonify({"error": f"Lỗi khi truy vấn người dùng: {e}"}), 500

    # Lấy mã xác thực từ Realtime Database
    ref = db.reference("verification_codes").child(user.uid)
    data_ref = ref.get()
    saved_code = str(data_ref.get("code", ""))
    if not data_ref:
        return jsonify({"error": "Không tìm thấy mã xác nhận cho email này."}), 400

    # So sánh mã
    if str(code).strip() == saved_code.strip():
        try:
            auth.update_user(user.uid, email_verified=True)
            ref.delete()
            return jsonify({"message": "✅ Xác thực thành công! Bạn có thể đăng nhập ngay bây giờ."}), 200
        except Exception as e:
            return jsonify({"error": f"Lỗi khi cập nhật trạng thái xác thực: {e}"}), 500
    else:
        return jsonify({"error": "❌ Mã xác thực không chính xác."}), 400