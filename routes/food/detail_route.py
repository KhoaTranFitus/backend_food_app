# routes/food/detail_route.py
from flask import jsonify
from routes.food import food_bp
from firebase_admin import db 
from core.database import RESTAURANTS, MENUS_BY_RESTAURANT_ID

@food_bp.route('/detail/<int:restaurant_id>', methods=['GET'])
def get_restaurant_detail(restaurant_id):
    """Lấy chi tiết nhà hàng và menu của nhà hàng đó."""
    # 1. Tìm nhà hàng có ID tương ứng (dùng RESTAURANTS_DICT index)
    rid = str(restaurant_id)
    # Lưu ý: Biến RESTAURANTS trong file review là dict, ở đây kiểm tra lại xem nó là RESTAURANTS hay RESTAURANTS_DICT
    # Giả sử bạn import RESTAURANTS từ core.database
    restaurant = RESTAURANTS.get(rid)
    
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    # 2. Lấy menu tương ứng (nếu có) - dùng MENUS_BY_RESTAURANT_ID index
    menu_items = MENUS_BY_RESTAURANT_ID.get(rid, [])

    # 3. [MỚI] Lấy Rating thực tế từ Firebase (Tính năng bạn cần khôi phục)
    real_rating = restaurant.get('rating', 0) # Mặc định lấy rating gốc
    try:
        rating_ref = db.reference(f"restaurants_rating/{rid}/rating")
        firebase_rating = rating_ref.get()
        if firebase_rating is not None:
            real_rating = firebase_rating
    except Exception as e:
        print(f"Lỗi lấy rating Firebase: {e}")

    # 4. Gộp dữ liệu lại
    detail = {
        **restaurant,
        "rating": real_rating, # Ghi đè rating mới
        "menu": menu_items
    }

    return jsonify(detail)