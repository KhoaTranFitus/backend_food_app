import requests
import json
import os
import time
import random

# --- CẤU HÌNH ---
OUTPUT_FILE = os.path.join("data", "restaurants.json")
RADIUS = 10000       # Tìm trong bán kính 10km từ trung tâm tỉnh (tăng từ 5km)

# Danh sách 63 tỉnh thành Việt Nam (tọa độ trung tâm thành phố)
CITIES = [
    # TP lớn - lấy 20 quán
    {"name": "TP. Hồ Chí Minh", "lat": 10.8231, "lon": 106.6297, "limit": 20},
    {"name": "Hà Nội", "lat": 21.0285, "lon": 105.8542, "limit": 20},
    
    # Các tỉnh thành còn lại - lấy 10 quán
    {"name": "Đà Nẵng", "lat": 16.0544, "lon": 108.2022, "limit": 10},
    {"name": "Hải Phòng", "lat": 20.8449, "lon": 106.6881, "limit": 10},
    {"name": "Cần Thơ", "lat": 10.0452, "lon": 105.7469, "limit": 10},
    {"name": "An Giang", "lat": 10.3817, "lon": 105.4350, "limit": 10},
    {"name": "Bà Rịa - Vũng Tàu", "lat": 10.5417, "lon": 107.2429, "limit": 10},
    {"name": "Bạc Liêu", "lat": 9.2940, "lon": 105.7215, "limit": 10},
    {"name": "Bắc Giang", "lat": 21.2819, "lon": 106.1975, "limit": 10},
    {"name": "Bắc Kạn", "lat": 22.1474, "lon": 105.8348, "limit": 10},
    {"name": "Bắc Ninh", "lat": 21.1861, "lon": 106.0763, "limit": 10},
    {"name": "Bến Tre", "lat": 10.2433, "lon": 106.3758, "limit": 10},
    {"name": "Bình Dương", "lat": 11.3254, "lon": 106.4770, "limit": 10},
    {"name": "Bình Định", "lat": 13.7830, "lon": 109.2196, "limit": 10},
    {"name": "Bình Phước", "lat": 11.7511, "lon": 106.7234, "limit": 10},
    {"name": "Bình Thuận", "lat": 10.9292, "lon": 108.1020, "limit": 10},
    {"name": "Cà Mau", "lat": 9.1526, "lon": 105.1960, "limit": 10},
    {"name": "Cao Bằng", "lat": 22.6666, "lon": 106.2525, "limit": 10},
    {"name": "Đắk Lắk", "lat": 12.7100, "lon": 108.2378, "limit": 10},
    {"name": "Đắk Nông", "lat": 12.2646, "lon": 107.6098, "limit": 10},
    {"name": "Điện Biên", "lat": 21.3842, "lon": 103.0158, "limit": 10},
    {"name": "Đồng Nai", "lat": 10.9467, "lon": 106.8340, "limit": 10},
    {"name": "Đồng Tháp", "lat": 10.4938, "lon": 105.6881, "limit": 10},
    {"name": "Gia Lai", "lat": 13.9833, "lon": 108.0000, "limit": 10},
    {"name": "Hà Giang", "lat": 22.8023, "lon": 104.9784, "limit": 10},
    {"name": "Hà Nam", "lat": 20.5835, "lon": 105.9230, "limit": 10},
    {"name": "Hà Tĩnh", "lat": 18.3559, "lon": 105.8877, "limit": 10},
    {"name": "Hải Dương", "lat": 20.9373, "lon": 106.3145, "limit": 10},
    {"name": "Hậu Giang", "lat": 9.7577, "lon": 105.6412, "limit": 10},
    {"name": "Hòa Bình", "lat": 20.6861, "lon": 105.3131, "limit": 10},
    {"name": "Hưng Yên", "lat": 20.6464, "lon": 106.0511, "limit": 10},
    {"name": "Khánh Hòa", "lat": 12.2388, "lon": 109.1967, "limit": 10},
    {"name": "Kiên Giang", "lat": 10.0125, "lon": 105.0808, "limit": 10},
    {"name": "Kon Tum", "lat": 14.3497, "lon": 108.0005, "limit": 10},
    {"name": "Lai Châu", "lat": 22.3864, "lon": 103.4702, "limit": 10},
    {"name": "Lâm Đồng", "lat": 11.9404, "lon": 108.4583, "limit": 10},
    {"name": "Lạng Sơn", "lat": 21.8537, "lon": 106.7619, "limit": 10},
    {"name": "Lào Cai", "lat": 22.4856, "lon": 103.9755, "limit": 10},
    {"name": "Long An", "lat": 10.6956, "lon": 106.2431, "limit": 10},
    {"name": "Nam Định", "lat": 20.4388, "lon": 106.1621, "limit": 10},
    {"name": "Nghệ An", "lat": 18.6793, "lon": 105.6811, "limit": 10},
    {"name": "Ninh Bình", "lat": 20.2506, "lon": 105.9745, "limit": 10},
    {"name": "Ninh Thuận", "lat": 11.6739, "lon": 108.8629, "limit": 10},
    {"name": "Phú Thọ", "lat": 21.4208, "lon": 105.2045, "limit": 10},
    {"name": "Phú Yên", "lat": 13.0882, "lon": 109.0929, "limit": 10},
    {"name": "Quảng Bình", "lat": 17.6102, "lon": 106.3487, "limit": 10},
    {"name": "Quảng Nam", "lat": 15.5394, "lon": 108.0194, "limit": 10},
    {"name": "Quảng Ngãi", "lat": 15.1214, "lon": 108.8044, "limit": 10},
    {"name": "Quảng Ninh", "lat": 21.0064, "lon": 107.2925, "limit": 10},
    {"name": "Quảng Trị", "lat": 16.8103, "lon": 107.1854, "limit": 10},
    {"name": "Sóc Trăng", "lat": 9.6025, "lon": 105.9738, "limit": 10},
    {"name": "Sơn La", "lat": 21.3273, "lon": 103.9143, "limit": 10},
    {"name": "Tây Ninh", "lat": 11.3351, "lon": 106.0988, "limit": 10},
    {"name": "Thái Bình", "lat": 20.4464, "lon": 106.3365, "limit": 10},
    {"name": "Thái Nguyên", "lat": 21.5671, "lon": 105.8252, "limit": 10},
    {"name": "Thanh Hóa", "lat": 19.8067, "lon": 105.7851, "limit": 10},
    {"name": "Thừa Thiên Huế", "lat": 16.4637, "lon": 107.5909, "limit": 10},
    {"name": "Tiền Giang", "lat": 10.4493, "lon": 106.3420, "limit": 10},
    {"name": "Trà Vinh", "lat": 9.8127, "lon": 106.2992, "limit": 10},
    {"name": "Tuyên Quang", "lat": 21.7767, "lon": 105.2280, "limit": 10},
    {"name": "Vĩnh Long", "lat": 10.2397, "lon": 105.9571, "limit": 10},
    {"name": "Vĩnh Phúc", "lat": 21.3609, "lon": 105.5474, "limit": 10},
    {"name": "Yên Bái", "lat": 21.7168, "lon": 104.8986, "limit": 10}
]

