# scripts/fetch_major_cities.py
import requests
import json
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('File.env')
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')

def fetch_nearby_restaurants(lat, lon, radius=5000):
    """
    Fetch restaurants from Google Places API (New)
    
    Args:
        lat: Latitude
        lon: Longitude
        radius: Search radius in meters (default 5000m = 5km)
    
    Returns:
        List of restaurant data
    """
    url = "https://places.googleapis.com/v1/places:searchNearby"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.priceLevel,places.types,places.currentOpeningHours,places.internationalPhoneNumber,places.photos"
    }
    
    body = {
        "includedTypes": ["restaurant"],
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": lat,
                    "longitude": lon
                },
                "radius": radius
            }
        }
    }
    
    all_results = []
    
    try:
        response = requests.post(url, headers=headers, json=body)
        data = response.json()
        
        if "places" in data:
            places = data.get("places", [])
            all_results.extend(places)
            print(f"✅ Fetched {len(places)} restaurants")
            
            # Handle pagination if available
            page_token = data.get("nextPageToken")
            while page_token:
                print("⏳ Waiting for next page...")
                time.sleep(2)
                
                body["pageToken"] = page_token
                response = requests.post(url, headers=headers, json=body)
                data = response.json()
                
                if "places" in data:
                    places = data.get("places", [])
                    all_results.extend(places)
                    print(f"✅ Fetched {len(places)} more restaurants")
                    page_token = data.get("nextPageToken")
                else:
                    break
        else:
            error_msg = data.get("error", {}).get("message", "Unknown error")
            print(f"❌ Error: {error_msg}")
    
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    return all_results

