"""Add a precomputed run to the public gallery.

python scripts/seed_demo.py --video clip.mp4 --title "Orchard row"
python scripts/seed_demo.py --frames data/APPLE_MOTS/images/0010 --title "Sequence 10"
python scripts/seed_demo.py --synthetic   (local development only, labelled as untrained)

Uses DATABASE_URL, STORAGE_DIR and DETECTOR_SPEC like the worker, without the length limit.
"""
import argparse
import dataclasses
import glob
import hashlib
import os
import sys
import tempfile

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from avia.api.db import Job, Video, make_session_factory, new_id
from avia.perception.base import load_detector
from avia.settings import load_settings
from avia.storage import make_storage
from avia.worker.main import run_job


def frames_to_video(pattern_dir: str, out: str, fps: int = 10) -> None:
    paths = sorted(glob.glob(os.path.join(pattern_dir, "*")))
    first = cv2.imread(paths[0])
    writer = cv2.VideoWriter(out, cv2.VideoWriter_fourcc(*"VP80"), fps,
                             (first.shape[1], first.shape[0]))
    for path in paths:
        writer.write(cv2.imread(path))
    writer.release()


def synthetic_video(out: str, frames: int = 120, size=(640, 480)) -> None:
    w, h = size
    rng = np.random.default_rng(0)
    background = cv2.GaussianBlur(rng.integers(0, 110, (h, w, 3), dtype=np.uint8), (9, 9), 0)
    background[..., 1] = np.minimum(background[..., 1].astype(int) + 40, 255)
    points = rng.integers(40, (w * 2, h - 40), size=(24, 2))
    writer = cv2.VideoWriter(out, cv2.VideoWriter_fourcc(*"VP80"), 20, size)
    for i in range(frames):
        frame = background.copy()
        for x, y in points:
            cv2.circle(frame, (int(x) - 4 * i, int(y)), 15, (20, 20, 215), -1)
        writer.write(frame)
    writer.release()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video")
    parser.add_argument("--frames")
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--title", default="Synthetic test clip (not real data)")
    args = parser.parse_args()

    settings = dataclasses.replace(load_settings(), max_video_seconds=100000, max_video_side=10000)
    factory = make_session_factory(settings.database_url)
    storage = make_storage(settings)
    detector = load_detector(settings.detector_spec)
    with tempfile.TemporaryDirectory() as temp:
        path = args.video
        if args.frames:
            path = os.path.join(temp, "frames.webm")
            frames_to_video(args.frames, path)
        elif args.synthetic:
            path = os.path.join(temp, "synthetic.webm")
            synthetic_video(path)
        if not path:
            parser.error("give --video, --frames or --synthetic")
        with open(path, "rb") as f:
            sha256 = hashlib.file_digest(f, "sha256").hexdigest()
        video_id = new_id()
        key = f"demo/{video_id}{os.path.splitext(path)[1]}"
        storage.put(key, path)
        with factory() as s:
            s.add(Video(id=video_id, filename=args.title, storage_key=key, sha256=sha256,
                        size_bytes=os.path.getsize(path), client_hash="demo", is_demo=True))
            s.flush()
            job = Job(video_id=video_id, model=settings.detector_spec, status="running", attempts=1)
            s.add(job)
            s.commit()
            job_id = job.id
    run_job(factory, storage, detector, settings, job_id)
    with factory() as s:
        job = s.get(Job, job_id)
        print(job.status, job.run_id or job.error)


if __name__ == "__main__":
    main()
