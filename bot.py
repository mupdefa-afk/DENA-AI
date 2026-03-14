import ccxt
import pandas as pd
import requests
import time
import threading
import json
from flask import Flask
from datetime import datetime, timedelta

TOKEN="8544210127:AAEBmSGLnSutz5bMzz7Hij-R00GhVAEWkZ0"
CHAT_ID="-1003524657786"

exchange = ccxt.bybit()

app = Flask(__name__)

signals_hour = 0
hora_actual = datetime.now().hour

historial_archivo="historial.json"

# ---------------- TELEGRAM

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

# ---------------- HORARIO OPERAR

def horario_operar():

    hora=datetime.now().hour

    if hora>=15 or hora<=2:
        return True

    return False

# ---------------- RSI

def rsi(df,periodo=14):

    delta=df["close"].diff()

    subida=delta.clip(lower=0)
    bajada=-delta.clip(upper=0)

    media_subida=subida.rolling(periodo).mean()
    media_bajada=bajada.rolling(periodo).mean()

    rs=media_subida/media_bajada

    return 100-(100/(1+rs))

# ---------------- MACD

def macd(df):

    ema12=df["close"].ewm(span=12).mean()
    ema26=df["close"].ewm(span=26).mean()

    macd=ema12-ema26
    signal=macd.ewm(span=9).mean()

    return macd,signal

# ---------------- EMA

def ema(df,periodo):

    return df["close"].ewm(span=periodo).mean()

# ---------------- ATR

def atr(df,periodo=14):

    high_low=df["high"]-df["low"]
    high_close=abs(df["high"]-df["close"].shift())
    low_close=abs(df["low"]-df["close"].shift())

    tr=pd.concat([high_low,high_close,low_close],axis=1).max(axis=1)

    atr=tr.rolling(periodo).mean()

    return atr

# ---------------- SOPORTE RESISTENCIA

def soporte_resistencia(df):

    soporte=df["low"].rolling(20).min().iloc[-1]
    resistencia=df["high"].rolling(20).max().iloc[-1]

    return soporte,resistencia

# ---------------- MERCADO LATERAL

def mercado_lateral(df):

    rango=df["high"].rolling(20).max().iloc[-1]-df["low"].rolling(20).min().iloc[-1]

    if rango<df["close"].iloc[-1]*0.002:
        return True

    return False

# ---------------- DETECTOR BALLENA

def ballena(df):

    vol=df["volume"].iloc[-1]
    media=df["volume"].rolling(20).mean().iloc[-1]

    if vol>media*3:
        return True

    return False

# ---------------- RUPTURA

def ruptura(df):

    precio=df["close"].iloc[-1]

    maximo=df["high"].rolling(20).max().iloc[-2]
    minimo=df["low"].rolling(20).min().iloc[-2]

    if precio>maximo:
        return "CALL"

    if precio<minimo:
        return "PUT"

    return None

# ---------------- ACTIVOS

def obtener_activos():

    markets=exchange.load_markets()

    activos=[]

    for m in markets:

        if "/USDT" in m:

            activos.append(m)

    return activos[:30]

# ---------------- ANALISIS

def analizar(symbol):

    score=0

    for tf in ["1m","5m","15m"]:

        data=exchange.fetch_ohlcv(symbol,tf,limit=100)

        df=pd.DataFrame(data,columns=["time","open","high","low","close","volume"])

        df["RSI"]=rsi(df)

        macd_val,signal_val=macd(df)

        ema50=ema(df,50).iloc[-1]
        ema200=ema(df,200).iloc[-1]

        atr_val=atr(df).iloc[-1]

        rsi_actual=df["RSI"].iloc[-1]

        macd_actual=macd_val.iloc[-1]
        signal_actual=signal_val.iloc[-1]

        if atr_val<df["close"].iloc[-1]*0.001:
            return None

        if rsi_actual<30 and macd_actual>signal_actual and ema50>ema200:
            score+=1

        if rsi_actual>70 and macd_actual<signal_actual and ema50<ema200:
            score-=1

    if mercado_lateral(df):
        return None

    if ballena(df):
        return None

    soporte,resistencia=soporte_resistencia(df)

    precio=df["close"].iloc[-1]

    if precio>resistencia*0.995 or precio<soporte*1.005:
        return None

    r=ruptura(df)

    if score>=2:
        return "CALL",score

    if score<=-2:
        return "PUT",abs(score)

    if r:
        return r,2

    return None

# ---------------- HISTORIAL

def guardar(resultado):

    try:
        data=json.load(open(historial_archivo))
    except:
        data=[]

    data.append(resultado)

    json.dump(data,open(historial_archivo,"w"))

# ---------------- WINRATE

def winrate():

    try:
        data=json.load(open(historial_archivo))
    except:
        return 0

    wins=0

    for d in data:

        if d["resultado"]=="win":
            wins+=1

    if len(data)==0:
        return 0

    return round((wins/len(data))*100,2)

# ---------------- MAPA CALOR

def heatmap(activos):

    resultados=[]

    for s in activos:

        try:

            data=exchange.fetch_ticker(s)

            cambio=data["percentage"]

            resultados.append((s,cambio))

        except:
            pass

    resultados=sorted(resultados,key=lambda x:abs(x[1]),reverse=True)

    return resultados[:5]

# ---------------- MERCADO LOOP

def mercado():

    global signals_hour,hora_actual

    enviar("DENA ULTRA ACTIVADO")

    activos=obtener_activos()

    enviar(f"Analizando {len(activos)} activos")

    while True:

        if not horario_operar():

            time.sleep(60)
            continue

        if datetime.now().hour!=hora_actual:

            signals_hour=0
            hora_actual=datetime.now().hour

        if signals_hour>=5:

            time.sleep(60)
            continue

        mejores=[]

        for s in activos:

            resultado=analizar(s)

            if resultado:

                direccion,score=resultado

                mejores.append((s,direccion,score))

        mejores=sorted(mejores,key=lambda x:x[2],reverse=True)[:5]

        if len(mejores)>0:

            activo,direccion,score=mejores[0]

            prob=70+(score*5)

            entrada=datetime.now()+timedelta(minutes=3)

            enviar(f"""

ALERTA PREVIA

Activo {activo}

Direccion {direccion}

Hora entrada {entrada.strftime('%H:%M:%S')}

""")

            time.sleep(180)

            enviar(f"""

SEÑAL CONFIRMADA

Activo {activo}

Direccion {direccion}

Hora exacta {datetime.now().strftime('%H:%M:%S')}

Probabilidad ganar {prob}%

""")

            signals_hour+=1

        time.sleep(60)

# ---------------- PANEL

@app.route("/panel")

def panel():

    return f"DENA ULTRA\nWinrate {winrate()}%"

@app.route("/")

def home():

    return "BOT ACTIVO"

threading.Thread(target=mercado).start()

if __name__=="__main__":

    app.run(host="0.0.0.0",port=10000)
