import dataclasses
from datetime import timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from avia.api.db import Job, Run, Video, make_session_factory, utcnow
from avia.api.main import create_app
from avia.perception.color import ColorBlobDetector
from avia.settings import Settings
from avia.storage import LocalStorage
from avia.worker.main import claim_next, delete_expired, requeue_stale, run_job


@pytest.fixture
def env(tmp_path):
    settings = Settings(database_url=f"sqlite:///{(tmp_path / 'a.db').as_posix()}",
                        storage_dir=str(tmp_path / "files"),
                        benchmarks_path=str(tmp_path / "benchmarks.json"), max_uploads_per_day=2,
                        max_queue=2)
    client = TestClient(create_app(settings))
    return settings, client, make_session_factory(settings.database_url), \
        LocalStorage(settings.storage_dir)


def upload(client, path, name="clip.webm"):
    with open(path, "rb") as f:
        return client.post("/api/videos", files={"file": (name, f, "video/webm")})


def work(env):
    settings, _, factory, storage = env
    job_id = claim_next(factory)
    assert job_id
    run_job(factory, storage, ColorBlobDetector(), settings, job_id)
    return job_id


def test_full_flow_from_upload_to_results(env, video):
    _, client, _, _ = env
    video_id = upload(client, video).json()["id"]
    job = client.post("/api/jobs", json={"video_id": video_id})
    assert job.status_code == 202 and job.json()["status"] == "queued"
    work(env)
    state = client.get(f"/api/jobs/{job.json()['id']}").json()
    assert state["status"] == "done" and state["progress"] == 1.0
    run_id = state["run_id"]
    run = client.get(f"/api/runs/{run_id}").json()
    assert run["trained_model"] is False and run["unique_apples"] == 3
    assert len(client.get(f"/api/runs/{run_id}/tracks").json()) == 3
    assert len(client.get(f"/api/runs/{run_id}/counts").json()) == run["frames"]
    assert client.get(f"/api/runs/{run_id}/events").json()[0]["type"] == "first_seen"
    response = client.get(f"/api/runs/{run_id}/video")
    assert response.status_code == 200 and response.headers["content-type"] == "video/webm"
    ranged = client.get(f"/api/runs/{run_id}/video", headers={"Range": "bytes=0-99"})
    assert ranged.status_code == 206


def test_sse_stream_reports_final_state(env, video):
    _, client, _, _ = env
    job = client.post("/api/jobs", json={"video_id": upload(client, video).json()["id"]}).json()
    work(env)
    body = client.get(f"/api/jobs/{job['id']}/events").text
    assert body.startswith("data: ") and '"status": "done"' in body


def test_upload_rejects_non_video(env, tmp_path):
    _, client, _, _ = env
    fake = tmp_path / "fake.webm"
    fake.write_bytes(b"not a video at all")
    assert upload(client, fake).status_code == 415
    assert upload(client, fake, "x.exe").status_code == 415


def test_upload_size_limit(env, tmp_path, video):
    settings, *_ = env
    client = TestClient(create_app(dataclasses.replace(settings, max_upload_mb=0)))
    assert upload(client, video).status_code == 413


def test_same_upload_and_job_are_idempotent(env, video):
    _, client, _, _ = env
    first, second = upload(client, video), upload(client, video)
    assert first.json()["id"] == second.json()["id"]
    body = {"video_id": first.json()["id"]}
    assert client.post("/api/jobs", json=body).json()["id"] == \
        client.post("/api/jobs", json=body).json()["id"]


def test_daily_upload_limit(env, tmp_path, video):
    _, client, _, _ = env
    original = Path(video).read_bytes()
    codes = []
    for i in range(3):
        path = tmp_path / f"v{i}.webm"
        path.write_bytes(original + bytes([i]))
        codes.append(upload(client, path).status_code)
    assert codes == [201, 201, 429]


def test_queue_cap(env, tmp_path, video):
    settings, _, _, _ = env
    client = TestClient(create_app(dataclasses.replace(settings, max_uploads_per_day=9)))
    original = Path(video).read_bytes()
    codes = []
    for i in range(3):
        path = tmp_path / f"q{i}.webm"
        path.write_bytes(original + bytes([i]))
        codes.append(client.post("/api/jobs", json={"video_id": upload(client, path).json()["id"]})
                     .status_code)
    assert codes == [202, 202, 503]


