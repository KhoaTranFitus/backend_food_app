import json
import firebase_admin
from firebase_admin import credentials, db

# Load Firebase credentials
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://food-app-d0127-ad2b7-default-rtdb.firebaseio.com/"
})

def import_json(node_path, json_path):
    print(f"Đang import {json_path} → {node_path} ...")
    ref = db.reference(node_path)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        key = str(item["id"])
        ref.child(key).set(item)

    print(f" Import xong {json_path}!")

# Import từng file
import_json("categories", "data/categories.json")
import_json("restaurants", "data/restaurants.json")
import_json("menus", "data/menus.json")
import_json("users", "data/users.json")

print("🎉 Tất cả dữ liệu đã import thành công!")
