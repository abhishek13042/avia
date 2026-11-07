# SPEC-09 — Experiment and Reproducibility System

> Revised 2026-10-21 per audit — see `DECISION_LOG.md` (D-018).

## Purpose

Make training, evaluation, and comparison repeatable.

## Scope

Configurations, seeds, runs, checkpoints, artifacts, and environment fingerprints.

## Inputs

Code version, dataset manifest, split manifest, model configuration, and runtime metadata.

## Outputs

Experiment record, checkpoint, metrics, logs, and artifact paths.

## Functional requirements

- The same command must work locally and on Kaggle.
- Every run must record configuration and environment.
- Checkpoints must be resumable.
- Artifacts must be linked to a run ID.
- Every experiment declares a planned GPU-hour budget before it runs; actual GPU-hours are recorded (D-018).
- Checkpoint/resume must work across Kaggle sessions (session time limit).
- The current Kaggle weekly GPU quota and local GPU are recorded in T03. Local machine: no CUDA GPU, 7.6 GB RAM, so all training and GPU runs use Kaggle (D-020).
- Local environment: dedicated Python 3.11 virtual environment (system Python 3.14 is too new for CV frameworks); pinned dependency file shared with the Kaggle notebook.
- Every test-set evaluation is recorded in the registry with a running count (maximum 3, D-021).

## Technical design

Use configuration-driven commands and immutable run directories. MLflow/DVC-style tracking may be used after the basic contract is stable.

## Interfaces/contracts

`RunRecord` must include run ID, commit, dataset hash, split hash, seed, hardware, configuration, metrics, artifact paths, planned GPU-hours, and actual GPU-hours.

## Configuration

YAML/TOML configuration with no hidden defaults.

## Failure handling

Interrupted runs, missing checkpoints, incompatible artifacts, and unavailable dependencies must be explicit.

## Testing requirements

Fixture rerun, checkpoint resume (including resume in a new Kaggle session), configuration validation, and artifact completeness tests.

## Acceptance criteria

A documented run can be reproduced from its manifest and configuration, and checkpoint resume works.

## Evidence requirements

Run registry, environment fingerprint, command log, checkpoint inventory, and GPU-hour budget vs. actual table (see `PROJECT_TIMELINE.md`).

## Dependencies

SPEC-01 through SPEC-08.

## Non-goals

Uncontrolled manual experiments.
