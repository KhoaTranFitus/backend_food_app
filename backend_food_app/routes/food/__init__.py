from flask import Blueprint

food_bp = Blueprint('food', __name__)

# Import các route để đăng ký vào blueprint (KHÔNG import ngược lại food_bp)
from . import search_route, list_all_foods_route,detail_route

