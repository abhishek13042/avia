"""Database schema. SQLite in development, Postgres in production."""
import os
import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    event,
)
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def new_id() -> str:
    return uuid.uuid4().hex


class Base(DeclarativeBase):
    pass


class Video(Base):
    __tablename__ = "videos"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    filename: Mapped[str] = mapped_column(String(255))
    storage_key: Mapped[str] = mapped_column(String(255))
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    size_bytes: Mapped[int] = mapped_column(Integer)
    client_hash: Mapped[str] = mapped_column(String(64), index=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"), index=True)
    status: Mapped[str] = mapped_column(String(16), default="queued", index=True)
    model: Mapped[str] = mapped_column(String(255))
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    run_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Run(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    model: Mapped[str] = mapped_column(String(255))
    trained_model: Mapped[bool] = mapped_column(Boolean)
    frames: Mapped[int] = mapped_column(Integer)
    fps_video: Mapped[float] = mapped_column(Float)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    fps_processed: Mapped[float] = mapped_column(Float)
    unique_apples: Mapped[int] = mapped_column(Integer)
    storage_prefix: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Track(Base):
    __tablename__ = "tracks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    track_id: Mapped[int] = mapped_column(Integer)
    first_frame: Mapped[int] = mapped_column(Integer)
    last_frame: Mapped[int] = mapped_column(Integer)
    length: Mapped[int] = mapped_column(Integer)
    mean_score: Mapped[float] = mapped_column(Float)


class EventRow(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    frame: Mapped[int] = mapped_column(Integer)
    track_id: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String(32))
    event_class: Mapped[str] = mapped_column(String(16))
    score: Mapped[float] = mapped_column(Float)
    details: Mapped[dict] = mapped_column(JSON)


class Count(Base):
    __tablename__ = "counts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    frame: Mapped[int] = mapped_column(Integer)
    visible: Mapped[int] = mapped_column(Integer)
    cumulative_unique: Mapped[int] = mapped_column(Integer)


def make_session_factory(database_url: str) -> sessionmaker:
    url = make_url(database_url)
    connect_args = {}
    if url.get_backend_name() == "sqlite":
        connect_args = {"check_same_thread": False, "timeout": 30}
        if url.database:
            os.makedirs(os.path.dirname(url.database) or ".", exist_ok=True)
    engine = create_engine(url, connect_args=connect_args, pool_pre_ping=True)
    if url.get_backend_name() == "sqlite":
        event.listen(engine, "connect", _sqlite_wal)
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)


def _sqlite_wal(connection, _record) -> None:
    connection.execute("PRAGMA journal_mode=WAL")


__all__ = ["Base", "Count", "Engine", "EventRow", "Job", "Run", "Track", "Video",
           "make_session_factory", "new_id", "utcnow"]
