from fastapi import FastAPI, HTTPException
import os
import sqlite3

from .worker import start_scan, get_status
from .database import open_db, Session
from duplicate_finder import find_duplicates, _get_db_path
from songripper.media import read_media_info

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scan")
def scan(root: str) -> dict[str, int]:
    engine = open_db()
    job_id = start_scan(root, engine)
    return {"task_id": job_id}


@app.get("/scan/{job_id}/status")
def scan_status(job_id: int) -> dict[str, object]:
    engine = open_db()
    return get_status(job_id, engine)


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
