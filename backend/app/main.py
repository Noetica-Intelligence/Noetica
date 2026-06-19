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

# Mount the static directory for the V2 Dashboard
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
def read_root():
    """Serve the User Dashboard as the root."""
    return FileResponse(os.path.join(static_dir, "index.html"))


