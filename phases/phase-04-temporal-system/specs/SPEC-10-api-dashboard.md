# SPEC-10 — API and Dashboard

> Revised 2026-10-21 per audit — see `DECISION_LOG.md` (D-008, D-010).

## Purpose

Deliver observations, tracks, events, health, and evidence through a usable interface.

## Scope

REST/OpenAPI API, WebSocket/SSE updates, dashboard views, and evidence retrieval.

## Inputs

Tracks, events, metrics, health telemetry, and rendered evidence.

## Outputs

API responses, live updates, and dashboard views.

## Functional requirements

Expose streams, health, tracks, events, evidence, model versions, and metrics.

## Technical design

REST API with OpenAPI, WebSocket or SSE for metadata, object storage for evidence, and a metadata store.

## Interfaces/contracts

Initial endpoints:

```text
GET /v1/streams
GET /v1/streams/{stream_id}/health
GET /v1/events
GET /v1/events/{event_id}
GET /v1/tracks
GET /v1/evidence/{evidence_id}
GET /v1/models
GET /metrics
```

## Configuration

Host, port, storage URI, authentication mode, retention, and update rate.

## Failure handling

Idempotent event ingestion, stale-stream status, unavailable evidence, and API timeout.

## Testing requirements

Contract tests, schema validation (including nullable `calibrated_probability` and `mask`, and `event_class`/`pts_source` fields), invalid-ID tests, browser smoke test, and stale-data test.

## Acceptance criteria

Responses match the contract and the dashboard displays source frames, tracks, alerts, event class, confidence, and timestamps (marked as synthetic where `pts_source = synthetic`).

## Evidence requirements

OpenAPI document, screenshots, recorded demo, and API test report.

## Dependencies

SPEC-07 and SPEC-09.

## Non-goals

Full multi-tenant production SaaS.
