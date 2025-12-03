from flask import Flask
from flask_cors import CORS
import os

# --- IMPORT KHỞI TẠO ---
import core.auth_service     # Firebase init
import core.database         # Load JSON

# --- IMPORT ROUTES ---
from routes.food import food_bp
from routes.user import user_bp
from routes.chatbot import chatbot_bp
from routes.map import map_bp
from routes.food.restaurants_route import restaurants_bp


# ------------------------------
# TẠO APP + HỖ TRỢ STATIC IMAGE
# ------------------------------
app = Flask(
    __name__,
    static_folder="static",            # <- Quan trọng để load ảnh
    static_url_path="/static"          # <- URL cho ảnh
)
CORS(app)


# ------------------------------
# ĐĂNG KÝ ROUTES
# ------------------------------
app.register_blueprint(food_bp, url_prefix="/api")
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(chatbot_bp, url_prefix="/api")
app.register_blueprint(map_bp, url_prefix="/api")
app.register_blueprint(restaurants_bp, url_prefix="/api")


# ------------------------------
# CHẠY SERVER (Railway yêu cầu)
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))   # <- Railway TỰ CẤP port
    app.run(host="0.0.0.0", port=port)
