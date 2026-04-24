import requests
import re
from flask import Flask, request
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor

# 🔥 Lingua
from lingua import Language, LanguageDetectorBuilder

app = Flask(__name__)

TOKEN = "8170971907:AAE5CjJoTMyp6UGz9P0hGjm0uKJpXDrBKgSs"
URL = f"https://api.telegram.org/bot{TOKEN}"

# 🔥 إعداد اللغات
languages = [Language.ENGLISH, Language.TURKISH, Language.RUSSIAN, Language.ARABIC]
detector = LanguageDetectorBuilder.from_languages(*languages).build()

# ⚡ Thread pool للسرعة
executor = ThreadPoolExecutor(max_workers=3)


# 🔍 كشف لغة (متعدد)
def detect_languages(text):
    langs_found = set()

    # تقسيم النص
    words = text.split()

    for word in words:
        try:
            lang = detector.detect_language_of(word)

            if lang == Language.TURKISH:
                langs_found.add("tr")
            elif lang == Language.RUSSIAN:
                langs_found.add("ru")
            elif lang == Language.ARABIC:
                langs_found.add("ar")
            else:
                langs_found.add("en")

        except:
            continue

    if not langs_found:
        langs_found.add("en")

    return list(langs_found)


# ⚡ ترجمة (async)
def translate_async(text, target):
    return executor.submit(
        lambda: GoogleTranslator(source="auto", target=target).translate(text)
    )


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

    langs = detect_languages(text)

    futures = []
    results = []

    # 🎯 نحدد الترجمات المطلوبة
    if "en" in langs:
        futures.append(("🇹🇷", translate_async(text, "tr")))
        futures.append(("🇷🇺", translate_async(text, "ru")))

    if "tr" in langs:
        futures.append(("🇬🇧", translate_async(text, "en")))
        futures.append(("🇷🇺", translate_async(text, "ru")))

    if "ru" in langs:
        futures.append(("🇬🇧", translate_async(text, "en")))
        futures.append(("🇹🇷", translate_async(text, "tr")))

    if "ar" in langs:
        futures.append(("🇬🇧", translate_async(text, "en")))
        futures.append(("🇹🇷", translate_async(text, "tr")))
        futures.append(("🇷🇺", translate_async(text, "ru")))

    # ⏳ نجمع النتائج
    for flag, future in futures:
        try:
            result = future.result()
            results.append(f"{flag} {result}")
        except:
            pass

    reply = "\n".join(results)

    requests.post(
        f"{URL}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": reply,
            "reply_to_message_id": message_id
        }
    )

    return "ok", 200


@app.route("/")
def home():
    return "Bot is running", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
