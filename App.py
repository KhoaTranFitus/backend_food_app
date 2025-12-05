from flask import Flask
from flask_cors import CORS


import core.auth_service  
import core.database     

#IMPORT ROUTES
from routes.food import food_bp
from routes.user import user_bp 
from routes.chatbot import chatbot_bp
from routes.map import map_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(food_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(chatbot_bp, url_prefix="/api")
app.register_blueprint(map_bp, url_prefix="/api")

if __name__ == '__main__':
    print("🚀 Khởi động Flask app trên port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)