def convert_to_restaurant_format(place, category_id=1):
    """
    Convert Google Places API (New) data to restaurant format
    
    Args:
        place: Google Place object from new API
        category_id: Category ID (1=dry, 2=soup, 3=vegetarian, 4=salty, 5=seafood)
    
    Returns:
        Restaurant object
    """
    # Get name
    display_name = place.get("displayName", {})
    name = display_name.get("text", "Unknown Restaurant") if isinstance(display_name, dict) else str(display_name)
    
    # Determine category based on types or name
    types = place.get("types", [])
    name_lower = name.lower()
    
    # Simple category detection
    if any(t in types for t in ["vegetarian_restaurant", "vegan_restaurant"]) or "chay" in name_lower or "vegetarian" in name_lower:
        category_id = 3  # vegetarian
    elif "seafood" in name_lower or "hải sản" in name_lower or "fish" in name_lower:
        category_id = 5  # seafood
    elif "soup" in name_lower or "phở" in name_lower or "bún" in name_lower or "noodle" in name_lower:
        category_id = 2  # soup
    elif "bbq" in name_lower or "nướng" in name_lower or "grill" in name_lower:
        category_id = 4  # salty
    else:
        category_id = 1  # dry (default)
    
    # Get location
    location = place.get("location", {})
    lat = location.get("latitude", 0)
    lon = location.get("longitude", 0)
    
    # Get rating
    rating = place.get("rating", 4.0)
    if rating == 0 or rating is None:
        rating = 4.0
    
    # Get price range based on Google's priceLevel
    price_level_str = place.get("priceLevel", "PRICE_LEVEL_MODERATE")
    price_ranges = {
        "PRICE_LEVEL_FREE": "0đ-20,000đ",
        "PRICE_LEVEL_INEXPENSIVE": "20,000đ-50,000đ",
        "PRICE_LEVEL_MODERATE": "50,000đ-150,000đ",
        "PRICE_LEVEL_EXPENSIVE": "150,000đ-300,000đ",
        "PRICE_LEVEL_VERY_EXPENSIVE": "300,000đ+",
        "PRICE_LEVEL_UNSPECIFIED": "50,000đ-150,000đ"
    }
    price_range = price_ranges.get(price_level_str, "50,000đ-150,000đ")
    
    # Extract tags
    tags = []
    
    # Address
    address = place.get("formattedAddress", "")
    
    # 1. Thêm tags từ types (loại hình nhà hàng)
    type_to_tag = {
        "restaurant": "Nhà Hàng",
        "bar": "Quán Bar",
        "cafe": "Quán Cafe",
        "bakery": "Tiệm Bánh",
        "meal_takeaway": "Mang Đi",
        "meal_delivery": "Giao Hàng",
        "chinese_restaurant": "Món Trung",
        "japanese_restaurant": "Món Nhật",
        "korean_restaurant": "Món Hàn",
        "vietnamese_restaurant": "Món Việt",
        "thai_restaurant": "Món Thái",
        "american_restaurant": "Món Mỹ",
        "italian_restaurant": "Món Ý",
        "french_restaurant": "Món Pháp",
        "indian_restaurant": "Món Ấn",
        "seafood_restaurant": "Hải Sản",
        "steakhouse": "Bít Tết",
        "fast_food_restaurant": "Đồ Ăn Nhanh",
        "hamburger_restaurant": "Burger",
        "pizza_restaurant": "Pizza",
        "sushi_restaurant": "Sushi",
        "ramen_restaurant": "Ramen",
        "barbecue_restaurant": "BBQ",
        "fine_dining_restaurant": "Cao Cấp",
        "buffet_restaurant": "Buffet"
    }
    
    for place_type in types:
        if place_type in type_to_tag:
            tag = type_to_tag[place_type]
            if tag not in tags:
                tags.append(tag)
    
    # 2. Thêm tag province
    province_map = {
        "Hồ Chí Minh": "TP. Hồ Chí Minh",
        "Ho Chi Minh": "TP. Hồ Chí Minh",
        "Saigon": "TP. Hồ Chí Minh",
        "Hà Nội": "Hà Nội",
        "Hanoi": "Hà Nội",
        "Đà Nẵng": "Đà Nẵng",
        "Da Nang": "Đà Nẵng",
        "Đà Lạt": "Lâm Đồng",
        "Da Lat": "Lâm Đồng",
        "Nha Trang": "Khánh Hòa",
        "Vũng Tàu": "Bà Rịa - Vũng Tàu",
        "Vung Tau": "Bà Rịa - Vũng Tàu",
        "Hội An": "Quảng Nam",
        "Hoi An": "Quảng Nam",
        "Huế": "Thừa Thiên Huế",
        "Hue": "Thừa Thiên Huế",
        "Cần Thơ": "Cần Thơ",
        "Can Tho": "Cần Thơ",
        "Phú Quốc": "Kiên Giang",
        "Phu Quoc": "Kiên Giang",
        "Quy Nhơn": "Bình Định",
        "Quy Nhon": "Bình Định"
    }
    
    for key, value in province_map.items():
        if key in address:
            if value not in tags:
                tags.append(value)
            break
    
    # 3. Thêm tag từ tên nhà hàng
    keyword_tags = {
        "phở": "Phở/Bún",
        "pho": "Phở/Bún",
        "bún": "Phở/Bún", 
        "cơm": "Cơm",
        "com": "Cơm",
        "rice": "Cơm",
        "bánh": "Tráng Miệng",
        "cake": "Tráng Miệng",
        "dessert": "Tráng Miệng",
        "kem": "Tráng Miệng",
        "lẩu": "Lẩu",
        "hotpot": "Lẩu",
        "nướng": "Nướng",
        "bbq": "BBQ",
        "grill": "Nướng",
        "chay": "Chay",
        "vegetarian": "Chay",
        "hải sản": "Hải Sản",
        "seafood": "Hải Sản",
        "buffet": "Buffet",
        "dimsum": "Dimsum",
        "sushi": "Sushi",
        "ramen": "Ramen",
        "pizza": "Pizza",
        "burger": "Fast Food",
        "steak": "Bít Tết",
        "coffee": "Cà Phê",
        "cafe": "Cà Phê"
    }
    
    for keyword, tag in keyword_tags.items():
        if keyword in name_lower and tag not in tags:
            tags.append(tag)
    
    # 4. Thêm tag giá
    if price_level_str in ["PRICE_LEVEL_FREE", "PRICE_LEVEL_INEXPENSIVE"]:
        tags.append("Giá Rẻ")
    elif price_level_str in ["PRICE_LEVEL_EXPENSIVE", "PRICE_LEVEL_VERY_EXPENSIVE"]:
        tags.append("Sang Trọng")
    
    # 5. Thêm tag "Đặc sản"
    specialty_keywords = ["đặc sản", "specialty", "authentic", "truyền thống", "traditional"]
    for keyword in specialty_keywords:
        if keyword in name_lower:
            tags.append("Đặc Sản")
            break
    
    # Nếu không có tag nào, thêm "Nhà Hàng" mặc định
    if not tags:
        tags.append("Nhà Hàng")
    
    # Get photo URL - chỉ lưu placeholder
    image_url = "URL:"
    
    # Get opening hours
    open_hours = "08:00-22:00"  # Default
    opening_hours = place.get("currentOpeningHours", {})
    weekday_descriptions = opening_hours.get("weekdayDescriptions", [])
    if weekday_descriptions and len(weekday_descriptions) > 0:
        hours = weekday_descriptions[0].split(": ", 1)[1] if ": " in weekday_descriptions[0] else "08:00-22:00"
        open_hours = hours.replace(" – ", "-").replace(" - ", "-").replace("–", "-")
    
    restaurant = {
        "id": place.get("id", ""),
        "name": name,
        "category_id": category_id,
        "rating": round(rating, 1),
        "price_range": price_range,
        "address": address,
        "lat": lat,
        "lon": lon,
        "phone_number": place.get("internationalPhoneNumber", ""),
        "open_hours": open_hours,
        "opening_hours_full": weekday_descriptions if weekday_descriptions else None,
        "image_url": image_url,
        "tags": tags
    }
    
    return restaurant

