# SPEC-07 — Events and Operational Anomaly Intelligence

> Revised 2026-10-21 per audit — see `DECISION_LOG.md` (D-008, D-019 m3).

## Purpose

Produce auditable operational alerts from temporal behavior.

## Scope

Track loss, reappearance, count instability, scene degradation, input failure, and normal-behavior deviation.

## Inputs

Temporal states, track features, and system health signals.

## Outputs

`EventRecord` objects, anomaly scores, and evidence references.

## Functional requirements

Events must contain type, event class, interval, confidence, source frames, model/config version, and evidence.

Every event type has exactly one class (D-008):

| Class | Meaning | Accuracy claim |
|---|---|---|
| `gt_derived` | Derived from GT IDs (track lost/reappeared, long GT gap) | Precision/recall/F1, onset error |
| `synthetic` | Injected perturbation (frame drop, freeze, blur, brightness, detector dropout) | Precision/recall/F1, PR-AUC |
| `ranked_only` | No ground truth (count instability, abnormal density) | None — reviewed examples only |

## Technical design

Rule-based event baseline plus normal-only embedding/statistical anomaly ranking.

## Interfaces/contracts

`EventRecord` contains `event_id`, `event_type`, `event_class`, `start_pts`, `end_pts`, `alert_pts`, `score`, `calibrated_probability` (nullable; set only where a calibration target exists), `evidence_uri`, and `model_version`.

## Configuration

Minimum duration, hysteresis, cooldown, threshold, alert budget, and calibration version.

## Failure handling

Duplicate alerts, uncertain state, missing frames, stale camera, and insufficient evidence.

## Testing requirements

Synthetic event injection, GT-derived event extraction, deduplication, threshold, and false-alert tests (false alerts per 1,000 frames).

## Acceptance criteria

Every alert is traceable to source frames, operational semantics are documented, and no agronomic diagnosis is implied.

## Evidence requirements

Alert timeline, false-alert examples, synthetic anomaly validation, and reviewed examples.

## Dependencies

SPEC-06. (System health signals come from the SPEC-02 ingestion layer; the SPEC-11 dependency was removed, D-019 m3.)

## Non-goals

Irrigation fault diagnosis, disease detection, or stress prediction.
