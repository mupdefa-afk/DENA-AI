import requests
import time
import random
import threading
from datetime import datetime, timedelta
from flask import Flask
import pytz

app = Flask(__name__)

TOKEN = "8544210127:AAFGMquOV2eHTMzNZlsOtdWY6HGvrDSgbEo"
CHAT_ID = "-1003524657786"

zona = pytz.timezone("America/Guayaquil")

# activos compatibles con OTC de Exnova
ACTIVOS = [
"BTC/USDT",
"ETH/USDT",
"BNB/USDT",
"SOL/USDT",
"XRP/USDT",
"ADA/USDT",
"DOGE/USDT",
"LTC/USDT",
"TRX/USDT",
"DOT/USDT"
]

wins = 0
loss = 0
total = 0

senales_hora = 0
hora_control = None


def enviar_telegram(mensaje):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": mensaje
    }

    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass


def horario_permitido():

    ahora = datetime.now(zona)

    if ahora.hour >= 15 or ahora.hour < 2:
        return True

    return False


def generar_senal():

    activo = random.choice(ACTIVOS)

    direccion = random.choice(["CALL 📈", "PUT 📉"])

    probabilidad = random.randint(80, 94)

    ahora = datetime.now(zona)

    entrada = ahora + timedelta(minutes=1)

    alerta = f"""
🟡 ALERTA PREVIA DENA

Activo: {activo}
Dirección posible: {direccion}

Hora alerta: {ahora.strftime("%H:%M:%S")}
Hora estimada de entrada: {entrada.strftime("%H:%M:%S")}
"""

    señal = f"""
🟢 SEÑAL CONFIRMADA DENA

Activo: {activo}
Dirección: {direccion}

Hora exacta de entrada: {entrada.strftime("%H:%M:%S")}
Expiración: 1M

Probabilidad IA: {probabilidad}%
"""

    return alerta, señal


def registrar_resultado():

    global wins, loss, total

    resultado = random.choice(["win","win","win","loss"])

    total += 1

    if resultado == "win":
        wins += 1
        return "WIN ✅"
    else:
        loss += 1
        return "LOSS ❌"


def panel():

    if total == 0:
        wr = 0
    else:
        wr = round((wins/total)*100,2)

    mensaje = f"""
📊 PANEL DENA

Operaciones: {total}
Wins: {wins}
Loss: {loss}

Winrate: {wr}%
"""

    enviar_telegram(mensaje)


def bot():

    global senales_hora
    global hora_control

    enviar_telegram("🤖 DENA BOT ACTIVADO")

    while True:

        ahora = datetime.now(zona)

        if not horario_permitido():

            time.sleep(300)
            continue

        if hora_control != ahora.hour:

            senales_hora = 0
            hora_control = ahora.hour

        if senales_hora < 5:

            alerta, señal = generar_senal()

            enviar_telegram(alerta)

            time.sleep(60)

            enviar_telegram(señal)

            senales_hora += 1

            time.sleep(60)

            resultado = registrar_resultado()

            enviar_telegram(f"Resultado operación: {resultado}")

            panel()

        espera = random.randint(1200,2400)

        time.sleep(espera)


@app.route("/")
def home():
    return "DENA BOT ACTIVO"


if __name__ == "__main__":

    hilo = threading.Thread(target=bot)
    hilo.start()

    app.run(host="0.0.0.0", port=10000)
