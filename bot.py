import ccxt
import pandas as pd
import requests
import time
import threading
from flask import Flask
from datetime import datetime

# =========================
# CONFIGURACION TELEGRAM
# =========================

TOKEN = "8544210127:AAEBmSGLnSutz5bMzz7Hij-R00GhVAEWkZ0"
CHAT_ID = "-1003524657786"

# =========================
# CONEXION EXCHANGE
# =========================

exchange = ccxt.binance()

# =========================
# FLASK SERVER
# =========================

app = Flask(__name__)

# =========================
# ENVIAR MENSAJE TELEGRAM
# =========================

def enviar(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    try:
        requests.post(url, data=data)
    except:
        print("Error enviando mensaje")

# =========================
# RSI
# =========================

def rsi(df, periodo=14):

    delta = df["close"].diff()

    subida = delta.clip(lower=0)
    bajada = -delta.clip(upper=0)

    media_subida = subida.rolling(periodo).mean()
    media_bajada = bajada.rolling(periodo).mean()

    rs = media_subida / media_bajada

    rsi = 100 - (100 / (1 + rs))

    return rsi

# =========================
# MACD
# =========================

def macd(df):

    ema12 = df["close"].ewm(span=12).mean()
    ema26 = df["close"].ewm(span=26).mean()

    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()

    return macd, signal

# =========================
# DETECTAR ACTIVOS
# =========================

def obtener_activos():

    try:

        mercados = exchange.load_markets()

        activos = []

        for symbol in mercados:

            if "USDT" in symbol and "/" in symbol:

                activos.append(symbol)

        return activos[:20]

    except:

        return []

# =========================
# ANALISIS
# =========================

def analizar(symbol):

    try:

        ohlcv = exchange.fetch_ohlcv(symbol, "1m", limit=100)

        df = pd.DataFrame(
            ohlcv,
            columns=["time","open","high","low","close","volume"]
        )

        df["RSI"] = rsi(df)

        macd_val, signal_val = macd(df)

        rsi_actual = df["RSI"].iloc[-1]

        macd_actual = macd_val.iloc[-1]
        signal_actual = signal_val.iloc[-1]

        if rsi_actual < 30 and macd_actual > signal_actual:

            return "CALL 🟢"

        if rsi_actual > 70 and macd_actual < signal_actual:

            return "PUT 🔴"

    except:

        return None

    return None

# =========================
# MERCADO LOOP
# =========================

def mercado():

    enviar("🤖 DENA BOT INICIADO")

    activos = obtener_activos()

    enviar(f"Activos detectados: {len(activos)}")

    while True:

        print("Analizando mercado...")

        for symbol in activos:

            señal = analizar(symbol)

            if señal:

                mensaje = f"""

🚨 SEÑAL DETECTADA

Activo: {symbol}

Direccion: {señal}

Tiempo: 1 minuto

Hora: {datetime.now()}
"""

                enviar(mensaje)

                time.sleep(60)

        time.sleep(60)

# =========================
# HOME SERVER
# =========================

@app.route("/")
def home():

    return "DENA BOT ACTIVO"

# =========================
# INICIAR BOT
# =========================

threading.Thread(target=mercado).start()

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=10000)
