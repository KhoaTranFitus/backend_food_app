# routes/food/reviews_route.py

from flask import request, jsonify
from firebase_admin import db
from . import food_bp                          # <--- FIX LỖI NAMERROR 'food_bp'
from core.auth_service import get_uid_from_auth_header 
from core.database import RESTAURANTS 
import time
import operator                               # <--- THÊM IMPORT ĐỂ SẮP XẾP PYTHON

# ⭐️ HỆ SỐ TIN CẬY (N_MIN): Trọng số của điểm rating ban đầu ⭐️
N_MIN = 10 

def _calculate_new_rating(restaurant_id):
    """
    Tính toán lại điểm trung bình có trọng số (Weighted Average Rating).
    """
    reviews_ref = db.reference(f"reviews_by_restaurant/{restaurant_id}")
    reviews_dict = reviews_ref.get()
    
    res_data = RESTAURANTS.get(restaurant_id)
    if not res_data:
        return None 
        
    try:
        source_rating = float(res_data.get('rating', 4.0)) 
    except ValueError:
        source_rating = 4.0
    
    total_app_rating = 0
    count_app_ratings = 0
    
    if reviews_dict:
        for review in reviews_dict.values():
            total_app_rating += int(review.get('rating', 0))
            count_app_ratings += 1
            
    # Áp dụng công thức Weighted Average Rating
    numerator = (source_rating * N_MIN) + total_app_rating
    denominator = N_MIN + count_app_ratings
    
    if denominator == 0:
        return source_rating 
        
    new_weighted_rating = numerator / denominator
    
    return round(new_weighted_rating, 1)


# ==========================================================
# ROUTE 1: TẠO/GỬI ĐÁNH GIÁ (POST)
# ==========================================================
@food_bp.route("/reviews", methods=["POST"])
def create_review():
    """Gửi đánh giá và cập nhật điểm rating tổng thể."""
    
    try:
        user_id = get_uid_from_auth_header() 
    except ValueError as e:
        return jsonify({"error": f"Unauthorized. Vui lòng đăng nhập lại. ({e})"}), 401

    data = request.get_json(force=True, silent=True) or {}
    target_id = data.get("target_id")
    rating = data.get("rating")
    comment = data.get("comment")
    review_type = data.get("type", "restaurant") 
    
    if not target_id or not rating or review_type != "restaurant":
        return jsonify({"error": "Thiếu target_id hoặc rating, hoặc loại đánh giá không hợp lệ."}), 400
    
    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            raise ValueError("Rating ngoài phạm vi.")
        target_id = str(target_id).strip()
    except (TypeError, ValueError):
        return jsonify({"error": "Rating phải là số nguyên từ 1 đến 5 hợp lệ."}), 400

    # 1. Chuẩn bị dữ liệu và lưu review mới
    timestamp = int(time.time() * 1000)
    review_key = f"{target_id}_{user_id}_{timestamp}" 

    user_ref = db.reference(f"users/{user_id}")
    user_data = user_ref.get()
    user_name = user_data.get("name", "Người dùng hiện tại") if user_data else "Người dùng hiện tại"
    avatar_url = user_data.get("avatar_url") 

    review_data = {
        "id": review_key,
        "user_id": user_id,
        "username": user_name,
        "avatar_url": avatar_url,
        "target_id": target_id, 
        "type": review_type,
        "rating": rating,
        "comment": comment or None,
        "timestamp": timestamp,
        "date": time.strftime("%d/%m/%Y", time.localtime(timestamp / 1000))
    }
    
    response_data = {"message": "Đánh giá của bạn đã được gửi thành công.", "review": review_data} 
    
    try:
        target_reviews_ref = db.reference(f"reviews_by_restaurant/{target_id}/{review_key}")
        target_reviews_ref.set(review_data)
        
        # 2. TÍNH TOÁN VÀ CẬP NHẬT RATING MỚI 
        new_weighted_rating = _calculate_new_rating(target_id)
        
        if new_weighted_rating is not None:
             rating_ref = db.reference(f"restaurants_rating/{target_id}/rating")
             rating_ref.set(new_weighted_rating)
             response_data['review']['new_restaurant_rating'] = new_weighted_rating
             
        print(f"✅ ĐÃ LƯU ĐÁNH GIÁ: Restaurant {target_id}. New Rating: {new_weighted_rating}")
        
        return jsonify(response_data), 201

    except Exception as e:
        print(f"Lỗi khi lưu đánh giá vào Firebase: {e}")
        return jsonify({"error": "Lỗi server khi lưu đánh giá."}), 500


