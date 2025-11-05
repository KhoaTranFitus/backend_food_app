import firebase_admin
from firebase_admin import credentials, db, auth
import smtplib
from email.mime.text import MIMEText
import random
import os
from dotenv import load_dotenv

# 1. Tải các biến môi trường
load_dotenv()
API_KEY = os.environ.get('GOOGLE_API_KEY')
DB_URL = os.environ.get('FIREBASE_DB_URL')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_APP_PASSWORD = os.environ.get('SENDER_APP_PASSWORD')

# 2. Xử lý đường dẫn file .json MỘT CÁCH CHÍNH XÁC
# Lấy đường dẫn thư mục hiện tại (core)
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
# Đi lùi 1 cấp để ra thư mục gốc (backend_food_app)
BASE_DIR = os.path.dirname(CORE_DIR)
# Trỏ đường dẫn đúng tới file key
KEY_PATH = os.path.join(BASE_DIR, "food-app-d0127-firebase-adminsdk-fbsvc-fb06070e09.json")

# 3. Khởi tạo Firebase
try:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DB_URL
    })
    print("✔️ KHỞI TẠO FIREBASE THÀNH CÔNG!")
except FileNotFoundError:
    print(f"❌ LỖI: Không tìm thấy file key Firebase tại: {KEY_PATH}")
except Exception as e:
    print(f"❌ LỖI KHỞI TẠO FIREBASE: {e}")


# 4. Hàm gửi email
def send_verification_email(to_email, code):
    # ... (code gửi email của bạn) ...
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            # ... (code send_message) ...
            print(f"Đã gửi email xác thực tới {to_email}")
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")