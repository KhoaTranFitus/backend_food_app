from flask import request, jsonify
from firebase_admin import db
from . import user_bp
from core.auth_service import get_uid_from_auth_header # Import hàm xác thực token
@user_bp.route("profile", methods=["GET"])
def get_user_profile():
    """
    Lấy thông tin người dùng hiện tại dựa trên token xác thực (JWT)
    được gửi trong header Authorization.
    """
    
    # 1. Lấy user_id từ token (an toàn và bảo mật)
    try:
        user_id = get_uid_from_auth_header() 
    except ValueError as e:
        # Trả về lỗi 401 nếu token không hợp lệ hoặc thiếu
        return jsonify({"error": f"Unauthorized. {e}"}), 401
    except Exception:
        # Xử lý các lỗi khác liên quan đến xác thực
        return jsonify({"error": "Lỗi xác thực token."}), 401
    
    # 2. Lấy thông tin user từ Realtime Database
    user_ref = db.reference(f"users/{user_id}")
    user_data = user_ref.get()

    if not user_data:
        # User đã đăng nhập nhưng không có trong database (trường hợp hiếm)
        return jsonify({"error": "Không tìm thấy thông tin người dùng trong database."}), 404

    # 3. Trả về thông tin user
    return jsonify({
        "message": "Lấy thông tin người dùng thành công.",
        "user": user_data
    }), 200