from flask import Flask, render_template, request
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_field(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=150
    )
    return response.choices[0].message["content"].strip()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    idea = request.form["idea"]
    emotion = request.form["emotion"]

    scientific_basis = generate_field(f"What is a possible scientific basis for this idea: '{idea}'?")
    positive_outcome = generate_field(f"What is a possible positive outcome for an idea like this motivated by the emotion: '{emotion}'?")

    blog = generate_field(f"Write a blog based on the idea '{idea}' with the emotion '{emotion}', scientific basis '{scientific_basis}', and positive outcome '{positive_outcome}'.")

    return render_template("index.html", blog=blog, scientific_basis=scientific_basis, positive_outcome=positive_outcome)

if __name__ == "__main__":
    app.run(debug=True)
