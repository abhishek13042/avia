"""Runs the Kaggle training script and evaluate.py on a tiny synthetic dataset (CPU, slow-ish)."""
import json
import os
import subprocess
import sys

import cv2
import numpy as np
import pytest
from PIL import Image

pytest.importorskip("torchvision")
ROOT = os.path.join(os.path.dirname(__file__), "..")


def make_dataset(base):
    rng = np.random.default_rng(0)
    for sequence in (0, 1, 2, 3, 4, 5):
        images = base / "images" / f"{sequence:04d}"
        labels = base / "instances" / f"{sequence:04d}"
        images.mkdir(parents=True)
        labels.mkdir(parents=True)
        for frame in range(3):
            image = rng.integers(0, 80, (120, 160, 3), dtype=np.uint8)
            ids = np.zeros((120, 160), dtype=np.uint16)
            for k in range(3):
                centre = (40 + 40 * k + frame, 60)
                cv2.circle(image, centre, 12, (220, 30, 30), -1)
                cv2.circle(ids, centre, 12, 1001 + k, -1)
            Image.fromarray(image).save(images / f"{frame:06d}.png")
            Image.fromarray(ids).save(labels / f"{frame:06d}.png")


def test_training_checkpoint_loads_into_the_app_and_evaluates(tmp_path):
    data, out = tmp_path / "input", tmp_path / "out"
    make_dataset(data)
    env = {**os.environ, "AVIA_INPUT": str(data), "AVIA_OUT": str(out),
           "AVIA_TMP": str(tmp_path / "tmp"), "AVIA_FOLD": "5", "AVIA_EPOCHS": "1",
           "AVIA_BATCH": "2", "AVIA_SIZE": "160", "AVIA_MAX_SIZE": "200",
           "AVIA_PRETRAINED": "0"}
    script = os.path.join(ROOT, "kaggle", "t24_baseline", "train_maskrcnn.py")
    subprocess.run([sys.executable, script], env=env, check=True, timeout=500)
    metrics = json.loads((out / "metrics.json").read_text())
    assert metrics["finished"] is True and metrics["fold"] == 5
    assert (out / "last.pt").exists() and (out / "model.pt").exists()

    from avia.perception.base import load_detector

    detector = load_detector(f"maskrcnn:{out / 'model.pt'}")
    assert detector.trained and detector.name == "maskrcnn-r50-fpn-fold5"
    image = np.zeros((120, 160, 3), np.uint8)
    assert isinstance(detector.detect(image), list)

    # Resuming from the finished run must not train again.
    second = subprocess.run([sys.executable, script], env=env, check=True, timeout=200,
                            capture_output=True, text=True)
    assert "resumed from" in second.stdout

    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "evaluate.py"), "--data", str(data),
         "--detector", f"maskrcnn:{out / 'model.pt'}", "--sequences", "5",
         "--out", str(tmp_path / "eval")], capture_output=True, check=False, text=True, timeout=200, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "eval" / "maskrcnn-r50-fpn-fold5" / "0005.txt").exists()


def test_trackeval_ground_truth_files(tmp_path):
    make_dataset(tmp_path / "input")
    out = tmp_path / "te"
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "run_trackeval.py"), "--data",
                    str(tmp_path / "input"), "--sequences", "5", "--out", str(out),
                    "--prepare-only"], check=True)
    lines = (out / "gt" / "label_02" / "0005.txt").read_text().splitlines()
    assert len(lines) == 9 and lines[0].split()[:3] == ["0", "1001", "1"]
    assert (out / "gt" / "evaluate_mots.seqmap.val").read_text().strip() == "0005 empty 000000 000002"


def test_evaluate_refuses_test_sequences_for_tuning(tmp_path):
    make_dataset(tmp_path)
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "evaluate.py"), "--data", str(tmp_path),
         "--detector", "color", "--sequences", "11"], capture_output=True, check=False, text=True, cwd=tmp_path)
    assert result.returncode != 0 and "cannot be used" in result.stderr
