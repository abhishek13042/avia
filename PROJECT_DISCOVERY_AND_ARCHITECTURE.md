# Project 3 — Real-Time Agricultural Video Intelligence

## Document status

- Status: Discovery and architecture complete; revised 2026-10-21 after audit (see [DECISION_LOG.md](DECISION_LOG.md) D-001–D-019 and [ARCHITECTURE_AUDIT_2026-10-21.md](ARCHITECTURE_AUDIT_2026-10-21.md))
- Implementation status: Not started
- Training status: Not started
- Primary dataset decision: AppleMOTS (Zenodo v1), pending G0 user approval
- Methodology: `PROJECT → PHASE → SPEC → TASK → IMPLEMENTATION → TEST → VERIFICATION → EVIDENCE → QUALITY GATE`
- Execution rule: One implementation task at a time

---

## 1. Project understanding

```text
Agricultural video
→ Visual perception
→ Temporal association / tracking
→ Temporal reasoning
→ Event / anomaly intelligence
→ Analytics
→ Measured real-time inference
→ API / dashboard
```

The project prioritizes correctness, scientific quality, engineering quality, reproducibility, experimental evidence, interview defensibility, and then feature count.

No code, serious training, large dependency installation, or Phase 0 implementation has been performed.

### Compute policy

#### Local

- Setup, inspection, preprocessing validation, visualization, tests, model initialization, forward passes, tiny smoke tests, inference, pipeline debugging, API, dashboard, and runtime integration.

#### Kaggle GPU

- Baseline training, main training, experiments, ablations, hyperparameter experiments, final model selection, full evaluation, and performance benchmarking.

The same training and evaluation code must run locally for smoke tests and on Kaggle for serious training.

---

## 2. Current plan audit

### Strengths

- Agricultural video is a meaningful computer-vision portfolio domain.
- Perception → tracking → temporal intelligence is technically serious.
- Precision agriculture supplies a real operational context.
- Kaggle GPU training plus local engineering is appropriate.
- Evidence-based quality gates are suitable for research-quality work.

### Risks discovered

1. **Choosing IrriDrone only because it mentions irrigation.** Its labels do not provide complete ground truth for irrigation intelligence.
2. **Treating visual patterns as physiological truth.** RGB video alone cannot establish soil moisture, water potential, irrigation need, disease cause, or harvest outcome.
3. **Calling the system real-time without measurement.** Throughput, latency, memory, dropped frames, and alert delay must be measured.
4. **Temporal leakage.** Random neighboring-frame splits are invalid.
5. **Unsupported feature expansion.** Disease diagnosis, irrigation scheduling, stress prediction, and harvest-yield prediction require labels that the chosen dataset does not provide.
6. **Duplicated test frames.** AppleMOTS test sequences 10–12 are very likely ignore-region copies of 6–8; using 6–8 for tuning would leak the test set (D-001).
7. **Small data and small objects.** About 1,673 unique frames, 9 sequences, and apples roughly 30–50 px wide constrain model choice, temporal learning, and statistics (D-006, D-009, D-013).
8. **No event or anomaly labels.** Event/anomaly accuracy can only be measured on GT-derived or synthetic events (D-008).

### Revised plan

Use the public dataset with the strongest ground truth for perception and tracking, then build temporal analytics and operational anomaly intelligence with explicit claim boundaries.

---

## 3. Dataset and problem research

### Dataset comparison

