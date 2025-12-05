# 🍽️ Chatbot API Documentation

## Base URL
```
http://localhost:5000/api
```

---

## 📋 Endpoints

### 1. **Chat** (Main Endpoint)
Gửi tin nhắn tới chatbot và nhận phản hồi

**Endpoint:** `POST /chatbot/chat`

**Request Body:**
```json
{
  "message": "Nhà hàng nào ở Hồ Chí Minh bán phở?",
  "conversation_id": "user-session-123"  // Optional (sẽ auto generate nếu không có)
}
```

**Hoặc sử dụng `query` thay vì `message`:**
```json
{
  "query": "Tìm nhà hàng ở Hà Nội",
  "conversation_id": "user-session-456"
}
```

**Response (Success - 200):**
```json
{
  "conversation_id": "user-session-123",
  "user_message": "Nhà hàng nào ở Hồ Chí Minh bán phở?",
  "bot_response": "Dưới đây là 3 quán ăn nổi bật ở Hồ Chí Minh:\n\n1. **Phở Việt Nam**\n   - Địa chỉ: 14 Phạm Hồng Thái, Quận 1\n   - Rating: 4.5/5\n   - Giờ mở: 7:00 AM - 9:00 PM\n...",
  "timestamp": "2025-12-03T20:28:34.123456"
}
```

**Response (Error - 400/500):**
```json
{
  "error": "Message is required"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad request (missing message or API key error)
- `500` - Server error (API key not configured, network error)
- `504` - Timeout (request took too long)

---

### 2. **Chat History** (Lấy lịch sử cuộc trao đổi)
Truy xuất lịch sử tin nhắn của một conversation

**Endpoint:** `GET /chatbot/chat/history/{conversation_id}`

**Path Parameters:**
- `conversation_id` (string): ID của cuộc trao đổi

**Response (Success - 200):**
```json
{
  "conversation_id": "user-session-123",
  "total_messages": 3,
  "history": [
    {
      "user_message": "Nhà hàng nào ở Hồ Chí Minh bán phở?",
      "bot_response": "Dưới đây là 3 quán ăn nổi bật...",
      "timestamp": "2025-12-03T20:28:34.123456"
    },
    {
      "user_message": "Giá bao nhiêu?",
      "bot_response": "Phở Việt Nam có giá...",
      "timestamp": "2025-12-03T20:29:15.654321"
    },
    {
      "user_message": "Có chỗ gì khác không?",
      "bot_response": "Có, bạn có thể thử...",
      "timestamp": "2025-12-03T20:30:01.987654"
    }
  ]
}
```

---

### 3. **Chatbot Status** (Kiểm tra trạng thái chatbot)
Kiểm tra xem chatbot có chạy bình thường không

**Endpoint:** `GET /chatbot/chat/status`

**Response (Success - 200):**
```json
{
  "status": "running",
  "api_key_configured": true,
  "total_conversations": 5,
  "total_restaurants": 341,
  "timestamp": "2025-12-03T20:28:34.123456"
}
```

---

## 🎯 Chatbot Features

### Tìm kiếm theo:
1. **Địa điểm (Location):**
   - Hồ Chí Minh / Sài Gòn / TP. Hồ Chí Minh / HCMC / TPHCM
   - Hà Nội / Hanoi
   - Đà Nẵng / Da Nang
   - Hải Phòng
   - Cần Thơ

2. **Tên món ăn (Dish):**
   - Phở, Bún bò, Cơm tấm, etc.
   - Chatbot sẽ tìm nhà hàng có menu phục vụ

3. **Tên nhà hàng (Restaurant name):**
   - Tìm kiếm chính xác hoặc gần đúng

### Thông tin trả về:
- Tên nhà hàng
- Địa chỉ chi tiết
- Số điện thoại
- Rating (sao)
- Giờ mở cửa
- Khoảng giá
- Các món ăn đề xuất (nếu tìm theo món)

---

## 💻 Code Examples

### JavaScript/Fetch
```javascript
// 1. Send message to chatbot
async function sendMessage(userMessage) {
  const response = await fetch('http://localhost:5000/api/chatbot/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: userMessage,
      conversation_id: 'user-123'
    })
  });
  
  const data = await response.json();
  console.log('Bot response:', data.bot_response);
  return data;
}

