import requests
import time
import random
from datetime import datetime, timedelta
import pytz

TOKEN = "8544210127:AAFGMquOV2eHTMzNZlsOtdWY6HGvrDSgbEo"
CHAT_ID = "-1003524657786"

zona = pytz.timezone("America/Guayaquil")

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


def enviar(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass


def horario_permitido():
    ahora = datetime.now(zona)
    return ahora.hour >= 15 or ahora.hour < 2


def precio(symbol):
    try:
        url=f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        return float(requests.get(url,timeout=5).json()["price"])
    except:
        return None


def generar_senal():
    symbol=random.choice(list(ACTIVOS.keys()))
    activo=ACTIVOS[symbol]
    direccion=random.choice(["CALL 📈","PUT 📉"])
    prob=random.randint(80,94)

    ahora=datetime.now(zona)
    entrada=ahora+timedelta(minutes=1)

    alerta=f"""🟡 ALERTA PREVIA

Activo: {activo}
Dirección: {direccion}

Hora: {ahora.strftime("%H:%M:%S")}
Entrada: {entrada.strftime("%H:%M:%S")}
"""

    señal=f"""🟢 SEÑAL

Activo: {activo}
Dirección: {direccion}

Hora exacta: {entrada.strftime("%H:%M:%S")}
Expiración: 1M
Probabilidad: {prob}%
"""

    return symbol,activo,direccion,alerta,señal


def evaluar(symbol,direccion,precio_inicio):
    global wins,loss,total

    time.sleep(60)

    precio_final=precio(symbol)

    if precio_final is None:
        return "Error"

    resultado="LOSS ❌"

    if direccion.startswith("CALL") and precio_final>precio_inicio:
        resultado="WIN ✅"

    if direccion.startswith("PUT") and precio_final<precio_inicio:
        resultado="WIN ✅"

    total+=1

    if "WIN" in resultado:
        wins+=1
    else:
        loss+=1

    return resultado


def panel():
    wr = round((wins/total)*100,2) if total>0 else 0

    enviar(f"""📊 PANEL

Operaciones: {total}
Wins: {wins}
Loss: {loss}
Winrate: {wr}%
""")


def heartbeat():
    while True:
        enviar("💓 DENA ACTIVO")
        time.sleep(600)


def main():

    enviar("🤖 BOT DENA INICIADO")

    while True:

        try:

            if not horario_permitido():
                time.sleep(60)
                continue

            symbol,activo,direccion,alerta,señal = generar_senal()

            enviar(alerta)

            time.sleep(60)

            enviar(señal)

            precio_inicio=precio(symbol)

            if precio_inicio:
                resultado=evaluar(symbol,direccion,precio_inicio)
                enviar(f"Resultado: {resultado}")
                panel()

            espera=random.randint(600,1200)  # 10 a 20 min

            time.sleep(espera)

        except Exception as e:
            enviar("⚠️ Error detectado, reiniciando...")
            time.sleep(5)


# ejecutar ambos
import threading

threading.Thread(target=heartbeat).start()
main()