if __name__ == "__main__":
    # Các thành phố lớn của Việt Nam với tọa độ trung tâm và bán kính phù hợp
    cities = [
        # Hà Nội
        {"name": "Hà Nội - Hoàn Kiếm", "lat": 21.0285, "lon": 105.8542, "radius": 3000},
        {"name": "Hà Nội - Ba Đình", "lat": 21.0333, "lon": 105.8196, "radius": 3000},
        {"name": "Hà Nội - Đống Đa", "lat": 21.0171, "lon": 105.8271, "radius": 3000},
        {"name": "Hà Nội - Hai Bà Trưng", "lat": 21.0065, "lon": 105.8478, "radius": 3000},
        {"name": "Hà Nội - Cầu Giấy", "lat": 21.0333, "lon": 105.7938, "radius": 3000},
        {"name": "Hà Nội - Tây Hồ", "lat": 21.0717, "lon": 105.8250, "radius": 3000},
        {"name": "Hà Nội - Long Biên", "lat": 21.0365, "lon": 105.8955, "radius": 3000},
        {"name": "Hà Nội - Thanh Xuân", "lat": 20.9952, "lon": 105.8072, "radius": 3000},
        
        # Đà Nẵng
        {"name": "Đà Nẵng - Hải Châu", "lat": 16.0544, "lon": 108.2022, "radius": 3000},
        {"name": "Đà Nẵng - Thanh Khê", "lat": 16.0608, "lon": 108.1630, "radius": 3000},
        {"name": "Đà Nẵng - Sơn Trà", "lat": 16.0878, "lon": 108.2433, "radius": 3000},
        {"name": "Đà Nẵng - Ngũ Hành Sơn", "lat": 16.0000, "lon": 108.2500, "radius": 3000},
        {"name": "Đà Nẵng - Liên Chiểu", "lat": 16.0762, "lon": 108.1476, "radius": 3000},
        
        # Đà Lạt
        {"name": "Đà Lạt - Trung tâm", "lat": 11.9404, "lon": 108.4583, "radius": 4000},
        {"name": "Đà Lạt - Hồ Xuân Hương", "lat": 11.9380, "lon": 108.4420, "radius": 3000},
        
        # Nha Trang
        {"name": "Nha Trang - Trung tâm", "lat": 12.2388, "lon": 109.1967, "radius": 4000},
        {"name": "Nha Trang - Vĩnh Nguyên", "lat": 12.2840, "lon": 109.1947, "radius": 3000},
        {"name": "Nha Trang - Vĩnh Hòa", "lat": 12.2675, "lon": 109.1828, "radius": 3000},
        
        # Vũng Tàu
        {"name": "Vũng Tàu - Trung tâm", "lat": 10.3459, "lon": 107.0843, "radius": 4000},
        {"name": "Vũng Tàu - Bãi Sau", "lat": 10.3359, "lon": 107.0964, "radius": 3000},
        
        # Hội An
        {"name": "Hội An - Phố cổ", "lat": 15.8793, "lon": 108.3350, "radius": 3000},
        {"name": "Hội An - An Hội", "lat": 15.8838, "lon": 108.3390, "radius": 2000},
        
        # Huế
        {"name": "Huế - Trung tâm", "lat": 16.4637, "lon": 107.5909, "radius": 4000},
        {"name": "Huế - Đại Nội", "lat": 16.4670, "lon": 107.5804, "radius": 3000},
        
        # Cần Thơ
        {"name": "Cần Thơ - Ninh Kiều", "lat": 10.0341, "lon": 105.7788, "radius": 4000},
        {"name": "Cần Thơ - Cái Răng", "lat": 10.0210, "lon": 105.7706, "radius": 3000},
        
        # Phú Quốc
        {"name": "Phú Quốc - Dương Đông", "lat": 10.2221, "lon": 103.9660, "radius": 4000},
        {"name": "Phú Quốc - An Thới", "lat": 10.0344, "lon": 103.9987, "radius": 3000},
        
        # Quy Nhơn
        {"name": "Quy Nhơn - Trung tâm", "lat": 13.7667, "lon": 109.2333, "radius": 4000},
        
        # Hạ Long
        {"name": "Hạ Long - Bãi Cháy", "lat": 20.9519, "lon": 107.0542, "radius": 3000},
        
        # Phan Thiết
        {"name": "Phan Thiết - Trung tâm", "lat": 10.9280, "lon": 108.1020, "radius": 4000},
        
        # Buôn Ma Thuột
        {"name": "Buôn Ma Thuột", "lat": 12.6667, "lon": 108.0500, "radius": 4000},
        
        # Sa Pa
        {"name": "Sa Pa - Trung tâm", "lat": 22.3364, "lon": 103.8438, "radius": 3000},
        
        # Hải Phòng
        {"name": "Hải Phòng - Hồng Bàng", "lat": 20.8649, "lon": 106.6881, "radius": 3000},
        {"name": "Hải Phòng - Lê Chân", "lat": 20.8449, "lon": 106.6881, "radius": 3000},
        
        # Ninh Bình
        {"name": "Ninh Bình - Trung tâm", "lat": 20.2506, "lon": 105.9745, "radius": 3000},
        {"name": "Ninh Bình - Tràng An", "lat": 20.2445, "lon": 105.8878, "radius": 3000},
    ]
    
    all_restaurants = []
    output_file = "data/restaurants.json"
    
    print(f"🚀 Bắt đầu cào nhà hàng từ {len(cities)} khu vực trên toàn quốc...\n")
    
    # Load existing restaurants
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_restaurants = json.load(f)
            existing_ids = {r['id'] for r in existing_restaurants}
            print(f"📊 Đã có {len(existing_restaurants)} nhà hàng trong database\n")
    except FileNotFoundError:
        existing_restaurants = []
        existing_ids = set()
        print("📊 Chưa có nhà hàng nào trong database\n")
    
    for i, city in enumerate(cities, 1):
        print(f"\n{'='*60}")
        print(f"📍 Khu vực {i}/{len(cities)}: {city['name']}")
        print(f"{'='*60}")
        
        places = fetch_nearby_restaurants(city['lat'], city['lon'], radius=city['radius'])
        
        new_count = 0
        for place in places:
            place_id = place.get("id", "")
            if place_id not in existing_ids:
                restaurant = convert_to_restaurant_format(place)
                all_restaurants.append(restaurant)
                existing_ids.add(place_id)
                new_count += 1
        
        print(f"✅ Đã lấy {len(places)} nhà hàng, {new_count} nhà hàng mới từ {city['name']}")
        
        # Delay giữa các request để tránh rate limit
        if i < len(cities):
            print("⏳ Chờ 2 giây...")
            time.sleep(2)
    
    # Merge with existing restaurants
    final_restaurants = existing_restaurants + all_restaurants
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_restaurants, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ HOÀN THÀNH!")
    print(f"{'='*60}")
    print(f"📊 Đã thêm {len(all_restaurants)} nhà hàng mới")
    print(f"💾 Tổng cộng {len(final_restaurants)} nhà hàng trong {output_file}")
    
    # Print statistics
    print("\n📈 Thống kê theo danh mục (tất cả nhà hàng):")
    categories = {}
    for r in final_restaurants:
        cat_id = r['category_id']
        categories[cat_id] = categories.get(cat_id, 0) + 1
    
    print(f"  - Category 1 (Dry): {categories.get(1, 0)}")
    print(f"  - Category 2 (Soup): {categories.get(2, 0)}")
    print(f"  - Category 3 (Vegetarian): {categories.get(3, 0)}")
    print(f"  - Category 4 (Salty): {categories.get(4, 0)}")
    print(f"  - Category 5 (Seafood): {categories.get(5, 0)}")
    
    # Statistics by province
    print("\n📈 Thống kê theo tỉnh thành:")
    provinces = {}
    for r in final_restaurants:
        for tag in r.get('tags', []):
            if tag in ["TP. Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Lâm Đồng", "Khánh Hòa", 
                      "Bà Rịa - Vũng Tàu", "Quảng Nam", "Thừa Thiên Huế", "Cần Thơ", 
                      "Kiên Giang", "Bình Định"]:
                provinces[tag] = provinces.get(tag, 0) + 1
                break
    
    for province, count in sorted(provinces.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {province}: {count}")
