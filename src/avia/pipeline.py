"""Video -> detections -> tracks -> events -> stored result files."""
import colorsys
import gzip
import json
import os
import time
from collections.abc import Callable

import cv2
import numpy as np

from avia.data import rle
from avia.events.engine import EventEngine
from avia.perception.base import Detector
from avia.tracking.tracker import MaskTracker, TrackerConfig
from avia.types import TrackedObject


def track_color(track_id: int) -> tuple[int, int, int]:
    r, g, b = colorsys.hsv_to_rgb((track_id * 0.618034) % 1.0, 0.8, 1.0)
    return int(b * 255), int(g * 255), int(r * 255)


def draw(frame: np.ndarray, objects: list[TrackedObject]) -> np.ndarray:
    out = frame.copy()
    for obj in objects:
        color = np.array(track_color(obj.track_id), dtype=np.uint8)
        out[obj.mask] = (0.5 * out[obj.mask] + 0.5 * color).astype(np.uint8)
    for obj in objects:
        x0, y0, _, _ = obj.box
        cv2.putText(out, str(obj.track_id), (x0, max(y0 - 3, 10)), cv2.FONT_HERSHEY_SIMPLEX,
                    0.45, track_color(obj.track_id), 1, cv2.LINE_AA)
    return out


def process_video(path: str, out_dir: str, detector: Detector,
                  tracker_config: TrackerConfig | None = None,
                  progress: Callable[[float], None] | None = None,
                  max_seconds: float | None = None, max_side: int | None = None) -> dict:
    """Raises ValueError for a bad video; the worker shows that message to the uploader."""
    capture = cv2.VideoCapture(path)
    if not capture.isOpened():
        raise ValueError("could not read the video")
    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if max_seconds and total / fps > max_seconds:
        capture.release()
        raise ValueError(f"video is longer than the {max_seconds:.0f} s limit")
    if max_side and max(width, height) > max_side:
        capture.release()
        raise ValueError(f"video is larger than the {max_side} px limit")

    os.makedirs(out_dir, exist_ok=True)
    # VP8 in WebM plays in every browser and ships inside the OpenCV wheels.
    writer = cv2.VideoWriter(os.path.join(out_dir, "annotated.webm"),
                             cv2.VideoWriter_fourcc(*"VP80"), fps, (width, height))
    tracker = MaskTracker(tracker_config)
    engine = EventEngine()
    tracks: dict[int, dict] = {}
    index = 0
    started = time.perf_counter()
    with gzip.open(os.path.join(out_dir, "masks.jsonl.gz"), "wt", encoding="utf-8") as masks:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if max_seconds and index > max_seconds * fps:  # the header frame count can lie
                raise ValueError(f"video is longer than the {max_seconds:.0f} s limit")
            objects = tracker.update(frame, detector.detect(frame))
            engine.update(index, {o.track_id: o.centroid for o in objects})
            for obj in objects:
                t = tracks.setdefault(obj.track_id, {"track_id": obj.track_id, "first_frame": index,
                                                     "length": 0, "score_sum": 0.0})
                t["last_frame"] = index
                t["length"] += 1
                t["score_sum"] += obj.score
                masks.write(json.dumps({"frame": index, "track_id": obj.track_id,
                                        "score": round(obj.score, 4),
                                        "rle": rle.encode(obj.mask)}) + "\n")
            writer.write(draw(frame, objects))
            index += 1
            if progress and total and index % 10 == 0:
                progress(min(index / total, 0.99))
    elapsed = time.perf_counter() - started
    capture.release()
    writer.release()
    if index == 0:
        raise ValueError("the video has no readable frames")

    track_rows = []
    for t in tracks.values():
        t["mean_score"] = round(t.pop("score_sum") / t["length"], 4)
        track_rows.append(t)
    result = {
        "model": detector.name, "trained_model": detector.trained,
        "frames": index, "fps_video": fps, "width": width, "height": height,
        "fps_processed": round(index / elapsed, 2), **engine.summary(),
    }
    for name, value in (("result", result), ("tracks", track_rows),
                        ("events", engine.events), ("counts", engine.counts)):
        with open(os.path.join(out_dir, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(value, f)
    return result
