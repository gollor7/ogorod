import sqlite3
import numpy as np
import json

DB_NAME = "game.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            humidity INTEGER,
            temperature INTEGER,
            cell_fruits REAL,
            size_cell TEXT,
            fruits REAL,
            day INTEGER,
            day_humidity INTEGER,
            day_temperature INTEGER
        )
    """)
    conn.commit()
    conn.close()

def add_player(user_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    size_cell = np.array([[10,10,10],[10,10,10],[10,10,10]])
    cursor.execute("""
        INSERT OR REPLACE INTO players 
        (user_id, humidity, temperature, cell_fruits, size_cell, fruits, day, day_humidity, day_temperature)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, 45, 19, 10, json.dumps(size_cell.tolist()), 0, 1, 0, 0))
    conn.commit()
    conn.close()

def get_player(user_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        user_data = {
            "user_id": row[0],
            "humidity": row[1],
            "temperature": row[2],
            "cell_fruits": row[3],
            "size_cell": np.array(json.loads(row[4])),
            "fruits": row[5],
            "day": row[6],
            "day_humidity": row[7],
            "day_temperature": row[8]
        }
        return user_data
    return None

def update_player(user_id: int, **kwargs):
    conn = get_conn()
    cursor = conn.cursor()
    fields = []
    values = []
    for k, v in kwargs.items():
        if k == "size_cell":
            v = json.dumps(v.tolist())
        fields.append(f"{k} = ?")
        values.append(v)
    values.append(user_id)
    sql = f"UPDATE players SET {', '.join(fields)} WHERE user_id = ?"
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
