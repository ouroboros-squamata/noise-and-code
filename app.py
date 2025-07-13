from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
import openai

app = Flask(__name__)
DATABASE = 'posts.db'

openai.api_key = os.environ.get("OPENAI_API_KEY")

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

@app.route("/autogen", methods=["POST"])
def autogen():
    data = request.get_json()
    idea = data.get("idea", "")
    emotion = data.get("emotion", "")
    perspective = data.get("perspective", "")

    prompt = f"""Generate a blog title and blog content.
Idea: {idea}
Emotion/problem: {emotion}
Perspective: {perspective}

Return in this format:
Title: <title>
Content: <content>"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response['choices'][0]['message']['content']
        lines = reply.strip().split("Content:")
        title = lines[0].replace("Title:", "").strip()
        content = lines[1].strip() if len(lines) > 1 else "No content generated."

        return jsonify({"title": title, "content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return "OK"

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