# ==========================================================
# ROUTE 2: TẢI ĐÁNH GIÁ (GET) - Đã FIX logic sắp xếp
# Endpoint: /api/food/reviews/restaurant/<restaurant_id>
# ==========================================================
@food_bp.route("/reviews/restaurant/<restaurant_id>", methods=["GET"])
def get_restaurant_reviews(restaurant_id):
    """
    Lấy đánh giá cho một nhà hàng cụ thể (đã FIX lỗi truy vấn Firebase).
    """
    
    try:
        # 1. Lấy toàn bộ dữ liệu đánh giá từ Firebase (Không dùng query để tránh lỗi)
        reviews_ref = db.reference(f"reviews_by_restaurant/{restaurant_id}")
        reviews_dict = reviews_ref.get()

        if not reviews_dict:
            reviews_list = []
        else:
            # Chuyển từ dictionary sang list
            reviews_list = list(reviews_dict.values())
            
            # ⭐️ [FIX] Sắp xếp bằng Python theo trường 'timestamp' (mới nhất lên đầu) ⭐️
            reviews_list.sort(key=operator.itemgetter('timestamp'), reverse=True)
            
            # Giới hạn 20 review mới nhất (nếu cần giới hạn hiển thị)
            reviews_list = reviews_list[:20]
        
        # 2. Lấy điểm rating đã cập nhật nếu có
        rating_ref = db.reference(f"restaurants_rating/{restaurant_id}/rating")
        current_rating = rating_ref.get()
        
        # 3. Trả về
        return jsonify({
            "success": True,
            "count": len(reviews_list),
            "reviews": reviews_list,
            "current_rating": current_rating 
        }), 200
        
    except Exception as e:
        print(f"Lỗi khi tải đánh giá từ Firebase: {e}")
        return jsonify({"error": "Lỗi server khi tải đánh giá."}), 500


# ==========================================================
# ROUTE 3: LẤY RATING NHANH 
# ==========================================================
@food_bp.route("/rating/<restaurant_id>", methods=["GET"])
def get_single_restaurant_rating(restaurant_id):
    """Lấy điểm rating có trọng số (Weighted Average Rating) mới nhất."""
    try:
        rating_ref = db.reference(f"restaurants_rating/{restaurant_id}/rating")
        current_rating = rating_ref.get()
        
        if current_rating is None:
            res_data = RESTAURANTS.get(restaurant_id)
            source_rating = float(res_data.get('rating', 0)) if res_data else 0
            current_rating = source_rating

        return jsonify({
            "success": True,
            "rating": current_rating 
        }), 200
        
    except Exception as e:
        print(f"Lỗi khi tải rating đơn lẻ: {e}")
        return jsonify({"error": "Lỗi server khi tải rating."}), 500


# ==========================================================
# ROUTE 4: XÓA ĐÁNH GIÁ (DELETE)
# ==========================================================
@food_bp.route("/reviews/<review_id>", methods=["DELETE"])
def delete_review(review_id):
    """Xóa đánh giá (chỉ người tạo mới được xóa)."""
    
    try:
        user_id = get_uid_from_auth_header() 
    except ValueError as e:
        return jsonify({"error": f"Unauthorized. Vui lòng đăng nhập lại. ({e})"}), 401

    parts = review_id.split('_')
    if len(parts) < 3:
        return jsonify({"error": "Định dạng review_id không hợp lệ."}), 400
    
    target_id = parts[0]

    review_ref = db.reference(f"reviews_by_restaurant/{target_id}/{review_id}")
    review_data = review_ref.get()

    if not review_data:
        return jsonify({"error": "Không tìm thấy đánh giá này."}), 404

    if review_data.get('user_id') != user_id:
        return jsonify({"error": "Bạn không có quyền xóa đánh giá này."}), 403

    try:
        review_ref.delete()
        
        new_weighted_rating = _calculate_new_rating(target_id)
        
        if new_weighted_rating is not None:
             rating_ref = db.reference(f"restaurants_rating/{target_id}/rating")
             rating_ref.set(new_weighted_rating)

        print(f"✅ ĐÃ XÓA ĐÁNH GIÁ: Review {review_id} bởi User {user_id}. New Rating: {new_weighted_rating}")
        
        return jsonify({
            "message": "Đánh giá đã được xóa thành công.",
            "new_restaurant_rating": new_weighted_rating
        }), 200

    except Exception as e:
        print(f"Lỗi khi xóa đánh giá: {e}")
        return jsonify({"error": "Lỗi server khi xóa đánh giá."}), 500