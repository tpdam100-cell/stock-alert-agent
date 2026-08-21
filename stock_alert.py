import os
import json
import requests
from datetime import datetime

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
FINNHUB_KEY = os.environ["FINNHUB_API_KEY"]

ALERT_FILE = "alerts.json"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        }
    )

    response.raise_for_status()


def load_alerts():
    try:
        with open(ALERT_FILE, "r") as file:
            return json.load(file)
    except:
        return {}


def save_alerts(alerts):
    with open(ALERT_FILE, "w") as file:
        json.dump(alerts, file, indent=2)


def check_stock(symbol, alerts):

    url = "https://finnhub.io/api/v1/quote"

    response = requests.get(
        url,
        params={
            "symbol": symbol,
            "token": FINNHUB_KEY
        }
    )

    response.raise_for_status()

    data = response.json()

    current = data.get("c")
    previous = data.get("pc")

    if not current or not previous:
        return

    change = ((current - previous) / previous) * 100

    print(f"{symbol}: {change:.2f}%")

    today = datetime.utcnow().strftime("%Y-%m-%d")

    if change >= 30:

        if alerts.get(symbol) == today:
            return

        message = (
            "🚨 AANDEEL ALERT\n\n"
            f"{symbol} +{change:.1f}% vandaag\n\n"
            f"Koers: {current}\n"
            f"Vorige slotkoers: {previous}"
        )

        send_telegram(message)

        alerts[symbol] = today


alerts = load_alerts()

with open("stocks.txt", "r") as file:
    stocks = [
        line.strip()
        for line in file
        if line.strip()
    ]

for symbol in stocks:
    check_stock(symbol, alerts)

save_alerts(alerts)