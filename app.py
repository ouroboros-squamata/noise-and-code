from flask import Flask, render_template, request, redirect
from openai import OpenAI
import sqlite3
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/health")
def health():
    return "OK", 200

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET", "POST"])
def home():
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM blogs ORDER BY views DESC LIMIT 10").fetchall()
    conn.close()
    return render_template("index.html", trending=posts)

@app.route("/submit", methods=["POST"])
def submit():
    idea = request.form["idea"]
    emotion = request.form["emotion"]
    perspective = request.form["perspective"]

    prompt = f"""Generate a scientific blog with:
    - Idea: {idea}
    - Emotion: {emotion}
    - Perspective: {perspective}
    """

    from openai import OpenAI
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO blogs (idea, emotion, perspective, content, views) VALUES (?, ?, ?, ?, 0)",
        (idea, emotion, perspective, content)
    )
    conn.commit()
    conn.close()

    return redirect("/")


    content = response.choices[0].message.content

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO blogs (idea, emotion, perspective, content, views) VALUES (?, ?, ?, ?, 0)",
        (idea, emotion, perspective, content)
    )
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/recent")
def recent():
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM blogs ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("recent.html", posts=posts)

@app.route("/all")
def all_blogs():
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM blogs").fetchall()
    conn.close()
    return render_template("all.html", posts=posts)

@app.route("/blog/<int:blog_id>")
def blog(blog_id):
    conn = get_db_connection()
    blog = conn.execute("SELECT * FROM blogs WHERE id = ?", (blog_id,)).fetchone()
    conn.execute("UPDATE blogs SET views = views + 1 WHERE id = ?", (blog_id,))
    conn.commit()
    conn.close()
    return render_template("blog.html", blog=blog)
