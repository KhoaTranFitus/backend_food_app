"""
Food Tourism Chatbot - Unified Version
Sử dụng OpenAI GPT + Backend Database Integration
"""

from flask import request, jsonify
from . import chatbot_bp
from datetime import datetime
from uuid import uuid4
import os
import json
import requests
from typing import List, Dict, Optional

# Import data từ backend
from core.database import DB_RESTAURANTS, MENUS_BY_RESTAURANT_ID, DB_CATEGORIES
from core.search import normalize_text

# Load environment variables
from dotenv import load_dotenv, dotenv_values

load_dotenv()

# Lấy API key (ưu tiên từ environment variable)
API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# Nếu không có trong env, thử lấy từ .env file trong chatbot folder
if not API_KEY:
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        config = dotenv_values(env_path)
        API_KEY = config.get("OPENAI_API_KEY", "").strip().strip('"').strip("'")

# Validate API key
if not API_KEY or not API_KEY.startswith("sk-"):
    print("⚠️  WARNING: API key không được cấu hình đúng. Chatbot có thể không hoạt động.")
    print(f"   API_KEY value: {API_KEY[:20] if API_KEY else 'None'}...")
else:
    print("✅ API key loaded successfully")

# Conversation memory (in-memory)
conversations: Dict[str, List[Dict]] = {}

def get_restaurant_context() -> str:
    """Lấy thông tin nhà hàng để đưa vào prompt"""
    restaurants_context = ""
    if DB_RESTAURANTS:
        restaurants_context = "\n\n📍 Danh sách các nhà hàng trong hệ thống (mẫu):\n"
        for r in DB_RESTAURANTS[:10]:  # Lấy top 10
            try:
                name = r.get('name', 'N/A')
                address = r.get('address', 'N/A')
                rating = r.get('rating', 'N/A')
                restaurants_context += f"- {name}\n"
                restaurants_context += f"  📍 {address}\n"
                restaurants_context += f"  ⭐ Rating: {rating}/5\n"
            except Exception as e:
                print(f"⚠️  Error formatting restaurant: {e}")
                continue
    return restaurants_context

def find_restaurants_by_dish(query: str) -> List[Dict]:
    """Tìm nhà hàng theo tên món ăn từ user query"""
    try:
        print(f"🍽️ Searching restaurants by dish: {query}")
        
        results_dict = {}  # Dùng dict để tránh duplicate
        query_lower = query.lower()
        
        # Build a dict: numeric restaurant_id -> Restaurant object
        restaurants_by_numeric_id = {}
        for idx, restaurant in enumerate(DB_RESTAURANTS, start=1):
            restaurants_by_numeric_id[str(idx)] = restaurant
        
        # Tìm kiếm trong menus
        for restaurant_id, menu_items in MENUS_BY_RESTAURANT_ID.items():
            if not isinstance(menu_items, list):
                continue
                
            for item in menu_items:
                if not isinstance(item, dict):
                    continue
                    
                dish_name = item.get("dish_name", "").lower()
                dish_tags = [tag.lower() for tag in item.get("dish_tags", [])]
                
                # Kiểm tra xem có từ khóa nào match
                if query_lower in dish_name or any(query_lower in tag for tag in dish_tags):
                    # Lấy thông tin nhà hàng dựa trên numeric restaurant_id
                    if restaurant_id in restaurants_by_numeric_id:
                        restaurant = restaurants_by_numeric_id[restaurant_id]
                        if restaurant_id not in results_dict:
                            results_dict[restaurant_id] = restaurant.copy()
                            results_dict[restaurant_id]['matching_dishes'] = []
                        # Thêm món ăn tìm thấy
                        results_dict[restaurant_id]['matching_dishes'].append(item)
        
        results = list(results_dict.values())
        print(f"✅ Found {len(results)} restaurants with matching dishes")
        return results[:10]
        
    except Exception as e:
        print(f"❌ Error in find_restaurants_by_dish: {e}")
        return []

