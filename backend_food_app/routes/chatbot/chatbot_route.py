from flask import Blueprint, request, jsonify
import openai
from . import chatbot_bp
chat_bp = Blueprint("chatbot", __name__)

openai.api_key = "YOUR_OPENAI_API_KEY"

@chat_bp.route("/chatbot", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # Giới hạn chatbot chỉ nói về đồ ăn
    prompt = f"Bạn là chatbot ẩm thực. Chỉ trả lời về món ăn, nhà hàng, nguyên liệu, mẹo nấu ăn.\nNgười dùng: {user_message}\nChatbot:"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
        )
        answer = response["choices"][0]["message"]["content"]
        return jsonify({"reply": answer})
    except Exception as e:
        return jsonify({"error": str(e)})
