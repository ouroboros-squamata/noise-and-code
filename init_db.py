import sqlite3

conn = sqlite3.connect('database.db')
conn.execute("""
    CREATE TABLE IF NOT EXISTS blogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        idea TEXT NOT NULL,
        emotion TEXT NOT NULL,
        perspective TEXT NOT NULL,
        content TEXT NOT NULL,
        views INTEGER DEFAULT 0
    );
""")
conn.commit()
conn.close()
print("✅ database initialized")
