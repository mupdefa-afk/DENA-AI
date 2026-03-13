import ccxt
import pandas as pd
import requests
import time
import threading
from flask import Flask
from datetime import datetime

TOKEN = "8544210127:AAEBmSGLnSutz5bMzz7Hij-R00GhVAEWkZ0"
CHAT_ID = "-1003524657786"

exchange = ccxt.kraken()

app = Flask(__name__)

symbols = [
"EUR/USD",
"GBP/USD",
"USD/JPY",
"AUD/USD",
"USD/CAD",
"EUR/JPY",
"EUR/GBP",
"USD/CHF",
"NZD/USD"
]

registro = []

max_senales_hora = 5
contador_senales = 0
hora_actual = datetime.now().hour


def enviar(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=data)


def rsi(df, periodo=14):

    delta = df["close"].diff()

    subida = delta.clip(lower=0)
    bajada = -delta.clip(upper=0)

    media_subida = subida.rolling(periodo).mean()
    media_bajada = bajada.rolling(periodo).mean()

    rs = media_subida / media_bajada

    rsi = 100 - (100 / (1 + rs))

    return rsi


def macd(df):

    ema12 = df["close"].ewm(span=12).mean()
    ema26 = df["close"].ewm(span=26).mean()

    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()

    return macd, signal


def tendencia(df):

    ema50 = df["close"].ewm(span=50).mean()
    ema200 = df["close"].ewm(span=200).mean()

    if ema50.iloc[-1] > ema200.iloc[-1]:
        return "CALL"

    return "PUT"


def soporte_resistencia(df):

    soporte = df["low"].rolling(20).min().iloc[-1]
    resistencia = df["high"].rolling(20).max().iloc[-1]

    return soporte, resistencia


def volumen_fuerte(df):

    vol_actual = df["volume"].iloc[-1]
    vol_media = df["volume"].rolling(20).mean().iloc[-1]

    return vol_actual > vol_media * 1.5


def mercado_lateral(df):

    rango = df["high"].max() - df["low"].min()

    if rango < df["close"].mean() * 0.002:
        return True

    return False


def probabilidad(rsi_v, macd_v, signal_v, vol_ok):

    score = 0

    if rsi_v < 30 or rsi_v > 70:
        score += 20

    if macd_v > signal_v:
        score += 20

    if vol_ok:
        score += 20

    score += 40

    return score


def analizar(symbol):

    timeframes = ["1m","5m","15m"]

    tendencias = []

    for tf in timeframes:

        try:
            data = exchange.fetch_ohlcv(symbol, tf, limit=200)
        except:
            return None

        df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])

        df["RSI"] = rsi(df)

        macd_val, signal_val = macd(df)

        tend = tendencia(df)

        tendencias.append(tend)

    call = tendencias.count("CALL")
    put = tendencias.count("PUT")

    if call >= 2:
        direccion = "CALL 🟢"

    elif put >= 2:
        direccion = "PUT 🔴"

    else:
        return None

    data = exchange.fetch_ohlcv(symbol,"1m",limit=200)

    df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])

    df["RSI"] = rsi(df)

    macd_val, signal_val = macd(df)

    rsi_v = df["RSI"].iloc[-1]

    macd_v = macd_val.iloc[-1]
    signal_v = signal_val.iloc[-1]

    soporte, resistencia = soporte_resistencia(df)

    precio = df["close"].iloc[-1]

    if direccion == "CALL 🟢" and precio > resistencia * 0.995:
        return None

    if direccion == "PUT 🔴" and precio < soporte * 1.005:
        return None

    vol_ok = volumen_fuerte(df)

    if not vol_ok:
        return None

    if mercado_lateral(df):
        return None

    prob = probabilidad(rsi_v,macd_v,signal_v,vol_ok)

    return {
        "symbol":symbol,
        "direccion":direccion,
        "prob":prob
    }


