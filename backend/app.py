import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "mydatabase")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[MONGO_DATABASE]
users = db["users"]


@app.get("/")
def home():
    return jsonify(message="Backend API is running", status="success")


@app.get("/health")
def health():
    try:
        client.admin.command("ping")
        return jsonify(status="healthy", database="connected"), 200
    except PyMongoError:
        return jsonify(status="unhealthy", database="disconnected"), 503


@app.post("/users")
def create_user():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()

    if not name or not email:
        return jsonify(message="Both name and email are required"), 400

    try:
        result = users.insert_one({"name": name, "email": email})
        return jsonify(message="User created", id=str(result.inserted_id)), 201
    except PyMongoError:
        app.logger.exception("Failed to create user")
        return jsonify(message="Database error"), 503


@app.get("/users")
def get_users():
    try:
        result = []
        for user in users.find().sort("_id", -1):
            result.append({
                "_id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
            })
        return jsonify(result)
    except PyMongoError:
        app.logger.exception("Failed to fetch users")
        return jsonify(message="Database error"), 503


@app.delete("/users/<user_id>")
def delete_user(user_id):
    if not ObjectId.is_valid(user_id):
        return jsonify(message="Invalid user ID"), 400
    try:
        result = users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            return jsonify(message="User not found"), 404
        return jsonify(message="User deleted")
    except PyMongoError:
        app.logger.exception("Failed to delete user")
        return jsonify(message="Database error"), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
