# Phase 3 — Perception and Temporal Association

## Objective

Build and evaluate the visual perception and persistent tracking layers.

## Components

- Mask R-CNN R50-FPN baseline (optional YOLOX-S box-only).
- Main perception model selected on validation from Mask R-CNN high-res/tiled, RTMDet-Ins, and Mask2Former.
- ByteTrack baseline.
- OC-SORT / BoT-SORT main association without ReID (ReID as ablation only).
- Mask-IoU association.
- Camera-motion compensation.
- Track state store.
- MOTS evaluation: mask HOTA (primary) and paper-comparable sMOTSA/MOTSA/MOTSP/IDS, with a validated evaluator.

## Deliverables

- Baseline checkpoint.
- Main checkpoint.
- Prediction files.
- Tracking visualizations.
- Detection metrics.
- Tracking metrics.
- Oracle-ladder analysis.
- Failure-case gallery.

## Dependencies

Phase 2 quality gate.

## Parallelizable work

After contracts are frozen:

- Tracker implementation audit.
- Metric implementation audit.
- Prediction-visualization audit.

Training and shared implementation remain controlled by the main workflow.

## Sequential work

1. Perception smoke test.
2. Kaggle baseline training.
3. Baseline evaluation.
4. Main model smoke test.
5. Kaggle main training.
6. Tracker integration.
7. Tracking evaluation.
8. Error analysis.
9. Pass the phase gate.

## Quality gate (G3, T35)

Perception outputs must be geometrically correct, tracking IDs must be valid, the evaluator must be validated (GT-as-prediction scores perfectly), HOTA/IDF1/sMOTSA must be compared with the published baseline (PointTrack 38.7 sMOTSA), and detector versus association errors must be separated.

## Specs

- [SPEC-04 — Visual perception](../phase-02-data-perception/specs/SPEC-04-perception.md)
- [SPEC-05 — Temporal association and tracking](specs/SPEC-05-tracking.md)
- [SPEC-08 — Evaluation and error analysis](../phase-01-discovery-contract/specs/SPEC-08-evaluation.md)

## Tasks

See [TASKS.md](TASKS.md).
