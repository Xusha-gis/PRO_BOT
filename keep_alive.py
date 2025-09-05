# keep_alive.py
from flask import Flask
import threading
import time
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlamoqda! ✅"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def ping_self():
    while True:
        try:
            url = os.environ.get('RENDER_URL')
            if url:
                response = requests.get(url)
                print(f"Ping muvaffaqiyatli: {response.status_code}")
        except Exception as e:
            print(f"Ping xatosi: {e}")
        time.sleep(300)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=ping_self, daemon=True).start()
    # Agar webhook rejimida bo'lsangiz, bot webserver (gunicorn + app_webhook) ishlaydi, shuning uchun __main__ ga bot ishga tushirish qo'shmang.
    while True:
        time.sleep(60)
