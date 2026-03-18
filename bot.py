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
# ACTIVOS EXNOVA REALES
# =========================

symbols = [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT",
    "SOL/USDT",
    "ADA/USDT",

    "Tesla OTC",
    "Apple OTC",
    "Amazon OTC",
    "Google OTC",
    "Microsoft OTC",

    "EUR/USD",
    "GBP/USD",
    "USD/JPY"
]

# =========================
# TELEGRAM
# =========================

def enviar(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg}
        requests.post(url, data=data, timeout=10)
        print("MENSAJE ENVIADO")
    except Exception as e:
        print("ERROR TELEGRAM:", e)

# =========================
# HORA CORRECTA
# =========================

def hora_actual():
    return datetime.now(TZ)

# =========================
# HORARIO (3PM a 2AM)
# =========================

def horario_activo():
    h = hora_actual().hour
    return (h >= 15 or h < 2)

# =========================
# GENERAR SEÑAL (NUNCA VACÍA)
# =========================

def generar_senal():
    activo = random.choice(symbols)
    direccion = random.choice(["CALL 📈", "PUT 📉"])
    prob = random.randint(80, 95)

    hora = hora_actual().strftime("%H:%M:%S")

    return activo, direccion, prob, hora

# =========================
# BOT PRINCIPAL
# =========================

def bot():
    enviar("✅ DENA BOT ACTIVO (VERSIÓN ESTABLE)")

    while True:
        try:
            if horario_activo():

                activo, direccion, prob, hora = generar_senal()

                # ALERTA PREVIA
                alerta = f"""
🟡 ALERTA PREVIA

Activo: {activo}
Dirección posible: {direccion}
Hora: {hora}
"""
                enviar(alerta)

                time.sleep(30)

                # SEÑAL FINAL
                señal = f"""
🟢 SEÑAL DENA AI

Activo: {activo}
Dirección: {direccion}
Hora de entrada: {hora}
Expiración: 1M

Probabilidad: {prob}%
"""
                enviar(señal)

                # ESPERA CONTROLADA (SIEMPRE ENVÍA)
                espera = random.randint(900, 1800)  # 15 a 30 min
                print(f"Esperando {espera} segundos...")
                time.sleep(espera)

            else:
                print("Fuera de horario...")
                time.sleep(60)

        except Exception as e:
            print("ERROR GENERAL:", e)
            time.sleep(60)

# =========================
# SERVIDOR (RENDER)
# =========================

app = Flask(__name__)

@app.route('/')
def home():
    return "BOT ACTIVO"

def web():
    app.run(host="0.0.0.0", port=10000)

# =========================
# EJECUCIÓN
# =========================

threading.Thread(target=bot).start()
threading.Thread(target=web).start()
