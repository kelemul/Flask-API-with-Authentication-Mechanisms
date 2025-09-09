from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt, secrets
from database import Base, engine, SessionLocal
from models import Book, User, APIKey
from auth import require_api_key, require_role

app = Flask(__name__)
Base.metadata.create_all(bind=engine)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    db = SessionLocal()
    if db.query(User).filter_by(username=data["username"]).first():
        db.close()
        return jsonify({"error": "User exists"}), 400

    user = User(
        username=data["username"],
        password_hash=generate_password_hash(data["password"]),
        role=data.get("role", "reader")
    )
    db.add(user)
    db.commit()

    raw_key = secrets.token_hex(16)
    hashed_key = bcrypt.hashpw(raw_key.encode(), bcrypt.gensalt()).decode()
    api_key_entry = APIKey(user_id=user.id, key_hash=hashed_key)
    db.add(api_key_entry)
    db.commit()
    db.close()

    return jsonify({"message": "User registered", "api_key": raw_key}), 201

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
