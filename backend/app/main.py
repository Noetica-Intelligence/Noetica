from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import engine, Base
from .api import endpoints
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Scientific Intelligence Platform API",
    description="V2 Backend - PostgreSQL, FastAPI, SQLAlchemy",
    version="2.0.0"
)

origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
def read_root():
    """Health check endpoint for Hugging Face."""
    return {"status": "ok", "message": "Noetica API is running"}
