from fastapi import FastAPI

from .worker import start_scan, get_status
from .database import open_db

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
