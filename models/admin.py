# models/admin.py
from sqlalchemy import Column, DateTime, String
from datetime import datetime, timezone
from database import Base

class AdminUser(Base):
    __tablename__ = "admin_users"

    username = Column(String, primary_key=True)
    password_hash = Column(String, nullable=False)

class AdminSession(Base):
    __tablename__ = "admin_sessions"

    token = Column(String, primary_key=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)

class HiddenTrack(Base):
    __tablename__ = "hidden_tracks"

    id = Column(String, primary_key=True)
    hidden_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
