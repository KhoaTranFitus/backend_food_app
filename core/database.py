# core/database.py
# --- Tải dữ liệu 1 lần duy nhất khi backend khởi động ---
import json
import os

def load_data(filename):
    """Hàm đọc file JSON và xử lý lỗi cơ bản."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f" ĐÃ TẢI {os.path.basename(filename)} ({len(data)}) phần tử.")
            return data
    except FileNotFoundError:
        print(f" LỖI: Không tìm thấy file {filename}")
        return []
    except json.JSONDecodeError as e:
        print(f" LỖI: File {filename} không phải JSON hợp lệ. {e}")
        return []
    except Exception as e:
        print(f" LỖI KHÁC khi đọc {filename}: {e}")
        return []

# --- Đường dẫn tới thư mục data ---
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# --- Đường dẫn từng file dữ liệu ---
RESTAURANTS_PATH = os.path.join(DATA_DIR, 'restaurants.json')
MENUS_PATH = os.path.join(DATA_DIR, 'menus.json')
CATEGORIES_PATH = os.path.join(DATA_DIR, 'categories.json')
USERS_PATH = os.path.join(DATA_DIR, 'users.json')

# --- Load toàn bộ dữ liệu ---
DB_RESTAURANTS = load_data(RESTAURANTS_PATH)
DB_MENUS = load_data(MENUS_PATH)
DB_CATEGORIES = load_data(CATEGORIES_PATH)
DB_USERS = load_data(USERS_PATH)

print("🎯 Tất cả dữ liệu đã được load thành công!")
