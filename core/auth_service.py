from email.mime.text import MIMEText
import random
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db, auth
import smtplib

# Tải các biến môi trường
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, 'File.env')

print(f"🔍 Loading env from: {ENV_PATH}")
load_dotenv(ENV_PATH)

# Lấy biến môi trường
API_KEY = os.getenv('GOOGLE_API_KEY')
DB_URL = os.getenv('FIREBASE_DB_URL')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_APP_PASSWORD = os.getenv('SENDER_APP_PASSWORD')

# Xử lý đường dẫn file key JSON
KEY_PATH = os.path.join(BASE_DIR, "food-app-d0127-firebase-adminsdk-fbsvc-fb06070e09.json")

# Khởi tạo Firebase
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

# 5. Hàm gửi email
def send_verification_email(to_email, code):
    try:
        print(f"📨 Đang gửi mã xác thực tới {to_email}...")
        msg = MIMEText(f"Mã xác thực của bạn là: {code}")
        msg["Subject"] = "Xác thực tài khoản Food App"
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email

        print(f"SENDER_EMAIL={SENDER_EMAIL}")
        print(f"SENDER_APP_PASSWORD={'*' * len(SENDER_APP_PASSWORD) if SENDER_APP_PASSWORD else None}")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.send_message(msg)
            print(f"✅ Đã gửi email xác thực tới {to_email}")
    except Exception as e:
        print(f"❌ Lỗi khi gửi email: {e}")