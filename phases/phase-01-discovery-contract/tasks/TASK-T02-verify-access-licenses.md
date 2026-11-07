# TASK-T02 — Verify Access, Licenses, Citations, and Archive Versions

## Task identity

- Task ID: T02
- Task name: Verify access, licenses, citations, and archive versions
- Phase: Phase 1 — Dataset, problem, and evaluation contract
- SPEC: SPEC-01 — Dataset provenance and split contract
- Status: Verified
- Execution date: 2026-10-08

## Objective

Verify that the registered datasets are accessible, correctly licensed, citable, and versioned before they are used in the project.

## Scope

### Included

- AppleMOTS.
- IrriDrone.
- 2022 UAV vineyard grape-bunch dataset.
- TexCot22/NTrack.
- Access status.
- License evidence.
- Citation requirements.
- Archive/version evidence.
- Redistribution caveats.

### Non-goals

- Downloading large archives into the project.
- Training models.
- Installing dependencies.
- Resolving blocked third-party archive pages by bypassing access controls.

## Dependencies

T01 — Register primary and alternative dataset sources.

## Inputs

- T01 source registry.
- Official dataset records.
- Official project repositories.
- Dataset papers and DOI metadata.

## Implementation result

### AppleMOTS

- Current Zenodo archive is open and returned HTTP 200 in the read-only audit.
- Dataset record: [Zenodo 10.5281/zenodo.5939726](https://doi.org/10.5281/zenodo.5939726).
- Dataset license: CC BY 4.0.
- Archive size: 5,661,248,829 bytes.
- MD5: `1f9b8cd79f05469d656a01015889b55d`.
- No semantic dataset version number was found.
- The WUR Google Drive URL registered in T01 currently returns 404.
- The Zenodo record is therefore the reproducible source of record.
- Required citations:
  - [Dataset record](https://doi.org/10.5281/zenodo.5939726).
  - [APPLE MOTS paper](https://doi.org/10.1109/LRA.2022.3199026).

### IrriDrone

- Zenodo record is open and version 1.0.
- Dataset record: [Zenodo 10.5281/zenodo.22017449](https://doi.org/10.5281/zenodo.22017449).
- Dataset license: CC BY 4.0.
- Concept DOI: `10.5281/zenodo.22017448`.
- README and metadata are accessible.
- UOK share endpoint resolves, but the dynamic file listing was not independently extracted.
- Required citations:
  - [Dataset record](https://doi.org/10.5281/zenodo.22017449).
  - [IrriDrone paper](https://doi.org/10.1016/j.dib.2026.113208).
- Paired annotated/unannotated recordings must remain in the same partition.

### UAV vineyard grape-bunch dataset

- Current Zenodo record is open and version 2.0.
- Dataset record: [Zenodo 10.5281/zenodo.7330951](https://doi.org/10.5281/zenodo.7330951).
- Current sample MP4 access returned HTTP 200.
- Dataset license: CC BY 4.0.
- Historical predecessor and concept DOI are preserved in Zenodo metadata.
- Required citations:
  - [Dataset record](https://doi.org/10.5281/zenodo.7330951).
  - [Vineyard dataset paper](https://doi.org/10.1016/j.dib.2022.108848).

### TexCot22/NTrack

- DOI is findable and open at the metadata level.
- Current DataCite metadata reports version 2.4.
- Official NTrack material calls the dataset V2.
- Official project material states CC BY-NC-SA 4.0 for the dataset.
- NTrack source code is separately Apache 2.0.
- Repository file-level access and current custom-license text were blocked by a WAF during the audit.
- Required citations:
  - [TexCot22 DOI](https://doi.org/10.18738/T8/5M9NCI).
  - [NTrack paper](https://doi.org/10.1109/TASE.2023.3342791).
- Project use is conditional on confirming current archive access and noncommercial terms.

## Verified facts

- AppleMOTS, IrriDrone, and the vineyard dataset have live open Zenodo records with license metadata.
- AppleMOTS is CC BY 4.0 but has no numbered dataset version exposed.
- IrriDrone is CC BY 4.0 version 1.0.
- The vineyard dataset is CC BY 4.0 version 2.0.
- TexCot22 is findable/open at DOI metadata level.
- Official NTrack materials state CC BY-NC-SA 4.0 for the data and Apache 2.0 for the code.

## Unknowns

- AppleMOTS semantic version and replacement for the dead WUR Google Drive link.
- IrriDrone UOK dynamic file listing details.
- TexCot22 current Dataverse custom-license text, exact live archive manifest, file-level download access, and mapping between metadata version 2.4 and project label V2.

## Tests executed

| Test | Procedure | Result |
|---|---|---|
| AppleMOTS access | Read-only Zenodo archive request | Passed, HTTP 200 |
| AppleMOTS license | Read Zenodo license metadata and CC BY record | Passed |
| AppleMOTS legacy link | Read-only WUR Google Drive URL request | Failed/obsolete, HTTP 404; Zenodo retained |
| IrriDrone access | Read-only Zenodo record and README requests | Passed |
| IrriDrone license/version | Checked Zenodo metadata and README | Passed, CC BY 4.0, v1.0 |
| Vineyard access | Read-only Zenodo record and sample MP4 request | Passed |
| Vineyard license/version | Checked Zenodo metadata and version history | Passed, CC BY 4.0, v2.0 |
| TexCot22 metadata | Checked DOI/DataCite metadata | Passed at metadata level |
| TexCot22 file access | Attempted repository file-level read | Blocked by WAF; recorded as unresolved |

## Verification

- Expected behavior: Access, license, citation, and version status must be known or explicitly marked unknown for every candidate.
- Observed behavior: Three datasets are fully verified through Zenodo; TexCot22 has metadata-level verification with file-access caveats.
- Verification result: Passed with documented limitations.

## Evidence

- Official dataset and DOI links are recorded in this task file.
- Detailed read-only audit returned by the research subagent on 2026-10-08.
- T01 source registry.
- Zenodo metadata and archive checksums where available.

## Quality gate

- Gate: T02 access/license/version gate
- Result: Passed with caveats
- Reason: AppleMOTS, IrriDrone, and the vineyard dataset are suitable for documented use through current open records. TexCot22 is retained as a conditional alternative only.

## Problems and follow-up

- Use Zenodo, not the obsolete AppleMOTS Google Drive URL.
- Retain AppleMOTS version as unknown rather than fabricating one.
- Do not use TexCot22 until current archive download and terms are confirmed through a normal repository session.
- T03 must record all verified facts, assumptions, and unknowns in a formal fact matrix.

## Approval to continue

- Approved for T03 by: Main agent
- Date: 2026-10-08

## Correction note (2026-10-21, appended; original record unchanged)

- Zenodo exposes AppleMOTS as version **v1** with dataset DOI 10.5281/zenodo.5939726; "no numbered dataset version" above is superseded.
- The open paper copy (edepot.wur.nl/577473) is under Taverne terms: cite it, do not redistribute it.
- See `../../../DECISION_LOG.md` D-015 and D-019 m7.
