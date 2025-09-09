
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timedelta

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)


# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="reader")
    created_at = Column(DateTime, default=datetime.utcnow)

    api_keys = relationship("APIKey", back_populates="user")  # ← this must exist

# APIKey model
class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_hash = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    role = Column(String, nullable=False)
    user = relationship("User", back_populates="api_keys")  # ← this must match
