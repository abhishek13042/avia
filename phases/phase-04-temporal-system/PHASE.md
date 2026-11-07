# Phase 4 — Temporal Intelligence, API, Dashboard, and Runtime

## Objective

Convert tracks into temporal analytics, operational anomaly signals, and a measured inference service.

## Components

- Track feature extraction.
- Causal temporal buffers.
- Count analytics.
- Temporal state machine.
- Optional causal GRU (kill criterion: ≥2 points absolute on LOSO, GT-derived targets only).
- Operational anomaly scoring with event classes `gt_derived`, `synthetic`, `ranked_only`.
- Evidence selection.
- API.
- Dashboard.
- Runtime benchmark.
- Health telemetry.

## Deliverables

- Track feature schema.
- Event schema.
- Anomaly schema.
- API contract.
- Dashboard views.
- Replay runner.
- Runtime benchmark.
- Latency, throughput, memory, and dropped-frame report.

## Dependencies

Phase 3 quality gate.

## Parallelizable work

- API contract review.
- Dashboard usability review.
- Runtime measurement review.
- Independent error-analysis audit.

## Sequential work

1. Track feature pipeline.
2. Count and persistence analytics.
3. Rule-based temporal baseline.
4. Optional causal GRU.
5. Operational anomaly layer.
6. API.
7. Dashboard.
8. End-to-end replay.
9. Runtime benchmark.
10. Pass the real-time or measured-offline gate.

## Quality gates

- G4 (after T44): causal behavior must contain no look-ahead; event schemas and classes are frozen.
- G5 (T50): real-time status is determined only from measured performance — ≥25 FPS sustained end-to-end at 1296 × 972 on a named GPU, otherwise "measured offline".

## Specs

- [SPEC-06 — Temporal features and state reasoning](specs/SPEC-06-temporal.md)
- [SPEC-07 — Events and operational anomaly intelligence](specs/SPEC-07-events-anomalies.md)
- [SPEC-10 — API and dashboard](specs/SPEC-10-api-dashboard.md)
- [SPEC-11 — Deployment and runtime benchmarking](specs/SPEC-11-runtime.md)

## Tasks

See [TASKS.md](TASKS.md).