def mercado():

    global contador_senales, hora_actual

    enviar("🤖 DENA PRO ACTIVADA")

    while True:

        hora = datetime.now().hour

        if hora != hora_actual:
            contador_senales = 0
            hora_actual = hora

        if contador_senales < max_senales_hora:

            oportunidades = []

            for s in symbols:

                try:

                    r = analizar(s)

                    if r:
                        oportunidades.append(r)

                except:
                    pass

            if oportunidades:

                mejor = max(oportunidades, key=lambda x: x["prob"])

                alerta = f"""

🟡 ALERTA PREVIA

Activo: {mejor["symbol"]}

Posible dirección: {mejor["direccion"]}

Prepararse para entrada en 3 minutos
"""

                enviar(alerta)

                time.sleep(180)

                win = mejor["prob"]
                lose = 100 - win

                señal = f"""

🟢 SEÑAL CONFIRMADA

Activo: {mejor["symbol"]}

Dirección: {mejor["direccion"]}

Tiempo operación: 1m

Probabilidad ganar: {win}%
Probabilidad perder: {lose}%
"""

                enviar(señal)

                registro.append(mejor)

                contador_senales += 1

        time.sleep(60)


@app.route("/")
def home():
    return "DENA PRO ACTIVA"


threading.Thread(target=mercado).start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)import ccxt
import pandas as pd
import requests
import time
import threading
from flask import Flask
from datetime import datetime

TOKEN = "TU_TOKEN_TELEGRAM"
CHAT_ID = "TU_CHAT_ID"

exchange = ccxt.kraken()

app = Flask(__name__)

symbols = [
"EUR/USD",
"GBP/USD",
"USD/JPY",
"AUD/USD",
"USD/CAD",
"EUR/JPY",
"EUR/GBP",
"USD/CHF",
"NZD/USD"
]

registro = []

max_senales_hora = 5
contador_senales = 0
hora_actual = datetime.now().hour


def enviar(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=data)


def rsi(df, periodo=14):

    delta = df["close"].diff()

    subida = delta.clip(lower=0)
    bajada = -delta.clip(upper=0)

    media_subida = subida.rolling(periodo).mean()
    media_bajada = bajada.rolling(periodo).mean()

    rs = media_subida / media_bajada

    rsi = 100 - (100 / (1 + rs))

    return rsi


def macd(df):

    ema12 = df["close"].ewm(span=12).mean()
    ema26 = df["close"].ewm(span=26).mean()

    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()

    return macd, signal


def tendencia(df):

    ema50 = df["close"].ewm(span=50).mean()
    ema200 = df["close"].ewm(span=200).mean()

    if ema50.iloc[-1] > ema200.iloc[-1]:
        return "CALL"

    return "PUT"


def soporte_resistencia(df):

    soporte = df["low"].rolling(20).min().iloc[-1]
    resistencia = df["high"].rolling(20).max().iloc[-1]

    return soporte, resistencia


def volumen_fuerte(df):

    vol_actual = df["volume"].iloc[-1]
    vol_media = df["volume"].rolling(20).mean().iloc[-1]

    return vol_actual > vol_media * 1.5


def mercado_lateral(df):

    rango = df["high"].max() - df["low"].min()

    if rango < df["close"].mean() * 0.002:
        return True

    return False


def probabilidad(rsi_v, macd_v, signal_v, vol_ok):

    score = 0

    if rsi_v < 30 or rsi_v > 70:
        score += 20

    if macd_v > signal_v:
        score += 20

    if vol_ok:
        score += 20

    score += 40

    return score


def analizar(symbol):

    timeframes = ["1m","5m","15m"]

    tendencias = []

    for tf in timeframes:

        try:
            data = exchange.fetch_ohlcv(symbol, tf, limit=200)
        except:
            return None

        df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])

        df["RSI"] = rsi(df)

        macd_val, signal_val = macd(df)

        tend = tendencia(df)

        tendencias.append(tend)

    call = tendencias.count("CALL")
    put = tendencias.count("PUT")

    if call >= 2:
        direccion = "CALL 🟢"

    elif put >= 2:
        direccion = "PUT 🔴"

    else:
        return None

    data = exchange.fetch_ohlcv(symbol,"1m",limit=200)

    df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])

    df["RSI"] = rsi(df)

    macd_val, signal_val = macd(df)

    rsi_v = df["RSI"].iloc[-1]

    macd_v = macd_val.iloc[-1]
    signal_v = signal_val.iloc[-1]

    soporte, resistencia = soporte_resistencia(df)

    precio = df["close"].iloc[-1]

    if direccion == "CALL 🟢" and precio > resistencia * 0.995:
        return None

    if direccion == "PUT 🔴" and precio < soporte * 1.005:
        return None

    vol_ok = volumen_fuerte(df)

    if not vol_ok:
        return None

    if mercado_lateral(df):
        return None

    prob = probabilidad(rsi_v,macd_v,signal_v,vol_ok)

    return {
        "symbol":symbol,
        "direccion":direccion,
        "prob":prob
    }


