# main.py
from fastapi import FastAPI
from database import engine, Base
import models  # Registers SQLAlchemy schemas 
from routers import sync

app = FastAPI(title="Music History Tracker")

# Spin up PostgreSQL schema states natively
Base.metadata.create_all(bind=engine)

# Mount separate router branches cleanly
app.include_router(sync.router)

@app.get("/")
def health_check():
    return {"status": "healthy"}
