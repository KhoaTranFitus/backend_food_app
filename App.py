from flask import Flask
from flask_cors import CORS

from routes.food_routes import food_bp
from routes.user_routes import user_bp

app = Flask(__name__)
CORS(app)

# home page route
@app.route('/')
def home():
    return "Welcome to the Food and User API"

# Đăng ký các nhóm route (blueprint)
app.register_blueprint(food_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)