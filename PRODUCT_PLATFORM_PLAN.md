# AVIA — Product Platform Plan (frontend, backend, database, hosting)

Created 2026-10-29. Status: **Approved and built in first form** (D-023, deviations in D-024). It extends Phase 4 (T45–T48) from "API + dashboard for one person" to "a public web app many people can use". It does not change the research contract (D-001–D-022).

## Goal

A public, working web app that a recruiter or engineer can open from a resume link and use in under a minute:

1. Open the site and see results on the APPLE MOTS test sequences straight away (precomputed, no wait).
2. Upload a short orchard video (≤ 30 s) and get back an annotated video, per-apple tracks, an apple count, and events.
3. Open a benchmark page showing honest numbers (mask HOTA, sMOTSA vs. PointTrack/TrackR-CNN, FPS on a named GPU) with a model card and reproduction instructions.

What makes it a top resume project is that it is **real, measured and running**, not a large feature list.

## Constraints that drive the design

| Constraint | Consequence |
|---|---|
| No local GPU; Kaggle cannot serve traffic (D-020) | Inference runs on a serverless GPU that starts on demand; the always-on parts run on CPU |
| GPU time costs money | Precompute the demo sequences; cap upload length; queue jobs; rate-limit per user |
| Many users, long jobs (seconds to minutes) | Asynchronous jobs: upload → queue → worker → results; never block an HTTP request on inference |
| Dataset CC BY 4.0 | Public demo allowed with attribution on the site and in the model card |

## Architecture

```text
Browser (Next.js on Vercel)
   │  HTTPS (REST + server-sent events for job progress)
   ▼
API (FastAPI, Python, CPU container)
   ├── Postgres (Neon or Supabase): users, videos, jobs, runs, tracks, events, counts
   ├── Object storage (Cloudflare R2 or S3): uploaded videos, annotated videos, mask files, thumbnails
   └── Job queue (Redis queue, or the GPU provider's own queue)
            ▼
GPU worker (Modal or RunPod serverless, T4/L4): ONNX/TensorRT detector + tracker + event engine
   └── writes results to object storage + Postgres, reports progress
```

Fallback, if the free path is preferred: one Hugging Face Space (Gradio/FastAPI + ZeroGPU) for the demo, with the same API contract. The Space is the cheapest option but gives less control over users and storage.

## Components

### Frontend (Next.js + TypeScript + Tailwind)

- Landing page: one-line pitch, demo video, three numbers (HOTA, apples counted, FPS).
- Demo gallery: test sequences 10–12 with a synchronized video player, mask/track overlay toggles, per-track timeline, apple count over time.
- Upload page: drag and drop, live job progress (queued → running → done), result page with a shareable link.
- Benchmark page: tables generated from the T52–T58 result files, not typed by hand.
- Model card and dataset attribution page.
- Sign-in (GitHub/Google via Auth.js or Supabase Auth) only for uploads; the gallery is public.

### Backend (FastAPI)

- Endpoints: `POST /videos` (pre-signed upload URL), `POST /jobs`, `GET /jobs/{id}` + SSE progress, `GET /runs/{id}/tracks|events|counts`, `GET /models`, `GET /health`, `GET /metrics`.
- The contracts come from T45 (OpenAPI schema frozen first; the frontend client is generated from it).
- Validation: file type, duration ≤ 30 s, resolution cap, virus-safe handling (decode with ffmpeg in the worker only).
- Rate limits and per-user quotas; idempotent job creation; retries with a dead-letter state.

### Database (Postgres)

| Table | Key fields |
|---|---|
| users | id, provider, created_at, quota_used |
| videos | id, owner, storage_key, duration_s, fps, width, height, sha256 |
| jobs | id, video_id, status, model_version, created_at, started_at, finished_at, error |
| runs | id, job_id, model_version, tracker_config_hash, fps_measured, gpu_name |
| tracks | id, run_id, track_id, first_frame, last_frame, length, mean_score |
| events | id, run_id, track_id, type, event_class (gt_derived/synthetic/ranked_only), frame, score, evidence_key |
| counts | run_id, frame, visible, cumulative_unique |

Per-frame masks are stored as RLE in Parquet files in object storage, not as database rows (millions of rows otherwise). Migrations with Alembic.

### Model serving

- Export the chosen model (T28) to ONNX; TensorRT FP16 where the GPU supports it (T49).
- Model registry: each model version has a name, weights hash, training-run link, and validation metrics; the API reports which version produced each result.
- Warm-start: keep one GPU container warm during demo hours only, to control cost.

### Engineering quality (what reviewers look for)

- Monorepo: `ml/`, `api/`, `worker/`, `web/`, `infra/`.
- Docker Compose for local development (API + Postgres + Redis + CPU worker running the ONNX model slowly).
- CI (GitHub Actions): lint, type check, unit tests, API contract tests, a CPU smoke test of the worker on the golden fixture (T15), frontend build, and Playwright end-to-end tests.
- Observability: structured logs, request IDs, Sentry for errors, a status page showing queue length and job latency.
- Security: pre-signed uploads, size limits, auth on uploads, secrets in the platform's secret store, CORS locked to the site.
- Load test (k6/Locust) on the API and the queue; the results go on the benchmark page.

## Order of work (fits around the GPU training)

| Step | When | Depends on |
|---|---|---|
| P1 OpenAPI contracts + DB schema (extends T45) | Now, during Phase 2 | — |
| P2 Monorepo, Docker Compose, CI skeleton | Phase 2, alongside T10–T21 | P1 |
| P3 API + Postgres + storage + queue with a dummy worker | Phase 3, while models train on Kaggle | P2 |
| P4 Frontend: gallery, upload, job progress | Phase 3 | P3 |
| P5 Real worker: ONNX model + tracker + events | After G3 (model selected, T32) | T28, T32 |
| P6 Deploy: Vercel + API host + Neon + R2 + serverless GPU | After P5 | P5 |
| P7 Benchmark page, model card, load test, Playwright | After T49–T58 | P6 |
| P8 Launch: README with GIF, demo video, write-up/blog | After G7 | P7 |

Estimated extra effort: about 3–5 weeks part-time (2–3 weeks full-time), mostly overlapping with GPU training waits. Running cost: about $0–10/month at demo traffic if the GPU only starts on demand and demo results are precomputed.

## Not in scope

- Real-time streaming from a live drone camera for the public (the runtime claim stays a measured benchmark, D-011).
- Payments or teams.
- Training from the web app.
