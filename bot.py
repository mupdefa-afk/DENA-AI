import requests
import time
import random
from datetime import datetime
import pytz

TOKEN = "8544210127:AAFGMquOV2eHTMzNZlsOtdWY6HGvrDSgbEo"
CHAT_ID = "-1003524657786"

zona = pytz.timezone("America/Guayaquil")

ACTIVOS = [
"BTC/USDT",
"ETH/USDT",
"BNB/USDT",
"SOL/USDT",
"XRP/USDT"
]

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data)
    except:
        pass

enviar("🤖 BOT DENA INICIADO")

while True:

    ahora = datetime.now(zona)

    activo = random.choice(ACTIVOS)

    direccion = random.choice(["CALL 📈","PUT 📉"])

    mensaje = f"""
SEÑAL DENA AI

Activo: {activo}
Dirección: {direccion}

Hora: {ahora.strftime("%H:%M:%S")}
Expiración: 1M
"""

    enviar(mensaje)

    time.sleep(300)
