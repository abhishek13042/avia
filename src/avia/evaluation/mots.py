"""CLEAR-MOTS metrics (sMOTSA, MOTSA, MOTSP) and KITTI MOTS txt output for TrackEval.

Mask HOTA, the primary metric, comes from TrackEval on the txt files written here.
"""
import numpy as np

from avia.data import rle


def _box(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    ys, xs = np.flatnonzero(mask.any(axis=1)), np.flatnonzero(mask.any(axis=0))
    return None if ys.size == 0 else (ys[0], ys[-1] + 1, xs[0], xs[-1] + 1)


def _iou(a: np.ndarray, a_box, a_area: int, b: np.ndarray, b_box, b_area: int) -> float:
    if a_box is None or b_box is None:
        return 0.0
    y0, y1 = max(a_box[0], b_box[0]), min(a_box[1], b_box[1])
    x0, x1 = max(a_box[2], b_box[2]), min(a_box[3], b_box[3])
    if y0 >= y1 or x0 >= x1:
        return 0.0
    inter = int(np.logical_and(a[y0:y1, x0:x1], b[y0:y1, x0:x1]).sum())
    return inter / max(a_area + b_area - inter, 1)


class MotsScorer:
    """Scores frame by frame, so a sequence needs no memory for its masks (1.3 MB each)."""

    def __init__(self):
        self.tp = self.fp = self.fn = self.ids = 0
        self.soft = 0.0
        self.last_match: dict[int, int] = {}

    def update(self, g: dict[int, np.ndarray], p: dict[int, np.ndarray],
               region: np.ndarray | None = None) -> None:
        """A match needs IoU > 0.5, so it is unique. Frames must arrive in order."""
        p_info = {pid: (_box(m), int(m.sum())) for pid, m in p.items()}
        matched = set()
        for gid, gmask in g.items():
            g_box, g_area = _box(gmask), int(gmask.sum())
            best = None
            for pid, pmask in p.items():
                iou = _iou(gmask, g_box, g_area, pmask, *p_info[pid])
                if iou > 0.5:
                    best = (pid, iou)
                    break
            if best is None:
                self.fn += 1
                continue
            pid, iou = best
            matched.add(pid)
            self.tp += 1
            self.soft += iou
            if gid in self.last_match and self.last_match[gid] != pid:
                self.ids += 1
            self.last_match[gid] = pid
        for pid, pmask in p.items():
            if pid in matched:
                continue
            if region is not None and np.logical_and(pmask, region).sum() > 0.5 * max(
                    p_info[pid][1], 1):
                continue
            self.fp += 1

    def result(self) -> dict:
        total = self.tp + self.fn
        return {
            "TP": self.tp, "FP": self.fp, "FN": self.fn, "IDS": self.ids, "GT": total,
            "sMOTSA": (self.soft - self.fp - self.ids) / total if total else 0.0,
            "MOTSA": (self.tp - self.fp - self.ids) / total if total else 0.0,
            "MOTSP": self.soft / self.tp if self.tp else 0.0,
        }


def evaluate(gt: dict[int, dict[int, np.ndarray]], pred: dict[int, dict[int, np.ndarray]],
             ignore: dict[int, np.ndarray] | None = None) -> dict:
    """gt and pred map frame -> {id: mask}."""
    scorer = MotsScorer()
    for frame in sorted(set(gt) | set(pred)):
        region = None if ignore is None else ignore.get(frame)
        scorer.update(gt.get(frame, {}), pred.get(frame, {}), region)
    return scorer.result()


def kitti_mots_lines(frame: int, objects: dict[int, np.ndarray], class_id: int = 1) -> list[str]:
    lines = []
    for track_id, mask in objects.items():
        encoded = rle.encode(mask)
        h, w = encoded["size"]
        text = rle.counts_to_string(encoded["counts"])
        lines.append(f"{frame} {class_id * 1000 + track_id} {class_id} {h} {w} {text}")
    return lines
