from flask import Flask, request
import os, requests, math

app = Flask(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID   = os.environ["CHAT_ID"]

EQUITY     = float(os.environ.get("EQUITY", "100000"))
RISK_PCT   = float(os.environ.get("RISK_PCT", "1.0"))
POINTVALUE = float(os.environ.get("POINTVALUE", "1.0"))
ROUNDSTEP  = float(os.environ.get("ROUNDSTEP", "1.0"))

def send(msg: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

@app.post("/tv")
def tv():
    data = request.get_json(force=True)

    symbol   = data.get("symbol", "UNKNOWN")
    side     = data.get("side", "UNKNOWN")
    tf       = data.get("tf", "")
    entry    = float(data.get("entry"))
    sl       = float(data.get("sl"))
    tp       = float(data.get("tp"))
    sl_pts   = float(data.get("sl_points"))
    tv_qty   = float(data.get("qty", 0))
    dailydd  = float(data.get("daily_dd_pct", 0))

    risk_amount = EQUITY * (RISK_PCT / 100.0)
    denom = max(sl_pts * POINTVALUE, 1e-9)
    qty = risk_amount / denom

    step = max(ROUNDSTEP, 1e-9)
    qty = max(qty, step)
    qty = math.floor(qty / step) * step

    msg = (
        f"📌 {symbol} {side} ({tf})\n"
        f"Entry: {entry:.2f}\n"
        f"SL: {sl:.2f} ({sl_pts:.2f} pts)\n"
        f"TP: {tp:.2f}\n"
        f"Equity: {EQUITY:.0f} | Risk: {RISK_PCT:.2f}% | DailyDD: {dailydd:.2f}%\n"
        f"➡️ SIZE (bot): {qty} contrats\n"
        f"(TV qty: {tv_qty})"
    )
    send(msg)
    return {"ok": True}

@app.get("/")
def home():
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
