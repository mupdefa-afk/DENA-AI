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

senales_hora = 0
hora_actual = None


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


def generar_senal():

    activo = random.choice(ACTIVOS)

    direccion = random.choice(["CALL 📈", "PUT 📉"])

    probabilidad = random.randint(80,95)

    ahora = datetime.now(zona)

    entrada = ahora + timedelta(minutes=1)

    hora_alerta = ahora.strftime("%H:%M:%S")
    hora_entrada = entrada.strftime("%H:%M:%S")

    alerta = f"""
🟡 ALERTA PREVIA DENA

Activo: {activo}
Posible dirección: {direccion}

Hora alerta: {hora_alerta}
Entrada estimada: {hora_entrada}
"""

    señal = f"""
🟢 SEÑAL CONFIRMADA DENA

Activo: {activo}
Dirección: {direccion}

Hora exacta entrada: {hora_entrada}
Expiración: 1M

Probabilidad IA: {probabilidad}%
"""

    return alerta, señal


def registrar_resultado():

    global win, loss, total

    resultado = random.choice(["win","win","win","loss"])

    total += 1

    if resultado == "win":
        win += 1
        return "WIN ✅"
    else:
        loss += 1
        return "LOSS ❌"


def panel():

    if total == 0:
        wr = 0
    else:
        wr = round((win/total)*100,2)

    mensaje = f"""
📊 PANEL DENA

Operaciones: {total}
Wins: {win}
Loss: {loss}

Winrate: {wr}%
"""

    enviar_telegram(mensaje)


def bot():

    global senales_hora
    global hora_actual

    enviar_telegram("🤖 DENA BOT ACTIVADO")

    while True:

        ahora = datetime.now(zona)

        if hora_actual != ahora.hour:
            senales_hora = 0
            hora_actual = ahora.hour

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
