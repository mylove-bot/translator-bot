import os
import requests
import re
from flask import Flask, request
from langdetect import detect
from deep_translator import GoogleTranslator

app = Flask(__name__)

# 🔴 مهم جدًا: لازم يكون في Render Environment Variables
TOKEN = os.getenv("TOKEN")

print("🔑 TOKEN IN SERVER:", TOKEN)

if not TOKEN:
    print("❌ TOKEN is missing!")

URL = f"https://api.telegram.org/bot{TOKEN}"


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
    data = request.get_json(force=True)

    print("🔥 UPDATE:", data)

    message = data.get("message") or data.get("edited_message")

    if not message:
        return "ok", 200

    text = message.get("text")
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")

    print("💬 TEXT:", text)
    print("🆔 CHAT ID:", chat_id)

    if not text or not chat_id:
        return "ok", 200

    lang = get_lang(text)

    if lang == "en":
        tr = translate(text, "tr")
        ru = translate(text, "ru")
        reply = f"🇹🇷 {tr}\n🇷🇺 {ru}"

    elif lang == "tr":
        en = translate(text, "en")
        ru = translate(text, "ru")
        reply = f"🇬🇧 {en}\n🇷🇺 {ru}"

    elif lang == "ru":
        en = translate(text, "en")
        tr = translate(text, "tr")
        reply = f"🇬🇧 {en}\n🇹🇷 {tr}"

    else:
        en = translate(text, "en")
        tr = translate(text, "tr")
        ru = translate(text, "ru")
        reply = f"🇬🇧 {en}\n🇹🇷 {tr}\n🇷🇺 {ru}"

    # 🚀 إرسال + كشف الخطأ الحقيقي
    r = requests.post(
        f"{URL}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": reply
        }
    )

    print("📤 STATUS:", r.status_code)
    print("📤 RESPONSE:", r.text)

    return "ok", 200


# 🏠 اختبار السيرفر
@app.route("/")
def home():
    return "Bot is running", 200


# 🚀 تشغيل
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
