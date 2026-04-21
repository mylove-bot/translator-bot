import os
import requests
from langdetect import detect
from flask import Flask, request
from deep_translator import GoogleTranslator

TOKEN = os.getenv("TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

session = requests.Session()


# ⚡ ترجمة سريعة
def multi_translate(text):
    try:
        en = GoogleTranslator(source="auto", target="en").translate(text)
        tr = GoogleTranslator(source="auto", target="tr").translate(text)
        ru = GoogleTranslator(source="auto", target="ru").translate(text)
        return en, tr, ru
    except Exception as e:
        print("Translate error:", e)
        return text, text, text


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if not data:
        return "ok", 200

    try:
        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")
        message_id = message.get("message_id")

        if not text or not chat_id:
            return "ok", 200

        # ⚡ ترجمة
        en, tr, ru = multi_translate(text)

        reply = f"""🌍 Translation:

🇬🇧 {en}
🇹🇷 {tr}
🇷🇺 {ru}
"""

        # 💬 Reply على نفس الرسالة
        requests.get(
            f"{URL}/sendMessage",
            params={
                "chat_id": chat_id,
                "text": reply,
                "reply_to_message_id": message_id
            }
        )

    except Exception as e:
        print("ERROR:", e)

    return "ok", 200


@app.route("/")
def home():
    return "Bot is running", 200
