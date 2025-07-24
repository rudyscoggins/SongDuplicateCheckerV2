from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .settings import NAS_PATH
from .worker import AUDIO_EXT

app = FastAPI()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def _find_first_file(root: Path) -> Path | None:
    """Return the first audio file found under ``root``."""
    for path in sorted(root.rglob(f"*{AUDIO_EXT}")):
        if path.is_file():
            return path
    return None


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    path = _find_first_file(NAS_PATH)
    message = str(path) if path is not None else "No files found"
    return templates.TemplateResponse(
        "base.html",
        {"request": request, "message": message},
    )
