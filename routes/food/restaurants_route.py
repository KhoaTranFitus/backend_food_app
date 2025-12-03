from flask import Blueprint, jsonify
from core.database import DB_RESTAURANTS

restaurants_bp = Blueprint("restaurants_bp", __name__)

@restaurants_bp.route("/restaurants", methods=["GET"])
def get_restaurants():
    return jsonify(DB_RESTAURANTS)  
