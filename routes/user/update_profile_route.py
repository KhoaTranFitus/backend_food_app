from flask import request, jsonify
from firebase_admin import auth, db
from . import user_bp

@user_bp.route("/user/update-profile", methods=["POST"])
def update_profile():
    data = request.get_json(force=True, silent=True) or {}
    
    uid = data.get("uid")
    name = data.get("name")
    avatar_url = data.get("avatar_url")

    if not uid:
        return jsonify({"error": "Thiếu UID người dùng."}), 400

    user_ref = db.reference(f"users/{uid}")
    
    update_data = {}
    firebase_args = {}

    if name:
        update_data["name"] = name
        firebase_args["display_name"] = name
    
    if avatar_url:
        update_data["avatar_url"] = avatar_url
        if avatar_url.startswith("http"):
            firebase_args["photo_url"] = avatar_url
    # ------------------------------

    if not update_data:
        return jsonify({"message": "Không có thông tin nào thay đổi."}), 200

    try:
        if firebase_args:
            auth.update_user(uid, **firebase_args)

        user_ref.update(update_data)

        new_user_data = user_ref.get()
        return jsonify({
            "message": "Cập nhật hồ sơ thành công!",
            "user": new_user_data
        }), 200

    except Exception as e:
        print(f"Lỗi update profile: {e}")
        return jsonify({"error": f"Lỗi khi cập nhật hồ sơ: {e}"}), 500