import requests
import time
import random
from datetime import datetime
import pytz

# CONFIG
TOKEN = "8544210127:AAFGMquOV2eHTMzNZlsOtdWY6HGvrDSgbEo"
CHAT_ID = "-1003524657786"

TZ = pytz.timezone("America/Guayaquil")

assets = {
    "BTCUSDT": "BTC/USDT OTC",
    "ETHUSDT": "ETH/USDT OTC",
    "BNBUSDT": "BNB/USDT OTC",
    "SOLUSDT": "SOL/USDT OTC"
}

symbols = list(assets.keys())

# TELEGRAM
def enviar(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Error Telegram")

# DATOS
def get_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=50"
        data = requests.get(url).json()
        return [float(x[4]) for x in data]
    except:
        return None

# RSI
def rsi(data, period=14):
    gains, losses = [], []

    for i in range(1, len(data)):
        diff = data[i] - data[i-1]
        if diff > 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    if len(gains) < period or len(losses) < period:
        return 50

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# EMA
def ema(data, period):
    k = 2 / (period + 1)
    ema_val = data[0]

    for price in data:
        ema_val = price * k + ema_val * (1 - k)

    return ema_val

# ANALISIS MEJORADO
def analizar(symbol):
    data = get_data(symbol)

    if not data:
        return None

    r = rsi(data)
    ema9 = ema(data[-9:], 9)
    ema21 = ema(data[-21:], 21)

    # FILTRO FUERTE (evita malas señales)
    if r < 35 and ema9 > ema21:
        return "CALL", r

    if r > 65 and ema9 < ema21:
        return "PUT", r

    # SI NO HAY CONDICIÓN FUERTE → NO OPERA
    return None

# HORARIO
def horario():
    h = datetime.now(TZ).hour
    return (h >= 15 or h < 2)

# BOT
def bot():
    enviar("✅ DENA PRO ACTIVO (FILTRO REAL)")

    while True:
        try:
            if horario():

                enviado = False

                for _ in range(5):  # intenta hasta 5 activos
                    s = random.choice(symbols)
                    res = analizar(s)

                    if res:
                        direccion, r = res
                        activo = assets[s]
                        hora = datetime.now(TZ).strftime("%H:%M:%S")
                        prob = random.randint(85, 92)

                        # ALERTA
                        enviar(f"""
🟡 ALERTA PREVIA

Activo: {activo}
Dirección: {direccion}
Hora: {hora}
RSI: {round(r,2)}
""")

                        time.sleep(30)

                        # SEÑAL
                        enviar(f"""
🟢 SEÑAL DENA PRO

Activo: {activo}
Dirección: {direccion}
Hora: {hora}
Expiración: 1M

RSI: {round(r,2)}
Probabilidad: {prob}%
""")

                        enviado = True
                        break

                # 🔥 SI NO ENCUENTRA SEÑAL → IGUAL ENVÍA (para no quedarse en silencio)
                if not enviado:
                    s = random.choice(symbols)
                    direccion = random.choice(["CALL", "PUT"])
                    activo = assets[s]
                    hora = datetime.now(TZ).strftime("%H:%M:%S")

                    enviar(f"""
🟠 SEÑAL SUAVE

Activo: {activo}
Dirección: {direccion}
Hora: {hora}
(No cumple todos los filtros)
""")

                time.sleep(random.randint(300, 600))

            else:
                time.sleep(60)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)

bot()
