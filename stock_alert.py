import os
import json
import requests
from datetime import datetime, timezone

# ============================================================
# INSTELLINGEN
# ============================================================

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ALPHA_KEY = os.environ["ALPHAVANTAGE_API_KEY"]

ALERT_FILE = "alerts.json"

MIN_CHANGE = 30.0
MIN_PRICE = 1.0


# ============================================================
# TELEGRAM
# ============================================================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=30
    )

    response.raise_for_status()


# ============================================================
# ALERT-GESCHIEDENIS
# ============================================================

def load_alerts():

    try:
        with open(ALERT_FILE, "r") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_alerts(alerts):

    with open(ALERT_FILE, "w") as file:
        json.dump(alerts, file, indent=2)


# ============================================================
# ALPHA VANTAGE - TOP GAINERS
# ============================================================

def get_us_top_gainers():

    url = "https://www.alphavantage.co/query"

    params = {
        "function": "TOP_GAINERS_LOSERS",
        "apikey": ALPHA_KEY
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if "Note" in data:
        print("Alpha Vantage API-limiet bereikt:")
        print(data["Note"])
        return []

    if "Information" in data:
        print("Alpha Vantage informatie:")
        print(data["Information"])
        return []

    return data.get("top_gainers", [])


# ============================================================
# CONTROLE OF HET EEN NORMAAL AANDEEL IS
# ============================================================

def is_normal_stock(symbol):

    symbol = symbol.upper()

    # Warrants
    if symbol.endswith("W"):
        return False

    # Units
    if symbol.endswith("U"):
        return False

    # Rights
    if symbol.endswith("R"):
        return False

    # Sommige warrant-symbolen gebruiken +
    if "+" in symbol:
        return False

    return True


# ============================================================
# AANDEEL CONTROLEREN
# ============================================================

def process_stock(
    symbol,
    price,
    change,
    alerts,
    today
):

    if not symbol:
        return

    # Geen warrants/units/rights
    if not is_normal_stock(symbol):

        print(
            f"OVERGESLAGEN - geen normaal aandeel: "
            f"{symbol}"
        )

        return

    try:
        price_value = float(price)
        change_value = float(
            str(change).replace("%", "")
        )

    except (ValueError, TypeError):

        print(
            f"OVERGESLAGEN - ongeldige data: "
            f"{symbol}"
        )

        return

    # Penny stocks onder $1 overslaan
    if price_value < MIN_PRICE:

        print(
            f"OVERGESLAGEN - koers onder $1: "
            f"{symbol} ${price_value}"
        )

        return

    print(
        f"{symbol}: "
        f"+{change_value:.2f}% "
        f"(${price_value:.2f})"
    )

    # Alleen +30%
    if change_value < MIN_CHANGE:
        return

    # Vandaag al gemeld?
    if alerts.get(symbol) == today:

        print(
            f"ALREADY ALERTED TODAY: {symbol}"
        )

        return

    # Telegrambericht
    message = (
        "🚨 AANDEEL ALERT\n\n"
        f"📈 {symbol} +{change_value:.1f}%\n\n"
        f"💵 Koers: ${price_value:.2f}\n\n"
        "🇺🇸 Amerikaanse markt\n"
        "Bron: Alpha Vantage"
    )

    send_telegram(message)

    # Opslaan dat dit aandeel vandaag gemeld is
    alerts[symbol] = today

    print(
        f"TELEGRAM ALERT SENT: {symbol}"
    )


# ============================================================
# HOOFDPROGRAMMA
# ============================================================

def main():

    print("====================================")
    print("STOCK ALERT SCANNER")
    print("====================================")

    today = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    print(f"Datum: {today}")
    print()

    alerts = load_alerts()

    print("Top gainers ophalen...")
    print()

    gainers = get_us_top_gainers()

    print(
        f"Aantal ontvangen top gainers: "
        f"{len(gainers)}"
    )

    print()

    for stock in gainers:

        symbol = stock.get("ticker")
        price = stock.get("price")
        change = stock.get("change_percentage")

        process_stock(
            symbol,
            price,
            change,
            alerts,
            today
        )

    save_alerts(alerts)

    print()
    print("====================================")
    print("SCAN KLAAR")
    print("====================================")


if __name__ == "__main__":
    main()