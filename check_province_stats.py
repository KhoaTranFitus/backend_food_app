# scripts/check_province_stats.py
import json

with open('data/restaurants.json', 'r', encoding='utf-8') as f:
    restaurants = json.load(f)

# Province tags list
province_tags_list = [
    "TP. Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Lâm Đồng", "Khánh Hòa",
    "Bà Rịa - Vũng Tàu", "Quảng Nam", "Thừa Thiên Huế", "Cần Thơ",
    "Kiên Giang", "Bình Định", "Quảng Ninh", "Bình Thuận", "Đắk Lắk",
    "Lào Cai", "Hải Phòng", "Ninh Bình", "Bình Dương", "Long An", "Tây Ninh"
]

# Count province tags
province_count = {}
no_province_list = []

for r in restaurants:
    tags = r.get('tags', [])
    has_province = False
    
    for tag in tags:
        if tag in province_tags_list:
            province_count[tag] = province_count.get(tag, 0) + 1
            has_province = True
            break
    
    if not has_province:
        no_province_list.append({
            'name': r['name'],
            'address': r.get('address', ''),
            'tags': tags
        })

print(f"Tong so nha hang: {len(restaurants)}")
print(f"So nha hang KHONG co province tag: {len(no_province_list)}")

# Count by category
category_count = {}
category_names = {
    1: "Category 1 (Dry)",
    2: "Category 2 (Soup)",
    3: "Category 3 (Vegetarian)",
    4: "Category 4 (Salty)",
    5: "Category 5 (Seafood)"
}

for r in restaurants:
    cat_id = r.get('category_id', 1)
    category_count[cat_id] = category_count.get(cat_id, 0) + 1

print(f"\nThong ke theo danh muc:")
for cat_id in sorted(category_count.keys()):
    cat_name = category_names.get(cat_id, f"Category {cat_id}")
    count = category_count[cat_id]
    percentage = (count / len(restaurants)) * 100
    print(f"  - {cat_name}: {count} ({percentage:.1f}%)")

print(f"\nThong ke theo tinh thanh:")
for province, count in sorted(province_count.items(), key=lambda x: x[1], reverse=True):
    print(f"  - {province}: {count}")

if no_province_list:
    print(f"\nNha hang KHONG co province tag:")
    for r in no_province_list[:10]:
        print(f"  - {r['name']}")
        print(f"    Address: {r['address']}")
