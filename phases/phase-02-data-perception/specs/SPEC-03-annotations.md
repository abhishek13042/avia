# SPEC-03 — Annotation and Ground-Truth Adapter

> Revised 2026-10-21 per audit — see `DECISION_LOG.md` (D-014).

## Purpose

Convert AppleMOTS labels into safe evaluation objects.

## Scope

MOTS masks, instance IDs, boxes, areas, ignore regions, and derived detection labels.

## Inputs

PNG images, PNG masks, and sequence metadata.

## Outputs

Canonical `GroundTruthFrame` objects.

## Functional requirements

- Preserve instance identity.
- Derive boxes transparently.
- Distinguish original and derived labels.
- Handle ignore regions using KITTI MOTS / TrackEval semantics: predictions overlapping ignore regions are neither true nor false positives.
- Verify ignore-region encoding in T03/T13 (gray overlay on images and/or a special value in instance PNGs) before relying on it (D-014).
- Document the train/test appearance shift caused by gray overlays on test images 10–12.

## Technical design

Use a non-destructive adapter that retains original mask values and derived geometry.

## Interfaces/contracts

`GroundTruthInstance` contains `instance_id`, `class_id`, `mask`, `bbox`, `area`, `ignore`, and `source_label_type`.

## Configuration

Class mapping, ignore policy (KITTI MOTS class/ID encoding), minimum area, and derived-box policy.

## Failure handling

Invalid mask values, missing masks, duplicate IDs, and inconsistent dimensions.

## Testing requirements

Pixel alignment, box derivation, ID continuity, ignore-region decoding, and ignore-region exclusion tests.

## Acceptance criteria

Visual overlays match ground truth, derived boxes are reproducible, and original labels are never overwritten.

## Evidence requirements

Annotation visualization grid, label statistics, and invalid-label report.

## Dependencies

SPEC-01 and SPEC-02.

## Non-goals

Treating derived boxes as independently annotated box ground truth.
