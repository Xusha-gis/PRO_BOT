import sqlite3
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_name="premium_bot.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Foydalanuvchilar jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Obunalar jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                plan_type TEXT,
                amount INTEGER,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                status TEXT DEFAULT 'pending',
                payment_date TIMESTAMP,
                receipt_file_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # To'lovlar jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                status TEXT DEFAULT 'pending',
                receipt_file_id TEXT,
                file_type TEXT,
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                admin_approved BOOLEAN DEFAULT FALSE,
                admin_id INTEGER,
                approval_date TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        self.conn.commit()
    
    def add_user(self, user_id, first_name, username):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
                (user_id, first_name, username)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Foydalanuvchi qo'shish xatosi: {e}")
            return False
    
    def add_subscription(self, user_id, plan_type, amount, duration_days):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration_days)
        
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO subscriptions (user_id, plan_type, amount, start_date, end_date, status) VALUES (?, ?, ?, ?, ?, 'active')",
            (user_id, plan_type, amount, start_date, end_date)
        )
        self.conn.commit()
        return end_date
    
    def get_subscription_end_date(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT end_date FROM subscriptions WHERE user_id = ? AND status = 'active' ORDER BY end_date DESC LIMIT 1",
            (user_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    
    def add_payment(self, user_id, amount, file_id, file_type):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO payments (user_id, amount, receipt_file_id, file_type) VALUES (?, ?, ?, ?)",
            (user_id, amount, file_id, file_type)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_pending_payments(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM payments WHERE status = 'pending'"
        )
        return cursor.fetchall()
    
    def update_payment_status(self, payment_id, status, admin_id=None):
        cursor = self.conn.cursor()
        if status == 'approved':
            cursor.execute(
                "UPDATE payments SET status = 'approved', admin_approved = TRUE, admin_id = ?, approval_date = CURRENT_TIMESTAMP WHERE id = ?",
                (admin_id, payment_id)
            )
        else:
            cursor.execute(
                "UPDATE payments SET status = ? WHERE id = ?",
                (status, payment_id)
            )
        self.conn.commit()
    
    def get_user_stats(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM subscriptions 
            WHERE end_date > CURRENT_TIMESTAMP AND status = 'active'
        """)
        premium_users = cursor.fetchone()[0]
        
        return total_users, premium_users
    
    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        return [row[0] for row in cursor.fetchall()]
    
    def remove_subscription(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE subscriptions SET status = 'cancelled' WHERE user_id = ?",
            (user_id,)
        )
        self.conn.commit()