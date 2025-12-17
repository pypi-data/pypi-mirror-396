# gate/ext/server.py

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import router

app = FastAPI(title="Revert Gateway", version="0.1.0")

# API routes
app.include_router(router, prefix="/api")

# ------------------------------
# Serve bundled frontend (if present)
# ------------------------------

BASE_DIR = Path(__file__).resolve().parent
UI_DIR = BASE_DIR / "ui"

if UI_DIR.is_dir():
    # Serve the built SPA from the installed package directory.
    # The root path ("/") will serve index.html, and static assets
    # (JS/CSS) are resolved relative to that file.
    app.mount("/", StaticFiles(directory=str(UI_DIR), html=True), name="ui")
