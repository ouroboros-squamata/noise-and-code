from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    db = get_db_connection()
    posts = db.execute("SELECT * FROM posts ORDER BY views DESC LIMIT 10").fetchall()
    db.close()
    return render_template("index.html", trending=posts)

@app.route('/generate', methods=['POST'])
def generate():
    idea = request.form['idea']
    emotion = request.form['emotion']
    perspective = request.form['perspective']
    content = "Generated blog content based on inputs."  # Placeholder content generation logic
    db = get_db_connection()
    db.execute(
        "INSERT INTO posts (idea, emotion, perspective, content, created_at, views) VALUES (?, ?, ?, ?, ?, ?)",
        (idea, emotion, perspective, content, datetime.datetime.now(), 0)
    )
    db.commit()
    db.close()
    return redirect(url_for('home'))

@app.route('/health')
def health():
    return "OK"

if __name__ == '__main__':
    app.run(debug=True)
