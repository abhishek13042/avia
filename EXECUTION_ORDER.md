# Project 3 — Complete Execution Order

## Status

- Documentation status: Saved
- Implementation status: Not started
- Training status: Not started
- Current gate: G0 — Discovery approval (pending)
- Current task: T03 — Record facts, assumptions, and unknowns (In Progress)
- Completed: T01, T02 (Verified; run before G0 was recorded — process deviation, D-017)
- Next task after G0 approval and T03: T04
- Revision: 2026-10-21 audit applied; see `DECISION_LOG.md` (D-001–D-019) and `ARCHITECTURE_AUDIT_2026-10-21.md`

## Master execution chain

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
↓
NEXT TASK
```

## Mandatory rule

Execute exactly one implementation task at a time.

Do not start a dependent task until the previous task has:

- an implementation result;
- tests;
- verification;
- evidence saved in Markdown;
- a quality-gate decision.

Parallel work is limited to independent research, audits, reviews, and validation. Parallel agents must not modify the same implementation files or make architectural decisions independently.

---

## Step 0 — G0 discovery approval

Before T01:

1. Read `PROJECT_DISCOVERY_AND_ARCHITECTURE.md`.
2. Read `phases/README.md`.
3. Read `DOCUMENTATION_PROCESS.md`.
4. Confirm AppleMOTS as the primary dataset.
5. Confirm the orchard fruit perception/tracking scope.
6. Confirm that irrigation scheduling, physiology, disease, and harvest-yield claims are excluded from the first release.
7. Confirm local versus Kaggle responsibilities.
8. Confirm the five-phase methodology.
9. Confirm the revised decisions in `DECISION_LOG.md` (duplicate-group test policy, Mask R-CNN baseline, no-ReID tracking, event classes, real-time target).

T01–T02 were executed before G0 was recorded (D-017). G0 approval is required before T04.

---

# Phase 1 — Dataset, Problem, and Evaluation Contract

## Objective

Freeze the scientific problem, dataset interpretation, label semantics, split policy, metrics, and claim boundaries.

## Task order

### T01 — Register dataset sources

Record AppleMOTS, IrriDrone, the vineyard alternative, and TexCot22 with source URLs, paper URLs, dataset versions, and licenses.

### T02 — Verify access and licenses

Confirm download availability, archive versions, file structure, license, citation, and known limitations.

### T03 — Record facts, assumptions, and unknowns

Separate verified facts from assumptions. Do not use unknown information as ground truth.

Must resolve: (1) whether sequences 10–12 are ignore-region copies of 6–8 (image hashes), (2) ignore-region encoding in instance PNGs, (3) platform per sequence ID and the missing sequence 9, (4) consecutive vs. subsampled frames, (5) per-sequence frame/instance counts, (6) local GPU and current Kaggle GPU quota. Local part of (6) resolved: no CUDA GPU, 7.6 GB RAM (D-020).

### T04 — Freeze the real-world problem

Freeze:

> Orchard fruit perception, persistent tracking, temporal counting analytics, and operational anomaly ranking.

Exclude irrigation scheduling, plant water stress, disease diagnosis, and harvest-yield prediction.

### T05 — Freeze the label ontology

Define apple class, instance mask, bounding box, persistent ID, ignore region, visible object, occlusion, lost track, reappeared track, and operational anomaly.

Assign every event type one class: `gt_derived`, `synthetic`, or `ranked_only` (D-008). Occlusion is proxied by GT ID gaps; there is no occlusion label.

### T06 — Freeze the split strategy

Use sequence-disjoint splits. Never randomly split adjacent frames.

- Treat {6, 10}, {7, 11}, {8, 12} as duplicate groups; test only on 10–12; never tune on 6–8 (D-001).
- Validation from sequences 0–5 only: leave-one-sequence-out by default, fallback holdout of 1 wearable + 1 Parrot Anafi sequence (D-002).
- Record platform per sequence; the DJI Matrice test sequence is an unseen-platform slice.

### T07 — Freeze metrics

Define detection, segmentation, tracking, count, temporal, anomaly, calibration, and runtime metrics.

- Primary tracking metric: mask-based HOTA (TrackEval); paper-comparable sMOTSA/MOTSA/MOTSP/IDS on 10–12 with ignore regions (D-004).
- Reference numbers: PointTrack 38.7 / 52.9 / 80.0 and TrackR-CNN 35.7 / 47.8 / 80.4 (D-003).
- Counts: per-frame visible count and per-sequence unique count; no yield claim (D-012).
- Events: false alerts per 1,000 frames; accuracy only on `gt_derived` and `synthetic` events.
- Runtime target: ≥25 FPS sustained end-to-end at 1296 × 972 on a named GPU (D-011).
- Statistics: per-sequence tables, ≥3 seeds, optional 30-frame block bootstrap, never bootstrap over sequences (D-013).

### T08 — Freeze the Project 3 contract

Finalize the problem, dataset, labels, splits, metrics, claims, non-goals, and evidence requirements.

### T09 — Obtain approval

Do not begin Phase 2 until the project contract is approved.

## Gate G1 — Project contract

Pass only when:

- the dataset is selected;
- labels are understood;
- splits are leakage-safe, including duplicate groups;
- a validation strategy from sequences 0–5 is frozen;
- metrics are defined;
- unsupported claims are removed;
- project direction is approved.

---

# Phase 2 — Data Engineering and Perception Foundation

## Objective

Create a verified data path from AppleMOTS to model-ready samples without serious local CPU training.

## Task order

### T10 — Create repository skeleton

Create the planned configuration, source, test, documentation, data, deployment, and artifact directories. Create a Python 3.11 virtual environment and a pinned dependency file shared with Kaggle (D-020).

### T11 — Create dataset manifest specification

Define dataset ID, sequence ID, frame ID, image path, annotation path, group ID, split, checksum, and license fields, plus `platform`, `duplicate_group`, `has_ignore_overlay`, and `pts_source` (D-019 m6).

### T12 — Build the AppleMOTS frame index

Index selected frames, sequence IDs, frame IDs, image paths, and annotation paths.

### T13 — Build the annotation index

Index masks, instance IDs, frame IDs, sequence IDs, and ignore-region information.

### T14 — Validate image and mask dimensions

Check alignment, missing annotations, invalid files, and image/mask dimensions.

### T15 — Validate identity continuity

Check ID validity, duplicate IDs, persistence, and sequence transitions.

### T16 — Render annotation visualizations

Create evidence showing images, masks, boxes, IDs, and ignore regions.

### T17 — Implement the deterministic frame adapter

Produce the canonical `FramePacket` structure with stream ID, sequence ID, frame ID, timestamp, image, source URI, and dropped-frame status.

Timestamps are synthesized as `capture_pts = frame_index / nominal_fps` per platform with `pts_source = synthetic` (D-010).

### T18 — Create the golden fixture

Include sample frames, masks, IDs, one missing frame, one dropped-frame case, and expected outputs.

### T19 — Add model input/output contracts

Define `PerceptionFrame`, `GroundTruthFrame`, `PerceptionInstance`, and `TrackState` contracts. `TrackState` carries an optional RLE mask field (D-019 m5).

### T20 — Run local forward-pass smoke checks

Check model initialization, shapes, coordinates, memory behavior, and NaN outputs on CPU with batch size 1 within 7.6 GB RAM. Confirm the chosen framework version installs on Kaggle (D-020, D-021).

### T21 — Pass the data-quality gate

Do not continue if the dataset, labels, splits, or smoke tests fail.

## Gate G2 — Data quality

Pass only when images, masks, IDs, ignore regions, duplicate groups, model inputs, and the golden fixture are verified.

---

# Phase 3 — Perception and Tracking

## Objective

Build and evaluate visual perception and persistent tracking.

## Task order

### T22 — Implement baseline perception configuration

Use Mask R-CNN R50-FPN (COCO-pretrained, full 1296 × 972 resolution) as the instance-segmentation baseline (D-005). YOLOX-S with mask-derived boxes is optional and box-only.

### T23 — Run the tiny local perception smoke test

Check model loading, forward pass, output placement, and tiny-sample behavior.

### T24 — Run Kaggle baseline training

Train the baseline on Kaggle GPU and save checkpoint, configuration, hashes, seed, logs, and metrics. Runs must be resumable and stay within the GPU-hour budget (D-018).

### T25 — Evaluate baseline perception

Report box and mask AP50, AP75, AP@[0.50:0.95], precision, recall, small-object recall (below 32 px), and GT-gap (occlusion-proxy) performance on validation.

### T26 — Implement main segmentation configuration

Select the main model on validation from Mask R-CNN high-res/tiled, RTMDet-Ins, and Mask2Former using pre-registered criteria: mask AP, small-object recall, and latency (D-006).

### T27 — Run the main-model local initialization and forward pass

Perform initialization and smoke testing locally. Do not perform serious CPU training.

### T28 — Run Kaggle main training

Train the selected main segmentation model on Kaggle GPU with ≥3 seeds for the final comparison. Apply the D-021 perception levers selected on validation.

### T29 — Implement ByteTrack baseline

Create persistent tracks from perception outputs, attaching masks to tracks.

### T30 — Implement main association (OC-SORT / BoT-SORT without ReID)

Add motion, camera-motion compensation, track aging, and occlusion handling. Do not use appearance ReID in the main tracker; apples are homogeneous and the paper shows learned appearance association underperforms. ReID is an ablation only (D-007).

### T31 — Add mask-aware association

Use mask IoU as an association gate/signal where masks are available. Tune tracker thresholds by grid search on LOSO validation (D-021).

### T32 — Evaluate tracking

Report mask-based HOTA (DetA/AssA/LocA), IDF1, identity switches, fragmentation, track survival, per-frame count MAE/RMSE, and per-sequence unique-count error. Report paper-comparable sMOTSA/MOTSA/MOTSP/IDS on 10–12 with ignore regions. Validate the evaluator first: GT-as-prediction must score perfectly. Report the online and offline best-accuracy tracks in separate tables; count each test-set evaluation (maximum 3, D-021).

### T33 — Complete oracle-ladder analysis

Compare ground-truth detections versus predicted detections and ground-truth tracks versus predicted tracks.

### T34 — Produce the tracking failure gallery

Document identity switches, missed objects, false tracks, fragmentation, occlusion failures, and frame-gap failures.

### T35 — Pass the perception/tracking gate

Do not continue if predictions, tracking IDs, metrics, or failure analysis are not verified.

## Gate G3 — Perception/tracking correctness

Pass only when detections, masks, tracks, the validated evaluator, HOTA/IDF1/sMOTSA metrics, comparison with the published baseline, and detector-versus-association error separation are correct.

---

# Phase 4 — Temporal Intelligence, API, Dashboard, and Runtime

## Objective

Convert tracks into temporal analytics, operational anomaly signals, and a measured inference service.

## Task order

### T36 — Define the track-level feature schema

Define track ID, center, mask area, box area, confidence, visibility, missed frames, association score, age, density, and count change.

### T37 — Implement causal feature history

Use bounded history and prevent future-frame access.

### T38 — Implement count and persistence analytics

Calculate per-frame visible count, per-sequence unique count, count trend, variance, persistence, track duration, reappearance rate, and missing-track rate. No yield claim (D-012).

### T39 — Implement the rule-based temporal baseline

Implement deterministic track-loss, count-instability, scene-degradation, and input-failure rules.

### T40 — Define supported temporal learning targets

Use only GT-derived targets: track continuation, GT ID gaps (occlusion proxy), and temporal consistency. No unsupported labels.

### T41 — Train and evaluate the causal GRU if justified (optional)

Use Kaggle GPU for serious training and compare against deterministic baselines. Kill criterion: keep the GRU only if it improves the target metric by ≥2 points absolute under LOSO validation (D-009); otherwise record it as a negative result and mark the task `Deferred`.

### T42 — Implement the operational event state machine

Implement track loss, reappearance, prolonged occlusion, count instability, scene degradation, input failure, and abnormal density change. Tag each event `gt_derived`, `synthetic`, or `ranked_only`; `calibrated_probability` is nullable (D-008).

### T43 — Implement normal-behavior anomaly ranking

Start with feature-distance and threshold baselines. Do not describe this as disease or crop-stress detection. Accuracy is measured only on synthetic injections; other anomalies are review-ranked.

### T44 — Define event evidence format

Every event must reference source frames, timestamps, scores, confidence, configuration, and evidence.

### T45 — Define API schemas

Freeze request and response contracts before API implementation.

### T46 — Implement the API

Implement stream, health, event, track, evidence, model, and metrics endpoints.

### T47 — Implement the dashboard

Display input, detections, masks, tracks, counts, events, anomaly scores, evidence, health, model version, and runtime metrics.

### T48 — Implement the replay runner

Support offline, source-paced, causal, frame-skipping, and dropped-frame replay. Extends the T17 frame adapter rather than duplicating it (D-019 m4).

### T49 — Benchmark end-to-end runtime

Measure throughput, inference latency, tracking latency, API latency, p50/p95/p99 latency, memory, GPU utilization, drops, and alert delay at 1296 × 972 on the allocated Kaggle GPU (recorded by name), at 25 FPS and a 30 FPS stress case. Try ONNX/TensorRT FP16 export and detector-interval propagation if the target is missed (D-020).

### T50 — Pass the runtime gate

Only call the system real-time if the measured pipeline sustains ≥25 FPS end-to-end under documented conditions (D-011). Otherwise label it "measured offline".

## Gate G4 — Temporal correctness (after T44)

Pass only when causal mode has no look-ahead, event schemas and classes are frozen, and every event has traceable evidence.

## Gate G5 — Runtime qualification (T50)

Pass only when runtime measurements are repeatable and the real-time/offline label is justified by evidence.

---

# Phase 5 — Experiments, Evidence, and Final Audit

## Objective

Establish scientific usefulness, reproducibility, cross-sequence/cross-platform robustness, and portfolio defensibility.

## Task order

### T51 — Freeze the experiment matrix

Freeze baselines, main model, tracker comparisons, temporal comparisons, calibration, runtime comparisons, and useful ablations.

### T52 — Run controlled baseline/main comparisons

Compare perception, segmentation, tracking, temporal, and confidence-calibration alternatives.

### T53 — Run justified ablations

Evaluate only justified changes such as resolution, tiling, augmentation (gray-patch, copy-paste), model size, detector interval, mask association, CMC, temporal window, precision, and event duration. Each ablation removes one D-021 lever from the final configuration.

### T54 — Run calibration analysis

Calibrate detector confidence only. Report reliability diagrams, ECE, Brier score, NLL, and precision at alert thresholds on `gt_derived` and `synthetic` events.

### T55 — Run cross-sequence / cross-platform robustness analysis

Use per-sequence results, LOSO folds, platform groupings (the DJI Matrice test sequence as an unseen-platform slice, n = 1), object density, GT-gap occlusion proxy, and object size. Report descriptively; do not claim broad generalization.

### T56 — Run error analysis by slice

Create visual and numerical evidence for false positives, false negatives, bad masks, ID switches, fragmentation, count instability, false alerts, missed alerts, and runtime failures.

### T57 — Run compute and accuracy–latency analysis

Record model accuracy, FPS, p95 latency, memory, GPU utilization, and dropped frames.

### T58 — Reproduce the final run from a clean environment

Re-run the final documented command with the recorded dataset, split, configuration, checkpoint, and environment.

### T59 — Assemble the final evidence package

Include dataset card, split report, logs, checkpoints, metrics, visualizations, error gallery, runtime report, API evidence, dashboard evidence, and reproduction instructions.

### T60 — Perform the independent final audit

Audit provenance, licenses, leakage, metrics, claims, runtime, failure handling, API behavior, dashboard behavior, and documentation.

### T61 — Produce the final portfolio report and demo

Explain the problem, data, limitations, architecture, baselines, models, metrics, runtime, errors, robustness, failures, and reproducibility.

### T62 — Pass the final quality gate

The project is complete only when the final evidence is reproducible and all claims match available ground truth.

## Gate G6 — Scientific quality (after T57)

Pass only when baselines, main comparison (≥3 seeds), ablations, error analysis, robustness, calibration, and compute analysis are complete.

## Gate G7 — Final audit (T62)

Pass only when reproduction succeeds, evidence is complete, licenses are correct, and every claim matches available ground truth.

---

## Milestones

### Data-ready milestone

```text
T01–T21
```

Produces a validated dataset, correct splits, correct labels, and a golden fixture.

### Perception/tracking MVP

```text
T22–T35
```

Produces detection, segmentation, persistent tracking, counting, and tracking metrics.

### Working application milestone

```text
T36–T50
```

Produces temporal analytics, operational events, anomaly ranking, API, dashboard, and runtime measurements.

### Portfolio-quality milestone

```text
T51–T62
```

Produces experiments, ablations, error analysis, robustness analysis, runtime evidence, reproducible reporting, and the final demo.
