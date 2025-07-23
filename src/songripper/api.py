from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .settings import NAS_PATH
from .worker import AUDIO_EXT

app = FastAPI()


def _find_first_file(root: Path) -> Path | None:
    """Return the first audio file found under ``root``."""
    for path in sorted(root.rglob(f"*{AUDIO_EXT}")):
        if path.is_file():
            return path
    return None


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    path = _find_first_file(NAS_PATH)
    if path is None:
        return HTMLResponse("No files found")
    return HTMLResponse(str(path))
