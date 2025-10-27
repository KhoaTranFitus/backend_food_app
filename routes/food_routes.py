from flask import Blueprint, jsonify

food_bp = Blueprint('food', __name__)  # <-- Biến bạn cần import từ app.py

@food_bp.route('/foods')
def get_foods():
    return jsonify([
        {"name": "Bún bò", "price": 40000},
        {"name": "Phở", "price": 35000}
    ])
