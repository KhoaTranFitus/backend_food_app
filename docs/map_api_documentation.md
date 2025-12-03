# Map API Documentation

API endpoints cho hiển thị bản đồ và markers với filtering.

## Base URL
```
http://localhost:5000/api
```

## 🎯 Logic Flow

1. **Load map** → Gọi `/api/map/filter` với lat/lon (nếu có) hoặc không (theo province)
2. **User thay đổi filter** → Gọi lại `/api/map/filter` với filters mới
3. **User nhấn marker** → Navigate với restaurant ID thật
4. **User chỉ đường** → Gọi `/api/food/direction`

## Endpoints

### 1. ⭐ Lọc markers (MAIN API)

**POST** `/map/filter`

API chính để lọc và hiển thị markers trên bản đồ. Hỗ trợ filtering theo vị trí, category, giá, rating, tags.

**Request Body:**
```json
{
  "lat": 10.762622,
  "lon": 106.660172,
  "radius": 10,
  "categories": [1, 2, 3],
  "price_levels": [1, 2],
  "min_rating": 4.0,
  "max_rating": 5.0,
  "tags": ["restaurant"],
  "limit": 100
}
```

**Parameters:**
- `lat` (float, optional): Vĩ độ vị trí hiện tại
- `lon` (float, optional): Kinh độ vị trí hiện tại
- `radius` (float, optional): Bán kính tìm kiếm (km) (default: 10)
- `categories` (array, optional): Danh sách category IDs
- `price_levels` (array, optional): Danh sách price levels (1-4)
- `min_rating` (float, optional): Rating tối thiểu (default: 0)
- `max_rating` (float, optional): Rating tối đa (default: 5)
- `tags` (array, optional): Danh sách tags
- `limit` (int, optional): Số lượng kết quả tối đa (default: 100)

**Response:**
```json
{
  "success": true,
  "total": 50,
  "filters_applied": {
    "has_location": true,
    "radius_km": 10,
    "categories": [1, 2, 3],
    "price_levels": [1, 2],
    "min_rating": 4.0,
    "max_rating": 5.0,
    "tags": ["restaurant"]
  },
  "data": [
    {
      "id": "729602712",
      "name": "Nhà Hàng BBQ Chicken",
      "lat": 10.768208,
      "lon": 106.6841501,
      "distance": 1.23,
      "rating": 4.9,
      "price_level": 1,
      "category_id": 3,
      "category_name": "BBQ & Nướng",
      "category_icon": "🍗",
      "address": "Đường phố, TP. Hồ Chí Minh",
      "phone_number": "",
      "open_hours": "08:00 - 22:00",
      "main_image_url": "",
      "tags": ["restaurant", "TP. Hồ Chí Minh"]
    }
  ]
}
```

---

### 2. Lấy danh sách tags và attributes

**GET** `/map/tags`

Trả về tất cả các tags, categories, price levels và rating ranges có sẵn.

**Response:**
```json
{
  "success": true,
  "data": {
    "tags": ["restaurant", "TP. Hồ Chí Minh", ...],
    "categories": [1, 2, 3, 4, 5, 6],
    "price_levels": [1, 2, 3, 4],
    "rating_ranges": [
      {
        "label": "4.5 - 5.0 ⭐⭐⭐⭐⭐",
        "min": 4.5,
        "max": 5.0
      }
    ]
  }
}
```

---

### 2. Lấy filter options chi tiết

**GET** `/map/filters`

Trả về danh sách các filter options kèm mô tả và icons.

