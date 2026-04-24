import requests
from flask import Flask, request
from deep_translator import GoogleTranslator

app = Flask(__name__)

# 🔴 حط التوكن الجديد هنا
TOKEN = "8170971907:AAE5CjJoTMyp6UGzP0hGjm0uKJpXDrBKgSs"

URL = f"https://api.telegram.org/bot{TOKEN}"


# 🌍 ترجمة + كشف لغة من Google
def translate_auto(text, target):
    try:
        translator = GoogleTranslator(source="auto", target=target)
        result = translator.translate(text)
        detected = translator.source  # اللغة المكتشفة
        return result, detected
    except Exception as e:
        print("Translate error:", e)
        return text, "en"


# 🌐 ترجمة لعدة لغات مرة وحدة
def multi_translate(text):
    try:
        en = GoogleTranslator(source="auto", target="en").translate(text)
        tr = GoogleTranslator(source="auto", target="tr").translate(text)
        ru = GoogleTranslator(source="auto", target="ru").translate(text)
        return en, tr, ru
    except Exception as e:
        print("Translate error:", e)
        return text, text, text


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

    # 🔍 كشف اللغة باستخدام Google
    _, lang = translate_auto(text, "en")

    # 🌍 ترجمة
    en, tr, ru = multi_translate(text)

    if lang == "en":
        reply = f"🇹🇷 {tr}\n🇷🇺 {ru}"

    elif lang == "tr":
        reply = f"🇬🇧 {en}\n🇷🇺 {ru}"

    elif lang == "ru":
        reply = f"🇬🇧 {en}\n🇹🇷 {tr}"

    else:
        reply = f"🇬🇧 {en}\n🇹🇷 {tr}\n🇷🇺 {ru}"

    # 🚀 إرسال + reply على نفس الرسالة
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
