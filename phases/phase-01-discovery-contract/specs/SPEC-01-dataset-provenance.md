# SPEC-01 — Dataset Provenance and Split Contract

> Revised 2026-10-21 per audit — see `DECISION_LOG.md` (D-001, D-002, D-015, D-019 m6).

## Purpose

Establish trustworthy data provenance and leakage-safe partitions.

## Scope

AppleMOTS archive, sequence IDs, metadata, license, checksums, and split policy.

## Inputs

- Zenodo archive (DOI 10.5281/zenodo.5939726, v1, `APPLE_MOTS.zip`, 5,661,248,829 bytes, MD5 `1f9b8cd79f05469d656a01015889b55d`).
- Official dataset description and paper (DOI 10.1109/LRA.2022.3199026).
- WUR repository documentation.

## Outputs

- Dataset card.
- Immutable manifest.
- Split manifest.
- License and citation record.

## Functional requirements

- Identify every used sequence.
- Record dataset source and version.
- Prevent sequence leakage.
- Preserve ignore regions.
- Record derived labels explicitly.
- Detect duplicated content across sequence IDs by image hash; treat {6, 10}, {7, 11}, {8, 12} as duplicate groups (D-001).
- Test only on 10–12; never use 6–8 for training, validation, or tuning.
- Define validation from sequences 0–5 only: leave-one-sequence-out by default, fallback holdout of 1 wearable + 1 Parrot Anafi sequence (D-002).
- Record the acquisition platform per sequence.

## Technical design

Use a versioned manifest with stable sequence/sample identifiers, file checksums, source URLs, and group keys.

## Interfaces/contracts

`SampleRecord` must include `dataset_id`, `sequence_id`, `frame_id`, `image_uri`, `annotation_uri`, `group_id`, `split`, `license`, `platform` (`wearable` | `parrot_anafi` | `dji_matrice`), `duplicate_group`, `has_ignore_overlay`, and `pts_source`.

## Configuration

Dataset root, selected sequences, split policy (`official` | `loso` | `holdout`), duplicate-group map, random seed, and checksum policy.

## Failure handling

Missing files, checksum mismatches, duplicate frames, unknown sequences, and split overlap block progression.

## Testing requirements

Manifest reconciliation, duplicate detection, cross-sequence image-hash tests, duplicate-group overlap tests, and checksum tests.

## Acceptance criteria

Every selected sample is accounted for, no sequence or duplicate group crosses splits, sequences 6–8 are excluded from all tuning, and split generation is deterministic.

## Evidence requirements

Dataset card, split table, per-sequence platform/frame/instance table, duplicate-group hash report, checksum report, and leakage report.

## Dependencies

None.

## Non-goals

Repairing source annotations or inventing missing metadata.