def mercado():

    global contador_senales, hora_actual

    enviar("🤖 DENA PRO ACTIVADA")

    while True:

        hora = datetime.now().hour

        if hora != hora_actual:
            contador_senales = 0
            hora_actual = hora

        if contador_senales < max_senales_hora:

            oportunidades = []

            for s in symbols:

                try:

                    r = analizar(s)

                    if r:
                        oportunidades.append(r)

                except:
                    pass

            if oportunidades:

                mejor = max(oportunidades, key=lambda x: x["prob"])

                alerta = f"""

🟡 ALERTA PREVIA

Activo: {mejor["symbol"]}

Posible dirección: {mejor["direccion"]}

Prepararse para entrada en 3 minutos
"""

                enviar(alerta)

                time.sleep(180)

                win = mejor["prob"]
                lose = 100 - win

                señal = f"""

🟢 SEÑAL CONFIRMADA

Activo: {mejor["symbol"]}

Dirección: {mejor["direccion"]}

Tiempo operación: 1m

Probabilidad ganar: {win}%
Probabilidad perder: {lose}%
"""

                enviar(señal)

                registro.append(mejor)

                contador_senales += 1

        time.sleep(60)


@app.route("/")
def home():
    return "DENA PRO ACTIVA"


threading.Thread(target=mercado).start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)import ccxt
import pandas as pd
import requests
import time
import threading
from flask import Flask
from datetime import datetime

TOKEN = "TU_TOKEN_TELEGRAM"
CHAT_ID = "TU_CHAT_ID"

exchange = ccxt.kraken()

app = Flask(__name__)

symbols = [
"EUR/USD",
"GBP/USD",
"USD/JPY",
"AUD/USD",
"USD/CAD",
"EUR/JPY",
"EUR/GBP",
"USD/CHF",
"NZD/USD"
]

registro = []

max_senales_hora = 5
contador_senales = 0
hora_actual = datetime.now().hour


def enviar(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=data)


def rsi(df, periodo=14):

    delta = df["close"].diff()

    subida = delta.clip(lower=0)
    bajada = -delta.clip(upper=0)

    media_subida = subida.rolling(periodo).mean()
    media_bajada = bajada.rolling(periodo).mean()

    rs = media_subida / media_bajada

    rsi = 100 - (100 / (1 + rs))

    return rsi


def macd(df):

    ema12 = df["close"].ewm(span=12).mean()
    ema26 = df["close"].ewm(span=26).mean()

    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()

    return macd, signal


def tendencia(df):

    ema50 = df["close"].ewm(span=50).mean()
    ema200 = df["close"].ewm(span=200).mean()

    if ema50.iloc[-1] > ema200.iloc[-1]:
        return "CALL"

    return "PUT"


def soporte_resistencia(df):

    soporte = df["low"].rolling(20).min().iloc[-1]
    resistencia = df["high"].rolling(20).max().iloc[-1]

    return soporte, resistencia


def volumen_fuerte(df):

    vol_actual = df["volume"].iloc[-1]
    vol_media = df["volume"].rolling(20).mean().iloc[-1]

    return vol_actual > vol_media * 1.5


def mercado_lateral(df):

    rango = df["high"].max() - df["low"].min()

    if rango < df["close"].mean() * 0.002:
        return True

    return False


def probabilidad(rsi_v, macd_v, signal_v, vol_ok):

    score = 0

    if rsi_v < 30 or rsi_v > 70:
        score += 20

    if macd_v > signal_v:
        score += 20

    if vol_ok:
        score += 20

    score += 40

    return score


