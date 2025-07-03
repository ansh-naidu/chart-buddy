import requests
import pandas as pd

def fetch_ohlc_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {"vs_currency": "usd", "days": "7", "interval": "hourly"}
        response = requests.get(url, params=params)
        data = response.json()

        prices = data["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df["open"] = df["price"]
        df["high"] = df["price"]
        df["low"] = df["price"]
        df["close"] = df["price"]
        df = df[["open", "high", "low", "close"]]
        return df
    except Exception as e:
        print("Data fetch error:", e)
        return None
