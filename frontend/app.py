import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-change-me")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5001")


@app.route("/", methods=["GET"])
def home():
    try:
        response = requests.get(f"{BACKEND_URL}/users", timeout=5)
        response.raise_for_status()
        users = response.json()
        error = None
    except requests.RequestException:
        users = []
        error = "Backend is unavailable. Please try again."

    return render_template("index.html", users=users, error=error)


@app.route("/add", methods=["POST"])
def add_user():
    payload = {
        "name": request.form.get("name", "").strip(),
        "email": request.form.get("email", "").strip(),
    }
    try:
        response = requests.post(f"{BACKEND_URL}/users", json=payload, timeout=5)
        response.raise_for_status()
        flash("User created successfully.")
    except requests.RequestException:
        flash("Could not create user. Check the backend.")
    return redirect(url_for("home"))


@app.route("/delete/<user_id>", methods=["POST"])
def delete_user(user_id):
    try:
        response = requests.delete(f"{BACKEND_URL}/users/{user_id}", timeout=5)
        response.raise_for_status()
        flash("User deleted.")
    except requests.RequestException:
        flash("Could not delete user.")
    return redirect(url_for("home"))


@app.get("/health")
def health():
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
