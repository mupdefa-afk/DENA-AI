import requests
import time
from datetime import datetime
import pytz

TOKEN = "8544210127:AAFGMquOV2eHTMzNZlsOtdWY6HGvrDSgbEo"
CHAT_ID = "-1003524657786"

TZ = pytz.timezone("America/Guayaquil")

def enviar(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        print("Mensaje enviado")
    except Exception as e:
        print("Error:", e)

def bot():
    enviar("🚀 TEST INICIADO")

    while True:
        hora = datetime.now(TZ).strftime("%H:%M:%S")

        enviar(f"⏰ BOT VIVO {hora}")

        time.sleep(60)

bot()
