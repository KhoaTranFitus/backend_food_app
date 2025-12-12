from flask import jsonify, request
from routes.food import food_bp
from core.database import DB_MENUS

@food_bp.route('/foods/<int:food_id>', methods=['GET'])
def get_food_detail(food_id):
    """Lấy chi tiết một món ăn."""
    try:
        # Tìm món ăn trong DB_MENUS
        # Lưu ý: DB_MENUS là list dict, không có index theo ID sẵn nên phải loop
        # Nếu data lớn, nên tạo index bên core/database.py
        food = next((f for f in DB_MENUS if str(f.get('id')) == str(food_id)), None)
        
        if not food:
            return jsonify({"error": "Food not found"}), 404
            
        return jsonify(food)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@food_bp.route('/foods/search', methods=['GET'])
def search_foods():
    """Tìm kiếm món ăn theo tên."""
    try:
        query = request.args.get('q', '').lower().strip()
        if not query:
            return jsonify({"success": True, "foods": []})
            
        results = [
            f for f in DB_MENUS 
            if query in f.get('name', '').lower()
        ]
        
        return jsonify({
            "success": True,
            "count": len(results),
            "foods": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@food_bp.route('/foods/category/<int:category_id>', methods=['GET'])
def get_foods_by_category(category_id):
    """Lấy món ăn theo category."""
    try:
        # Giả sử món ăn cũng có category_id, hoặc lấy tất cả món của nhà hàng thuộc category đó
        # Ở đây giả định món ăn có category_id (nếu không có thì phải join với restaurant)
        # Check cấu trúc DB_MENUS xem có category_id không. Nếu không, ta cần map từ restaurant.
        
        # Cách an toàn hiện tại: Lọc món ăn mà restaurant_id của nó thuộc các nhà hàng trong category đó
        # Tuy nhiên, để đơn giản và nhanh, ta check key category_id trong menu item trước
        
        results = [
            f for f in DB_MENUS 
            if str(f.get('category_id')) == str(category_id)
        ]
        
        return jsonify({
            "success": True,
            "count": len(results),
            "foods": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#@food_bp.route('/foods/restaurant/<int:restaurant_id>', methods=['GET'])
#def get_foods_by_restaurant(restaurant_id):
 #   """Lấy danh sách món ăn của một nhà hàng."""
  #  try:
   #     results = [
    #        f for f in DB_MENUS 
     #       if str(f.get('restaurant_id')) == str(restaurant_id)
      #  ]
        
       # return jsonify({
        #    "success": True,
         #   "count": len(results),
          #  "foods": results
     #   })
   # except Exception as e:
    #    return jsonify({"error": str(e)}), 500
