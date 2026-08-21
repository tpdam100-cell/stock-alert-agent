import os
import requests

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
FINNHUB_KEY = os.environ["FINNHUB_API_KEY"]


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


def check_stock(symbol):
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

    if change >= 30:
        send_telegram(
            f"🚨 AANDEEL ALERT\n\n"
            f"{symbol} +{change:.1f}% vandaag\n\n"
            f"Koers: {current}\n"
            f"Vorige slotkoers: {previous}"
        )


# Testaandelen
stocks = [
    "ASML",
    "NVDA"
]

for symbol in stocks:
    check_stock(symbol)