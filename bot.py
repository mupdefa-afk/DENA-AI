import requests
import pandas as pd
import ta
import schedule
import time
from flask import Flask
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "DENA AI funcionando"

def run_web():
    app.run(host="0.0.0.0", port=10000)
TOKEN = "8544210127:AAGefu7tMGkhVH6-z4YA4v0JN9DcATtTs5Jo"
CHAT_ID = "-1002148392748"

symbol = "bitcoin"

def obtener_precio():

    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=usd&days=1"

    data = requests.get(url).json()

    precios = [p[1] for p in data["prices"]]

    df = pd.DataFrame(precios, columns=["close"])

    return df


def analizar():

    df = obtener_precio()

    df["ema9"] = ta.trend.ema_indicator(df["close"], window=9)
    df["ema21"] = ta.trend.ema_indicator(df["close"], window=21)

    df["rsi"] = ta.momentum.rsi(df["close"], window=14)

    ema9 = df["ema9"].iloc[-1]
    ema21 = df["ema21"].iloc[-1]
    rsi = df["rsi"].iloc[-1]

    señal = "SIN SEÑAL"

    if ema9 > ema21 and rsi > 55:
        señal = "🟢 CALL"

    elif ema9 < ema21 and rsi < 45:
        señal = "🔴 PUT"

    return señal, rsi


def enviar_telegram(texto):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": texto
    }

    requests.post(url, data=data)


def ejecutar():

    señal, rsi = analizar()

    mensaje = f"""
🤖 DENA PRO SIGNAL

Activo: BTC
Temporalidad: 1M

Señal: {señal}
RSI: {round(rsi,2)}

Plataforma: EXNOVA
"""

    enviar_telegram(mensaje)


schedule.every(1).minutes.do(ejecutar)

threading.Thread(target=run_web).start()

while True:
    schedule.run_pending()
    time.sleep(1)
    time.sleep(1)
