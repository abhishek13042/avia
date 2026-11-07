# Project 3 — Timeline and Compute Budget

Created 2026-10-21 after the architecture audit (`DECISION_LOG.md` D-018). This is a planning estimate, not a commitment. Re-estimate at each gate.

## Assumptions

- One person working part-time (about 20–25 hours/week). Full-time (about 40 hours/week) is shown for comparison.
- Kaggle free GPU (T4/P100) with about 30 GPU-hours/week and time-limited sessions. The current quota is verified in T03 (U6).
- Local machine (verified 2026-10-21): i3-1115G4, 7.6 GB RAM, no CUDA GPU. All training and runtime benchmarks run on Kaggle; local work is engineering, tests, and CPU smoke runs only (D-020).
- Includes the best-results plan (D-021): accuracy levers, tracker tuning, offline best-accuracy track.
- The scope is the revised scope in `DECISION_LOG.md`. The GRU (T41) is optional and may be cut by its kill criterion.

## Schedule

| Phase | Tasks | Gates | Part-time | Full-time | Main driver |
|---|---|---|---|---|---|
| 1 — Contract (remaining) | T03–T09 | G0, G1 | 3–5 days | 2–3 days | 5.66 GB download, duplicate-hash check, approvals |
| 2 — Data and perception foundation | T10–T21 | G2 | 1.5–2 weeks | 1 week | Manifest, ignore-region decoding, golden fixture |
| 3 — Perception and tracking | T22–T35 | G3 | 4–6 weeks | 2.5–3.5 weeks | Kaggle GPU quota; model selection; D-021 levers; evaluator validation |
| 4 — Temporal, API, dashboard, runtime | T36–T50 | G4, G5 | 3–4 weeks | 2 weeks | Event classes, API/dashboard, runtime benchmark |
| 5 — Experiments and final audit | T51–T62 | G6, G7 | 3–4 weeks | 1.5–2 weeks | ≥3 seeds, ablations, reproduction, report |
| **Total** | T03–T62 | G0–G7 | **≈12–17 weeks** | **≈6.5–9.5 weeks** | |

Add about 20% buffer for unknowns (for example, if U1 shows 10–12 are not duplicates, or the Kaggle quota is lower).

## GPU-hour budget (Kaggle)

| Item | Runs | GPU-hours each | Total |
|---|---|---|---|
| Mask R-CNN baseline (T24) | 1 + LOSO check | 1–2 | 3–6 |
| Main-model candidate comparison (T26) | 3 candidates | 2–6 | 10–20 |
| Main model final training (T28) | 3 seeds | 2–6 | 6–18 |
| Tracker tuning and evaluation (T29–T32) | many, inference only | 0.2–0.5 | 3–6 |
| Optional GRU (T41) | 3–6 | 0.2–0.5 | 1–3 |
| Runtime benchmark (T49) | few | 0.5–1 | 2–4 |
| Experiments and ablations (T52–T57) | 10–20 | 1–3 | 20–50 |
| Reproduction run (T58) | 1 | 2–6 | 2–6 |
| D-021 levers: lever screening, tracker grid search, offline track | 10–15 | 1–2 | 15–25 |
| **Total** | | | **≈65–140 GPU-hours** |

At about 30 GPU-hours/week, compute alone needs 2.5–5 weeks of quota, spread over Phases 3 and 5. GPU runs should be queued while engineering work continues.

## Critical path

T03 (download + duplicate check) → G0 → T06 split freeze → T12–T15 → T24 baseline → T26 model selection → T32 tracking evaluation → T49 runtime → T52 comparisons → T58 reproduction → T62.

## Biggest schedule risks

1. Kaggle quota or session limits are lower than assumed.
2. Main-model small-object recall is poor and needs tiling/high-resolution work.
3. Ignore-region encoding differs from KITTI MOTS and needs a custom decoder.
4. The ≥25 FPS target is not reachable on the available GPU (result: "measured offline", not a delay).
