from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# ⚠️ Mets ces valeurs dans Render > Environment (recommandé)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.getenv("CHAT_ID", "").strip()


@app.route("/", methods=["GET"])
def home():
    return "OK - TV webhook Telegram bot running", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    # 1) Log brut pour debug (indispensable)
    raw = request.data.decode("utf-8", errors="replace")
    headers = dict(request.headers)

    print("==== INCOMING WEBHOOK ====")
    print("HEADERS:", headers)
    print("RAW BODY:", raw)
    print("==========================")

    # 2) Parse JSON sans jamais planter
    data = request.get_json(silent=True)

    # 3) Construire un message robuste (JSON ou texte brut)
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
        # Si pas JSON, on envoie le body brut (utile pour diagnostiquer TradingView)
        text = f"📩 TradingView (RAW)\n{raw}"

    # 4) Vérifications de sécurité (évite erreurs silencieuses)
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Missing TELEGRAM_TOKEN or CHAT_ID environment variables.")
        return jsonify({"ok": False, "error": "Missing TELEGRAM_TOKEN or CHAT_ID"}), 500

    # 5) Envoi vers Telegram
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}

    try:
        r = requests.post(tg_url, json=payload, timeout=15)
        print("TELEGRAM STATUS:", r.status_code)
        print("TELEGRAM RESPONSE:", r.text)
    except Exception as e:
        print("❌ Telegram request failed:", str(e))
        return jsonify({"ok": False, "error": "Telegram request failed"}), 500

    # 6) Toujours répondre 200 à TradingView si on a traité la requête
    return jsonify({"ok": True}), 200


if __name__ == "__main__":
    # Render fournit PORT automatiquement
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)

