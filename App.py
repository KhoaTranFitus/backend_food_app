from flask import Flask
from flask_cors import CORS

# --- IMPORT KHỞI TẠO ---
# (Import 2 file này sẽ chạy code bên trong chúng 1 lần duy nhất)
import core.auth_service  # <- Dòng này sẽ khởi tạo Firebase
import core.database      # <- Dòng này sẽ tải JSON

# --- IMPORT ROUTES ---
from routes.food import food_bp
# ⭐️ THÊM IMPORT reviews_route VÀO ĐÂY (để đăng ký route) ⭐️
from routes.food import reviews_route 
from routes.user import user_bp 
from routes.chatbot import chatbot_bp
from routes.map import map_bp

app = Flask(__name__)
CORS(app)

# ⭐️ ĐĂNG KÝ BLUEPRINT VỚI TIỀN TỐ RÕ RÀNG ⭐️
app.register_blueprint(food_bp, url_prefix='/api/food') 
app.register_blueprint(user_bp, url_prefix='/api/user')  
app.register_blueprint(chatbot_bp, url_prefix="/api/chatbot")
app.register_blueprint(map_bp, url_prefix="/api/map")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)