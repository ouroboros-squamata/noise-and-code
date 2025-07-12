import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime
import uuid
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.before_request
def handle_head():
    if request.method == 'HEAD':
        # Flask won't call route functions for HEAD, so we handle it manually
        return "", 200

@app.route("/health", methods=["GET", "HEAD"])
def health_check():
    return "", 200

def init_db():
    with sqlite3.connect("database.db") as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS blogs (
            id TEXT PRIMARY KEY,
            title TEXT,
            content TEXT,
            views INTEGER DEFAULT 0,
            created_at TEXT,
            tags TEXT
        )
        """)
        conn.commit()

@app.route("/", methods=["GET", "HEAD"])
def home():
    with sqlite3.connect("database.db") as conn:
        trending = conn.execute("SELECT id, title FROM blogs ORDER BY views DESC LIMIT 3").fetchall()
    return render_template("index.html", blogs=trending)

@app.route("/generate", methods=["GET", "POST", "HEAD"])
def generate():
    if request.method == "POST":
        idea = request.form["idea"]
        logic = request.form["scientific_basis"]
        emotion = request.form["emotion_or_problem"]
        outcome = request.form["outcome"]
        tags = request.form.get("tags", "").strip().lower()

        prompt = f"""
        Turn the following idea into a positive, belief-driven blog post with logic and scientific reasoning.

        Idea: {idea}
        Scientific Basis: {logic}
        Emotion: {emotion}
        Positive Outcome: {outcome}

        The blog should always find an optimistic interpretation and use science to support and refine the belief.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800
            )
            content = response['choices'][0]['message']['content']
        except Exception as e:
            content = f"<p>Error generating blog: {str(e)}</p>"

        title = f"Belief Blog: {idea[:50]}"
        post_id = str(uuid.uuid4())
        with sqlite3.connect("database.db") as conn:
            conn.execute("INSERT INTO blogs (id, title, content, created_at, tags) VALUES (?, ?, ?, ?, ?)",
                         (post_id, title, content, datetime.now().isoformat(), tags))
            conn.commit()
        return redirect(url_for("view_blog", blog_id=post_id))
    return render_template("generate.html")

@app.route("/blog/<blog_id>", methods=["GET", "HEAD"])
def view_blog(blog_id):
    with sqlite3.connect("database.db") as conn:
        blog = conn.execute("SELECT * FROM blogs WHERE id = ?", (blog_id,)).fetchone()
        if blog:
            conn.execute("UPDATE blogs SET views = views + 1 WHERE id = ?", (blog_id,))
            conn.commit()
            return render_template("blog.html", blog=blog)
    return "Blog not found", 404

@app.route("/recent", methods=["GET", "HEAD"])
def recent():
    with sqlite3.connect("database.db") as conn:
        blogs = conn.execute("SELECT id, title FROM blogs ORDER BY created_at DESC LIMIT 10").fetchall()
    return render_template("recent.html", blogs=blogs)

@app.route("/all", methods=["GET", "HEAD"])
def all_blogs():
    with sqlite3.connect("database.db") as conn:
        blogs = conn.execute("SELECT id, title FROM blogs ORDER BY created_at DESC").fetchall()
    return render_template("all.html", blogs=blogs)

@app.route("/tags/<tag>", methods=["GET", "HEAD"])
def blogs_by_tag(tag):
    with sqlite3.connect("database.db") as conn:
        blogs = conn.execute("SELECT id, title FROM blogs WHERE tags LIKE ?", (f"%{tag}%",)).fetchall()
    return render_template("tags.html", blogs=blogs, tag=tag)

@app.route("/api/blogs")
def api_all_blogs():
    with sqlite3.connect("database.db") as conn:
        blogs = conn.execute("SELECT id, title, created_at, views FROM blogs").fetchall()
    return jsonify([{"id": b[0], "title": b[1], "created_at": b[2], "views": b[3]} for b in blogs])

@app.route("/api/blogs/<blog_id>")
def api_single_blog(blog_id):
    with sqlite3.connect("database.db") as conn:
        blog = conn.execute("SELECT * FROM blogs WHERE id = ?", (blog_id,)).fetchone()
    if blog:
        return jsonify({
            "id": blog[0],
            "title": blog[1],
            "content": blog[2],
            "views": blog[3],
            "created_at": blog[4],
            "tags": blog[5]
        })
    return jsonify({"error": "Not found"}), 404

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
