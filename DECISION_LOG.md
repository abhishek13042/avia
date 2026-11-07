# Project 3 — Decision Log

Per `DOCUMENTATION_PROCESS.md` Rule 9, every changed decision is recorded here with the previous decision, the new decision, the reason, and the impact. Original wording is preserved in this file. The live documents carry only the current decision plus a pointer to this log.

Source audit for D-001 to D-024: [ARCHITECTURE_AUDIT_2026-10-21.md](ARCHITECTURE_AUDIT_2026-10-21.md). Fact IDs (F1–F14) refer to §1 of that audit.

- Date of all entries below: 2026-10-21
- Status of all entries below: `Decision` — applied to documents. User requested application of all audit changes on 2026-10-21. G0 discovery approval is still pending.

---

## D-001 — Test-sequence duplicate grouping (audit C1)

- Previous: "sequences 0–5 for training, 6–8 for testing/validation, and 10–12 as testing sequences with ignore regions."
- New: Sequences {6, 10}, {7, 11} and {8, 12} are treated as one `duplicate_group` each until hash comparison proves otherwise. Sequences 10–12 (ignore regions) form the only official test set. Sequences 6–8 are never used for training, tuning, threshold selection, or model selection.
- Reason:
  - The paper reports 9 annotated sequences (6 train / 3 test, F3) but Zenodo has 12 folders.
  - Frame arithmetic: 1,147 + 526 ≈ 1,673 unique frames, while the mirror has 2,198 files.
  - The ignore regions are overlays painted on the test images (F6).
- Evidence status: `Assumption` (strong). It is verified in T03 (hash comparison) and T15.
- Impact: SPEC-01, T03, T06, T12, T15; architecture §3 and §7.

## D-002 — Validation split carved from training sequences (audit C2)

- Previous: no validation split defined, apart from "6–8 for testing/validation".
- New:
  - Validation comes only from training sequences 0–5. Default: leave-one-sequence-out (LOSO) over the 6 training sequences for model selection and thresholds; the final model is retrained on all of 0–5.
  - Fallback when compute is insufficient: one fixed holdout of 1 wearable + 1 Parrot Anafi sequence.
  - T06 records the exact sequence IDs after T03 confirms which platform produced each sequence.
- Reason: The official split is train/test only (F3, F4).
- Limitation: With only 6 groups, validation variance is high.
- Impact: SPEC-01, T06, T24, T28, T41, T51.

## D-003 — Correct the published baseline reference (audit C3)

- Previous: "Published results report MOTSP 80.4, sMOTSA 38.7, and MOTSA 52.9."
- New: The reference rows from paper Table I, evaluated on test sequences with ignore regions:
  - PointTrack (scratch): sMOTSA 38.7, MOTSA 52.9, MOTSP 80.0, 7.81 FPS.
  - TrackR-CNN: sMOTSA 35.7, MOTSA 47.8, MOTSP 80.4, 0.20 FPS.
- Reason: The abstract combines numbers from two different models (F9, F10).
- Impact: Architecture §3, SPEC-08, T25, T32.

## D-004 — Add paper-comparable MOTS metrics; HOTA becomes the mask-based primary metric (audit C4)

- Previous: Tracking metrics were HOTA, IDF1, MOTA, ID switches, fragmentation, track survival, count MAE/RMSE.
- New:
  - Primary metric: mask-based HOTA (with DetA, AssA, LocA) via TrackEval.
  - Paper-comparable: sMOTSA, MOTSA, MOTSP, IDS in the KITTI MOTS definition, on sequences 10–12 with ignore regions.
  - Also reported: IDF1, fragmentation, track survival, count metrics.
  - Results with and without ignore regions are both reported.
  - Before any number is reported, the evaluator is validated with GT-as-prediction (must score perfectly) and hand-computed toy cases.
- Reason: The paper reports only sMOTSA / MOTSA / MOTSP / IDS (F8).
- Impact: SPEC-08, T07, T32, T33.

