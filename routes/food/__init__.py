from flask import Blueprint
food_bp = Blueprint('food', __name__)

# Import các route để đăng ký vào blueprint (KHÔNG import ngược lại food_bp)
from . import search_route
from . import list_all_foods_route
from . import detail_route
from . import direction_route
from . import restaurants_route
import routes.food.get_menu_by_restaurant
