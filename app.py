from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# ✅ IMPORTANT: Render > Environment doit contenir EXACTEMENT ces noms :
# TELEGRAM_TOKEN = 123456:ABC...
# CHAT_ID = 5000....
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.getenv("CHAT_ID", "").strip()


@app.route("/", methods=["GET"])
def home():
    return "OK - TV webhook Telegram bot running", 200


# ✅ Endpoint de test (GET) : vérifie Render -> Telegram sans TradingView
@app.route("/test", methods=["GET"])
def test():
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return "Missing TELEGRAM_TOKEN or CHAT_ID environment variables.", 500

    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "✅ TEST Render -> Telegram OK"}

    try:
        r = requests.post(tg_url, json=payload, timeout=15)
        return f"Telegram status={r.status_code} resp={r.text}", 200
    except Exception as e:
        return f"Telegram request failed: {str(e)}", 500


@app.route("/webhook", methods=["POST"])
def webhook():
    raw = request.data.decode("utf-8", errors="replace")
    headers = dict(request.headers)

    print("==== INCOMING WEBHOOK ====")
    print("HEADERS:", headers)
    print("RAW BODY:", raw)
    print("==========================")

    data = request.get_json(silent=True)

    if isinstance(data, dict):
        text = (
            f"📩 TradingView Alert\n"
            f"📊 Symbol: {data.get('symbol', '?')}\n"
            f"📌 Side: {data.get('side', '?')}\n"
            f"⏱ TF: {data.get('tf', '?')}\n"
            f"🎯 Entry: {data.get('entry', '?')}\n"
            f"🛑 SL: {data.get('sl', '?')}\n"
            f"✅ TP: {data.get('tp', '?')}\n"
            f"📏 SL pts: {data.get('sl_points', '?')}\n"
            f"📦 Qty: {data.get('qty', '?')}\n"
            f"⚠️ Risk%: {data.get('risk_pct', '?')}\n"
            f"📉 Daily DD%: {data.get('daily_dd_pct', '?')}\n"
        )
    else:
        text = f"📩 TradingView (RAW)\n{raw}"

    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Missing TELEGRAM_TOKEN or CHAT_ID environment variables.")
        return jsonify({"ok": False, "error": "Missing TELEGRAM_TOKEN or CHAT_ID"}), 500

    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}

    try:
        r = requests.post(tg_url, json=payload, timeout=15)
        print("TELEGRAM STATUS:", r.status_code)
        print("TELEGRAM RESPONSE:", r.text)
    except Exception as e:
        print("❌ Telegram request failed:", str(e))
        return jsonify({"ok": False, "error": "Telegram request failed"}), 500

    return jsonify({"ok": True}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)

