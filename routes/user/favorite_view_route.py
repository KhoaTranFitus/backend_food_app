from flask import request, jsonify
from firebase_admin import db
from . import user_bp

@user_bp.route("/favorite/view", methods=["POST"])
def favorite_view():
    data = request.get_json(force=True, silent=True) or {}

    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Thiếu user_id"}), 400

    user_ref = db.reference(f"users/{user_id}")
    user_data = user_ref.get()

    if not user_data:
        return jsonify({"error": "Không tìm thấy user"}), 404

    # Lấy danh sách yêu thích
    favorites = user_data.get("favorites", [])

    normalized = []
    for item in favorites:
        try:
            normalized.append(int(item))
        except:
            pass

    return jsonify({
        "user_id": user_id,
        "favorites": normalized
    }), 200