## D-005 — Replace the box-only baseline with an instance-segmentation baseline (audit C5)

- Previous: "Perception baseline: YOLOX-S with boxes derived from masks."
- New:
  - Perception baseline: Mask R-CNN R50-FPN, COCO-pretrained, full resolution.
  - YOLOX-S is optional: box-only, evaluated only with box metrics against mask-derived GT boxes, and labelled `derived-box`.
- Reason: MOTS metrics and the project claim need masks. TrackR-CNN, the paper's baseline, is built on Mask R-CNN.
- Impact: SPEC-04, Phase 3 PHASE.md, T22–T25.

## D-006 — Main perception model chosen by a pre-registered comparison (audit C6)

- Previous: "Main research perception: Mask2Former with a practical backbone."
- New:
  - The main model is selected on validation (D-002) from {Mask R-CNN high-res/tiled, RTMDet-Ins, Mask2Former}.
  - Criteria, frozen in T26 before any run: mask AP, small-object recall (apples below 32 px), and latency.
  - Ultralytics YOLO-seg is excluded unless AGPL-3.0 is accepted explicitly.
- Reason: Apples are ~30–50 px wide in 1296×972 frames, ~48 per frame (F2). Mask2Former's authors list small objects as a limitation, and the model is heavy on Kaggle GPUs.
- Impact: SPEC-04, Phase 3 PHASE.md, T26–T28.

## D-007 — Tracking: no appearance ReID by default; add OC-SORT (audit C7)

- Previous:
  - "Tracking baseline: ByteTrack."
  - "Main tracking: BoT-SORT-style association with camera-motion compensation and mask-overlap gating."
  - T30: "Add motion, appearance where justified, …"
- New:
  - Baseline: ByteTrack, with masks attached to boxes.
  - Main candidates: OC-SORT and BoT-SORT without ReID, both with camera-motion compensation (CMC) and mask-IoU gating. The winner is selected on validation.
  - Appearance ReID is an ablation only.
- Reason: In the paper, learned appearance association lost to plain box association, and ID reuse between identical apples was the main failure mode (F11, F12).
- Impact: SPEC-05, Phase 3 PHASE.md, T29–T31, T53.

## D-008 — Three event classes, nullable calibration (audit C8)

- Previous:
  - Event and anomaly metrics included PR-AUC, false alerts per camera-hour and calibration of alerts.
  - `EventRecord.calibrated_probability` was mandatory.
  - Hypothesis 4: "Calibration improves alert quality."
- New:
  - Every event type is assigned one class:
    - `gt_derived`: track lost, reappeared, long gap. Derived from GT ID gaps and evaluated with precision/recall/F1/onset error.
    - `synthetic`: frame drop, frozen frame, blur, brightness shift, detector dropout. Evaluated only on injected perturbations and reported as synthetic.
    - `ranked_only`: count instability, density change, normal-behavior deviation. Reported only as review-ranked examples, with no accuracy claim.
  - `calibrated_probability` is nullable.
  - Calibration (ECE/Brier/NLL) is applied to detector confidence only.
  - Hypothesis 4 becomes: "Detector confidence calibration improves precision at a fixed alert budget on `gt_derived` and `synthetic` events."
  - False-alert rates are reported per 1,000 frames, not per camera-hour.
- Reason: The test set is ~526 frames (~18–21 s of video) and has no event or anomaly labels.
- Impact: Architecture §6 and §7, SPEC-07, SPEC-08, T42–T44, T54.

## D-009 — GRU becomes optional with a kill criterion (audit C9)

- Previous: "Main temporal model: causal GRU over track-level features where supported."
- New:
  - The GRU is optional.
  - Allowed targets: GT-derived track continuation and gap prediction only.
  - Kill criterion, frozen in T40: the GRU must beat the deterministic baseline on LOSO validation by a margin pre-registered in T40 (default: ≥2 points absolute in the chosen F1/AUC). Otherwise it is dropped and reported as a negative result.
