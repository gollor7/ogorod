import sqlite3
from datetime import datetime
import os


# Функція для підключення до бази даних
def create_connection():
    conn = sqlite3.connect('user_data.db')  # Зв'язок з базою даних
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        growth_days INTEGER,
        drought_resistance INTEGER,
        size INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()
