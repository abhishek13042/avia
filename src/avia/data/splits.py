"""Split policy (D-001): tune with LOSO over 0-5, test only on 10-12, never tune on 6-8."""
import json
import os
import time

TRAIN = (0, 1, 2, 3, 4, 5)
DUPLICATES_OF_TEST = (6, 7, 8)
TEST = (10, 11, 12)
MAX_TEST_EVALUATIONS = 3  # D-021


def loso_folds() -> list[dict]:
    return [{"fold": s, "train": [t for t in TRAIN if t != s], "val": [s]} for s in TRAIN]


def assert_tuning_safe(sequences) -> None:
    bad = sorted(set(sequences) - set(TRAIN))
    if bad:
        raise ValueError(f"sequences {bad} cannot be used for training or tuning")


def record_test_evaluation(log_path: str, note: str) -> int:
    """Log a test-set evaluation; refuses to go past the budget."""
    entries = []
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            entries = json.load(f)
    if len(entries) >= MAX_TEST_EVALUATIONS:
        raise RuntimeError(f"test budget of {MAX_TEST_EVALUATIONS} evaluations is used up")
    entries.append({"time": time.strftime("%Y-%m-%d %H:%M:%S"), "note": note})
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=1)
    return len(entries)
