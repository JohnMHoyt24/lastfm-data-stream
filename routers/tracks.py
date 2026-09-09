# routers/tracks.py
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import MusicTrackResponse

router = APIRouter(prefix="/tracks", tags=["Tracks"])

@router.get("/recent", response_model=List[MusicTrackResponse])
def get_recent_tracks(limit: int = 12, db: Session = Depends(get_db)):
    return (
        db.query(models.SpotifyHistory)
        .order_by(models.SpotifyHistory.played_at.desc())
        .limit(limit)
        .all()
    )