def fetch_restaurants_in_city(city):
    """Gọi Overpass API để lấy quán ăn tại 1 thành phố."""
    print(f"🔍 Đang quét {city['name']}...")
    
    limit = city.get('limit', 10)
    # Query nhiều hơn để sau khi lọc fast_food vẫn còn đủ
    query_limit = limit * 3
    
    # Query: Chỉ lấy nhà hàng thực sự, không lấy cafe, bakery, bar...
    overpass_query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="restaurant"](around:{RADIUS},{city['lat']},{city['lon']});
    );
    out body {query_limit}; 
    """
    # Lưu ý: Chỉ lấy amenity=restaurant, không lấy cafe/bar/pub/bakery
    
    url = "https://overpass-api.de/api/interpreter"
    try:
        response = requests.get(url, params={'data': overpass_query})
        if response.status_code == 429: # Lỗi quá nhiều request
            print("⚠️ Server bận, đang chờ 5s...")
            time.sleep(5)
            return fetch_restaurants_in_city(city) # Thử lại
            
        response.raise_for_status()
        data = response.json()
        return data.get('elements', [])
    except Exception as e:
        print(f"❌ Lỗi tại {city['name']}: {e}")
        return []

def main():
    all_restaurants = []
    
    for city in CITIES:
        elements = fetch_restaurants_in_city(city)
        
        added_count = 0
        target_limit = city.get('limit', 10)
        
        for item in elements:
            if added_count >= target_limit:
                break
                
            tags = item.get('tags', {})
            name = tags.get('name')
            if not name: continue
            
            # Bỏ qua fast food và các loại không phải nhà hàng thực sự
            amenity = tags.get('amenity', '')
            shop = tags.get('shop', '')
            
            # Chỉ giữ lại restaurant, loại bỏ tất cả các loại khác
            if amenity != 'restaurant':
                continue
            
            # Loại bỏ các quán có tên "cafe", "bakery", "coffee" trong tên
            name_lower = name.lower()
            if any(word in name_lower for word in ['cafe', 'coffee', 'bakery', 'bar', 'pub']):
                continue
            
            # Chuẩn hóa dữ liệu sang format của App
            # (Logic này giống hệt các bước trước)
            osm_id = str(item['id'])
            
            # Tạo tags giả lập cho sinh động
            app_tags = [tags.get('amenity', 'restaurant')]
            if "cuisine" in tags:
                app_tags.extend(tags["cuisine"].split(';'))
            # Thêm tag tên tỉnh/thành phố để dễ lọc!
            app_tags.append(city['name'])

            res = {
                "id": osm_id,
                "name": name,
                "category_id": random.randint(1, 4),
                "rating": round(random.uniform(3.8, 5.0), 1),
                "price_level": random.randint(1, 3),
                "address": f"{tags.get('addr:housenumber', '')} {tags.get('addr:street', 'Đường phố')}, {city['name']}".strip(),
                "lat": item['lat'],
                "lon": item['lon'],
                "phone_number": tags.get('phone', ''),
                "open_hours": tags.get('opening_hours', '08:00 - 22:00'),
                "main_image_url": "",
                "tags": app_tags
            }
            all_restaurants.append(res)
            added_count += 1
        
        # Nghỉ 1 chút để không bị ban IP
        time.sleep(1)

    # Loại bỏ trùng lặp (nếu các vùng quét giao nhau)
    unique_restaurants = {r['id']: r for r in all_restaurants}.values()
    
    # Lưu file
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(unique_restaurants), f, indent=2, ensure_ascii=False)
        
    print(f"🎉 Xong! Đã thu thập {len(unique_restaurants)} quán ăn trải dài khắp Việt Nam.")

if __name__ == "__main__":
    main()