# routers/sync.py
import logging
import httpx
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timezone

from config import settings
from database import get_db, SessionLocal
import models
from schemas import MusicTrackCreate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sync", tags=["Synchronizations"])

def fetch_and_store_from_lastfm():
    """Isolated background logic targeting the Last.fm pipeline."""
    url = "https://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "user.getrecenttracks",
        "user": settings.LASTFM_USERNAME,
        "api_key": settings.LASTFM_API_KEY,
        "format": "json",
        "limit": 50
    }

    try:
        response = httpx.get(url, params=params, timeout=10)
        response.raise_for_status()
    except httpx.HTTPError:
        logger.exception("Last.fm request failed")
        return

    data = response.json()
    if "error" in data:
        logger.error("Last.fm API error %s: %s", data["error"], data.get("message"))
        return

    tracks = data.get("recenttracks", {}).get("track", [])
    
    db: Session = SessionLocal()
    try:
        for track in tracks:
            if track.get("@attr", {}).get("nowplaying") == "true":
                continue
                
            uts_timestamp = int(track["date"]["uts"])
            played_at_dt = datetime.fromtimestamp(uts_timestamp, tz=timezone.utc)

            image_url = next(
                (img["#text"] for img in track.get("image", []) if img.get("size") == "extralarge" and img.get("#text")),
                None
            )

            track_data = MusicTrackCreate(
                user_id=settings.LASTFM_USERNAME,
                track_id=track.get("mbid", track["name"] + track["artist"]["#text"]),
                title=track["name"],
                artist=track["artist"]["#text"],
                image_url=image_url,
                track_url=track.get("url"),
                played_at=played_at_dt
            )

            stmt = insert(models.SpotifyHistory).values(
                user_id=track_data.user_id,
                track_id=track_data.track_id,
                title=track_data.title,
                artist=track_data.artist,
                image_url=track_data.image_url,
                track_url=track_data.track_url,
                played_at=track_data.played_at
            )
            
            stmt = stmt.on_conflict_do_nothing(index_elements=['user_id', 'played_at'])
            db.execute(stmt)
            
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to store Last.fm tracks")
    finally:
        db.close()

@router.post("")
def trigger_sync(background_tasks: BackgroundTasks):
    """Triggers historical listening scrobble streams seamlessly."""
    background_tasks.add_task(fetch_and_store_from_lastfm)
    return {"status": "Last.fm backup stream scheduled cleanly"}
