"""Configuration, all from environment variables (see deployment/.env.example)."""
import os
from dataclasses import dataclass, field


def _int(name: str, default: int) -> int:
    return int(os.environ.get(name, default))


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///storage/avia.db"
    storage_dir: str = "storage/files"
    s3_bucket: str = ""
    s3_endpoint: str = ""
    detector_spec: str = "color"
    benchmarks_path: str = "artifacts/benchmarks.json"
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:3000"])
    max_upload_mb: int = 200
    max_video_seconds: int = 30
    max_video_side: int = 1920
    max_uploads_per_day: int = 5
    max_queue: int = 20
    retention_days: int = 7
    stale_seconds: int = 300
    max_attempts: int = 3
    ip_salt: str = "change-me"
    trust_proxy: bool = False


def load_settings() -> Settings:
    d = Settings()
    origins = os.environ.get("CORS_ORIGINS")
    return Settings(
        database_url=os.environ.get("DATABASE_URL", d.database_url),
        storage_dir=os.environ.get("STORAGE_DIR", d.storage_dir),
        s3_bucket=os.environ.get("S3_BUCKET", d.s3_bucket),
        s3_endpoint=os.environ.get("S3_ENDPOINT", d.s3_endpoint),
        detector_spec=os.environ.get("DETECTOR_SPEC", d.detector_spec),
        benchmarks_path=os.environ.get("BENCHMARKS_PATH", d.benchmarks_path),
        cors_origins=origins.split(",") if origins else d.cors_origins,
        max_upload_mb=_int("MAX_UPLOAD_MB", d.max_upload_mb),
        max_video_seconds=_int("MAX_VIDEO_SECONDS", d.max_video_seconds),
        max_video_side=_int("MAX_VIDEO_SIDE", d.max_video_side),
        max_uploads_per_day=_int("MAX_UPLOADS_PER_DAY", d.max_uploads_per_day),
        max_queue=_int("MAX_QUEUE", d.max_queue),
        retention_days=_int("RETENTION_DAYS", d.retention_days),
        ip_salt=os.environ.get("IP_SALT", d.ip_salt),
        trust_proxy=os.environ.get("TRUST_PROXY", "") == "1",
    )
