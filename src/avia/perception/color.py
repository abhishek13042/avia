"""Untrained placeholder: red-blob detector so the system runs before the model exists.

Its output is never a result. Runs made with it are marked trained=False in the API and UI.
"""
import cv2
import numpy as np

from avia.types import Detection


class ColorBlobDetector:
    name = "placeholder-color-v0"
    trained = False

    def __init__(self, min_area: int = 40, max_area: int = 8000):
        self.min_area = min_area
        self.max_area = max_area

    def detect(self, image_bgr: np.ndarray) -> list[Detection]:
        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        low = cv2.inRange(hsv, (0, 90, 60), (12, 255, 255))
        high = cv2.inRange(hsv, (168, 90, 60), (180, 255, 255))
        mask = cv2.morphologyEx(low | high, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
        out = []
        for i in range(1, n):
            area = stats[i, cv2.CC_STAT_AREA]
            if self.min_area <= area <= self.max_area:
                box = stats[i, cv2.CC_STAT_WIDTH] * stats[i, cv2.CC_STAT_HEIGHT]
                out.append(Detection(labels == i, float(min(0.99, 0.4 + 0.6 * area / box))))
        return out
