from __future__ import annotations

from typing import Optional

from ..interfaces.kv_store import ObjectStore


class GCSObjectStore(ObjectStore):
    """Google Cloud Storage implementation of ObjectStore.

    URIs use the form gs://bucket/path/to/object
    The instance is initialized with a default bucket and optional prefix.
    If a provided uri already includes gs://bucket, that bucket is used.
    """

    def __init__(self, bucket: str, prefix: Optional[str] = None) -> None:
        from google.cloud import storage  # type: ignore

        self._client = storage.Client()
        self._bucket = self._client.bucket(bucket)
        self._prefix = prefix.strip("/") if prefix else None

    # ----- helpers -----
    def _split_gs_uri(self, uri: str) -> tuple[str, str]:
        assert uri.startswith("gs://"), f"Not a GCS URI: {uri}"
        without = uri[len("gs://") :]
        parts = without.split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""
        return bucket, key

    def _blob_for(self, uri_or_key: str):
        if uri_or_key.startswith("gs://"):
            bkt, key = self._split_gs_uri(uri_or_key)
            return self._client.bucket(bkt).blob(key)
        key = uri_or_key.lstrip("/")
        if self._prefix:
            if not key:
                key = self._prefix
            elif key == self._prefix or key.startswith(f"{self._prefix}/"):
                pass
            else:
                key = f"{self._prefix}/{key}"
        return self._bucket.blob(key)

    def put_bytes(self, uri: str, data: bytes, content_type: Optional[str] = None) -> None:
        blob = self._blob_for(uri)
        blob.upload_from_string(data, content_type=content_type)

    def get_bytes(self, uri: str) -> bytes:
        blob = self._blob_for(uri)
        return blob.download_as_bytes()

    def put_file(self, uri: str, file_path: str, content_type: Optional[str] = None) -> None:
        blob = self._blob_for(uri)
        # Use streaming upload directly from filename to avoid large in-memory buffers
        blob.upload_from_filename(file_path, content_type=content_type)

    def exists(self, uri: str) -> bool:
        blob = self._blob_for(uri)
        return bool(blob.exists())

    def build_uri(self, *parts: str) -> str:
        if not parts:
            return f"gs://{self._bucket.name}/{self._prefix}" if self._prefix else f"gs://{self._bucket.name}"
        # If first part is already a gs:// prefix, treat rest as path
        if parts[0].startswith("gs://"):
            base = parts[0].rstrip("/")
            rest = "/".join([p.strip("/") for p in parts[1:]])
            return f"{base}/{rest}" if rest else base
        key = "/".join([p.strip("/") for p in parts])
        if self._prefix:
            # Avoid double-prefix if caller-provided parts already start with the prefix
            if not key:
                key = self._prefix
            elif key == self._prefix or key.startswith(f"{self._prefix}/"):
                pass
            else:
                key = f"{self._prefix}/{key}"
        return f"gs://{self._bucket.name}/{key}"

    # --------- pickling support (avoid shipping live clients) ---------
    def __getstate__(self) -> dict:
        return {
            "_bucket_name": getattr(self._bucket, "name", None),
            "_prefix": self._prefix,
        }

    def __setstate__(self, state: dict) -> None:
        from google.cloud import storage  # type: ignore
        self._prefix = state.get("_prefix")
        bucket_name = state.get("_bucket_name")
        self._client = storage.Client()
        self._bucket = self._client.bucket(bucket_name) if bucket_name else None


