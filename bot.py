import ccxt
import pandas as pd
import requests
import time
import threading
from flask import Flask
from datetime import datetime

TOKEN="8544210127:AAEBmSGLnSutz5bMzz7Hij-R00GhVAEWkZ0"

CHAT_ID="-1003524657786"

exchange = ccxt.bybit()

app = Flask(__name__)

signals_hour = 0
hora_actual = datetime.now().hour


# ---------- TELEGRAM

def enviar(msg):

    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data={
        "chat_id":CHAT_ID,
        "text":msg
    }

    try:
        requests.post(url,data=data)
    except:
        print("error telegram")


# ---------- HORARIO

def horario_operar():

    hora=datetime.now().hour

    if hora>=15 or hora<=2:
        return True

    return False


# ---------- RSI

def rsi(df,periodo=14):

    delta=df["close"].diff()

    subida=delta.clip(lower=0)
    bajada=-delta.clip(upper=0)

    media_subida=subida.rolling(periodo).mean()
    media_bajada=bajada.rolling(periodo).mean()

    rs=media_subida/media_bajada

    return 100-(100/(1+rs))


# ---------- MACD

def macd(df):

    ema12=df["close"].ewm(span=12).mean()
    ema26=df["close"].ewm(span=26).mean()

    macd=ema12-ema26
    signal=macd.ewm(span=9).mean()

    return macd,signal


# ---------- ACTIVOS

def obtener_activos():

    markets=exchange.load_markets()

    activos=[]

    for m in markets:

        if "/USDT" in m:
            activos.append(m)

    return activos[:20]


# ---------- ANALISIS

def analizar(symbol):

    try:

        data=exchange.fetch_ohlcv(symbol,"1m",limit=100)

        df=pd.DataFrame(data,columns=["time","open","high","low","close","volume"])

        df["RSI"]=rsi(df)

        macd_val,signal_val=macd(df)

        rsi_actual=df["RSI"].iloc[-1]

        macd_actual=macd_val.iloc[-1]
        signal_actual=signal_val.iloc[-1]

        if rsi_actual<35 and macd_actual>signal_val.iloc[-1]:

            return "CALL"

        if rsi_actual>65 and macd_actual<signal_val.iloc[-1]:

            return "PUT"

    except:

        return None


# ---------- LOOP MERCADO

def mercado():

    global signals_hour,hora_actual

    enviar("DENA BOT ACTIVADO")

    activos=obtener_activos()

    enviar(f"Analizando {len(activos)} activos")

    while True:

        if not horario_operar():

            time.sleep(60)
            continue

        if datetime.now().hour!=hora_actual:

            signals_hour=0
            hora_actual=datetime.now().hour

        if signals_hour>=3:

            time.sleep(60)
            continue

        for s in activos:

            direccion=analizar(s)

            if direccion:

                enviar(f"""

SEÑAL DENA

Activo: {s}

Dirección: {direccion}

Hora: {datetime.now().strftime('%H:%M:%S')}

Tiempo operación: 1 minuto

""")

                signals_hour+=1

                time.sleep(60)

                break

        time.sleep(20)


# ---------- PANEL

@app.route("/")
