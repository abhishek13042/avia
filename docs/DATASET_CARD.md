# Dataset card: APPLE MOTS

| Field | Value |
|---|---|
| Source | De Jong et al., 2022 |
| DOI | [10.5281/zenodo.5939726](https://doi.org/10.5281/zenodo.5939726) |
| Licence | CC BY 4.0 |
| File | `APPLE_MOTS.zip`, 5,661,248,829 bytes |
| MD5 | `1f9b8cd79f05469d656a01015889b55d` |
| Layout | `APPLE_MOTS/train/` (0–5) and `APPLE_MOTS/testing/` (6–8, 10–12), each with `images/` and `instances/` PNGs |
| Frames | 1,147 train and 526 unique test, all 1296 x 972 |
| Labels | uint16, 1000 + instance id, one class; no ignore value |

## How AVIA splits it

| Sequences | Use |
|---|---|
| 0–5 | Training and leave-one-sequence-out validation |
| 6–8 | Clean copies of 10–12; read only to locate ignore patches, never for training or tuning |
| 10–12 | Official test set, with translucent gray patches; at most 3 evaluations |

`src/avia/data/splits.py` enforces this. `scripts/evaluate.py` refuses test sequences during tuning.

## Audit results (T03, 2026-10-31)

- Sequences 10–12 are 6–8 with patches added: same frame names, identical labels, and identical pixels on frames without a patch.
- Ignore regions are not in the label PNGs. In the audited frames, patches cover 5–21% of sequence 10, 0–10% of 11 and 0–3.6% of 12. `overlay_mask` recovers them by comparing each frame with its clean copy (D-025).
- Sequence 10 has no image for frame 96, so that frame is skipped; its clean copy and label exist.
- Which camera platform recorded each sequence is still unknown.

## Attribution

Any public use must credit the dataset as above. The site footer does this.
