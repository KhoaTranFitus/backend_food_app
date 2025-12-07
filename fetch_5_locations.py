# scripts/fetch_5_locations.py
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
    # Use Places API (New) - Text Search endpoint
    url = "https://places.googleapis.com/v1/places:searchNearby"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.priceLevel,places.types,places.currentOpeningHours,places.internationalPhoneNumber,places.photos"
    }
    
    # Gọi nhiều lần với các loại địa điểm khác nhau để lấy đầy đủ
    included_types_list = [
        ["restaurant"],
        ["cafe", "coffee_shop"],
        ["bar"],
        ["bakery", "meal_takeaway"],
        ["american_restaurant", "chinese_restaurant", "japanese_restaurant"],
        ["korean_restaurant", "vietnamese_restaurant", "thai_restaurant"],
        ["seafood_restaurant", "fast_food_restaurant", "hamburger_restaurant"],
        ["pizza_restaurant", "sushi_restaurant", "ramen_restaurant"],
        ["ice_cream_shop", "sandwich_shop", "barbecue_restaurant"]
    ]
    
    all_results = []
    seen_ids = set()
    
    for included_types in included_types_list:
        body = {
            "includedTypes": included_types,
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
    
        try:
            response = requests.post(url, headers=headers, json=body)
            data = response.json()
            
            if "places" in data:
                places = data.get("places", [])
                new_count = 0
                for place in places:
                    place_id = place.get("id", "")
                    if place_id and place_id not in seen_ids:
                        all_results.append(place)
                        seen_ids.add(place_id)
                        new_count += 1
                
                if new_count > 0:
                    print(f"   +{new_count} nhà hàng từ {', '.join(included_types)}")
                
                # Handle pagination if available
                page_token = data.get("nextPageToken")
                while page_token:
                    time.sleep(1)
                    
                    body["pageToken"] = page_token
                    response = requests.post(url, headers=headers, json=body)
                    data = response.json()
                    
                    if "places" in data:
                        places = data.get("places", [])
                        new_count = 0
                        for place in places:
                            place_id = place.get("id", "")
                            if place_id and place_id not in seen_ids:
                                all_results.append(place)
                                seen_ids.add(place_id)
                                new_count += 1
                        if new_count > 0:
                            print(f"   +{new_count} more")
                        page_token = data.get("nextPageToken")
                    else:
                        break
        
        except Exception as e:
            print(f"   ⚠️ {', '.join(included_types)}: {str(e)}")
        
        # Delay giữa các loại
        time.sleep(0.5)
    
    print(f"✅ Tổng: {len(all_results)} nhà hàng unique")
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
    
    # Extract tags từ types của Google Places
    tags = []
    
    # 1. Thêm tags từ types (loại hình nhà hàng)
    type_to_tag = {
        "restaurant": "Nhà Hàng",
        "bar": "Quán Bar",
        "cafe": "Quán Cafe",
        "bakery": "Tiệm Bánh",
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
        "fast_food_restaurant": "Fast Food",
        "hamburger_restaurant": "Burger",
        "pizza_restaurant": "Pizza",
        "sushi_restaurant": "Sushi",
        "ramen_restaurant": "Ramen",
        "sandwich_shop": "Bánh Mì",
        "ice_cream_shop": "Kem",
        "coffee_shop": "Cà Phê",
        "buffet_restaurant": "Buffet",
        "barbecue_restaurant": "BBQ"
    }
    
    for place_type in types:
        if place_type in type_to_tag:
            tag = type_to_tag[place_type]
            if tag not in tags:
                tags.append(tag)
    
    # 2. Thêm tag province
    address = place.get("formattedAddress", "")
    if "Hồ Chí Minh" in address or "Ho Chi Minh" in address or "Saigon" in address:
        tags.append("TP. Hồ Chí Minh")
    elif "Hà Nội" in address or "Hanoi" in address:
        tags.append("Hà Nội")
    elif "Đà Nẵng" in address or "Da Nang" in address:
        tags.append("Đà Nẵng")
    elif "Đà Lạt" in address or "Da Lat" in address:
        tags.append("Đà Lạt")
    elif "Nha Trang" in address:
        tags.append("Nha Trang")
    elif "Vũng Tàu" in address:
        tags.append("Vũng Tàu")
    elif "Hội An" in address:
        tags.append("Hội An")
    elif "Huế" in address or "Hue" in address:
        tags.append("Huế")
    elif "Cần Thơ" in address or "Can Tho" in address:
        tags.append("Cần Thơ")
    
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
        "ice cream": "Tráng Miệng",
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
        "sushi": "Sushi",
        "pizza": "Pizza",
        "burger": "Fast Food",
        "mcdonald": "Fast Food",
        "kfc": "Fast Food",
        "coffee": "Cà Phê",
        "cafe": "Cà Phê"
    }
    
    for keyword, tag in keyword_tags.items():
        if keyword in name_lower and tag not in tags:
            tags.append(tag)
    
    # 4. Thêm tag giá dựa trên price_level
    if price_level_str in ["PRICE_LEVEL_FREE", "PRICE_LEVEL_INEXPENSIVE"]:
        tags.append("Giá Rẻ")
    elif price_level_str in ["PRICE_LEVEL_EXPENSIVE", "PRICE_LEVEL_VERY_EXPENSIVE"]:
        tags.append("Sang Trọng")
    
    # 5. Thêm tag "Đặc sản" nếu có từ khóa đặc biệt
    specialty_keywords = ["đặc sản", "specialty", "traditional", "truyền thống"]
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
        "id": place.get("id", "").replace("places/", ""),
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
    # 5 địa điểm được yêu cầu - Tăng bán kính để lấy nhiều hơn
    locations = [
        {"name": "Quanh trường HCMUS", "lat": 10.762726, "lon": 106.682534, "radius": 5000},
        {"name": "Quanh chợ Bến Thành", "lat": 10.772431, "lon": 106.698111, "radius": 3000},
        {"name": "Quanh Lăng Chủ Tịch (Hà Nội)", "lat": 21.036810, "lon": 105.834709, "radius": 5000},
        {"name": "Quanh Cầu Rồng (Đà Nẵng)", "lat": 16.061005, "lon": 108.227764, "radius": 4000},
        {"name": "Quanh BigC (Đà Lạt)", "lat": 11.940419, "lon": 108.438262, "radius": 4000},
    ]
    
    all_restaurants = []
    output_file = "data/restaurants.json"
    
    print(f"🚀 Bắt đầu fetch nhà hàng từ 5 địa điểm...\n")
    
    for i, loc in enumerate(locations, 1):
        print(f"\n{'='*60}")
        print(f"📍 Địa điểm {i}/{len(locations)}: {loc['name']}")
        print(f"   Tọa độ: ({loc['lat']}, {loc['lon']})")
        print(f"   Bán kính: {loc['radius']}m")
        print(f"{'='*60}")
        
        places = fetch_nearby_restaurants(loc['lat'], loc['lon'], radius=loc['radius'])
        
        for place in places:
            restaurant = convert_to_restaurant_format(place)
            all_restaurants.append(restaurant)
        
        print(f"✅ Đã lấy {len(places)} nhà hàng từ {loc['name']}")
        print(f"   📊 Tổng tích lũy: {len(all_restaurants)} nhà hàng\n")
        
        # Delay giữa các địa điểm để tránh rate limit
        if i < len(locations):
            print("⏳ Chờ 3 giây trước khi chuyển địa điểm...\n")
            time.sleep(3)
    
    # Load existing restaurants
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_restaurants = json.load(f)
        print(f"\n📖 Đã load {len(existing_restaurants)} nhà hàng hiện có")
    except FileNotFoundError:
        existing_restaurants = []
        print(f"\n📖 Không có file cũ, sẽ tạo mới")
    
    # Remove duplicates và merge với dữ liệu cũ
    existing_ids = {r['id'] for r in existing_restaurants}
    new_count = 0
    
    for r in all_restaurants:
        if r['id'] not in existing_ids:
            existing_restaurants.append(r)
            existing_ids.add(r['id'])
            new_count += 1
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(existing_restaurants, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ HOÀN THÀNH!")
    print(f"{'='*60}")
    print(f"📊 Tổng fetch: {len(all_restaurants)} nhà hàng")
    print(f"✨ Thêm mới: {new_count} nhà hàng")
    print(f"⏭️  Bỏ qua (trùng): {len(all_restaurants) - new_count} nhà hàng")
    print(f"💾 Tổng cộng: {len(existing_restaurants)} nhà hàng trong database")
    print(f"📁 File: {output_file}")
    
    # Print statistics
    print("\n📈 Thống kê theo danh mục:")
    categories = {}
    for r in existing_restaurants:
        cat_id = r['category_id']
        categories[cat_id] = categories.get(cat_id, 0) + 1
    
    print(f"  - Category 1 (Dry): {categories.get(1, 0)}")
    print(f"  - Category 2 (Soup): {categories.get(2, 0)}")
    print(f"  - Category 3 (Vegetarian): {categories.get(3, 0)}")
    print(f"  - Category 4 (Salty): {categories.get(4, 0)}")
    print(f"  - Category 5 (Seafood): {categories.get(5, 0)}")
