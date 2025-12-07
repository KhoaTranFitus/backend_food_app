# scripts/clean_non_restaurants.py
import json

def is_non_restaurant(name, address):
    """
    Kiểm tra xem có phải là không phải nhà hàng không
    
    Args:
        name: Tên địa điểm
        address: Địa chỉ
    
    Returns:
        True nếu là khu du lịch, sinh thái, chùa, đền, công viên, etc.
    """
    name_lower = name.lower()
    address_lower = address.lower()
    
    # Blacklist keywords - các từ khóa không phải nhà hàng
    blacklist_keywords = [
        # Khu du lịch / Tourist sites
        "khu du lịch",
        "du lịch sinh thái",
        "du lịch trải nghiệm",
        "khu sinh thái",
        "vườn sinh thái",
        "làng sinh thái",
        "sinh thái vườn",
        "tourist",
        "tourism",
        "resort sinh thái",
        
        # Vườn / Gardens
        "vườn trái cây",
        "vườn cây",
        "fruit garden",
        "ecological garden",
        
        # Tôn giáo / Religious sites
        "chùa",
        "đền",
        "miếu",
        "temple",
        "pagoda",
        "shrine",
        "thánh đường",
        "nhà thờ",
        "church",
        "cathedral",
        
        # Công viên / Parks
        "công viên",
        "park",
        "garden park",
        
        # Khác
        "bảo tàng",
        "museum",
        "di tích",
        "heritage site",
        "historic site",
        "khu bảo tồn",
        "conservation area",
        "khu vui chơi",
        "amusement",
        "theme park",
        "water park",
        "zoo",
        "vườn thú",
        "aquarium",
        "thủy cung"
    ]
    
    # Kiểm tra name
    for keyword in blacklist_keywords:
        if keyword in name_lower:
            # Ngoại lệ: Nếu có từ "nhà hàng" hoặc "quán" đi kèm thì vẫn giữ lại
            if "nhà hàng" in name_lower or "quán" in name_lower or "restaurant" in name_lower:
                # Nhưng nếu có "khu du lịch" hoặc "du lịch sinh thái" thì vẫn loại
                if "khu du lịch" in name_lower or "du lịch sinh thái" in name_lower or "vườn sinh thái" in name_lower:
                    return True
                continue
            return True
    
    return False

def clean_restaurants(input_file, output_file, backup_file=None):
    """
    Lọc bỏ các địa điểm không phải nhà hàng
    
    Args:
        input_file: File JSON đầu vào
        output_file: File JSON đầu ra (clean)
        backup_file: File backup (optional)
    """
    # Load existing restaurants
    with open(input_file, 'r', encoding='utf-8') as f:
        restaurants = json.load(f)
    
    print(f"📊 Tổng số địa điểm ban đầu: {len(restaurants)}")
    
    # Backup if needed
    if backup_file:
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(restaurants, f, ensure_ascii=False, indent=2)
        print(f"💾 Đã backup vào {backup_file}")
    
    # Filter restaurants
    clean_restaurants = []
    removed_restaurants = []
    
    for restaurant in restaurants:
        name = restaurant.get('name', '')
        address = restaurant.get('address', '')
        
        if is_non_restaurant(name, address):
            removed_restaurants.append(restaurant)
            print(f"❌ Loại bỏ: {name}")
        else:
            clean_restaurants.append(restaurant)
    
    # Save clean restaurants
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_restaurants, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ HOÀN THÀNH!")
    print(f"{'='*60}")
    print(f"📊 Tổng số địa điểm ban đầu: {len(restaurants)}")
    print(f"✅ Số nhà hàng hợp lệ: {len(clean_restaurants)}")
    print(f"❌ Số địa điểm bị loại: {len(removed_restaurants)}")
    print(f"💾 Đã lưu vào {output_file}")
    
    # Show removed restaurants
    if removed_restaurants:
        print(f"\n📋 Danh sách các địa điểm bị loại:")
        for r in removed_restaurants:
            print(f"  - {r['name']} ({r.get('address', 'N/A')})")
    
    return clean_restaurants, removed_restaurants

if __name__ == "__main__":
    input_file = "data/restaurants.json"
    output_file = "data/restaurants.json"
    backup_file = "data/restaurants_backup_before_clean.json"
    
    clean_restaurants, removed = clean_restaurants(input_file, output_file, backup_file)
    
    # Statistics
    print(f"\n📈 Thống kê theo danh mục (sau khi clean):")
    categories = {}
    for r in clean_restaurants:
        cat_id = r['category_id']
        categories[cat_id] = categories.get(cat_id, 0) + 1
    
    print(f"  - Category 1 (Dry): {categories.get(1, 0)}")
    print(f"  - Category 2 (Soup): {categories.get(2, 0)}")
    print(f"  - Category 3 (Vegetarian): {categories.get(3, 0)}")
    print(f"  - Category 4 (Salty): {categories.get(4, 0)}")
    print(f"  - Category 5 (Seafood): {categories.get(5, 0)}")
