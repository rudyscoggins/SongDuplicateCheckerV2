from fastapi import FastAPI

from .worker import start_scan, get_status
from .database import open_db, Session
from duplicate_finder import find_duplicates
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
