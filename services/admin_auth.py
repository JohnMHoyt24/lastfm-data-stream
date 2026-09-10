# services/admin_auth.py
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

import models
from database import get_db

SESSION_TTL = timedelta(hours=12)

def verify_credentials(db: Session, username: str, password: str) -> bool:
    admin = db.query(models.AdminUser).filter(models.AdminUser.username == username).first()
    if not admin:
        return False

    return bcrypt.checkpw(password.encode("utf-8"), admin.password_hash.encode("utf-8"))

def create_session(db: Session) -> str:
    token = secrets.token_hex(32)
    db.add(models.AdminSession(
        token=token,
        expires_at=datetime.now(timezone.utc) + SESSION_TTL,
    ))
    db.commit()
    return token

def revoke_session(db: Session, token: str) -> None:
    db.query(models.AdminSession).filter(models.AdminSession.token == token).delete()
    db.commit()

def extract_bearer_token(authorization: str | None) -> str | None:
    if authorization and authorization.startswith("Bearer "):
        return authorization[len("Bearer "):]
    return None

def require_admin(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> None:
    token = extract_bearer_token(authorization)
    session = (
        db.query(models.AdminSession).filter(models.AdminSession.token == token).first()
        if token else None
    )

    if not session or session.expires_at < datetime.now(timezone.utc):
        if session:
            db.delete(session)
            db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
