from functools import wraps
from flask import request, jsonify
from werkzeug.security import check_password_hash
from database import SessionLocal
from models import APIKey
import bcrypt

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-KEY")
        if not api_key:
            return jsonify({"error": "API key required"}), 401

        db = SessionLocal()
        valid = False
        role = None
        now = datetime.utcnow()

        for key_entry in db.query(APIKey).filter_by(active=True).all():
            if key_entry.expires_at < now:
                key_entry.active = False
                db.commit()
                continue
            if bcrypt.checkpw(api_key.encode(), key_entry.key_hash.encode()):
                valid = True
                role = key_entry.user.role
                break

        db.close()
        if not valid:
            return jsonify({"error": "Invalid or expired API key"}), 403

        request.user_role = role
        return f(*args, **kwargs)
    return decorated


def require_role(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if getattr(request, "user_role", None) not in allowed_roles:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
