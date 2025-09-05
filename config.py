import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
        self.CHANNEL_ID = os.getenv('CHANNEL_ID', '-1001234567890')
        self.ADMIN_IDS = os.getenv('ADMIN_IDS', '123456789').split(',')
        self.CARD_NUMBER = os.getenv('CARD_NUMBER', '8600 1234 5678 9012')
        self.CARDHOLDER_NAME = os.getenv('CARDHOLDER_NAME', 'John Doe')
        
        # Obuna narxlari
        self.SUBSCRIPTION_PRICES = {
            '1_oy': 20000,
            '3_oy': 55000,
            '6_oy': 105000,
            '1_yil': 185000
        }
        
        # Obuna muddatlari (kunlarda)
        self.SUBSCRIPTION_DURATIONS = {
            '1_oy': 30,
            '3_oy': 90,
            '6_oy': 180,
            '1_yil': 365
        }
