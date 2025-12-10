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

def _parse_price(price_range: str) -> int:
    """Parse price range string và trả về giá trung bình để sort"""
    try:
        # Format: "50,000đ-150,000đ" hoặc "50.000đ-150.000đ"
        price_range = price_range.replace('đ', '').replace(',', '').replace('.', '')
        prices = [int(p.strip()) for p in price_range.split('-') if p.strip().isdigit()]
        if prices:
            return sum(prices) // len(prices)  # Trả về giá trung bình
    except:
        pass
    return 999999  # Giá rất cao nếu không parse được
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

def find_restaurants_by_name(query: str) -> List[Dict]:
    """Tìm nhà hàng theo TÊN QUÁN từ user query"""
    try:
        print(f"🏪 Searching restaurants by name: {query}")
        
        results = []
        query_normalized = normalize_text(query)
        query_words = query_normalized.split()
        
        for restaurant in DB_RESTAURANTS:
            if not isinstance(restaurant, dict):
                continue
            
            name_normalized = normalize_text(restaurant.get("name", ""))
            
            # Kiểm tra xem có từ nào trong query match với tên quán
            match = any(word in name_normalized for word in query_words if len(word) > 2)
            
            if match:
                results.append(restaurant)
                print(f"  ✅ Found by name: {restaurant.get('name')}")
        
        print(f"📊 Found {len(results)} restaurants by name")
        return results[:10]
        
    except Exception as e:
        print(f"❌ Error in find_restaurants_by_name: {e}")
        return []

def find_restaurants_by_location(query: str) -> List[Dict]:
    """Tìm nhà hàng theo ĐỊA ĐIỂM từ user query - sử dụng normalize_text()"""
    try:
        print(f"🔍 Searching restaurants by location: {query}")
        
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
        
        # Kiểm tra "gần tôi" / "nearby"
        nearby_keywords = ["gan toi", "gan day", "nearby", "near me", "o day"]
        is_nearby_query = any(keyword in query_normalized for keyword in nearby_keywords)
        
        if is_nearby_query:
            print("📍 Detected 'nearby' query - returning top restaurants")
            # Trả về top restaurants (có thể sort theo rating)
            sorted_restaurants = sorted(
                [r for r in DB_RESTAURANTS if isinstance(r, dict)],
                key=lambda x: x.get('rating', 0),
                reverse=True
            )
            return sorted_restaurants[:10]
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
        
        print(f"📊 Total found: {len(results)} restaurants by location")
        return results[:10]  # Return top 10
        
    except Exception as e:
        print(f"❌ Error in find_restaurants_by_location: {e}")
        return []

