from flask import Flask
import threading
import time
import requests
import os
from app import main  # asosiy botni import qilamiz

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlamoqda! ✅"

def run_flask():
    port = int(os.environ.get('PORT', 10000))  # Render odatda 10000 port beradi
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
        time.sleep(300)  # har 5 daqiqada ping

if __name__ == "__main__":
    # Flask server
    threading.Thread(target=run_flask, daemon=True).start()
    # Ping
    threading.Thread(target=ping_self, daemon=True).start()
    # Botni ishga tushirish
    main()
