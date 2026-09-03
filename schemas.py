# schemas.py
from pydantic import BaseModel
from datetime import datetime

class MusicTrackBase(BaseModel):
    user_id: str
    track_id: str
    title: str
    artist: str
    played_at: datetime

class MusicTrackCreate(MusicTrackBase):
    pass

class MusicTrackResponse(MusicTrackBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
