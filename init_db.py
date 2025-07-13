import sqlite3
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea TEXT,
    emotion TEXT,
    perspective TEXT,
    content TEXT,
    created_at TEXT,
    views INTEGER DEFAULT 0
)''')
conn.commit()
conn.close()