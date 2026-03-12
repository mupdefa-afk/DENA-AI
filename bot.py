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

symbols = [
"BTC/USDT","ETH/USDT","BNB/USDT","SOL/USDT","XRP/USDT",
"ADA/USDT","DOGE/USDT","AVAX/USDT","DOT/USDT","MATIC/USDT",
"LTC/USDT","LINK/USDT","ATOM/USDT","FIL/USDT","APT/USDT",
"ARB/USDT","OP/USDT","SAND/USDT","AAVE/USDT","NEAR/USDT"
]

registro = []

max_senales_hora = 5
contador_senales = 0
hora_actual = datetime.now().hour


def enviar(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=data)


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


def tendencia(df):

    ema50 = df["close"].ewm(span=50).mean()
    ema200 = df["close"].ewm(span=200).mean()

    if ema50.iloc[-1] > ema200.iloc[-1]:
        return "ALCISTA"
    else:
        return "BAJISTA"


def probabilidad(rsi_v, macd_v, signal_v, tendencia):

    score = 0

    if rsi_v < 30 or rsi_v > 70:
        score += 20

    if macd_v > signal_v:
        score += 20

    if tendencia == "ALCISTA":
        score += 20

    if abs(macd_v - signal_v) > 0:
        score += 20

    score += 20

    return score


def analizar(symbol):

    timeframe = "1m"

    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=200)

    df = pd.DataFrame(ohlcv, columns=["time", "open", "high", "low", "close", "volume"])

    df["RSI"] = rsi(df)

    macd_val, signal_val = macd(df)

    df["MACD"] = macd_val
    df["SIGNAL"] = signal_val

    tend = tendencia(df)

    rsi_v = df["RSI"].iloc[-1]
    macd_v = df["MACD"].iloc[-1]
    signal_v = df["SIGNAL"].iloc[-1]

    precio = df["close"].iloc[-1]

    prob = probabilidad(rsi_v, macd_v, signal_v, tend)

    señal = None

    if rsi_v < 30 and macd_v > signal_v and tend == "ALCISTA":
        señal = "CALL 🟢"

    if rsi_v > 70 and macd_v < signal_v and tend == "BAJISTA":
        señal = "PUT 🔴"

    if señal:

        return {
            "symbol": symbol,
            "precio": precio,
            "rsi": round(rsi_v, 2),
            "tendencia": tend,
            "probabilidad": prob,
            "senal": señal
        }

    return None


def mercado():

    global contador_senales, hora_actual

    while True:

        hora = datetime.now().hour

        if hora != hora_actual:
            contador_senales = 0
            hora_actual = hora

        if hora >= 15 or hora <= 2:

            if contador_senales < max_senales_hora:

                señales = []

                for s in symbols:

                    try:

                        resultado = analizar(s)

                        if resultado:
                            señales.append(resultado)

                    except:
                        pass

                if señales:

                    mejor = max(señales, key=lambda x: x["probabilidad"])

                    win = mejor["probabilidad"]
                    lose = 100 - win

                    mensaje = f"""

🚀 DENA PRO SIGNAL

Activo: {mejor["symbol"]}

Precio: {mejor["precio"]}

Tendencia: {mejor["tendencia"]}

RSI: {mejor["rsi"]}

Probabilidad ganar: {win}%
Probabilidad perder: {lose}%

Señal: {mejor["senal"]}

Tiempo sugerido: 1m
"""

                    enviar(mensaje)

                    registro.append(mejor)

                    contador_senales += 1

        time.sleep(60)


@app.route("/")
def home():
    return "DENA PRO ACTIVA"


threading.Thread(target=mercado).start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
