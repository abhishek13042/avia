# SPEC-05 — Temporal Association and Tracking

> Revised 2026-10-21 per audit — see `DECISION_LOG.md` (D-007, D-019 m5, D-021).

## Purpose

Maintain persistent apple identities across frames.

## Scope

Detection-to-track association, motion, mask overlap, camera motion, and occlusion. Appearance ReID is an ablation only.

## Inputs

`PerceptionFrame`, `FramePacket`, and optional ground truth.

## Outputs

`TrackFrame` objects.

## Functional requirements

- Create, update, age, and terminate tracks.
- Preserve IDs.
- Expose association confidence.
- Record missed frames.

## Technical design

- Baseline: ByteTrack with masks attached.
- Main: OC-SORT or BoT-SORT without ReID, selected on validation (D-007).
- Mask-IoU gating where masks exist.
- Camera-motion compensation (wearable and UAV motion).
- Appearance ReID only as an ablation: apples are visually homogeneous, and the APPLE MOTS paper reports that learned appearance association underperformed box association.
- Primary failure mode to test: ID reuse between identical neighbouring apples.
- Accuracy levers (D-021), tuned by grid search on LOSO validation: two-stage low-score association, CMC (ECC or sparse optical flow), mask IoU after motion warp with strict gating, OC-SORT observation-centric re-update, conservative re-activation (`max_age`).
- Offline best-accuracy track only: tracklet interpolation/linking and detector-seeded video mask propagation (e.g. SAM 2, license to verify). Never mixed with online results.

## Interfaces/contracts

`TrackState` contains `track_id`, `class_id`, geometry, optional RLE `mask`, confidence, age, missed count, association score, and state (D-019 m5).

## Configuration

Association thresholds, maximum age, mask-IoU threshold, camera-motion-compensation method, appearance weight (ablation only, default 0), and detector interval.

## Failure handling

Frame gaps, detector outage, sudden camera motion, duplicate tracks, and ID collision.

## Testing requirements

Synthetic crossing, dropped-frame, occlusion, ID-reuse, ID-stability, and oracle-tracking tests.

## Acceptance criteria

Track IDs are unique within a stream, track state remains valid under expected gaps, and mask HOTA/IDF1 and sMOTSA/MOTSA/MOTSP/IDS are computed with a validated evaluator.

## Evidence requirements

Tracking videos, identity-switch examples, HOTA/IDF1 tables, and oracle ladder.

## Dependencies

SPEC-04.

## Non-goals

Cross-camera identity recognition.
