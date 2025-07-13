
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'posts.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS posts (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            content TEXT NOT NULL,
                            idea TEXT,
                            emotion TEXT,
                            perspective TEXT,
                            views INTEGER DEFAULT 0
                        )""")
        conn.commit()
    print("✅ Database initialized successfully.")

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    db = get_db_connection()
    posts = db.execute("SELECT * FROM posts ORDER BY views DESC LIMIT 10").fetchall()
    db.close()
    return render_template("home.html", posts=posts)

@app.route("/all")
def all_blogs():
    db = get_db_connection()
    posts = db.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    db.close()
    return render_template("all.html", posts=posts)

@app.route("/recent")
def recent_blogs():
    db = get_db_connection()
    posts = db.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 5").fetchall()
    db.close()
    return render_template("recent.html", posts=posts)

@app.route("/generate", methods=["GET", "POST"])
def generate_blog():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        idea = request.form.get("idea", "")
        emotion = request.form.get("emotion", "")
        perspective = request.form.get("perspective", "")
        db = get_db_connection()
        db.execute("INSERT INTO posts (title, content, idea, emotion, perspective) VALUES (?, ?, ?, ?, ?)", 
                   (title, content, idea, emotion, perspective))
        db.commit()
        db.close()
        return redirect(url_for("all_blogs"))
    return render_template("generate.html")

@app.route("/health")
def health():
    return "OK"

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
