# core/database.py
# --- Tải dữ liệu 1 lần duy nhất khi backend khởi động ---
import json
import os
from collections import defaultdict

# ⭐️ ĐỊNH NGHĨA BIẾN GLOBAL (Sẽ được import) ⭐️
RESTAURANTS = {} # Chứa dictionary {id: restaurant_data}
MENUS = {}
CATEGORIES = {}
USERS = {}

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

# --- Load toàn bộ dữ liệu thô (List) ---
DB_RESTAURANTS = load_data(RESTAURANTS_PATH)
DB_MENUS = load_data(MENUS_PATH)
DB_CATEGORIES = load_data(CATEGORIES_PATH)
DB_USERS = load_data(USERS_PATH)

# --- TẠO INDEX ĐỂ TỐI ƯU TÌM KIẾM ---

# 1. Tạo index tra cứu nhà hàng (key: "id", value: {restaurant_data})
# ⭐️ GÁN VÀO BIẾN GLOBAL ĐÚNG TÊN ĐỂ KHẮC PHỤC ImportError ⭐️
RESTAURANTS = {str(r['id']): r for r in DB_RESTAURANTS}

# 2. Tạo index tra cứu menu (key: "restaurant_id", value: [list of menu items])
MENUS_BY_RESTAURANT_ID = defaultdict(list)
for item in DB_MENUS:
    res_id_str = str(item.get('restaurant_id'))
    if res_id_str:
        MENUS_BY_RESTAURANT_ID[res_id_str].append(item)

# 3. Tạo index tra cứu user (key: "id", value: {user_data})
USERS = {str(u['id']): u for u in DB_USERS}


# ⭐️ LOGGING VÀ XÁC NHẬN LOAD THÀNH CÔNG ⭐️
print(f"✔️ Đã tạo index tra cứu cho {len(RESTAURANTS)} nhà hàng.")
print(f"✔️ Đã nhóm menu cho {len(MENUS_BY_RESTAURANT_ID)} nhà hàng.")
print(f"✔️ Đã tạo index tra cứu cho {len(USERS)} người dùng.")
print("🎯 Tất cả dữ liệu đã được load thành công!")