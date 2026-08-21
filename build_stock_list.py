import requests

URL = "https://www.alphavantage.co/query"

# Voorlopig gebruiken we de lijst die al in stocks.txt staat.
# In de volgende stap vervangen we dit door een automatische
# Nasdaq/NYSE/AEX-lijst.

print("Stock list builder gestart.")

with open("stocks.txt", "r") as file:
    stocks = [
        line.strip()
        for line in file
        if line.strip()
    ]

print(f"Aantal aandelen: {len(stocks)}")

for stock in stocks:
    print(stock)