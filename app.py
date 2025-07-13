from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/generate")
def generate():
    return render_template("generate.html")

@app.route("/all")
def all_blogs():
    return render_template("all.html")

@app.route("/recent")
def recent_blogs():
    return render_template("recent.html")

@app.route("/health")
def health():
    return "OK"

if __name__ == "__main__":
    app.run(debug=True)
