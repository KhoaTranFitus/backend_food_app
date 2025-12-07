from flask import Blueprint

chatbot_bp = Blueprint('chatbot', __name__)

# Import agent routes (unified chatbot)
from . import agent




