import os
import sqlite3
from flask import Flask, request, render_template, redirect
from datetime import datetime

app = Flask(__name__)
DB_NAME = "posts.db"

import sqlite3
import os

DB_NAME = "posts.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Check if posts table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts';")
        if not cursor.fetchone():
            cursor.execute('''
                CREATE TABLE posts (
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
            print("✅ 'posts' table created.")
        else:
            print("ℹ️ 'posts' table already exists.")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Failed to initialize DB: {e}")

init_db()  # run this when app starts

from flask import Flask, render_template, request, redirect, g
import sqlite3
from datetime import datetime
import openai

app = Flask(__name__)
DATABASE = 'blogs.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route("/")
def home():
    db = get_db()
    posts = db.execute("SELECT * FROM posts ORDER BY views DESC LIMIT 10").fetchall()
    return render_template("index.html", posts=posts)

@app.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "POST":
        idea = request.form["idea"]
        emotion = request.form["emotion"]
        perspective = request.form["perspective"]
        prompt = f"Write a positive blog post about {idea}, based on the emotion {emotion}, from the perspective of {perspective}."
        openai.api_key = "sk-REPLACE_ME"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()
        db = get_db()
        db.execute("""
            INSERT INTO posts (idea, emotion, perspective, content, created_at, views)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (idea, emotion, perspective, content, datetime.utcnow(), 0))
        db.commit()
        return redirect("/all")
    return render_template("generate.html")

@app.route("/recent")
def recent():
    db = get_db()
    posts = db.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT 10").fetchall()
    return render_template("recent.html", posts=posts)

@app.route("/all")
def all():
    db = get_db()
    posts = db.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()
    return render_template("all.html", posts=posts)

@app.route("/post/<int:post_id>")
def view_post(post_id):
    db = get_db()
    db.execute("UPDATE posts SET views = views + 1 WHERE id = ?", (post_id,))
    db.commit()
    post = db.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    return render_template("view_post.html", post=post)

@app.route("/health")
def health():
    return "OK"