**Response:**
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "id": 1,
        "name": "Món Khô",
        "icon": "🍖"
      }
    ],
    "price_levels": [
      {
        "level": 1,
        "label": "$",
        "description": "Dưới 50k"
      }
    ],
    "ratings": [
      {
        "min": 4.5,
        "max": 5.0,
        "label": "Xuất sắc (4.5+)",
        "stars": 5
      }
    ],
    "dish_types": [
      {
        "type": "dry",
        "label": "Món Khô",
        "icon": "🍖"
      }
    ]
  }
}
```

---

### 3. Lấy markers cho bản đồ với filtering

**POST** `/map/markers`

Lấy danh sách markers với các bộ lọc.

**Request Body:**
```json
{
  "categories": [1, 2, 3],
  "price_levels": [1, 2],
  "min_rating": 4.0,
  "tags": ["restaurant", "TP. Hồ Chí Minh"],
  "bounds": {
    "north": 10.8,
    "south": 10.7,
    "east": 106.75,
    "west": 106.65
  },
  "limit": 100
}
```

**Parameters:**
- `categories` (array, optional): Danh sách category IDs cần lọc
- `price_levels` (array, optional): Danh sách price levels (1-4)
- `min_rating` (float, optional): Rating tối thiểu (default: 0)
- `tags` (array, optional): Danh sách tags cần filter
- `bounds` (object, optional): Giới hạn bản đồ {north, south, east, west}
- `limit` (int, optional): Số lượng kết quả tối đa (default: 100)

**Response:**
```json
{
  "success": true,
  "total": 50,
  "data": [
    {
      "id": "729602712",
      "name": "Nhà Hàng BBQ Chicken",
      "lat": 10.768208,
      "lon": 106.6841501,
      "rating": 4.9,
      "price_level": 1,
      "category_id": 3,
      "category_name": "BBQ & Nướng",
      "category_icon": "🍗",
      "address": "Đường phố, TP. Hồ Chí Minh",
      "phone_number": "",
      "open_hours": "08:00 - 22:00",
      "main_image_url": "",
      "tags": ["restaurant", "TP. Hồ Chí Minh"]
    }
  ]
}
```

---

### 4. Lấy markers gần vị trí hiện tại

**POST** `/map/markers/nearby`

Lấy danh sách markers gần vị trí người dùng, sắp xếp theo khoảng cách.

**Request Body:**
```json
{
  "lat": 10.762622,
  "lon": 106.660172,
  "radius": 5,
  "categories": [1, 2, 3],
  "price_levels": [1, 2],
  "min_rating": 4.0,
  "limit": 50
}
```

**Parameters:**
- `lat` (float, required): Vĩ độ vị trí hiện tại
- `lon` (float, required): Kinh độ vị trí hiện tại
- `radius` (float, optional): Bán kính tìm kiếm (km) (default: 5)
- `categories` (array, optional): Danh sách category IDs
- `price_levels` (array, optional): Danh sách price levels
- `min_rating` (float, optional): Rating tối thiểu
- `limit` (int, optional): Số lượng kết quả tối đa (default: 50)

**Response:**
```json
{
  "success": true,
  "total": 25,
  "data": [
    {
      "id": "729602712",
      "name": "Nhà Hàng BBQ Chicken",
      "lat": 10.768208,
      "lon": 106.6841501,
      "distance": 1.23,
      "rating": 4.9,
      "price_level": 1,
      "category_id": 3,
      "category_name": "BBQ & Nướng",
      "category_icon": "🍗",
      "address": "Đường phố, TP. Hồ Chí Minh",
      "phone_number": "",
      "open_hours": "08:00 - 22:00",
      "main_image_url": "",
      "tags": ["restaurant", "TP. Hồ Chí Minh"]
    }
  ]
}
```

---

### 5. Lấy chi tiết một marker

**GET** `/map/markers/:marker_id`

Lấy thông tin chi tiết của một marker kèm menu.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "729602712",
    "name": "Nhà Hàng BBQ Chicken",
    "lat": 10.768208,
    "lon": 106.6841501,
    "rating": 4.9,
    "price_level": 1,
    "category_id": 3,
    "category_name": "BBQ & Nướng",
    "category_icon": "🍗",
    "address": "Đường phố, TP. Hồ Chí Minh",
    "phone_number": "",
    "open_hours": "08:00 - 22:00",
    "main_image_url": "",
    "tags": ["restaurant", "TP. Hồ Chí Minh"],
    "menu": [
      {
        "id": "menu_1",
        "restaurant_id": "729602712",
        "name": "Gà nướng",
        "price": 150000,
        "description": "Gà nướng thơm ngon"
      }
    ]
  }
}
```

---

### 6. Lấy chỉ đường

**POST** `/food/direction`

Tính toán chỉ đường từ vị trí hiện tại đến điểm đến (dùng OSRM).

**Request Body:**
```json
{
  "origin": {
    "lat": 10.762622,
    "lon": 106.660172
  },
  "destination": {
    "lat": 10.755,
    "lon": 106.671
  },
  "mode": "driving"
}
```

**Parameters:**
- `origin` (object, required): Vị trí xuất phát {lat, lon}
- `destination` (object, required): Vị trí đích {lat, lon}
- `mode` (string, optional): Phương tiện (driving, walking, bicycling) (default: driving)

**Response:**
```json
{
  "distance_meters": 5420,
  "duration_seconds": 720,
  "overview_polyline": "encoded_polyline_string",
  "legs": [{
    "steps": [...],
    "start_address": "Vị trí xuất phát",
    "end_address": "Điểm đến"
  }]
}
```

---

## Sử dụng trong Frontend

### Import service
```javascript
import { 
  filterMapMarkers,
  getFilterOptions,
  getMarkerDetail,
  getDirection
} from '../services/mapService';
```

### Lấy filter options
```javascript
const response = await getFilterOptions();
if (response.success) {
  setFilterOptions(response.data);
}
```

### Lọc và hiển thị markers
```javascript
// Với vị trí người dùng
const response = await filterMapMarkers({
  lat: userLocation.latitude,
  lon: userLocation.longitude,
  radius: 10, // 10km
  categories: [1, 2, 3],
  price_levels: [1, 2],
  min_rating: 4.0,
  limit: 100
});

// Không có vị trí (hiển thị tất cả theo filters)
const response = await filterMapMarkers({
  categories: [1, 2, 3],
  price_levels: [1, 2],
  min_rating: 4.0,
  limit: 100
});

if (response.success) {
  setMarkers(response.data);
}
```

### Lấy chỉ đường
```javascript
const response = await getDirection(
  { lat: 10.762622, lon: 106.660172 },
  { lat: 10.755, lon: 106.671 },
  'driving'
);

if (response.distance_meters) {
  // Parse polyline và vẽ route
  const points = decodePolyline(response.overview_polyline);
  setRouteCoords(points);
}
```

### Lấy chi tiết marker
```javascript
const response = await getMarkerDetail(markerId);
if (response.success) {
  console.log(response.data);
}
```

---

## Color Mapping cho Categories

```javascript
const colors = {
  1: '#FF9500', // Món Khô - Orange
  2: '#00BCD4', // Món Nước - Cyan
  3: '#F44336', // BBQ - Red
  4: '#4CAF50', // Món Chay - Green
  5: '#2196F3', // Hải Sản - Blue
  6: '#9C27B0', // Đồ Uống - Purple
};
```

---

## Testing

Để test APIs:

1. Start backend server:
```bash
cd backend_food_app
python App.py
```

2. Test với curl hoặc Postman:
```bash
# Get filter options
curl http://localhost:5000/api/map/filters

# Get nearby markers
curl -X POST http://localhost:5000/api/map/markers/nearby \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 10.762622,
    "lon": 106.660172,
    "radius": 5,
    "limit": 10
  }'
```

3. Trong frontend, map screen mới đã được tạo tại `MapScreenNew.jsx` với đầy đủ chức năng filtering và hiển thị markers từ backend.
