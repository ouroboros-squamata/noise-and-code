from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import openai
from datetime import datetime
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-...")

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/health")
def health():
    return "OK", 200

@app.route("/")
def home():
    db = get_db_connection()
    posts = db.execute("SELECT * FROM posts ORDER BY views DESC LIMIT 10").fetchall()
    db.close()
    return render_template("home.html", posts=posts)

@app.route("/all")
def all_blogs():
    db = get_db_connection()
    posts = db.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()
    db.close()
    return render_template("all.html", posts=posts)

@app.route("/recent")
def recent():
    db = get_db_connection()
    posts = db.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT 5").fetchall()
    db.close()
    return render_template("recent.html", posts=posts)

@app.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "POST":
        idea = request.form["idea"]
        emotion = request.form["emotion"]
        perspective = request.form["perspective"]
        content = generate_blog(idea, emotion, perspective)
        db = get_db_connection()
        db.execute("INSERT INTO posts (idea, emotion, perspective, content, created_at, views)
                    VALUES (?, ?, ?, ?, ?, ?)",
                   (idea, emotion, perspective, content, datetime.utcnow(), 0))
        db.commit()
        db.close()
        return redirect(url_for("home"))
    return render_template("generate.html")

def generate_blog(idea, emotion, perspective):
    prompt = f"Write a positive, belief-based blog based on the idea: '{idea}', emotion: '{emotion}', and perspective: '{perspective}'."
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    app.run(debug=True)