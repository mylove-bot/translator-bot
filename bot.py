import os
import requests
from langdetect import detect
from flask import Flask, request

TOKEN = os.getenv("TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

session = requests.Session()


def translate(text, source, target):
    try:
        url = "https://libretranslate.de/translate"
        payload = {
            "q": text,
            "source": source,
            "target": target,
            "format": "text"
        }
        r = session.post(url, json=payload, timeout=5)
        return r.json().get("translatedText", "")
    except Exception:
        return "..."


def get_lang(text):
    try:
        return detect(text)
    except Exception:
        return "en"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if not data:
        return "ok", 200

    try:
        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if not text or not chat_id:
            return "ok", 200

        lang = get_lang(text)

        if lang.startswith("en"):
            tr = translate(text, "en", "tr")
            ru = translate(text, "en", "ru")
            reply = f"🇹🇷 {tr}\n🇷🇺 {ru}"

        elif lang.startswith("tr"):
            en = translate(text, "tr", "en")
            ru = translate(text, "tr", "ru")
            reply = f"🇬🇧 {en}\n🇷🇺 {ru}"

        elif lang.startswith("ru"):
            en = translate(text, "ru", "en")
            tr = translate(text, "ru", "tr")
            reply = f"🇬🇧 {en}\n🇹🇷 {tr}"

        else:
            en = translate(text, "auto", "en")
            tr = translate(text, "auto", "tr")
            ru = translate(text, "auto", "ru")
            reply = f"🇬🇧 {en}\n🇹🇷 {tr}\n🇷🇺 {ru}"

        # 🔥 إرسال الرسالة (بدون telegram library)
        requests.get(
            f"{URL}/sendMessage",
            params={
                "chat_id": chat_id,
                "text": reply
            }
        )

    except Exception as e:
        print("ERROR:", e)

    return "ok", 200


@app.route("/")
def home():
    return "Bot is running", 200