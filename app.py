from flask import Flask, request, render_template, redirect
from openai import OpenAI
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'blog.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/health")
def health():
    return "OK", 200

@app.route("/")
def home():
    db = get_db()
    posts = db.execute("SELECT * FROM posts ORDER BY views DESC LIMIT 10").fetchall()
    return render_template("index.html", trending=posts)

@app.route("/all")
def all_blogs():
    db = get_db()
    posts = db.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()
    return render_template("all.html", posts=posts)

@app.route("/recent")
def recent_blogs():
    db = get_db()
    posts = db.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT 10").fetchall()
    return render_template("recent.html", posts=posts)

@app.route("/submit", methods=["POST"])
def submit():
    idea = request.form.get("idea")
    emotion = request.form.get("emotion")
    perspective = request.form.get("perspective")

    if not all([idea, emotion, perspective]):
        return "Missing required fields", 400

    prompt = (
        f"Write a short, inspiring blog post based on the following idea:\n"
        f"Idea: {idea}\n"
        f"Emotion or Problem: {emotion}\n"
        f"Perspective or Voice: {perspective}\n\n"
        f"Include a clear scientific basis, a hopeful tone, and assign 3 relevant tags."
    )

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        blog = response.choices[0].message.content

        db = get_db()
        db.execute(
            "INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)",
            (idea, blog, datetime.utcnow().isoformat())
        )
        db.commit()
        return redirect("/all")

    except Exception as e:
        print("OpenAI error:", e)
        return f"Failed to generate blog: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
