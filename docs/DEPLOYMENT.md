# Deployment

**What has been tested:** API, worker and site running together on SQLite and local disk, on Windows, with the placeholder model. **Not tested yet:** Docker images, Compose, Postgres, S3 storage, CI, and a GPU worker. Expect to fix small problems on the first run of each.

## Docker Compose

```bash
cp deployment/.env.example deployment/.env
docker compose --env-file deployment/.env -f deployment/docker-compose.yml up --build
```

Change `POSTGRES_PASSWORD` and `IP_SALT` in `deployment/.env` first. The site is on port 3000 and the API on port 8000. Put trained weights in `artifacts/`, which is mounted at `/artifacts`, and set `DETECTOR_SPEC=maskrcnn:/artifacts/model.pt`.

`NEXT_PUBLIC_API_URL` is fixed when the web image is built. Rebuild the image after changing `PUBLIC_API_URL`.

## Settings

| Variable | Default | Meaning |
|---|---|---|
| `DATABASE_URL` | `sqlite:///storage/avia.db` | Use `postgresql+psycopg://...` when public |
| `STORAGE_DIR` | `storage/files` | Local files; shared by API and worker |
| `S3_BUCKET`, `S3_ENDPOINT` | empty | Object storage instead of local files |
| `DETECTOR_SPEC` | `color` | See [MODEL_INTEGRATION.md](MODEL_INTEGRATION.md) |
| `BENCHMARKS_PATH` | `artifacts/benchmarks.json` | Results file |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated site addresses |
| `MAX_UPLOAD_MB` | 200 | Upload size limit |
| `MAX_VIDEO_SECONDS` | 30 | Video length limit |
| `MAX_VIDEO_SIDE` | 1920 | Frame size limit |
| `MAX_UPLOADS_PER_DAY` | 5 | Per client |
| `MAX_QUEUE` | 20 | Queued jobs before new ones are refused |
| `RETENTION_DAYS` | 7 | Uploads and results are then deleted; demos stay |
| `IP_SALT` | `change-me` | Must be changed; hashes client addresses |
| `TRUST_PROXY` | off | Set to `1` only behind your own proxy |

## Going public

The app has no sign-in. Anyone can upload within the limits, and anyone with a run link can open that run. Before sharing a public link:

- Set a real `IP_SALT`, use HTTPS, and use Postgres.
- Run behind a reverse proxy with its own upload size limit, and set `TRUST_PROXY=1`.
- Back up the database. Tables are created at startup and there are no migrations, so a schema change on live data needs a manual migration.
- Run at least one worker. A CPU worker works but is slow on a real model, so short clips and precomputed demos matter.

## Suggested low-cost hosting

Site on Vercel, API and worker on a small container host, Postgres and S3-compatible storage from a managed provider. GPU inference is only worthwhile once there is real traffic; a precomputed gallery covers most visitors.
