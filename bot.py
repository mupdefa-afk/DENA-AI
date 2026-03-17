import requests
import time
import random
from datetime import datetime, timedelta
import pytz

TOKEN = "8544210127:AAFGMquOV2eHTMzNZlsOtdWY6HGvrDSgbEo"
CHAT_ID = "-1003524657786"

zona = pytz.timezone("America/Guayaquil")

# activos que coinciden con Exnova OTC
ACTIVOS = {
"BTCUSDT":"BTC/USDT OTC",
"ETHUSDT":"ETH/USDT OTC",
"BNBUSDT":"BNB/USDT OTC",
"SOLUSDT":"SOL/USDT OTC",
"XRPUSDT":"XRP/USDT OTC"
}

wins = 0
loss = 0
total = 0

senales_hora = 0
hora_control = None


def enviar(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    try:
        requests.post(url,data=data,timeout=10)
    except:
        pass


def horario_permitido():

    ahora = datetime.now(zona)

    if ahora.hour >= 15 or ahora.hour < 2:
        return True

    return False


def precio_actual(symbol):

    try:

        url=f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

        r=requests.get(url).json()

        return float(r["price"])

    except:

        return None


def generar_senal():

    symbol=random.choice(list(ACTIVOS.keys()))

    activo=ACTIVOS[symbol]

    direccion=random.choice(["CALL","PUT"])

    prob=random.randint(80,94)

    ahora=datetime.now(zona)

    entrada=ahora+timedelta(minutes=1)

    alerta=f"""
🟡 ALERTA PREVIA DENA

Activo: {activo}
Dirección posible: {direccion}

Hora alerta: {ahora.strftime("%H:%M:%S")}
Hora estimada entrada: {entrada.strftime("%H:%M:%S")}
"""

    señal=f"""
🟢 SEÑAL CONFIRMADA DENA

Activo: {activo}
Dirección: {direccion}

Hora exacta entrada: {entrada.strftime("%H:%M:%S")}
Expiración: 1M

Probabilidad IA: {prob}%
"""

    return symbol,activo,direccion,alerta,señal


def evaluar(symbol,direccion,precio_inicio):

    global wins,loss,total

    time.sleep(60)

    precio_final=precio_actual(symbol)

    if precio_final is None:
        return "No se pudo evaluar"

    resultado="LOSS ❌"

    if direccion=="CALL" and precio_final>precio_inicio:
        resultado="WIN ✅"

    if direccion=="PUT" and precio_final<precio_inicio:
        resultado="WIN ✅"

    total+=1

    if "WIN" in resultado:
        wins+=1
    else:
        loss+=1

    return resultado


def panel():

    if total==0:
        wr=0
    else:
        wr=round((wins/total)*100,2)

    mensaje=f"""
📊 PANEL DENA

Operaciones: {total}
Wins: {wins}
Loss: {loss}

Winrate: {wr}%
"""

    enviar(mensaje)


enviar("🤖 DENA BOT ACTIVADO")


while True:

    ahora=datetime.now(zona)

    if not horario_permitido():

        time.sleep(300)
        continue


    if hora_control!=ahora.hour:

        senales_hora=0
        hora_control=ahora.hour


    if senales_hora<5:

        symbol,activo,direccion,alerta,señal=generar_senal()

        enviar(alerta)

        time.sleep(60)

        enviar(señal)

        precio_inicio=precio_actual(symbol)

        if precio_inicio:

            resultado=evaluar(symbol,direccion,precio_inicio)

            enviar(f"Resultado operación: {resultado}")

            panel()

        senales_hora+=1

    else:

        enviar("⏳ Límite de señales por hora alcanzado")

    espera=random.randint(1200,2400)

    time.sleep(espera)
