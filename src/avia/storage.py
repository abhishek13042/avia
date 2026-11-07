"""File storage: local disk for development, S3 or R2 in production."""
import os
import shutil

from avia.settings import Settings


class LocalStorage:
    def __init__(self, root: str):
        self.root = root

    def _path(self, key: str) -> str:
        path = os.path.abspath(os.path.join(self.root, key))
        if not path.startswith(os.path.abspath(self.root) + os.sep):
            raise ValueError("key escapes the storage root")
        return path

    def put(self, key: str, source: str) -> None:
        path = self._path(key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        shutil.copyfile(source, path)

    def fetch(self, key: str, destination: str) -> None:
        shutil.copyfile(self._path(key), destination)

    def local_path(self, key: str) -> str | None:
        path = self._path(key)
        return path if os.path.exists(path) else None

    def public_url(self, key: str) -> str | None:
        return None

    def delete(self, key: str) -> None:
        path = self._path(key)
        if os.path.exists(path):
            os.remove(path)

    def delete_prefix(self, prefix: str) -> None:
        shutil.rmtree(self._path(prefix), ignore_errors=True)


class S3Storage:
    """Any S3-compatible store. Videos reach the browser through presigned URLs."""

    def __init__(self, bucket: str, endpoint: str = ""):
        import boto3

        self.bucket = bucket
        self.client = boto3.client("s3", endpoint_url=endpoint or None)

    def put(self, key: str, source: str) -> None:
        self.client.upload_file(source, self.bucket, key)

    def fetch(self, key: str, destination: str) -> None:
        self.client.download_file(self.bucket, key, destination)

    def local_path(self, key: str) -> str | None:
        return None

    def public_url(self, key: str) -> str | None:
        return self.client.generate_presigned_url(
            "get_object", Params={"Bucket": self.bucket, "Key": key}, ExpiresIn=3600)

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def delete_prefix(self, prefix: str) -> None:
        pages = self.client.get_paginator("list_objects_v2").paginate(
            Bucket=self.bucket, Prefix=prefix.rstrip("/") + "/")
        for page in pages:
            for item in page.get("Contents", []):
                self.delete(item["Key"])


def make_storage(settings: Settings):
    if settings.s3_bucket:
        return S3Storage(settings.s3_bucket, settings.s3_endpoint)
    os.makedirs(settings.storage_dir, exist_ok=True)
    return LocalStorage(settings.storage_dir)
