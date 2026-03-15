import requests
import time
import random
from datetime import datetime
from flask import Flask

app = Flask(__name__)

# =========================
# CONFIGURACIÓN
# =========================

TOKEN = "8544210127:AAFGMquOV2eHTMzNZlsOtdWY6HGvrDSgbEo"
CHAT_ID = "-1003524657786"

ACTIVOS = [
"BTC/USDT",
"ETH/USDT",
"SOL/USDT",
"BNB/USDT",
"XRP/USDT"
]

win = 0
loss = 0
total = 0

# =========================
# TELEGRAM
# =========================

def enviar_telegram(mensaje):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": mensaje
    }

    try:
        requests.post(url, data=data)
    except:
        pass


# =========================
# GENERADOR DE SEÑALES
# =========================

def generar_senal():

    activo = random.choice(ACTIVOS)

    direccion = random.choice(["CALL 📈", "PUT 📉"])

    probabilidad = random.randint(80,95)

    ahora = datetime.now()

    hora = ahora.strftime("%H:%M")

    señal = f"""
🚨 SEÑAL DENA AI

Activo: {activo}
Dirección: {direccion}
Hora de entrada: {hora}
Expiración: 1M

Probabilidad IA: {probabilidad}%

Prepárate para operar.
"""

    return señal


# =========================
# REGISTRO RESULTADOS
# =========================

def registrar_resultado():

    global win, loss, total

    resultado = random.choice(["win","loss","win","win"])

    total += 1

    if resultado == "win":
        win += 1
        return "WIN ✅"
    else:
        loss += 1
        return "LOSS ❌"


# =========================
# PANEL DE ESTADÍSTICAS
# =========================

def panel():

    if total == 0:
        wr = 0
    else:
        wr = round((win/total)*100,2)

    panel = f"""
📊 PANEL DENA AI

Operaciones: {total}
Wins: {win}
Loss: {loss}

Winrate: {wr}%
"""

    enviar_telegram(panel)


# =========================
# BOT LOOP
# =========================

def bot():

    enviar_telegram("🤖 DENA AI ACTIVADO")

    while True:

        señales_hora = random.randint(1,3)

        for i in range(señales_hora):

            señal = generar_senal()

            enviar_telegram(señal)

            time.sleep(60)

            resultado = registrar_resultado()

            enviar_telegram(f"Resultado operación: {resultado}")

            time.sleep(60)

        panel()

        time.sleep(3600)


# =========================
# SERVIDOR RENDER
# =========================

@app.route("/")
def home():
    return "DENA AI ACTIVO"


if __name__ == "__main__":
    import threading

    hilo = threading.Thread(target=bot)
    hilo.start()

    app.run(host="0.0.0.0", port=10000)
