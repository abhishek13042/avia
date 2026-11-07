# TASK-T03 — Record Verified Facts, Assumptions, and Unknowns

## Task identity

- Task ID: T03
- Task name: Record verified facts, assumptions, and unknowns
- Phase: Phase 1 — Dataset, problem, and evaluation contract
- SPEC: SPEC-01, SPEC-08
- Status: In Progress
- Start date: 2026-10-21
- End date:

## Objective

Separate verified AppleMOTS facts from assumptions and unknowns, and resolve the unknowns that block the split, metric, and compute decisions.

## Scope

### Included

- Facts verified against the paper full text, Zenodo, and the WUR repository.
- Assumptions with their evidence and the test that will confirm or reject them.
- Unknowns with a resolution method.

### Non-goals

- Implementing the manifest (T11–T13).
- Using any assumption as ground truth.

## Dependencies

- T01, T02 (Verified).
- Audit: `../../../ARCHITECTURE_AUDIT_2026-10-21.md`.

## Verified facts

| ID | Fact | Source |
|---|---|---|
| F1 | 1,673 annotated frames, 2,304 unique apples, almost 86k masks | Paper |
| F2 | Resolution 1296 × 972; apples are roughly 30–50 px wide | Paper |
| F3 | 9 sequences: 6 train (2 wearable + 4 Parrot Anafi), 3 test (DJI Matrice + Anafi + wearable) | Paper |
| F4 | Video captured at 25–30 FPS; no timestamps are released | Paper, Zenodo |
| F5 | Ignore regions are gray overlays painted on test images | Paper |
| F6 | Paper reports only sMOTSA, MOTSA, MOTSP, IDS | Paper Table I |
| F7 | PointTrack (scratch, ignore): 38.7 / 52.9 / 80.0 at 7.81 FPS | Paper Table I |
| F8 | TrackR-CNN (ignore): 35.7 / 47.8 / 80.4 at 0.20 FPS | Paper Table I |
| F9 | Learned appearance association underperformed box association; Kalman and optical-flow variants failed | Paper |
| F10 | Main tracking failure mode: ID reuse between identical apples | Paper |
| F11 | Zenodo v1, CC BY 4.0, 5,661,248,829 bytes, MD5 `1f9b8cd79f05469d656a01015889b55d` | Zenodo |
| F12 | Zenodo folders: 0–5 train, 6–8 test/val, 10–12 test with ignore regions; no sequence 9 | Zenodo |
| F13 | KITTI MOTS PNG layout `images/<seq>/<frame>.png`, `instances/<seq>/<frame>.png`; repository MIT | WUR repository |
| F14 | A secondary mirror lists 2,198 images (1,147 train + 1,051 test), 105,559 objects | Dataset Ninja |

## Assumptions

| ID | Assumption | Evidence | How it is tested |
|---|---|---|---|
| A1 | Sequences 10–12 are ignore-region copies of 6–8 | 1,147 + ≈526 ≈ 1,673 unique; 1,051 ≈ 2 × 526 | U1 |

## Unknowns to resolve

| ID | Unknown | Resolution method | Status |
|---|---|---|---|
| U1 | Are 10–12 duplicates of 6–8? | Compare frame counts and perceptual/pixel hashes outside ignore regions | Resolved 2026-10-31: yes. Same frame names, identical mid-frame instance PNGs, identical mask totals; frames without a patch match exactly. Sequence 10 lacks image 000096 (its label exists) |
| U2 | Ignore-region encoding in instance PNGs | Inspect unique values in instance PNGs of 10–12 vs. 6–8 | Resolved 2026-10-31: none. Value 10000 never occurs; ids are 1000+ (class 1). Patches are translucent and exist only in the images, so masks are derived by diffing against 6–8 (D-025) |
| U3 | Platform per sequence ID; why there is no sequence 9 | Image resolution/EXIF/visual inspection; repository docs | Open (not blocking): all sequences are 1296x972, so resolution does not separate platforms |
| U4 | Are annotated frames consecutive or subsampled? | Inter-frame motion check and frame-name gaps | Resolved for names 2026-10-31: every gap is 1. Motion check not run |
| U5 | Per-sequence frame and instance counts | Count after download | Resolved 2026-10-31: train 0–5 = 71, 169, 119, 151, 486, 151 (1,147); 6–8 = 101, 103, 322 (526). See `artifacts/t03/t03_report.json` |
| U6 | Local GPU and current Kaggle weekly GPU quota | `nvidia-smi`; Kaggle account settings | Partly resolved: local = i3-1115G4, 7.6 GB RAM, Intel UHD only (no CUDA), Python 3.14, CPU PyTorch, 103 GB free on D: (D-020). Kaggle quota: still unknown; a GPU kernel was accepted on 2026-10-31 |

U1, U2, U4 and U5 were answered by kernel v4 on 2026-10-31. U3 and the Kaggle part of U6 remain.

## Implementation result

- Download verified by size and MD5, uploaded as private Kaggle dataset `abhishekg14/apple-mots`, and audited on all sequences. A1 confirmed.

## Tests executed

| Test | Command or procedure | Result |
|---|---|---|
| Paper fact check | Full-text extraction of the paper (pdftotext) | Passed (F1–F10) |
| Zenodo metadata check | Zenodo record API | Passed (F11–F12) |
| Local hardware check | `nvidia-smi`, `Win32_VideoController`, `torch.cuda.is_available()` | No CUDA GPU (U6 local part) |
| Zip listing without download | Zenodo zip preview | Failed: archive too large to preview; U1–U5 need the download |
| Kaggle data-audit kernel `avia-t03-data-audit` v1 (2026-10-29) | Kernel downloads APPLE_MOTS.zip from Zenodo with curl | Failed: Zenodo returned HTTP 403 (763-byte response) on all 5 attempts from Kaggle; no data reached the checks. No Kaggle mirror of APPLE MOTS exists. Next step: the user downloads the zip in a browser, then it is uploaded as a private Kaggle dataset and the kernel reads it from there |
| Kaggle data-audit kernel v4 (2026-10-31) | Reads the private dataset; counts, duplicate check, overlay comparison | Passed. The earlier `gray_overlay_mask` rule scored IoU about 0.1 on 10 and about 0 on 11 and 12 against the true patches, so it was replaced (D-025) |

## Verification

- Expected behavior: every fact has a source; every assumption has a test.
- Observed behavior: F1–F14 sourced; A1 confirmed by U1.
- Verification result: Partial (U3 and the Kaggle part of U6 open; neither blocks training).

## Evidence

- `../../../ARCHITECTURE_AUDIT_2026-10-21.md`
- `../../../DECISION_LOG.md` (D-001, D-014, D-015, D-025)
- `../../../artifacts/t03/t03_report.json`, `../../../artifacts/t03/evidence/`

## Quality gate

- Gate: T03 facts gate
- Pass/fail: Pending
- Reason: U3 and part of U6 are unresolved.

## Problems and follow-up

- Sequence 10 has no image for frame 96, so that frame is skipped and the tracker sees a one-frame gap.

## Approval to continue

- Approved by:
- Date:
