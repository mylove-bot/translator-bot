import os
import requests
import re
from flask import Flask, request
from langdetect import detect
from deep_translator import GoogleTranslator

app = Flask(__name__)

# 🔴 مهم: التوكن لازم يكون موجود في Render Environment Variables
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ TOKEN is missing! Add it in Render Environment Variables")
    TOKEN = "MISSING_TOKEN"

URL = f"https://api.telegram.org/bot{TOKEN}"

session = requests.Session()


# 🔍 كشف اللغة
def get_lang(text):
    try:
        if re.search(r'[\u0600-\u06FF]', text):
            return "ar"

        if re.search(r'[\u0400-\u04FF]', text):
            return "ru"

        if re.search(r'[ğüşöçıİ]', text.lower()):
            return "tr"

        lang = detect(text)

        if lang.startswith("tr"):
            return "tr"
        if lang.startswith("ru"):
            return "ru"

        return "en"

    except:
        return "en"


# ⚡ الترجمة
def translate(text, target):
    try:
        return GoogleTranslator(source="auto", target=target).translate(text)
    except Exception as e:
        print("Translate error:", e)
        return text


# 💬 webhook
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

        lang = get_lang(text)

        # 🇬🇧 English → TR + RU
        if lang == "en":
            tr = translate(text, "tr")
            ru = translate(text, "ru")
            reply = f"🇹🇷 {tr}\n🇷🇺 {ru}"

        # 🇹🇷 Turkish → EN + RU
        elif lang == "tr":
            en = translate(text, "en")
            ru = translate(text, "ru")
            reply = f"🇬🇧 {en}\n🇷🇺 {ru}"

        # 🇷🇺 Russian → EN + TR
        elif lang == "ru":
            en = translate(text, "en")
            tr = translate(text, "tr")
            reply = f"🇬🇧 {en}\n🇹🇷 {tr}"

        # 🌍 fallback
        else:
            en = translate(text, "en")
            tr = translate(text, "tr")
            ru = translate(text, "ru")
            reply = f"🇬🇧 {en}\n🇹🇷 {tr}\n🇷🇺 {ru}"

        # 💬 إرسال الرد
        requests.post(
            f"{URL}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": reply,
                "reply_to_message_id": message_id
            },
            timeout=10
        )

    except Exception as e:
        print("ERROR:", e)

    return "ok", 200


# 🏠 اختبار السيرفر
@app.route("/")
def home():
    return "Bot is running", 200


# 🚀 تشغيل Flask على Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
