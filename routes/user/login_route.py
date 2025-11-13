from flask import request, jsonify
from . import user_bp  # Import blueprint
import requests
# Import các biến và dịch vụ đã khởi tạo từ 'core'
#from core.auth_service import API_KEY, auth 

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    # (Đây là code login dùng API Key, không phải admin SDK)
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
        return jsonify({
            "message": "Đăng nhập thành công!",
            "idToken": res_data.get("idToken"),
            "email": res_data.get("email")
        })
    else:
        return jsonify({
            "error": response.json().get("error", {}).get("message", "Sai email hoặc password.")
        }), 400