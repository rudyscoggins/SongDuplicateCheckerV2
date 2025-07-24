from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
import sqlite3

from .worker import start_scan, get_status
from .database import open_db, Session
from duplicate_finder import find_duplicates, _get_db_path
from songripper.media import read_media_info

app = FastAPI()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/scan", response_class=HTMLResponse)
def scan_page(request: Request) -> HTMLResponse:
    """Render the scan page."""
    return templates.TemplateResponse("scan.html", {"request": request})


@app.post("/scan")
def scan(root: str) -> dict[str, int]:
    engine = open_db()
    job_id = start_scan(root, engine)
    return {"task_id": job_id}


@app.get("/scan/{job_id}/status")
def scan_status(job_id: int) -> dict[str, object]:
    engine = open_db()
    return get_status(job_id, engine)


@app.get("/scan/{job_id}/progress", response_class=HTMLResponse)
def scan_progress(job_id: int) -> HTMLResponse:
    """Return HTML snippet showing progress for ``job_id``."""
    engine = open_db()
    status = get_status(job_id, engine)
    total = status.get("total", 0) or 0
    done = status.get("done", 0) or 0
    percent = int(done / total * 100) if total else 0
    if status.get("status") == "done":
        html = (
            f"<div class='w-full bg-green-500 text-white text-center py-2 rounded'>"
            f"Scan complete: {done} files</div>"
        )
    else:
        html = (
            "<div class='w-full bg-gray-200 rounded-full h-4'>"
            f"<div class='bg-blue-600 h-4 rounded-full' style='width: {percent}%'></div>"
            "</div>"
            f"<p class='text-sm mt-1'>{done}/{total} files</p>"
        )
    return HTMLResponse(html)


@app.get("/duplicates")
def list_duplicates() -> dict[str, object]:
    """Return groups of duplicate tracks with metadata."""
    engine = open_db()
    with Session(engine) as session:
        groups = find_duplicates(session)

    result = []
    for g in groups:
        files = []
        for path in g.files:
            info = read_media_info(path)
            files.append(
                {
                    "path": path,
                    "title": info.title,
                    "artist": info.artist,
                    "album": info.album,
                    "length": info.length,
                    "bitrate": info.bitrate,
                }
            )
        result.append({"files": files, "confidence": g.score})
    return {"groups": result}


@app.post("/duplicates/{group_id}/action")
def duplicate_action(group_id: int, action: str) -> dict[str, object]:
    """Perform an action on a duplicate group."""
    engine = open_db()
    with Session(engine) as session:
        groups = find_duplicates(session)

    if group_id < 0 or group_id >= len(groups):
        raise HTTPException(status_code=404, detail="group not found")

    group = groups[group_id]

    if action == "keep_newest":
        newest = max(group.files, key=lambda p: os.path.getmtime(p))
        to_delete = [p for p in group.files if p != newest]
    elif action == "trash":
        to_delete = list(group.files)
    else:
        raise HTTPException(status_code=400, detail="invalid action")

    db_path = _get_db_path(engine)
    removed = 0
    with sqlite3.connect(db_path) as conn:
        for path in to_delete:
            try:
                os.remove(path)
            except OSError:
                pass
            conn.execute("DELETE FROM track WHERE path=?", (path,))
            removed += 1
        conn.commit()

    return {"status": "ok", "removed": removed}
