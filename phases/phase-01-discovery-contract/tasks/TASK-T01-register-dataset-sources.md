# TASK-T01 — Register Primary and Alternative Dataset Sources

## Task identity

- Task ID: T01
- Task name: Register primary and alternative dataset sources
- Phase: Phase 1 — Dataset, problem, and evaluation contract
- SPEC: SPEC-01 — Dataset provenance and split contract
- Status: Verified
- Execution date: 2026-10-08

## Objective

Create the canonical source registry for the selected primary dataset and the principal alternatives.

## Scope

### Included

- AppleMOTS.
- IrriDrone.
- UAV vineyard grape-bunch dataset.
- TexCot22/NTrack.
- Dataset records.
- Dataset-introducing papers.
- Official project or repository links.
- DOI and version information.
- Primary/secondary source classification.

### Non-goals

- Downloading large archives.
- Installing dependencies.
- Training models.
- Selecting final model architecture.
- Implementing dataset adapters.

## Dependencies

None. This is the first project task.

## Inputs

- Discovery research report.
- Official Zenodo records.
- Dataset papers.
- Official project repositories.

## Implementation result

The following source registry was verified and recorded.

| Dataset | Canonical dataset source | Primary paper | Official project/repository | DOI/version status |
|---|---|---|---|---|
| AppleMOTS | [WUR official download](https://drive.google.com/file/d/1WbNRwyAhLY4afib7oT1VceeK1fNwup7p/view?usp=sharing) | [APPLE MOTS](https://doi.org/10.1109/LRA.2022.3199026) | [WUR RT-Obj-Tracking](https://git.wur.nl/said-lab/rt-obj-tracking) | Dataset DOI/version not found; paper DOI verified |
| IrriDrone | [Zenodo v1.0](https://doi.org/10.5281/zenodo.22017449) | [IrriDrone Data in Brief](https://doi.org/10.1016/j.dib.2026.113208) | [UOK data endpoint](https://cloud.uok.ac.ir/s/7G4qbEsQJFk6zwQ) | Dataset DOI and v1.0 verified |
| UAV vineyard grape-bunch dataset | [Zenodo v2.0](https://doi.org/10.5281/zenodo.7330951) | [Vineyard dataset paper](https://doi.org/10.1016/j.dib.2022.108848) | [Zenodo record](https://zenodo.org/records/7330951) | Dataset DOI and v2.0 verified |
| TexCot22/NTrack | [Texas Data Repository v2](https://doi.org/10.18738/T8/5M9NCI) | [NTrack journal paper](https://doi.org/10.1109/TASE.2023.3342791) | [NTrack project](https://robotic-vision-lab.github.io/ntrack), [source code](https://github.com/robotic-vision-lab/NTrack-A-Multiple-Object-Tracker) | Current V2 DOI verified; historical V1 also recorded |

## Verified facts

- AppleMOTS official access is linked from the WUR project and the dataset-introducing paper is verified.
- IrriDrone Zenodo record is version 1.0 and has a versioned DOI.
- The vineyard Zenodo record is version 2.0 and has a versioned DOI.
- TexCot22 has a current V2 record and a historical V1 release.
- Dataset deposits and dataset-introducing papers are treated as primary sources.
- Derivative implementations are treated as secondary sources.

## Unknowns

- AppleMOTS has no authoritative dataset version or dataset DOI identified in this audit.
- IrriDrone has no separate source-code repository identified.
- The phrase “UAV vineyard grape-bunch dataset” may refer to the 2022 vineyard dataset or the later GrapeMOTS dataset; the 2022 dataset is the current registered alternative.

## Tests executed

| Test | Procedure | Result |
|---|---|---|
| Primary URL verification | Checked official dataset records, papers, and repositories | Passed |
| DOI verification | Compared dataset and paper DOI links | Passed for IrriDrone, vineyard, and TexCot22; AppleMOTS paper DOI passed |
| Version verification | Checked Zenodo and repository metadata | Passed where version was published; AppleMOTS version remains unknown |
| Primary/secondary classification | Compared source origin and derivative repositories | Passed |

## Verification

- Expected behavior: Each candidate dataset has a canonical data source, primary paper, official project/repository, and version/DOI status.
- Observed behavior: All four candidates have registered sources; AppleMOTS version/DOI remains explicitly unknown.
- Verification result: Passed.

## Evidence

- Primary sources are recorded in this task file.
- Complete source links are also recorded in `PROJECT_DISCOVERY_AND_ARCHITECTURE.md`.
- Independent source audit returned by the research subagent on 2026-10-08.

## Quality gate

- Gate: T01 source-registry gate
- Result: Passed
- Reason: Primary and alternative sources are registered, and unknown source metadata is not fabricated.

## Problems and follow-up

- AppleMOTS dataset version and dataset DOI remain unknown and must remain marked as unknown in later documentation.
- T02 must verify current access and licenses before any dataset is used.

## Approval to continue

- Approved for T02 by: Main agent
- Date: 2026-10-08

## Correction note (2026-10-21, appended; original record unchanged)

- The AppleMOTS canonical source is the Zenodo record [10.5281/zenodo.5939726](https://doi.org/10.5281/zenodo.5939726), version **v1** (2022-02-25), CC BY 4.0, `APPLE_MOTS.zip` 5,661,248,829 bytes, MD5 `1f9b8cd79f05469d656a01015889b55d`.
- The WUR Google Drive link registered above returns HTTP 404 (found in T02) and is obsolete.
- The "Dataset DOI/version not found" status above is superseded. See `../../../DECISION_LOG.md` D-015.
