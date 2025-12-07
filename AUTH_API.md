# 🔐 Authentication API Documentation

## Base URL
```
http://localhost:5000/api
```

---

## 📋 Auth Endpoints

### 1. **Register** (Đăng ký tài khoản)
Tạo tài khoản mới với email và mật khẩu

**Endpoint:** `POST /register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "name": "Nguyễn Văn A"
}
```

**Request Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ | Email hợp lệ (định dạng: user@domain.com) |
| `password` | string | ✅ | Mật khẩu ≥ 6 ký tự |
| `name` | string | ✅ | Tên đầy đủ của người dùng |

**Response (Success - 200):**
```json
{
  "message": "Đăng ký thành công! Mã xác thực đã được gửi đến email của bạn.",
  "user": {
    "uid": "firebase_uid_12345",
    "name": "Nguyễn Văn A",
    "email": "user@example.com",
    "avatar_url": "",
    "favorites": [],
    "history": [],
    "location": {}
  }
}
```

**Response (Error - 400):**
```json
{
  "error": "Email đã tồn tại!"
}
```

**Possible Error Messages:**
| Error | Cause | Solution |
|-------|-------|----------|
| `Thiếu thông tin người dùng` | Missing email, password, hoặc name | Gửi đủ 3 fields |
| `Email không hợp lệ` | Invalid email format | Kiểm tra định dạng email |
| `Mật khẩu phải có ít nhất 6 ký tự` | Password < 6 characters | Sử dụng mật khẩu dài hơn |
| `Email đã tồn tại!` | Email được đăng ký trước đó | Sử dụng email khác hoặc login |
| `Email không tồn tại hoặc gửi mã thất bại` | Mail service error | Kiểm tra email, thử lại sau |

**Status Codes:**
- `200` - Đăng ký thành công
- `400` - Invalid request
- `500` - Server error

**Next Steps:**
1. Gửi mã xác thực được gửi đến email
2. Gọi `/verify` để xác thực email

---

### 2. **Verify Email** (Xác thực email)
Xác thực email bằng mã được gửi

**Endpoint:** `POST /verify`

**Request Body:**
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

**Request Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ | Email cần xác thực |
| `code` | string | ✅ | Mã 6 chữ số gửi qua email |

**Response (Success - 200):**
```json
{
  "message": "Xác thực email thành công!"
}
```

**Response (Error - 400):**
```json
{
  "error": "Mã xác thực không đúng."
}
```

**Possible Error Messages:**
| Error | Cause | Solution |
|-------|-------|----------|
| `Thiếu email hoặc mã xác thực` | Missing email or code | Gửi cả 2 fields |
| `Email không tồn tại` | Email chưa được register | Đăng ký tài khoản trước |
| `Mã xác thực không đúng` | Code sai hoặc hết hạn | Kiểm tra email lại, yêu cầu mã mới |

**Status Codes:**
- `200` - Xác thực thành công
- `400` - Invalid code hoặc email
- `500` - Server error

---

### 3. **Login** (Đăng nhập)
Đăng nhập bằng email và mật khẩu

