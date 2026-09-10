# schemas.py
from pydantic import BaseModel
from datetime import datetime

class MusicTrackBase(BaseModel):
    user_id: str
    track_id: str
    title: str
    artist: str
    image_url: str | None = None
    track_url: str | None = None
    played_at: datetime

class MusicTrackCreate(MusicTrackBase):
    pass

class MusicTrackResponse(MusicTrackBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    token: str

class HiddenTracksResponse(BaseModel):
    hidden_ids: list[str]

class HideTrackRequest(BaseModel):
    id: str
