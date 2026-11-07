# SPEC-11 — Deployment, Observability, and Runtime Benchmarking

> Revised 2026-10-21 per audit — see `DECISION_LOG.md` (D-011, D-020).

## Purpose

Measure and operate the pipeline under realistic runtime conditions.

## Scope

Replay worker, optional live input, queues, metrics, resource monitoring, and export.

## Inputs

Frames/video stream, model artifact, and runtime configuration.

## Outputs

Inference results, telemetry, benchmark report, and evidence frames.

## Functional requirements

Record throughput, stage latency, queue depth, drops, memory, GPU utilization, failures, and recovery.

Real-time target (D-011): ≥25 FPS sustained end-to-end (ingest → perception → tracking → events) at the native 1296 × 972 resolution on a named GPU, with a 30 FPS stress case. If not met, the system is labelled "measured offline".

Benchmark hardware (D-020): the local machine has no CUDA GPU, so G5 is measured on the Kaggle GPU actually allocated (recorded by name). A CPU-only local measurement may be reported separately and is never called real-time. Runtime levers: ONNX/TensorRT FP16 export, lighter runtime model, and detector interval with tracker propagation between detections.

## Technical design

Use a modular worker pipeline with bounded queues and explicit timestamps. Export/optimization occurs only after correctness is established.

## Interfaces/contracts

Every output carries source frame ID, capture timestamp, processing timestamp, model version, and dropped/skipped-frame status.

## Configuration

Stream count, input size, detector interval, precision, queue policy, and rendering mode.

## Failure handling

Camera loss, decoder failure, queue overflow, GPU OOM, restart, stale frame, and storage failure.

## Testing requirements

Load test, induced drops, decode failure, camera restart, memory stress, and precision comparison.

## Acceptance criteria

The benchmark is repeatable and reports p50/p95/p99 latency, throughput, memory, and drop rate at 1296 × 972 on a named GPU. Real-time status is determined from measured results against the ≥25 FPS target.

## Evidence requirements

Benchmark logs, hardware information, latency charts, memory charts, and drop-rate report.

## Dependencies

SPEC-02, SPEC-04 through SPEC-10.

## Non-goals

Claiming production deployment on hardware that was not tested.
