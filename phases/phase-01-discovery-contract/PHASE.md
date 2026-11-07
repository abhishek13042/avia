# Phase 1 — Dataset, Problem, and Evaluation Contract

## Objective

Freeze the scientific problem, primary dataset, label semantics, leakage-safe split policy, metrics, and claim boundaries before implementation.

## Components

- Dataset provenance.
- License and citation record.
- Problem definition.
- Label ontology.
- Derived-label policy.
- Split manifest policy (duplicate-group aware: {6, 10}, {7, 11}, {8, 12}; validation from 0–5).
- Evaluation protocol.
- Claim boundary.

## Deliverables

- Dataset card.
- Problem statement.
- Label dictionary.
- Split policy.
- Evaluation protocol.
- Claim matrix.
- Evidence checklist.

## Dependencies

None. This phase is the entry gate for implementation.

## Parallelizable work

- Independent source verification.
- License/access verification.
- Split leakage audit.
- Metric and paper review.

## Sequential work

1. Integrate research.
2. Freeze the problem.
3. Freeze the label ontology.
4. Freeze metrics.
5. Obtain project approval.

## Quality gate (G1, T09)

Pass only when every claim has defensible ground truth, no split leakage is possible (including duplicate groups), a validation strategy from sequences 0–5 is frozen, and unsupported irrigation/physiology claims are removed. See `../../DECISION_LOG.md`.

## Specs

- [SPEC-01 — Dataset provenance and split contract](specs/SPEC-01-dataset-provenance.md)
- [SPEC-08 — Evaluation and error-analysis contract](specs/SPEC-08-evaluation.md)
- [SPEC-09 — Experiment and reproducibility contract](specs/SPEC-09-reproducibility.md)

## Tasks

See [TASKS.md](TASKS.md). Execute only one task at a time.
