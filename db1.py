import sqlite3
from datetime import datetime

DB_NAME = "points.db"

def init_db1():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            points INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            points INTEGER,
            timestamp TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_points (
            username TEXT,
            date TEXT,
            points INTEGER DEFAULT 0,
            PRIMARY KEY (username, date)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (username) VALUES (?)', (username,))
    conn.commit()
    conn.close()

def add_points(username, points,now):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE users SET points = points + ? WHERE username = ?', (points, username))
    c.execute('INSERT INTO history (username, points, timestamp) VALUES (?, ?, ?)', 
              (username, points, datetime.now().isoformat()))
    
    c.execute('''
        INSERT INTO daily_points (username, date, points)
        VALUES (?, ?, ?)
        ON CONFLICT(username, date) DO UPDATE SET
        points = points + excluded.points
    ''', (username, now, points))
    conn.commit()
    conn.close()

def get_points(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT points FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0


def get_daily_points(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT date, points FROM daily_points
        WHERE username = ?
        ORDER BY date ASC
    ''', (username,))
    result = c.fetchall()
    conn.close()
    return result
