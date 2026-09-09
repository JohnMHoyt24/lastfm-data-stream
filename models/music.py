# models/music.py
from sqlalchemy import Column, BigInteger, String, DateTime, UniqueConstraint
from datetime import datetime, timezone
from database import Base

class SpotifyHistory(Base):
    __tablename__ = "spotify_history"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    track_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    track_url = Column(String, nullable=True)
    played_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('user_id', 'played_at', name='_user_played_uc'),
    )
