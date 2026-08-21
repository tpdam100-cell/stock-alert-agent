import os
import requests

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
FINNHUB_KEY = os.environ["FINNHUB_API_KEY"]

# Aandelen die we voorlopig controleren
stocks = [
    # AEX
    "ASML",
    "ADYEN",
    "INGA",
    "PHIA",
    "HEIA",
    "UNA",
    "WKL",
    "PRX",
    "ASM",
    "BESI",

    # Grote Amerikaanse aandelen
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "META",
    "TSLA",
    "GOOGL",
    "AMD",
    "NFLX",
    "PLTR",
]


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        }
    )


def check_stock(symbol):

    url = "https://finnhub.io/api/v1/quote"

    params = {
        "symbol": symbol,
        "token": FINNHUB_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    current = data.get("c")
    previous = data.get("pc")

    if not current or not previous:
        return

    change = ((current - previous) / previous) * 100

    if change >= 30:

        message = (
            "🚨 AANDEEL ALERT\n\n"
            f"{symbol} is vandaag +{change:.1f}%\n\n"
            f"Koers: {current}\n"
            f"Vorige slotkoers: {previous}\n\n"
            "Bron: Finnhub"
        )

        send_telegram(message)


for stock in stocks:
    check_stock(stock)