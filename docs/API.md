# API

Default address `http://localhost:8000`. Interactive documentation is at `/docs`. Errors return `{"detail": "..."}`.

## Flow

1. `POST /api/videos` with multipart field `file`. Returns `{id, filename, size_bytes}`.
2. `POST /api/jobs` with `{"video_id": "..."}`. Returns the job with status `queued`.
3. `GET /api/jobs/{id}/events` streams job state until it ends, or poll `GET /api/jobs/{id}`.
4. When `status` is `done`, read the results from `run_id`.

Repeating step 1 or 2 with the same input returns the existing record.

## Endpoints

| Method and path | Returns |
|---|---|
| `POST /api/videos` | Video record (201) |
| `POST /api/jobs` | Job (202) |
| `GET /api/jobs/{id}` | `id, video_id, status, progress, error, run_id, created_at` |
| `GET /api/jobs/{id}/events` | Server-sent events with the same fields |
| `GET /api/runs/{id}` | `title, model, trained_model, frames, fps_video, width, height, fps_processed, unique_apples` and more |
| `GET /api/runs/{id}/tracks` | `track_id, first_frame, last_frame, length, mean_score` |
| `GET /api/runs/{id}/events` | `frame, track_id, type, event_class, score, details` |
| `GET /api/runs/{id}/counts` | `frame, visible, cumulative_unique` |
| `GET /api/runs/{id}/video` | Annotated WebM, with range requests |
| `GET /api/gallery` | Published demo runs |
| `GET /api/models` | `{active, trained}` |
| `GET /api/limits` | Upload limits |
| `GET /api/benchmarks` | `{status: "pending" or "measured", ...}` plus paper baselines |
| `GET /api/health` | `{status, queued}` |
| `GET /metrics` | Job counts in Prometheus text format |

Job status is `queued`, `running`, `done` or `failed`. Benchmark metrics are fractions from 0 to 1; paper baselines are percentages.

`trained_model: false` means the run used the placeholder, and its counts must not be quoted as accuracy. `event_class` is `gt_derived` for events that can be checked against ground truth, and `ranked_only` for heuristics.

## Error codes

| Code | Meaning |
|---|---|
| 404 | Unknown id |
| 411 | Upload without Content-Length |
| 413 | File over `MAX_UPLOAD_MB` |
| 415 | Not a supported video container |
| 429 | Daily upload limit reached |
| 503 | Queue full |

A video that is too long, or that cannot be decoded, fails in the worker with a readable `error` on the job.
