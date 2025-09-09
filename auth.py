from functools import wraps
from flask import request, jsonify
from werkzeug.security import check_password_hash
from database import SessionLocal
from models import APIKey
import bcrypt
from datetime import datetime, timedelta


from flask import request, jsonify, g  # add g if you prefer

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

                    # ✅ Attach role to request object
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
            if getattr(request, "user_role", None) not in allowed_roles:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
