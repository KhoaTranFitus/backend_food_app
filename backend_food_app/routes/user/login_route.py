from flask import request, jsonify
from . import user_bp   
import json
import os
import uuid  # để tạo token giả

# Đường dẫn tới file users.json
DATA_PATH = os.path.join(os.path.dirname(__file__), '../../data/users.json')

@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Kiểm tra dữ liệu đầu vào
        if not email or not password:
            return jsonify({"message": "Email and password required"}), 400

        # Đọc dữ liệu người dùng từ users.json
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            users = json.load(f)

        # Tìm user phù hợp
        for user in users:
            if user.get('email') == email and user.get('password') == password:
                token = str(uuid.uuid4())  # tạo token giả
                return jsonify({
                    "message": "Login successful",
                    "token": token,
                    "user": {
                        "name": user.get("name"),
                        "email": user.get("email")
                    }
                }), 200

        return jsonify({"message": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({"message": "Error processing login", "error": str(e)}), 500
