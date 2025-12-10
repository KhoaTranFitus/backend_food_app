from flask import jsonify
from routes.food import food_bp
from core.database import DB_CATEGORIES

@food_bp.route('/categories', methods=['GET'])
def get_all_categories():
    """Lấy danh sách tất cả danh mục."""
    try:
        return jsonify({
            "success": True,
            "count": len(DB_CATEGORIES),
            "categories": DB_CATEGORIES
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@food_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category_detail(category_id):
    """Lấy thông tin chi tiết danh mục."""
    try:
        category = next((c for c in DB_CATEGORIES if str(c.get('id')) == str(category_id)), None)
        
        if not category:
            return jsonify({"error": "Category not found"}), 404
            
        return jsonify(category)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
