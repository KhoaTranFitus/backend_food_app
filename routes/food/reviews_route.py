# routes/food/reviews_route.py

from flask import request, jsonify
from firebase_admin import db
from . import food_bp  
from core.auth_service import get_uid_from_auth_header 
import time

# ==========================================================
# ROUTE 1: TẠO/GỬI ĐÁNH GIÁ (POST)
# ==========================================================
@food_bp.route("/reviews", methods=["POST"])
def create_review():
    """
    Gửi đánh giá (rating và comment) cho một nhà hàng và lưu vào Firebase Realtime Database.
    Endpoint: /api/food/reviews
    """
    
    # 1. Xác thực người dùng và lấy ID
    try:
        user_id = get_uid_from_auth_header() 
    except ValueError as e:
        return jsonify({"error": f"Unauthorized. Vui lòng đăng nhập lại. ({e})"}), 401

    data = request.get_json(force=True, silent=True) or {}
    
    # 2. Lấy dữ liệu cần thiết
    target_id = data.get("target_id") # ID của nhà hàng
    rating = data.get("rating")
    comment = data.get("comment")
    review_type = data.get("type", "restaurant") 
    
    # Kiểm tra dữ liệu đầu vào
    if not target_id or not rating or review_type != "restaurant":
        return jsonify({"error": "Thiếu target_id hoặc rating, hoặc loại đánh giá không hợp lệ."}), 400
    
    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            raise ValueError("Rating ngoài phạm vi.")
        target_id = str(target_id).strip() # Đảm bảo ID là chuỗi
    except (TypeError, ValueError):
        return jsonify({"error": "Rating phải là số nguyên từ 1 đến 5 hợp lệ."}), 400

    # 3. Chuẩn bị dữ liệu đánh giá
    timestamp = int(time.time() * 1000)
    review_key = f"{target_id}_{user_id}_{timestamp}" 

    # Lấy thông tin user (từ Firebase)
    user_data = db.reference(f"users/{user_id}").get()
    user_name = user_data.get("name", "Người dùng hiện tại") if user_data else "Người dùng hiện tại"

    review_data = {
        "id": review_key,
        "user_id": user_id,
        "username": user_name,
        "target_id": target_id, 
        "type": review_type,
        "rating": rating,
        "comment": comment or None,
        "timestamp": timestamp,
        "date": time.strftime("%d/%m/%Y", time.localtime(timestamp / 1000))
    }
    
    # 4. Lưu đánh giá vào Firebase 
    try:
        # Lưu vào node reviews_by_restaurant/{target_id}/
        target_reviews_ref = db.reference(f"reviews_by_restaurant/{target_id}/{review_key}")
        target_reviews_ref.set(review_data)
        
        return jsonify({
            "message": "Đánh giá của bạn đã được gửi thành công.",
            "review": review_data
        }), 201

    except Exception as e:
        print(f"Lỗi khi lưu đánh giá vào Firebase: {e}")
        return jsonify({"error": "Lỗi server khi lưu đánh giá."}), 500


# ==========================================================
# ROUTE 2: TẢI ĐÁNH GIÁ (GET)
# ==========================================================
@food_bp.route("/reviews/restaurant/<restaurant_id>", methods=["GET"])
def get_restaurant_reviews(restaurant_id):
    """
    Lấy tất cả đánh giá cho một nhà hàng cụ thể.
    Endpoint: /api/food/reviews/restaurant/<restaurant_id>
    """
    
    # 1. Lấy dữ liệu từ Firebase
    try:
        # Đường dẫn lưu: reviews_by_restaurant/{target_id}
        reviews_ref = db.reference(f"reviews_by_restaurant/{restaurant_id}")
        reviews_dict = reviews_ref.get()

        if not reviews_dict:
            return jsonify({"message": "Không tìm thấy đánh giá nào.", "reviews": []}), 200

        # Chuyển từ dictionary Firebase (key: review_id, value: review_data) thành list
        reviews_list = list(reviews_dict.values())
        
        # 2. Trả về
        return jsonify({
            "success": True,
            "count": len(reviews_list),
            "reviews": reviews_list
        }), 200
        
    except Exception as e:
        print(f"Lỗi khi tải đánh giá từ Firebase: {e}")
        return jsonify({"error": "Lỗi server khi tải đánh giá."}), 500