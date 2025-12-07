from flask import request, jsonify
from firebase_admin import auth, db
import requests
import random
import time
from . import user_bp
from core.auth_service import API_KEY, send_verification_email

@user_bp.route("/user/update-email", methods=["POST"])
def change_email():
    data = request.get_json(force=True, silent=True) or {}
    
    uid = data.get("uid")
    password = data.get("password")
    new_email = data.get("new_email", "").strip()

    if not uid or not password or not new_email:
        return jsonify({"error": "Thiếu thông tin xác thực hoặc email mới."}), 400

    user_ref = db.reference(f"users/{uid}")
    user_data = user_ref.get()
    if not user_data:
        return jsonify({"error": "User không tồn tại"}), 404
    
    current_email = user_data.get("email")

    if current_email == new_email:
        return jsonify({"error": "Email mới phải khác email hiện tại."}), 400

    verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    response = requests.post(verify_url, json={"email": current_email, "password": password, "returnSecureToken": True})
    if "error" in response.json():
        return jsonify({"error": "Mật khẩu không đúng."}), 401

    try:
        auth.update_user(uid, email=new_email, email_verified=False)
        
        user_ref.update({"email": new_email})
        
        verification_code = str(random.randint(100000, 999999))
        db.reference("verification_codes").child(uid).set({
            "email": new_email,
            "code": verification_code,
            "timestamp": int(time.time())
        })
        
        send_verification_email(new_email, verification_code)

        return jsonify({
            "message": "Đổi email thành công! Vui lòng kiểm tra email mới để lấy mã xác thực.",
            "require_verify": True
        }), 200

    except auth.EmailAlreadyExistsError:
        return jsonify({"error": "Email này đã được sử dụng bởi tài khoản khác."}), 400
    except Exception as e:
        return jsonify({"error": f"Lỗi khi đổi email: {e}"}), 500

