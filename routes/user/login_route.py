from flask import request, jsonify
from . import user_bp  # Import blueprint
import requests
# Import các biến và dịch vụ đã khởi tạo từ 'core'
from core.auth_service import API_KEY, auth 

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}",
        json=payload
    )

    if response.status_code == 200:
        res_data = response.json()
        user = auth.get_user_by_email(email)

        # Nếu chưa xác thực email thì chặn người dùng đăng nhập
        if not user.email_verified:
            return jsonify({
                "error": "Tài khoản chưa được xác thực email. Vui lòng kiểm tra hộp thư của bạn."
            }), 403

        return jsonify({
            "message": "Đăng nhập thành công!",
            "idToken": res_data.get("idToken"),
            "email": res_data.get("email")
        })
    # Phần này là để chuyển đổi tin nhắn báo lỗi của Firebase sang tiếng Việt
    else:
        error_code = response.json().get("error", {}).get("message", "")
        decoded_message = {
            "INVALID_EMAIL": "Email không hợp lệ.",
            "INVALID_LOGIN_CREDENTIALS": "Sai email hoặc mật khẩu.",
            "EMAIL_NOT_FOUND": "Email không tồn tại.",
            "INVALID_PASSWORD": "Sai mật khẩu.",
            "USER_DISABLED": "Tài khoản đã bị vô hiệu hóa."
        }.get(error_code, "Đăng nhập thất bại, vui lòng thử lại.")
        
        return jsonify({"error": decoded_message}), 400