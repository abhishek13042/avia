# Phase 5 — Scientific Experiments, Evidence, and Final Audit

## Objective

Establish scientific usefulness, reproducibility, cross-sequence/cross-platform robustness, and interview defensibility.

## Components

- Controlled comparisons.
- Ablations.
- Calibration.
- Error analysis.
- Cross-sequence / cross-platform robustness analysis.
- Compute analysis.
- Reproducibility audit.
- Evidence package.
- Final claim audit.

## Deliverables

- Experiment registry.
- Final metrics table.
- Ablation table.
- Robustness report (per sequence, per platform; DJI Matrice as unseen-platform slice, n = 1).
- Calibration report.
- Error taxonomy.
- Accuracy–latency analysis.
- Reproduction report.
- Final technical report.
- Final demo.

## Dependencies

Phases 1–4.

## Parallelizable work

- Independent metric audit.
- Independent reproducibility audit.
- Documentation audit.
- API/deployment audit.
- Claim-overreach audit.

## Sequential work

1. Lock experiment matrix.
2. Run Kaggle experiments.
3. Run ablations.
4. Run robustness tests.
5. Run calibration.
6. Complete error analysis.
7. Complete runtime analysis.
8. Assemble evidence.
9. Perform final audit.
10. Pass final quality gate.

## Quality gates

- G6 (after T57): baselines, main comparison (≥3 seeds), ablations, error analysis, robustness, calibration, and compute analysis are complete.
- G7 (T62): results must be traceable, claims must match labels, compute must be recorded, and another person must be able to reproduce the main result.

## Specs

- [SPEC-08 — Evaluation and error analysis](../phase-01-discovery-contract/specs/SPEC-08-evaluation.md)
- [SPEC-09 — Experiment and reproducibility](../phase-01-discovery-contract/specs/SPEC-09-reproducibility.md)
- [SPEC-12 — Evidence and final audit](specs/SPEC-12-final-audit.md)

## Tasks

See [TASKS.md](TASKS.md).