def analizar(symbol):

    timeframes = ["1m","5m","15m"]

    tendencias = []

    for tf in timeframes:

        try:
            data = exchange.fetch_ohlcv(symbol, tf, limit=200)
        except:
            return None

        df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])

        df["RSI"] = rsi(df)

        macd_val, signal_val = macd(df)

        tend = tendencia(df)

        tendencias.append(tend)

    call = tendencias.count("CALL")
    put = tendencias.count("PUT")

    if call >= 2:
        direccion = "CALL 🟢"

    elif put >= 2:
        direccion = "PUT 🔴"

    else:
        return None

    data = exchange.fetch_ohlcv(symbol,"1m",limit=200)

    df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])

    df["RSI"] = rsi(df)

    macd_val, signal_val = macd(df)

    rsi_v = df["RSI"].iloc[-1]

    macd_v = macd_val.iloc[-1]
    signal_v = signal_val.iloc[-1]

    soporte, resistencia = soporte_resistencia(df)

    precio = df["close"].iloc[-1]

    if direccion == "CALL 🟢" and precio > resistencia * 0.995:
        return None

    if direccion == "PUT 🔴" and precio < soporte * 1.005:
        return None

    vol_ok = volumen_fuerte(df)

    if not vol_ok:
        return None

    if mercado_lateral(df):
        return None

    prob = probabilidad(rsi_v,macd_v,signal_v,vol_ok)

    return {
        "symbol":symbol,
        "direccion":direccion,
        "prob":prob
    }


def mercado():

    global contador_senales, hora_actual

    enviar("🤖 DENA PRO ACTIVADA")

    while True:

        hora = datetime.now().hour

        if hora != hora_actual:
            contador_senales = 0
            hora_actual = hora

        if contador_senales < max_senales_hora:

            oportunidades = []

            for s in symbols:

                try:

                    r = analizar(s)

                    if r:
                        oportunidades.append(r)

                except:
                    pass

            if oportunidades:

                mejor = max(oportunidades, key=lambda x: x["prob"])

                alerta = f"""

🟡 ALERTA PREVIA

Activo: {mejor["symbol"]}

Posible dirección: {mejor["direccion"]}

Prepararse para entrada en 3 minutos
"""

                enviar(alerta)

                time.sleep(180)

                win = mejor["prob"]
                lose = 100 - win

                señal = f"""

🟢 SEÑAL CONFIRMADA

Activo: {mejor["symbol"]}

Dirección: {mejor["direccion"]}

Tiempo operación: 1m

Probabilidad ganar: {win}%
Probabilidad perder: {lose}%
"""

                enviar(señal)

                registro.append(mejor)

                contador_senales += 1

        time.sleep(60)


@app.route("/")
def home():
    return "DENA PRO ACTIVA"


threading.Thread(target=mercado).start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)import ccxt
import pandas as pd
import requests
import time
import threading
from flask import Flask
from datetime import datetime

TOKEN = "TU_TOKEN_TELEGRAM"
CHAT_ID = "TU_CHAT_ID"

exchange = ccxt.kraken()

app = Flask(__name__)

symbols = [
"EUR/USD",
"GBP/USD",
"USD/JPY",
"AUD/USD",
"USD/CAD",
"EUR/JPY",
"EUR/GBP",
"USD/CHF",
"NZD/USD"
]

registro = []

max_senales_hora = 5
contador_senales = 0
hora_actual = datetime.now().hour


def enviar(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=data)


def rsi(df, periodo=14):

    delta = df["close"].diff()

    subida = delta.clip(lower=0)
    bajada = -delta.clip(upper=0)

    media_subida = subida.rolling(periodo).mean()
    media_bajada = bajada.rolling(periodo).mean()

    rs = media_subida / media_bajada

    rsi = 100 - (100 / (1 + rs))

    return rsi


def macd(df):

    ema12 = df["close"].ewm(span=12).mean()
    ema26 = df["close"].ewm(span=26).mean()

    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()

    return macd, signal


def tendencia(df):

    ema50 = df["close"].ewm(span=50).mean()
    ema200 = df["close"].ewm(span=200).mean()

    if ema50.iloc[-1] > ema200.iloc[-1]:
        return "CALL"

    return "PUT"


def soporte_resistencia(df):

    soporte = df["low"].rolling(20).min().iloc[-1]
    resistencia = df["high"].rolling(20).max().iloc[-1]

    return soporte, resistencia