- Reason: There are ~1,147 training frames and 6 sequences, and no occlusion or visibility labels exist.
- Impact: SPEC-06, Phase 4 PHASE.md, T40, T41.

## D-010 — Synthesized timestamps (audit M1)

- Previous: `FramePacket.capture_pts` with no source defined.
- New:
  - `capture_pts` is synthesized as `frame_index / nominal_fps`, where `nominal_fps` is a per-platform configuration value.
  - `pts_source` is `synthetic` for APPLE MOTS.
  - Frame spacing (consecutive vs. subsampled) is checked in T03 and T17.
- Reason: The dataset contains numbered PNGs only. Capture was 25–30 FPS (F5).
- Impact: SPEC-02, T03, T17.

## D-011 — Real-time target defined (audit M2)

- Previous: "Only call the system real-time if the measured pipeline sustains the required source rate."
- New:
  - Required source rate: ≥25 FPS sustained at 1296×972, with a stress case at 30 FPS.
  - The test is end-to-end: ingestion → perception → tracking → events.
  - It runs on a named GPU, recorded with its specification.
  - The PointTrack reference (7.81 FPS, F9) is reported for context.
  - Model-only and end-to-end throughput are reported separately.
- Impact: SPEC-11, T49, T50.

## D-012 — Two count definitions (audit M3)

- Previous: "Visible-apple counting", "count MAE/RMSE" (undefined).
- New:
  - (a) Per-frame visible count: MAE/RMSE against GT instances per frame, inside non-ignore areas.
  - (b) Per-sequence unique-fruit count: predicted distinct track IDs vs. GT distinct IDs, reported as absolute and relative error.
  - No tree-level or yield claim, because only one side of each tree is visible (F14).
- Impact: T05, T07, T38, SPEC-08.

## D-013 — Statistics policy for 3 test sequences (audit M4)

- Previous: "bootstrap unit" and "confidence intervals" were unspecified.
- New:
  - Report per-sequence tables plus pooled metrics.
  - Use ≥3 training seeds for every main comparison and report mean ± standard deviation.
  - Optionally use a block bootstrap over contiguous frame windows (default 30 frames), with the autocorrelation caveat stated.
  - Never bootstrap over sequences.
  - The DJI Matrice test sequence is an unseen-platform slice (n = 1, descriptive only).
- Impact: SPEC-08, T52, T55.

## D-014 — Ignore-region handling (audit M5)

- Previous: "Preserve ignore regions" (encoding unspecified).
- New:
  - The encoding is verified in T03 and T13 (instance-PNG class/id vs. pixel-only overlay).
  - Evaluation follows KITTI `mots_tools` / TrackEval ignore semantics.
  - Training images contain no gray overlays. This train/test appearance shift is documented as a `Limitation` and measured by comparing results with and without ignore regions.
- Impact: SPEC-03, SPEC-08, T13, T32.

## D-015 — Dataset facts corrected (audit M6)

- Previous:
  - "1,700 annotated frames"
  - "approximately 86,000 apple instances"
  - "Approximately 5.66 GB"
  - AppleMOTS source = WUR Google Drive
  - "Dataset DOI/version not found"
- New:
  - 1,673 unique annotated frames (paper); ~2,198 files including duplicated test frames (mirror).
  - "Almost 86,000" masks; 2,304 unique apples.
  - Archive of 5,661,248,829 bytes, MD5 `1f9b8cd79f05469d656a01015889b55d`.
  - Source of record: Zenodo DOI 10.5281/zenodo.5939726, version v1. The Google Drive link returns 404.
- Impact: Architecture §3, T01 correction note.

## D-016 — Unified gate scheme (audit M7)

