import sqlite3

def init_db():
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea TEXT NOT NULL,
            emotion TEXT NOT NULL,
            perspective TEXT NOT NULL,
            scientific_basis TEXT,
            positive_outcome TEXT,
            tags TEXT,
            views INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully. posts.db created.")

if __name__ == "__main__":
    init_db()
