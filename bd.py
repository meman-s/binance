from keys import api_key, api_secret
from binance.client import Client
import sqlite3

class DB:
    def __init__(self, db):
        self.conn = sqlite3.connect(db, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def get_last_id(self):
            max_id = self.cursor.execute("SELECT max(id) FROM sex").fetchone()[0]
            return max_id

    def put_data(self, symbol, price, time):
        data = (symbol, price, time)
        self.cursor.execute("INSERT OR IGNORE INTO sex (symbol, price, time) VALUES (?, ?, ?)", data)
        return self.conn.commit()
