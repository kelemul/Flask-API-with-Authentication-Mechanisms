# 📚 Book Management API

A modular, audit-friendly RESTful API for managing books—built with Flask, SQLAlchemy, and Alembic. Designed for clarity, upgrade safety, and future-proof extensibility.

---

## 🚀 Features

- Add, update, delete, and list books
- SQLite-powered with Alembic migrations
- Marshmallow schemas for clean serialization
- Audit-friendly structure with explicit validation
- Easily extendable for reviews, authors, or asset tracking

---

## 🛠️ Setup Instructions

```bash
# Create project folder
mkdir book_mgmt_api && cd book_mgmt_api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install flask flask_sqlalchemy flask_marshmallow

# Save dependencies
pip freeze > requirements.txt