**Endpoint:** `POST /login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Request Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ | Email đã đăng ký |
| `password` | string | ✅ | Mật khẩu tài khoản |

**Response (Success - 200):**
```json
{
  "message": "Đăng nhập thành công!",
  "user": {
    "uid": "firebase_uid_12345",
    "name": "Nguyễn Văn A",
    "email": "user@example.com",
    "avatar_url": "",
    "favorites": [1, 5, 23],
    "history": [{"restaurant_id": 1, "timestamp": "2025-12-03"}],
    "location": {
      "latitude": 10.8231,
      "longitude": 106.6297
    }
  },
  "idToken": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMyJ9..."
}
```

**Response (Error - 401):**
```json
{
  "error": "Sai email hoặc mật khẩu"
}
```

**Possible Error Messages:**
| Error | Cause | Solution |
|-------|-------|----------|
| `Thiếu email hoặc mật khẩu` | Missing email or password | Gửi cả 2 fields |
| `Email không tồn tại` | Email chưa được register | Đăng ký tài khoản trước |
| `Sai email hoặc mật khẩu` | Wrong credentials | Kiểm tra lại email/password |
| `Email chưa được xác thực` | Email not verified | Xác thực email trước (status 403) |

**Status Codes:**
- `200` - Đăng nhập thành công
- `400` - Missing fields
- `401` - Invalid credentials
- `403` - Email not verified
- `404` - User not found
- `500` - Server error

**Important:**
- Lưu `idToken` để dùng trong các requests tiếp theo
- `idToken` hết hạn sau ~1 giờ (cần refresh)

---

### 4. **Google Login** (Đăng nhập Google)
Đăng nhập/đăng ký bằng Google Account

**Endpoint:** `POST /google-login`

**Request Body:**
```json
{
  "idToken": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMyJ9..."
}
```

**Request Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `idToken` | string | ✅ | Google ID Token (từ Google Sign-In) |

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Đăng nhập Google thành công!",
  "user": {
    "uid": "google_uid_98765",
    "name": "Trần Thị B",
    "email": "user@gmail.com",
    "avatar_url": "https://lh3.googleusercontent.com/...",
    "favorites": [],
    "history": [],
    "location": {}
  }
}
```

**Response (Error - 401):**
```json
{
  "success": false,
  "error": "Token không hợp lệ hoặc đã hết hạn"
}
```

**Possible Error Messages:**
| Error | Cause | Solution |
|-------|-------|----------|
| `Thiếu idToken` | Missing Google token | Lấy token từ Google Sign-In |
| `Token không hợp lệ hoặc đã hết hạn` | Invalid/expired token | Yêu cầu token mới từ Google |

**Status Codes:**
- `200` - Login successful
- `400` - Missing token
- `401` - Invalid token
- `500` - Server error

**How to get idToken:**
```javascript
// Using Google Sign-In JavaScript Library
gapi.auth2.getAuthInstance().signIn().then(function() {
  const idToken = gapi.auth2.getAuthInstance().currentUser.get().getAuthResponse().idToken;
  // Send idToken to backend
});
```

---

## 💻 Code Examples

### JavaScript/Fetch

#### Register
```javascript
async function register(email, password, name) {
  try {
    const response = await fetch('http://localhost:5000/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      console.log('Register successful:', data.user);
      // Navigate to verify email page
      return data;
    } else {
      console.error('Register failed:', data.error);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
}

// Usage
register('user@example.com', 'SecurePass123', 'Nguyễn Văn A');
```

#### Verify Email
```javascript
async function verifyEmail(email, code) {
  try {
    const response = await fetch('http://localhost:5000/api/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, code })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      console.log('Email verified:', data.message);
      // Navigate to login page
      return true;
    } else {
      console.error('Verification failed:', data.error);
      return false;
    }
  } catch (error) {
    console.error('Network error:', error);
  }
}

// Usage
verifyEmail('user@example.com', '123456');
```

#### Login
```javascript
async function login(email, password) {
  try {
    const response = await fetch('http://localhost:5000/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      console.log('Login successful:', data.user);
      // Save user data and idToken to localStorage
      localStorage.setItem('user', JSON.stringify(data.user));
      localStorage.setItem('idToken', data.idToken);
      return data;
    } else {
      console.error('Login failed:', data.error);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
}

// Usage
login('user@example.com', 'SecurePass123');
```

#### Google Login
```javascript
async function googleLogin(idToken) {
  try {
    const response = await fetch('http://localhost:5000/api/google-login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idToken })
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Google login successful:', data.user);
      localStorage.setItem('user', JSON.stringify(data.user));
      return data;
    } else {
      console.error('Google login failed:', data.error);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
}
```

### Python/Requests

