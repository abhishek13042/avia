"""Detector interface. This is the slot the trained model plugs into."""
import importlib
from typing import Protocol

import numpy as np

from avia.types import Detection


class Detector(Protocol):
    name: str
    trained: bool

    def detect(self, image_bgr: np.ndarray) -> list[Detection]: ...


def load_detector(spec: str) -> Detector:
    """Build a detector from a spec string.

    color                     untrained colour placeholder
    maskrcnn:/path/model.pt   checkpoint from kaggle/t24_baseline
    package.module:factory    any other model; factory() returns a Detector
    """
    if spec == "color":
        from avia.perception.color import ColorBlobDetector
        return ColorBlobDetector()
    if spec.startswith("maskrcnn:"):
        from avia.perception.maskrcnn import MaskRCNNDetector
        return MaskRCNNDetector(spec.split(":", 1)[1])
    module, _, factory = spec.partition(":")
    if not factory:
        raise ValueError(f"unknown detector spec: {spec}")
    return getattr(importlib.import_module(module), factory)()
