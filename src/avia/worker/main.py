"""Job worker: claims queued jobs from the database, runs the pipeline, stores results.

The queue is the jobs table (D-024). Claiming is one conditional UPDATE, so several workers can
share it on Postgres or SQLite. Run with: python -m avia.worker.main
"""
import json
import logging
import os
import tempfile
import time
from datetime import timedelta

from sqlalchemy import delete, select, update
from sqlalchemy.orm import sessionmaker

from avia.api.db import Count, EventRow, Job, Run, Track, Video, make_session_factory, utcnow
from avia.perception.base import Detector, load_detector
from avia.pipeline import process_video
from avia.settings import Settings, load_settings
from avia.storage import make_storage

log = logging.getLogger("avia.worker")
RESULT_FILES = ("annotated.webm", "masks.jsonl.gz", "result.json", "tracks.json", "events.json",
                "counts.json")
FRIENDLY_FAILURE = "processing failed, please try another video"


def claim_next(factory: sessionmaker) -> str | None:
    with factory() as s:
        job_id = s.scalar(select(Job.id).where(Job.status == "queued")
                          .order_by(Job.created_at).limit(1))
        if job_id is None:
            return None
        now = utcnow()
        claimed = s.execute(update(Job).where(Job.id == job_id, Job.status == "queued").values(
            status="running", attempts=Job.attempts + 1, started_at=now, heartbeat_at=now,
            progress=0.0))
        s.commit()
        return job_id if claimed.rowcount == 1 else None


def requeue_stale(factory: sessionmaker, settings: Settings) -> int:
    """Return jobs from crashed workers to the queue, or fail them after max_attempts."""
    cutoff = utcnow() - timedelta(seconds=settings.stale_seconds)
    with factory() as s:
        stale = s.scalars(select(Job).where(Job.status == "running",
                                            Job.heartbeat_at < cutoff)).all()
        for job in stale:
            if job.attempts >= settings.max_attempts:
                job.status, job.error, job.finished_at = "failed", FRIENDLY_FAILURE, utcnow()
            else:
                job.status = "queued"
        s.commit()
        return len(stale)


def _finish_failed(factory, job_id, settings, error: Exception) -> None:
    with factory() as s:
        job = s.get(Job, job_id)
        if isinstance(error, ValueError):  # the video is at fault: retrying cannot help
            job.status, job.error = "failed", str(error)
        elif job.attempts >= settings.max_attempts:
            job.status, job.error = "failed", FRIENDLY_FAILURE
        else:
            job.status = "queued"
        if job.status == "failed":
            job.finished_at = utcnow()
        s.commit()


def _store_results(factory, storage, job_id, out_dir, result, title, is_demo) -> None:
    prefix = f"runs/{job_id}"
    for name in RESULT_FILES:
        storage.put(f"{prefix}/{name}", os.path.join(out_dir, name))

    def read(name):
        with open(os.path.join(out_dir, f"{name}.json"), encoding="utf-8") as f:
            return json.load(f)

    with factory() as s:
        job = s.get(Job, job_id)
        run = Run(job_id=job_id, title=title, is_demo=is_demo, model=result["model"],
                  trained_model=result["trained_model"], frames=result["frames"],
                  fps_video=result["fps_video"], width=result["width"], height=result["height"],
                  fps_processed=result["fps_processed"], unique_apples=result["unique_apples"],
                  storage_prefix=prefix)
        s.add(run)
        s.flush()
        s.add_all(Track(run_id=run.id, **row) for row in read("tracks"))
        s.add_all(EventRow(run_id=run.id, **row) for row in read("events"))
        s.add_all(Count(run_id=run.id, **row) for row in read("counts"))
        job.status, job.run_id, job.progress, job.finished_at = "done", run.id, 1.0, utcnow()
        s.commit()


def run_job(factory, storage, detector: Detector, settings: Settings, job_id: str) -> None:
    with factory() as s:
        job = s.get(Job, job_id)
        video = s.get(Video, job.video_id)
        key, title, is_demo = video.storage_key, video.filename, video.is_demo

    def progress(fraction: float) -> None:
        with factory() as s:
            s.execute(update(Job).where(Job.id == job_id).values(progress=round(fraction, 3),
                                                                 heartbeat_at=utcnow()))
            s.commit()

    try:
        with tempfile.TemporaryDirectory() as temp:
            source = os.path.join(temp, "input" + os.path.splitext(key)[1])
            storage.fetch(key, source)
            out_dir = os.path.join(temp, "out")
            result = process_video(source, out_dir, detector, progress=progress,
                                   max_seconds=settings.max_video_seconds,
                                   max_side=settings.max_video_side)
            _store_results(factory, storage, job_id, out_dir, result, title, is_demo)
    except ValueError as error:
        log.info("job %s rejected: %s", job_id, error)
        _finish_failed(factory, job_id, settings, error)
    except Exception as error:
        log.exception("job %s failed", job_id)
        _finish_failed(factory, job_id, settings, error)


def delete_expired(factory, storage, settings: Settings) -> int:
    """Remove uploads and everything derived from them after the retention period."""
    cutoff = utcnow() - timedelta(days=settings.retention_days)
    with factory() as s:
        videos = s.scalars(select(Video).where(~Video.is_demo, Video.created_at < cutoff)).all()
        for video in videos:
            jobs = s.scalars(select(Job).where(Job.video_id == video.id)).all()
            for job in jobs:
                if job.status in ("queued", "running"):
                    break
            else:
                for job in jobs:
                    storage.delete_prefix(f"runs/{job.id}")
                    if job.run_id:
                        for table in (Track, EventRow, Count):
                            s.execute(delete(table).where(table.run_id == job.run_id))
                        s.execute(delete(Run).where(Run.id == job.run_id))
                    s.delete(job)
                s.flush()
                storage.delete(video.storage_key)
                s.delete(video)
        s.commit()
        return len(videos)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    settings = load_settings()
    factory = make_session_factory(settings.database_url)
    storage = make_storage(settings)
    detector = load_detector(settings.detector_spec)
    log.info("worker ready, model %s", detector.name)
    next_cleanup = 0.0
    while True:
        if time.monotonic() >= next_cleanup:
            requeue_stale(factory, settings)
            delete_expired(factory, storage, settings)
            next_cleanup = time.monotonic() + 60
        job_id = claim_next(factory)
        if job_id:
            run_job(factory, storage, detector, settings, job_id)
        else:
            time.sleep(1)


if __name__ == "__main__":
    main()