```python
import requests
import json

BASE_URL = "http://localhost:5000/api"

# Register
def register(email, password, name):
    response = requests.post(
        f"{BASE_URL}/register",
        json={"email": email, "password": password, "name": name}
    )
    return response.json()

# Verify
def verify_email(email, code):
    response = requests.post(
        f"{BASE_URL}/verify",
        json={"email": email, "code": code}
    )
    return response.json()

# Login
def login(email, password):
    response = requests.post(
        f"{BASE_URL}/login",
        json={"email": email, "password": password}
    )
    return response.json()

# Google Login
def google_login(id_token):
    response = requests.post(
        f"{BASE_URL}/google-login",
        json={"idToken": id_token}
    )
    return response.json()

# Usage
result = register('user@example.com', 'SecurePass123', 'Nguyễn Văn A')
print(result)
```

### cURL

```bash
# Register
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "name": "Nguyễn Văn A"
  }'

# Verify Email
curl -X POST http://localhost:5000/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "code": "123456"
  }'

# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'

# Google Login
curl -X POST http://localhost:5000/api/google-login \
  -H "Content-Type: application/json" \
  -d '{"idToken": "eyJhbGci..."}'
```

---

## 🔄 Authentication Flow

### Email/Password Flow
```
1. Register (POST /register)
   ↓
2. Verify Email (POST /verify) - user gets code via email
   ↓
3. Login (POST /login)
   ↓
4. Get idToken (save to localStorage)
```

### Google Flow
```
1. User clicks "Sign in with Google"
   ↓
2. Get idToken from Google
   ↓
3. Google Login (POST /google-login)
   ↓
4. User auto-created or logged in
```

---

## 📊 User Data Structure

```json
{
  "uid": "firebase_uid_unique",
  "name": "Nguyễn Văn A",
  "email": "user@example.com",
  "avatar_url": "https://...",
  "favorites": [1, 5, 23],
  "history": [
    {
      "restaurant_id": 1,
      "timestamp": "2025-12-03T20:28:34"
    }
  ],
  "location": {
    "latitude": 10.8231,
    "longitude": 106.6297
  }
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `uid` | string | Unique user ID (Firebase) |
| `name` | string | User's full name |
| `email` | string | User's email |
| `avatar_url` | string | Profile picture URL |
| `favorites` | array | List of favorite restaurant IDs |
| `history` | array | Recently viewed restaurants |
| `location` | object | User's last known location |

---

## 🔒 Security Best Practices

1. **Store idToken securely:**
   ```javascript
   // Use localStorage (be careful with sensitive data)
   localStorage.setItem('idToken', idToken);
   
   // Or use cookies with httpOnly flag (more secure)
   document.cookie = `idToken=${idToken}; path=/; secure; samesite=strict`;
   ```

2. **Include idToken in requests:**
   ```javascript
   fetch('/api/protected-route', {
     headers: {
       'Authorization': `Bearer ${localStorage.getItem('idToken')}`
     }
   });
   ```

3. **Never expose passwords:**
   - Always use HTTPS
   - Don't log passwords
   - Don't send passwords in URLs

4. **Handle token expiration:**
   ```javascript
   // Token valid for ~1 hour
   // Implement refresh token flow for longer sessions
   ```

---

## ⚙️ Configuration

### Firebase Setup Required
```
- Firebase Project ID
- Web API Key (for REST API)
- Google OAuth 2.0 Client ID (for Google Sign-In)
```

### Environment Variables
```
OPENAI_API_KEY=sk-proj-xxx
FIREBASE_API_KEY=xxx
FIREBASE_CLIENT_ID=xxx.apps.googleusercontent.com
```

---

## ❌ Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Email đã tồn tại` | Email registered before | Use different email or login |
| `Mật khẩu phải có ít nhất 6 ký tự` | Password too short | Use password ≥ 6 characters |
| `Email không hợp lệ` | Invalid email format | Use format: user@domain.com |
| `Email chưa được xác thực` | Need to verify first | Check email for verification code |
| `Sai email hoặc mật khẩu` | Wrong credentials | Double-check email and password |
| `Token không hợp lệ` | Google token expired | Get new token from Google |

---

## 📞 Support

**Issues?**
1. Check error message in response
2. Verify all required fields are sent
3. Check Firebase configuration
4. Review logs on backend

---

**Last Updated:** 2025-12-03
**API Version:** 1.0
**Status:** Production Ready ✅