def test_too_long_video_fails_with_clear_message(env, video):
    settings, client, factory, storage = env
    job = client.post("/api/jobs", json={"video_id": upload(client, video).json()["id"]}).json()
    short = dataclasses.replace(settings, max_video_seconds=0.1)
    run_job(factory, storage, ColorBlobDetector(), short, claim_next(factory))
    state = client.get(f"/api/jobs/{job['id']}").json()
    assert state["status"] == "failed" and "limit" in state["error"]
    with factory() as s:
        assert s.get(Job, job["id"]).attempts == 1


def test_crash_retries_then_fails_without_leaking_details(env, video):
    settings, client, factory, storage = env
    job = client.post("/api/jobs", json={"video_id": upload(client, video).json()["id"]}).json()

    class Broken:
        name, trained = "broken", False

        def detect(self, image):
            raise RuntimeError("secret internal path")

    for _ in range(settings.max_attempts):
        run_job(factory, storage, Broken(), settings, claim_next(factory))
    state = client.get(f"/api/jobs/{job['id']}").json()
    assert state["status"] == "failed" and "secret" not in state["error"]
    assert claim_next(factory) is None


def test_job_is_claimed_once(env, video):
    _, client, factory, _ = env
    client.post("/api/jobs", json={"video_id": upload(client, video).json()["id"]})
    assert claim_next(factory) is not None
    assert claim_next(factory) is None


def test_stale_job_goes_back_to_queue(env, video):
    settings, client, factory, _ = env
    job = client.post("/api/jobs", json={"video_id": upload(client, video).json()["id"]}).json()
    claim_next(factory)
    with factory() as s:
        s.get(Job, job["id"]).heartbeat_at = utcnow() - timedelta(hours=1)
        s.commit()
    assert requeue_stale(factory, settings) == 1
    assert claim_next(factory) == job["id"]


def test_expired_uploads_are_deleted_but_demos_stay(env, video):
    settings, client, factory, storage = env
    video_id = upload(client, video).json()["id"]
    job = client.post("/api/jobs", json={"video_id": video_id}).json()
    work(env)
    run_id = client.get(f"/api/jobs/{job['id']}").json()["run_id"]
    with factory() as s:
        row = s.get(Video, video_id)
        row.created_at = utcnow() - timedelta(days=30)
        key = row.storage_key
        s.commit()
    assert delete_expired(factory, storage, settings) == 1
    assert storage.local_path(key) is None
    assert client.get(f"/api/runs/{run_id}").status_code == 404
    assert storage.local_path(f"runs/{job['id']}/annotated.webm") is None


def test_gallery_shows_only_demo_runs(env, video):
    _, client, factory, _ = env
    job = client.post("/api/jobs", json={"video_id": upload(client, video).json()["id"]}).json()
    work(env)
    assert client.get("/api/gallery").json() == []
    with factory() as s:
        s.query(Run).filter(Run.job_id == job["id"]).update({"is_demo": True})
        s.commit()
    assert len(client.get("/api/gallery").json()) == 1


def test_benchmarks_are_pending_until_the_file_exists(env):
    settings, client, _, _ = env
    body = client.get("/api/benchmarks").json()
    assert body["status"] == "pending" and body["baselines"][0]["sMOTSA"] == 38.7
    with open(settings.benchmarks_path, "w", encoding="utf-8") as f:
        f.write('{"status": "measured", "overall": {"sMOTSA": 0.5}}')
    assert client.get("/api/benchmarks").json()["status"] == "measured"


def test_health_metrics_models_and_404(env):
    _, client, _, _ = env
    assert client.get("/api/health").json() == {"status": "ok", "queued": 0}
    assert client.get("/metrics").status_code == 200
    assert client.get("/api/models").json() == {"active": "color", "trained": False}
    assert client.get("/api/runs/nope").status_code == 404
    assert "x-request-id" in client.get("/api/health").headers
