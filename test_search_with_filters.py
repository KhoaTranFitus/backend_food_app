# Test search API with filters integrated
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_search_with_filters():
    """Test các trường hợp search kết hợp với filters"""
    
    print("="*70)
    print("TEST 1: Tìm 'phở' ở Hà Nội, giá rẻ (<100k), rating >= 4.5")
    print("="*70)
    response = requests.post(f"{BASE_URL}/search", json={
        "query": "phở",
        "province": "Hà Nội",
        "max_price": 100000,
        "min_rating": 4.5
    })
    data = response.json()
    print(f"✅ Tìm thấy: {data.get('total', 0)} nhà hàng")
    for i, r in enumerate(data.get('results', [])[:3], 1):
        print(f"   {i}. {r['name']} - {r['rating']}⭐ - {r['price_range']}")
    
    print("\n" + "="*70)
    print("TEST 2: Tìm 'seafood' trong bán kính 5km từ vị trí (10.7769, 106.7009)")
    print("="*70)
    response = requests.post(f"{BASE_URL}/search", json={
        "query": "seafood",
        "lat": 10.7769,
        "lon": 106.7009,
        "radius": 5
    })
    data = response.json()
    print(f"✅ Tìm thấy: {data.get('total', 0)} nhà hàng")
    for i, r in enumerate(data.get('results', [])[:3], 1):
        dist = r.get('distance', 'N/A')
        print(f"   {i}. {r['name']} - {dist}km - {r['rating']}⭐")
    
    print("\n" + "="*70)
    print("TEST 3: Lọc nhà hàng category 1 (Dry) và 5 (Seafood), giá 50k-150k")
    print("="*70)
    response = requests.post(f"{BASE_URL}/search", json={
        "categories": [1, 5],
        "min_price": 50000,
        "max_price": 150000,
        "province": "TP.HCM"
    })
    data = response.json()
    print(f"✅ Tìm thấy: {data.get('total', 0)} nhà hàng")
    
    # Đếm theo category
    categories_count = {}
    for r in data.get('results', []):
        cat = r.get('category_id')
        categories_count[cat] = categories_count.get(cat, 0) + 1
    
    print(f"   - Category 1 (Dry): {categories_count.get(1, 0)}")
    print(f"   - Category 5 (Seafood): {categories_count.get(5, 0)}")
    
    print("\n" + "="*70)
    print("TEST 4: Tìm 'lẩu' có tag 'BBQ' hoặc 'Hải Sản'")
    print("="*70)
    response = requests.post(f"{BASE_URL}/search", json={
        "query": "lẩu",
        "tags": ["BBQ", "Hải Sản"],
        "min_rating": 4.0
    })
    data = response.json()
    print(f"✅ Tìm thấy: {data.get('total', 0)} nhà hàng")
    for i, r in enumerate(data.get('results', [])[:3], 1):
        tags = ', '.join(r.get('tags', [])[:3])
        print(f"   {i}. {r['name']} - {r['rating']}⭐")
        print(f"      Tags: {tags}")
    
    print("\n" + "="*70)
    print("TEST 5: Chỉ filter không search - Tất cả nhà hàng giá rẻ (<50k)")
    print("="*70)
    response = requests.post(f"{BASE_URL}/search", json={
        "max_price": 50000,
        "min_rating": 4.0
    })
    data = response.json()
    print(f"✅ Tìm thấy: {data.get('total', 0)} nhà hàng")
    for i, r in enumerate(data.get('results', [])[:5], 1):
        print(f"   {i}. {r['name']} - {r['price_range']} - {r['rating']}⭐")
    
    print("\n" + "="*70)
    print("TEST 6: Search + Filter + Location - 'burger' gần Bến Thành, rating >= 4.5")
    print("="*70)
    response = requests.post(f"{BASE_URL}/search", json={
        "query": "burger",
        "lat": 10.772431,
        "lon": 106.698111,
        "radius": 3,
        "min_rating": 4.5
    })
    data = response.json()
    print(f"✅ Tìm thấy: {data.get('total', 0)} nhà hàng")
    for i, r in enumerate(data.get('results', [])[:3], 1):
        dist = r.get('distance', 'N/A')
        print(f"   {i}. {r['name']}")
        print(f"      📍 {dist}km - {r['rating']}⭐ - {r['price_range']}")
    
    print("\n" + "="*70)
    print("✅ HOÀN THÀNH TẤT CẢ TEST!")
    print("="*70)

if __name__ == "__main__":
    print("\n🚀 Bắt đầu test Search API với Filters tích hợp...\n")
    
    try:
        test_search_with_filters()
    except requests.exceptions.ConnectionError:
        print("❌ Không thể kết nối đến Flask server!")
        print("   Vui lòng chạy: python App.py")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
