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
            day_temperature INTEGER,
            fertilizer_baff TEXT,
            toxic_time TEXT,
            a_hum INTEGER,
            greenhouse_counter INTEGER,
            min_need_temperature INTEGER,
            minus_hum INTEGER,
            goods_details TEXT,
            fire_time INTEGER,
            fertility_time INTEGER,
            god_blessing_time INTEGER,
            late_blight_time INTEGER,
            silver_scab_time INTEGER
        )
    """)
    conn.commit()
    conn.close()

def add_player(user_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    size_cell = np.array([[10,10,10],[10,10,10],[10,10,10]])
    goods_details = {
        "Тканина: 80": "trade_greenhouse_fabric",
        "Вентиляція: 100": "trade_greenhouse_ventilation",
        "Деревина: 90": "trade_greenhouse_wood"
    }
    cursor.execute("""
        INSERT OR REPLACE INTO players 
        (user_id, humidity, temperature, cell_fruits, size_cell, fruits, day, day_humidity, day_temperature, fertilizer_baff, toxic_time, a_hum, 
        greenhouse_counter, min_need_temperature, minus_hum, goods_details, fire_time, fertility_time, god_blessing_time, late_blight_time, silver_scab_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, 45, 19, 10, json.dumps(size_cell.tolist()), 0, 1, 0, 0, "standart", 0, 0, 0, 8, 10, json.dumps(goods_details), 0, 0, 0, 0, 0))
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
            "day_temperature": row[8],
            "fertilizer_baff": row[9],
            "toxic_time": row[10],
            "a_hum": row[11],
            "greenhouse_counter": row[12],
            "min_need_temperature": row[13],
            "minus_hum": row[14],
            'goods_details': json.loads(row[15]) if row[15] else {},
            'fire_time': row[16],
            'fertility_time': row[17],
            'god_blessing_time': row[18],
            'late_blight_time': row[19],
            'silver_scab_time': row[20]
        }
        return user_data
    return None

def update_player(user_id: int, **kwargs):
    conn = get_conn()
    cursor = conn.cursor()
    fields = []
    values = []
    for k, v in kwargs.items():
        if isinstance(v, (dict, list)):
            v = json.dumps(v)
        elif isinstance(v, np.ndarray):
            v = json.dumps(v.tolist())
        fields.append(f"{k} = ?")
        values.append(v)
    values.append(user_id)
    sql = f"UPDATE players SET {', '.join(fields)} WHERE user_id = ?"
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
