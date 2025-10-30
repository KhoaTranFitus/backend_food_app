from flask import Blueprint
from .login_route import *

user_bp = Blueprint('user', __name__)
