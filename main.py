# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import engine, Base
import models  # Registers SQLAlchemy schemas
from routers import sync, tracks

app = FastAPI(title="Music History Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Spin up PostgreSQL schema states natively
Base.metadata.create_all(bind=engine)

# Mount separate router branches cleanly
app.include_router(sync.router)
app.include_router(tracks.router)

@app.get("/")
def health_check():
    return {"status": "healthy"}
