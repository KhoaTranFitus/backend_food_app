from flask import Blueprint

chatbot_bp = Blueprint('chatbot', __name__)

# Import agent routes (unified chatbot)
from . import agent

# Import route planner for favorites-based route planning
from . import route_planner




