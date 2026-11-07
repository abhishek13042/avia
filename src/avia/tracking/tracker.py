"""Two-stage mask-IoU tracker with camera-motion compensation.

Uses the low-score second pass from ByteTrack, with masks warped by the estimated camera
motion before matching. Track ids are never reused and lost tracks expire early, because ID
reuse between identical apples is the failure the AppleMOTS paper reports (F10).
"""
from dataclasses import dataclass

import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment

from avia.types import Detection, TrackedObject, resolve_overlaps


@dataclass
class TrackerConfig:
    high_score: float = 0.5
    low_score: float = 0.1
    new_track_score: float = 0.6
    match_iou: float = 0.3
    low_match_iou: float = 0.5
    max_age: int = 15
    min_hits: int = 2
    scale: int = 4  # masks are matched at 1/scale resolution
    cmc: bool = True


@dataclass
class _Track:
    track_id: int
    mask: np.ndarray  # small, float32
    velocity: np.ndarray
    score: float
    hits: int = 1
    age: int = 0


def estimate_camera_motion(previous: np.ndarray, current: np.ndarray) -> np.ndarray | None:
    """Similarity transform from the previous gray frame to the current one."""
    points = cv2.goodFeaturesToTrack(previous, 300, 0.01, 12)
    if points is None or len(points) < 8:
        return None
    moved, status, _ = cv2.calcOpticalFlowPyrLK(previous, current, points, None)
    good = status.ravel() == 1
    if good.sum() < 8:
        return None
    matrix, _ = cv2.estimateAffinePartial2D(points[good], moved[good], method=cv2.RANSAC)
    return matrix


def iou_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """IoU between flattened masks a (N, P) and b (M, P)."""
    if len(a) == 0 or len(b) == 0:
        return np.zeros((len(a), len(b)), dtype=np.float32)
    intersection = a @ b.T
    union = a.sum(1, keepdims=True) + b.sum(1, keepdims=True).T - intersection
    return intersection / np.maximum(union, 1)


def _shift(mask: np.ndarray, dx: float, dy: float) -> np.ndarray:
    matrix = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(mask, matrix, mask.shape[::-1], flags=cv2.INTER_NEAREST)


def _centroid(mask: np.ndarray) -> np.ndarray:
    ys, xs = np.nonzero(mask)
    return np.array([xs.mean(), ys.mean()]) if len(xs) else np.zeros(2)


class MaskTracker:
    def __init__(self, config: TrackerConfig | None = None):
        self.config = config or TrackerConfig()
        self.tracks: list[_Track] = []
        self.next_id = 1
        self.previous_gray: np.ndarray | None = None
        self.camera: np.ndarray | None = None

    def _predict(self, gray: np.ndarray) -> None:
        c = self.config
        self.camera = None
        if c.cmc and self.previous_gray is not None:
            self.camera = estimate_camera_motion(self.previous_gray, gray)
        self.previous_gray = gray
        for t in self.tracks:
            t.age += 1
            if self.camera is not None:
                small = self.camera.copy()
                small[:, 2] /= c.scale
                t.mask = cv2.warpAffine(t.mask, small, t.mask.shape[::-1],
                                        flags=cv2.INTER_NEAREST)
            t.mask = _shift(t.mask, *t.velocity)

    def _match(self, tracks, detections, small, min_iou):
        if not tracks or not detections:
            return [], tracks, detections
        a = np.stack([t.mask.ravel() for t in tracks])
        b = np.stack([small[d].ravel() for d in detections])
        iou = iou_matrix(a, b)
        rows, cols = linear_sum_assignment(-iou)
        pairs = [(tracks[r], detections[c]) for r, c in zip(rows, cols) if iou[r, c] >= min_iou]
        used_t = {id(t) for t, _ in pairs}
        used_d = {d for _, d in pairs}
        return pairs, [t for t in tracks if id(t) not in used_t], \
            [d for d in detections if d not in used_d]

    def update(self, image_bgr: np.ndarray, detections: list[Detection]) -> list[TrackedObject]:
        c = self.config
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        self._predict(gray)
        detections = resolve_overlaps([d for d in detections if d.score >= c.low_score])
        h, w = gray.shape
        size = (w // c.scale, h // c.scale)
        small = [cv2.resize(d.mask.astype(np.float32), size, interpolation=cv2.INTER_NEAREST)
                 for d in detections]
        high = [i for i, d in enumerate(detections) if d.score >= c.high_score]
        low = [i for i, d in enumerate(detections) if d.score < c.high_score]

        pairs, rest, unmatched = self._match(self.tracks, high, small, c.match_iou)
        recent = [t for t in rest if t.age <= 1]
        low_pairs, _, _ = self._match(recent, low, small, c.low_match_iou)
        pairs += low_pairs

        output = []
        for track, index in pairs:
            before, after = _centroid(track.mask), _centroid(small[index])
            track.velocity = 0.7 * track.velocity + 0.3 * (after - before)
            track.mask, track.score, track.age = small[index], detections[index].score, 0
            track.hits += 1
            if track.hits >= c.min_hits:
                output.append(TrackedObject(track.track_id, detections[index].mask,
                                            detections[index].score))
        for index in unmatched:
            if detections[index].score >= c.new_track_score:
                self.tracks.append(_Track(self.next_id, small[index], np.zeros(2),
                                          detections[index].score))
                self.next_id += 1
        self.tracks = [t for t in self.tracks if t.age <= c.max_age]
        return output