- Previous: Two inconsistent schemes.
  - Architecture doc: G0 discovery, G1 data contract, G2 perception/tracking, G3 temporal, G4 runtime, G5 science, G6 final.
  - `EXECUTION_ORDER.md`: G1 data contract, G2 data quality, G3 perception/tracking, G4 runtime, G5/G6 science + final.
- New (used in every file):

  | Gate | Name | Closes |
  |---|---|---|
  | G0 | Discovery approval | Before T01 (retroactive, see D-017) |
  | G1 | Project contract | Phase 1 (T09) |
  | G2 | Data quality | Phase 2 (T21) |
  | G3 | Perception/tracking correctness | Phase 3 (T35) |
  | G4 | Temporal correctness | Phase 4 after T44 |
  | G5 | Runtime qualification | Phase 4 (T50) |
  | G6 | Scientific quality | Phase 5 after T57 |
  | G7 | Final audit | Phase 5 (T62) |

## D-017 — Status synchronization and process deviation (audit M8)

- Previous:
  - The README says no work has started and that approval is needed before T01.
  - Phase 1 TASKS.md shows T01/T02 as Pending.
  - EXECUTION_STATUS.md shows T01/T02 Verified and T03 In Progress.
- New:
  - All status tables are synchronized: T01 Verified, T02 Verified, T03 In Progress.
  - Process deviation recorded: T01–T02 (read-only research tasks) were executed before G0 approval.
  - G0 remains pending user approval and must be granted before T04 freezes the problem.
- Impact: README, EXECUTION_ORDER, EXECUTION_STATUS, phases/README, Phase 1 TASKS.md.

## D-018 — Compute budget (audit M9)

- New: SPEC-09 requires a GPU-hour budget per experiment, a checkpoint/resume test across Kaggle sessions, and a recorded Kaggle quota (verified in T03). The total plan is in [PROJECT_TIMELINE.md](PROJECT_TIMELINE.md).

## D-019 — Minor contract and process fixes (audit m1–m9)

| Item | Change |
|---|---|
| m1 | Fixed the broken code fence in `DOCUMENTATION_PROCESS.md`. |
| m2 | SPEC-08 split: metric definitions are frozen in Phase 1 (T07); the evaluation implementation depends on SPEC-01–07. |
| m3 | Removed the SPEC-07 → SPEC-11 dependency. |
| m4 | T48 extends the T17 adapter instead of building a new replay runner. |
| m5 | `TrackState` / `TrackFrame` gain an RLE `mask` field. |
| m6 | `SampleRecord` gains `platform`, `duplicate_group`, `has_ignore_overlay`, `pts_source`. |
| m7 | The paper PDF is cited, never redistributed (Taverne terms). |
| m8 | A third-party license table was added to SPEC-12 and is filled in T02/T60. |
| m9 | "Generalization" renamed to "cross-sequence / cross-platform robustness"; no cross-orchard claim. |

## D-020 — Compute environment matches the actual hardware (2026-10-21)

- Finding (T03 U6, local part): the local machine has an Intel i3-1115G4, 7.6 GB RAM, Intel UHD graphics only (no CUDA GPU), Python 3.14, and CPU-only PyTorch. About 103 GB of disk is free on D:.
- New:
  - All training, GPU inference, and the G5 runtime benchmark run on Kaggle. The "named GPU" in D-011 is the Kaggle GPU actually allocated (e.g. T4 or P100), recorded per run.
  - Local work is limited to code, unit tests, golden-fixture checks, and CPU forward passes with batch size 1.
  - Local Python environment: a separate Python 3.11 virtual environment. Python 3.14 is too new for most CV frameworks (Detectron2, MMCV); versions are pinned and verified in T10/T20.
  - Data access is streamed from the manifest; the full dataset is never loaded into 7.6 GB of RAM.
  - Kaggle weekly quota: still to be confirmed by the user (U6 remote part).
- Impact: SPEC-09, SPEC-11, EXECUTION_ORDER T03/T10/T20/T49, PROJECT_TIMELINE.md.

