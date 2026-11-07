# SPEC-02 — Media Ingestion and Temporal Replay

> Revised 2026-10-21 per audit — see `DECISION_LOG.md` (D-010).

## Purpose

Convert frame sequences and optional local video streams into a canonical temporal input.

## Scope

PNG sequence reader, optional MP4/RTSP adapter, timestamps, offline replay, and causal replay.

## Inputs

Image frames, sequence metadata, and optional local replay video.

## Outputs

Canonical `FramePacket` objects.

## Functional requirements

- Preserve frame order.
- Provide source frame ID.
- Support offline and causal replay.
- Detect gaps.
- Prevent look-ahead.
- Synthesize timestamps: AppleMOTS has no timestamps, so `capture_pts = frame_index / nominal_fps` with a nominal FPS per platform (25–30 FPS), and `pts_source = synthetic` (D-010). Real streams use `pts_source = source`.

## Technical design

Use adapters with deterministic sequence mode and wall-clock replay mode.

## Interfaces/contracts

`FramePacket` contains `stream_id`, `sequence_id`, `frame_id`, `capture_pts`, `pts_source` (`synthetic` | `source`), `image`, `source_uri`, and `dropped_flag`.

## Configuration

Replay FPS, nominal FPS per platform, resize, color order, queue size, frame skipping, and causal mode.

## Failure handling

Corrupt image, missing frame, non-monotonic timestamp, decode failure, and queue overflow.

## Testing requirements

Deterministic order, corrupt-frame, timestamp, and dropped-frame tests.

## Acceptance criteria

The same manifest creates the same ordered frame stream, and causal mode never exposes future frames.

## Evidence requirements

Replay log, frame-order report, and rendered sample stream.

## Dependencies

SPEC-01.

## Non-goals

Claiming AppleMOTS itself is a live camera feed.
