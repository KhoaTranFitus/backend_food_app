from flask import jsonify, request
from routes.food import food_bp
from core.database import DB_MENUS

@food_bp.route('/foods', methods=['GET'])
def get_foods():
    """Lấy danh sách món ăn (có thể phân trang hoặc limit)."""
    try:
        # Lấy tham số limit từ query string (mặc định 50 để tránh overload)
        limit = request.args.get('limit', 50, type=int)
        
        # Chỉ trả về số lượng món ăn giới hạn
        foods = DB_MENUS[:limit]
        
        return jsonify({
            "success": True,
            "count": len(foods),
            "foods": foods
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
