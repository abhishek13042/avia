# Project 3 — Architecture and Phase Audit

## Audit identity

- Audit date: 2026-10-21
- Scope: `PROJECT_DISCOVERY_AND_ARCHITECTURE.md`, `EXECUTION_ORDER.md`, `DOCUMENTATION_PROCESS.md`, `README.md`, all `phases/*` files (PHASE, TASKS, SPEC-01 to SPEC-12, T01/T02 records, status files).
- Method: Full read of all project Markdown, then re-verification against primary sources (APPLE MOTS paper full text, Zenodo record, official WUR repository README) and secondary sources.
- Status: **Proposed changes — not yet applied.** Per Documentation Rule 9, the existing decisions are preserved until the user approves each change.

Labels used: `Verified fact`, `Measured result`, `Assumption`, `Unknown`, `Decision`, `Limitation`.

---

## 1. Verified facts from the APPLE MOTS paper (re-read 2026-10-21)

Source: de Jong, Baja, Tamminga, Valente, "APPLE MOTS: Detection, Segmentation and Tracking of Homogeneous Objects Using MOTS", IEEE RA-L 7(4), 2022, [doi:10.1109/LRA.2022.3199026](https://doi.org/10.1109/LRA.2022.3199026), open copy [edepot.wur.nl/577473](https://edepot.wur.nl/577473).

| # | Verified fact | Where in paper |
|---|---|---|
| F1 | Masks are spread over **1,673 frames** with **2,304 unique apple instances** ("almost 86,000" masks). | §III-B |
| F2 | Resolution **1296 × 972**. Apples are **~30–50 px wide**. | §III-B, §III-D, §IV-D |
| F3 | **9 datasets** were annotated: **6 train / 3 test** (≈70/30). | §III-B |
| F4 | Train = **2 wearable-sensor + 4 Parrot Anafi** sequences. Test = **1 DJI Matrice 210 + 1 Parrot Anafi + 1 wearable**. | §III-B |
| F5 | Videos were captured at **25–30 FPS** from 2–3 m height, on 4 days over 1.5 months, with 3 cultivars (Elstar, Jonagold, Junami). | §III-A |
| F6 | Ignore regions are **gray overlays painted on the test images** over unlabelled background apples (KITTI-style). | §III-B, Fig. 3, §IV-D |
| F7 | Annotation used CVAT with interpolation/tracking (MinneApple protocol: fully + partially visible fruit, background trees and ground fruit ignored). | §III-B |
| F8 | Metrics reported: **sMOTSA, MOTSA, MOTSP, ID switches, FPS** only. **No HOTA, IDF1, AP or count metrics.** | §III-E, Table I |
| F9 | Best tracking result (**PointTrack trained from scratch, evaluated with ignore regions**): **sMOTSA 38.7, MOTSA 52.9, MOTSP 80.0, 7.81 FPS**. | Table I |
| F10 | **MOTSP 80.4** belongs to **TrackR-CNN**, not to the PointTrack row. TrackR-CNN with ignore regions: sMOTSA 35.7, MOTSA 47.8, MOTSP 80.4, 0.20 FPS. | Table I |
| F11 | The learned appearance association head **lost** to plain box-based association. Kalman-filter (sMOTSA −9.7) and optical-flow mask-warping (−13.2) variants failed. | §IV-D, Table I |
| F12 | Main failure mode: **ID reuse / ID switches between visually identical apples**, with one ID assigned to up to 9 apples. | §IV-D, Fig. 8 |
| F13 | Speed was measured on a Titan RTX-class workstation (repo README). | Repo README |
| F14 | Stated limitation: only one side of the tree is viewed, so double counting is still possible. No tree-level yield ground truth. | §IV-D |

Repository facts ([git.wur.nl/said-lab/rt-obj-tracking](https://git.wur.nl/said-lab/rt-obj-tracking), README, MIT license):

- Layout `train/images/<seq>/<frame>.png` and `train/instances/<seq>/<frame>.png` (KITTI MOTS PNG format, CVAT export).
- Tuning uses `train.seqmap` / `val.seqmap` via KITTI `mots_tools`.

Zenodo ([10.5281/zenodo.5939726](https://doi.org/10.5281/zenodo.5939726)): v1, published 2022-02-25. Folders: sequences 0–5 train, 6–8 "testing/validation", 10–12 "testing with ignore regions". **Sequence 9 is not mentioned.**

Third-party mirror statistics ([Dataset Ninja](https://datasetninja.com/apple-mots)): 2,198 images (1,147 train + 1,051 test), 105,559 objects, mean object height 28 px.

---

## 2. Critical findings (must change before T03–T08 are frozen)

### C1 — Sequences 10–12 are very likely duplicates of 6–8, so the planned split leaks

- Evidence:
  - The paper says there are **9** sequences (F3), but Zenodo lists 12 folders (0–8, 10–12).
  - The ignore-region versions are overlays on the test images (F6).
  - Arithmetic check: 1,147 train + 526 test ≈ **1,673** unique frames (F1). The mirror has 1,147 + 1,051 = 2,198, and 1,051 ≈ 2 × 526. This means the test frames appear twice.
- Status: `Assumption` (strong). It must be verified with image hashes and frame counts after download.
- Impact: The current text "6–8 testing/validation, 10–12 testing" invites using 6–8 for model selection and 10–12 for the final test. **That would be test-set leakage** (same frames, same apples, gray patches only).
- Change: In T03/T06, treat {6, 10}, {7, 11} and {8, 12} as the **same group key**. Use 10–12 (with ignore regions) as the only official test set. Never tune on 6–8.

### C2 — There is no validation set, so one must be carved from the 6 training sequences

- Evidence: F3 and F4. The official split is train/test only.
- Change: T06 must define a **sequence-disjoint validation split taken from sequences 0–5**. Two options:
  - (a) Hold out 1 wearable + 1 Anafi sequence.
  - (b) Use leave-one-sequence-out cross-validation for model and threshold selection, then retrain on all of 0–5.
- Record this as a `Decision` with its limitation: with only 6 groups, validation variance is high.

### C3 — The published-baseline numbers are recorded wrongly

- Current text (architecture doc §3): "Published results report MOTSP 80.4, sMOTSA 38.7, and MOTSA 52.9."
- Correction: sMOTSA 38.7 / MOTSA 52.9 / MOTSP 80.0 come from PointTrack (scratch, with ignore regions). MOTSP 80.4 comes from TrackR-CNN (F9, F10). The abstract mixes the two models.
- Change: Replace the line with the full Table I rows and state which row is the reference.

### C4 — The metric plan cannot be compared with the published baseline

- Evidence: The paper reports only sMOTSA / MOTSA / MOTSP / IDS (F8). The project's primary metrics are HOTA / IDF1 / MOTA (box-style).
- Change (SPEC-08, T07, T32):
  - Report **sMOTSA, MOTSA, MOTSP, IDS** using the KITTI MOTS definition on sequences 10–12 with ignore regions, for direct comparison.
  - Add **mask-based HOTA (DetA/AssA/LocA) and IDF1** via TrackEval ([Luiten et al., IJCV 2021](https://doi.org/10.1007/s11263-020-01375-2)) as the primary modern metrics.
  - Before trusting any of these numbers, reproduce at least one reference row (or a sanity check on GT-as-prediction = perfect scores).

### C5 — The box-only baseline (YOLOX-S) cannot produce MOTS results

- Evidence: YOLOX outputs boxes only. All published metrics and the project's main claim are mask-based. The T29 ByteTrack baseline on YOLOX boxes yields no masks, so sMOTSA and mask-HOTA cannot be computed for the baseline.
- Change (SPEC-04, T22):
  - Make the baseline an **instance-segmentation** model. **Mask R-CNN R50-FPN** is the most defensible choice: TrackR-CNN, the paper's baseline, is built on Mask R-CNN.
  - Keep YOLOX-S only as an optional box-only detector, evaluated with box metrics against derived GT boxes and labelled as such.

### C6 — Mask2Former as the main model is risky for this data

- Evidence:
  - Objects are tiny: ~30–50 px wide, mean height 28 px, ~48 apples/frame, at 1296×972 (F2).
  - The Mask2Former authors list small objects as a known weakness ([Cheng et al., CVPR 2022](https://arxiv.org/abs/2112.01527), limitations section).
  - Query-based models also have a fixed query budget and are heavy to train on a Kaggle T4/P100 at full resolution.
- Change (SPEC-04, T26–T28):
  - Choose the main model by a **small pre-registered comparison** on the validation split: Mask R-CNN (baseline) vs. a real-time instance segmenter (e.g. RTMDet-Ins, Apache-2.0, [Lyu et al. 2022](https://arxiv.org/abs/2212.07784)) vs. Mask2Former.
  - Require full-resolution (or tiled) input and check recall for the smallest apples.
  - Avoid AGPL-licensed Ultralytics YOLO-seg unless the license is accepted explicitly.

### C7 — Appearance ReID is contraindicated for homogeneous apples

- Evidence: F11 (the learned appearance association underperformed) and F12 (ID reuse between identical apples).
- Change (SPEC-05, T30):
  - Configure BoT-SORT **without ReID by default**: motion + camera-motion compensation + mask-IoU association.
  - Make ReID an ablation, not a main component.
  - Add **OC-SORT** ([Cao et al., CVPR 2023](https://arxiv.org/abs/2203.14360)) as a tracker candidate, because it is designed for occlusion and non-linear motion (wearable and UAV camera motion).
  - Keep ByteTrack ([Zhang et al., ECCV 2022](https://arxiv.org/abs/2110.06864)) as the baseline.
- Related evidence: an apple-counting study comparing SORT, DeepSORT and ByteTrack found ByteTrack best (HOTA 0.689) ([Gené-Mola et al., MetroAgriFor 2023](https://repositori.udl.cat/items/c64ee46c-a482-4d77-b642-7e7c595e38fc/full)).

### C8 — Event, anomaly and alert metrics assume data that does not exist

- Evidence: The whole test set is ~526 frames, about **18–21 s of video** at 25–30 FPS (F1, F5; `Assumption` until frame spacing is verified). There are no event or anomaly labels.
- Impact:
  - "False alerts per camera-hour" cannot be measured.
  - PR-AUC on real anomalies is impossible.
  - Hypothesis 4 ("calibration improves alert quality") cannot be tested on real alerts.
  - `calibrated_probability` in `EventRecord` has nothing to calibrate against.
- Change (SPEC-07, T42–T44, T54, architecture §7):
  - Split events into three classes:
    1. **GT-derivable events.** Track lost / reappeared / long gap can be derived from GT ID gaps, so they are evaluable with precision/recall/onset error. Label them `derived`.
    2. **Synthetic-injection events.** Frame drop, blur, brightness shift, frozen frame, detector dropout are evaluated only on injected perturbations. Report them as synthetic.
    3. **Unlabelled ranking.** Count instability and density change are reported only as review-ranked examples, with no accuracy claim.
  - Make `calibrated_probability` nullable.
  - Restrict calibration (ECE/Brier/NLL) to **detector confidence**, which has labels.

### C9 — The causal GRU is very unlikely to be justified

- Evidence: Training has ~1,147 frames, 6 sequences, and a few thousand GT tracks (F1, F3). The planned targets (occlusion, visibility) have **no labels**; at best they can be proxied from GT ID gaps.
- Change (T40–T41):
  - Keep the GRU optional with a **pre-registered kill criterion**: it must beat the deterministic baseline on validation by a stated margin, or it is dropped and documented as a negative result.
  - Allowed targets: GT-derived track continuation / gap prediction only.

---

## 3. Major findings

### M1 — Timestamps are not in the dataset

- Evidence: Frames are numbered PNGs only (repo README). The capture rate is 25–30 FPS, varying by platform (F5). Whether annotated frames are consecutive or subsampled is `Unknown`.
- Change (SPEC-02, T03, T17): `capture_pts` must be **synthesized** from a nominal FPS per platform, labelled `Assumption`, and kept configurable. T03 must check frame spacing, e.g. by looking at motion between consecutive frames.

### M2 — The real-time target is undefined

- Change (SPEC-11, T49–T50):
  - Freeze the target: **sustain ≥25 FPS (worst case 30 FPS) at 1296×972 on a named GPU** (Kaggle T4 and/or the local GPU).
  - Record the reference: PointTrack at 7.81 FPS on a Titan RTX-class GPU (F9, F13).
  - Report end-to-end throughput separately from model-only throughput.
  - The local hardware is currently `Unknown` and must be recorded.

### M3 — "Counting" is ambiguous

- Change (T05, T07, T38):
  - Define two counts:
    - (a) **Per-frame visible count**, with MAE/RMSE against GT masks per frame.
    - (b) **Per-sequence unique-fruit count**, i.e. distinct track IDs vs. distinct GT IDs. This is the double-counting metric that matters for the paper's motivation.
  - State the paper's limitation F14: one-sided view, so there is no tree-level or yield claim.

### M4 — Statistics with 3 test sequences

- Evidence: 3 test sequences, one per platform (F4).
- Change (SPEC-08, T55):
  - Do not bootstrap over sequences (n = 3).
  - Report **per-sequence tables** plus pooled metrics, ≥3 training seeds for main comparisons, and, if needed, a block bootstrap over contiguous frame windows (state the correlation caveat).
  - Treat the DJI Matrice test sequence as an **unseen-platform slice**: no Matrice data is in train (F4). It is descriptive only, with n = 1.

### M5 — Ignore-region handling is underspecified

- Evidence: The overlays are pixels painted into the test images (F6). It is `Unknown` whether the instance PNGs also encode an ignore class (KITTI MOTS convention: class 10 / id 10000).
- Change (SPEC-03, T03, T13):
  - Verify the encoding after download.
  - The evaluator must exclude predictions inside ignore regions exactly as KITTI `mots_tools` does.
  - Report results both with and without ignore regions, as the paper does.
  - Note that the gray patches create a **train/test appearance shift**: they never appear in training images.

### M6 — Dataset size and facts are inconsistent across documents

| Document claim | Verified value |
|---|---|
| "1,700 annotated frames" | 1,673 unique frames (paper); 2,198 files incl. duplicated test frames (mirror) |
| "~86,000 instances" | "almost 86,000" masks; 2,304 unique apples; mirror counts 105,559 objects (consistent with test duplication) |
| AppleMOTS source in T01 = WUR Google Drive | Drive link 404 (T02); Zenodo is the source of record |
| "Dataset DOI/version not found" (T01) | Zenodo DOI 10.5281/zenodo.5939726, version **v1** (T02 + Zenodo page) |

- Change: Update the architecture doc §3 and append a correction note to T01 (do not overwrite it).

### M7 — Gate numbering is inconsistent

- Architecture doc: G1 = data contract, G2 = perception/tracking, G3 = temporal, G4 = runtime, G5 = science, G6 = final.
- `EXECUTION_ORDER.md`: G1 = data contract (Phase 1), **G2 = data quality** (Phase 2), **G3 = perception/tracking** (Phase 3), G4 = runtime, and the temporal gate is missing.
- Change: Use one gate table everywhere. Proposal: G0 discovery, G1 contract, G2 data quality, G3 perception/tracking, G4 temporal correctness, G5 runtime, G6 science, G7 final audit. Alternatively keep 7 gates and merge some, but make the definitions identical in all files.

### M8 — Status is inconsistent across files

- `EXECUTION_STATUS.md`: T01/T02 Verified, T03 In Progress, G0 "Waiting for user approval".
- `phases/phase-01-discovery-contract/TASKS.md`: T01/T02 "Pending".
- `README.md` / `EXECUTION_ORDER.md`: "No implementation has been started; wait for approval before T01".
- Change:
  - Record G0 approval explicitly, or record that T01/T02 were executed before G0 as a process deviation.
  - Sync all status tables.
  - Create the missing `TASK-T03-*.md` record.

### M9 — Compute budget is unplanned

- Change (SPEC-09, Phase 3 / Phase 5):
  - Add a GPU-hour budget per experiment. Kaggle imposes session time limits and a weekly GPU quota; check the current limits and record them as `Verified fact` at T03.
  - Require checkpoint/resume across sessions (already in SPEC-09).
  - Reduce the experiment matrix to fit the budget.

---

## 4. Minor findings

| # | Finding | Change |
|---|---|---|
| m1 | `DOCUMENTATION_PROCESS.md` has a stray closing ``` after the "Task completion template" path, which breaks rendering. | Fix the fence. |
| m2 | SPEC-08 (in Phase 1) depends on SPEC-01–07, which are written later. | Split it: a Phase 1 metric definition (frozen in T07) and a Phase 5 evaluation implementation. |
| m3 | SPEC-07 depends on SPEC-11 (runtime), but events do not need the runtime spec. | Remove or justify the dependency. |
| m4 | T17 (frame adapter / replay) and T48 (replay runner) overlap. | T48 = extend the T17 adapter with wall-clock pacing and drop injection; reference T17. |
| m5 | `TrackState` has no mask field; mask-IoU association and MOTS output need one. | Add an RLE `mask` to `TrackState` / `TrackFrame`. |
| m6 | `SampleRecord` lacks `platform` (wearable / Anafi / Matrice), `has_ignore_overlay`, `duplicate_group`. | Add these fields. They are needed for C1, M4 and M5. |
| m7 | The paper PDF is under Dutch "Taverne" terms (personal use). | Cite it; do not redistribute the PDF in the repo or evidence package. |
| m8 | Component licenses are not tracked (Mask2Former: MIT; MMDetection/RTMDet, YOLOX: Apache-2.0; Ultralytics: AGPL-3.0; TrackEval: MIT; WUR code: MIT). | Add a third-party license table to T02 or the final audit. |
| m9 | "Generalization" in Phase 5 overstates what one orchard can support (one site, 3 cultivars, 4 days). | Rename to "cross-sequence / cross-platform robustness"; no cross-orchard claim. |

---

## 5. Proposed revised core architecture (summary)

```text
APPLE MOTS (Zenodo v1) — 9 unique sequences, test = 10–12 with ignore regions
        ↓
Manifest with duplicate-group check (6↔10, 7↔11, 8↔12), platform tag, synthetic PTS
        ↓
Instance segmentation
  baseline: Mask R-CNN R50-FPN
  main: selected on validation from {RTMDet-Ins, Mask2Former, Mask R-CNN-hi-res}
        ↓
Tracking
  baseline: ByteTrack (box) + mask attach
  main: OC-SORT / BoT-SORT-noReID + CMC + mask-IoU gating; ReID only as ablation
        ↓
Evaluation
  KITTI-MOTS sMOTSA/MOTSA/MOTSP/IDS (comparable to paper)
  + mask HOTA/IDF1 (TrackEval) + per-frame and unique counts
        ↓
Temporal analytics (deterministic) → events: GT-derived | synthetic | ranked-only
        ↓
API / dashboard / replay → runtime benchmark vs. ≥25 FPS at 1296×972 on named GPU
```

## 6. Files that change, if approved

| File | Changes |
|---|---|
| `PROJECT_DISCOVERY_AND_ARCHITECTURE.md` | C3, C5–C9, M2–M4, M6, m9, revised flow (§5) |
| `EXECUTION_ORDER.md` | M7 gates, T22/T26/T29–T31/T40–T43 wording, m4 |
| `phases/EXECUTION_STATUS.md`, `phase-01/TASKS.md`, `README.md` | M8 |
| `DOCUMENTATION_PROCESS.md` | m1 |
| SPEC-01 | C1, C2, m6 |
| SPEC-02 | M1 |
| SPEC-03 | M5 |
| SPEC-04 | C5, C6 |
| SPEC-05 | C7, m5 |
| SPEC-07 | C8, m3 |
| SPEC-08 | C4, M3, M4, m2 |
| SPEC-09 | M9 |
| SPEC-11 | M2 |
| T01 record | Append a correction note (M6) |
| New: `TASK-T03-*.md` | Record F1–F14 and the unknowns below |

## 7. Unknowns to resolve in T03 (after download)

1. Do 10–12 contain the same frames as 6–8? (hash comparison)
2. Is the ignore region encoded in the instance PNGs (class/id), or only painted on images?
3. Which sequence comes from which platform? Is the sequence 9 folder present?
4. Are annotated frames consecutive at the native frame rate, or subsampled?
5. Exact frame and instance counts per sequence.
6. Which GPU is available locally? What are the current Kaggle GPU types and quota?

## Sources

- [APPLE MOTS paper (RA-L 2022)](https://doi.org/10.1109/LRA.2022.3199026), [open copy](https://edepot.wur.nl/577473)
- [APPLE MOTS Zenodo record](https://zenodo.org/records/5939726)
- [WUR rt-obj-tracking repository](https://git.wur.nl/said-lab/rt-obj-tracking)
- [Dataset Ninja APPLE MOTS statistics](https://datasetninja.com/apple-mots) (secondary)
- [HOTA — Luiten et al., IJCV 2021](https://doi.org/10.1007/s11263-020-01375-2)
- [MOTS — Voigtlaender et al., CVPR 2019](https://arxiv.org/abs/1902.03604)
- [Mask2Former — Cheng et al., CVPR 2022](https://arxiv.org/abs/2112.01527)
- [RTMDet — Lyu et al., 2022](https://arxiv.org/abs/2212.07784)
- [ByteTrack — Zhang et al., ECCV 2022](https://arxiv.org/abs/2110.06864)
- [OC-SORT — Cao et al., CVPR 2023](https://arxiv.org/abs/2203.14360)
- [BoT-SORT — Aharon et al., 2022](https://arxiv.org/abs/2206.14651)
- [Video-based apple counting with SORT/DeepSORT/ByteTrack — Gené-Mola et al., 2023](https://repositori.udl.cat/items/c64ee46c-a482-4d77-b642-7e7c595e38fc/full)
