
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import openai
import os
import json

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
DATABASE = 'database.db'

@app.route('/health')
def health():
    return "OK", 200

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea TEXT,
            emotion TEXT,
            perspective TEXT,
            title TEXT,
            content TEXT,
            niches TEXT,
            views INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM blogs ORDER BY views DESC LIMIT 10").fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/submit', methods=['POST'])
def submit():
    idea = request.form['idea']
    emotion = request.form['emotion']
    perspective = request.form['perspective']

    prompt = f"""
Given this blog idea:
Idea: {idea}
Emotion: {emotion}
Perspective: {perspective}

1. Write a full positive blog.
2. Suggest up to 3 relevant topic niches (lowercase, URL-safe) from domains like AI, environment, wellness, finance, space, technology, education, psychology, etc.
Respond in JSON:
{{
  "title": "...",
  "content": "...",
  "niches": ["niche1", "niche2"]
}}
"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    blog = response.choices[0].message.content.strip()
    parsed = json.loads(blog)
    title = parsed["title"]
    content = parsed["content"]
    niches = ",".join(parsed["niches"])

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO blogs (idea, emotion, perspective, title, content, niches) VALUES (?, ?, ?, ?, ?, ?)',
        (idea, emotion, perspective, title, content, niches)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/blog/<int:post_id>')
def blog(post_id):
    conn = get_db_connection()
    conn.execute("UPDATE blogs SET views = views + 1 WHERE id = ?", (post_id,))
    blog = conn.execute("SELECT * FROM blogs WHERE id = ?", (post_id,)).fetchone()
    conn.commit()
    conn.close()
    return render_template('blog.html', blog=blog)

@app.route('/niche/<name>')
def niche(name):
    conn = get_db_connection()
    blogs = conn.execute('SELECT * FROM blogs WHERE niches LIKE ?', (f'%{name}%',)).fetchall()
    conn.close()
    return render_template('niche.html', blogs=blogs, name=name)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
