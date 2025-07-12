import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from openai import OpenAI

app = Flask(__name__)
client = OpenAI()

DB_PATH = "blogs.db"
if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE blogs (id INTEGER PRIMARY KEY AUTOINCREMENT, idea TEXT, emotion TEXT, perspective TEXT, content TEXT, scientific TEXT, outcome TEXT, views INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def generate_blog(idea, emotion, perspective):
    prompt = f"Generate a scientific blog with:
Idea: {idea}
Emotion: {emotion}
Perspective: {perspective}
Include a scientific basis and a positive outcome."
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

@app.route("/")
def home():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, idea, content, views FROM blogs ORDER BY views DESC LIMIT 10")
    trending = c.fetchall()
    conn.close()
    return render_template("index.html", trending=trending)

@app.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "POST":
        idea = request.form["idea"]
        emotion = request.form["emotion"]
        perspective = request.form["perspective"]
        blog = generate_blog(idea, emotion, perspective)

        # Extract scientific basis and outcome if present
        scientific = ""
        outcome = ""
        if "Scientific Basis:" in blog and "Positive Outcome:" in blog:
            parts = blog.split("Scientific Basis:")
            intro = parts[0].strip()
            scientific_part = parts[1].split("Positive Outcome:")
            scientific = scientific_part[0].strip()
            outcome = scientific_part[1].strip()
            content = intro
        else:
            content = blog

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO blogs (idea, emotion, perspective, content, scientific, outcome) VALUES (?, ?, ?, ?, ?, ?)",
                  (idea, emotion, perspective, content, scientific, outcome))
        conn.commit()
        blog_id = c.lastrowid
        conn.close()
        return redirect(url_for("view_blog", blog_id=blog_id))
    return render_template("generate.html")

@app.route("/blog/<int:blog_id>")
def view_blog(blog_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE blogs SET views = views + 1 WHERE id = ?", (blog_id,))
    c.execute("SELECT idea, content, scientific, outcome FROM blogs WHERE id = ?", (blog_id,))
    blog = c.fetchone()
    conn.commit()
    conn.close()
    return render_template("blog.html", blog=blog)