def find_restaurants_by_location(query: str) -> List[Dict]:
    """Tìm nhà hàng theo location từ user query - sử dụng normalize_text()"""
    try:
        print(f"🔍 Searching restaurants for query: {query}")
        
        results = []
        query_normalized = normalize_text(query)  # Chuyển thành: "ho chi minh"
        
        print(f"📍 Normalized query: {query_normalized}")
        
        # Các biến thể địa điểm (đã normalize)
        location_variants = {
            "ho chi minh": ["ho chi minh", "sai gon", "tp ho chi minh", "hcmc", "tphcm", "tp hcm"],
            "ha noi": ["ha noi", "hanoi"],
            "da nang": ["da nang"],
            "hai phong": ["hai phong"],
            "can tho": ["can tho"],
        }
        
        # Tìm location nào match với query
        matched_location = None
        for location_key, variants in location_variants.items():
            for variant in variants:
                if variant in query_normalized:
                    matched_location = location_key
                    print(f"✅ Matched location key: {location_key} (variant: {variant})")
                    break
            if matched_location:
                break
        
        # Nếu tìm được location, lọc nhà hàng
        if matched_location:
            for restaurant in DB_RESTAURANTS:
                if not isinstance(restaurant, dict):
                    continue
                    
                address_normalized = normalize_text(restaurant.get("address", ""))
                tags = restaurant.get("tags", [])
                
                # Xử lý tags có thể là list hoặc string
                if isinstance(tags, list):
                    tags_normalized = [normalize_text(tag) for tag in tags]
                else:
                    tags_normalized = [normalize_text(str(tags))]
                
                # Kiểm tra tất cả variants của location trong address hoặc tags
                for variant in location_variants[matched_location]:
                    if variant in address_normalized or any(variant in tag for tag in tags_normalized):
                        results.append(restaurant)
                        print(f"  ✅ Found: {restaurant.get('name')} at {restaurant.get('address')}")
                        break
        
        print(f"📊 Total found: {len(results)} restaurants")
        return results[:10]  # Return top 10
        
    except Exception as e:
        print(f"❌ Error in find_restaurants_by_location: {e}")
        return []

