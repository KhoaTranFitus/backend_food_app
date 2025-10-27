from flask import Blueprint, request, jsonify

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if email == "admin@gmail.com" and password == "123":
        return jsonify({"message": "Đăng nhập thành công!"})
    else:
        return jsonify({"message": "Sai email hoặc mật khẩu!"}), 401
