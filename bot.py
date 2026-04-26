import requests
from flask import Flask, request

app = Flask(__name__)

# 🔴 التوكن
TOKEN = "8170971907:AAE5CjJoTMyp6UGzP0hGjm0uKJpXDrBKgSs"
URL = f"https://api.telegram.org/bot{TOKEN}"

# 🌐 ترجمة باستخدام LibreTranslate
def translate(text, target):
    try:
        response = requests.post(
            "https://libretranslate.de/translate",
            data={
                "q": text,
                "source": "auto",
                "target": target,
                "format": "text"
            }
        )
        return response.json()["translatedText"]
    except Exception as e:
        return f"خطأ بالترجمة: {e}"


# 💬 webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    message = data.get("message") or data.get("edited_message")

    if not message:
        return "ok", 200

    text = message.get("text")
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")

    if not text or not chat_id:
        return "ok", 200

    # 🌍 الترجمات (دائمًا إنجليزي + روسي + تركي)
    en = translate(text, "en")
    ru = translate(text, "ru")
    tr = translate(text, "tr")

    # 💬 الرد
    reply = f"🇬🇧 {en}\n🇷🇺 {ru}\n🇹🇷 {tr}"

    # 🚀 إرسال الرد
    requests.post(
        f"{URL}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": reply,
            "reply_to_message_id": message_id
        }
    )

    return "ok", 200


# 🏠 اختبار السيرفر
@app.route("/")
def home():
    return "Bot is running", 200


# 🚀 تشغيل
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
