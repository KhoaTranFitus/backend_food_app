# core/database.py — Load dữ liệu từ Firebase thay vì JSON

from firebase_admin import db
from collections import defaultdict

print("🔥 Đang tải dữ liệu từ Firebase...")

# --- Lấy dữ liệu từ Firebase ---
restaurants_ref = db.reference("restaurants").get()
menus_ref = db.reference("menus").get()
categories_ref = db.reference("categories").get()
users_ref = db.reference("users").get()

# Convert dict → list (Firebase returns dict), filter None
def to_list(data):
    if isinstance(data, dict):
        return [v for v in data.values() if v is not None]
    if isinstance(data, list):
        return [v for v in data if v is not None]
    return []

DB_RESTAURANTS = to_list(restaurants_ref)
DB_MENUS = to_list(menus_ref)
DB_CATEGORIES = to_list(categories_ref)
DB_USERS = to_list(users_ref)

print(f"✔ Load restaurants: {len(DB_RESTAURANTS)}")
print(f"✔ Load menus: {len(DB_MENUS)}")
print(f"✔ Load categories: {len(DB_CATEGORIES)}")
print(f"✔ Load users: {len(DB_USERS)}")

# --- TẠO INDEX ---

RESTAURANTS_DICT = {str(r['id']): r for r in DB_RESTAURANTS}

MENUS_BY_RESTAURANT_ID = defaultdict(list)
for item in DB_MENUS:
    res_id = str(item.get('restaurant_id'))
    MENUS_BY_RESTAURANT_ID[res_id].append(item)

USERS_DICT = {str(u['id']): u for u in DB_USERS}

print("🎯 Dữ liệu từ Firebase đã được index thành công!")
