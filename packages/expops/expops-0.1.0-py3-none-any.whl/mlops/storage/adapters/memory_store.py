from __future__ import annotations

from typing import Any, Dict, Optional
import numbers
import json
import time
from ..interfaces.kv_store import KeyValueEventStore
from ..path_utils import encode_probe_path


class InMemoryStore(KeyValueEventStore):
    """Simple in-memory implementation for dev/tests.
    Not persistent and no real pub/sub; events are appended to a list.
    """

    def __init__(self, project_id: str) -> None:
        self.project_id = project_id
        self._kv: Dict[str, Any] = {}
        self._events: list[Dict[str, Any]] = []

    # Helpers
    def _json_set(self, key: str, value: Dict[str, Any]) -> None:
        self._kv[key] = json.loads(json.dumps(value, default=str))

    def _json_get(self, key: str) -> Optional[Dict[str, Any]]:
        val = self._kv.get(key)
        if val is None:
            return None
        return json.loads(json.dumps(val))

    # Cache indices
    def set_step_cache_record(self, process_name: str, step_name: str, input_hash: str, config_hash: str,
                               function_hash: Optional[str], record: Dict[str, Any], ttl_seconds: Optional[int] = None) -> None:
        key = f"steps:{process_name}:{step_name}:{input_hash}:{config_hash}:{function_hash or 'none'}"
        self._json_set(key, record)

    def get_step_cache_path(self, process_name: str, step_name: str, input_hash: Optional[str], config_hash: Optional[str], function_hash: Optional[str]) -> Optional[str]:
        if not input_hash or not config_hash:
            return None
        key = f"steps:{process_name}:{step_name}:{input_hash}:{config_hash}:{function_hash or 'none'}"
        rec = self._json_get(key)
        if rec and rec.get("status") in ("completed", "cached") and rec.get("cache_path"):
            return rec["cache_path"]
        return None

    def get_step_cache_record(self, process_name: str, step_name: str, input_hash: Optional[str], config_hash: Optional[str], function_hash: Optional[str]) -> Optional[Dict[str, Any]]:
        if not input_hash or not config_hash:
            return None
        key = f"steps:{process_name}:{step_name}:{input_hash}:{config_hash}:{function_hash or 'none'}"
        return self._json_get(key)

    def set_process_cache_record(self, process_name: str, input_hash: str, config_hash: str, function_hash: Optional[str], record: Dict[str, Any], ttl_seconds: Optional[int] = None) -> None:
        key = f"process:{process_name}:{input_hash}:{config_hash}:{function_hash or 'none'}"
        self._json_set(key, record)

    def get_process_cache_path(self, process_name: str, input_hash: Optional[str], config_hash: Optional[str], function_hash: Optional[str]) -> Optional[str]:
        if not input_hash or not config_hash:
            return None
        key = f"process:{process_name}:{input_hash}:{config_hash}:{function_hash or 'none'}"
        rec = self._json_get(key)
        if rec and rec.get("status") in ("completed", "cached") and rec.get("cache_path"):
            return rec["cache_path"]
        return None

    def get_process_cache_record(self, process_name: str, input_hash: Optional[str], config_hash: Optional[str], function_hash: Optional[str]) -> Optional[Dict[str, Any]]:
        if not input_hash or not config_hash:
            return None
        key = f"process:{process_name}:{input_hash}:{config_hash}:{function_hash or 'none'}"
        return self._json_get(key)

    def get_process_cache_paths_batch(self, lookups: list[tuple[str, Optional[str], Optional[str], Optional[str]]]) -> dict[str, Optional[str]]:
        """In-memory batched lookup by iterating local dict; returns composite-key map."""
        out: dict[str, Optional[str]] = {}
        for process_name, ih, ch, fh in lookups or []:
            fhash = (fh or 'none') if (ih and ch) else (fh or 'none')
            comp = f"{process_name}|{ih}|{ch}|{fhash}"
            if not ih or not ch:
                out[comp] = None
                continue
            key = f"process:{process_name}:{ih}:{ch}:{fhash}"
            rec = self._json_get(key)
            if rec and rec.get("status") in ("completed", "cached") and rec.get("cache_path"):
                out[comp] = rec.get("cache_path")
            else:
                out[comp] = None
        return out

    # Run lifecycle + metrics
    def mark_pipeline_started(self, run_id: str) -> None:
        self._kv[f"runs:{run_id}:status"] = "running"
        self._json_set(f"runs:{run_id}:timestamps", {"start": time.time(), "end": None})
        self.publish_event({"type": "pipeline.started", "run_id": run_id, "status": "running"})

    def mark_pipeline_completed(self, run_id: str, success: bool) -> None:
        self._kv[f"runs:{run_id}:status"] = "completed" if success else "failed"
        self._json_set(f"runs:{run_id}:timestamps", {"start": None, "end": time.time()})
        self.publish_event({"type": "pipeline.completed", "run_id": run_id, "status": self._kv[f'runs:{run_id}:status']})


    # Events
    def publish_event(self, event: Dict[str, Any]) -> None:
        self._events.append(json.loads(json.dumps(event, default=str)))

    def get_run_status(self, run_id: str) -> Optional[str]:
        status = self._kv.get(f"runs:{run_id}:status")
        if status is None:
            return None
        if isinstance(status, (bytes, bytearray)):
            try:
                status = status.decode()
            except Exception:
                return None
        return str(status).lower() if isinstance(status, str) else None

    # Per-run step bookkeeping
    def record_run_step(self, run_id: str, process_name: str, step_name: str, record: Dict[str, Any]) -> None:
        self._json_set(f"runs:{run_id}:steps:{process_name}:{step_name}", record)

    def list_run_steps(self, run_id: str) -> Dict[str, Dict[str, Any]]:
        prefix = f"runs:{run_id}:steps:"
        out: Dict[str, Dict[str, Any]] = {}
        for key, val in self._kv.items():
            if isinstance(key, str) and key.startswith(prefix):
                _, _, _, process, step = key.split(":", 4)
                out[f"{process}.{step}"] = self._json_get(key) or {}
        return out

    # Stats
    def increment_stat(self, run_id: str, name: str, amount: int = 1) -> None:
        hkey = f"runs:{run_id}:stats:{name}"
        self._kv[hkey] = int(self._kv.get(hkey, 0)) + amount

    def get_pipeline_stats(self, run_id: str) -> Dict[str, Any]:
        prefix = f"runs:{run_id}:stats:"
        return { key[len(prefix):]: int(val) for key, val in self._kv.items() if isinstance(key, str) and key.startswith(prefix) }

    # Charts index
    def record_run_chart_artifacts(self, run_id: str, chart_name: str, artifacts: list[dict[str, Any]]) -> None:
        idx_key = f"runs:{run_id}:charts:{chart_name}"
        self._json_set(idx_key, {"items": artifacts})

    def list_run_charts(self, run_id: str) -> Dict[str, Any]:
        # Debug trace
        try:
            import logging as _logging
            _logging.getLogger(__name__).info(f"[InMemoryStore] list_run_charts(run_id={run_id})")
        except Exception:
            pass
        prefix = f"runs:{run_id}:charts:"
        out: Dict[str, Any] = {}
        for key, val in self._kv.items():
            if isinstance(key, str) and key.startswith(prefix):
                name = key[len(prefix):]
                data = self._json_get(key) or {}
                items = data.get("items", [])
                # Derive chart type from first item's chart_type if available
                ctype = None
                try:
                    if isinstance(items, list) and items and isinstance(items[0], dict):
                        ctype = items[0].get("chart_type")
                except Exception:
                    ctype = None
                out[name] = {"type": (ctype or "static"), "items": items}
        try:
            import logging as _logging
            _logging.getLogger(__name__).info(f"[InMemoryStore] list_run_charts -> {list(out.keys())}")
        except Exception:
            pass
        return out

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
            from_key = f"runs:{from_run_id}:charts:{chart_name}"
            from_data = self._json_get(from_key)
            
            if not from_data:
                try:
                    import logging as _logging
                    _logging.getLogger(__name__).info(f"[InMemoryStore] copy_run_chart_artifacts: chart {chart_name} not found in run {from_run_id}")
                except Exception:
                    pass
                return False
            
            # Write to destination run
            to_key = f"runs:{to_run_id}:charts:{chart_name}"
            self._json_set(to_key, from_data)
            
            try:
                import logging as _logging
                _logging.getLogger(__name__).info(f"[InMemoryStore] copy_run_chart_artifacts: copied chart {chart_name} from {from_run_id} to {to_run_id}")
            except Exception:
                pass
            
            return True
            
        except Exception as e:
            try:
                import logging as _logging
                _logging.getLogger(__name__).warning(f"[InMemoryStore] copy_run_chart_artifacts failed: {e}")
            except Exception:
                pass
            return False


    def save_probe_metrics_by_path(self, run_id: str, probe_path: str, metrics: Dict[str, Any]) -> None:
        enc = encode_probe_path(probe_path)
        self._json_set(f"metric:{run_id}:probe_path:{enc}", metrics)
        try:
            self.publish_event({"type": "probe_metrics.updated", "run_id": run_id, "probe_path": probe_path, "metrics": metrics})
        except Exception:
            pass

    def get_probe_metrics_by_path(self, run_id: str, probe_path: str) -> Dict[str, Any]:
        enc = encode_probe_path(probe_path)
        return self._json_get(f"metric:{run_id}:probe_path:{enc}") or {}


    # Run listing (for UI)
    def list_runs(self, limit: int = 100) -> list[str]:
        prefix = "runs:"
        ids: list[str] = []
        for key in self._kv.keys():
            if isinstance(key, str) and key.startswith(prefix) and key.endswith(":status"):
                rid = key[len(prefix):-len(":status")]
                ids.append(rid)
        # Return insertion order approximation
        return ids[:limit]


