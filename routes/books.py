# app.py
from flask import Flask, request, jsonify
from database import SessionLocal, engine, Base
from models import Book

app = Flask(__name__)
Base.metadata.create_all(bind=engine)

@app.route("/books", methods=["GET"])
def get_books():
    db = SessionLocal()
    books = db.query(Book).all()
    db.close()
    return jsonify([{"id": b.id, "title": b.title, "author": b.author} for b in books])

@app.route("/books", methods=["POST"])
def add_book():
    data = request.json
    db = SessionLocal()
    new_book = Book(title=data["title"], author=data["author"])
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    db.close()
    return jsonify({"id": new_book.id, "title": new_book.title, "author": new_book.author}), 201
