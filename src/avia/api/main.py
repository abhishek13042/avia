"""AVIA HTTP API. Run with: uvicorn avia.api.main:app"""
import asyncio
import hashlib
import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    StreamingResponse,
)
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from avia.api.db import (
    Count,
    EventRow,
    Job,
    Run,
    Track,
    Video,
    make_session_factory,
    new_id,
    utcnow,
)
from avia.settings import Settings, load_settings
from avia.storage import make_storage

log = logging.getLogger("avia.api")
VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".mkv", ".avi"}
TERMINAL = {"done", "failed"}

# Published results from the AppleMOTS paper (De Jong et al. 2022), on the same test sequences.
PAPER_BASELINES = [
    {"model": "PointTrack", "sMOTSA": 38.7, "MOTSA": 52.9, "MOTSP": 80.0},
    {"model": "TrackR-CNN", "sMOTSA": 35.7, "MOTSA": 47.8, "MOTSP": 80.4},
]


class Orm(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class VideoOut(Orm):
    id: str
    filename: str
    size_bytes: int


class JobIn(BaseModel):
    video_id: str


class JobOut(Orm):
    id: str
    video_id: str
    status: str
    progress: float
    error: str | None
    run_id: str | None
    created_at: datetime


class RunOut(Orm):
    id: str
    title: str
    is_demo: bool
    model: str
    trained_model: bool
    frames: int
    fps_video: float
    width: int
    height: int
    fps_processed: float
    unique_apples: int
    created_at: datetime


class TrackOut(Orm):
    track_id: int
    first_frame: int
    last_frame: int
    length: int
    mean_score: float


class EventOut(Orm):
    frame: int
    track_id: int
    type: str
    event_class: str
    score: float
    details: dict


class CountOut(Orm):
    frame: int
    visible: int
    cumulative_unique: int


def looks_like_video(head: bytes) -> bool:
    """Container check only. Decoding happens in the worker, never in the API process."""
    return (head[4:8] == b"ftyp" or head[:4] == b"\x1a\x45\xdf\xa3"
            or (head[:4] == b"RIFF" and head[8:11] == b"AVI"))


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    factory = make_session_factory(settings.database_url)
    storage = make_storage(settings)
    app = FastAPI(title="AVIA API", version="0.1.0")
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                       allow_methods=["GET", "POST"], allow_headers=["*"])

    def session():
        with factory() as s:
            yield s

    def client_hash(request: Request) -> str:
        ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("x-forwarded-for")
        if settings.trust_proxy and forwarded:
            ip = forwarded.split(",")[-1].strip()  # the entry our own proxy appended
        return hashlib.sha256(f"{settings.ip_salt}:{ip}".encode()).hexdigest()

    def get_or_404(s: Session, model, row_id: str):
        row = s.get(model, row_id)
        if row is None:
            raise HTTPException(404, f"{model.__name__.lower()} not found")
        return row

    @app.middleware("http")
    async def guard(request: Request, call_next):
        request_id = uuid.uuid4().hex[:12]
        started = time.perf_counter()
        if request.method == "POST" and request.url.path == "/api/videos":
            length = request.headers.get("content-length")
            if length is None:
                return JSONResponse({"detail": "Content-Length is required"}, 411)
            if int(length) > settings.max_upload_mb * 1024 * 1024:
                return JSONResponse(
                    {"detail": f"file is larger than {settings.max_upload_mb} MB"}, 413)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        log.info(json.dumps({"id": request_id, "method": request.method,
                             "path": request.url.path, "status": response.status_code,
                             "ms": round((time.perf_counter() - started) * 1000, 1)}))
        return response

    @app.post("/api/videos", response_model=VideoOut, status_code=201)
    def upload_video(file: UploadFile, request: Request, s: Session = Depends(session)):
        if not settings.uploads_open:
            raise HTTPException(503, "uploads are off on this free demo, which has too little "
                                     "memory to run the model; run AVIA locally to try your own video")
        name = os.path.basename(file.filename or "video")
        extension = os.path.splitext(name)[1].lower()
        head = file.file.read(16)
        file.file.seek(0)
        if extension not in VIDEO_EXTENSIONS or not looks_like_video(head):
            raise HTTPException(415, "upload an MP4, MOV, WebM, MKV or AVI video")

        digest, size = hashlib.sha256(), 0
        while chunk := file.file.read(1 << 20):
            digest.update(chunk)
            size += len(chunk)
        sha256 = digest.hexdigest()
        client = client_hash(request)
        existing = s.scalar(select(Video).where(Video.sha256 == sha256,
                                                Video.client_hash == client))
        if existing:
            return existing
        since = utcnow() - timedelta(days=1)
        used = s.scalar(select(func.count()).select_from(Video).where(
            Video.client_hash == client, Video.created_at >= since))
        if used >= settings.max_uploads_per_day:
            raise HTTPException(429, f"limit of {settings.max_uploads_per_day} uploads a day")

        video_id = new_id()
        key = f"uploads/{video_id}{extension}"
        file.file.seek(0)
        temp = os.path.join(settings.storage_dir, f"incoming-{video_id}")
        os.makedirs(settings.storage_dir, exist_ok=True)
        with open(temp, "wb") as out:
            while chunk := file.file.read(1 << 20):
                out.write(chunk)
        try:
            storage.put(key, temp)
        finally:
            os.remove(temp)
        video = Video(id=video_id, filename=name[:255], storage_key=key, sha256=sha256,
                      size_bytes=size, client_hash=client)
        s.add(video)
        s.commit()
        return video

    @app.post("/api/jobs", response_model=JobOut, status_code=202)
    def create_job(body: JobIn, s: Session = Depends(session)):
        video = get_or_404(s, Video, body.video_id)
        existing = s.scalar(select(Job).where(Job.video_id == video.id,
                                              Job.model == settings.detector_spec,
                                              Job.status != "failed"))
        if existing:  # repeating the request is safe
            return existing
        queued = s.scalar(select(func.count()).select_from(Job).where(Job.status == "queued"))
        if queued >= settings.max_queue:
            raise HTTPException(503, "the queue is full, try again in a few minutes")
        job = Job(video_id=video.id, model=settings.detector_spec)
        s.add(job)
        s.commit()
        return job

    @app.get("/api/jobs/{job_id}", response_model=JobOut)
    def get_job(job_id: str, s: Session = Depends(session)):
        return get_or_404(s, Job, job_id)

    @app.get("/api/jobs/{job_id}/events")
    async def job_events(job_id: str):
        """Server-sent events: one JSON job state per change, ends when the job ends."""
        def read() -> dict | None:
            with factory() as s:
                job = s.get(Job, job_id)
                return JobOut.model_validate(job).model_dump(mode="json") if job else None

        if await run_in_threadpool(read) is None:
            raise HTTPException(404, "job not found")

        async def stream():
            last = None
            deadline = time.monotonic() + 1800
            while time.monotonic() < deadline:
                state = await run_in_threadpool(read)
                if state != last:
                    yield f"data: {json.dumps(state)}\n\n"
                    last = state
                if state["status"] in TERMINAL:
                    return
                await asyncio.sleep(1)

        return StreamingResponse(stream(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-store"})

    @app.get("/api/runs/{run_id}", response_model=RunOut)
    def get_run(run_id: str, s: Session = Depends(session)):
        return get_or_404(s, Run, run_id)

    @app.get("/api/runs/{run_id}/tracks", response_model=list[TrackOut])
    def run_tracks(run_id: str, s: Session = Depends(session)):
        get_or_404(s, Run, run_id)
        return s.scalars(select(Track).where(Track.run_id == run_id).order_by(Track.track_id)).all()

    @app.get("/api/runs/{run_id}/events", response_model=list[EventOut])
    def run_events(run_id: str, s: Session = Depends(session)):
        get_or_404(s, Run, run_id)
        return s.scalars(select(EventRow).where(EventRow.run_id == run_id)
                         .order_by(EventRow.frame, EventRow.id)).all()

    @app.get("/api/runs/{run_id}/counts", response_model=list[CountOut])
    def run_counts(run_id: str, s: Session = Depends(session)):
        get_or_404(s, Run, run_id)
        return s.scalars(select(Count).where(Count.run_id == run_id).order_by(Count.frame)).all()

    @app.get("/api/runs/{run_id}/video")
    def run_video(run_id: str, s: Session = Depends(session)):
        run = get_or_404(s, Run, run_id)
        key = f"{run.storage_prefix}/annotated.webm"
        url = storage.public_url(key)
        if url:
            return RedirectResponse(url)
        path = storage.local_path(key)
        if path is None:
            raise HTTPException(404, "video not found")
        return FileResponse(path, media_type="video/webm")

    @app.get("/api/gallery", response_model=list[RunOut])
    def gallery(s: Session = Depends(session)):
        return s.scalars(select(Run).where(Run.is_demo).order_by(Run.title)).all()

    @app.get("/api/models")
    def models():
        spec = settings.detector_spec
        return {"active": spec.split(":")[0], "trained": spec != "color"}

    @app.get("/api/limits")
    def limits():
        return {"max_upload_mb": settings.max_upload_mb,
                "max_video_seconds": settings.max_video_seconds,
                "max_uploads_per_day": settings.max_uploads_per_day,
                "retention_days": settings.retention_days}

    @app.get("/api/benchmarks")
    def benchmarks():
        """Only ever reports the file written by scripts/evaluate.py --test."""
        payload = {"status": "pending", "baselines": PAPER_BASELINES}
        if os.path.exists(settings.benchmarks_path):
            with open(settings.benchmarks_path, encoding="utf-8") as f:
                payload = {**json.load(f), "baselines": PAPER_BASELINES}
        return payload

    @app.get("/api/health")
    def health(s: Session = Depends(session)):
        s.execute(text("SELECT 1"))
        queued = s.scalar(select(func.count()).select_from(Job).where(Job.status == "queued"))
        return {"status": "ok", "queued": queued}

    @app.get("/metrics", response_class=PlainTextResponse)
    def metrics(s: Session = Depends(session)):
        rows = s.execute(select(Job.status, func.count()).group_by(Job.status)).all()
        lines = ["# TYPE avia_jobs gauge"]
        lines += [f'avia_jobs{{status="{status}"}} {count}' for status, count in rows]
        return "\n".join(lines) + "\n"

    return app


logging.basicConfig(level=logging.INFO, format="%(message)s")
app = None if os.environ.get("AVIA_NO_APP") else create_app()
