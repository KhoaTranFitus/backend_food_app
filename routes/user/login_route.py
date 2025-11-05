# API / login sẽ được đặt ở đây
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, auth, db
import smtplib
from email.mime.text import MIMEText
import random
import requests
app = Flask(__name__)
API_KEY = "AIzaSyAeY6UVkgtl7MSjuLBlMIcDSoOYLXLJSYw"
cred = credentials.Certificate("food-app-d0127-firebase-adminsdk-fbsvc-fb06070e09.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://food-app-d0127-default-rtdb.firebaseio.com/'
})
SENDER_EMAIL = "luminkhoi@gmail.com" # T dùng Gmail của t để gửi mã xác nhận cho người dùng luôn
SENDER_APP_PASSWORD = "ztimyvmgtrdfrcan"

def send_verification_email(to_email, code):
    subject = "Mã xác thực tài khoản Food App"
    body = f"Mã xác thực của bạn là: {code}"
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print("Lỗi khi gửi email:", e)
# API Đăng ký tài khoản
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email và mật khẩu không được để trống."}), 400

    try:
        user = auth.get_user_by_email(email)
        return jsonify({"error": "Email đã tồn tại!"}), 400
    except:
        pass
    user = auth.create_user(email=email, password=password, email_verified=False)

    # Tạo mã xác thực
    verification_code = str(random.randint(100000, 999999))
    db.reference("verification_codes").child(user.uid).set({
        "email": email,
        "code": verification_code
    })
    send_verification_email(email, verification_code)
    return jsonify({"message": "Đăng ký thành công! Mã xác thực đã được gửi đến email của bạn."}), 200
# API Xác minh mã OTP
@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")

    if not email or not code:
        return jsonify({"error": "Thiếu email hoặc mã xác nhận."}), 400

    try:
        user = auth.get_user_by_email(email)
    except:
        return jsonify({"error": "Email không tồn tại."}), 400

    ref = db.reference("verification_codes").child(user.uid).get()
    if not ref:
        return jsonify({"error": "Không tìm thấy mã xác nhận cho email này."}), 400

    saved_code = ref.get("code")

    if str(code) == str(saved_code):
        auth.update_user(user.uid, email_verified=True)
        db.reference("verification_codes").child(user.uid).delete()
        return jsonify({"message": "Xác thực thành công! Bạn có thể đăng nhập ngay bây giờ."}), 200
    else:
        return jsonify({"error": "Mã xác thực không chính xác."}), 400
# API Đăng nhập
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}",
        json=payload
    )
    if response.status_code == 200:
        res_data = response.json()
        return jsonify({
            "message": "Đăng nhập thành công!",
            "idToken": res_data.get("idToken"),
            "refreshToken": res_data.get("refreshToken"),
            "email": res_data.get("email")
        })
    else:
        return jsonify({
            "error": response.json().get("error", {}).get("message", "Sai email hoặc password.")
        }), 400
# Chạy app
if __name__ == "__main__":
    app.run(debug=True)
