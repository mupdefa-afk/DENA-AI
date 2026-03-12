import ccxt
import pandas as pd
import requests
import time
import threading
from flask import Flask
from datetime import datetime

TOKEN = "8544210127:AAEBmSGLnSutz5bMzz7Hij-R00GhVAEWkZ0"
CHAT_ID = "-1003524657786"

exchange = ccxt.kraken()

app = Flask(__name__)

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    requests.post(url, data=data)

# mensaje de prueba
enviar("DENA BOT ACTIVADO")

symbols = [
"BTC/USDT","ETH/USDT","BNB/USDT","SOL/USDT","XRP/USDT",
"ADA/USDT","DOGE/USDT","AVAX/USDT","DOT/USDT","MATIC/USDT"
]

def rsi(df, periodo=14):

    delta = df["close"].diff()

    subida = delta.clip(lower=0)
    bajada = -delta.clip(upper=0)

    media_subida = subida.rolling(periodo).mean()
    media_bajada = bajada.rolling(periodo).mean()

    rs = media_subida / media_bajada

    rsi = 100 - (100 / (1 + rs))

    return rsi


def macd(df):

    ema12 = df["close"].ewm(span=12).mean()
    ema26 = df["close"].ewm(span=26).mean()

    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()

    return macd, signal


def analizar(symbol):

    data = exchange.fetch_ohlcv(symbol, "1m", limit=200)

    df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])

    df["RSI"] = rsi(df)

    macd_val, signal_val = macd(df)

    rsi_v = df["RSI"].iloc[-1]

    macd_v = macd_val.iloc[-1]
    signal_v = signal_val.iloc[-1]

    precio = df["close"].iloc[-1]

    if rsi_v < 30 and macd_v > signal_v:

        mensaje = f"""
DENA SIGNAL

Activo: {symbol}

Precio: {precio}

RSI: {round(rsi_v,2)}

Señal: CALL 🟢
Tiempo: 1m
"""

        enviar(mensaje)


def mercado():

    while True:

        for s in symbols:

            try:
                analizar(s)
            except:
                pass

        time.sleep(60)


@app.route("/")
def home():
    return "DENA ACTIVA"


threading.Thread(target=mercado).start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
