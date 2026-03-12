import requests
import time
import ccxt
import pandas as pd
import threading
from flask import Flask
from datetime import datetime

TOKEN = "8544210127:AAGefu7tMGkhVH6-z4YA4v0JN9DcATtTs5Jo"
CHAT_ID = "-1003524657786"

exchange = ccxt.kraken()

app = Flask(__name__)

symbols = [
"BTC/USDT",
"ETH/USDT",
"BNB/USDT",
"SOL/USDT",
"XRP/USDT"
]

registro_señales = []

def enviar_mensaje(texto):

    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data={
    "chat_id":CHAT_ID,
    "text":texto
    }

    requests.post(url,data=data)

def calcular_rsi(df,periodo=14):

    delta=df["close"].diff()

    subida=delta.clip(lower=0)
    bajada=-delta.clip(upper=0)

    media_subida=subida.rolling(periodo).mean()
    media_bajada=bajada.rolling(periodo).mean()

    rs=media_subida/media_bajada

    rsi=100-(100/(1+rs))

    return rsi

def calcular_macd(df):

    ema12=df["close"].ewm(span=12).mean()
    ema26=df["close"].ewm(span=26).mean()

    macd=ema12-ema26
    señal=macd.ewm(span=9).mean()

    return macd,señal

def calcular_adx(df,periodo=14):

    high=df["high"]
    low=df["low"]
    close=df["close"]

    plus_dm=high.diff()
    minus_dm=low.diff()

    plus_dm[plus_dm<0]=0
    minus_dm[minus_dm>0]=0

    tr=pd.concat([
    high-low,
    abs(high-close.shift()),
    abs(low-close.shift())
    ],axis=1).max(axis=1)

    atr=tr.rolling(periodo).mean()

    plus_di=100*(plus_dm.ewm(alpha=1/periodo).mean()/atr)
    minus_di=100*(minus_dm.abs().ewm(alpha=1/periodo).mean()/atr)

    dx=(abs(plus_di-minus_di)/(plus_di+minus_di))*100

    adx=dx.ewm(alpha=1/periodo).mean()

    return adx

def tendencia(df):

    ema50=df["close"].ewm(span=50).mean()
    ema200=df["close"].ewm(span=200).mean()

    if ema50.iloc[-1]>ema200.iloc[-1]:
        return "ALCISTA"
    else:
        return "BAJISTA"

def analizar(symbol):

    timeframe="1m"

    ohlcv=exchange.fetch_ohlcv(symbol,timeframe,limit=200)

    df=pd.DataFrame(ohlcv,columns=["time","open","high","low","close","volume"])

    df["RSI"]=calcular_rsi(df)

    macd,signal=calcular_macd(df)

    df["MACD"]=macd
    df["SIGNAL"]=signal

    df["ADX"]=calcular_adx(df)

    tend=tendencia(df)

    rsi=df["RSI"].iloc[-1]
    macd_val=df["MACD"].iloc[-1]
    macd_sig=df["SIGNAL"].iloc[-1]
    adx=df["ADX"].iloc[-1]

    precio=df["close"].iloc[-1]

    prob=0
    señal=None

    if rsi<30:
        prob+=20

    if rsi>70:
        prob+=20

    if macd_val>macd_sig:
        prob+=20

    if macd_val<macd_sig:
        prob+=20

    if tend=="ALCISTA":
        prob+=20

    if tend=="BAJISTA":
        prob+=20

    if adx>25:
        prob+=20

    if rsi<30 and macd_val>macd_sig and tend=="ALCISTA" and adx>25:
        señal="CALL"

    if rsi>70 and macd_val<macd_sig and tend=="BAJISTA" and adx>25:
        señal="PUT"

    if señal:

        registro_señales.append({
        "activo":symbol,
        "precio":precio,
        "señal":señal,
        "hora":datetime.now()
        })

        mensaje=f"""
DENA PRO SIGNAL

Activo: {symbol}
Precio: {precio}

Tendencia: {tend}
RSI: {round(rsi,2)}
ADX: {round(adx,2)}

Probabilidad estimada: {prob} %

Señal: {señal}
"""

        enviar_mensaje(mensaje)

def reporte_diario():

    total=len(registro_señales)

    if total==0:
        return

    ganadas=0
    perdidas=0

    efectividad=(ganadas/(total))*100 if total>0 else 0

    mensaje=f"""
REPORTE DENA

Señales totales: {total}

Ganadas: {ganadas}

Perdidas: {perdidas}

Efectividad estimada: {round(efectividad,2)} %
"""

    enviar_mensaje(mensaje)

def loop():

    while True:

        for s in symbols:

            try:
                analizar(s)

            except Exception as e:
                print("error",e)

        time.sleep(60)

@app.route("/")
def home():
    return "DENA PRO ACTIVA"

threading.Thread(target=loop).start()

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
