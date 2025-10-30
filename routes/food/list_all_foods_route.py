from flask import jsonify
from routes.food import food_bp

@food_bp.route('/foods')
def get_foods():
	# Đây là route cũ của bạn, dùng để test
	return jsonify([
		{"name": "Bún bò", "price": 40000},
		{"name": "Phở", "price": 35000}
	])
