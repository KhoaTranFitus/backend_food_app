# API Search với Filters - Tài liệu sử dụng

## Endpoint

```
POST /api/search
```

## Mô tả

API tìm kiếm và lọc nhà hàng tích hợp đầy đủ, hỗ trợ:
- **Tìm kiếm theo từ khóa** (tên nhà hàng, món ăn, tags)
- **Lọc theo địa lý** (tỉnh/thành, tọa độ, bán kính)
- **Lọc theo thuộc tính** (category, giá, rating, tags)
- **Sắp xếp thông minh** (điểm liên quan + khoảng cách)

## Request Body (tất cả optional)

```json
{
  "query": "phở",              // Từ khóa tìm kiếm (tên, món, tags)
  "province": "Hà Nội",        // Tỉnh/thành phố (hỗ trợ tiếng Việt + English)
  "lat": 21.0285,              // Vĩ độ người dùng
  "lon": 105.8542,             // Kinh độ người dùng
  "radius": 5,                 // Bán kính tìm kiếm (km)
  "categories": [1, 2, 5],     // Lọc theo category IDs
  "min_price": 50000,          // Giá tối thiểu (VND)
  "max_price": 150000,         // Giá tối đa (VND)
  "min_rating": 4.0,           // Rating tối thiểu
  "max_rating": 5.0,           // Rating tối đa
  "tags": ["Hải Sản", "BBQ"]   // Lọc theo tags
}
```

## Response

```json
{
  "success": true,
  "total": 112,
  "results": [
    {
      "id": "ChIJ...",
      "name": "Phở Cuốn Chinh Thắng",
      "category_id": 2,
      "rating": 4.5,
      "price_range": "50,000đ-150,000đ",
      "address": "123 Nguyễn Du, Hai Bà Trưng, Hà Nội",
      "lat": 21.0285,
      "lon": 105.8542,
      "phone_number": "+84 123 456 789",
      "open_hours": "08:00-22:00",
      "image_url": "URL:",
      "tags": ["Phở/Bún", "Món Việt", "Hà Nội"],
      "score": 25.0,           // Điểm liên quan (càng cao càng match)
      "distance": 0.5          // Khoảng cách (km) - chỉ có khi gửi lat/lon
    }
  ]
}
```

## Categories

| ID | Tên | Mô tả |
|----|-----|-------|
| 1 | Dry | Đồ khô (cơm, mì xào, v.v.) |
| 2 | Soup | Đồ nước (phở, bún, v.v.) |
| 3 | Vegetarian | Chay |
| 4 | Salty | Mặn (thịt nướng, v.v.) |
| 5 | Seafood | Hải sản |

## Ví dụ sử dụng

### 1. Tìm kiếm đơn giản

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "phở"}'
```

### 2. Tìm kiếm theo tỉnh

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "seafood",
    "province": "TP.HCM"
  }'
```

### 3. Tìm kiếm gần vị trí hiện tại

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "burger",
    "lat": 10.772431,
    "lon": 106.698111,
    "radius": 3
  }'
```

### 4. Lọc theo giá và rating

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "province": "Hà Nội",
    "max_price": 100000,
    "min_rating": 4.5
  }'
```

### 5. Lọc theo category và tags

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "categories": [1, 5],
    "tags": ["BBQ", "Hải Sản"],
    "min_rating": 4.0
  }'
```

### 6. Kết hợp tất cả (Full Search + Filter)

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "lẩu",
    "province": "TP. Hồ Chí Minh",
    "lat": 10.7769,
    "lon": 106.7009,
    "radius": 5,
    "categories": [1, 4, 5],
    "min_price": 50000,
    "max_price": 200000,
    "min_rating": 4.0,
    "tags": ["BBQ"]
  }'
```

## Translation Support

API tự động dịch query từ tiếng Anh sang tiếng Việt:

| English | Vietnamese |
|---------|------------|
| seafood | Hải Sản |
| hotpot | Lẩu |
| bbq | BBQ |
| vegetarian | Chay |
| coffee | Cà Phê |
| noodles, pho | Phở/Bún |
| rice | Cơm |
| burger | Burger |
| pizza | Pizza |
| sushi | Sushi |

