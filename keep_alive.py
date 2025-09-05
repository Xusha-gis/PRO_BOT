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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

def ping_self():
    while True:
        try:
            # O'zining URL manzilini ping qilish
            url = os.environ.get('RENDER_URL', 'https://your-bot-name.onrender.com')
            response = requests.get(url)
            print(f"Ping muvaffaqiyatli: {response.status_code}")
        except Exception as e:
            print(f"Ping xatosi: {e}")
        time.sleep(300)  # 5 daqiqada bir

if __name__ == "__main__":
    # Flask serverini backgroundda ishga tushirish
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Ping qilishni boshlash
    ping_thread = threading.Thread(target=ping_self)
    ping_thread.daemon = True
    ping_thread.start()
    
    # Asosiy botni ishga tushirish
    from app import main
    main()