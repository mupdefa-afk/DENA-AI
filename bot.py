import requests
import schedule
import time
import pandas as pd
import ccxt
import ta

TOKEN = "TU_TOKEN"
CHAT_ID = "-1003524657786"

exchange = ccxt.binance()

def get_data():

    bars = exchange.fetch_ohlcv("BTC/USDT","1m",limit=100)

    df = pd.DataFrame(
        bars,
        columns=["time","open","high","low","close","volume"]
    )

    return df


def indicators(df):

    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()

    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    df["ema20"] = ta.trend.EMAIndicator(df["close"],window=20).ema_indicator()
    df["ema50"] = ta.trend.EMAIndicator(df["close"],window=50).ema_indicator()

    return df


def strategy(df):

    last = df.iloc[-1]

    if last["rsi"] < 30 and last["macd"] > last["macd_signal"]:
        return "BUY"

    if last["rsi"] > 70 and last["macd"] < last["macd_signal"]:
        return "SELL"

    return None


def send_signal():

    df = get_data()
    df = indicators(df)

    signal = strategy(df)

    if signal:

        message = f"""
🚨 DENA SIGNAL

Asset: BTC/USDT
Signal: {signal}
Timeframe: 1m
"""

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        data = {
            "chat_id": CHAT_ID,
            "text": message
        }

        requests.post(url,data=data)


schedule.every(1).minutes.do(send_signal)

while True:
    schedule.run_pending()
    time.sleep(1)
