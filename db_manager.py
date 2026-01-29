import sqlite3
import os
import json

DB_PATH = "save_game.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_game(money, unlocked_fields, worker_data):
    """
    unlocked_fields: list of indices or names of unlocked fields
    worker_data: dict of worker stats keyed by field and worker index
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Save money
    cursor.execute("INSERT OR REPLACE INTO game_state (key, value) VALUES (?, ?)", ("money", str(money)))
    
    # Save unlocked fields as a comma-separated string
    fields_str = ",".join(map(str, unlocked_fields))
    cursor.execute("INSERT OR REPLACE INTO game_state (key, value) VALUES (?, ?)", ("unlocked_fields", fields_str))

    # Save worker data as JSON
    cursor.execute("INSERT OR REPLACE INTO game_state (key, value) VALUES (?, ?)", ("worker_data", json.dumps(worker_data)))
    
    conn.commit()
    conn.close()

def load_game():
    if not os.path.exists(DB_PATH):
        init_db()
        return None

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT key, value FROM game_state")
    rows = cursor.fetchall()
    
    data = {}
    for row in rows:
        data[row[0]] = row[1]
    
    conn.close()
    
    if not data:
        return None
        
    money = float(data.get("money", 0))
    unlocked_fields_str = data.get("unlocked_fields", "")
    unlocked_fields = []
    if unlocked_fields_str:
        unlocked_fields = unlocked_fields_str.split(",")
        
    worker_data_json = data.get("worker_data", "{}")
    worker_data = json.loads(worker_data_json)

    return {
        "money": money,
        "unlocked_fields": unlocked_fields,
        "worker_data": worker_data
    }

def delete_save():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