| Dataset | Verified strengths | Main limitations | Decision |
|---|---|---|---|
| **AppleMOTS** | Open, CC BY 4.0, almost 86,000 apple masks, 1,673 unique annotated frames, 2,304 unique apples, temporally consistent instance IDs and masks | Frame sequences only, no timestamps; small objects; only 9 unique sequences; no validation split; no irrigation or physiological labels | **Recommended primary dataset** |
| **IrriDrone** | Open, CC BY 4.0, 674 paired one-rotation recordings, 50 FPS MP4, irrigation metadata | Embedded overlays instead of machine-readable masks; no frame-level flow/pressure; no anomaly labels; about 122 GB | Irrigation-specific alternative |
| **Vineyard grape-bunch dataset** | Open, CC BY 4.0, 40 MP4 files, 29 annotated videos, temporally consistent grape masks | One vineyard/cultivar/session; sparse labels; no direct yield or disease ground truth | Strong raw-video alternative |
| **TexCot22 / NTrack** | Standard MOT structure, approximately 9,000 frames, approximately 150,000 instances, persistent cotton-boll IDs | Bounding boxes only; cotton-specific; CC BY-NC-SA 4.0 | Strong MOT alternative |
| **PhenoBench** | Crop, weed, plant, and leaf segmentation | Primarily image-based | Useful spatial benchmark |
| **Agriculture-Vision** | Aerial agricultural anomaly-pattern masks | Not persistent video tracking | Useful complementary benchmark |
| **LettuceTrack** | Relevant agricultural tracking paper | Public access and licensing are not independently clear | Not primary |

### AppleMOTS — verified facts

Sources:

