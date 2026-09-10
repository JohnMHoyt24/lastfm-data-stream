# routers/admin.py
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import (
    AdminLoginRequest,
    AdminLoginResponse,
    HiddenTracksResponse,
    HideTrackRequest,
)
from services.admin_auth import (
    create_session,
    extract_bearer_token,
    require_admin,
    revoke_session,
    verify_credentials,
)

router = APIRouter(prefix="/admin", tags=["Admin"])

def _hidden_ids(db: Session) -> list[str]:
    return [row.id for row in db.query(models.HiddenTrack.id).all()]

@router.post("/login", response_model=AdminLoginResponse)
def login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    if not verify_credentials(db, payload.username, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return AdminLoginResponse(token=create_session(db))

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    token = extract_bearer_token(authorization)
    if token:
        revoke_session(db, token)

@router.get("/hidden-tracks", response_model=HiddenTracksResponse)
def get_hidden_tracks(db: Session = Depends(get_db)):
    return HiddenTracksResponse(hidden_ids=_hidden_ids(db))

@router.post("/hidden-tracks", response_model=HiddenTracksResponse, dependencies=[Depends(require_admin)])
def hide_track(payload: HideTrackRequest, db: Session = Depends(get_db)):
    if not db.query(models.HiddenTrack).filter(models.HiddenTrack.id == payload.id).first():
        db.add(models.HiddenTrack(id=payload.id))
        db.commit()
    return HiddenTracksResponse(hidden_ids=_hidden_ids(db))

@router.delete("/hidden-tracks/{track_id}", response_model=HiddenTracksResponse, dependencies=[Depends(require_admin)])
def unhide_track(track_id: str, db: Session = Depends(get_db)):
    db.query(models.HiddenTrack).filter(models.HiddenTrack.id == track_id).delete()
    db.commit()
    return HiddenTracksResponse(hidden_ids=_hidden_ids(db))