@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    """Chat endpoint sử dụng OpenAI GPT với dữ liệu từ backend"""
    try:
        # Validate API key
        if not API_KEY:
            return jsonify({
                "error": "API key không được cấu hình. Vui lòng thiết lập OPENAI_API_KEY."
            }), 500
        
        data = request.get_json() or {}
        user_message = (data.get("message") or data.get("query") or "").strip()

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        conversation_id = data.get("conversation_id", str(uuid4()))

        # Tìm kiếm nhà hàng theo địa điểm và theo món ăn
        location_results = find_restaurants_by_location(user_message)
        dish_results = find_restaurants_by_dish(user_message)
        
        # Logic tìm kiếm: 
        # 1. Nếu có cả địa điểm VÀ món ăn -> lọc dish_results theo location
        # 2. Nếu chỉ có địa điểm -> dùng location_results
        # 3. Nếu chỉ có món ăn -> dùng dish_results
        search_results = []
        search_type = ""
        
        if location_results and dish_results:
            # Có cả 2 -> ưu tiên địa điểm, sau đó lọc theo món ăn
            print("🔎 Có cả địa điểm và món ăn - lọc theo địa điểm trước")
            location_ids = {r.get('place_id') or r.get('name') for r in location_results}
            search_results = [r for r in dish_results if (r.get('place_id') or r.get('name')) in location_ids]
            search_type = "location_and_dish"
            
            # Nếu không có kết quả giao nhau, dùng location_results
            if not search_results:
                search_results = location_results
                search_type = "location_only"
        elif location_results:
            search_results = location_results
            search_type = "location_only"
        elif dish_results:
            search_results = dish_results
            search_type = "dish_only"
        
        print(f"🔎 Location results: {len(location_results)}, Dish results: {len(dish_results)}")
        print(f"🔎 Search type: {search_type}, Total results: {len(search_results)}")
        
        # Chuẩn bị dữ liệu nhà hàng cho prompt
        all_restaurants_data = []
        for r in search_results:
            try:
                restaurant_info = {
                    "name": r.get("name", "N/A"),
                    "address": r.get("address", "N/A"),
                    "rating": r.get("rating", "N/A"),
                    "phone": r.get("phone_number", "N/A"),
                    "price_range": r.get("price_range", "N/A"),
                    "open_hours": r.get("open_hours", "N/A")
                }
                
                # Nếu có matching_dishes từ search theo món ăn, thêm vào
                if "matching_dishes" in r:
                    restaurant_info["recommended_dishes"] = [
                        {
                            "name": d.get("dish_name"),
                            "price": d.get("price"),
                            "description": d.get("description")
                        }
                        for d in r["matching_dishes"]
                        if isinstance(d, dict)
                    ]
                
                all_restaurants_data.append(restaurant_info)
            except Exception as e:
                print(f"⚠️  Error formatting restaurant data: {e}")
                continue
        
        # Convert to JSON string để đưa vào prompt
        restaurants_json = json.dumps(all_restaurants_data, ensure_ascii=False, indent=2)

        # Prepare system prompt với context về loại tìm kiếm
        search_context = ""
        if search_type == "dish_only":
            search_context = "\n🍽️ Người dùng hỏi về MÓN ĂN. Kết quả dưới đây là các QUÁN ĂN có món này."
        elif search_type == "location_only":
            search_context = "\n📍 Người dùng hỏi về ĐỊA ĐIỂM. Kết quả dưới đây là các quán ăn tại địa điểm này."
        elif search_type == "location_and_dish":
            search_context = "\n📍🍽️ Người dùng hỏi về MÓN ĂN tại ĐỊA ĐIỂM cụ thể. Đã lọc theo địa điểm trước, sau đó tìm món ăn."
        
        system_prompt = f"""Bạn là chatbot ẩm thực Việt Nam chuyên tư vấn về đồ ăn, nhà hàng, và nguyên liệu.
{search_context}

Dữ liệu nhà hàng liên quan từ hệ thống:
{restaurants_json}

Hướng dẫn:
1. **QUAN TRỌNG**: Luôn sử dụng dữ liệu nhà hàng trên để trả lời nếu có thông tin liên quan

2. **KHI NGƯỜI DÙNG HỎI VỀ MÓN ĂN**:
   - Hệ thống đã TÌM KIẾM THEO TÊN MÓN và trả về danh sách QUÁN ĂN có món đó
   - Giải thích: "Dưới đây là các quán ăn có [tên món]:"
   - Liệt kê từng quán với: tên, địa chỉ, rating, số điện thoại
   - Nếu có "recommended_dishes": liệt kê món ăn phù hợp với TÊN, GIÁ, MÔ TẢ

3. **KHI CÓ CẢ ĐỊA ĐIỂM VÀ MÓN ĂN**:
   - Ưu tiên lọc theo ĐỊA ĐIỂM trước, sau đó tìm món ăn
   - Giải thích: "Dưới đây là các quán ăn có [món] tại [địa điểm]:"

4. **Nếu có dữ liệu nhà hàng**:
   - Liệt kê tên nhà hàng, địa chỉ, số điện thoại, rating, giờ mở cửa, khoảng giá
   - Trả lời bằng tiếng Việt, chi tiết nhưng ngắn gọn (5-8 câu)
   - Format dễ đọc với emoji phù hợp

5. **Nếu KHÔNG có dữ liệu**:
   - Nói rõ: "Xin lỗi, hệ thống tôi hiện không có thông tin về [gì đó]"
   - Có thể tư vấn chung chung về món ăn đó

6. Chỉ trả lời về ẩm thực, nhà hàng, món ăn Việt Nam
7. Nếu người dùng hỏi chủ đề khác, lịch sự từ chối"""

        # Call OpenAI API
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        # Handle HTTP errors
        if response.status_code != 200:
            print(f"❌ OpenAI API error: {response.status_code}")
            return jsonify({
                "error": f"OpenAI API error: {response.status_code}"
            }), 500
        
        result = response.json()

        print(f"🤖 OpenAI Response: {result}")

        if "error" in result:
            error_msg = result['error'].get('message', 'Unknown error')
            print(f"❌ API error: {error_msg}")
            return jsonify({"error": f"API error: {error_msg}"}), 400

        bot_response = result["choices"][0]["message"]["content"]

        # Save conversation
        conversations.setdefault(conversation_id, []).append({
            "user_message": user_message,
            "bot_response": bot_response,
            "timestamp": datetime.now().isoformat()
        })

        return jsonify({
            "conversation_id": conversation_id,
            "user_message": user_message,
            "bot_response": bot_response,
            "timestamp": datetime.now().isoformat()
        })

    except requests.exceptions.Timeout:
        print(f"❌ OpenAI API timeout")
        return jsonify({"error": "Request timeout"}), 504
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return jsonify({"error": f"Network error: {str(e)}"}), 500
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Chat error: {str(e)}"}), 500


@chatbot_bp.route("/chat/history/<conversation_id>", methods=["GET"])
def get_conversation_history(conversation_id: str):
    """Lấy lịch sử cuộc trò chuyện"""
    try:
        history = conversations.get(conversation_id, [])
        return jsonify({
            "conversation_id": conversation_id,
            "history": history,
            "total_messages": len(history)
        })
    except Exception as e:
        print(f"❌ Error getting history: {e}")
        return jsonify({"error": f"Error: {str(e)}"}), 500


@chatbot_bp.route("/chat/status", methods=["GET"])
def chat_status():
    """Check chatbot status"""
    return jsonify({
        "status": "running",
        "api_key_configured": bool(API_KEY),
        "total_conversations": len(conversations),
        "total_restaurants": len(DB_RESTAURANTS),
        "timestamp": datetime.now().isoformat()
    })
