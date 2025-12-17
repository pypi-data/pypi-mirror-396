from typing import Dict, List, Optional, Any
import json
import hashlib
import io
from pathlib import Path
from datetime import datetime
import logging
from dataclasses import dataclass
import numpy as np
import joblib
import time
import inspect
import ast

from mlops.storage.interfaces.kv_store import KeyValueEventStore, ObjectStore
from mlops.storage.path_utils import decode_probe_path


@dataclass
class StepExecutionResult:
	"""Result of executing a single step."""
	step_name: str
	success: bool
	result: Optional[Dict[str, Any]] = None
	error: Optional[str] = None
	execution_time: float = 0.0
	timestamp: str = ""

@dataclass
class ProcessExecutionResult:
	"""Result of executing a single process."""
	process_name: str
	success: bool
	result: Optional[Dict[str, Any]] = None
	error: Optional[str] = None
	execution_time: float = 0.0
	timestamp: str = ""


class StepStateManager:
	"""State manager for step-based pipeline execution with caching."""
	
	def __init__(self, cache_dir: Path, kv_store: KeyValueEventStore, logger: Optional[logging.Logger] = None,
		cache_ttl_hours: Optional[int] = None, object_store: Optional[ObjectStore] = None,
		object_prefix: Optional[str] = None):
		self.logger = logger or logging.getLogger(__name__)
		self.cache_dir = cache_dir
		self.cache_dir.mkdir(parents=True, exist_ok=True)
		
		self.kv_store = kv_store
		self.redis_ttl_seconds = int((cache_ttl_hours or 24) * 3600)
		self.object_store = object_store
		self.object_prefix = object_prefix.strip("/") if isinstance(object_prefix, str) else None

	def _safe_proc(self, name: Optional[str]) -> str:
		"""Return a filesystem-safe process identifier."""
		return (name or 'no_process').replace('/', '_')

	def _stable_step_filename(
		self,
		process_name: Optional[str],
		step_name: str,
		input_hash: Optional[str],
		config_hash: Optional[str],
		function_hash: Optional[str],
	) -> Optional[str]:
		if not input_hash or not config_hash:
			return None
		return f"stable_{self._safe_proc(process_name)}_{step_name}_{input_hash}_{config_hash}_{(function_hash or 'none')}.pkl"

	def _stable_process_filename(
		self,
		process_name: str,
		input_hash: Optional[str],
		config_hash: Optional[str],
		function_hash: Optional[str],
	) -> Optional[str]:
		if not input_hash or not config_hash:
			return None
		return f"stable_process__{self._safe_proc(process_name)}_{input_hash}_{config_hash}_{(function_hash or 'none')}.pkl"

	def _build_object_uri(self, filename: str) -> str:
		"""Build an object store URI honoring the optional prefix."""
		return self.object_store.build_uri(*(filter(None, [self.object_prefix, filename])))

	def _format_probe_path(
		self,
		process_name: Optional[str],
		step_name: Optional[str],
		input_hash: Optional[str] = None,
		config_hash: Optional[str] = None,
		function_hash: Optional[str] = None,
	) -> str:
		"""Clean, human-readable path string for charts.

		Returns simple process or process/step paths without hash suffixes.
		Since metrics are now cached directly, we don't need hash disambiguation.
		"""
		if step_name is None:
			# Process-level path
			return str(process_name or "no_process")
		else:
			# Step-level path
			return f"{process_name or 'no_process'}/{step_name}"

	def _append_probe_metrics(self, run_id: str, probe_id: str, new_metrics: Dict[str, Any], path_key: str, step: int = 0) -> None:
		"""Append numeric metrics as step-indexed dictionaries under metric/{run_id}/probes/{probe_id}.

		New behavior (MLflow-style):
		- Numeric values -> stored as {step_number: value} dictionaries
		- Non-numeric values -> store last snapshot under a separate map
		- step=0 is reserved for auto-logged metrics (from process/step returns)
		- step>=1 for manual log_metric() calls
		"""
		try:
			try:
				self.logger.info(f"[Metrics] Append begin -> run_id={run_id}, path_key={path_key}, step={step}, keys={list((new_metrics or {}).keys())}")
			except Exception:
				pass
			# Attempt to read existing metrics for this probe and append
			existing = {}
			try:
				existing = self.kv_store.get_probe_metrics_by_path(run_id, path_key) or {}
			except Exception:
				existing = {}
			updated: Dict[str, Any] = dict(existing) if isinstance(existing, dict) else {}
			def _to_firestore_safe(obj: Any) -> Any:
				"""Convert values to Firestore-safe types.
				- Dict keys must be strings
				- Convert numpy scalars to native Python
				- Recurse through lists/tuples/dicts
				"""
				try:
					import numpy as _np  # type: ignore
				except Exception:
					_np = None  # type: ignore
				# Primitive JSON-safe types
				if obj is None or isinstance(obj, (bool, int, float, str)):
					return obj
				# Numpy scalar types -> Python native
				if _np is not None and isinstance(obj, (_np.integer, _np.floating)):
					try:
						return float(obj) if isinstance(obj, _np.floating) else int(obj)
					except Exception:
						return obj.item()  # type: ignore[attr-defined]
				# Lists/Tuples -> list of safe
				if isinstance(obj, (list, tuple)):
					return [_to_firestore_safe(x) for x in obj]
				# Dicts -> string keys and safe values
				if isinstance(obj, dict):
					out = {}
					for k, v in obj.items():
						try:
							out[str(k)] = _to_firestore_safe(v)
						except Exception:
							# Best-effort: stringify both key and value
							out[str(k)] = str(v)
					return out
				# Fallback: stringify
				try:
					return str(obj)
				except Exception:
					return obj

			for mname, mval in (new_metrics or {}).items():
				try:
					if isinstance(mval, (int, float)):
						# Get existing metric dict (or create new one)
						metric_dict = updated.get(mname) or {}
						# Handle legacy list format - convert to dict
						if isinstance(metric_dict, list):
							# Convert old list format to dict (use indices as steps)
							# IMPORTANT: Keys must be strings for Firestore compatibility
							metric_dict = {str(i): v for i, v in enumerate(metric_dict)}
						elif not isinstance(metric_dict, dict):
							metric_dict = {}
						# Add new value at specified step
						# IMPORTANT: Convert step to string for Firestore compatibility
						metric_dict[str(step)] = float(mval)
						updated[mname] = metric_dict
					else:
						# Store non-numeric snapshot directly under the metric name
						# Ensure payload is Firestore-safe (string keys, JSON-serializable)
						safe_val = _to_firestore_safe(mval)
						updated[mname] = safe_val
				except Exception:
					continue
			try:
				self.logger.info(f"[Metrics] Saving metrics -> run_id={run_id}, path_key={path_key}, keys={list(updated.keys())}")
			except Exception:
				pass
			self.kv_store.save_probe_metrics_by_path(run_id, path_key, updated)
		except Exception as e:
			self.logger.warning(f"Failed to append probe metrics for {probe_id}: {e}")

	def log_metric(self, run_id: str, process_name: Optional[str], step_name: Optional[str], 
		metric_name: str, value: Any, step: Optional[int] = None) -> None:
		"""Manually log a metric with a step number (MLflow-style).
		
		Args:
			run_id: Current run ID
			process_name: Process name (None for process-level metrics)
			step_name: Step name (None for process-level metrics)
			metric_name: Name of the metric
			value: Metric value
			step: Step number (if None, auto-increments from the largest existing step)
		"""
		try:
			# Compute path for this process/step
			path_key = self._format_probe_path(process_name, step_name)
			
			# Get existing metrics to determine next step if needed
			if step is None:
				existing = self.kv_store.get_probe_metrics_by_path(run_id, path_key) or {}
				metric_dict = existing.get(metric_name)
				if isinstance(metric_dict, dict) and metric_dict:
					try:
						max_step = max(int(k) for k in metric_dict.keys())
						step = max_step + 1
					except (ValueError, TypeError):
						step = 1
				else:
					# No existing data, start at 1
					step = 1
			
			# Log the metric
			self._append_probe_metrics(run_id, path_key, {metric_name: value}, path_key, step=step)
		except Exception as e:
			self.logger.warning(f"Failed to log metric {metric_name}: {e}")
		
	def _get_cache_path(self, run_id: str, step_name: str, process_name: Optional[str] = None) -> Path:
		# Include process_name to avoid collisions across processes
		safe_proc = (process_name or "no_process").replace("/", "_")
		return self.cache_dir / f"{run_id}_{safe_proc}_{step_name}.pkl"

	def _get_process_cache_path(self, run_id: str, process_name: str) -> Path:
		safe_proc = (process_name or "no_process").replace("/", "_")
		return self.cache_dir / f"{run_id}__process__{safe_proc}.pkl"

	def _get_stable_step_cache_path(
		self,
		step_name: str,
		process_name: Optional[str],
		input_hash: Optional[str],
		config_hash: Optional[str],
		function_hash: Optional[str],
	) -> Optional[Path]:
		"""Deterministic, cross-run cache file path for a step based on hashes.

		Returns None if required hashes are missing.
		"""
		if not input_hash or not config_hash:
			return None
		safe_proc = (process_name or "no_process").replace("/", "_")
		fhash = function_hash or "none"
		return self.cache_dir / f"stable_{safe_proc}_{step_name}_{input_hash}_{config_hash}_{fhash}.pkl"

	def _get_stable_process_cache_path(
		self,
		process_name: str,
		input_hash: Optional[str],
		config_hash: Optional[str],
		function_hash: Optional[str],
	) -> Optional[Path]:
		"""Deterministic, cross-run cache file path for a process based on hashes.

		Returns None if required hashes are missing.
		"""
		if not input_hash or not config_hash:
			return None
		safe_proc = (process_name or "no_process").replace("/", "_")
		fhash = function_hash or "none"
		return self.cache_dir / f"stable_process__{safe_proc}_{input_hash}_{config_hash}_{fhash}.pkl"
	
	def _compute_hash(self, obj: Any) -> str:
		"""Compute cryptographically secure SHA-256 hash of any object.

		Uses canonical JSON serialization with custom handling for common non-JSON
		types to ensure determinism and minimize collision risk.
		"""
		try:
			def _to_canonical(o: Any) -> Any:
				# Primitive JSON types pass through
				if o is None or isinstance(o, (str, int, float, bool)):
					return o
				# Paths -> string
				if isinstance(o, Path):
					return str(o)
				# Datetime -> ISO8601
				if isinstance(o, datetime):
					return {"__datetime__": True, "iso": o.isoformat()}
				# Bytes-like -> SHA-256 digest to avoid bloating payloads
				if isinstance(o, (bytes, bytearray, memoryview)):
					bh = hashlib.sha256()
					bh.update(bytes(o))
					return {"__bytes__": True, "sha256": bh.hexdigest()}
				# NumPy arrays -> digest over shape|dtype|data
				if isinstance(o, np.ndarray):
					import os as _os
					_prev_omp = _os.environ.get('OMP_NUM_THREADS')
					try:
						_os.environ['OMP_NUM_THREADS'] = '1'
						ah = hashlib.sha256()
						ah.update(b"ndarray|")
						ah.update(str(o.shape).encode("utf-8"))
						ah.update(b"|")
						ah.update(str(o.dtype).encode("utf-8"))
						ah.update(b"|")
						ah.update(o.tobytes())
						return {"__ndarray__": True, "sha256": ah.hexdigest()}
					finally:
						if _prev_omp is not None:
							_os.environ['OMP_NUM_THREADS'] = _prev_omp
						else:
							_os.environ.pop('OMP_NUM_THREADS', None)
				# Mappings -> dict with stringified keys, recursively canonicalized, sorted by key
				if isinstance(o, dict):
					return {str(k): _to_canonical(v) for k, v in sorted(o.items(), key=lambda kv: str(kv[0]))}
				# Sequences -> list of canonicalized items
				if isinstance(o, (list, tuple)):
					return [_to_canonical(x) for x in o]
				# Sets -> sorted list to make order deterministic
				if isinstance(o, (set, frozenset)):
					return sorted([_to_canonical(x) for x in o], key=lambda x: json.dumps(x, sort_keys=True, separators=(",", ":")))
				# Fallback: use repr for a stable textual form
				return {"__repr__": True, "type": type(o).__name__, "value": repr(o)}

			canonical = _to_canonical(obj)
			payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
			return hashlib.sha256(payload).hexdigest()
		except Exception as e:
			self.logger.warning(f"Failed to compute hash for {type(obj)}: {e}")
			return hashlib.sha256(f"{type(obj).__name__}:{datetime.now()}".encode()).hexdigest()
	
	def _compute_function_hash(self, func: callable) -> str:
		"""Compute hash of a function's source code and signature only.
		"""
		try:
			try:
				source = inspect.getsource(func)
			except (OSError, TypeError):
				source = f"{func.__module__}.{func.__qualname__}" if hasattr(func, '__qualname__') else str(func)
			
			try:
				sig = str(inspect.signature(func))
			except (ValueError, TypeError):
				sig = ""
			
			try:
				tree = ast.parse(source)
				normalized = ast.dump(tree)
			except:
				normalized = ' '.join(source.split())
			
			return hashlib.sha256(f"{normalized}|{sig}".encode()).hexdigest()
			
		except Exception as e:
			self.logger.warning(f"Failed to compute function hash for {func}: {e}")
			# Fallback hash based on function name
			return hashlib.sha256(str(func).encode()).hexdigest()
	
	def start_pipeline_execution(self, run_id: str, config: Dict[str, Any], cache_enabled: bool = True) -> None:
		"""Record pipeline start."""
		try:
			self.kv_store.mark_pipeline_started(run_id)
		except Exception as e:
			self.logger.warning(f"kv_store pipeline start failed: {e}")
		
	def record_step_started(
		self,
		run_id: str,
		process_name: Optional[str],
		step_name: str,
	) -> None:
		"""Record that a step has started running for the given run.

		Writes a per-run step record so the web UI can show start time and live elapsed.
		"""
		try:
			record = {
				"status": "running",
				"started_at": time.time(),
				"execution_time": 0.0,  # Initialize to 0, will be updated on completion
				"step_name": step_name,
				"process_name": process_name or "no_process",
			}
			self.kv_store.record_run_step(run_id, process_name or "no_process", step_name, record)
			self.kv_store.publish_event({
				"type": "step.started",
				"process": process_name or "no_process",
				"step": step_name,
				"status": "running",
			})
		except Exception as e:
			self.logger.warning(f"kv_store step started record failed: {e}")

	def record_process_started(
		self,
		run_id: str,
		process_name: str,
		input_hash: Optional[str] = None,
		config_hash: Optional[str] = None,
		function_hash: Optional[str] = None,
		started_at: Optional[float] = None,
		enable_logging: bool = True,
	) -> None:
		"""Record that a process has started running for the given run.

		Writes a per-run process record under the special step name "__process__" to
		allow the web UI to display start time and live elapsed. If strict hashes are
		available, best-effort mark the process index as running as well.
		"""
		try:
			# Use provided started_at (captured at timing start) if available
			_started = float(started_at) if isinstance(started_at, (int, float)) else time.time()
			record = {
				"status": "running",
				"started_at": _started,
				"execution_time": 0.0,  # Initialize to 0, will be updated on completion
				"process_name": process_name,
			}
			# Per-run process record for UI
			try:
				self.kv_store.record_run_step(run_id, process_name, "__process__", dict(record))
			except Exception:
				pass
			# Best-effort: reflect running state in process index when hashes available
			if input_hash and config_hash:
				try:
					# Avoid overriding an existing terminal cache record that already has a cache_path
					existing = self.kv_store.get_process_cache_record(
						process_name,
						input_hash or "",
						config_hash or "",
						function_hash or None,
					)
					should_write_running = not (isinstance(existing, dict) and existing.get("status") in ("completed", "cached") and existing.get("cache_path"))
					if should_write_running:
						if hasattr(self.kv_store, "set_process_cache_record_batched") and callable(getattr(self.kv_store, "set_process_cache_record_batched")):
							getattr(self.kv_store, "set_process_cache_record_batched")(  # type: ignore
								run_id,
								process_name,
								input_hash or "",
								config_hash or "",
								function_hash or None,
								record,
								ttl_seconds=self.redis_ttl_seconds,
							)
						else:
							self.kv_store.set_process_cache_record(
								process_name,
								input_hash or "",
								config_hash or "",
								function_hash or None,
								record,
								ttl_seconds=self.redis_ttl_seconds,
							)
				except Exception:
					pass
			self.kv_store.publish_event({
				"type": "process.started",
				"process": process_name,
				"status": "running",
			})
		except Exception as e:
			self.logger.warning(f"kv_store process started record failed: {e}")
		
	def record_step_completion(
		self,
		run_id: str,
		step_result: StepExecutionResult,
		input_hash: Optional[str] = None,
		config_hash: Optional[str] = None,
		function_name: Optional[str] = None,
		function_hash: Optional[str] = None,
		was_cached: bool = False,
		process_name: Optional[str] = None,
		enable_logging: bool = True,
		cached_run_id: Optional[str] = None,
		cached_started_at: Optional[float] = None,
		cached_ended_at: Optional[float] = None,
		cached_execution_time: Optional[float] = None,
	) -> None:
		"""Record step completion with hash-based caching including function hash and process_name.
		
		Args:
			enable_logging: If True, create probes for metrics. If False, skip probe creation.
		"""
		step_name = step_result.step_name
		cache_path = None

		if step_result.success and step_result.result and not was_cached:
			try:
				# Prefer object store when configured; otherwise cache locally (absolute path)
				if self.object_store:
					import tempfile, os as _os
					# Write to a temporary file to avoid large in-memory buffers
					with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as _tmpf:
						tmp_path = _tmpf.name
					try:
						joblib.dump(step_result.result, tmp_path)
						fname = self._stable_step_filename(process_name, step_name, input_hash, config_hash, function_hash) \
							if (input_hash and config_hash) else f"{run_id}_{self._safe_proc(process_name)}_{step_name}.pkl"
						cache_uri = self._build_object_uri(fname)
						if hasattr(self.object_store, 'put_file'):
							self.object_store.put_file(cache_uri, tmp_path, content_type="application/octet-stream")
						else:
							with open(tmp_path, 'rb') as _f:
								self.object_store.put_bytes(cache_uri, _f.read(), content_type="application/octet-stream")
						cache_path = cache_uri
					finally:
						try:
							_os.remove(tmp_path)
						except Exception:
							pass
				else:
					# Local filesystem fallback with absolute path stored in KV
					if input_hash and config_hash:
						local_path = self._get_stable_step_cache_path(step_name, process_name, input_hash, config_hash, function_hash)
					else:
						local_path = self._get_cache_path(run_id, step_name, process_name)
					if local_path is not None:
						local_path.parent.mkdir(parents=True, exist_ok=True)
						joblib.dump(step_result.result, local_path)
						cache_path = str(local_path.resolve())
			except Exception as e:
				self.logger.warning(f"Failed to cache step {step_name}: {e}")
		
		status = "cached" if was_cached else ("completed" if step_result.success else "failed")
		try:
			# For cached steps, use the original timing from cache
			if was_cached and cached_started_at is not None and cached_ended_at is not None and cached_execution_time is not None:
				record = {
					"status": status,
					"execution_time": cached_execution_time,
					"ended_at": cached_ended_at,
					"cache_path": cache_path,
					"step_name": step_name,
					"process_name": process_name or "no_process",
					"run_id": run_id,
					"started_at": cached_started_at,
					"cached_run_id": cached_run_id,
				}
			else:
				# For non-cached steps, use current run timing
				# Convert ISO timestamp to Unix timestamp for consistency with record_step_started
				timestamp = step_result.timestamp
				if isinstance(timestamp, str):
					try:
						from datetime import datetime
						timestamp = datetime.fromisoformat(timestamp).timestamp()
					except Exception:
						timestamp = time.time()
				elif not isinstance(timestamp, (int, float)):
					timestamp = time.time()
				# Preserve started_at if a prior running record exists so UI can compute duration
				started_at_existing = None
				try:
					prev = self.kv_store.list_run_steps(run_id)
					if isinstance(prev, dict):
						key = f"{process_name or 'no_process'}.{step_name}"
						started_at_existing = (prev.get(key) or {}).get("started_at")
				except Exception:
					started_at_existing = None
				
				record = {
					"status": status,
					"execution_time": step_result.execution_time,
					"ended_at": timestamp,
					"cache_path": cache_path,
					"step_name": step_name,
					"process_name": process_name or "no_process",
					"run_id": run_id,
				}
				# If we have an existing started_at, include it; otherwise derive from ended_at - execution_time
				try:
					if started_at_existing is not None:
						record["started_at"] = started_at_existing
					elif isinstance(step_result.execution_time, (int, float)) and step_result.execution_time >= 0:
						record["started_at"] = float(record["ended_at"]) - float(step_result.execution_time)
				except Exception:
					pass
			# Note: Metrics are no longer auto-logged from step results.
			# Users must explicitly call log_metric() to log metrics.
			# No probe_id bookkeeping needed.
			# Prefer batched write when backend supports it (e.g., Firestore)
			if hasattr(self.kv_store, "set_step_cache_record_batched") and callable(getattr(self.kv_store, "set_step_cache_record_batched")):
				try:
					getattr(self.kv_store, "set_step_cache_record_batched")(  # type: ignore
						run_id,
						process_name or "no_process",
						step_name,
						input_hash or "",
						config_hash or "",
						function_hash or None,
						record,
						ttl_seconds=self.redis_ttl_seconds,
					)
				except Exception:
					# Fallback to non-batched on error
					self.kv_store.set_step_cache_record(
						process_name or "no_process",
						step_name,
						input_hash or "",
						config_hash or "",
						function_hash or None,
						record,
						ttl_seconds=self.redis_ttl_seconds,
					)
			else:
				self.kv_store.set_step_cache_record(
					process_name or "no_process",
					step_name,
					input_hash or "",
					config_hash or "",
					function_hash or None,
					record,
					ttl_seconds=self.redis_ttl_seconds,
				)
			# Stats for cache hit/miss
			if status == "cached":
				self.kv_store.increment_stat(run_id, "cache_hit_count", 1)
			# Per-run step record for UI
			try:
				self.kv_store.record_run_step(run_id, process_name or "no_process", step_name, dict(record))
			except Exception as record_err:
				self.logger.warning(f"❌ Failed to record step completion for {step_name} in process {process_name} run {run_id}: {record_err}")
				import traceback
				self.logger.debug(f"Traceback: {traceback.format_exc()}")
			self.kv_store.publish_event({
				"type": "step.completed",
				"process": process_name or "no_process",
				"step": step_name,
				"status": status,
			})
		except Exception as e:
			self.logger.warning(f"kv_store step index/event failed: {e}")
	
	def record_process_completion(
		self,
		run_id: str,
		process_result: ProcessExecutionResult,
		input_hash: Optional[str] = None,
		config_hash: Optional[str] = None,
		function_hash: Optional[str] = None,
		was_cached: bool = False,
		enable_logging: bool = True,
		cached_run_id: Optional[str] = None,
		cached_started_at: Optional[float] = None,
		cached_ended_at: Optional[float] = None,
		cached_execution_time: Optional[float] = None,
	) -> None:
		"""Record process completion and cache combined process result.
		
		Args:
			enable_logging: If True, create probes for metrics. If False, skip probe creation.
			cached_run_id: Run ID of the original cached execution (for was_cached=True)
			cached_started_at: Start timestamp from original cached execution
			cached_ended_at: End timestamp from original cached execution
			cached_execution_time: Execution time from original cached execution
		"""
		process_name = process_result.process_name
		cache_path = None
		
		# When we have a fresh result (not from cache) we persist the artifact.
		if process_result.success and process_result.result and not was_cached:
			try:
				if self.object_store:
					import tempfile, os as _os
					# Write to a temporary file to avoid large in-memory buffers
					with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as _tmpf:
						tmp_path = _tmpf.name
					try:
						joblib.dump(process_result.result, tmp_path)
						fname = self._stable_process_filename(process_name, input_hash, config_hash, function_hash) \
							if (input_hash and config_hash) else f"{run_id}__process__{self._safe_proc(process_name)}.pkl"
						cache_uri = self._build_object_uri(fname)
						if hasattr(self.object_store, 'put_file'):
							self.object_store.put_file(cache_uri, tmp_path, content_type="application/octet-stream")
						else:
							with open(tmp_path, 'rb') as _f:
								self.object_store.put_bytes(cache_uri, _f.read(), content_type="application/octet-stream")
						cache_path = cache_uri
					finally:
						try:
							_os.remove(tmp_path)
						except Exception:
							pass
				else:
					# Local filesystem fallback with absolute path stored in KV
					if input_hash and config_hash:
						local_path = self._get_stable_process_cache_path(process_name, input_hash, config_hash, function_hash)
					else:
						local_path = self._get_process_cache_path(run_id, process_name)
					if local_path is not None:
						local_path.parent.mkdir(parents=True, exist_ok=True)
						joblib.dump(process_result.result, local_path)
						cache_path = str(local_path.resolve())
			except Exception as e:
				self.logger.warning(f"Failed to cache process {process_name}: {e}")
		
		# If we are marking a cached completion, try to preserve the original cache_path
		# so future lookups still return a path. Do not overwrite existing cache_path with null.
		# Also preserve cache_path if result is None (e.g., MemoryError during deserialization)
		# but process succeeded - worker already cached it
		if (was_cached or (process_result.success and not process_result.result)) and (cache_path is None):
			try:
				if hasattr(self, "kv_store") and input_hash and config_hash:
					# Prefer full record to recover cache_path even if status is currently running
					existing_rec = self.kv_store.get_process_cache_record(process_name, input_hash, config_hash, function_hash)
					if isinstance(existing_rec, dict) and existing_rec.get("cache_path"):
						cache_path = existing_rec.get("cache_path")
					else:
						cache_path = self.kv_store.get_process_cache_path(process_name, input_hash, config_hash, function_hash)
			except Exception:
				cache_path = None

		status = "cached" if was_cached else ("completed" if process_result.success else "failed")
		try:
			# For cached processes, use the original timing from the cached metadata
			if was_cached and cached_started_at is not None and cached_ended_at is not None and cached_execution_time is not None:
				record = {
					"status": status,
					"execution_time": cached_execution_time,
					"ended_at": cached_ended_at,
					"process_name": process_name,
					"started_at": cached_started_at,
					"cached_run_id": cached_run_id,
					"cached_started_at": cached_started_at,
					"cached_ended_at": cached_ended_at,
					"cached_execution_time": cached_execution_time,
					"run_id": run_id,
				}
				# Only include cache_path when we actually have one to avoid nulling existing values
				if cache_path:
					record["cache_path"] = cache_path
			else:
				# For non-cached processes, use current run timing
				# Convert ISO timestamp to Unix timestamp for consistency with record_process_started
				timestamp = process_result.timestamp
				if isinstance(timestamp, str):
					try:
						from datetime import datetime
						timestamp = datetime.fromisoformat(timestamp).timestamp()
					except Exception:
						timestamp = time.time()
				elif not isinstance(timestamp, (int, float)):
					timestamp = time.time()
				# Preserve started_at from prior running record, and prefer the earliest ended_at
				started_at_existing = None
				ended_at_existing = None
				try:
					prev = self.kv_store.list_run_steps(run_id)
					if isinstance(prev, dict):
						key = f"{process_name}.__process__"
						_prev_rec = (prev.get(key) or {})
						started_at_existing = _prev_rec.get("started_at")
						ended_at_existing = _prev_rec.get("ended_at")
				except Exception:
					started_at_existing = None
					ended_at_existing = None
				
				record = {
					"status": status,
					"execution_time": process_result.execution_time,
					"ended_at": timestamp,
					"process_name": process_name,
					# Persist this run id on process index for future cache lookups and provenance
					"run_id": run_id,
				}
				# Only include cache_path when we actually have one to avoid nulling existing values
				if cache_path:
					record["cache_path"] = cache_path
				try:
					if started_at_existing is not None:
						record["started_at"] = started_at_existing
					elif isinstance(process_result.execution_time, (int, float)) and process_result.execution_time >= 0:
						record["started_at"] = float(record["ended_at"]) - float(process_result.execution_time)
					# Preserve the earliest ended_at if a prior value exists to avoid late overwrites
					if ended_at_existing is not None:
						try:
							record["ended_at"] = min(float(record["ended_at"]), float(ended_at_existing))
						except Exception:
							pass
				except Exception:
					pass
			try:
				if enable_logging:
					# If this was cached, try to copy ALL metrics from the source run
					# Find another run with the same process hash and copy all its probe metrics
					if was_cached and input_hash and config_hash:
						self.logger.info(f"🔍 [METRICS COPY] Attempting to copy cached metrics for {process_name} (was_cached={was_cached})")
						try:
							from ..storage.adapters.gcp_kv_store import GCPStore
							if isinstance(self.kv_store, GCPStore):
								self.logger.info(f"🔍 [METRICS COPY] GCP store detected, proceeding with metrics copy (path-based)")
								# Scan recent runs and copy metrics from probes_by_path
								try:
									runs_col = self.kv_store._root.collection('runs')
									metric_col = self.kv_store._root.collection('metric')
									run_docs = list(runs_col.limit(10).stream())
									self.logger.info(f"🔍 [METRICS COPY] Query returned {len(run_docs)} runs")
								except Exception as query_err:
									self.logger.warning(f"❌ [METRICS COPY] Failed to query runs: {query_err}")
									run_docs = []
								found_metrics = False
								for run_doc in run_docs:
									try:
										source_run_id = run_doc.id
										if source_run_id == run_id:
											continue
										try:
											docs = list(metric_col.document(source_run_id).collection('probes_by_path').limit(50).stream())
										except Exception:
											docs = []
										for d in docs:
											try:
												source_metrics = d.to_dict() or {}
												if source_metrics:
													enc_id = getattr(d, 'id', '')
													try:
														path = decode_probe_path(enc_id)
													except Exception:
														continue
													if not (isinstance(path, str) and (path == process_name or path.startswith(f"{process_name}/"))):
														continue
													self.kv_store.save_probe_metrics_by_path(run_id, path, source_metrics)
													found_metrics = True
											except Exception:
												continue
										if found_metrics:
											break
									except Exception:
										continue
								if not found_metrics:
									self.logger.warning(f"⚠️ [METRICS COPY] No source metrics found for {process_name}")
							else:
								self.logger.info(f"🔍 [METRICS COPY] Not using GCP store (type={type(self.kv_store).__name__}), skipping metrics copy")
						except Exception as copy_err:
							self.logger.warning(f"❌ [METRICS COPY] Failed to copy metrics for {process_name}: {copy_err}")
							import traceback
							self.logger.warning(f"Traceback: {traceback.format_exc()}")
				# Note: Step-level probes are now created directly by individual steps
				# with clean paths that match chart configurations exactly
			except Exception as e:
				print(f"❌ Exception in process metrics handling: {e}")
				pass
			# Prefer batched write when backend supports it (e.g., Firestore)
			try:
				# Debug: surface the exact key parts used for process_indices completion write
				self.logger.debug(
					f"process_indices[complete] key parts -> process={process_name}, ih={input_hash}, ch={config_hash}, fh={function_hash}"
				)
			except Exception:
				pass
			_should_write_index = (not was_cached) or bool(cache_path)
			if _should_write_index:
				if hasattr(self.kv_store, "set_process_cache_record_batched") and callable(getattr(self.kv_store, "set_process_cache_record_batched")):
					try:
						getattr(self.kv_store, "set_process_cache_record_batched")(  # type: ignore
							run_id,
							process_name,
							input_hash or "",
							config_hash or "",
							function_hash or None,
							record,
							ttl_seconds=self.redis_ttl_seconds,
						)
					except Exception:
						self.kv_store.set_process_cache_record(
							process_name,
							input_hash or "",
							config_hash or "",
							function_hash or None,
							record,
							ttl_seconds=self.redis_ttl_seconds,
						)
				else:
					self.kv_store.set_process_cache_record(
						process_name,
						input_hash or "",
						config_hash or "",
						function_hash or None,
						record,
						ttl_seconds=self.redis_ttl_seconds,
					)
			# Per-run process summary record for UI
			try:
				self.kv_store.record_run_step(run_id, process_name, "__process__", dict(record))
			except Exception as record_err:
				self.logger.warning(f"❌ Failed to record __process__ completion for {process_name} in run {run_id}: {record_err}")
				import traceback
				self.logger.debug(f"Traceback: {traceback.format_exc()}")
			self.kv_store.publish_event({
				"type": "process.completed",
				"process": process_name,
				"status": status,
			})
		except Exception as e:
			self.logger.warning(f"kv_store process index/event failed: {e}")
	
	def can_skip_step(
		self,
		run_id: str,
		step_name: str,
		input_hash: str,
		config_hash: str,
		function_hash: Optional[str] = None,
		process_name: Optional[str] = None,
	) -> bool:
		"""Check if step can be skipped based on hash validation including function hash and process name."""
		if not input_hash or not config_hash:
			return False
		# Fast-path via kv_store exact index only
		try:
			path = self.kv_store.get_step_cache_path(
				process_name or "no_process",
				step_name,
				input_hash,
				config_hash,
				function_hash,
			)
			if path:
				# Support object store URIs and local absolute paths
				if isinstance(path, str) and path.startswith('gs://') and self.object_store:
					try:
						return self.object_store.exists(path)
					except Exception:
						pass
				else:
					try:
						return Path(path).exists()
					except Exception:
						pass
		except Exception:
			pass
		return False
	
	def get_expired_cache_entries(self, step_name: Optional[str] = None) -> List[Dict[str, Any]]:
		"""Get expired cache entries for potential recovery or debugging (removed)."""
		return []

	def restore_expired_cache_entry(self, run_id: str, step_name: str) -> bool:
		"""Restore an expired cache entry back to 'completed' status (removed)."""
		return False
	
	def _cleanup_stale_cache_entry(self, step_name: str, cache_path: str) -> None:
		"""Deprecated no-op (removed)."""
		return None
	
	def get_cached_step_result(
		self,
		run_id: str,
		step_name: str,
		process_name: Optional[str] = None,
		input_hash: Optional[str] = None,
		config_hash: Optional[str] = None,
		function_hash: Optional[str] = None,
	) -> Optional[Dict[str, Any]]:
		"""Get cached step result via kv_store strict-hash lookup.
		
		Only returns a result if the KV index has a valid cache_path entry.
		No fallback to deterministic file paths - cache must be explicitly indexed.
		"""
		cache_path = self.kv_store.get_step_cache_path(
			process_name or "no_process",
			step_name,
			input_hash,
			config_hash,
			function_hash,
		)
		
		loaded = None
		# If index returned a path, load from appropriate backend
		try:
			if cache_path and isinstance(cache_path, str):
				if cache_path.startswith('gs://') and self.object_store:
					data = self.object_store.get_bytes(cache_path)
					loaded = joblib.load(io.BytesIO(data))
				else:
					p = Path(cache_path)
					if p.exists():
						loaded = joblib.load(p)
		except Exception as e:
			self.logger.warning(f"Failed to load cached step result from {cache_path}: {e}")
		
		proc = process_name or "no_process"
		if loaded is not None:
			try:
				self.logger.info(f"[Cache] step hit: {proc}/{step_name}")
			except Exception:
				pass
			return loaded
		else:
			try:
				self.logger.info(f"[Cache] step miss: {proc}/{step_name}")
			except Exception:
				pass
			return None
	
	def get_cached_step_result_with_metadata(
		self,
		run_id: str,
		step_name: str,
		process_name: Optional[str] = None,
		input_hash: Optional[str] = None,
		config_hash: Optional[str] = None,
		function_hash: Optional[str] = None,
	) -> Optional[tuple[Dict[str, Any], str, Dict[str, Any]]]:
		"""Get cached step result with metadata including cached run-id and timing.
		
		Returns: (result, cached_run_id, cached_metadata) or None if not cached.
		"""
		# First check if cache exists
		cache_path = self.kv_store.get_step_cache_path(
			process_name or "no_process",
			step_name,
			input_hash,
			config_hash,
			function_hash,
		)
		
		if not cache_path:
			try:
				self.logger.info(f"[Cache] step miss: {(process_name or 'no_process')}/{step_name}")
			except Exception:
				pass
			return None
		
		# Get the full cache record to extract metadata
		cache_record = self.kv_store.get_step_cache_record(
			process_name or "no_process",
			step_name,
			input_hash,
			config_hash,
			function_hash,
		)
		
		if not cache_record:
			return None
		
		# Load the actual cached result
		try:
			if cache_path and isinstance(cache_path, str):
				if cache_path.startswith('gs://') and self.object_store:
					data = self.object_store.get_bytes(cache_path)
					result = joblib.load(io.BytesIO(data))
				else:
					p = Path(cache_path)
					if p.exists():
						result = joblib.load(p)
					else:
						result = None
			else:
				result = None
		except Exception as e:
			self.logger.warning(f"Failed to load cached step result from {cache_path}: {e}")
			result = None
		
		proc = process_name or "no_process"
		if result is None:
			try:
				self.logger.info(f"[Cache] step miss: {proc}/{step_name}")
			except Exception:
				pass
			return None
		
		# Extract metadata
		# Prefer cached_run_id if it exists (points to original run that executed the step)
		# Otherwise use run_id (this record is from the original execution)
		cached_run_id = cache_record.get("cached_run_id") or cache_record.get("run_id", "unknown")
		cached_metadata = {
			"started_at": cache_record.get("cached_started_at") or cache_record.get("started_at"),
			"ended_at": cache_record.get("cached_ended_at") or cache_record.get("ended_at"),
			"execution_time": cache_record.get("cached_execution_time") or cache_record.get("execution_time"),
			"run_id": cached_run_id,
		}
		
		return (result, cached_run_id, cached_metadata)
	
	def get_cached_process_result(
		self,
		process_name: str,
		input_hash: Optional[str] = None,
		config_hash: Optional[str] = None,
		function_hash: Optional[str] = None,
		run_id: Optional[str] = None,
	) -> Optional[Dict[str, Any]]:
		"""Get cached process result via kv_store strict-hash lookup.

		Only returns a result if the KV index has a valid cache_path entry.
		No fallback to deterministic file paths - cache must be explicitly indexed.
		"""
		cache_path = self.kv_store.get_process_cache_path(
			process_name,
			input_hash,
			config_hash,
			function_hash,
		)
		
		loaded = None
		load_error = None
		# If index returned a path, load from appropriate backend
		try:
			if cache_path and isinstance(cache_path, str):
				if cache_path.startswith('gs://') and self.object_store:
					data = self.object_store.get_bytes(cache_path)
					loaded = joblib.load(io.BytesIO(data))
				else:
					p = Path(cache_path)
					if p.exists():
						loaded = joblib.load(p)
					else:
						load_error = f"Cache file not found at {cache_path}"
			else:
				load_error = "Invalid cache path format"
		except Exception as e:
			load_error = str(e)
			self.logger.warning(f"Failed to load cached result for {process_name}: {e}")
		
		if loaded is not None:
			try:
				self.logger.info(f"[Cache] process hit: {process_name}")
			except Exception:
				pass
			return loaded
		else:
			# Cache entry exists but file couldn't be loaded - treat as miss
			if load_error:
				self.logger.warning(f"⚠️ [CACHE] Stale cache entry for {process_name}: cache index exists but file load failed ({load_error}). Treating as cache miss.")
			try:
				self.logger.info(f"[Cache] process miss: {process_name}")
			except Exception:
				pass
			return None

	def get_cached_process_result_with_metadata(
		self,
		process_name: str,
		input_hash: Optional[str] = None,
		config_hash: Optional[str] = None,
		function_hash: Optional[str] = None,
		run_id: Optional[str] = None,
	) -> Optional[tuple[Dict[str, Any], str, Dict[str, Any]]]:
		"""Get cached process result with metadata including cached run-id and timing.
		
		Returns: (result, cached_run_id, cached_metadata) or None if not cached.
		
		If cache path exists but file cannot be loaded, logs a warning and returns None
		to allow fallback to execution. The stale cache entry remains in the index
		but won't be used until it's overwritten by a successful execution.
		"""
		# First check if cache exists
		cache_path = self.kv_store.get_process_cache_path(
			process_name,
			input_hash,
			config_hash,
			function_hash,
		)
		
		if not cache_path:
			try:
				self.logger.info(f"[Cache] process miss: {process_name}")
			except Exception:
				pass
			return None
		
		# Get the full cache record to extract metadata
		cache_record = self.kv_store.get_process_cache_record(
			process_name,
			input_hash,
			config_hash,
			function_hash,
		)
		
		if not cache_record:
			return None
		
		# Load the actual cached result
		load_error = None
		try:
			if cache_path and isinstance(cache_path, str):
				if cache_path.startswith('gs://') and self.object_store:
					data = self.object_store.get_bytes(cache_path)
					result = joblib.load(io.BytesIO(data))
				else:
					p = Path(cache_path)
					if p.exists():
						result = joblib.load(p)
					else:
						result = None
						load_error = f"Cache file not found at {cache_path}"
			else:
				result = None
				load_error = "Invalid cache path format"
		except Exception as e:
			load_error = str(e)
			result = None
		
		# Extract metadata
		# Prefer cached_run_id if it exists (points to original run that executed the process)
		# Otherwise use run_id (this record is from the original execution)
		cached_run_id = cache_record.get("cached_run_id") or cache_record.get("run_id", "unknown")
		cached_metadata = {
			"started_at": cache_record.get("cached_started_at") or cache_record.get("started_at"),
			"ended_at": cache_record.get("cached_ended_at") or cache_record.get("ended_at"),
			"execution_time": cache_record.get("cached_execution_time") or cache_record.get("execution_time"),
			"run_id": cached_run_id,
		}
		
		if result is not None:
			try:
				self.logger.info(f"[Cache] process hit: {process_name}")
			except Exception:
				pass
			return (result, cached_run_id, cached_metadata)
		else:
			# Cache entry exists but file couldn't be loaded - treat as miss
			# This can happen if cache files were deleted or corrupted
			try:
				if load_error:
					self.logger.warning(f"⚠️ [CACHE] Stale cache entry for {process_name}: cache index exists but file load failed ({load_error}). Treating as cache miss and will re-execute.")
				else:
					self.logger.info(f"[Cache] process miss: {process_name}")
			except Exception:
				pass
			return None

	def load_process_result_from_path(self, cache_path: str) -> Optional[Dict[str, Any]]:
		"""Load a process result dictionary directly from a known cache path or object URI.

		Best-effort; returns None on any failure.
		"""
		try:
			if not cache_path or not isinstance(cache_path, str):
				return None
			if cache_path.startswith('gs://') and self.object_store:
				data = self.object_store.get_bytes(cache_path)
				return joblib.load(io.BytesIO(data))
			p = Path(cache_path)
			if p.exists():
				return joblib.load(p)
		except Exception:
			return None
	
	def get_cache_statistics(self) -> Dict[str, Any]:
		"""Get cache statistics."""
		cache_files = list(self.cache_dir.glob("*.pkl"))
		total_size = sum(f.stat().st_size for f in cache_files if f.exists())
		return {
			'total_cache_files': len(cache_files),
			'total_cache_size_mb': total_size / (1024**2),
			'cache_directory': str(self.cache_dir)
		}
	
	def complete_pipeline_execution(self, run_id: str, success: bool) -> None:
		"""Record pipeline completion."""
		status = "completed" if success else "failed"
		try:
			self.kv_store.mark_pipeline_completed(run_id, success)
		except Exception as e:
			self.logger.warning(f"kv_store pipeline completion failed: {e}")
	
	def get_step_results(self, run_id: str) -> Dict[str, Dict[str, Any]]:
		"""Get all step results for a run."""
		results = {}
		try:
			step_records = self.kv_store.list_run_steps(run_id)
			for key, rec in step_records.items():
				cache_path = rec.get("cache_path")
				if cache_path:
					try:
						if isinstance(cache_path, str) and cache_path.startswith('gs://') and self.object_store:
							data = self.object_store.get_bytes(cache_path)
							result = joblib.load(io.BytesIO(data))
						else:
							result = joblib.load(Path(cache_path))
						step_name = key.split(".", 1)[-1]
						results[step_name] = result
					except Exception as e:
						self.logger.warning(f"Failed to load result for {key}: {e}")
		except Exception as e:
			self.logger.warning(f"kv_store list_run_steps failed: {e}")
		return results
	
	def can_resume_from_step(self, run_id: str, step_name: str, config_hash: str) -> bool:
		"""Check if pipeline can be resumed (not supported without persistent status)."""
		return False
	
	def get_pipeline_stats(self, run_id: str) -> Dict[str, Any]:
		"""Get pipeline statistics."""
		try:
			return self.kv_store.get_pipeline_stats(run_id)
		except Exception:
			return {}
	
	def _compute_config_hash(self, config: Dict[str, Any]) -> str:
		"""Compute a hash of the step graph configuration for change detection."""
		return self._compute_hash(config) 