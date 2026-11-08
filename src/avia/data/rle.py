"""COCO run-length encoding without pycocotools (column-major counts)."""
import numpy as np


def encode(mask: np.ndarray) -> dict:
    h, w = mask.shape
    flat = mask.ravel(order="F").astype(np.uint8)
    if flat.size == 0:
        return {"size": [h, w], "counts": []}
    change = np.flatnonzero(flat[1:] != flat[:-1]) + 1
    runs = np.diff(np.concatenate(([0], change, [flat.size]))).tolist()
    return {"size": [h, w], "counts": ([0] + runs) if flat[0] else runs}


def decode(rle: dict) -> np.ndarray:
    h, w = rle["size"]
    values = np.arange(len(rle["counts"])) % 2 == 1
    return np.repeat(values, rle["counts"]).reshape((h, w), order="F")


def counts_to_string(counts: list[int]) -> str:
    """Compressed form used by KITTI MOTS txt files (pycocotools rleToString)."""
    out = []
    for i, value in enumerate(counts):
        x = value - counts[i - 2] if i > 2 else value
        more = True
        while more:
            c = x & 0x1F
            x >>= 5
            more = not (x == -1 if c & 0x10 else x == 0)
            out.append(chr((c | 0x20 if more else c) + 48))
    return "".join(out)


def string_to_counts(s: str) -> list[int]:
    counts: list[int] = []
    p = 0
    while p < len(s):
        x, k, more = 0, 0, True
        while more:
            c = ord(s[p]) - 48
            x |= (c & 0x1F) << (5 * k)
            more = bool(c & 0x20)
            p += 1
            k += 1
            if not more and c & 0x10:
                x |= -1 << (5 * k)
        if len(counts) > 2:
            x += counts[-2]
        counts.append(x)
    return counts
