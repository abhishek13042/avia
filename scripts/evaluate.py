"""Run a model and the tracker over APPLE MOTS sequences and write the benchmark files.

Validation (sequences 0-5):  python scripts/evaluate.py --data D --detector SPEC --sequences 0 1
Final test (10-12, budget 3): python scripts/evaluate.py --data D --detector SPEC --test --note WHY

Writes KITTI MOTS txt files for TrackEval (mask HOTA) and, for --test, artifacts/benchmarks.json,
which the benchmark page reads. Numbers on that page only ever come from this script.
"""
import argparse
import json
import os
import platform
import sys
import time

import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from avia.data import kitti_mots, splits
from avia.evaluation.mots import MotsScorer, kitti_mots_lines
from avia.perception.base import load_detector
from avia.tracking.tracker import MaskTracker


def run_sequence(root, sequence, detector, out_dir):
    tracker = MaskTracker()
    scorer, lines = MotsScorer(), []
    frames = kitti_mots.list_frames(root, sequence)
    elapsed = 0.0
    for frame in frames:
        image = cv2.imread(frame.image_path)
        started = time.perf_counter()
        objects = tracker.update(image, detector.detect(image))
        elapsed += time.perf_counter() - started
        pred = {o.track_id: o.mask for o in objects}
        lines += kitti_mots_lines(frame.index, pred)
        gt, ignore = {}, None
        if frame.instance_path:
            gt, ignore_mask = kitti_mots.load_instances(frame.instance_path)
            overlay = kitti_mots.overlay_mask(root, sequence, frame.index)
            ignore = ignore_mask if overlay is None else ignore_mask | overlay
        scorer.update(gt, pred, ignore)
    with open(os.path.join(out_dir, f"{sequence:04d}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    metrics = scorer.result()
    metrics["frames"] = len(frames)
    metrics["seconds"] = round(elapsed, 2)
    return metrics


def combine(per_sequence: dict) -> dict:
    """Pool the counts; sMOTSA is rebuilt from MOTSP so the mean is weighted by GT."""
    total = {k: sum(m[k] for m in per_sequence.values()) for k in ("TP", "FP", "FN", "IDS", "GT")}
    soft = sum(m["MOTSP"] * m["TP"] for m in per_sequence.values())
    gt = max(total["GT"], 1)
    frames = sum(m["frames"] for m in per_sequence.values())
    seconds = sum(m["seconds"] for m in per_sequence.values())
    return {**total, "sMOTSA": (soft - total["FP"] - total["IDS"]) / gt,
            "MOTSA": (total["TP"] - total["FP"] - total["IDS"]) / gt,
            "MOTSP": soft / max(total["TP"], 1), "fps": frames / max(seconds, 1e-9)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--detector", required=True)
    parser.add_argument("--sequences", type=int, nargs="*")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--note", default="")
    parser.add_argument("--out", default="artifacts/eval")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    if args.test:
        if not args.note:
            parser.error("--test needs --note saying why this evaluation is being spent")
        used = splits.record_test_evaluation(os.path.join("artifacts", "test_log.json"), args.note)
        print(f"test evaluation {used} of {splits.MAX_TEST_EVALUATIONS}")
        sequences = list(splits.TEST)
    else:
        sequences = args.sequences or list(splits.TRAIN)
        splits.assert_tuning_safe(sequences)

    root = kitti_mots.find_root(args.data)
    detector = load_detector(args.detector)
    txt_dir = os.path.join(args.out, detector.name)
    os.makedirs(txt_dir, exist_ok=True)
    per_sequence = {str(s): run_sequence(root, s, detector, txt_dir) for s in sequences}
    summary = {
        "status": "measured", "split": "test" if args.test else "validation",
        "model": detector.name, "trained_model": detector.trained,
        "date": time.strftime("%Y-%m-%d"), "note": args.note,
        "hardware": _hardware(), "overall": combine(per_sequence), "sequences": per_sequence,
        "kitti_mots_txt": txt_dir, "HOTA": None,
    }
    print(json.dumps(summary["overall"], indent=1))
    with open(os.path.join(args.out, f"{detector.name}_{summary['split']}.json"), "w",
              encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    if args.test:
        with open(os.path.join("artifacts", "benchmarks.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=1)


def _hardware() -> str:
    try:
        import torch
        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
    except ImportError:
        pass
    return platform.processor() or "cpu"


if __name__ == "__main__":
    main()