// 2. Get chat history
async function getChatHistory(conversationId) {
  const response = await fetch(
    `http://localhost:5000/api/chatbot/chat/history/${conversationId}`
  );
  const data = await response.json();
  console.log('Chat history:', data.history);
  return data;
}

// 3. Check chatbot status
async function checkStatus() {
  const response = await fetch('http://localhost:5000/api/chatbot/chat/status');
  const data = await response.json();
  console.log('Chatbot status:', data.status);
  return data;
}

// Usage
sendMessage('Tìm nhà hàng phở ở Hồ Chí Minh');
```

### Python/Requests
```python
import requests
import json

BASE_URL = "http://localhost:5000/api"

# 1. Send message
def send_message(user_message, conversation_id="user-123"):
    response = requests.post(
        f"{BASE_URL}/chatbot/chat",
        json={
            "message": user_message,
            "conversation_id": conversation_id
        }
    )
    return response.json()

# 2. Get history
def get_history(conversation_id):
    response = requests.get(
        f"{BASE_URL}/chatbot/chat/history/{conversation_id}"
    )
    return response.json()

# 3. Check status
def check_status():
    response = requests.get(f"{BASE_URL}/chatbot/chat/status")
    return response.json()

# Usage
result = send_message("Nhà hàng nào ở Hà Nội bán bún bò?")
print(result['bot_response'])
```

### cURL
```bash
# Send message
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tìm nhà hàng ở Hồ Chí Minh",
    "conversation_id": "user-123"
  }'

# Get history
curl -X GET http://localhost:5000/api/chatbot/chat/history/user-123

# Check status
curl -X GET http://localhost:5000/api/chatbot/chat/status
```

---

## ⚙️ Configuration

### Environment Variables
Tạo file `.env` ở root folder hoặc `/routes/chatbot/`:
```
OPENAI_API_KEY=sk-proj-xxx...xxx
```

### Required Python Packages
```
flask
python-dotenv
requests
```

---

## 🐛 Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Message is required` | Không gửi message | Thêm `"message"` hoặc `"query"` vào request |
| `API key không được cấu hình` | OPENAI_API_KEY không được set | Thiết lập `OPENAI_API_KEY` trong .env |
| `OpenAI API error: 429` | Rate limit exceeded | Chờ vài giây rồi thử lại |
| `Request timeout` | Request mất >30 giây | Có thể mạng chậm, thử lại |
| `500 Server Error` | Lỗi backend | Check logs xem sự cố gì |

---

## 📊 Data Structure

### Restaurant Object
```json
{
  "name": "Phở Việt Nam",
  "address": "14 Phạm Hồng Thái, Phường Bến Thành, Quận 1",
  "phone": "+84 28 3827 5743",
  "rating": 4.5,
  "price_range": "$$",
  "open_hours": "7:00 AM - 9:00 PM",
  "recommended_dishes": [
    {
      "name": "Phở bò",
      "price": "50,000 VND",
      "description": "Phở bò truyền thống"
    }
  ]
}
```

---

## 🚀 Performance Notes

- **Response time:** 2-5 giây (phụ thuộc vào OpenAI API)
- **Max conversations stored:** Unlimited (in-memory)
- **Max restaurants:** 341
- **Timeout:** 30 giây per request

---

## 📞 Support

Nếu có vấn đề:
1. Check API key configuration
2. Verify server is running: `GET /api/chatbot/chat/status`
3. Check network connection
4. Review error message in response

---

**Last Updated:** 2025-12-03
**API Version:** 1.0
**Status:** Production Ready ✅
