from __future__ import annotations

from typing import Any, Dict, Optional, List, Tuple
import json
import logging
import os
import time
import threading
from contextlib import contextmanager

from ..interfaces.kv_store import KeyValueEventStore
from ..path_utils import encode_probe_path

try:
    from google.cloud import firestore_v1 as firestore  # type: ignore
    from google.cloud import pubsub_v1 as pubsub  # type: ignore
    from google.api_core import exceptions as gax_exceptions  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    firestore = None  # type: ignore
    pubsub = None  # type: ignore
    gax_exceptions = None  # type: ignore


class GCPStore(KeyValueEventStore):
    """GCP Firestore + Pub/Sub implementation of KeyValueEventStore.

    Layout in Firestore (collections/documents):
      - mlops_projects (collection)
        - {project_id} (document)
          - step_indices (collection)
            - {process}:{step}:{ih}:{ch}:{fh} (document)
          - process_indices (collection)
            - {process}:{ih}:{ch}:{fh} (document)
          - runs (collection)
            - {run_id} (document) fields: status, timestamps (start,end), metrics (map), stats (map)
              - steps (collection)
                - {process}.{step} (document) record

    Events are published to Pub/Sub on topic: {topic_name}
      - default topic_name: mlops-projects-{project_id}-events
    """

    def __init__(
        self,
        project_id: str,
        gcp_project: Optional[str] = None,
        topic_name: Optional[str] = None,
        emulator_host: Optional[str] = None,
    ) -> None:
        if firestore is None or pubsub is None:
            raise RuntimeError("google-cloud-firestore/pubsub not installed. Add google-cloud-firestore and google-cloud-pubsub to dependencies.")

        # Record emulator host and support emulator for Firestore if provided
        self._emulator_host = emulator_host
        if self._emulator_host:
            os.environ.setdefault("FIRESTORE_EMULATOR_HOST", self._emulator_host)

        self.project_id = project_id
        self.gcp_project = gcp_project or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.gcp_project:
            # Allow running without real GCP project; attempts will fail but caller can catch
            self.gcp_project = project_id

        self._fs = None
        self._publisher = None
        self._topic_path = None
        self.topic_name = topic_name or f"mlops-projects-{self.project_id}-events"
        # Initialize clients now (driver) so immediate use works; they will be rebuilt lazily on unpickle
        self._init_clients()
        
        # Batch writing support to reduce network overhead
        self._batch_writes: List[Tuple[str, Any, Any]] = []  # (operation, args, kwargs)
        self._batch_mode = False
        
        # Batch PubSub events to reduce thread creation
        self._batch_events: List[Dict[str, Any]] = []
        self._event_batch_size = 50  # Publish events in batches of 50
        self._max_pending_events = 200  # Max events to queue before forcing flush
        self._events_lock = threading.Lock()  # Thread lock for batch_events access
        
        # Logger for batch operations
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def required_env(config: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Return SDK-required env vars based on config (for workers).

        - GOOGLE_APPLICATION_CREDENTIALS if provided by user/global env
        - GOOGLE_CLOUD_PROJECT if set in config
        - FIRESTORE_EMULATOR_HOST if set in config
        """
        envs: Dict[str, str] = {}
        try:
            cfg = dict(config or {})
            creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            if creds:
                envs["GOOGLE_APPLICATION_CREDENTIALS"] = creds
            gproj = cfg.get("gcp_project") or os.environ.get("GOOGLE_CLOUD_PROJECT")
            if gproj:
                envs["GOOGLE_CLOUD_PROJECT"] = str(gproj)
            emu = cfg.get("emulator_host") or os.environ.get("FIRESTORE_EMULATOR_HOST")
            if emu:
                envs["FIRESTORE_EMULATOR_HOST"] = str(emu)
        except Exception:
            pass
        return envs

    def _init_clients(self) -> None:
        """(Re)initialize Firestore and Pub/Sub clients and derived handles."""
        if firestore is None or pubsub is None:
            raise RuntimeError("google-cloud-firestore/pubsub not installed. Add google-cloud-firestore and google-cloud-pubsub to dependencies.")
        # Respect emulator setting if present
        if self._emulator_host:
            os.environ.setdefault("FIRESTORE_EMULATOR_HOST", self._emulator_host)
        self._fs = firestore.Client(project=self.gcp_project)
        self._root = self._fs.collection("mlops_projects").document(self.project_id)
        # Configure PublisherClient with batch settings to reduce thread creation
        # batch_settings controls how many threads are created for batch operations
        batch_settings = pubsub.types.BatchSettings(
            max_bytes=1 * 1024 * 1024,  # 1 MB max batch size
            max_latency=1.0,  # 1 second max latency before flushing
            max_messages=100,  # Max messages per batch
        )
        # publisher_options can limit thread creation
        publisher_options = pubsub.types.PublisherOptions(
            flow_control=pubsub.types.PublishFlowControl(
                message_limit=500,  # Limit pending messages
                byte_limit=5 * 1024 * 1024,  # 5 MB limit
                limit_exceeded_behavior=pubsub.types.LimitExceededBehavior.BLOCK,  # Block instead of creating more threads
            )
        )
        self._publisher = pubsub.PublisherClient(
            batch_settings=batch_settings,
            publisher_options=publisher_options,
        )
        self._topic_path = self._publisher.topic_path(self.gcp_project, self.topic_name)
        try:
            self._publisher.get_topic(request={"topic": self._topic_path})
        except Exception as e:  # pragma: no cover - environment-specific
            try:
                if gax_exceptions and isinstance(e, getattr(gax_exceptions, "NotFound", Exception)):
                    try:
                        self._publisher.create_topic(request={"name": self._topic_path})
                    except Exception:
                        pass
            except Exception:
                pass

    def __getstate__(self) -> Dict[str, Any]:
        """Make the store picklable by excluding live client objects.

        Only persist lightweight configuration; clients are re-created on unpickle.
        """
        return {
            "project_id": self.project_id,
            "gcp_project": self.gcp_project,
            "topic_name": self.topic_name,
            "_emulator_host": getattr(self, "_emulator_host", None),
        }

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.project_id = state.get("project_id")
        self.gcp_project = state.get("gcp_project")
        self.topic_name = state.get("topic_name")
        self._emulator_host = state.get("_emulator_host")
        # Recreate clients on the unpickling side
        self._fs = None
        self._publisher = None
        self._topic_path = None
        # Reinitialize batch collections
        self._batch_writes = []
        self._batch_events = []
        self._batch_mode = False
        self._event_batch_size = 50
        self._max_pending_events = 200
        self._events_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        self._init_clients()

    # -------------------- Batch Writing Support --------------------
    @contextmanager
    def batch_write_context(self):
        """Context manager for batching multiple write operations."""
        self._batch_mode = True
        self._batch_writes.clear()
        try:
            yield self
        finally:
            self._flush_batch_writes()
            self._flush_events()  # Flush PubSub events when batch completes
            self._batch_mode = False
    
    def _flush_batch_writes(self) -> None:
        """Flush all batched write operations to Firestore."""
        if not self._batch_writes:
            return
            
        try:
            batch = self._fs.batch()
            for operation, args, kwargs in self._batch_writes:
                if operation == "set_step_cache_record":
                    process_name, step_name, ih, ch, fh, record = args
                    doc_id = self._step_idx_doc_id(process_name, step_name, ih, ch, fh)
                    doc_ref = self._root.collection("step_indices").document(doc_id)
                    batch.set(doc_ref, record, merge=True)
                elif operation == "set_process_cache_record":
                    process_name, ih, ch, fh, record = args
                    doc_id = self._proc_idx_doc_id(process_name, ih, ch, fh)
                    doc_ref = self._root.collection("process_indices").document(doc_id)
                    batch.set(doc_ref, record, merge=True)
                elif operation == "record_run_step":
                    run_id, process_name, step_name, record = args
                    doc_id = f"{process_name}.{step_name}"
                    run_ref = self._root.collection("runs").document(run_id)
                    step_ref = run_ref.collection("steps").document(doc_id)
                    batch.set(step_ref, record, merge=True)
                    # Touch run document for ordering
                    batch.set(run_ref, {"last_updated": time.time()}, merge=True)
            
            batch.commit()
            self.logger.debug(f"Flushed {len(self._batch_writes)} batched write operations")
        except Exception as e:
            self.logger.warning(f"Batch write flush failed: {e}")
        finally:
            self._batch_writes.clear()

    # -------------------- Helpers --------------------
    def _step_idx_doc_id(self, process_name: str, step_name: str, ih: str, ch: str, fh: Optional[str]) -> str:
        return f"{process_name}:{step_name}:{ih}:{ch}:{fh or 'none'}"

    def _proc_idx_doc_id(self, process_name: str, ih: str, ch: str, fh: Optional[str]) -> str:
        return f"{process_name}:{ih}:{ch}:{fh or 'none'}"

    def _charts_index_doc(self, run_id: str):
        # Compact charts index per run for UI
        return self._root.collection("runs").document(run_id).collection("charts_index").document("index")



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
        doc_id = self._step_idx_doc_id(process_name, step_name, input_hash, config_hash, function_hash)
        payload = dict(record)
        if ttl_seconds:
            try:
                payload["expires_at"] = time.time() + int(ttl_seconds)
            except Exception:
                pass
        
        # Use batching if in batch mode
        if self._batch_mode:
            self._batch_writes.append(("set_step_cache_record", (process_name, step_name, input_hash, config_hash, function_hash, payload), {}))
        else:
            self._root.collection("step_indices").document(doc_id).set(payload, merge=True)

    # Batched variant to coalesce writes for step completion
    def set_step_cache_record_batched(
        self,
        run_id: str,
        process_name: str,
        step_name: str,
        input_hash: str,
        config_hash: str,
        function_hash: Optional[str],
        record: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
    ) -> None:
        batch = self._fs.batch()
        # Step index write
        doc_id = self._step_idx_doc_id(process_name, step_name, input_hash, config_hash, function_hash)
        payload = dict(record)
        if ttl_seconds:
            try:
                payload["expires_at"] = time.time() + int(ttl_seconds)
            except Exception:
                pass
        batch.set(self._root.collection("step_indices").document(doc_id), payload, merge=True)
        batch.commit()

    def get_step_cache_path(
        self,
        process_name: str,
        step_name: str,
        input_hash: Optional[str],
        config_hash: Optional[str],
        function_hash: Optional[str],
    ) -> Optional[str]:
        if not input_hash or not config_hash:
            return None
        doc_id = self._step_idx_doc_id(process_name, step_name, input_hash, config_hash, function_hash)
        snap = self._root.collection("step_indices").document(doc_id).get()
        if not snap.exists:
            return None
        data = snap.to_dict() or {}
        if data.get("status") in ("completed", "cached") and data.get("cache_path"):
            return data["cache_path"]
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
        doc_id = self._step_idx_doc_id(process_name, step_name, input_hash, config_hash, function_hash)
        snap = self._root.collection("step_indices").document(doc_id).get()
        return snap.to_dict() if snap.exists else None

    def set_process_cache_record(
        self,
        process_name: str,
        input_hash: str,
        config_hash: str,
        function_hash: Optional[str],
        record: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
    ) -> None:
        if not input_hash or not config_hash:
            return
        
        doc_id = self._proc_idx_doc_id(process_name, input_hash, config_hash, function_hash)
        payload = dict(record)
        if ttl_seconds:
            try:
                payload["expires_at"] = time.time() + int(ttl_seconds)
            except Exception:
                pass
        
        # Use batching if in batch mode
        if self._batch_mode:
            self._batch_writes.append(("set_process_cache_record", (process_name, input_hash, config_hash, function_hash, payload), {}))
        else:
            self._root.collection("process_indices").document(doc_id).set(payload, merge=True)

    # Batched variant for process completion
    def set_process_cache_record_batched(
        self,
        run_id: str,
        process_name: str,
        input_hash: str,
        config_hash: str,
        function_hash: Optional[str],
        record: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
    ) -> None:
        if not input_hash or not config_hash:
            return
            
        batch = self._fs.batch()
        # Process index write
        doc_id = self._proc_idx_doc_id(process_name, input_hash, config_hash, function_hash)
        payload = dict(record)
        if ttl_seconds:
            try:
                payload["expires_at"] = time.time() + int(ttl_seconds)
            except Exception:
                pass
        batch.set(self._root.collection("process_indices").document(doc_id), payload, merge=True)
        # Optional: include a lightweight run summary touch (last_updated)
        batch.set(
            self._root.collection("runs").document(run_id),
            {"last_updated": time.time()},
            merge=True,
        )
        batch.commit()

    def get_process_cache_path(
        self,
        process_name: str,
        input_hash: Optional[str],
        config_hash: Optional[str],
        function_hash: Optional[str],
    ) -> Optional[str]:
        if not input_hash or not config_hash:
            return None
        
        doc_id = self._proc_idx_doc_id(process_name, input_hash, config_hash, function_hash)
        
        snap = self._root.collection("process_indices").document(doc_id).get()
        if not snap.exists:
            return None
            
        data = snap.to_dict() or {}
        
        # Only accept a hit when status is terminal AND cache_path is present and valid
        # Failed or stale entries without cache_path should be treated as cache misses
        status = data.get("status")
        cache_path = data.get("cache_path")
        
        if status in ("completed", "cached") and cache_path and isinstance(cache_path, str):
            return cache_path
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
        doc_id = self._proc_idx_doc_id(process_name, input_hash, config_hash, function_hash)
        snap = self._root.collection("process_indices").document(doc_id).get()
        return snap.to_dict() if snap.exists else None

    def get_process_cache_paths_batch(
        self,
        lookups: list[tuple[str, Optional[str], Optional[str], Optional[str]]],
    ) -> dict[str, Optional[str]]:
        """Batch get process cache paths via Firestore get_all for fewer RPCs.

        Returns mapping from composite key "process_name|ih|ch|fh" to cache_path (or None).
        """
        # Build document references and composite keys in order
        refs = []
        composite: list[str] = []
        for process_name, ih, ch, fh in lookups or []:
            if not ih or not ch:
                composite.append(f"{process_name}|{ih}|{ch}|{fh or 'none'}")
                refs.append(None)
                continue
            doc_id = self._proc_idx_doc_id(process_name, ih, ch, fh)
            refs.append(self._root.collection("process_indices").document(doc_id))
            composite.append(f"{process_name}|{ih}|{ch}|{fh or 'none'}")

        out: dict[str, Optional[str]] = {}
        # Early return
        if not refs:
            return out
        # Firestore get_all supports filtering out None; maintain ordering by iterating zips
        # Collect snapshots for non-None refs, keep placeholders for None
        snaps_iter = self._fs.get_all([r for r in refs if r is not None])
        snaps = list(snaps_iter)
        # Re-map results back to original order
        snap_idx = 0
        for comp_key, ref in zip(composite, refs):
            if ref is None:
                out[comp_key] = None
                continue
            snap = snaps[snap_idx] if snap_idx < len(snaps) else None
            snap_idx += 1
            if snap is None or not getattr(snap, 'exists', False):
                out[comp_key] = None
                continue
            data = snap.to_dict() or {}
            if data.get("status") in ("completed", "cached") and data.get("cache_path"):
                out[comp_key] = data.get("cache_path")
            else:
                out[comp_key] = None
        return out

    # -------------------- Run lifecycle + metrics --------------------
    def mark_pipeline_started(self, run_id: str) -> None:
        run_ref = self._root.collection("runs").document(run_id)
        run_ref.set({
            "status": "running",
            "timestamps": {"start": time.time(), "end": None},
        }, merge=True)
        self.publish_event({"type": "pipeline.started", "run_id": run_id, "status": "running"})

    def mark_pipeline_completed(self, run_id: str, success: bool) -> None:
        run_ref = self._root.collection("runs").document(run_id)
        run_ref.set({
            "status": "completed" if success else "failed",
            "timestamps": {"end": time.time()},
        }, merge=True)
        self.publish_event({"type": "pipeline.completed", "run_id": run_id, "status": "completed" if success else "failed"})
        # Flush events immediately on pipeline completion to ensure they're sent
        self._flush_events()


    def get_run_status(self, run_id: str) -> Optional[str]:
        try:
            snap = self._root.collection("runs").document(run_id).get()
            if not snap.exists:
                return None
            data = snap.to_dict() or {}
            status = data.get("status")
            return str(status).lower() if status is not None else None
        except Exception:
            return None


    # -------------------- Events --------------------
    def publish_event(self, event: Dict[str, Any]) -> None:
        """Queue event for batch publishing to reduce thread creation.
        
        Events are batched and published when:
        - Batch size reaches _event_batch_size (50)
        - Pending events exceed _max_pending_events (200)
        - flush_events() is called explicitly
        """
        try:
            with self._events_lock:
                self._batch_events.append(event)
                batch_size = len(self._batch_events)
                should_flush = batch_size >= self._max_pending_events or batch_size >= self._event_batch_size
            
            # Flush outside lock to avoid holding lock during I/O
            if should_flush:
                self._flush_events()
        except Exception as e:
            # If batching fails, try immediate publish as fallback
            try:
                data = json.dumps(event, default=str).encode("utf-8")
                self._publisher.publish(self._topic_path, data=data)
            except Exception:
                pass
    
    def _flush_events(self) -> None:
        """Flush batched PubSub events (thread-safe)."""
        # Extract events to publish while holding lock
        events_to_publish = []
        try:
            with self._events_lock:
                if not self._batch_events or not self._publisher:
                    return
                events_to_publish = list(self._batch_events)
                self._batch_events.clear()
        except Exception:
            return
        
        # Publish events outside lock to avoid holding lock during I/O
        if not events_to_publish:
            return
        
        try:
            # Publish all events in batch
            # Add small delay between publishes to avoid overwhelming gRPC's batch manager
            futures = []
            for idx, event in enumerate(events_to_publish):
                try:
                    data = json.dumps(event, default=str).encode("utf-8")
                    # Retry publish on KeyError (gRPC batch operation error)
                    max_retries = 2
                    for attempt in range(max_retries + 1):
                        try:
                            future = self._publisher.publish(self._topic_path, data=data)
                            futures.append(future)
                            break  # Success, exit retry loop
                        except (KeyError, RuntimeError) as e:
                            if attempt < max_retries:
                                # KeyError can happen if gRPC's batch state is corrupted
                                # Retry with a small delay
                                time.sleep(0.01 * (attempt + 1))  # Exponential backoff
                                continue
                            else:
                                # Log but don't fail - individual event loss is acceptable
                                if isinstance(e, KeyError):
                                    self.logger.debug(f"PubSub batch operation error after {max_retries} retries (may be transient): {e}")
                                raise
                    # Small delay between publishes to avoid overwhelming gRPC batch manager
                    # This reduces the chance of KeyError in gRPC's internal threads
                    if idx < len(events_to_publish) - 1:  # Don't delay after last event
                        time.sleep(0.001)  # 1ms delay between publishes
                except Exception as e:
                    # Catch any other exceptions and continue
                    self.logger.debug(f"PubSub publish error (event skipped): {e}")
                    pass
            
            # Wait for all publishes to complete (non-blocking, but ensures they're submitted)
            # This prevents thread exhaustion by not creating excessive background threads
            # Note: We don't wait() on futures to avoid blocking, but the batching helps
            self.logger.debug(f"Flushed {len(events_to_publish)} PubSub events")
        except (KeyError, RuntimeError, Exception) as e:
            # Handle KeyError from gRPC batch operations gracefully
            if isinstance(e, KeyError):
                self.logger.debug(f"PubSub batch flush error (may be transient): {e}")
            else:
                self.logger.warning(f"PubSub event flush failed: {e}")

    # -------------------- Per-run step bookkeeping --------------------
    def record_run_step(self, run_id: str, process_name: str, step_name: str, record: Dict[str, Any]) -> None:
        # Persist per-run step record under runs/{run_id}/steps/{process}.{step}
        try:
            # Use batching if in batch mode
            if self._batch_mode:
                self._batch_writes.append(("record_run_step", (run_id, process_name, step_name, dict(record)), {}))
            else:
                run_ref = self._root.collection("runs").document(run_id)
                doc_id = f"{process_name}.{step_name}"
                run_ref.collection("steps").document(doc_id).set(dict(record), merge=True)
                # Touch run document for ordering
                try:
                    run_ref.set({"last_updated": time.time()}, merge=True)
                except Exception:
                    pass
        except Exception:
            # Best-effort; ignore errors
            return None

    def list_run_steps(self, run_id: str) -> Dict[str, Dict[str, Any]]:
        # Read directly from steps subcollection
        results: Dict[str, Dict[str, Any]] = {}
        steps_ref = self._root.collection("runs").document(run_id).collection("steps")
        for doc in steps_ref.stream():
            results[doc.id] = doc.to_dict() or {}
        return results

    def increment_stat(self, run_id: str, name: str, amount: int = 1) -> None:
        from google.cloud.firestore_v1 import Increment  # type: ignore
        self._root.collection("runs").document(run_id).set({"stats": {name: Increment(amount)}}, merge=True)

    def get_pipeline_stats(self, run_id: str) -> Dict[str, Any]:
        snap = self._root.collection("runs").document(run_id).get()
        if not snap.exists:
            return {}
        data = snap.to_dict() or {}
        return data.get("stats", {})

    # -------------------- Charts index --------------------
    def record_run_chart_artifacts(self, run_id: str, chart_name: str, artifacts: list[dict[str, Any]]) -> None:
        """Record chart artifacts into a compact charts_index document for the run.

        Structure:
          runs/{run_id}/charts_index/index -> {
            charts: {
              <chart_name>: {
                type: "static"|"dynamic",
                items: [ { title, object_path, cache_path, mime_type, size_bytes, created_at } ]
              }
            },
            last_updated: <ts>
          }
        """
        try:
            idx_ref = self._charts_index_doc(run_id)
            # Load existing charts map to avoid overwriting other entries
            existing: Dict[str, Any] = {}
            try:
                snap = idx_ref.get()
                if getattr(snap, 'exists', False):
                    data = snap.to_dict() or {}
                    if isinstance(data.get('charts'), dict):
                        existing = dict(data.get('charts'))
            except Exception:
                existing = {}
            # Determine chart type if present on first artifact
            chart_type = None
            try:
                if artifacts and isinstance(artifacts[0], dict):
                    ctype = artifacts[0].get("chart_type")
                    if isinstance(ctype, str) and ctype.strip():
                        chart_type = ctype.strip().lower()
            except Exception:
                chart_type = None
            existing[chart_name] = {"type": (chart_type or "static"), "items": artifacts}
            payload = {
                "charts": existing,
                "last_updated": time.time(),
            }
            idx_ref.set(payload, merge=True)
        except Exception as e:
            self.logger.debug(
                "Failed to record chart artifacts (run_id=%s, chart_name=%s)",
                run_id,
                chart_name,
                exc_info=True,
            )
            return None

    def list_run_charts(self, run_id: str) -> Dict[str, Any]:
        idx_ref = self._charts_index_doc(run_id)
        snap = idx_ref.get()
        if not snap.exists:
            return {}
        data = snap.to_dict() or {}
        charts = data.get("charts", {})
        # Ensure each entry has {type, items}
        out: Dict[str, Any] = {}
        if isinstance(charts, dict):
            for name, val in charts.items():
                if isinstance(val, dict):
                    ctype = val.get("type") or None
                    items = val.get("items") or []
                    out[name] = {"type": (str(ctype).lower() if isinstance(ctype, str) else "static"), "items": items}
        return out

    def copy_run_chart_artifacts(self, from_run_id: str, to_run_id: str, chart_name: str) -> bool:
        try:
            # Read chart artifacts from source run
            from_idx_ref = self._charts_index_doc(from_run_id)
            from_snap = from_idx_ref.get()
            if not from_snap.exists:
                return False
            
            from_data = from_snap.to_dict() or {}
            from_charts = from_data.get("charts", {})
            
            # Check if the specific chart exists in source
            if chart_name not in from_charts:
                return False
            
            chart_data = from_charts[chart_name]
            if not isinstance(chart_data, dict):
                return False
            
            # Read existing charts from destination run
            to_idx_ref = self._charts_index_doc(to_run_id)
            to_snap = to_idx_ref.get()
            to_data = to_snap.to_dict() if to_snap.exists else {}
            to_charts = to_data.get("charts", {})
            
            # Copy the chart data to destination
            to_charts[chart_name] = chart_data
            
            # Write back to destination run
            to_idx_ref.set({
                "charts": to_charts,
                "last_updated": time.time()
            }, merge=True)
            return True
            
        except Exception:
            self.logger.debug("copy_run_chart_artifacts failed", exc_info=True)
            return False

    # -------------------- Probe metrics --------------------
    def save_probe_metrics_by_path(self, run_id: str, probe_path: str, metrics: Dict[str, Any]) -> None:
        """Store metrics under metric/{run_id}/probes_by_path/{encoded_path}."""
        encoded = encode_probe_path(probe_path)
        metric_ref = (
            self._root.collection("metric").document(run_id).collection("probes_by_path").document(encoded)
        )
        payload = dict(metrics)
        metric_ref.set(payload, merge=True)
        try:
            self.publish_event({
                "type": "probe_metrics.updated",
                "run_id": run_id,
                "probe_path": probe_path,
                "metrics": metrics,
            })
        except Exception:
            pass

    def get_probe_metrics_by_path(self, run_id: str, probe_path: str) -> Dict[str, Any]:
        encoded = encode_probe_path(probe_path)
        ref = self._root.collection("metric").document(run_id).collection("probes_by_path").document(encoded)
        snap = ref.get()
        if not snap.exists:
            return {}
        data = snap.to_dict() or {}
        data.pop("updated_at", None)
        return data


    def list_runs(self, limit: int = 100) -> list[str]:
        """List recent run IDs from Firestore for this project namespace.

        Tries to order by 'last_updated' desc if present; otherwise returns up to `limit` docs.
        """
        try:
            runs_col = self._root.collection("runs")
            try:
                # Prefer ordering by last_updated if available
                docs = list(runs_col.order_by("last_updated", direction=firestore.Query.DESCENDING).limit(limit).stream())  # type: ignore[attr-defined]
            except Exception:
                docs = list(runs_col.limit(limit).stream())
            return [d.id for d in docs]
        except Exception:
            return []


