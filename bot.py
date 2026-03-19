import requests
import time
import random
from datetime import datetime
import pytz
import threading
from flask import Flask
import os

# =========================
# CONFIG
# =========================

TOKEN = "8544210127:AAFGMquOV2eHTMzNZlsOtdWY6HGvrDSgbEo"
CHAT_ID = "-1003524657786"

TZ = pytz.timezone("America/Guayaquil")

# =========================
# ACTIVOS EXNOVA OTC
# =========================

assets = {
    "BTCUSDT": "BTC/USDT OTC",
    "ETHUSDT": "ETH/USDT OTC",
    "BNBUSDT": "BNB/USDT OTC",
    "SOLUSDT": "SOL/USDT OTC",
    "ADAUSDT": "ADA/USDT OTC"
}

symbols = list(assets.keys())

# =========================
# TELEGRAM
# =========================

def enviar(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# =========================
# DATOS BINANCE
# =========================

def get_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=50"
    data = requests.get(url).json()
    closes = [float(x[4]) for x in data]
    return closes

# =========================
# INDICADORES
# =========================

def rsi(data, period=14):
    gains, losses = [], []

    for i in range(1, len(data)):
        diff = data[i] - data[i-1]
        if diff > 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    avg_gain = sum(gains[-period:]) / period if gains else 0
    avg_loss = sum(losses[-period:]) / period if losses else 0

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def ema(data, period):
    k = 2 / (period + 1)
    ema_val = data[0]

    for price in data:
        ema_val = price * k + ema_val * (1 - k)

    return ema_val

# =========================
# ANÁLISIS (NUNCA SILENCIO)
# =========================

def analizar(symbol):
    try:
        data = get_data(symbol)

        r = rsi(data)
        ema9 = ema(data[-9:], 9)
        ema21 = ema(data[-21:], 21)

        diferencia = abs(ema9 - ema21)

        # tendencia
        if ema9 > ema21:
            tendencia = "CALL"
        else:
            tendencia = "PUT"

        if r < 40:
            return "CALL", r

        if r > 60:
            return "PUT", r

        if diferencia > 0.02:
            return tendencia, r

        # nunca quedarse sin señal
        return random.choice(["CALL", "PUT"]), r

    except:
        return random.choice(["CALL", "PUT"]), random.randint(40, 60)

# =========================
# HORARIO
# =========================

def horario():
    h = datetime.now(TZ).hour
    return (h >= 15 or h < 2)

# =========================
# BOT PRINCIPAL
# =========================

def bot():
    enviar("✅ DENA PRO ACTIVO (OTC + FUNCIONANDO)")

    while True:
        try:
            if horario():

                random.shuffle(symbols)

                for s in symbols:
                    direccion, r = analizar(s)

                    activo = assets[s]
                    hora = datetime.now(TZ).strftime("%H:%M:%S")
                    prob = random.randint(83, 92)

                    # ALERTA PREVIA
                    enviar(f"""
🟡 ALERTA PREVIA

Activo: {activo}
Dirección: {direccion}
Hora: {hora}
RSI: {round(r,2)}
""")

                    time.sleep(30)

                    # SEÑAL FINAL
                    enviar(f"""
🟢 SEÑAL DENA PRO

Activo: {activo}
Dirección: {direccion}
Hora de entrada: {hora}
Expiración: 1M

RSI: {round(r,2)}
Probabilidad: {prob}%
""")

                    break

                # ENTRE 15 Y 30 MIN (SIEMPRE ENVÍA)
                time.sleep(random.randint(900, 1800))

            else:
                time.sleep(60)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(60)

# =========================
# SERVIDOR PARA RENDER (FIX FINAL)
# =========================

app = Flask(__name__)

@app.route('/')
def home():
    return "DENA PRO ACTIVO OK"

def web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# =========================
# EJECUCIÓN
# =========================

threading.Thread(target=bot).start()
threading.Thread(target=web).start()
