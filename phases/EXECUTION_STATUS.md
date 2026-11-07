# Project 3 Execution Status

## Current active task

- Task: T03 — Record verified facts, assumptions, and unknowns.
- Phase: Phase 1 — Dataset, problem, and evaluation contract.
- Status: T01 and T02 verified; T03 data checks done on 2026-10-31; U3 and the Kaggle quota part of U6 stay open and do not block training.

## Application status (2026-10-31, D-024, D-025)

- Built ahead of the task order at the user's request: pipeline, Kaggle training script, evaluation, API, worker, database, web app, Docker files, CI, documentation.
- Verified: test suite, web build, and upload to results in a browser, all with the placeholder model on SQLite and local disk. Data audit on the full dataset (T03).
- Not verified: Docker, Postgres, S3, CI, and the TrackEval run.
- 2026-11-01: six folds and the final model trained; test evaluation 1 of 3 spent. Results in `../artifacts/benchmarks.json`.
- Next: TrackEval (needs the user's approval), then real demo frames.

## Rule

Only one task may be marked `In Progress` at a time.

## Status values

- `Pending`
- `In Progress`
- `Blocked`
- `Verified`
- `Failed`
- `Deferred`

## Gate status

| Gate | Description | Task | Status |
|---|---|---|---|
| G0 | Discovery approval | Before T04 | Go-ahead given 2026-10-29 (D-022) |
| G1 | Project contract | T09 | Not started |
| G2 | Data quality | T21 | Not started |
| G3 | Perception/tracking correctness | T35 | Not started |
| G4 | Temporal correctness | After T44 | Not started |
| G5 | Runtime qualification | T50 | Not started |
| G6 | Scientific quality | After T57 | Not started |
| G7 | Final audit | T62 | Not started |

Gate scheme unified on 2026-10-21 (`../DECISION_LOG.md` D-016).

## Process deviation

T01 and T02 were executed and verified before G0 approval was recorded (D-017). They are research-only tasks with no implementation. G0 must be approved before T04.

## Task execution record

When a task starts, create a Markdown record using `TASK_EXECUTION_TEMPLATE.md` under the current phase `tasks/` directory and update this file before moving to another task.

Required task record format:

```text
TASK-<id>-<name>.md
```

Required contents:

- objective;
- scope and non-goals;
- dependencies;
- implementation result;
- tests;
- verification;
- evidence paths;
- quality-gate decision;
- follow-up or approval to continue.
