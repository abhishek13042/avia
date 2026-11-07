# SPEC-12 — Evidence and Final Audit

> Revised 2026-10-21 per audit — see `DECISION_LOG.md` (D-019 m7, m8, m9).

## Purpose

Confirm that the project is scientifically, technically, and communicatively defensible.

## Scope

Provenance, claims, metrics, code, artifacts, licensing, reproducibility, and final presentation.

## Inputs

All phase evidence, reports, artifacts, source records, and final outputs.

## Outputs

Final audit report, evidence index, release checklist, and claim matrix.

## Functional requirements

- Every major claim maps to evidence.
- Unsupported claims are removed.
- Licenses and citations are preserved.
- Final artifacts are traceable to configurations and runs.
- Robustness is described as cross-sequence / cross-platform robustness, not generalization (D-019 m9).
- The APPLE MOTS paper PDF is cited, not redistributed (Taverne terms, D-019 m7).

Third-party license table (filled in T02/T60, D-019 m8):

| Component | License | Use | Status |
|---|---|---|---|
| APPLE MOTS dataset | CC BY 4.0 | Data | Attribution required |
| APPLE MOTS paper (open copy) | Taverne | Citation only | Do not redistribute |
| WUR rt-obj-tracking | MIT | Reference code | To verify |
| Detectron2 / MMDetection | Apache-2.0 | Perception | To verify |
| ByteTrack / OC-SORT / BoT-SORT | MIT | Tracking | To verify |
| TrackEval | MIT | Evaluation | To verify |
| mots_tools | MIT | Evaluation | To verify |
| Ultralytics YOLO | AGPL-3.0 | Not used | Excluded |

## Technical design

Use a claim-to-evidence matrix with status `verified`, `measured`, `assumed`, or `unsupported`.

## Interfaces/contracts

Audit records contain claim, source, experiment, evidence path, reviewer, and status.

## Configuration

Required evidence list, metric thresholds, release policy, and final audit checklist.

## Failure handling

Missing evidence, inconsistent metrics, licensing ambiguity, unreproducible run, and unsupported statement.

## Testing requirements

Clean-environment reproduction, final API smoke test, final benchmark rerun, license-table check, and documentation-link check.

## Acceptance criteria

No unresolved critical audit item remains and the final project can be explained without overstating capabilities.

## Evidence requirements

Final report, demo, metrics, benchmark, error gallery, and reproduction instructions.

## Dependencies

All previous SPECs.

## Non-goals

Publishing claims beyond the dataset ground truth.
