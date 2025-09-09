from flask import Flask, request, jsonify
from functools import wraps
from datetime import datetime, timedelta
import bcrypt

from database import SessionLocal
from models import Book, APIKey

app = Flask(__name__)

# --- Decorators ---

def require_api_key(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        key = request.headers.get("X-API-KEY")
        print("🔐 Received API key:", key)

        if not key:
            return jsonify({"error": "Missing API key"}), 403

        db = SessionLocal()
        try:
            key_entries = db.query(APIKey).filter_by(active=True).all()
            for entry in key_entries:
                if bcrypt.checkpw(key.encode(), entry.key_hash.encode()):
                    if entry.expires_at < datetime.utcnow():
                        return jsonify({"error": "API key expired"}), 403

                    # Attach role to request object
                    request.user_role = entry.role
                    print("🎭 Role attached:", entry.role)
                    return view_func(*args, **kwargs)

            return jsonify({"error": "Invalid API key"}), 403

        except Exception as e:
            print("🔥 Decorator error:", str(e))
            return jsonify({"error": f"Decorator error: {str(e)}"}), 500
        finally:
            db.close()
    return wrapped_view

def require_role(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            role = getattr(request, "user_role", None)
            print("🔒 Checking role:", role)
            if role not in allowed_roles:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

# --- Routes ---

@app.route("/books", methods=["GET", "POST"])
@require_api_key
def books():
    if request.method == "GET":
        return get_books()
    elif request.method == "POST":
        return add_book()

def get_books():
    db = SessionLocal()
    try:
        books = db.query(Book).all()
        print(f"📚 Found {len(books)} books")
        return jsonify([
            {"id": b.id, "title": b.title, "author": b.author}
            for b in books
        ])
    except Exception as e:
        print("🔥 Error in get_books:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@require_role(["admin"])
def add_book():
    db = SessionLocal()
    try:
        data = request.get_json()
        print("📥 Received data:", data)

        if not data or "title" not in data or "author" not in data:
            return jsonify({"error": "Missing title or author"}), 400

        title = data["title"]
        author = data["author"]

        new_book = Book(title=title, author=author)
        db.add(new_book)
        db.commit()
        print("✅ Book added:", title, author)

        # 🔄 Fetch all books after insert
        books = db.query(Book).all()
        book_list = [
            {"id": b.id, "title": b.title, "author": b.author}
            for b in books
        ]

        return jsonify({
            "message": "Book added",
            "books": book_list
        }), 201

    except Exception as e:
        print("🔥 Error in add_book:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


# if __name__ == "__main__":
#     app.run(debug=True)