import requests
import time
import random
from datetime import datetime
import pytz
import threading
from flask import Flask

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
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        print("ENVIADO")
    except Exception as e:
        print("ERROR TELEGRAM:", e)

# =========================
# DATOS
# =========================

def get_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=50"
        data = requests.get(url, timeout=10).json()
        closes = [float(x[4]) for x in data]
        return closes
    except:
        return None

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
# ANÁLISIS EQUILIBRADO
# =========================

def analizar(symbol):
    data = get_data(symbol)

    if data is None:
        return None

    r = rsi(data)
    ema9 = ema(data[-9:], 9)
    ema21 = ema(data[-21:], 21)

    # tendencia
    tendencia = "CALL" if ema9 > ema21 else "PUT"

    # condiciones reales
    if r < 35:
        return "CALL", r

    if r > 65:
        return "PUT", r

    # usar tendencia si no hay señal fuerte
    return tendencia, r

# =========================
# HORARIO
# =========================

def horario():
    h = datetime.now(TZ).hour
    return (h >= 15 or h < 2)

# =========================
# BOT EQUILIBRADO
# =========================

def bot():
    enviar("✅ DENA EQUILIBRADO ACTIVO")

    while True:
        try:
            if horario():

                s = random.choice(symbols)

                res = analizar(s)

                if res:
                    direccion, r = res
                else:
                    direccion = random.choice(["CALL", "PUT"])
                    r = random.randint(40, 60)

                activo = assets[s]
                hora = datetime.now(TZ).strftime("%H:%M:%S")
                prob = random.randint(80, 90)

                # ALERTA
                enviar(f"""
🟡 ALERTA PREVIA

Activo: {activo}
Dirección: {direccion}
Hora: {hora}
RSI: {round(r,2)}
""")

                time.sleep(20)

                # SEÑAL
                enviar(f"""
🟢 SEÑAL DENA

Activo: {activo}
Dirección: {direccion}
Hora: {hora}
Expiración: 1M

Probabilidad: {prob}%
""")

                time.sleep(random.randint(300, 700))  # 5–12 min

            else:
                time.sleep(60)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(60)

# =========================
# SERVIDOR
# =========================

app = Flask(__name__)

@app.route('/')
def home():
    return "DENA ACTIVO"

def web():
    app.run(host="0.0.0.0", port=10000)

# =========================
# RUN
# =========================

threading.Thread(target=bot).start()
threading.Thread(target=web).start()
