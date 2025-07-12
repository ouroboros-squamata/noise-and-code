import os
from flask import Flask, request, render_template, redirect, url_for
from openai import OpenAI
import stripe
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
openai_api_key = os.getenv("OPENAI_API_KEY")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
YOUR_DOMAIN = os.getenv("DOMAIN", "http://localhost:5000")

# Dummy content generation logic
def is_sales_pitch(text):
    sales_keywords = ["buy", "offer", "limited", "discount", "deal", "enroll", "get your", "subscribe"]
    return any(kw in text.lower() for kw in sales_keywords)

@app.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "POST":
        idea = request.form["idea"]
        emotion = request.form.get("emotion", "")
        wants_promotion = "promotion" in request.form

        if is_sales_pitch(idea + emotion):
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "Sales Pitch Blog Generation"},
                        "unit_amount": 500,  # $5
                    },
                    "quantity": 1,
                }] + ([{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "Homepage Promotion"},
                        "unit_amount": 500,  # $5
                    },
                    "quantity": 1,
                }] if wants_promotion else []),
                mode="payment",
                success_url=f"{YOUR_DOMAIN}/success",
                cancel_url=f"{YOUR_DOMAIN}/cancel",
            )
            return redirect(session.url, code=303)

        return render_template("blog.html", title="Your Blog", content="AI-generated content here.")
    return render_template("generate.html")

@app.route("/success")
def success():
    return "<h2>Payment successful. Your blog is being generated...</h2>"

@app.route("/cancel")
def cancel():
    return "<h2>Payment was cancelled.</h2>"

if __name__ == "__main__":
    app.run(debug=True)
