from flask import Blueprint

# Tạo Blueprint cho map
map_bp = Blueprint('map', __name__)

# Import các route con
from . import markers_route
from . import tags_route
from . import filter_route
