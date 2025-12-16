from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

@app.route("/", methods=["GET"])
def home():
    return "Bot Telegram OK", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("📩 Alerte reçue :", data)

    text = f"""📊 {data.get('symbol')}
🚀 {data.get('side')}
TF: {data.get('tf')}
Entry: {data.get('entry')}
SL: {data.get('sl')}
TP: {data.get('tp')}
Risk: {data.get('risk_pct')}%
"""

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }

    r = requests.post(url, json=payload)
    print("📨 Telegram status:", r.status_code, r.text)

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

