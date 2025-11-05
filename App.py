from flask import Flask
from flask_cors import CORS

# --- IMPORT KHỞI TẠO ---
# (Import 2 file này sẽ chạy code bên trong chúng 1 lần duy nhất)
import core.auth_service  # <- Dòng này sẽ khởi tạo Firebase
import core.database      # <- Dòng này sẽ tải JSON

# --- IMPORT ROUTES ---
from routes.food import food_bp
from routes.user import user_bp

app = Flask(__name__)
CORS(app)

# ... (các route và app.run) ...
app.register_blueprint(food_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)