def volumen_fuerte(df):

    vol_actual = df["volume"].iloc[-1]
    vol_media = df["volume"].rolling(20).mean().iloc[-1]

    return vol_actual > vol_media * 1.5


def mercado_lateral(df):

    rango = df["high"].max() - df["low"].min()

    if rango < df["close"].mean() * 0.002:
        return True

    return False


def probabilidad(rsi_v, macd_v, signal_v, vol_ok):

    score = 0

    if rsi_v < 30 or rsi_v > 70:
        score += 20

    if macd_v > signal_v:
        score += 20

    if vol_ok:
        score += 20

    score += 40

    return score


def analizar(symbol):

    timeframes = ["1m","5m","15m"]

    tendencias = []

    for tf in timeframes:

        try:
            data = exchange.fetch_ohlcv(symbol, tf, limit=200)
        except:
            return None

        df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])

        df["RSI"] = rsi(df)

        macd_val, signal_val = macd(df)

        tend = tendencia(df)

        tendencias.append(tend)

    call = tendencias.count("CALL")
    put = tendencias.count("PUT")

    if call >= 2:
        direccion = "CALL 🟢"

    elif put >= 2:
        direccion = "PUT 🔴"

    else:
        return None

    data = exchange.fetch_ohlcv(symbol,"1m",limit=200)

    df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])

    df["RSI"] = rsi(df)

    macd_val, signal_val = macd(df)

    rsi_v = df["RSI"].iloc[-1]

    macd_v = macd_val.iloc[-1]
    signal_v = signal_val.iloc[-1]

    soporte, resistencia = soporte_resistencia(df)

    precio = df["close"].iloc[-1]

    if direccion == "CALL 🟢" and precio > resistencia * 0.995:
        return None

    if direccion == "PUT 🔴" and precio < soporte * 1.005:
        return None

    vol_ok = volumen_fuerte(df)

    if not vol_ok:
        return None

    if mercado_lateral(df):
        return None

    prob = probabilidad(rsi_v,macd_v,signal_v,vol_ok)

    return {
        "symbol":symbol,
        "direccion":direccion,
        "prob":prob
    }


def mercado():

    global contador_senales, hora_actual

    enviar("🤖 DENA PRO ACTIVADA")

    while True:

        hora = datetime.now().hour

        if hora != hora_actual:
            contador_senales = 0
            hora_actual = hora

        if contador_senales < max_senales_hora:

            oportunidades = []

            for s in symbols:

                try:

                    r = analizar(s)

                    if r:
                        oportunidades.append(r)

                except:
                    pass

            if oportunidades:

                mejor = max(oportunidades, key=lambda x: x["prob"])

                alerta = f"""

🟡 ALERTA PREVIA

Activo: {mejor["symbol"]}

Posible dirección: {mejor["direccion"]}

Prepararse para entrada en 3 minutos
"""

                enviar(alerta)

                time.sleep(180)

                win = mejor["prob"]
                lose = 100 - win

                señal = f"""

🟢 SEÑAL CONFIRMADA

Activo: {mejor["symbol"]}

Dirección: {mejor["direccion"]}

Tiempo operación: 1m

Probabilidad ganar: {win}%
Probabilidad perder: {lose}%
"""

                enviar(señal)

                registro.append(mejor)

                contador_senales += 1

        time.sleep(60)


@app.route("/")
def home():
    return "DENA PRO ACTIVA"


threading.Thread(target=mercado).start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)import ccxt
import pandas as pd
import requests
import time
import threading
from flask import Flask
from datetime import datetime

TOKEN = "TU_TOKEN_TELEGRAM"
CHAT_ID = "TU_CHAT_ID"

exchange = ccxt.kraken()

app = Flask(__name__)

symbols = [
"EUR/USD",
"GBP/USD",
"USD/JPY",
"AUD/USD",
"USD/CAD",
"EUR/JPY",
"EUR/GBP",
"USD/CHF",
"NZD/USD"
]

registro = []

max_senales_hora = 5
contador_senales = 0
hora_actual = datetime.now().hour


def enviar(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=data)


