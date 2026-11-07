# Phase Execution System

This directory contains the executable project plan for Project 3.

All execution records, task results, tests, verification, evidence, and quality-gate decisions must be saved in Markdown files. Read [../DOCUMENTATION_PROCESS.md](../DOCUMENTATION_PROCESS.md) before starting work.

## Execution order

```text
PROJECT
↓
PHASE
↓
SPEC
↓
TASK
↓
IMPLEMENTATION
↓
TEST
↓
VERIFICATION
↓
EVIDENCE
↓
QUALITY GATE
```

## One-task rule

- Execute one task at a time.
- Do not start a dependent task before its dependency passes verification.
- Do not modify shared implementation files through parallel tasks.
- Parallel agents may be used for independent research, audits, reviews, and validation.
- The main agent integrates and verifies all parallel results.

## Task lifecycle

Each task must record:

1. Task objective.
2. Scope and non-goals.
3. Inputs and dependencies.
4. Implementation result.
5. Tests executed.
6. Verification result.
7. Evidence paths.
8. Quality-gate decision.
9. Follow-up task, if any.

## Phase order

1. [Phase 1 — Dataset, problem, and evaluation contract](phase-01-discovery-contract/PHASE.md)
2. [Phase 2 — Data engineering and perception foundation](phase-02-data-perception/PHASE.md)
3. [Phase 3 — Perception and temporal association](phase-03-perception-tracking/PHASE.md)
4. [Phase 4 — Temporal intelligence, API, dashboard, and runtime](phase-04-temporal-system/PHASE.md)
5. [Phase 5 — Scientific experiments, robustness, evidence, and final audit](phase-05-final-audit/PHASE.md)

## Execution order

See [../EXECUTION_ORDER.md](../EXECUTION_ORDER.md) for the complete T01–T62 order.

## Current status

- Phase 1: T01–T02 verified; T03 in progress; G0 approval pending (required before T04). Revised 2026-10-21 per `../DECISION_LOG.md`.
- Phase 2: Not started.
- Phase 3: Not started.
- Phase 4: Not started.
- Phase 5: Not started.
