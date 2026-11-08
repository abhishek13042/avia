"""Reader for the KITTI MOTS PNG layout used by APPLE MOTS.

Ids are class * 1000 + instance, as in KITTI MOTS (confirmed by T03). The value 10000 never
appears in APPLE MOTS: its ignore regions are patches on the test images, see `overlay_mask`.
"""
import os
from dataclasses import dataclass

import numpy as np
from PIL import Image

IGNORE_ID = 10000
CLEAN_COPY_OF = {10: 6, 11: 7, 12: 8}


@dataclass(frozen=True)
class Frame:
    sequence: int
    index: int
    image_path: str
    instance_path: str | None


def _pairs(base: str) -> list[str]:
    """Every folder holding images/ + instances/; APPLE MOTS has train/ and testing/."""
    pairs = []
    for root, dirs, _ in os.walk(base):
        if "images" in dirs and "instances" in dirs:
            pairs.append(root)
            dirs.clear()
    return sorted(pairs)


def find_root(base: str) -> str:
    pairs = _pairs(base)
    if not pairs:
        raise FileNotFoundError(f"no images/ + instances/ pair under {base}")
    return pairs[0] if len(pairs) == 1 else base


def list_sequences(root: str) -> list[int]:
    return sorted(int(n) for pair in _pairs(root)
                  for n in os.listdir(os.path.join(pair, "images")) if n.isdigit())


def _sequence_dir(root: str, kind: str, sequence: int) -> str:
    for pair in _pairs(root):
        for name in os.listdir(os.path.join(pair, kind)):
            if name.isdigit() and int(name) == sequence:
                return os.path.join(pair, kind, name)
    raise FileNotFoundError(f"sequence {sequence} missing from {kind}/")


def list_frames(root: str, sequence: int) -> list[Frame]:
    image_dir = _sequence_dir(root, "images", sequence)
    instance_dir = _sequence_dir(root, "instances", sequence)
    frames = []
    for name in sorted(os.listdir(image_dir)):
        stem, _ = os.path.splitext(name)
        instance = os.path.join(instance_dir, stem + ".png")
        frames.append(Frame(sequence, int(stem), os.path.join(image_dir, name),
                            instance if os.path.exists(instance) else None))
    return frames


def split_instances(ids: np.ndarray) -> tuple[dict[int, np.ndarray], np.ndarray]:
    """Return ({instance_id: mask}, ignore_mask) from an instance PNG array."""
    masks = {int(v): ids == v for v in np.unique(ids) if v != 0 and v != IGNORE_ID}
    return masks, ids == IGNORE_ID


def load_instances(path: str) -> tuple[dict[int, np.ndarray], np.ndarray]:
    return split_instances(np.array(Image.open(path)))


def overlay_mask(root: str, sequence: int, index: int) -> np.ndarray | None:
    """Ignore patches on a test frame, found by diffing it with its clean copy (T03, D-025).

    Sequences 6-8 are 10-12 without the patches, and pixels outside a patch match exactly.
    They are read here only to locate the patches, never to tune anything.
    """
    import cv2

    clean_sequence = CLEAN_COPY_OF.get(sequence)
    if clean_sequence is None:
        return None
    try:
        clean = _sequence_dir(root, "images", clean_sequence)
        overlaid = _sequence_dir(root, "images", sequence)
    except FileNotFoundError:
        return None
    paths = [os.path.join(d, f"{index:06d}.png") for d in (clean, overlaid)]
    if not all(os.path.exists(p) for p in paths):
        return None
    a, b = (np.asarray(Image.open(p).convert("RGB"), dtype=np.int16) for p in paths)
    changed = (np.abs(a - b).max(axis=2) > 8).astype(np.uint8)
    changed = cv2.morphologyEx(changed, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return cv2.morphologyEx(changed, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)).astype(bool)
