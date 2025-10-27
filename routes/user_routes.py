from flask import Blueprint, request, jsonify

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if email == 'khoa@gmail.com' and password == '123':
        return jsonify({"message": "Đăng nhập thành công!"})
    else:
        return jsonify({"message": "Sai tài khoản/mật khẩu!"}), 401
