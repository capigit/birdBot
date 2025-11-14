from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Dossier des templates
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Renvoie l'interface HTML BirdBot."""
    with open(os.path.join(TEMPLATE_PATH, "ui.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())