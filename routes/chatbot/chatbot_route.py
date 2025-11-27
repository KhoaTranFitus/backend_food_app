from flask import Blueprint, request, jsonify
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

from . import chatbot_bp

# Load .env
env_path = Path(__file__).parent / "openrouter.env"
load_dotenv(env_path)

API_KEY = os.getenv("OPENROUTER_API_KEY")
print("OPENROUTER KEY =", API_KEY)

URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

@chatbot_bp.route("/chatbot", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    payload = {
        "model": "meta-llama/llama-3-8b-instruct", 
        "messages": [
            {
                "role": "system",
                "content": "Bạn là chatbot ẩm thực Việt Nam, chỉ trả lời về đồ ăn, nhà hàng, nguyên liệu. Không trả lời các câu hỏi ngoài chủ đề ẩm thực ở Việt Nam."
                "nếu người dùng hỏi về các chủ đề khác, hãy lịch sự từ chối và nhắc họ hỏi về ẩm thực hay chỉ cần nói 'Tôi là một chatbot ẩm thực Việt Nam. Nếu người dùng"
                "hỏi bằng tiếng anh thì hãy trả lời bằng tiếng việt. Và trả lời ngắn gọn súc tích. Trình bày dưới dạng danh sách nếu có thể.Sửa lỗi fornt,form tiếng việt khi trả về file json."
                "thông tin cần được chính xác và cập nhật.Không trả lời các câu hỏi về y tế, tôn giáo hay chính trị, lịch sử, triết học, khoa học."
        
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    try:
        res = requests.post(URL, headers=HEADERS, json=payload)
        result = res.json()

        print("=== OPENROUTER RAW RESPONSE ===")
        print(result)

        reply = result["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)})
