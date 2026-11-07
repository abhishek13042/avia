# Model card

**Status: trained and test-scored on 2026-11-01.** Mask HOTA is pending.

| Field | Value |
|---|---|
| Architecture | Mask R-CNN, ResNet-50 FPN (torchvision), COCO-pretrained start |
| Task | Apple instance segmentation, tracked and counted in video |
| Training data | APPLE MOTS sequences 0–5 |
| Selection | Leave-one-sequence-out validation on 0–5 |
| Test data | Sequences 10–12, at most 3 evaluations |
| Checkpoint | `artifacts/t24/final/model.pt`, 3 epochs on sequences 0–5, chosen from mean fold F1 |
| Training hardware | Kaggle Tesla T4 |
| Validation scores | Six-fold LOSO, pooled: sMOTSA 42.3%, MOTSA 58.6%, MOTSP 79.5%. Slightly optimistic: each fold kept its best epoch on its held-out sequence |
| Test scores | Sequences 10–12, repo scorer: sMOTSA 43.0%, MOTSA 55.8%, MOTSP 81.2%, 402 ID switches. By sequence, sMOTSA 31.1%, 51.7%, 41.5%. Not yet checked with TrackEval |
| Speed | 1.8 FPS on a Tesla T4, detector plus tracker |

## Default detector

The app uses this checkpoint only when `DETECTOR_SPEC=maskrcnn:artifacts/t24/final/model.pt` is set. Without that setting it runs `placeholder-color-v0`, a colour rule that is not trained and is not evidence of accuracy. Every result from the colour rule is labelled as such. The two published examples were produced with the trained checkpoint on test sequences 10 and 11. They are for display and were not an evaluation.

## Intended use

Counting visible apples in short orchard row videos, for research and demonstration.

## Not intended for

Yield prediction, disease or stress diagnosis, or any decision that depends on an exact count. Apples hidden from the camera are not counted.

## Known limits

- Training data covers a small number of orchard sequences, so other varieties, lighting or camera setups may do worse.
- Apples are small in the frame, so small-object recall limits results.
- Events marked `ranked_only` are heuristics with no ground truth.
