import os
import json
import requests
from datetime import datetime

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ALPHA_KEY = os.environ["ALPHAVANTAGE_API_KEY"]

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


def get_top_gainers():

    url = "https://www.alphavantage.co/query"

    params = {
        "function": "TOP_GAINERS_LOSERS",
        "apikey": ALPHA_KEY
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    if "top_gainers" not in data:
        print("Geen top gainers ontvangen.")
        print(data)
        return []

    return data["top_gainers"]


def check_gainers():

    alerts = load_alerts()

    today = datetime.utcnow().strftime("%Y-%m-%d")

    gainers = get_top_gainers()

    for stock in gainers:

        symbol = stock.get("ticker")
        price = stock.get("price")
        change = stock.get("change_percentage")
            
        if not symbol or not change:
    continue

# Warrants, units, rights en vergelijkbare instrumenten uitsluiten
if (
    symbol.endswith("W")
    or symbol.endswith("U")
    or symbol.endswith("R")
    or "+" in symbol
):
    print(f"Overgeslagen (geen gewoon aandeel): {symbol}")
    continue

        try:
            change_value = float(
                change.replace("%", "")
            )
        except:
            continue

        print(f"{symbol}: {change_value}%")

        if change_value >= 30:

            if alerts.get(symbol) == today:
                continue

            message = (
                "🚨 AANDEEL ALERT\n\n"
                f"{symbol} +{change_value:.1f}% vandaag\n\n"
                f"Koers: {price}\n\n"
                "Bron: Alpha Vantage"
            )

            send_telegram(message)

            alerts[symbol] = today

    save_alerts(alerts)


check_gainers()