# SPEC-06 — Temporal Features and State Reasoning

> Revised 2026-10-21 per audit — see `DECISION_LOG.md` (D-009, D-010).

## Purpose

Convert tracks into temporally meaningful signals.

## Scope

Track histories, count series, persistence, visibility, occlusion, and causal temporal models.

## Inputs

`TrackFrame`, timestamps, and ground-truth tracks where available.

## Outputs

Track features, count series, and temporal states.

## Functional requirements

- Maintain bounded history.
- Calculate derivatives.
- Support causal inference.
- Expose uncertainty and missing data.

## Technical design

- Baseline (primary): deterministic smoothing and state machine.
- Optional: causal GRU over track features, only for GT-derived targets (track continuation, GT ID gaps). Kill criterion: keep only if it improves the target metric by ≥2 points absolute under LOSO validation; otherwise report it as a negative result (D-009).
- Timestamps are synthesized (`pts_source = synthetic`, D-010).

## Interfaces/contracts

`TemporalState` contains `track_id`, timestamp, state, feature vector, confidence, and history length.

## Configuration

Window length, smoothing, minimum persistence, missing-frame tolerance, and causal mode.

## Failure handling

Insufficient history, irregular timestamps, missing tracks, and stale state.

## Testing requirements

Frame-order, synthetic-trajectory, shuffled-frame, and causal look-ahead tests.

## Acceptance criteria

Features are timestamp-aligned, state transitions are reproducible, and future frames cannot influence online output.

## Evidence requirements

Track plots, count curves, state transitions, and a temporal-model report including the kill-criterion decision.

## Dependencies

SPEC-05.

## Non-goals

Claiming biological growth or physiological stress.