- [Zenodo dataset (v1, source of record)](https://doi.org/10.5281/zenodo.5939726)
- [APPLE MOTS paper](https://doi.org/10.1109/LRA.2022.3199026) ([open copy, Taverne terms — cite, do not redistribute](https://edepot.wur.nl/577473))
- [WUR paper record](https://research.wur.nl/en/publications/apple-mots-detection-segmentation-and-tracking-of-homogeneous-obj/)
- [WUR repository (MIT)](https://git.wur.nl/said-lab/rt-obj-tracking)

Verified facts (re-verified against the paper full text on 2026-10-21):

- Open Zenodo record, version v1 (2022-02-25), CC BY 4.0 license.
- Archive `APPLE_MOTS.zip`: 5,661,248,829 bytes, MD5 `1f9b8cd79f05469d656a01015889b55d`.
- Almost 86,000 manually annotated apple masks over **1,673 frames**, **2,304 unique apple instances**.
- Resolution 1296 × 972; apples are roughly 30–50 px wide.
- Acquisition: wearable sensor platform, Parrot Anafi UAV, and DJI Matrice 210 RTK V2 UAV; 25–30 FPS video; one orchard.
- **9 annotated sequences: 6 train (2 wearable + 4 Parrot Anafi), 3 test (1 DJI Matrice + 1 Parrot Anafi + 1 wearable).**
- Zenodo folders: 0–5 training, 6–8 "testing/validation", 10–12 testing with ignore regions; sequence 9 is not described.
- Ignore regions are gray overlays painted on test images over unlabelled background apples (KITTI-style).
- Annotation exported as KITTI MOTS PNG (`images/<seq>/<frame>.png`, `instances/<seq>/<frame>.png`).

Published baseline (paper Table I, test set with ignore regions):

| Method | sMOTSA | MOTSA | MOTSP | FPS |
|---|---|---|---|---|
| PointTrack (scratch) | 38.7 | 52.9 | 80.0 | 7.81 |
| TrackR-CNN | 35.7 | 47.8 | 80.4 | 0.20 |

The abstract's "MOTSP 80.4, sMOTSA 38.7, MOTSA 52.9" mixes these two rows (D-003). The paper reports no HOTA, IDF1, AP, or count metrics.

Paper findings that shape this architecture:

- The learned appearance association head underperformed box-based association; Kalman-filter and optical-flow mask-warping variants failed.
- The main failure mode is ID reuse between visually identical apples.
- Only one side of each tree is observed; double counting across sides remains possible.

Assumptions and unknowns (resolved in T03):

- `Assumption` (strong): sequences 10–12 are ignore-region copies of 6–8 (a secondary mirror lists 2,198 files vs. 1,673 unique frames). They are treated as duplicate groups (D-001).
- `Unknown`: whether ignore regions are also encoded in instance PNGs.
- `Unknown`: the platform of each sequence ID.
- `Unknown`: whether annotated frames are consecutive or subsampled.
- `Unknown`: per-sequence frame counts.

Supports:

- Apple instance segmentation.
- Bounding-box detection derived from masks.
- Persistent identity tracking.
- Occlusion and identity-association evaluation.
- Per-frame visible-apple counting and per-sequence unique-apple counting (one-sided view only).
- Track continuity analysis.
- Mask-aware temporal analytics.
- Frame-processing performance benchmarking.

Does not support:

- Irrigation events.
- Soil moisture or water stress.
- Disease classification.
- Maturity or ripeness.
- Harvest-yield ground truth.
- Physiological diagnosis.
- Tree-level or orchard-level fruit totals.
- Event or anomaly ground truth.
- Real timestamps (they must be synthesized, D-010).

### IrriDrone — verified facts and limitations

Sources:

- [Zenodo record](https://doi.org/10.5281/zenodo.22017449)
- [README](https://zenodo.org/api/records/22017449/files/README.txt/content)
- [Dataset paper](https://doi.org/10.1016/j.dib.2026.113208)

Facts:

- Open access and CC BY 4.0.
- 674 paired one-rotation recordings.
- 674 annotated MP4 files and 674 matching unannotated MP4 files.
- 1,348 MP4 files total.
- Approximately 122 GB of archive data.
- H.264 MP4, 1920 × 1080, 50 FPS.
- Duration approximately 12.54–81.28 seconds.
- Crops: carrot, potato, and alfalfa.
- Active sprinklers: 3, 6, or 9.
- Mean discharge is recording-level and measured after recording.
- Nominal flight altitudes: 35 m, 45 m, and 55 m.
- One complete sprinkler rotation per released clip.

Limitations:

- White circular boundary embedded in the annotated video.
- No separate masks or polygons.
- No direct pressure values.
- No frame-synchronized flow values.
- No soil-moisture or crop-stress labels.
- No explicit anomaly classes.
- No official train/validation/test split.

IrriDrone supports narrow spray-boundary analysis, approximate coverage assessment, recording-level discharge regression, relative pressure prediction, and temporal video processing. It does not support general irrigation scheduling, plant stress prediction, frame-level discharge prediction, or general irrigation fault classification.

### Vineyard dataset — verified facts

Sources:

- [Zenodo record](https://doi.org/10.5281/zenodo.7330951)
- [Dataset paper](https://doi.org/10.1016/j.dib.2022.108848)

It provides 40 MP4 videos, 29 annotated videos, 681 annotated frames, temporally consistent grape-cluster masks, four vineyard rows, approximately 4K/59.94 FPS acquisition, one vineyard, one cultivar, and one campaign. It supports raw-video processing, cluster detection, segmentation, tracking, counting, and size measurement. It lacks direct harvest-yield labels, disease-severity labels, and broad geographic generalization.

### TexCot22 — verified facts

Sources:

- [NTrack paper](https://arxiv.org/abs/2312.10922)
- [NTrack project](https://robotic-vision-lab.github.io/ntrack/)
- [TexCot22 DOI](https://doi.org/10.18738/T8/5M9NCI)

It provides 30 tracking sequences, approximately 9,000 frames, approximately 150,000 labeled instances, persistent cotton-boll IDs, bounding boxes, and standard MOT organization. It supports detection, tracking, identity preservation, occlusion analysis, and counting. It has no masks or irrigation labels and is reported as CC BY-NC-SA 4.0.

---

## 4. Recommended project direction

# Real-Time Orchard Fruit Video Intelligence

### Real-world problem

Build a system that processes orchard video or temporally ordered orchard imagery to:

1. Detect visible apples.
2. Segment individual apples.
3. Maintain persistent identities.
4. Quantify visible-fruit counts.
5. Measure track continuity and occlusion behavior.
6. Produce temporal analytics.
7. Identify operational visual anomalies such as count instability, prolonged track loss, excessive identity switching, camera/scene degradation, and abnormal visibility changes.
8. Expose results through an API and dashboard.
9. Benchmark the complete pipeline for measured throughput and latency.

### Primary dataset

**AppleMOTS**.

### Why it is stronger than IrriDrone for this project

- Persistent object identities are available.
- Machine-readable instance masks are available.
- Tracking ground truth is available.
- Segmentation can be evaluated directly.
- MOTS research metrics and published baselines exist.
- The dataset is substantially smaller to manage.
- The license is CC BY 4.0.

### Scope boundary

The project will not claim irrigation scheduling, plant physiological stress detection, disease diagnosis, harvest-yield prediction, or general orchard health intelligence.

The project will claim:

> Real-time-capable orchard fruit perception, persistent tracking, temporal counting analytics, and operational anomaly ranking, evaluated with sequence-disjoint ground truth and measured systems performance.

"Real-time-capable" is claimed only if gate G5 passes: at least 25 FPS sustained end-to-end at 1296 × 972 on a named GPU (D-011). Otherwise the system is reported as "measured offline".

### Proposed system flow

```text
AppleMOTS frame sequence
or local/replayed video stream
        ↓
Manifest with duplicate-group check, platform tag, and synthesized timestamps
        ↓
Frame ingestion and timestamp normalization
        ↓
Instance perception
        ↓
Mask/box association
        ↓
Persistent track store
        ↓
Track-level temporal feature extraction
        ↓
Causal temporal state engine
        ↓
Operational event/anomaly logic
        ↓
Analytics and evidence generation
        ↓
API and dashboard
        ↓
Runtime benchmark and audit
```

### Model architecture

- Perception baseline: Mask R-CNN R50-FPN, COCO-pretrained, full resolution (D-005). YOLOX-S is optional, box-only, with derived boxes.
- Main perception: selected on validation from Mask R-CNN high-res/tiled, RTMDet-Ins, and Mask2Former, using pre-registered criteria: mask AP, small-object recall, and latency (D-006).
- Runtime candidate: lighter exported model selected only after measured benchmarking.
- Tracking baseline: ByteTrack with masks attached.
- Main tracking: OC-SORT or BoT-SORT without ReID, with camera-motion compensation and mask-IoU gating, selected on validation. Appearance ReID is an ablation only (D-007).
- Temporal baseline: deterministic track statistics, smoothing, and state machine.
- Optional temporal model: causal GRU for GT-derived track-continuation targets only, kept only if it passes the pre-registered kill criterion (D-009).
- Event/anomaly layer: operational state machine with three event classes (`gt_derived`, `synthetic`, `ranked_only`) plus normal-behavior deviation ranking (D-008).
- Best-results plan (D-021): pre-registered accuracy levers for small objects and ID reuse, all chosen on LOSO validation; the test set is evaluated at most 3 times. Results are reported as an online/real-time track and a separate offline best-accuracy track.
- Compute (D-020): no local CUDA GPU, so all training and runtime benchmarks run on Kaggle.

---

## 5. Five-phase architecture

### Phase 1 — Dataset, problem, and evaluation contract

Objective: Freeze dataset interpretation, labels, splits, metrics, and claims.

Deliverables: dataset card, problem statement, label dictionary, split manifest, evaluation protocol, claim boundary document, evidence checklist.

Dependencies: None.

Parallelizable work: source verification, license verification, split audit, metric review.

Sequential work: integrate findings, freeze problem, freeze ontology, freeze metrics, approve contract.

Quality gate G1: every claim has ground truth, no split leakage (including the 6/10, 7/11, 8/12 duplicate groups), a validation split from sequences 0-5 is defined, unsupported agronomic claims are removed, and user approval is obtained.

### Phase 2 — Data engineering and perception foundation

Objective: Build a verified path from dataset to model-ready samples.

Deliverables: immutable manifest, frame/annotation indexes, visualization report, golden fixture, model contracts, tiny forward-pass report.

Dependencies: Phase 1.

Parallelizable work: manifest audit, annotation audit, model-interface review.

Sequential work: manifest, annotation validation, frame adapter, visualization, smoke test, data gate.

Quality gate G2: images, masks, IDs, ignore regions, duplicate groups, and inputs are verified.

### Phase 3 — Perception and temporal association

Objective: Build and evaluate detection, segmentation, and tracking.

Deliverables: baseline/main checkpoints, predictions, tracking visualizations, detection/tracking metrics, oracle ladder, failure cases.

Dependencies: Phase 2.

Parallelizable work: tracker audit, metric audit, visualization audit after contracts are frozen.

Sequential work: perception smoke test, Kaggle training, evaluation, tracker integration, tracking evaluation, error analysis.

Quality gate G3: outputs are geometrically correct, the evaluator is validated (GT-as-prediction scores perfectly), mask HOTA/IDF1/sMOTSA are verified and compared with the published baseline, and detector and association errors are separated.

### Phase 4 — Temporal intelligence, API, dashboard, and runtime

Objective: Convert tracks into temporal analytics, operational anomalies, and a measured service.

Deliverables: feature schema, event/anomaly schema, API, dashboard, replay runner, runtime benchmark.

Dependencies: Phase 3.

Parallelizable work: API review, dashboard review, runtime review, error-analysis audit.

Sequential work: track features, analytics, rules, optional GRU, anomaly layer, API, dashboard, replay, benchmark.

Quality gates: G4 (after T44) - causal behavior is verified with no look-ahead and event classes are assigned. G5 (T50) - real-time status is based on measurements against the 25 FPS target.

### Phase 5 — Scientific experiments, robustness, evidence, and final audit

Objective: Establish scientific usefulness, reproducibility, cross-sequence/cross-platform robustness, and defensibility.

Deliverables: experiment registry, final metrics, ablations, cross-sequence/cross-platform robustness report, calibration report, error taxonomy, compute analysis, reproduction report, final report, final demo.

Dependencies: Phases 1–4.

Parallelizable work: metric audit, reproducibility audit, documentation audit, API/deployment audit, claim audit.

Sequential work: lock experiments, Kaggle runs, ablations, robustness, calibration, error analysis, evidence, final audit.

Quality gates: G6 (after T57) - scientific quality. G7 (T62) - all results are traceable and the project can be reproduced without unsupported claims.

---

## 6. Model, tracking, temporal, and event architecture

### Perception

- Mask R-CNN R50-FPN baseline (instance masks; lineage of the published TrackR-CNN baseline).
- Main model selected from Mask R-CNN high-res/tiled, RTMDet-Ins, and Mask2Former on validation, judged on small-object recall and latency.
- Optional YOLOX-S box-only detector, evaluated with derived boxes.
- Lightweight runtime candidate chosen from measured accuracy/latency results.
- License constraint: Apache-2.0/MIT components preferred; AGPL-3.0 (Ultralytics) excluded unless explicitly accepted.

### Tracking

- ByteTrack baseline.
- OC-SORT and BoT-SORT (no ReID) main candidates.
- Mask-IoU gating where masks are available.
- Camera-motion compensation (wearable and UAV motion).
- Appearance ReID as an ablation only: apples are homogeneous, and the paper shows learned appearance association underperforms.
- No cross-camera identity claim.

### Temporal intelligence

- Bounded per-track history.
- Timestamp-aligned features using synthesized timestamps (`pts_source = synthetic`).
- Causal state updates.
- Rule-based baseline.
- Optional causal GRU, only for GT-derived track-continuation and gap targets, with a pre-registered kill criterion.

### Event/anomaly intelligence

| Event | Class | How it is evaluated |
|---|---|---|
| Track lost / reappeared | `gt_derived` | Precision/recall/F1 and onset error against GT ID gaps |
| Prolonged occlusion (long GT gap) | `gt_derived` | Same as above |
| Camera/frame failure (drop, frozen, blur, brightness) | `synthetic` | Injected perturbations only |
| Scene-wide detection degradation | `synthetic` | Injected detector dropout and perturbation only |
| Count instability | `ranked_only` | Review-ranked examples; no accuracy claim |
| Abnormal track-density change | `ranked_only` | Review-ranked examples; no accuracy claim |

Anomaly output means operational review prioritization, not agronomic diagnosis.

---

## 7. Experiment and evaluation architecture

### Hypotheses

1. Temporal association improves count stability and unique-count accuracy.
2. Mask-aware association improves identity preservation (AssA, IDF1, IDS).
3. Causal temporal reasoning improves state consistency.
4. Detector confidence calibration improves precision at a fixed alert budget on `gt_derived` and `synthetic` events.
5. Runtime optimizations change the accuracy–latency tradeoff.

### Metrics

- Detection: AP@[0.50:0.95], AP50, AP75, precision, recall, and small-object recall (apples below 32 px).
- Segmentation: mask AP, IoU, Dice, boundary quality.
- Tracking (primary): mask-based HOTA with DetA, AssA, and LocA (TrackEval), and IDF1.
- Tracking (paper-comparable): sMOTSA, MOTSA, MOTSP, and IDS (KITTI MOTS definition) on sequences 10–12, with and without ignore regions.
- Tracking (secondary): fragmentation, track survival.
- Counting: per-frame visible-count MAE/RMSE; per-sequence unique-count absolute and relative error.
- Temporal events: precision, recall, F1, temporal IoU, onset error, delay; false alerts per 1,000 frames (`gt_derived` and `synthetic` only).
- Anomalies: PR-AUC and recall at alert budget on `synthetic` injections only; `ranked_only` events are reported as reviewed examples.
- Calibration (detector confidence): reliability, ECE, Brier, NLL, risk-coverage.
- Runtime: FPS, throughput, p50/p95/p99 latency, memory, GPU utilization, queue latency, dropped frames, alert delay; target ≥25 FPS at 1296 × 972.

### Split policy

- Sequence-disjoint.
- Duplicate-group aware: {6, 10}, {7, 11}, and {8, 12} are one group each. Only 10–12 are used for testing; 6–8 are never used for tuning.
- Validation comes from sequences 0–5 only, via leave-one-sequence-out (default) or a 1 wearable + 1 Anafi holdout.
- Official AppleMOTS train/test comparison is kept.
- No random adjacent-frame splitting.

### Statistics policy

- Per-sequence tables plus pooled metrics.
- At least 3 training seeds per main comparison; report mean ± standard deviation.
- Optional block bootstrap over contiguous 30-frame windows, with the autocorrelation caveat stated; never bootstrap over sequences (n = 3).
- The DJI Matrice test sequence is an unseen-platform slice (n = 1, descriptive only).

### Error slices

- Camera platform (wearable, Parrot Anafi, DJI Matrice).
- Object size, density, occlusion (proxied by GT ID gaps), motion, brightness.
- Confidence, track age, frame gaps, sequence identity.
- Inside vs. outside ignore regions.

---

## 8. Repository architecture

```text
project-3/
├── README.md
├── LICENSE
├── CITATION.cff
├── pyproject.toml
├── configs/
├── data/
│   ├── raw/
│   ├── manifests/
│   ├── splits/
│   ├── derived/
│   └── golden/
├── src/agri_video_intelligence/
│   ├── schemas/
│   ├── io/
│   ├── data/
│   ├── perception/
│   ├── tracking/
│   ├── temporal/
│   ├── events/
│   ├── evaluation/
│   ├── experiments/
│   ├── runtime/
│   ├── api/
│   └── visualization/
├── scripts/
├── tests/
├── notebooks/
├── docs/
├── deployment/
└── artifacts/
```

Raw data, checkpoints, and generated artifacts should not be committed directly to Git.

---

## 9. Local versus Kaggle strategy

Local work includes inspection, validation, visualization, tests, initialization, forward passes, tiny smoke tests, inference, debugging, API, dashboard, and runtime integration.

Kaggle work includes baseline/main training, experiments, ablations, hyperparameters, final model selection, full evaluation, export experiments, and performance benchmarking.

Every Kaggle run records GPU, VRAM, CPU/RAM, runtime versions, dataset hash, split hash, seed, duration, peak memory, checkpoint, and artifacts.

Kaggle sessions are time-limited and GPU time is quota-limited per week, so every training run must be resumable from a checkpoint and fit a planned GPU-hour budget (D-018, [PROJECT_TIMELINE.md](PROJECT_TIMELINE.md)). Current quota values are verified in T03.

A golden fixture must run locally and on Kaggle with documented tolerances.

---

## 10. Testing strategy

- Unit: geometry, masks, timestamps, transitions, metrics, configuration.
- Data: manifest existence, dimensions, IDs, duplicates, duplicate-group hashing (6/10, 7/11, 8/12), splits, checksums.
- Model: initialization, forward pass, tiny overfit, shapes, coordinates, NaNs, export.
- Tracking: crossing, occlusion, reappearance, detector dropout, gaps, motion, ID reuse between identical objects.
- Evaluation: GT-as-prediction scores perfectly; hand-computed sMOTSA/HOTA toy cases; ignore-region exclusion.
- Temporal: order, no look-ahead, irregular timestamps, missing frames, bounded memory.
- Events: onset/end, hysteresis, cooldown, deduplication, evidence, synthetic anomalies.
- API: schemas, invalid IDs, missing evidence, stale stream, idempotency.
- End-to-end: frame → perception → track → state → event → API → dashboard.
- Performance: single/multiple streams, object density, resolution, temporal history, precision, drops, memory.

---

## 11. Quality gates

Unified gate scheme (D-016), used in every project document.

### G0 — Discovery approval

The primary direction, AppleMOTS selection, scope, claims, metrics, and methodology are approved.

### G1 — Project contract (end of Phase 1, T09)

Problem, labels, duplicate-aware splits, validation strategy, metrics, and claims are frozen and approved.

### G2 — Data quality (end of Phase 2, T21)

Manifest, checksums, duplicate groups, split leakage, labels, ignore regions, visualization, and golden fixture pass.

### G3 — Perception/tracking correctness (end of Phase 3, T35)

Outputs align, IDs are valid, the evaluator is validated (GT-as-prediction scores perfectly), metrics are compared with the published baseline, and failure cases are documented.

### G4 — Temporal correctness (Phase 4, after T44)

Causal mode contains no look-ahead, event schemas and event classes are frozen, and evidence is traceable.

### G5 — Runtime qualification (end of Phase 4, T50)

Throughput, p50/p95/p99 latency, memory, overhead, queues, drops, and alert delay are measured against the ≥25 FPS target.

### G6 — Scientific quality (Phase 5, after T57)

Baselines, main comparison, ablations, error analysis, calibration, robustness, and compute analysis are complete.

### G7 — Final audit (end of Phase 5, T62)

Reproduction succeeds, interfaces work, evidence is complete, licenses are correct, and unsupported claims are removed.

---

## 12. Final definition of the finished project

The finished system will ingest temporally ordered agricultural imagery or replay/live input, detect and segment apples, maintain persistent tracks, calculate per-frame visible counts, per-sequence unique counts, and temporal statistics, identify operational anomalies, expose results through an API and dashboard, run the same code locally and on Kaggle, provide baselines and controlled experiments, report scientific and systems metrics, document failures, and provide reproducible artifacts.

Final project claim:

> A measured, reproducible agricultural video-intelligence pipeline for orchard fruit perception, persistent tracking, temporal counting analytics, and operational anomaly ranking.

The project will not claim to be an irrigation-decision or plant-physiology system because the selected public ground truth cannot support those conclusions.
