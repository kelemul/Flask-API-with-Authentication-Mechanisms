import os
from datetime import datetime

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")  # Flask sessions
    API_KEY = os.environ.get("API_KEY", "supersecretapikey")     # API key for clients
