# SPEC-04 — Visual Perception

> Revised 2026-10-21 per audit — see `DECISION_LOG.md` (D-005, D-006, D-020, D-021).

## Purpose

Detect and segment visible apples.

## Scope

Baseline detector, main instance-segmentation model, preprocessing, training, and inference.

## Inputs

`FramePacket`, training labels, and split manifest.

## Outputs

`PerceptionFrame` objects.

## Functional requirements

Return boxes, masks where supported, class confidence, model version, and processing time.

## Technical design

- Baseline: Mask R-CNN R50-FPN, COCO-pretrained, full 1296 × 972 resolution (D-005). Optional: YOLOX-S with mask-derived boxes, evaluated box-only.
- Main: selected on validation (sequences 0–5) from Mask R-CNN high-res/tiled, RTMDet-Ins, and Mask2Former, using pre-registered criteria: mask AP, small-object recall (below 32 px), and latency (D-006). Apples are about 30–50 px, so small-object recall is decisive.
- Runtime candidate: selected by measured accuracy/latency.
- Licensing: prefer Apache-2.0/MIT components (Detectron2, MMDetection); exclude AGPL-3.0 (Ultralytics) unless explicitly accepted.
- Framework: one framework for the whole comparison (MMDetection 3.x preferred, Detectron2 fallback); versions pinned in T10/T20.
- Accuracy levers (D-021), chosen on LOSO validation only: native or upscaled resolution, small anchors / P2 level, random gray-patch augmentation (matches the test ignore overlays), copy-paste, scale/color/blur jitter, higher-resolution mask head, EMA weights, score threshold tuned for HOTA/sMOTSA.
- Offline-only levers: sliced (tiled) inference and flip/multi-scale TTA. Results are labelled "offline".

## Interfaces/contracts

`PerceptionInstance` contains `class_id`, `confidence`, `bbox`, and optional `mask` plus `model_version`.

## Configuration

Input size, upscale factor, tiling and tile overlap, anchor sizes, augmentation set, TTA flag, EMA, confidence threshold, NMS, batch size, precision, and checkpoint path.

## Failure handling

Empty frame, invalid tensor shape, NaN output, out-of-range box, and out-of-memory.

## Testing requirements

Tiny overfit, shape checks, coordinate checks, mask rendering, CPU forward pass, GPU smoke pass, and small-object recall evaluation.

## Acceptance criteria

Predictions align with images, no NaNs occur, a tiny fixture can be overfit, and metrics are reproducible.

## Evidence requirements

Training curves, sample predictions, checkpoint metadata, and metric report.

## Dependencies

SPEC-01 through SPEC-03.

## Non-goals

Disease, stress, irrigation, maturity, or yield prediction.
