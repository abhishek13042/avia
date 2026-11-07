# Phase 2 — Data Engineering and Perception Foundation

## Objective

Create a verified data path from AppleMOTS to model-ready samples without serious local CPU training.

## Components

- Dataset manifest.
- Frame adapter.
- MOTS annotation adapter.
- Derived bounding boxes.
- Ignore-region handling (encoding verified in T03/T13).
- Duplicate-group hash check (6↔10, 7↔11, 8↔12).
- Synthetic timestamps (`pts_source = synthetic`).
- Visualization.
- Golden fixture.
- Model input/output contracts.
- Local smoke-test path.

## Deliverables

- Immutable dataset manifest.
- Validated frame index.
- Validated annotation index.
- Visualization report.
- Golden fixture.
- Perception contract.
- Tiny forward-pass report.

## Dependencies

Phase 1 quality gate.

## Parallelizable work

- Independent manifest audit.
- Independent annotation visualization audit.
- Model-interface review.

## Sequential work

1. Build manifest.
2. Validate annotations.
3. Build frame adapter.
4. Produce visual evidence.
5. Run local smoke checks.
6. Pass the data-quality gate.

## Quality gate (G2, T21)

Images, masks, IDs, ignore regions, duplicate groups, and model inputs must be verified before training.

## Specs

- [SPEC-02 — Media ingestion and temporal replay](specs/SPEC-02-media-ingestion.md)
- [SPEC-03 — Annotation and ground truth adapter](specs/SPEC-03-annotations.md)
- [SPEC-04 — Visual perception contract](specs/SPEC-04-perception.md)

## Tasks

See [TASKS.md](TASKS.md).
