categories/{category_id}
{
  "id": 1,
  "name": "Vietnamese",
  "icon": "🍜",
  "color": "#FFD700"
}

restaurants/{id}
{
  "id": 1,
  "name": "Phở Lệ",
  "category_id": 1,
  "rating": 4.7,
  "price_level": 2,
  "address": "413-415 Nguyễn Trãi, Phường 7, Quận 5, TP. HCM",
  "lat": 10.75501,
  "lon": 106.67102,
  "phone_number": "02839234008",
  "open_hours": "06:00 - 13:00",
  "main_image_url": "https://example.com/images/pho-le-cover.jpg",
  "photos": [
    "https://example.com/images/pho-le-1.jpg",
    "https://example.com/images/pho-le-2.jpg"
  ],
  "tags": ["pho", "bò", "quán ăn địa phương", "quận 5", "bữa sáng"],
  "description": "Quán phở bò nổi tiếng hơn 70 năm tại Quận 5."
}

menus/{id}
{
    {
  "id": 101,
  "restaurant_id": 1,
  "dish_name": "Phở Tái",
  "price": 70000,
  "description": "Thịt bò tái mềm, nước lèo đậm đà.",
  "dish_tags": ["bò", "nước", "phở"],
  "image_url": "https://example.com/foods/pho-tai.jpg",
  "category_id": 1
}

}
users/{user_id}
{
    {
  "id": "U001",
  "name": "Le Thi Hieu",
  "email": "a@example.com",
  "password": "123456",  
  "avatar_url": "",
  "favorites": [1, 3],
  "history": [
    { "query": "pho", "time": "2025-11-07T10:00:00Z" }
  ],
  "location": {
    "lat": 10.77,
    "lon": 106.69
  }
}
}
