from flask import request, jsonify
from firebase_admin import auth, db
from . import user_bp

@user_bp.route("/user/update-profile", methods=["POST"])
def update_profile():
    # Sử dụng silent=True để tránh lỗi nếu format JSON không chuẩn
    data = request.get_json(force=True, silent=True) or {}
    
    uid = data.get("uid")
    name = data.get("name")
    avatar_url = data.get("avatar_url")

    if not uid:
        return jsonify({"error": "Thiếu UID người dùng."}), 400

    user_ref = db.reference(f"users/{uid}")
    
    # Chuẩn bị dữ liệu update
    update_data = {}
    firebase_args = {}

    if name:
        update_data["name"] = name
        firebase_args["display_name"] = name
    
    # --- PHẦN QUAN TRỌNG ĐÃ SỬA ---
    if avatar_url:
        # Luôn lưu vào Realtime Database (DB chấp nhận Base64)
        update_data["avatar_url"] = avatar_url
        
        # CHỈ lưu vào Firebase Auth NẾU nó là đường dẫn HTTP (URL thật)
        # Nếu là Base64 (bắt đầu bằng data:image...) thì KHÔNG ĐƯỢC lưu vào Firebase Auth
        if avatar_url.startswith("http"):
            firebase_args["photo_url"] = avatar_url
    # ------------------------------

    if not update_data:
        return jsonify({"message": "Không có thông tin nào thay đổi."}), 200

    try:
        # 1. Cập nhật Firebase Auth (Chỉ tên, hoặc avatar nếu là link)
        if firebase_args:
            auth.update_user(uid, **firebase_args)

        # 2. Cập nhật Realtime Database (Chứa mọi thứ)
        user_ref.update(update_data)

        # Trả về data mới để Frontend cập nhật
        new_user_data = user_ref.get()
        return jsonify({
            "message": "Cập nhật hồ sơ thành công!",
            "user": new_user_data
        }), 200

    except Exception as e:
        print(f"Lỗi update profile: {e}") # In lỗi ra console server để debug
        return jsonify({"error": f"Lỗi khi cập nhật hồ sơ: {e}"}), 500