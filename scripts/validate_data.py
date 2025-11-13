# scripts/validate_data.py
import json, os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def load_json(name):
    path = os.path.join(DATA_DIR, name)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load các file
restaurants = load_json('restaurants.json')
menus = load_json('menus.json')
categories = load_json('categories.json')
users = load_json('users.json')

# Danh sách ID để kiểm tra
restaurant_ids = {r["id"] for r in restaurants}
category_ids = {c["id"] for c in categories}

errors = []

# Kiểm tra liên kết giữa Restaurant và Category
for r in restaurants:
    if r["category_id"] not in category_ids:
        errors.append(f"❌ Restaurant '{r['name']}' có category_id không hợp lệ: {r['category_id']}")

# Kiểm tra liên kết giữa Menu và Restaurant
for m in menus:
    if m["restaurant_id"] not in restaurant_ids:
        errors.append(f"❌ Món '{m['dish_name']}' có restaurant_id không hợp lệ: {m['restaurant_id']}")

# Kiểm tra User favorites
for u in users:
    for fav in u.get("favorites", []):
        if fav not in restaurant_ids:
            errors.append(f"❌ User '{u['name']}' có favorite_id không hợp lệ: {fav}")

# Kết quả
if errors:
    print("⚠️ Phát hiện lỗi dữ liệu:")
    for e in errors:
        print("-", e)
else:
    print("✅ Dữ liệu hợp lệ 100%.")
