# Tải dữ liệu 1 lần duy nhất
import json
import os

def load_data(filename):
	try:
		with open(filename, 'r', encoding='utf-8') as f:
			data = json.load(f)
			print(f"ĐÃ TẢI {filename}: {type(data)} với {len(data) if hasattr(data, '__len__') else 'unknown'} phần tử.")
			return data
	except FileNotFoundError:
		print(f"LỖI: Không tìm thấy file {filename}")
		return [] if filename.endswith('restaurants.json') else {}
	except json.JSONDecodeError as e:
		print(f"LỖI: File {filename} không phải là JSON hợp lệ. {e}")
		return [] if filename.endswith('restaurants.json') else {}
	except Exception as e:
		print(f"LỖI KHÁC khi đọc {filename}: {e}")
		return [] if filename.endswith('restaurants.json') else {}

# Đường dẫn tới thư mục data
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
RESTAURANTS_PATH = os.path.join(DATA_DIR, 'restaurants.json')
MENUS_PATH = os.path.join(DATA_DIR, 'menus.json')

DB_RESTAURANTS = load_data(RESTAURANTS_PATH)
DB_MENUS = load_data(MENUS_PATH)
