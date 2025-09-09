from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt, secrets
from database import Base, engine, SessionLocal
from models import Book, User, APIKey
from auth import require_api_key, require_role
from datetime import datetime, timedelta
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5050"}})


Base.metadata.create_all(bind=engine)


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500
import secrets

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")
    db = SessionLocal()
    if not username or not password or not role:
        return jsonify({"error": "Username, password, and role are required"}), 400
    

    # ✅ Generate secure API key
    raw_key = secrets.token_hex(16)  # e.g., '4a2e8693592bcd490ed6cbecd1618559'
    hashed_key = bcrypt.hashpw(raw_key.encode(), bcrypt.gensalt()).decode()
    expires = datetime.utcnow() + timedelta(days=30)

    
    try:
        new_key = APIKey(
            user_id=1,
            key_hash=hashed_key,
            role=role,
            active=True,
            created_at=datetime.utcnow(),
            expires_at=expires
        )
        existing = db.query(APIKey).filter_by(user_id=username, active=True).first()
        if existing:
            return jsonify({
                    "message": "API key already exists",
                    "api_key": "🔒 Not retrievable — please use your saved key"
                }), 409
        else:
            db.add(new_key)
            db.commit()
            db.close()

        # ✅ Return raw key to client
        return jsonify({
            "message": "API key registered",
            "api_key": raw_key,
            "expires_at": expires.isoformat(),
            "role": role
        }), 201
    except Exception as e:
        print("🔥 Registration error:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    db = SessionLocal()
    user = db.query(User).filter_by(username=data["username"]).first()
    if not user or not check_password_hash(user.password_hash, data["password"]):
        db.close()
        return jsonify({"error": "Invalid credentials"}), 401

    key_entry = db.query(APIKey).filter_by(user_id=user.id, active=True).first()
    db.close()
    return jsonify({"message": "Login successful", "role": user.role, "api_key": "Use the one from registration"})

@app.route("/books", methods=["GET"])
@require_api_key
def get_books():
    db = SessionLocal()
    books = db.query(Book).all()
    db.close()
    return jsonify([{"id": b.id, "title": b.title, "author": b.author} for b in books])

@app.route("/books", methods=["POST"])
@require_api_key
@require_role(["admin"])
def add_book():
    data = request.json
    db = SessionLocal()
    new_book = Book(title=data["title"], author=data["author"])
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    db.close()
    return jsonify({"id": new_book.id, "title": new_book.title, "author": new_book.author}), 201
@app.route("/rotate_key", methods=["POST"])
@require_api_key
def rotate_key():
    db = SessionLocal()
    api_key = request.headers.get("X-API-KEY")

    for key_entry in db.query(APIKey).filter_by(active=True).all():
        if bcrypt.checkpw(api_key.encode(), key_entry.key_hash.encode()):
            # Deactivate old key
            key_entry.active = False

            # Create new key
            raw_key = secrets.token_hex(16)
            hashed_key = bcrypt.hashpw(raw_key.encode(), bcrypt.gensalt()).decode()
            new_key = APIKey(
                user_id=key_entry.user_id,
                key_hash=hashed_key,
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            db.add(new_key)
            db.commit()
            db.close()
            return jsonify({"message": "API key rotated", "new_api_key": raw_key}), 201

    db.close()
    return jsonify({"error": "Invalid API key"}), 403
if __name__ == "__main__":
    app.run(debug=True)
