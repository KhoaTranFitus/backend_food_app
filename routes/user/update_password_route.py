from flask import request, jsonify
from firebase_admin import auth, db
import requests
from . import user_bp
from core.auth_service import API_KEY

@user_bp.route("/user/update-password", methods=["POST"])
def change_password_logged_in():
    data = request.get_json(force=True, silent=True) or {}
    
    uid = data.get("uid")
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not uid or not old_password or not new_password:
        return jsonify({"error": "Vui lòng nhập đủ: Mật khẩu cũ và Mật khẩu mới."}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Mật khẩu mới phải có ít nhất 6 ký tự."}), 400

    # 1. Lấy email từ DB
    user_ref = db.reference(f"users/{uid}")
    user_data = user_ref.get()
    
    if not user_data or "email" not in user_data:
        print(f"DEBUG: Không tìm thấy email trong DB cho UID {uid}")
        return jsonify({"error": "Lỗi dữ liệu user (không tìm thấy email)."}), 404
    
    email = user_data["email"]
    print(f"DEBUG: Đang thử đổi pass cho email: {email}")

    # 2. Xác thực mật khẩu cũ
    verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {
        "email": email,
        "password": old_password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(verify_url, json=payload)
        result = response.json()
        
        # --- DEBUG QUAN TRỌNG: IN LỖI RA TERMINAL ---
        if "error" in result:
            error_msg = result["error"].get("message", "")
            print("❌ DEBUG LỖI TỪ FIREBASE:", error_msg)
            print("Chi tiết:", result)

            if error_msg == "INVALID_PASSWORD" or error_msg == "INVALID_LOGIN_CREDENTIALS":
                return jsonify({"error": "Mật khẩu cũ không đúng."}), 401
            elif error_msg == "EMAIL_NOT_FOUND":
                return jsonify({"error": "Email không tồn tại trong hệ thống xác thực."}), 404
            elif error_msg == "USER_DISABLED":
                return jsonify({"error": "Tài khoản đã bị vô hiệu hóa."}), 403
            else:
                return jsonify({"error": f"Lỗi xác thực: {error_msg}"}), 400

        # 3. Nếu đúng, tiến hành cập nhật
        auth.update_user(uid, password=new_password)
        print("✅ Đổi mật khẩu thành công!")
        
        return jsonify({"message": "Đổi mật khẩu thành công!"}), 200

    except Exception as e:
        print(f"❌ Lỗi server: {e}")
        return jsonify({"error": f"Lỗi hệ thống: {e}"}), 500