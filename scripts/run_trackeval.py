"""Mask HOTA with TrackEval, from the KITTI MOTS txt files written by evaluate.py.

python scripts/run_trackeval.py --data data/APPLE_MOTS --pred artifacts/eval/<model> \
    --sequences 10 11 12 --summary artifacts/benchmarks.json

Ground truth is written from the instance PNGs first. Apples use class 1, which TrackEval calls
"car"; the class name has no effect on the score. --prepare-only stops before TrackEval, which
needs installing separately (see docs/KAGGLE_RUNBOOK.md).
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from avia.data import kitti_mots, rle
from avia.evaluation.mots import kitti_mots_lines


def write_ground_truth(root: str, sequences: list[int], out: str) -> None:
    os.makedirs(os.path.join(out, "label_02"), exist_ok=True)
    seqmap = []
    for sequence in sequences:
        frames = kitti_mots.list_frames(root, sequence)
        lines = []
        for frame in frames:
            if frame.instance_path is None:
                continue
            masks, ignore = kitti_mots.load_instances(frame.instance_path)
            overlay = kitti_mots.overlay_mask(root, sequence, frame.index)
            ignore = ignore if overlay is None else ignore | overlay
            lines += kitti_mots_lines(frame.index, {k % 1000: m for k, m in masks.items()})
            if np.any(ignore):
                encoded = rle.encode(ignore)
                h, w = encoded["size"]
                lines.append(f"{frame.index} {kitti_mots.IGNORE_ID} 10 {h} {w} "
                             f"{rle.counts_to_string(encoded['counts'])}")
        with open(os.path.join(out, "label_02", f"{sequence:04d}.txt"), "w") as f:
            f.write("\n".join(lines) + "\n")
        seqmap.append(f"{sequence:04d} empty 000000 {frames[-1].index:06d}")
    with open(os.path.join(out, "evaluate_mots.seqmap.val"), "w") as f:
        f.write("\n".join(seqmap) + "\n")


def run_trackeval(gt: str, pred_dir: str, sequences: list[int], out: str) -> float:
    import trackeval

    name = os.path.basename(os.path.normpath(pred_dir))
    tracker_data = os.path.join(out, "trackers", name, "data")
    os.makedirs(tracker_data, exist_ok=True)
    for sequence in sequences:
        shutil.copy(os.path.join(pred_dir, f"{sequence:04d}.txt"), tracker_data)

    dataset = trackeval.datasets.KittiMOTS({
        **trackeval.datasets.KittiMOTS.get_default_dataset_config(),
        "GT_FOLDER": gt, "TRACKERS_FOLDER": os.path.join(out, "trackers"), "SEQMAP_FOLDER": gt,
        "OUTPUT_FOLDER": out, "TRACKERS_TO_EVAL": [name], "CLASSES_TO_EVAL": ["car"],
        "SPLIT_TO_EVAL": "val", "PRINT_CONFIG": False})
    evaluator = trackeval.Evaluator({**trackeval.Evaluator.get_default_eval_config(),
                                     "USE_PARALLEL": False, "PRINT_CONFIG": False})
    results, _ = evaluator.evaluate([dataset], [trackeval.metrics.HOTA({"PRINT_CONFIG": False})])
    combined = results["KittiMOTS"][name]["COMBINED_SEQ"]["car"]["HOTA"]["HOTA"]
    return float(np.mean(combined))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--pred")
    parser.add_argument("--sequences", type=int, nargs="+", required=True)
    parser.add_argument("--out", default="artifacts/trackeval")
    parser.add_argument("--summary", help="JSON file from evaluate.py to fill in HOTA")
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()

    gt = os.path.join(args.out, "gt")
    write_ground_truth(kitti_mots.find_root(args.data), args.sequences, gt)
    if args.prepare_only:
        return
    if not args.pred:
        parser.error("--pred is required unless --prepare-only is set")
    hota = run_trackeval(gt, args.pred, args.sequences, args.out)
    print(f"mask HOTA {hota:.4f}")
    if args.summary:
        with open(args.summary, encoding="utf-8") as f:
            summary = json.load(f)
        summary["HOTA"] = hota
        with open(args.summary, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=1)


if __name__ == "__main__":
    main()
