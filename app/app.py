from flask import Flask, render_template, request, redirect, jsonify
import openai
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'database.db'

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                idea TEXT NOT NULL,
                scientific_basis TEXT,
                emotion TEXT,
                positive_outcome TEXT,
                tags TEXT,
                content TEXT,
                views INTEGER DEFAULT 0
            );
        """)
        conn.commit()

@app.route("/", methods=["GET"])
def home():
    conn = get_db_connection()
    trending = conn.execute("SELECT id, title FROM blogs ORDER BY views DESC LIMIT 3").fetchall()
    return render_template("index.html", trending=trending)

@app.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "POST":
        idea = request.form["idea"]
        emotion = request.form["emotion"]
        scientific_basis = request.form["scientific_basis"]
        positive_outcome = request.form["positive_outcome"]
        tags = request.form["tags"]

        prompt = f"Write a positive blog post about: {idea}. Emotional angle: {emotion}. Scientific basis: {scientific_basis}. Outcome: {positive_outcome}."

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a scientific, optimistic blog writer."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response["choices"][0]["message"]["content"]

        conn = get_db_connection()
        conn.execute("INSERT INTO blogs (title, idea, scientific_basis, emotion, positive_outcome, tags, content) VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (idea, idea, scientific_basis, emotion, positive_outcome, tags, content))
        conn.commit()
        return redirect("/")

    return render_template("generate.html")

@app.route("/autofill", methods=["POST"])
def autofill():
    data = request.json
    idea = data.get("idea", "")
    emotion = data.get("emotion", "")

    prompt = f"""Given the idea: '{idea}' and the emotion/problem: '{emotion}', generate:
    1. A scientific explanation (1–2 sentences) behind how this idea is relevant.
    2. A positive outcome (1–2 sentences) that can come from acting on this idea.
    3. A comma-separated list of 3–5 relevant tags."""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're a helpful assistant that generates scientific reasoning and blog metadata."},
            {"role": "user", "content": prompt}
        ]
    )
    content = response["choices"][0]["message"]["content"]

    lines = content.strip().split("\n")
    return jsonify({
        "scientific_basis": lines[0].strip(),
        "positive_outcome": lines[1].strip(),
        "tags": lines[2].strip().replace("Tags:", "").strip()
    })

@app.route("/health", methods=["GET", "HEAD"])
def health_check():
    return "", 200

if __name__ != "__main__":
    init_db()
