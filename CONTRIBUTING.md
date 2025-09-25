# 🛠️ Contributing to `book_mgmt_api`

Welcome! We’re building a modular, audit-friendly book management API using Flask, SQLAlchemy, and Alembic. Contributions are not just welcome—they’re essential to making this project robust, maintainable, and empowering for users.

---

## 📦 Project Setup

To get started locally:

```bash
# Clone the repo
git clone https://github.com/<your-username>/book_mgmt_api.git
cd book_mgmt_api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Initialize DB migrations
alembic upgrade head

# Run the scaffold
python scaffold.py
