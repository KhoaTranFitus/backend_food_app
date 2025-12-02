# scripts/fetch_google_places.py
import requests
import json
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('File.env')
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')

def fetch_nearby_restaurants(lat, lon, radius=5000, keyword="restaurant"):
    """
    Fetch restaurants from Google Places API (New)
    
    Args:
        lat: Latitude
        lon: Longitude
        radius: Search radius in meters (default 5000m = 5km)
        keyword: Search keyword (default "restaurant")
    
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
            print(f"Full response: {json.dumps(data, indent=2)}")
    
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    return all_results

def get_place_details(place_id):
    """
    Get detailed information about a place
    
    Args:
        place_id: Google Place ID
    
    Returns:
        Detailed place information
    """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,formatted_phone_number,opening_hours,website,price_level,rating,user_ratings_total,photos,types",
        "key": GOOGLE_PLACES_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("status") == "OK":
            return data.get("result", {})
    except Exception as e:
        print(f"❌ Error fetching details for {place_id}: {str(e)}")
    
    return {}

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
    # New API: PRICE_LEVEL_UNSPECIFIED, PRICE_LEVEL_FREE, PRICE_LEVEL_INEXPENSIVE, 
    #          PRICE_LEVEL_MODERATE, PRICE_LEVEL_EXPENSIVE, PRICE_LEVEL_VERY_EXPENSIVE
    price_level_str = place.get("priceLevel", "PRICE_LEVEL_MODERATE")
    price_ranges = {
        "PRICE_LEVEL_FREE": "0đ-20,000đ",
        "PRICE_LEVEL_INEXPENSIVE": "20,000đ-50,000đ",
        "PRICE_LEVEL_MODERATE": "50,000đ-150,000đ",
        "PRICE_LEVEL_EXPENSIVE": "150,000đ-300,000đ",
        "PRICE_LEVEL_VERY_EXPENSIVE": "300,000đ+",
        "PRICE_LEVEL_UNSPECIFIED": "50,000đ-150,000đ"
    }
    price_range = price_ranges.get(price_level_str, "50,000đ - 150,000đ")
    
    # Extract tags
    tags = ["restaurant"]
    address = place.get("formattedAddress", "")
    if "Hồ Chí Minh" in address or "Ho Chi Minh" in address or "Saigon" in address:
        tags.append("TP. Hồ Chí Minh")
    elif "Hà Nội" in address or "Hanoi" in address:
        tags.append("Hà Nội")
    elif "Đà Nẵng" in address or "Da Nang" in address:
        tags.append("Đà Nẵng")
    
    # Get photo URL if available
    photo_url = ""
    photos = place.get("photos", [])
    if photos and len(photos) > 0:
        photo_name = photos[0].get("name", "")
        if photo_name:
            # New API photo URL format
            photo_url = f"https://places.googleapis.com/v1/{photo_name}/media?maxWidthPx=400&key={GOOGLE_PLACES_API_KEY}"
    
    # Get opening hours
    open_hours = "08:00-22:00"  # Default
    opening_hours = place.get("currentOpeningHours", {})
    weekday_descriptions = opening_hours.get("weekdayDescriptions", [])
    if weekday_descriptions and len(weekday_descriptions) > 0:
        # Use first day's hours and remove spaces around dash
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
        "main_image_url": photo_url,
        "tags": tags
    }
    
    return restaurant

def fetch_and_save_restaurants(lat, lon, radius=5000, output_file="data/restaurants_google.json"):
    """
    Fetch restaurants and save to JSON file
    
    Args:
        lat: Latitude
        lon: Longitude
        radius: Search radius in meters
        output_file: Output JSON file path
    """
    print(f"🔍 Fetching restaurants near ({lat}, {lon}) within {radius}m radius...")
    
    places = fetch_nearby_restaurants(lat, lon, radius)
    
    print(f"\n📊 Total places found: {len(places)}")
    
    restaurants = []
    for i, place in enumerate(places, 1):
        print(f"Processing {i}/{len(places)}: {place.get('name', 'Unknown')}")
        restaurant = convert_to_restaurant_format(place)
        restaurants.append(restaurant)
    
    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Saved {len(restaurants)} restaurants to {output_file}")
    
    # Print statistics
    print("\n📈 Statistics:")
    categories = {}
    for r in restaurants:
        cat_id = r['category_id']
        categories[cat_id] = categories.get(cat_id, 0) + 1
    
    print(f"  - Category 1 (Dry): {categories.get(1, 0)}")
    print(f"  - Category 2 (Soup): {categories.get(2, 0)}")
    print(f"  - Category 3 (Vegetarian): {categories.get(3, 0)}")
    print(f"  - Category 4 (Salty): {categories.get(4, 0)}")
    print(f"  - Category 5 (Seafood): {categories.get(5, 0)}")

def merge_restaurants(existing_file, new_restaurants):
    """Merge new restaurants with existing ones, avoiding duplicates"""
    try:
        with open(existing_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    except FileNotFoundError:
        existing = []
    
    existing_ids = {r['id'] for r in existing}
    merged = existing.copy()
    
    for restaurant in new_restaurants:
        if restaurant['id'] not in existing_ids:
            merged.append(restaurant)
    
    return merged

if __name__ == "__main__":
    # Tất cả các quận/huyện của TP. Hồ Chí Minh
    locations = [
        {"name": "Quận 1", "lat": 10.762622, "lon": 106.660172},
        {"name": "Quận 2", "lat": 10.782000, "lon": 106.748000},
        {"name": "Quận 3", "lat": 10.784900, "lon": 106.687140},
        {"name": "Quận 4", "lat": 10.762000, "lon": 106.702000},
        {"name": "Quận 5", "lat": 10.754730, "lon": 106.663590},
        {"name": "Quận 6", "lat": 10.747000, "lon": 106.635000},
        {"name": "Quận 7", "lat": 10.732500, "lon": 106.717500},
        {"name": "Quận 8", "lat": 10.736000, "lon": 106.664000},
        {"name": "Quận 9", "lat": 10.843000, "lon": 106.792000},
        {"name": "Quận 10", "lat": 10.773530, "lon": 106.665320},
        {"name": "Quận 11", "lat": 10.762000, "lon": 106.645000},
        {"name": "Quận 12", "lat": 10.868000, "lon": 106.680000},
        {"name": "Bình Thạnh", "lat": 10.801373, "lon": 106.710600},
        {"name": "Tân Bình", "lat": 10.799980, "lon": 106.652430},
        {"name": "Tân Phú", "lat": 10.793000, "lon": 106.627000},
        {"name": "Phú Nhuận", "lat": 10.797870, "lon": 106.678080},
        {"name": "Bình Tân", "lat": 10.765000, "lon": 106.607000},
        {"name": "Gò Vấp", "lat": 10.837730, "lon": 106.650950},
        {"name": "Thủ Đức", "lat": 10.850000, "lon": 106.770000},
        {"name": "Bình Chánh", "lat": 10.668000, "lon": 106.537000},
        {"name": "Hóc Môn", "lat": 10.882000, "lon": 106.593000},
        {"name": "Củ Chi", "lat": 10.968000, "lon": 106.492000},
        {"name": "Nhà Bè", "lat": 10.695000, "lon": 106.733000},
        {"name": "Cần Giờ", "lat": 10.407000, "lon": 106.955000},
    ]
    
    all_restaurants = []
    output_file = "data/restaurants_google.json"
    
    print(f"🚀 Bắt đầu cào nhà hàng từ {len(locations)} khu vực...\n")
    
    for i, loc in enumerate(locations, 1):
        print(f"\n{'='*60}")
        print(f"📍 Khu vực {i}/{len(locations)}: {loc['name']}")
        print(f"{'='*60}")
        
        places = fetch_nearby_restaurants(loc['lat'], loc['lon'], radius=3000)
        
        for place in places:
            restaurant = convert_to_restaurant_format(place)
            all_restaurants.append(restaurant)
        
        print(f"✅ Đã lấy {len(places)} nhà hàng từ {loc['name']}")
        
        # Delay giữa các request để tránh rate limit
        if i < len(locations):
            print("⏳ Chờ 2 giây...")
            time.sleep(2)
    
    # Remove duplicates based on ID
    unique_restaurants = []
    seen_ids = set()
    for r in all_restaurants:
        if r['id'] not in seen_ids:
            unique_restaurants.append(r)
            seen_ids.add(r['id'])
    
    # Merge with existing data
    final_restaurants = merge_restaurants(output_file, unique_restaurants)
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_restaurants, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ HOÀN THÀNH!")
    print(f"{'='*60}")
    print(f"📊 Tổng cộng: {len(unique_restaurants)} nhà hàng mới")
    print(f"💾 Đã lưu {len(final_restaurants)} nhà hàng vào {output_file}")
    
    # Print statistics
    print("\n📈 Thống kê theo danh mục:")
    categories = {}
    for r in final_restaurants:
        cat_id = r['category_id']
        categories[cat_id] = categories.get(cat_id, 0) + 1
    
    print(f"  - Category 1 (Dry): {categories.get(1, 0)}")
    print(f"  - Category 2 (Soup): {categories.get(2, 0)}")
    print(f"  - Category 3 (Vegetarian): {categories.get(3, 0)}")
    print(f"  - Category 4 (Salty): {categories.get(4, 0)}")
    print(f"  - Category 5 (Seafood): {categories.get(5, 0)}")
