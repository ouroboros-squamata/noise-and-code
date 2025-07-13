
import sqlite3

conn = sqlite3.connect("blogs.db")
with open("schema.sql") as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
