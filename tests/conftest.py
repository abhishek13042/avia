import os

os.environ.setdefault("AVIA_NO_APP", "1")  # tests build their own app on a temporary database

import cv2
import numpy as np
import pytest


def make_video(path: str, frames: int = 30, size=(320, 240)) -> str:
    """Three red discs drifting right over a textured background."""
    w, h = size
    rng = np.random.default_rng(0)
    background = cv2.GaussianBlur(rng.integers(0, 90, (h, w, 3), dtype=np.uint8), (5, 5), 0)
    writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"VP80"), 25, size)
    for i in range(frames):
        frame = background.copy()
        for k, (x, y) in enumerate(((60, 60), (160, 120), (240, 180))):
            cv2.circle(frame, (x + i + k, y), 14, (0, 0, 220), -1)
        writer.write(frame)
    writer.release()
    return path


@pytest.fixture
def video(tmp_path):
    return make_video(str(tmp_path / "clip.webm"))