## D-021 — Best-results plan: pre-registered accuracy levers (2026-10-21)

- Goal: get the best defensible results without overfitting the 3 test sequences.
- Protection rule: every lever below is chosen on LOSO validation (sequences 0–5) only. The test set (10–12) is evaluated only on locked configurations, at most 3 times in total, and every test evaluation is logged in the experiment registry.
- Two reported tracks, never mixed:
  - **Online / real-time track:** causal, single pass, counted toward G5.
  - **Offline best-accuracy track:** may use TTA, sliced inference, bidirectional linking, and heavy mask propagation. Labelled "offline" in every table.

### Perception levers (apples are about 30–50 px, so small-object recall decides results)

| Lever | Why | Track |
|---|---|---|
| Train and infer at native 1296 × 972 or upscaled (×1.25–1.5) | Small objects lose detail when downscaled | Both |
| Small anchors / stride-4 FPN level (P2) | Matches 16–50 px objects | Both |
| Sliced (tiled) inference with overlap, merged by mask NMS | Raises small-object recall | Offline (online if latency allows) |
| Random gray-patch augmentation on training images | Test images 10–12 carry gray ignore overlays that training images lack; reduces the train/test appearance shift (D-014) | Both |
| Copy-paste augmentation of apple instances | Low data (≈1,147 train frames); dense small objects | Both |
| Scale jitter, color/brightness jitter, motion blur | UAV and wearable motion, outdoor light | Both |
| Higher-resolution mask head (e.g. PointRend-style refinement) | Raises MOTSP and mask AP on small objects | Both, if the latency budget allows |
| EMA weights | Stabilises training with small data | Both |
| Score threshold tuned for sMOTSA/HOTA on validation | sMOTSA is sensitive to false positives | Both |
| Flip / multi-scale TTA | Usually a small mask-AP gain | Offline only |
| Extra fruit datasets for pretraining | More apple appearance | Only after license check; never test data |

### Tracking levers (main failure mode is ID reuse between identical apples)

| Lever | Why | Track |
|---|---|---|
| Two-stage low-score association (ByteTrack principle) | Recovers partly occluded apples | Both |
| Camera-motion compensation (ECC or sparse optical flow, as in BoT-SORT) | UAV and wearable ego-motion dominates apple motion | Both |
| Mask IoU after motion warp, with strict gating | Reduces ID reuse between neighbours | Both |
| Observation-centric re-update (OC-SORT) | Recovers after short occlusions | Both |
| Conservative track re-activation (short `max_age` unless motion-consistent) | Directly targets ID reuse | Both |
| Tracker thresholds tuned by grid search on LOSO | Thresholds matter more than architecture at this data size | Both |
| Offline tracklet interpolation and linking | Fills gaps; raises IDF1/AssA | Offline only |
| Detector-seeded video mask propagation (e.g. SAM 2, license to verify) | Strong temporal masks | Offline only; candidate, dropped if it does not beat the main tracker on validation |

### Framework

- Prefer one framework for the perception comparison, so it is fair. MMDetection 3.x contains Mask R-CNN, RTMDet-Ins, and Mask2Former under Apache-2.0. Fallback: Detectron2.
- Version pins and Kaggle compatibility are verified in T10/T20.

### Impact

- SPEC-04, SPEC-05, SPEC-08, SPEC-11, EXECUTION_ORDER (T22–T32, T49, T52–T53), PROJECT_TIMELINE.md.
- Expected extra cost: about +1 week of work and +15–25 GPU-hours.

## D-022 — G0 go-ahead and Kaggle execution start (2026-10-29)

