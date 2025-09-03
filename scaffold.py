import os

structure = [
    "book_api",
    "book_api/routes"
]

files = [
    "book_api/app.py",
    "book_api/config.py",
    "book_api/auth.py",
    "book_api/routes/books.py",
    "book_api/requirements.txt"
]

for folder in structure:
    os.makedirs(folder, exist_ok=True)

for file in files:
    open(file, "a").close()

print("✅ Project structure created.")
