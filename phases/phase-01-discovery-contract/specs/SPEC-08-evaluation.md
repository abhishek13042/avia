# SPEC-08 — Evaluation and Error Analysis

> Revised 2026-10-21 per audit — see `DECISION_LOG.md` (D-003, D-004, D-008, D-012, D-013, D-019 m2).

## Purpose

Produce scientifically valid metrics and failure explanations.

## Scope

Detection, segmentation, tracking, counting, temporal, anomaly, calibration, cross-sequence/cross-platform robustness, and systems metrics.

Phase split (D-019 m2): metric definitions are frozen in Phase 1 (T07); the evaluation implementation is built in Phase 3 and later and depends on SPEC-01–07.

## Inputs

Ground truth, predictions, tracks, events, and runtime logs.

## Outputs

Metric tables, plots, confidence intervals, and an error taxonomy.

## Functional requirements

- Use locked, duplicate-group-aware splits; test only on 10–12.
- Report per-sequence and per-platform tables plus pooled results.
- Report per-condition slices, including inside vs. outside ignore regions.
- Preserve raw counts.
- Separate detector and tracker errors.
- Record metric configuration and sample counts.

## Technical design

- Detection/segmentation: COCO-style box and mask AP, small-object recall (below 32 px).
- Tracking primary: mask-based HOTA (DetA, AssA, LocA) via TrackEval, plus IDF1.
- Tracking paper-comparable: KITTI MOTS sMOTSA, MOTSA, MOTSP, IDS on sequences 10–12 with ignore regions (D-004). Reference: PointTrack 38.7 / 52.9 / 80.0, TrackR-CNN 35.7 / 47.8 / 80.4 (D-003).
- Secondary: fragmentation, track survival.
- Counting: per-frame visible-count MAE/RMSE; per-sequence unique-count absolute and relative error (D-012).
- Events: precision/recall/F1, temporal IoU, onset error, false alerts per 1,000 frames — only for `gt_derived` and `synthetic` events (D-008).
- Calibration: detector-confidence reliability, ECE, Brier, NLL.

Test-set protection (D-021): all tuning on LOSO validation; the test set (10–12) is evaluated only for locked configurations, at most 3 times in total, each logged. Online and offline results are reported in separate tables.

Statistics (D-013): at least 3 seeds per main comparison (mean ± std); optional block bootstrap over contiguous 30-frame windows with the autocorrelation caveat; never bootstrap over sequences (n = 3). The DJI Matrice test sequence is an unseen-platform slice (n = 1, descriptive only).

## Interfaces/contracts

Every metric result must include metric name, value, split, slice, sample count, seed, and configuration hash.

## Configuration

IoU thresholds, temporal-IoU thresholds, ignore-region handling, bootstrap unit (30-frame block), confidence intervals, seeds, and primary metric (mask HOTA).

## Failure handling

Missing predictions, metric mismatches, empty classes, invalid IDs, and split contamination fail evaluation.

## Testing requirements

GT-as-prediction must score perfectly (HOTA = 1, sMOTSA = 1), hand-computed toy cases, comparison with official mots_tools/TrackEval, ignore-region exclusion tests, empty-input tests, and regression tests.

## Acceptance criteria

Metrics agree with reference implementations within tolerance and every reported result is traceable to predictions.

## Evidence requirements

Final metric tables, plots, raw counts, error gallery, and bootstrap report.

## Dependencies

Definitions: SPEC-01 only. Implementation: SPEC-01 through SPEC-07.

## Non-goals

Hiding poor performance behind a single aggregate score.
