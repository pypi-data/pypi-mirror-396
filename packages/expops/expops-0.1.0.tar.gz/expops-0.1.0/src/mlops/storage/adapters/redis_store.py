from __future__ import annotations

from typing import Any, Dict, Optional
import json
import os
import time
import numbers

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    redis = None  # type: ignore


from ..interfaces.kv_store import KeyValueEventStore
from ..path_utils import encode_probe_path


class RedisStore(KeyValueEventStore):
    """Lightweight Redis wrapper for pipeline state, cache lookup, metrics, and events.

    Key design:
    - Namespaced keys per project: prefix = f"mlops:projects:{project_id}"
    - Step cache index key (exact-hash match):
      f"{prefix}:steps:{process}:{step}:idx:{input_hash}:{config_hash}:{function_hash or 'none'}" -> JSON(record)
    - Process cache index key (exact-hash match):
      f"{prefix}:process:{process}:idx:{input_hash}:{config_hash}:{function_hash or 'none'}" -> JSON(record)
    - Pipeline execution status:
      f"{prefix}:runs:{run_id}:status" -> "running|completed|failed"
      f"{prefix}:runs:{run_id}:timestamps" -> JSON({start,end})
    - Metrics (optional):
      f"{prefix}:runs:{run_id}:metrics" -> JSON(flat metrics)
    - Events channel:
      channel = f"{prefix}:events"
    """

    def __init__(
        self,
        project_id: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[int] = None,
        password: Optional[str] = None,
        namespace_prefix: str = "mlops:projects",
        connection_timeout: float = 1.0,
    ) -> None:
        if redis is None:
            raise RuntimeError("redis-py not installed. Please add 'redis' to dependencies.")

        self.project_id = project_id
        self.prefix = f"{namespace_prefix}:{project_id}"
        self.channel = f"{self.prefix}:events"

        self.host = host or os.getenv("MLOPS_REDIS_HOST", "127.0.0.1")
        self.port = int(port or os.getenv("MLOPS_REDIS_PORT", "6379"))
        self.db = int(db or os.getenv("MLOPS_REDIS_DB", "0"))
        self.password = password or os.getenv("MLOPS_REDIS_PASSWORD", None)

        self.client = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            socket_connect_timeout=connection_timeout,
        )

        # Eagerly validate connection; fail fast to allow fallback
        self.client.ping()

    @staticmethod
    def required_env(config: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Redis requires no SDK envs, but allow optional host/port/db/password env passthrough."""
        envs: Dict[str, str] = {}
        try:
            for key in ("MLOPS_REDIS_HOST", "MLOPS_REDIS_PORT", "MLOPS_REDIS_DB", "MLOPS_REDIS_PASSWORD"):
                val = os.environ.get(key)
                if val:
                    envs[key] = val
        except Exception:
            pass
        return envs

    # -------------------- Helpers --------------------
    def _json_set(self, key: str, value: Dict[str, Any], ttl_seconds: Optional[int] = None) -> None:
        payload = json.dumps(value, default=str)
        self.client.set(key, payload)
        if ttl_seconds and ttl_seconds > 0:
            self.client.expire(key, ttl_seconds)

    def _json_get(self, key: str) -> Optional[Dict[str, Any]]:
        data = self.client.get(key)
        if not data:
            return None
        try:
            if isinstance(data, (bytes, bytearray)):
                data = data.decode("utf-8")
            return json.loads(data)
        except Exception:
            return None

    # -------------------- Cache indices --------------------
    def set_step_cache_record(
        self,
        process_name: str,
        step_name: str,
        input_hash: str,
        config_hash: str,
        function_hash: Optional[str],
        record: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
    ) -> None:
        fhash = function_hash or "none"
        key = f"{self.prefix}:steps:{process_name}:{step_name}:idx:{input_hash}:{config_hash}:{fhash}"
        self._json_set(key, record, ttl_seconds)

    def get_step_cache_path(
        self,
        process_name: str,
        step_name: str,
        input_hash: Optional[str],
        config_hash: Optional[str],
        function_hash: Optional[str],
    ) -> Optional[str]:
        # Only strict-hash lookups are supported in Redis backend to keep operations O(1)
        if not input_hash or not config_hash:
            return None
        fhash = function_hash or "none"
        key = f"{self.prefix}:steps:{process_name}:{step_name}:idx:{input_hash}:{config_hash}:{fhash}"
        rec = self._json_get(key)
        if not rec:
            return None
        if rec.get("status") in ("completed", "cached") and rec.get("cache_path"):
            return rec["cache_path"]
        return None

    def get_step_cache_record(
        self,
        process_name: str,
        step_name: str,
        input_hash: Optional[str],
        config_hash: Optional[str],
        function_hash: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        if not input_hash or not config_hash:
            return None
        fhash = function_hash or "none"
        key = f"{self.prefix}:steps:{process_name}:{step_name}:idx:{input_hash}:{config_hash}:{fhash}"
        return self._json_get(key)

    def set_process_cache_record(
        self,
        process_name: str,
        input_hash: str,
        config_hash: str,
        function_hash: Optional[str],
        record: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
    ) -> None:
        fhash = function_hash or "none"
        key = f"{self.prefix}:process:{process_name}:idx:{input_hash}:{config_hash}:{fhash}"
        self._json_set(key, record, ttl_seconds)

    def get_process_cache_path(
        self,
        process_name: str,
        input_hash: Optional[str],
        config_hash: Optional[str],
        function_hash: Optional[str],
    ) -> Optional[str]:
        if not input_hash or not config_hash:
            return None
        fhash = function_hash or "none"
        key = f"{self.prefix}:process:{process_name}:idx:{input_hash}:{config_hash}:{fhash}"
        rec = self._json_get(key)
        if not rec:
            return None
        if rec.get("status") in ("completed", "cached") and rec.get("cache_path"):
            return rec["cache_path"]
        return None

    def get_process_cache_record(
        self,
        process_name: str,
        input_hash: Optional[str],
        config_hash: Optional[str],
        function_hash: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        if not input_hash or not config_hash:
            return None
        fhash = function_hash or "none"
        key = f"{self.prefix}:process:{process_name}:idx:{input_hash}:{config_hash}:{fhash}"
        return self._json_get(key)

    def get_process_cache_paths_batch(
        self,
        lookups: list[tuple[str, Optional[str], Optional[str], Optional[str]]],
    ) -> dict[str, Optional[str]]:
        """Batched fetch of process cache paths using MGET where possible.

        Input tuples: (process_name, input_hash, config_hash, function_hash)
        Returns mapping from composite key "process_name|ih|ch|fh" to cache_path (or None).
        """
        # Build keys and index map
        keys: list[str] = []
        composite_keys: list[str] = []
        for process_name, ih, ch, fh in lookups or []:
            if not ih or not ch:
                # Maintain position with a placeholder; will map to None
                composite_keys.append(f"{process_name}|{ih}|{ch}|{fh or 'none'}")
                keys.append("")
                continue
            fhash = fh or "none"
            redis_key = f"{self.prefix}:process:{process_name}:idx:{ih}:{ch}:{fhash}"
            keys.append(redis_key)
            composite_keys.append(f"{process_name}|{ih}|{ch}|{fhash}")

        result: dict[str, Optional[str]] = {}
        if not keys:
            return result
        # Pipeline for efficiency
        pipe = self.client.pipeline(transaction=False)
        for k in keys:
            if k:
                pipe.get(k)
            else:
                # Push a None placeholder to keep ordering
                pipe.execute_command("ECHO", "")
        raw_vals = pipe.execute()

        for comp, raw in zip(composite_keys, raw_vals):
            try:
                # Placeholder case from ECHO
                if isinstance(raw, (bytes, bytearray)):
                    data = raw.decode()
                    # Empty string indicates placeholder => None
                    if data == "":
                        result[comp] = None
                        continue
                elif raw is None:
                    result[comp] = None
                    continue
                # Parse JSON
                val = raw
                if isinstance(val, (bytes, bytearray)):
                    val = val.decode("utf-8")
                rec = json.loads(val) if isinstance(val, str) else None
                if rec and isinstance(rec, dict) and rec.get("status") in ("completed", "cached") and rec.get("cache_path"):
                    result[comp] = rec.get("cache_path")
                else:
                    result[comp] = None
            except Exception:
                result[comp] = None
        return result

    # -------------------- Pipeline status --------------------
    def mark_pipeline_started(self, run_id: str) -> None:
        self.client.set(f"{self.prefix}:runs:{run_id}:status", "running")
        self._json_set(
            f"{self.prefix}:runs:{run_id}:timestamps",
            {"start": time.time(), "end": None},
        )
        self.publish_event({"type": "pipeline.started", "run_id": run_id, "status": "running"})

    def mark_pipeline_completed(self, run_id: str, success: bool) -> None:
        status = "completed" if success else "failed"
        self.client.set(f"{self.prefix}:runs:{run_id}:status", status)
        self._json_set(
            f"{self.prefix}:runs:{run_id}:timestamps",
            {"start": None, "end": time.time()},
        )
        self.publish_event({"type": "pipeline.completed", "run_id": run_id, "status": status})


    def get_run_status(self, run_id: str) -> Optional[str]:
        try:
            val = self.client.get(f"{self.prefix}:runs:{run_id}:status")
            if val is None:
                return None
            if isinstance(val, (bytes, bytearray)):
                val = val.decode()
            return str(val).lower() if isinstance(val, str) else None
        except Exception:
            return None

    # -------------------- Events --------------------
    def publish_event(self, event: Dict[str, Any]) -> None:
        try:
            self.client.publish(self.channel, json.dumps(event, default=str))
        except Exception:
            # Best-effort publishing; do not raise
            pass

    def record_run_step(self, run_id: str, process_name: str, step_name: str, record: Dict[str, Any]) -> None:
        key = f"{self.prefix}:runs:{run_id}:steps:{process_name}:{step_name}"
        self._json_set(key, record)

    def list_run_steps(self, run_id: str) -> Dict[str, Dict[str, Any]]:
        pattern = f"{self.prefix}:runs:{run_id}:steps:*"
        result: Dict[str, Dict[str, Any]] = {}
        for key in self.client.scan_iter(match=pattern):
            data = self._json_get(key.decode() if isinstance(key, bytes) else key)
            if not data:
                continue
            # key format: ...:steps:{process}:{step}
            parts = (key.decode() if isinstance(key, bytes) else key).split(":")
            process = parts[-2]
            step = parts[-1]
            result[f"{process}.{step}"] = data
        return result

    # -------------------- Stats --------------------
    def increment_stat(self, run_id: str, name: str, amount: int = 1) -> None:
        self.client.hincrby(f"{self.prefix}:runs:{run_id}:stats", name, amount)

    def get_pipeline_stats(self, run_id: str) -> Dict[str, Any]:
        stats = self.client.hgetall(f"{self.prefix}:runs:{run_id}:stats")
        parsed = { (k.decode() if isinstance(k, bytes) else k): int(v) for k, v in stats.items() } if stats else {}
        return parsed

    # -------------------- Charts index --------------------
    def record_run_chart_artifacts(self, run_id: str, chart_name: str, artifacts: list[dict[str, Any]]) -> None:
        key = f"{self.prefix}:runs:{run_id}:charts:{chart_name}"
        self._json_set(key, {"items": artifacts})

    def list_run_charts(self, run_id: str) -> Dict[str, Any]:
        try:
            import logging as _logging
            _logging.getLogger(__name__).info(f"[RedisStore] list_run_charts(run_id={run_id})")
        except Exception:
            pass
        pattern = f"{self.prefix}:runs:{run_id}:charts:*"
        result: Dict[str, Any] = {}
        for key in self.client.scan_iter(match=pattern):
            data = self._json_get(key.decode() if isinstance(key, bytes) else key)
            if not data:
                continue
            name = (key.decode() if isinstance(key, bytes) else key).split(":")[-1]
            items = data.get("items", [])
            ctype = None
            try:
                if isinstance(items, list) and items and isinstance(items[0], dict):
                    ctype = items[0].get("chart_type")
            except Exception:
                ctype = None
            result[name] = {"type": (ctype or "static"), "items": items}
        try:
            import logging as _logging
            _logging.getLogger(__name__).info(f"[RedisStore] list_run_charts -> {list(result.keys())}")
        except Exception:
            pass
        return result

    def copy_run_chart_artifacts(self, from_run_id: str, to_run_id: str, chart_name: str) -> bool:
        """Copy chart artifacts from one run to another.
        
        Args:
            from_run_id: Source run ID
            to_run_id: Destination run ID  
            chart_name: Name of the chart to copy
            
        Returns:
            True if copy was successful, False otherwise
        """
        try:
            # Read chart artifacts from source run
            from_key = f"{self.prefix}:runs:{from_run_id}:charts:{chart_name}"
            from_data = self._json_get(from_key)
            
            if not from_data:
                try:
                    import logging as _logging
                    _logging.getLogger(__name__).info(f"[RedisStore] copy_run_chart_artifacts: chart {chart_name} not found in run {from_run_id}")
                except Exception:
                    pass
                return False
            
            # Write to destination run
            to_key = f"{self.prefix}:runs:{to_run_id}:charts:{chart_name}"
            self._json_set(to_key, from_data)
            
            try:
                import logging as _logging
                _logging.getLogger(__name__).info(f"[RedisStore] copy_run_chart_artifacts: copied chart {chart_name} from {from_run_id} to {to_run_id}")
            except Exception:
                pass
            
            return True
            
        except Exception as e:
            try:
                import logging as _logging
                _logging.getLogger(__name__).warning(f"[RedisStore] copy_run_chart_artifacts failed: {e}")
            except Exception:
                pass
            return False


    # -------------------- Probe metrics --------------------
    def save_probe_metrics_by_path(self, run_id: str, probe_path: str, metrics: Dict[str, Any]) -> None:
        enc = encode_probe_path(probe_path)
        self._json_set(f"{self.prefix}:metric:{run_id}:probe_path:{enc}", metrics)
        try:
            self.publish_event({"type": "probe_metrics.updated", "run_id": run_id, "probe_path": probe_path, "metrics": metrics})
        except Exception:
            pass

    def get_probe_metrics_by_path(self, run_id: str, probe_path: str) -> Dict[str, Any]:
        enc = encode_probe_path(probe_path)
        return self._json_get(f"{self.prefix}:metric:{run_id}:probe_path:{enc}") or {}


    # -------------------- Run listing (for UI) --------------------
    def list_runs(self, limit: int = 100) -> list[str]:
        """List recent run IDs by scanning keys for this project namespace.

        Note: Redis has no server-side ordering; we approximate by timestamps key presence.
        """
        try:
            pattern = f"{self.prefix}:runs:*:timestamps"
            run_ids: list[str] = []
            for key in self.client.scan_iter(match=pattern):
                k = key.decode() if isinstance(key, (bytes, bytearray)) else str(key)
                # key format: {prefix}:runs:{run_id}:timestamps
                parts = k.split(":")
                if len(parts) >= 5:
                    run_ids.append(parts[-2])
            # Deduplicate and cap
            seen = set()
            uniq = []
            for rid in run_ids:
                if rid not in seen:
                    seen.add(rid)
                    uniq.append(rid)
            return uniq[:limit]
        except Exception:
            return []


