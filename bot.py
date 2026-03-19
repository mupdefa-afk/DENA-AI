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

assets = [
    "BTC/USDT OTC",
    "ETH/USDT OTC",
    "BNB/USDT OTC",
    "SOL/USDT OTC",
    "ADA/USDT OTC"
]

# =========================
# TELEGRAM
# =========================

def enviar(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        print("ENVIADO")
    except Exception as e:
        print("ERROR:", e)

# =========================
# HORARIO
# =========================

def horario():
    h = datetime.now(TZ).hour
    return (h >= 15 or h < 2)

# =========================
# GENERAR SEÑAL SIMPLE
# =========================

def generar_senal():
    activo = random.choice(assets)
    direccion = random.choice(["CALL 📈", "PUT 📉"])
    prob = random.randint(80, 90)
    hora = datetime.now(TZ).strftime("%H:%M:%S")
    return activo, direccion, prob, hora

# =========================
# BOT SIN BLOQUEOS
# =========================

def bot():
    enviar("✅ DENA ACTIVO (SIN BLOQUEOS)")

    while True:
        try:
            if horario():

                activo, direccion, prob, hora = generar_senal()

                enviar(f"""
🟡 ALERTA PREVIA

Activo: {activo}
Dirección: {direccion}
Hora: {hora}
""")

                time.sleep(15)

                enviar(f"""
🟢 SEÑAL DENA

Activo: {activo}
Dirección: {direccion}
Hora: {hora}
Expiración: 1M

Probabilidad: {prob}%
""")

                # 🔥 CLAVE: intervalo corto SIEMPRE
                for _ in range(300):  # 5 minutos en segundos
                    time.sleep(1)

            else:
                time.sleep(30)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(10)

# =========================
# SERVIDOR
# =========================

app = Flask(__name__)

@app.route('/')
def home():
    return "BOT ACTIVO"

def web():
    app.run(host="0.0.0.0", port=10000)

# =========================
# EJECUCIÓN SEGURA
# =========================

threading.Thread(target=bot, daemon=True).start()
threading.Thread(target=web, daemon=True).start()
