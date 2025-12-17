from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# =========================
# ENV VARS (Render)
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.getenv("CHAT_ID", "").strip()


# =========================
# HOME (health check)
# =========================
@app.route("/", methods=["GET"])
def home():
    return "OK - TV webhook Telegram bot running", 200


# =========================
# TEST TELEGRAM (GET)
# =========================
@app.route("/test", methods=["GET"])
def test():
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return "❌ Missing TELEGRAM_TOKEN or CHAT_ID", 500

    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": "✅ TEST OK : Render → Telegram fonctionne"
    }

    r = requests.post(tg_url, json=payload, timeout=15)
    return f"Telegram status={r.status_code} | resp={r.text}", 200


# =========================
# WEBHOOK TRADINGVIEW
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    # Log brut (ULTRA IMPORTANT)
    raw = request.data.decode("utf-8", errors="replace")
    headers = dict(request.headers)

    print("===== TRADINGVIEW WEBHOOK =====")
    print("HEADERS:", headers)
    print("RAW BODY:", raw)
    print("===============================")

    # Parse JSON (sans crash)
    data = request.get_json(silent=True)

    # Construire message Telegram
    if isinstance(data, dict):
        text = (
            "📩 TradingView Alert\n"
            f"📊 Symbol: {data.get('symbol', '?')}\n"
            f"📌 Side: {data.get('side', '?')}\n"
            f"⏱ TF: {data.get('tf', '?')}\n"
            f"🎯 Entry: {data.get('entry', '?')}\n"
            f"🛑 SL: {data.get('sl', '?')}\n"
            f"✅ TP: {data.get('tp', '?')}\n"
            f"📏 SL pts: {data.get('sl_points', '?')}\n"
            f"📦 Qty: {data.get('qty', '?')}\n"
            f"⚠️ Risk%: {data.get('risk_pct', '?')}\n"
            f"📉 Daily DD%: {data.get('daily_dd_pct', '?')}"
        )
    else:
        # Si TradingView envoie du texte brut
        text = f"📩 TradingView RAW\n{raw}"

    # Vérification env vars
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Missing TELEGRAM_TOKEN or CHAT_ID")
        return jsonify({"ok": False}), 500

    # Envoi Telegram
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}

    try:
        r = requests.post(tg_url, json=payload, timeout=15)
        print("TELEGRAM STATUS:", r.status_code)
        print("TELEGRAM RESPONSE:", r.text)
    except Exception as e:
        print("❌ Telegram error:", str(e))
        return jsonify({"ok": False}), 500

    return jsonify({"ok": True}), 200


# =========================
# RUN (Render)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)

