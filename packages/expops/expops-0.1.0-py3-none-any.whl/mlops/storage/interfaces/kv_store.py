from __future__ import annotations

from typing import Any, Optional, Protocol


class KeyValueEventStore(Protocol):
    """Key/value store + events interface used by the platform."""

    # Cache indices (strict-hash match)
    def set_step_cache_record(
        self,
        process_name: str,
        step_name: str,
        input_hash: str,
        config_hash: str,
        function_hash: str | None,
        record: dict[str, Any],
        ttl_seconds: int | None = None,
    ) -> None: ...

    def get_step_cache_path(
        self,
        process_name: str,
        step_name: str,
        input_hash: str | None,
        config_hash: str | None,
        function_hash: str | None,
    ) -> str | None: ...

    def get_step_cache_record(
        self,
        process_name: str,
        step_name: str,
        input_hash: str | None,
        config_hash: str | None,
        function_hash: str | None,
    ) -> dict[str, Any] | None: ...

    def set_process_cache_record(
        self,
        process_name: str,
        input_hash: str,
        config_hash: str,
        function_hash: str | None,
        record: dict[str, Any],
        ttl_seconds: int | None = None,
    ) -> None: ...

    def get_process_cache_path(
        self,
        process_name: str,
        input_hash: str | None,
        config_hash: str | None,
        function_hash: str | None,
    ) -> str | None: ...

    def get_process_cache_record(
        self,
        process_name: str,
        input_hash: str | None,
        config_hash: str | None,
        function_hash: str | None,
    ) -> dict[str, Any] | None: ...

    # Optional: batched cache lookups (implement when backend supports efficient multi-get)
    def get_process_cache_paths_batch(
        self,
        lookups: list[tuple[str, str | None, str | None, str | None]],
    ) -> dict[str, str | None]: ...

    # Run lifecycle + metrics
    def mark_pipeline_started(self, run_id: str) -> None: ...
    def mark_pipeline_completed(self, run_id: str, success: bool) -> None: ...
    def get_run_status(self, run_id: str) -> str | None: ...

    # Events
    def publish_event(self, event: dict[str, Any]) -> None: ...

    # Per-run step bookkeeping (for resume/get_step_results)
    def record_run_step(self, run_id: str, process_name: str, step_name: str, record: dict[str, Any]) -> None: ...
    def list_run_steps(self, run_id: str) -> dict[str, dict[str, Any]]: ...

    # Stats
    def increment_stat(self, run_id: str, name: str, amount: int = 1) -> None: ...
    def get_pipeline_stats(self, run_id: str) -> dict[str, Any]: ...

    # Charts/artifacts index per run (optional but recommended)
    def record_run_chart_artifacts(self, run_id: str, chart_name: str, artifacts: list[dict[str, Any]]) -> None: ...
    def list_run_charts(self, run_id: str) -> dict[str, Any]: ...
    def copy_run_chart_artifacts(self, from_run_id: str, to_run_id: str, chart_name: str) -> bool: ...

    # Run listing for UI (optional)
    def list_runs(self, limit: int = 100) -> list[str]: ...

    # Probe metrics (keyed by probe_path)
    def save_probe_metrics_by_path(self, run_id: str, probe_path: str, metrics: dict[str, Any]) -> None: ...
    def get_probe_metrics_by_path(self, run_id: str, probe_path: str) -> dict[str, Any]: ...




# -------------------- Object storage protocol --------------------
class ObjectStore(Protocol):
    """Abstraction for binary/object storage backends (e.g., GCS/S3).

    Implementations operate on opaque URIs (e.g., gs://bucket/prefix/key.pkl).
    """

    def put_bytes(self, uri: str, data: bytes, content_type: str | None = None) -> None: ...

    def put_file(self, uri: str, file_path: str, content_type: str | None = None) -> None: ...

    def get_bytes(self, uri: str) -> bytes: ...

    def exists(self, uri: str) -> bool: ...

    def build_uri(self, *parts: str) -> str: ...

