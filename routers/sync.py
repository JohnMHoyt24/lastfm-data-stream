# routers/sync.py
import httpx
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timezone

from config import settings
from database import get_db, SessionLocal
import models
from schemas import MusicTrackCreate

router = APIRouter(prefix="/sync", tags=["Synchronizations"])

def fetch_and_store_from_lastfm():
    """Isolated background logic targeting the Last.fm pipeline."""
    url = "http://audioscrobbler.com"
    params = {
        "method": "user.getrecenttracks",
        "user": settings.LASTFM_USERNAME,
        "api_key": settings.LASTFM_API_KEY,
        "format": "json",
        "limit": 50
    }
    
    response = httpx.get(url, params=params)
    if response.status_code != 200:
        return
        
    data = response.json()
    tracks = data.get("recenttracks", {}).get("track", [])
    
    db: Session = SessionLocal()
    try:
        for track in tracks:
            if track.get("@attr", {}).get("nowplaying") == "true":
                continue
                
            uts_timestamp = int(track["date"]["uts"])
            played_at_dt = datetime.fromtimestamp(uts_timestamp, tz=timezone.utc)
            
            track_data = MusicTrackCreate(
                user_id=settings.LASTFM_USERNAME,
                track_id=track.get("mbid", track["name"] + track["artist"]["#text"]),
                title=track["name"],
                artist=track["artist"]["#text"],
                played_at=played_at_dt
            )
            
            stmt = insert(models.SpotifyHistory).values(
                user_id=track_data.user_id,
                track_id=track_data.track_id,
                title=track_data.title,
                artist=track_data.artist,
                played_at=track_data.played_at
            )
            
            stmt = stmt.on_conflict_do_nothing(index_elements=['user_id', 'played_at'])
            db.execute(stmt)
            
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error executing backend router task: {e}")
    finally:
        db.close()

@router.post("")
def trigger_sync(background_tasks: BackgroundTasks):
    """Triggers historical listening scrobble streams seamlessly."""
    background_tasks.add_task(fetch_and_store_from_lastfm)
    return {"status": "Last.fm backup stream scheduled cleanly"}
