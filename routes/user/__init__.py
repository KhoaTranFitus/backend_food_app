from flask import Blueprint

# 1. Tạo Blueprint
user_bp = Blueprint('user', __name__)

# 2. Import các file route con
# (File login_route.py bạn đã có)
from . import login_route 
# (Chúng ta sẽ tạo 2 file này ở bước 4)
from . import register_route
from . import verify_route