### Province Translation

| Input | Translated |
|-------|------------|
| saigon, ho chi minh, tp.hcm | TP. Hồ Chí Minh |
| hanoi, ha noi | Hà Nội |
| da nang, danang | Đà Nẵng |
| nha trang | Khánh Hòa |
| da lat, dalat | Lâm Đồng |
| vung tau | Bà Rịa - Vũng Tàu |
| hoi an | Quảng Nam |
| hue | Thừa Thiên Huế |

## Scoring Algorithm

Kết quả được sắp xếp theo **score** (giảm dần), sau đó **distance** (tăng dần):

1. **Match tên nhà hàng**: +10 điểm
2. **Match tag**: +5 điểm
3. **Match món ăn trong menu**: +2 điểm
4. **Rating bonus**: rating × 2 (VD: 4.5⭐ = +9 điểm)

**Ví dụ:**
- Nhà hàng "Phở 24" có từ "phở" trong tên → +10 điểm
- Tag "Phở/Bún" → +5 điểm
- Rating 4.5⭐ → +9 điểm
- **Tổng: 24 điểm**

## Filter Logic

### Categories
- `null`: Không lọc (trả về tất cả)
- `[]`: Lọc nghiêm ngặt (trả về rỗng)
- `[1, 2, 5]`: Chỉ trả về category 1, 2, 5

### Price Range
- Overlap matching: Nhà hàng có khoảng giá giao với filter được giữ lại
- VD: Filter 50k-150k → Match với "50k-150k", "100k-200k", "20k-100k"

### Tags
- **OR logic**: Nhà hàng có ít nhất 1 tag trong danh sách filter
- VD: `tags: ["BBQ", "Hải Sản"]` → Match nhà hàng có BBQ HOẶC Hải Sản

### Radius
- Chỉ hoạt động khi có `lat`, `lon`, và `radius`
- Tính theo Haversine formula (km)

## Notes

### Không có query text
Nếu không gửi `query` hoặc `query: ""`:
- Trả về **tất cả nhà hàng** sau khi áp dụng filters
- Sắp xếp theo rating (cao → thấp) và distance (gần → xa)

### Response format
- `success`: Boolean - Trạng thái request
- `total`: Integer - Số lượng kết quả
- `results`: Array - Danh sách nhà hàng

### Distance field
- Chỉ xuất hiện khi gửi `lat` và `lon`
- Đơn vị: kilometer (km)
- Làm tròn 2 chữ số thập phân

## Test Suite

Chạy test để xác minh API:

```bash
python test_search_with_filters.py
```

Test cases bao gồm:
1. ✅ Search + Province + Price + Rating
2. ✅ Search + Location + Radius
3. ✅ Filter Categories + Price
4. ✅ Search + Tags + Rating
5. ✅ Pure Filter (no search)
6. ✅ Full Combo (Search + All Filters + Location)

## Performance

- **Database size**: 1458 nhà hàng
- **Response time**: ~50-200ms (tùy filters)
- **Max results**: Không giới hạn (có thể thêm `limit` parameter nếu cần)

## Migration từ API cũ

### `/api/search` (cũ)
```json
{
  "query": "phở",
  "province": "Hà Nội",
  "lat": 21.0285,
  "lon": 105.8542
}
```

### `/api/search` (mới) - 100% backward compatible
Vẫn hỗ trợ tất cả tham số cũ, chỉ cần thêm filters mới nếu muốn:

```json
{
  "query": "phở",
  "province": "Hà Nội",
  "lat": 21.0285,
  "lon": 105.8542,
  "min_rating": 4.5,        // NEW
  "max_price": 100000,      // NEW
  "categories": [2]         // NEW
}
```

### `/api/map/filter` (cũ)
**Không còn cần thiết!** Tất cả chức năng đã tích hợp vào `/api/search`.

Tuy nhiên, route `/api/map/filter` vẫn tồn tại để backward compatibility.
