from flask import Blueprint

# 1. Tạo Blueprint
user_bp = Blueprint('user', __name__)

# 2. Import các file route con
# (File login_route.py bạn đã có)
from . import login_route 
# (Chúng ta sẽ tạo 2 file này ở bước 4)
from . import register_route
from . import verify_route
from . import favorite_add_route
from . import favorite_view_route
from . import google_login_route

from . import profile_route

from . import forgot_password_route
from . import change_password_route
from . import update_profile_route
from . import update_password_route
from . import update_email_route

