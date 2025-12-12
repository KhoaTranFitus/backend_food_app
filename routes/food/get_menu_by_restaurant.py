from flask import jsonify
from routes.food import food_bp
from core.database import MENUS_BY_RESTAURANT_ID

@food_bp.route('/foods/restaurant/<string:restaurant_id>', methods=['GET'])
def get_foods_by_restaurant(restaurant_id):
    rid = str(restaurant_id)
    menu = MENUS_BY_RESTAURANT_ID.get(rid, None)

    if menu is None:
        return jsonify([]), 200

    return jsonify(menu), 200
