from flask import jsonify
from routes.food import food_bp
from core.database import DB_RESTAURANTS

@food_bp.route('/restaurants', methods=['GET'])
def get_all_restaurants():
    return jsonify(DB_RESTAURANTS)
