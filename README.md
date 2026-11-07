# AVIA: apple segmentation, tracking and counting from orchard video

Upload a short orchard clip. AVIA outlines each apple, tracks it through occlusion, counts each one once, and returns an annotated video, a count over time, and flagged events.

**Status (2026-11-01):** the application works end to end, and a trained Mask R-CNN has been scored on the test set (1 of 3 allowed evaluations). The numbers below come from the repo scorer; mask HOTA is pending because TrackEval has not been run. Docker, Postgres, S3 and CI are still unverified.

| Metric on APPLE MOTS test | AVIA | PointTrack (paper) | TrackR-CNN (paper) |
|---|---|---|---|
| sMOTSA | 43.0 | 38.7 | 35.7 |
| MOTSA | 55.8 | 52.9 | 47.8 |
| MOTSP | 81.2 | 80.0 | 80.4 |
| Mask HOTA | pending | not published | not published |

## How it works

```text
Browser (Next.js) ── upload, SSE progress, results
   │
FastAPI ── Postgres or SQLite (videos, jobs, runs, tracks, events, counts)
   │
Worker ── claims jobs from the database
   │
   ├─ Detector (the plug-in slot: colour placeholder or trained Mask R-CNN)
   ├─ Tracker (links masks across frames)
   ├─ Event engine (lost, reappeared, possible duplicate, unusual motion)
   └─ Writes annotated WebM, masks, tracks, events, counts to local disk or S3
```

## Run it locally

Needs Python 3.11+ and Node 22+. Run each block in its own terminal.

```bash
pip install -e ".[ml,dev]"
uvicorn avia.api.main:app --port 8000
```

```bash
python -m avia.worker.main
```

```bash
python scripts/seed_demo.py --synthetic
npm install --prefix web
npm run dev --prefix web
```

Open http://localhost:3000.

## Plug in the trained model

```bash
DETECTOR_SPEC=maskrcnn:artifacts/model.pt python -m avia.worker.main
```

Set the same `DETECTOR_SPEC` on the API. Nothing else changes. See [docs/MODEL_INTEGRATION.md](docs/MODEL_INTEGRATION.md).

## Tests

```bash
pytest -q
```

The suite covers masks, tracking, events, MOTS metrics, the API, the worker, and a real training run on a tiny synthetic dataset, including resume and loading the checkpoint into the app.

## Documentation

| Document | Purpose |
|---|---|
| [docs/KAGGLE_RUNBOOK.md](docs/KAGGLE_RUNBOOK.md) | From the dataset zip to trained model and results |
| [docs/MODEL_INTEGRATION.md](docs/MODEL_INTEGRATION.md) | Putting a model into the app |
| [docs/API.md](docs/API.md) | HTTP endpoints |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Docker Compose, settings, hosting |
| [docs/MODEL_CARD.md](docs/MODEL_CARD.md) | Model facts and limits |
| [docs/DATASET_CARD.md](docs/DATASET_CARD.md) | APPLE MOTS facts, splits, attribution |
| [DECISION_LOG.md](DECISION_LOG.md) | Every design decision and change |
| [PROJECT_DISCOVERY_AND_ARCHITECTURE.md](PROJECT_DISCOVERY_AND_ARCHITECTURE.md) | Research contract and architecture |
| [PRODUCT_PLATFORM_PLAN.md](PRODUCT_PLATFORM_PLAN.md) | Public product plan |
| [phases/EXECUTION_STATUS.md](phases/EXECUTION_STATUS.md) | Current status and gates |

## Scope

AVIA tracks and counts visible apples. It does not claim irrigation scheduling, plant stress detection, disease diagnosis, or yield prediction.

## Data and licence

APPLE MOTS: De Jong et al., 2022, CC BY 4.0, [doi:10.5281/zenodo.5939726](https://doi.org/10.5281/zenodo.5939726).