- Decision: The user's instruction on 2026-10-29 ("u have kaggle cli u have to train it over these na") is recorded as the G0 go-ahead to run work on Kaggle. The user can withdraw it at any time.
- Kaggle account `abhishekg14`; CLI 2.2.4 run as `python -m kaggle`. All AVIA kernels are private and named `avia-*`. Kernels from other projects are not touched.
- The first kernel, `avia-t03-data-audit` (CPU, internet on), downloads APPLE_MOTS.zip from Zenodo, checks the MD5 and resolves U1–U5. Its output (the extracted dataset) is the input to later kernels, so the 5.66 GB download happens only once.
- Impact: T03 can be finished. T04 onwards can start once T03 is verified.

## D-023 — Public product platform (Approved, 2026-10-30)

- Status: Approved by the user on 2026-10-30 ("will code the remaing things"). Built as recorded in D-024.
- Decision: Extend Phase 4 into a public multi-user web app (Next.js frontend, FastAPI backend, Postgres, object storage, job queue, serverless GPU worker). Full plan: `PRODUCT_PLATFORM_PLAN.md`.
- Reason: The user's main objective (2026-10-29) is a flagship computer-vision resume project that many people can use.
- Impact: T45–T48 grow; new steps P1–P8; about +3–5 weeks part-time, mostly overlapping GPU training. The research contract and metrics are unchanged.

## D-024 — Application built ahead of the task order (2026-10-30)

- Decision: The user asked on 2026-10-30 to write all documentation and code everything remaining now, with the model plugged in later. This overrides the one-task-at-a-time rule for application code. T03 stays open, and the research gates G1–G7 are not passed by this work.
- Protection: The detector is a plug-in slot, an untrained result is labelled on every page, and no metric is shown unless it comes from `scripts/evaluate.py`.
- Deviations from `PRODUCT_PLATFORM_PLAN.md`:
  - The queue is the database jobs table, not Redis. One less service; claiming is one conditional UPDATE.
  - Plain CSS, not a component library. Few pages, no build dependency.
  - Masks are stored as `jsonl.gz`, not Parquet. No extra dependency.
  - No Alembic: tables are created at startup. Needs adding before schema changes on live data.
  - No OAuth: anonymous uploads with per-client daily limits, a queue cap, and 7-day deletion.
  - Output video is WebM VP8, which browsers play and OpenCV can write without an H.264 licence issue.
  - Flat `src/avia/` layout instead of an `ml/ api/ worker/ web/ infra/` monorepo. `web/` and `deployment/` sit beside it.
- Not verified: Docker, Postgres, S3, CI, GPU training, real data, and the TrackEval run.
- Impact: T45–T48 and P1–P8 are implemented in first form and await real-model evaluation.

## D-025 — Ignore regions come from comparing 10–12 with 6–8 (2026-10-31)

- Finding: T03 kernel v4 showed APPLE MOTS has no ignore value in its labels, and its patches are translucent. The colour rule `gray_overlay_mask` scored IoU about 0.1 on sequence 10 and about 0 on 11 and 12, and marked 3–7% of sequence 12 where no patch exists.
- Decision: `kitti_mots.overlay_mask` finds patches by diffing each test frame with its clean copy in 6–8. `scripts/evaluate.py` and `scripts/run_trackeval.py` both use it; TrackEval ground truth had no overlay regions before this.
- Limit on D-001: sequences 6–8 are read only to locate patches, and never for training, tuning or scoring.
- Also fixed: the dataset is split into `train/` and `testing/`, which the loaders did not handle. Training accepts only the folder holding sequence 0.
- Caveat: the paper's own ignore handling cannot be compared directly, so differences from its scores may come partly from this.
- Impact: test scores are comparable only when they use this mask. No test evaluation had been spent when this changed.

## D-026 — Final model trained for 3 epochs (2026-11-01)

- Finding: mean F1 over the six folds peaked at the third epoch (0.791) and ended at 0.781 after 12.
- Decision: the final model on sequences 0–5 trains for 3 epochs, because it has no validation data to pick an epoch.
- Evidence: `artifacts/eval/loso_summary.json`, `artifacts/test_log.json` (1 of 3 used).
