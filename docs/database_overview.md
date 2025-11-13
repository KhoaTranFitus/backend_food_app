# 🗂️ Database Overview — Food App

## 🎯 Mục tiêu
Tài liệu này giúp nhóm Database và Backend hiểu rõ:
- Cấu trúc dữ liệu (schema) của các file JSON.  
- Quan hệ giữa các bảng (entity).  
- Quy ước nhập liệu để tránh lỗi.  

---

## 🧩 Cấu trúc dữ liệu (Entities)

### 🍴 Restaurant
> Danh sách nhà hàng hiển thị trên bản đồ / trang chính.

| Trường | Kiểu dữ liệu | Ghi chú |
|--------|---------------|---------|
| `id` | int | Mã định danh duy nhất |
| `name` | string | Tên nhà hàng |
| `category_id` | int | Liên kết tới `Category.id` |
| `rating` | float | Điểm đánh giá trung bình |
| `price_level` | int | 1 = rẻ, 2 = trung bình, 3 = cao |
| `address` | string | Địa chỉ đầy đủ |
| `lat`, `lon` | float | Tọa độ bản đồ |
| `phone_number` | string | Số điện thoại |
| `open_hours` | string | Giờ mở cửa |
| `main_image_url` | string | Ảnh đại diện |
| `tags` | list<string> | Từ khóa tìm kiếm (VD: “pho”, “chay”) |

---

### 🍜 MenuItem
> Danh sách món ăn của từng nhà hàng.

| Trường | Kiểu dữ liệu | Ghi chú |
|--------|---------------|---------|
| `id` | int | ID món ăn |
| `restaurant_id` | int | Liên kết với `Restaurant.id` |
| `dish_name` | string | Tên món ăn |
| `price` | int | Giá tiền (VNĐ) |
| `description` | string | Mô tả ngắn |
| `dish_tags` | list<string> | Các từ khóa tìm kiếm |
| `image_url` | string (optional) | Ảnh món ăn |

---

### 🥗 Category
> Phân loại món ăn, hiển thị bằng màu và icon.

| Trường | Kiểu dữ liệu | Ghi chú |
|--------|---------------|---------|
| `id` | int | Mã loại duy nhất |
| `name` | string | Tên loại món ăn |
| `color` | string | Mã màu hex (VD: `#FF6347`) |
| `icon` | string | Emoji hoặc icon URL |

---

### 👤 User
> Thông tin người dùng (hiện chỉ lưu local, chưa kết nối Firebase).

| Trường | Kiểu dữ liệu | Ghi chú |
|--------|---------------|---------|
| `id` | string | UID hoặc UUID người dùng |
| `name` | string | Tên người dùng |
| `email` | string | Email đăng nhập |
| `favorites` | list<int> | Danh sách `restaurant_id` yêu thích |
| `history` | list<object> | Lịch sử tìm kiếm |
| `location` | object | `{ "lat":..., "lon":... }` |

---

## 🔗 Mối quan hệ giữa các bảng (ERD)


---

## 🧾 Quy ước nhập dữ liệu

1. **Tất cả key viết dạng snake_case**  
   👉 Ví dụ: `main_image_url`, `open_hours`

2. **Giá tiền và cấp độ giá**  
   - `price`: ghi số, không ghi đơn vị (VD: `50000`)  
   - `price_level`: 1 = rẻ, 2 = trung bình, 3 = cao

3. **Định dạng JSON chuẩn UTF-8**  
   Mỗi file trong `/data/` phải có:
   - Dấu `[` mở đầu và `]` kết thúc.  
   - Không có dấu phẩy dư ở cuối.  
   - Dấu ngoặc kép `" "` cho tất cả key và value dạng text.

4. **File dữ liệu chính** nằm trong thư mục `/data/`:
    restaurants.json
    menus.json
    categories.json
    users.json

    ## ✅ Kiểm tra dữ liệu
Ngày kiểm tra: 2025-11-07  
Kết quả: ✅ Dữ liệu hợp lệ 100% (kiểm tra bằng `python scripts/validate_data.py`)
