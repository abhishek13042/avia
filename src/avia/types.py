"""Types shared by perception, tracking and the pipeline."""
from dataclasses import dataclass

import numpy as np


@dataclass
class Detection:
    mask: np.ndarray  # bool, H x W
    score: float


@dataclass
class TrackedObject:
    track_id: int
    mask: np.ndarray
    score: float

    @property
    def centroid(self) -> tuple[float, float]:
        ys, xs = np.nonzero(self.mask)
        return float(xs.mean()), float(ys.mean())

    @property
    def box(self) -> list[int]:
        ys, xs = np.nonzero(self.mask)
        return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def resolve_overlaps(detections: list[Detection]) -> list[Detection]:
    """Give each pixel to the highest-scoring detection, as MOTS requires."""
    taken = None
    out = []
    for det in sorted(detections, key=lambda d: d.score, reverse=True):
        mask = det.mask if taken is None else det.mask & ~taken
        taken = mask.copy() if taken is None else taken | mask
        if mask.any():
            out.append(Detection(mask, det.score))
    return out