@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    """Chat endpoint sử dụng OpenAI GPT với dữ liệu từ backend - có memory"""
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

        # Lấy hoặc tạo conversation_id mới
        conversation_id = data.get("conversation_id", str(uuid4()))
        
        # Khởi tạo conversation history nếu chưa có
        if conversation_id not in conversations:
            conversations[conversation_id] = []

        # Tìm kiếm theo nhiều tiêu chí
        location_results = find_restaurants_by_location(user_message)
        dish_results = find_restaurants_by_dish(user_message)
        name_results = find_restaurants_by_name(user_message)
        
        # Phát hiện từ khóa đặc biệt để sắp xếp
        query_normalized = normalize_text(user_message)
        
        # Từ khóa liên quan đến giá
        price_keywords = ["gia re", "re nhat", "re", "binh dan", "tiet kiem", "cheap"]
        has_price_filter = any(keyword in query_normalized for keyword in price_keywords)
        
        # Từ khóa liên quan đến đánh giá
        rating_keywords = ["ngon nhat", "tot nhat", "diem cao", "danh gia cao", "best", "top rated", "ngon", "chat luong"]
        has_rating_filter = any(keyword in query_normalized for keyword in rating_keywords)
        
        # Logic tìm kiếm theo thứ tự ưu tiên:
        # 1. Địa điểm + Món ăn -> lọc theo địa điểm trước, sau đó món ăn
        # 2. Địa điểm + Tên quán -> lọc theo địa điểm trước, sau đó tên quán
        # 3. Chỉ địa điểm -> dùng location_results
        # 4. Chỉ món ăn -> dùng dish_results
        # 5. Chỉ tên quán -> dùng name_results
        
        search_results = []
        search_type = ""
        
        # Case 1: Có địa điểm + món ăn
        if location_results and dish_results:
            print("🔎 Có cả địa điểm và món ăn - ưu tiên địa điểm, lọc theo món ăn")
            location_ids = {r.get('id') or r.get('name') for r in location_results}
            search_results = [r for r in dish_results if (r.get('id') or r.get('name')) in location_ids]
            search_type = "location_and_dish"
            
            # Nếu không có giao nhau, dùng location_results
            if not search_results:
                search_results = location_results
                search_type = "location_only"
        
        # Case 2: Có địa điểm + tên quán
        elif location_results and name_results:
            print("🔎 Có cả địa điểm và tên quán - ưu tiên địa điểm, lọc theo tên quán")
            location_ids = {r.get('id') or r.get('name') for r in location_results}
            search_results = [r for r in name_results if (r.get('id') or r.get('name')) in location_ids]
            search_type = "location_and_name"
            
            # Nếu không có giao nhau, dùng location_results
            if not search_results:
                search_results = location_results
                search_type = "location_only"
        
        # Case 3: Chỉ có địa điểm
        elif location_results:
            search_results = location_results
            search_type = "location_only"
        
        # Case 4: Chỉ có món ăn
        elif dish_results:
            search_results = dish_results
            search_type = "dish_only"
        
        # Case 5: Chỉ có tên quán
        elif name_results:
            search_results = name_results
            search_type = "name_only"
        
        print(f"🔎 Search results - Location: {len(location_results)}, Dish: {len(dish_results)}, Name: {len(name_results)}")
        print(f"🔎 Search type: {search_type}, Total results: {len(search_results)}")
        
        # Áp dụng filter và sort dựa trên từ khóa
        if search_results:
            # Nếu có từ khóa về giá rẻ -> sắp xếp theo giá tăng dần
            if has_price_filter:
                print("💰 Filtering by price - sorting by low to high price")
                search_results = sorted(
                    search_results,
                    key=lambda x: _parse_price(x.get('price_range', '999999'))
                )
                search_type += "_price_sorted"
            
            # Nếu có từ khóa về đánh giá -> sắp xếp theo rating giảm dần
            elif has_rating_filter:
                print("⭐ Filtering by rating - sorting by highest rating")
                search_results = sorted(
                    search_results,
                    key=lambda x: float(x.get('rating', 0)),
                    reverse=True
                )
                search_type += "_rating_sorted"
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
        

        restaurants_json = json.dumps(all_restaurants_data, ensure_ascii=False, indent=2)

        # Prepare system prompt với context về loại tìm kiếm
        search_context = ""
        base_type = search_type.replace("_price_sorted", "").replace("_rating_sorted", "")
        
        if base_type == "dish_only":
            search_context = "\n🍽️ Người dùng tìm kiếm theo MÓN ĂN. Kết quả dưới đây là các QUÁN ĂN có món này."
        elif base_type == "location_only":
            search_context = "\n📍 Người dùng tìm kiếm theo ĐỊA ĐIỂM. Kết quả dưới đây là các quán ăn tại địa điểm này."
        elif base_type == "location_and_dish":
            search_context = "\n📍🍽️ Người dùng tìm kiếm MÓN ĂN tại ĐỊA ĐIỂM cụ thể. Đã ưu tiên lọc theo địa điểm trước, sau đó tìm món ăn."
        elif base_type == "name_only":
            search_context = "\n🏪 Người dùng tìm kiếm theo TÊN QUÁN. Kết quả dưới đây là các quán ăn có tên phù hợp."
        elif base_type == "location_and_name":
            search_context = "\n📍🏪 Người dùng tìm kiếm TÊN QUÁN tại ĐỊA ĐIỂM cụ thể. Đã ưu tiên lọc theo địa điểm trước, sau đó tìm theo tên quán."
        
        # Thêm context về sorting
        if "_price_sorted" in search_type:
            search_context += "\n💰 Kết quả đã được SẮP XẾP THEO GIÁ từ RẺ đến ĐẮNG (ưu tiên giá rẻ)."
        elif "_rating_sorted" in search_type:
            search_context += "\n⭐ Kết quả đã SẮP XẾP THEO RATING từ CAO đến THẤP."
        
        system_prompt = f"""Bạn là chatbot ẩm thực Việt Nam chuyên tư vấn về đồ ăn, nhà hàng, và nguyên liệu.
{search_context}

Dữ liệu nhà hàng từ hệ thống:
{restaurants_json}

Hướng dẫn:
1. LUÔN sử dụng dữ liệu nhà hàng trên để trả lời nếu có

2. **KHI TÌM KIẾM THEO MÓN ĂN**:
   - Hệ thống đã TÌM KIẾM THEO TÊN MÓN và trả về danh sách QUÁN ĂN có món đó
   - Giải thích: "Dưới đây là các quán ăn có [tên món]:"
   - Liệt kê từng quán với: tên, địa chỉ, rating, số điện thoại, giờ mở cửa, khoảng giá
   - Nếu có "recommended_dishes": liệt kê món ăn cụ thể với TÊN, GIÁ, MÔ TẢ

3. **KHI TÌM KIẾM THEO TÊN QUÁN**:
   - Hệ thống đã tìm theo tên quán ăn
   - Giải thích: "Dưới đây là các quán ăn [tên quán]:"
   - Liệt kê thông tin chi tiết của từng quán

4. **KHI TÌM KIẾM THEO ĐỊA ĐIỂM**:
   - Nếu người dùng hỏi "quán ăn gần tôi" / "gần đây" / "nearby": trả lời "Dưới đây là các quán ăn gần bạn:"
   - Nếu hỏi địa điểm cụ thể: "Dưới đây là các quán ăn ở [địa điểm]:"

5. **KHI CÓ CẢ ĐỊA ĐIỂM VÀ (MÓN ĂN hoặc TÊN QUÁN)**:
   - Hệ thống đã ưu tiên lọc theo ĐỊA ĐIỂM trước
   - Giải thích rõ: "Dưới đây là các quán [món/tên quán] tại [địa điểm]:"

6. **KHI CÓ "GIÁ RẺ"**: Nhấn mạnh "Dưới đây là các quán [món] với giá rẻ nhất:", ưu tiên hiển thị khoảng giá.

7. **KHI CÓ "NGON NHẤT"**: Nhấn mạnh "Dưới đây là các quán [món] ngon nhất/được đánh giá cao nhất:", ưu tiên hiển thị rating.

8. **THEO DÕI NGỮ CẢNH**:
   - Bạn có thể nhớ những gì đã nói trong cuộc trò chuyện này
   - Khi người dùng nói "quán đầu tiên", "quán thứ 2", "quán này", "nó" -> tham chiếu đến quán đã recommend
   - Khi người dùng đồng ý ("ok", "được", "đồng ý", "yes", "có", "thích") -> hiểu là họ muốn action với quán đó
   - Khi người dùng yêu cầu "thêm vào yêu thích", "lưu lại", "save", "bookmark" -> gợi ý họ dùng tính năng favorite

9. **Format trả lời**: Liệt kê với emoji: 📍 địa chỉ, ⭐ rating, 📞 điện thoại, 🕒 giờ mở, 💰 giá. Trả lời tiếng Việt, ngắn gọn 5-8 câu.

10. **NẾU KHÔNG CÓ DỮ LIỆU**: "Xin lỗi, hệ thống tôi hiện không có thông tin về [...]"

11. Chỉ trả lời về ẩm thực Việt Nam. Nếu hỏi chủ đề khác, lịch sự từ chối."""
        # Xây dựng messages array với lịch sử
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        # Thêm lịch sử cuộc trò chuyện (giới hạn 10 messages gần nhất để tránh token limit)
        history = conversations.get(conversation_id, [])
        for msg in history[-10:]:
            messages.append({
                "role": "user",
                "content": msg["user_message"]
            })
            messages.append({
                "role": "assistant",
                "content": msg["bot_response"]
            })
        
        # Thêm message hiện tại
        messages.append({
            "role": "user",
            "content": user_message
        })
        

        # Call OpenAI API
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 600
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

        # Lưu conversation với metadata
        conversation_entry = {
            "user_message": user_message,
            "bot_response": bot_response,
            "timestamp": datetime.now().isoformat(),
            "search_type": search_type,
            "restaurants_found": len(search_results),
            "restaurant_names": [r.get("name") for r in search_results[:5]] if search_results else []
        }
        
        conversations[conversation_id].append(conversation_entry)

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
