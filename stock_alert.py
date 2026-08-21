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

    params = {
        "symbol": symbol,
        "token": FINNHUB_KEY
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    current_price = data.get("c")
    previous_close = data.get("pc")

    if not current_price or not previous_close:
        return

    change = ((current_price - previous_close) / previous_close) * 100

    if change >= 30:
        message = (
            "🚨 AANDEEL ALERT\n\n"
            f"{symbol} +{change:.1f}%\n"
            f"Koers: {current_price}\n"
            f"Vorige slotkoers: {previous_close}"
        )

        send_telegram(message)


# Eerste testlijst
stocks = [
    "ASML",
    "INGA",
    "PHIA",
    "ADYEN",
]

for stock in stocks:
    check_stock(stock)