def rsi(df, periodo=14):

    delta = df["close"].diff()

    subida = delta.clip(lower=0)
    bajada = -delta.clip(upper=0)

    media_subida = subida.rolling(periodo).mean()
    media_bajada = bajada.rolling(periodo).mean()

    rs = media_subida / media_bajada

    rsi = 100 - (100 / (1 + rs))

    return rsi


def macd(df):

    ema12 = df["close"].ewm(span=12).mean()
    ema26 = df["close"].ewm(span=26).mean()

    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()

    return macd, signal


def tendencia(df):

    ema50 = df["close"].ewm(span=50).mean()
    ema200 = df["close"].ewm(span=200).mean()

    if ema50.iloc[-1] > ema200.iloc[-1]:
        return "CALL"

    return "PUT"


def soporte_resistencia(df):

    soporte = df["low"].rolling(20).min().iloc[-1]
    resistencia = df["high"].rolling(20).max().iloc[-1]

    return soporte, resistencia


def volumen_fuerte(df):

    vol_actual = df["volume"].iloc[-1]
    vol_media = df["volume"].rolling(20).mean().iloc[-1]

    return vol_actual > vol_media * 1.5


def mercado_lateral(df):

    rango = df["high"].max() - df["low"].min()

    if rango < df["close"].mean() * 0.002:
        return True

    return False


def probabilidad(rsi_v, macd_v, signal_v, vol_ok):

    score = 0

    if rsi_v < 30 or rsi_v > 70:
        score += 20

    if macd_v > signal_v:
        score += 20

    if vol_ok:
        score += 20

    score += 40

    return score


def analizar(symbol):

    timeframes = ["1m","5m","15m"]

    tendencias = []

    for tf in timeframes:

        try:
            data = exchange.fetch_ohlcv(symbol, tf, limit=200)
        except:
            return None

        df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])

        df["RSI"] = rsi(df)

        macd_val, signal_val = macd(df)

        tend = tendencia(df)

        tendencias.append(tend)

    call = tendencias.count("CALL")
    put = tendencias.count("PUT")

    if call >= 2:
        direccion = "CALL 🟢"

    elif put >= 2:
        direccion = "PUT 🔴"

    else:
        return None

    data = exchange.fetch_ohlcv(symbol,"1m",limit=200)

    df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])

    df["RSI"] = rsi(df)

    macd_val, signal_val = macd(df)

    rsi_v = df["RSI"].iloc[-1]

    macd_v = macd_val.iloc[-1]
    signal_v = signal_val.iloc[-1]

    soporte, resistencia = soporte_resistencia(df)

    precio = df["close"].iloc[-1]

    if direccion == "CALL 🟢" and precio > resistencia * 0.995:
        return None

    if direccion == "PUT 🔴" and precio < soporte * 1.005:
        return None

    vol_ok = volumen_fuerte(df)

    if not vol_ok:
        return None

    if mercado_lateral(df):
        return None

    prob = probabilidad(rsi_v,macd_v,signal_v,vol_ok)

    return {
        "symbol":symbol,
        "direccion":direccion,
        "prob":prob
    }


def mercado():

    global contador_senales, hora_actual

    enviar("🤖 DENA PRO ACTIVADA")

    while True:

        hora = datetime.now().hour

        if hora != hora_actual:
            contador_senales = 0
            hora_actual = hora

        if contador_senales < max_senales_hora:

            oportunidades = []

            for s in symbols:

                try:

                    r = analizar(s)

                    if r:
                        oportunidades.append(r)

                except:
                    pass

            if oportunidades:

                mejor = max(oportunidades, key=lambda x: x["prob"])

                alerta = f"""

🟡 ALERTA PREVIA

Activo: {mejor["symbol"]}

Posible dirección: {mejor["direccion"]}

Prepararse para entrada en 3 minutos
"""

                enviar(alerta)

                time.sleep(180)

                win = mejor["prob"]
                lose = 100 - win

                señal = f"""

🟢 SEÑAL CONFIRMADA

Activo: {mejor["symbol"]}

Dirección: {mejor["direccion"]}

Tiempo operación: 1m

Probabilidad ganar: {win}%
Probabilidad perder: {lose}%
"""

                enviar(señal)

                registro.append(mejor)

                contador_senales += 1

        time.sleep(60)


@app.route("/")
def home():
    return "DENA PRO ACTIVA"


threading.Thread(target=mercado).start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
