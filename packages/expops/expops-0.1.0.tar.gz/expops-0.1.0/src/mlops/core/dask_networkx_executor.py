from __future__ import annotations

from datetime import datetime
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import networkx as nx

from dask import compute
from dask.delayed import delayed

from .graph_types import ExecutionResult, NetworkXGraphConfig, NodeType
from .step_state_manager import StepStateManager
from .step_system import StepContext, StepDefinition, StepRegistry

from .executor_worker import (
    _return_placeholder_cached_process_execution_result,
    _return_placeholder_cached_process_execution_result_with_deps,
    _worker_execute_process_task,
    _worker_execute_process_with_deps,
)


class DaskNetworkXExecutor:
    """
    Execute NetworkX DAGs with Dask (threads or distributed) and integrated caching.
    """

    @staticmethod
    def _flatten_dask_overrides(overrides: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        flat: Dict[str, Any] = {}
        if not isinstance(overrides, dict):
            return flat
        for key, value in overrides.items():
            if isinstance(value, dict):
                nested = DaskNetworkXExecutor._flatten_dask_overrides(value)
                for sub_key, sub_val in nested.items():
                    flat_key = f"{key}.{sub_key}" if key else sub_key
                    flat[flat_key] = sub_val
            else:
                flat[str(key)] = value
        return flat

    def __init__(self, step_registry: StepRegistry, state_manager: Optional[StepStateManager] = None, 
                 logger: Optional[logging.Logger] = None,
                 n_workers: int = 2,
                 scheduler_mode: str = "threads",
                 scheduler_address: Optional[str] = None,
                 client: Any = None,
                 extra_files_to_upload: Optional[List[str]] = None,
                 strict_cache: bool = True,
                 min_workers: Optional[int] = None,
                 wait_for_workers_sec: Optional[float] = None,
                 dask_config_overrides: Optional[Dict[str, Any]] = None):
        self.step_registry = step_registry
        self.state_manager = state_manager
        self.logger = logger or logging.getLogger(__name__)
        self.cache_enabled = True
        self.n_workers = n_workers
        self.scheduler_mode = scheduler_mode
        self._scheduler_address = scheduler_address
        self._distributed_client = client
        self.strict_cache = bool(strict_cache)
        try:
            self._extra_upload_files: List[str] = list(extra_files_to_upload) if extra_files_to_upload else []
        except Exception:
            self._extra_upload_files = []
        self._min_workers_override = min_workers if isinstance(min_workers, int) and min_workers > 0 else None
        self._wait_for_workers_override = float(wait_for_workers_sec) if isinstance(wait_for_workers_sec, (int, float)) and wait_for_workers_sec > 0 else None
        self._dask_config_overrides = self._flatten_dask_overrides(dask_config_overrides)

    def _prepare_dask_overrides(self) -> Dict[str, Any]:
        overrides = dict(self._dask_config_overrides)
        # Only apply env defaults when not explicitly configured.
        if "distributed.comm.compression" not in overrides:
            overrides["distributed.comm.compression"] = (
                os.environ.get("MLOPS_DASK_COMPRESSION")
                or os.environ.get("DASK_DISTRIBUTED__COMM__COMPRESSION")
                or "zlib"
            )
        return overrides

    @staticmethod
    def _normalize_bootstrap_mode(value: Optional[str]) -> str:
        """Normalize the bootstrap mode string.

        Supported values:
        - "auto" (default): only bootstrap when workers/scheduler can't import `mlops`
        - "always": always bootstrap (upload zip, sys.path, cleanup)
        - "never": never bootstrap `mlops` package code (still may upload extra files)
        """
        try:
            v = (value or "").strip().lower()
        except Exception:
            v = ""
        if v in ("1", "true", "yes", "y", "always", "on"):
            return "always"
        if v in ("0", "false", "no", "n", "never", "off"):
            return "never"
        return "auto"

    @staticmethod
    def _worker_apply_dask_config(overrides: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply Dask config overrides in the current process (worker or scheduler)."""
        applied: Dict[str, Any] = {}
        try:
            from dask import config as _dask_config
        except Exception:
            return {"error": "config_import_failed"}
        if isinstance(overrides, dict):
            for key, value in overrides.items():
                try:
                    _dask_config.set({key: value})
                    applied[key] = _dask_config.get(key)
                except Exception:
                    applied[key] = value
        return applied

    @staticmethod
    def _worker_try_import(module_name: str) -> bool:
        try:
            __import__(str(module_name))
            return True
        except Exception:
            return False

    @staticmethod
    def _worker_set_env_vars(env_vars: Dict[str, Any]) -> bool:
        import os as _os
        try:
            for key, value in (env_vars or {}).items():
                if value is not None:
                    _os.environ[str(key)] = str(value)
            return True
        except Exception:
            return False

    @staticmethod
    def _worker_ensure_sys_path(paths: List[str]) -> Dict[str, bool]:
        import sys as _sys
        results: Dict[str, bool] = {}
        for p in paths or []:
            try:
                p_str = str(p)
            except Exception:
                continue
            if p_str and p_str not in _sys.path:
                _sys.path.insert(0, p_str)
            results[p_str] = p_str in _sys.path
        return results

    @staticmethod
    def _worker_cleanup_import_state(patterns: List[str], files_to_clean: List[str], clean_mlops: bool = True) -> Dict[str, Any]:
        """Best-effort cleanup to avoid stale imports between runs on long-lived worker processes."""
        import sys as _sys
        import re as _re
        import importlib as _importlib
        import os as _os

        removed_paths: List[str] = []
        removed_files: List[str] = []
        removed_modules: List[str] = []

        # Remove sys.path entries matching known uploaded artifacts (zip names, temp dirs, etc.)
        new_path: List[str] = []
        for p in list(_sys.path):
            try:
                p_str = str(p or "")
            except Exception:
                p_str = ""
            try:
                matched = any(_re.search(ptn, p_str) for ptn in (patterns or []))
            except Exception:
                matched = False
            if matched:
                removed_paths.append(p_str)
                continue
            if p not in new_path:
                new_path.append(p)
        _sys.path[:] = new_path

        # Optionally evict previously loaded `mlops` modules to force a clean import.
        if clean_mlops:
            for name in list(_sys.modules.keys()):
                if name == "mlops" or name.startswith("mlops."):
                    removed_modules.append(name)
                    _sys.modules.pop(name, None)

        # Aggressively remove uploaded custom model modules from sys.modules and common upload locations.
        for fname in (files_to_clean or []):
            try:
                base_fname = _os.path.basename(str(fname))
                if not base_fname.endswith(".py"):
                    continue
                mod_name = base_fname[:-3]
                if mod_name in _sys.modules:
                    removed_modules.append(mod_name)
                    _sys.modules.pop(mod_name, None)
                # Also clear our canonical fallback module name.
                if "custom_model" in _sys.modules:
                    removed_modules.append("custom_model")
                    _sys.modules.pop("custom_model", None)

                # Try to find and remove file from common upload locations (best-effort).
                search_paths = [
                    _os.path.expanduser("~"),
                    _os.getcwd(),
                ]
                for search_dir in search_paths:
                    try:
                        worker_file_path = _os.path.join(search_dir, base_fname)
                        if _os.path.exists(worker_file_path):
                            _os.remove(worker_file_path)
                            removed_files.append(worker_file_path)
                    except Exception:
                        pass
            except Exception:
                pass

        try:
            _importlib.invalidate_caches()
        except Exception:
            pass
        return {
            "removed_paths": removed_paths,
            "removed_modules": removed_modules,
            "removed_files": removed_files,
        }
    
    def _ensure_connected_to_scheduler(self, force: bool = False) -> None:
        """Connect to an external Dask scheduler if requested; otherwise use threads.

        Note: For many real clusters, workers already have `mlops` installed or share a filesystem.
        In that case, this method will skip the heavy "upload source zip / sys.path surgery" work
        by default (bootstrap mode = auto).
        """
        if self.scheduler_mode != 'distributed':
            return
        if self._distributed_client is not None and not force:
            return
        scheduler_addr = self._scheduler_address or os.environ.get('DASK_SCHEDULER_ADDRESS')
        # If a client already exists (e.g., user passed one in, or restart created one),
        # prefer its known scheduler address as a fallback.
        if not scheduler_addr and self._distributed_client is not None:
            try:
                scheduler_addr = getattr(getattr(self._distributed_client, "scheduler", None), "address", None)
            except Exception:
                scheduler_addr = None
        if not scheduler_addr:
            self.logger.warning(
                "Distributed scheduler requested but no Client or address provided. Falling back to threads."
            )
            self.scheduler_mode = 'threads'
            return
        try:
            # Ensure we have a client connection.
            if self._distributed_client is None:
                try:
                    from distributed import Client
                except Exception:
                    from dask.distributed import Client
                self._distributed_client = Client(scheduler_addr)
                self.logger.info(f"Connected to Dask scheduler at {scheduler_addr}")

            self._configure_distributed_runtime(scheduler_addr)
        except Exception as e:
            self.logger.warning(
                f"Failed to connect/configure scheduler at {scheduler_addr} ({e}). Falling back to threads."
            )
            self.scheduler_mode = 'threads'

    def _configure_distributed_runtime(self, scheduler_addr: str) -> None:
        """Best-effort cluster setup after a Client is connected."""
        if not self._distributed_client:
            raise RuntimeError("Distributed client is not initialized")

        client = self._distributed_client
        config_overrides = self._prepare_dask_overrides()

        # Push config to scheduler first (so it is applied even before workers join).
        try:
            sched_conf = client.run_on_scheduler(self._worker_apply_dask_config, config_overrides)
            self.logger.info(f"Scheduler Dask config applied: {sched_conf}")
        except Exception as e:
            self.logger.warning(f"Failed to push Dask config to scheduler: {e}")

        # Resolve worker wait settings.
        min_workers_env = os.environ.get('MLOPS_DASK_MIN_WORKERS', '').strip()
        timeout_env = os.environ.get('MLOPS_DASK_WAIT_FOR_WORKERS_SEC', '').strip()
        if self._min_workers_override:
            min_workers = self._min_workers_override
        elif min_workers_env.isdigit():
            min_workers = int(min_workers_env)
        else:
            min_workers = self.n_workers if isinstance(self.n_workers, int) and self.n_workers > 0 else 1
        if min_workers < 1:
            min_workers = 1
        if self._wait_for_workers_override:
            wait_timeout = self._wait_for_workers_override
        elif timeout_env:
            try:
                wait_timeout = float(timeout_env)
            except Exception:
                wait_timeout = 30.0
        else:
            wait_timeout = 30.0

        # Wait for workers to connect (best-effort; verify count afterwards).
        try:
            self.logger.info(f"Waiting for at least {min_workers} worker(s) to connect (timeout={wait_timeout}s)")
            client.wait_for_workers(min_workers, timeout=wait_timeout)  # type: ignore[attr-defined]
        except Exception:
            pass

        try:
            info = client.scheduler_info()
            workers_dict = info.get('workers', {}) if isinstance(info, dict) else {}
            worker_count = len(workers_dict)
        except Exception:
            worker_count = 0

        if worker_count < min_workers:
            raise RuntimeError(
                f"Connected to Dask scheduler at {scheduler_addr} but only {worker_count} worker(s) "
                f"available after waiting {wait_timeout}s. Ensure workers are started and connected."
            )
        self.logger.info(f"Workers connected: {worker_count}")

        # After workers connect, push config to workers as well.
        try:
            workers_conf = client.run(self._worker_apply_dask_config, config_overrides)
            self.logger.info(f"Workers Dask config applied: {workers_conf}")
        except Exception as e:
            self.logger.warning(f"Failed to push Dask config to workers: {e}")

        # Bootstrap code/env on long-lived worker processes (auto-skip when not needed).
        self._bootstrap_distributed_imports_and_env()

    def _bootstrap_distributed_imports_and_env(self) -> None:
        if not self._distributed_client:
            return

        client = self._distributed_client
        bootstrap_mode = self._normalize_bootstrap_mode(os.environ.get("MLOPS_DASK_BOOTSTRAP", "auto"))

        # Decide whether we need to ship the `mlops` package code to workers.
        needs_mlops_bootstrap = bootstrap_mode == "always"
        if bootstrap_mode == "auto":
            try:
                import_ok_workers = client.run(self._worker_try_import, "mlops")
                needs_mlops_bootstrap = not all(bool(v) for v in import_ok_workers.values())
            except Exception:
                needs_mlops_bootstrap = True
            try:
                import_ok_sched = client.run_on_scheduler(self._worker_try_import, "mlops")
                needs_mlops_bootstrap = needs_mlops_bootstrap or not bool(import_ok_sched)
            except Exception:
                needs_mlops_bootstrap = True
        elif bootstrap_mode == "never":
            needs_mlops_bootstrap = False

        # Cleanup import state only when we are about to upload something (mlops zip and/or extra files).
        if needs_mlops_bootstrap or self._extra_upload_files:
            try:
                cleanup_patterns = [r"mlops_src.*\\.zip", r"mlops_src_"]
                files_to_clean = self._extra_upload_files if self._extra_upload_files else []
                try:
                    cleaned_workers = client.run(
                        self._worker_cleanup_import_state,
                        cleanup_patterns,
                        files_to_clean,
                        needs_mlops_bootstrap,
                    )
                    self.logger.info(f"Cleaned worker import state: {cleaned_workers}")
                except Exception as e:
                    self.logger.warning(f"Failed to clean workers import state: {e}")
                try:
                    cleaned_sched = client.run_on_scheduler(
                        self._worker_cleanup_import_state,
                        cleanup_patterns,
                        files_to_clean,
                        needs_mlops_bootstrap,
                    )
                    self.logger.info(f"Cleaned scheduler import state: {cleaned_sched}")
                except Exception as e:
                    self.logger.warning(f"Failed to clean scheduler import state: {e}")
            except Exception as e:
                self.logger.warning(f"Cleanup of previous uploaded code failed: {e}")

        # Ship mlops code only when required.
        if needs_mlops_bootstrap:
            try:
                from pathlib import Path as _Path
                import tempfile
                import zipfile

                # Package just the `mlops/` python package, not an entire repo root or site-packages.
                mlops_pkg_dir = _Path(__file__).resolve().parents[1]  # .../mlops
                pkg_parent = mlops_pkg_dir.parent  # .../src (source) or .../site-packages (installed)

                zip_path = _Path(tempfile.gettempdir()) / "mlops_pkg.zip"
                with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                    for path in mlops_pkg_dir.rglob('*.py'):
                        try:
                            # Keep `mlops/...` as the top-level folder inside the zip.
                            zf.write(path, arcname=str(path.relative_to(pkg_parent)))
                        except Exception:
                            pass
                client.upload_file(str(zip_path))
                self.logger.info(f"Uploaded mlops source package to workers: {zip_path}")

                # Ensure the zip and repo paths are importable (best-effort; may be a no-op on real clusters).
                paths_to_add: List[str] = []
                try:
                    paths_to_add.append(str(zip_path))
                except Exception:
                    pass
                try:
                    added = client.run(self._worker_ensure_sys_path, paths_to_add)
                    self.logger.info(f"Adjusted sys.path on workers for importability: {added}")
                except Exception as e:
                    self.logger.warning(f"Failed to adjust worker sys.path: {e}")
                try:
                    added_sched = client.run_on_scheduler(self._worker_ensure_sys_path, paths_to_add)
                    self.logger.info(f"Adjusted sys.path on scheduler for importability: {added_sched}")
                except Exception as e:
                    self.logger.warning(f"Failed to adjust scheduler sys.path: {e}")

                # Validate import on workers (warn-only).
                try:
                    import_ok = client.run(self._worker_try_import, "mlops")
                    if isinstance(import_ok, dict) and not all(bool(v) for v in import_ok.values()):
                        self.logger.warning(
                            "One or more workers cannot import 'mlops'. Ensure shared filesystem or install package on workers."
                        )
                except Exception:
                    pass
            except Exception as e:
                self.logger.warning(f"Failed to package/upload mlops code to workers: {e}")

        # Upload any additional files requested (e.g., custom model script, reporting entrypoint).
        if self._extra_upload_files:
            for _f in self._extra_upload_files:
                try:
                    if _f and os.path.exists(_f):
                        client.upload_file(str(_f))
                        self.logger.info(f"Uploaded extra file to workers: {_f}")
                except Exception as e:
                    self.logger.warning(f"Failed to upload extra file '{_f}' to workers: {e}")

        # Propagate critical environment variables to workers (best-effort).
        try:
            env_to_propagate: Dict[str, str] = {}
            critical_env_vars = [
                'MLOPS_PROJECT_ID',
                'MLOPS_WORKSPACE_DIR',
                'MLOPS_REPO_ROOT',
                'GOOGLE_APPLICATION_CREDENTIALS',
                'GOOGLE_CLOUD_PROJECT',
                'FIRESTORE_EMULATOR_HOST',
                'DASK_DISTRIBUTED__COMM__COMPRESSION',
                'MLOPS_REPORTING_PYTHON',
                'MLOPS_REPORTING_CONFIG',
                'MLOPS_RANDOM_SEED',
                'MLOPS_TASK_LEVEL_SEEDING',
            ]
            for env_var in critical_env_vars:
                value = os.environ.get(env_var)
                if value is not None:
                    env_to_propagate[env_var] = value
            if env_to_propagate:
                client.run(self._worker_set_env_vars, env_to_propagate)
                client.run_on_scheduler(self._worker_set_env_vars, env_to_propagate)
                self.logger.info(f"Propagated environment variables: {list(env_to_propagate.keys())}")
        except Exception as e:
            self.logger.warning(f"Failed to propagate environment variables to workers: {e}")
        
    def set_cache_enabled(self, enabled: bool) -> None:
        """Enable or disable step caching."""
        self.cache_enabled = enabled
    
    def restart_distributed_client(self) -> None:
        """Restart the distributed client connection to ensure clean state between runs.
        
        This is a more aggressive cleanup than the automatic cleanup performed in 
        _ensure_connected_to_scheduler. Use this if you're experiencing persistent
        deserialization errors between consecutive runs.
        """
        if self.scheduler_mode != 'distributed' or not self._distributed_client:
            return
        
        try:
            scheduler_addr = self._distributed_client.scheduler.address
            self.logger.info(f"Restarting Dask client connection to {scheduler_addr}")
            
            # Close the existing client
            try:
                self._distributed_client.close()
            except Exception as e:
                self.logger.warning(f"Error closing existing client: {e}")
            
            # Create a new client
            try:
                from distributed import Client  # type: ignore
            except Exception:
                from dask.distributed import Client  # type: ignore
            
            self._distributed_client = Client(scheduler_addr)
            self.logger.info(f"Successfully restarted Dask client connection")
            
            # Re-run the setup (compression, worker checks, etc.)
            self._ensure_connected_to_scheduler(force=True)
        except Exception as e:
            self.logger.error(f"Failed to restart Dask client: {e}")
            raise
        
    def _build_process_graph(self, config: NetworkXGraphConfig) -> nx.DiGraph:
        """Build the main process-level DAG."""
        process_graph = nx.DiGraph()
        
        for process_config in config.processes:
            process_graph.add_node(
                process_config.name,
                type=NodeType.PROCESS,
                config=process_config
            )
            
        for process_config in config.processes:
            depends_on = getattr(process_config, 'depends_on', [])
            for dependency in depends_on:
                process_graph.add_edge(dependency, process_config.name)
                
        return process_graph
        
    def _validate_process_dag(self, process_graph: nx.DiGraph) -> None:
        """Validate that the process-level graph is a DAG."""
        if not nx.is_directed_acyclic_graph(process_graph):
            cycles = list(nx.simple_cycles(process_graph))
            raise ValueError(f"Process-level graph contains cycles: {cycles}")
    
    # Removed unused step-config hashing; step-level caching uses stable context hash instead
    
    def _compute_step_input_hash(self, step_def: StepDefinition, context: StepContext) -> str:
        """Compute a stable step input hash without parameter resolution.
        Uses available context surface to approximate variability.
        """
        if not self.state_manager:
            return ""
        try:
            context_data = {
                'step': getattr(step_def, 'name', None),
                'process': getattr(context, 'current_process', None),
                'step_results_keys': sorted(list((getattr(context, 'step_results', {}) or {}).keys())),
                'iteration': getattr(context, 'iteration', 0),
            }
            return self.state_manager._compute_hash(context_data)
        except Exception as e:
            try:
                self.logger.warning(f"Failed to compute context-based step hash: {e}")
            except Exception:
                pass
            return ""
            
    # Removed unused Dask step task; steps execute via the step wrapper inside process runners

    def _serialize_context_for_worker(self, context: StepContext) -> dict:
        """Serialize minimal context payload with only primitives for safe graph shipping."""
        try:
            data_paths = {k: str(v) for k, v in (context.data_paths or {}).items()}
        except Exception:
            data_paths = {}
        # Sanitize step_results: keep only JSON-serializable fields and avoid heavy objects
        sanitized_results: Dict[str, Dict[str, Any]] = {}
        for process_name, result in (context.step_results or {}).items():
            try:
                # Copy data and drop recursive/heavy fields (nested step maps, logs, large artifact pointers)
                _data = dict(result) if isinstance(result, dict) else {}
                _common_drop_keys = ['__step_results__', '__logs__', 'checkpoint_path', 'cache_path', 'artifacts']
                _heavy_drop_keys = ['model', 'saved_model'] if str(self.scheduler_mode) == 'distributed' else []
                for _k in (_common_drop_keys + _heavy_drop_keys):
                    try:
                        _data.pop(_k, None)
                    except Exception:
                        pass
                # Best-effort: attach cache path so workers can rehydrate dependencies locally without shipping heavy objects
                _cache_path = None
                try:
                    if self.state_manager:
                        ih, ch, fh = self._compute_process_lookup_hashes(context, process_name)
                        # Guard against missing kv_store in rare cases
                        _kvs = getattr(self.state_manager, 'kv_store', None)
                        if _kvs and hasattr(_kvs, 'get_process_cache_path'):
                            _cache_path = _kvs.get_process_cache_path(process_name, ih, ch, fh)
                except Exception:
                    _cache_path = None
                # Keep the same shape as original result surface for dependency injection.
                # Attach cache path as a top-level meta key to enable rehydration when needed.
                _data['cache_path'] = _cache_path
                sanitized_results[process_name] = _data
            except Exception:
                continue
        return {
            'project_id': context.project_id,
            'run_id': context.run_id,
            'global_config': dict(getattr(context, 'global_config', {}) or {}),
            'data_paths': data_paths,
            'checkpoint_dir': str(getattr(context, 'checkpoint_dir', 'artifacts/checkpoints')),
            'step_results': sanitized_results,
        }
    
    def _compute_process_lookup_hashes(self, context: StepContext, process_name: str) -> tuple:
        """Compute (ih, ch, fh) via shared helper to keep driver/worker in lockstep."""
        try:
            from .process_hashing import compute_process_hashes
        except Exception:
            compute_process_hashes = None

        # Build deterministic dependency_map from the process graph
        dependency_map = {}
        try:
            if hasattr(self, 'process_graph'):
                for n in list(self.process_graph.nodes):
                    try:
                        preds = list(self.process_graph.predecessors(n))
                        preds = sorted(set(preds))
                        dependency_map[n] = preds
                    except Exception:
                        dependency_map[n] = []
        except Exception:
            dependency_map = {}

        if compute_process_hashes and self.state_manager:
            # Use code_function mapping when available to resolve the correct process definition
            try:
                lookup_name = self._get_lookup_name(process_name) or process_name
            except Exception:
                lookup_name = process_name
            ih, ch, fh = compute_process_hashes(
                self.state_manager,
                context,
                process_name,
                dependency_map,
                lookup_name=lookup_name,
            )
        else:
            ih = ch = fh = None

        self.logger.debug(f"[HashTrace] side=driver process={process_name} ih={ih} ch={ch} fh={fh}")

        return (ih, ch, fh)
    
    def _get_cache_config_for_worker(self) -> Dict[str, Any]:
        """Extract cache configuration for worker state manager creation."""
        try:
            if self.state_manager is None:
                return {}

            cfg: Dict[str, Any] = {}

            kv_store = getattr(self.state_manager, "kv_store", None)
            if kv_store is not None:
                kv_type = type(kv_store).__name__
                cfg["kv_store_type"] = kv_type
                if "GCP" in kv_type or "Firestore" in kv_type:
                    cfg["kv_store_config"] = {
                        "project_id": getattr(kv_store, "project_id", None),
                        "gcp_project": getattr(kv_store, "gcp_project", None),
                        "topic_name": getattr(kv_store, "topic_name", None),
                        "emulator_host": getattr(kv_store, "_emulator_host", None),
                    }

            obj_store = getattr(self.state_manager, "object_store", None)
            if obj_store is not None:
                obj_type = type(obj_store).__name__
                cfg["object_store_type"] = obj_type
                if "GCS" in obj_type:
                    bucket_name = None
                    try:
                        bucket_obj = getattr(obj_store, "_bucket", None)
                        bucket_name = getattr(bucket_obj, "name", None) if bucket_obj is not None else None
                    except Exception:
                        bucket_name = None
                    cfg["object_store_config"] = {
                        "bucket": bucket_name,
                        "prefix": getattr(obj_store, "_prefix", None),
                    }

            return cfg
        except Exception:
            return {}
            
    def _get_lookup_name(self, proc_name: str) -> Optional[str]:
        try:
            if hasattr(self, 'process_graph') and self.process_graph.has_node(proc_name):
                cfg = self.process_graph.nodes[proc_name].get('config')
                return getattr(cfg, 'code_function', None)
        except Exception:
            return None
        return None

    def _get_logging_flag(self, proc_name: str) -> bool:
        try:
            from .step_system import get_process_registry  # type: ignore
            pr = get_process_registry()
            pdef = pr.get_process(self._get_lookup_name(proc_name) or proc_name) if pr else None
            return getattr(pdef, 'logging', True) if pdef else True
        except Exception:
            return True

    def _repo_root(self) -> Path:
        # Legacy: many code paths historically treated this as the repo root.
        # For installed packages, use the workspace root (where projects/ lives).
        try:
            from .workspace import get_workspace_root
            return get_workspace_root()
        except Exception:
            return Path.cwd()

    def _resolve_path(self, p: str) -> Path:
        try:
            path = Path(p)
            if path.is_absolute():
                return path
            return self._repo_root() / p
        except Exception:
            return Path(p)

    def _get_reporting_cfg(self) -> dict:
        try:
            txt = os.environ.get('MLOPS_REPORTING_CONFIG') or ''
            if not txt:
                return {}
            return json.loads(txt)
        except Exception:
            return {}

    def _get_chart_spec(self, name: str) -> dict:
        rcfg = self._get_reporting_cfg()
        charts = rcfg.get('charts') or []
        for item in charts:
            try:
                if isinstance(item, dict) and str(item.get('name')) == name and str(item.get('type', 'static')).lower() != 'dynamic':
                    return item
            except Exception:
                continue
        return {}

    def _compute_chart_function_hash(self, static_entrypoint: str) -> Optional[str]:
        try:
            p = self._resolve_path(static_entrypoint)
            with open(p, 'rb') as f:
                data = f.read()
            return hashlib.sha256(data).hexdigest()
        except Exception:
            return None

    def _compute_chart_config_hash(self, name: str) -> Optional[str]:
        try:
            rcfg = self._get_reporting_cfg()
            global_args = rcfg.get('args') or []
            theme = os.environ.get('MLOPS_CHART_THEME')
            spec = self._get_chart_spec(name)
            cfg_payload = {
                'name': name,
                'probe_paths': spec.get('probe_paths') or {},
                'chart_args': spec.get('args') or [],
                'global_args': global_args,
                'theme': theme,
            }
            if self.state_manager:
                return self.state_manager._compute_hash(cfg_payload)
            else:
                payload = json.dumps(cfg_payload, sort_keys=True, separators=(",", ":")).encode()
                return hashlib.sha256(payload).hexdigest()
        except Exception:
            return None

    def _maybe_apply_chart_hash_overrides(
        self,
        process_name: str,
        config_hash: Optional[str],
        function_hash: Optional[str],
    ) -> tuple[Optional[str], Optional[str]]:
        """Override hashes for chart nodes so cache keys track chart config + entrypoint content."""
        try:
            if not hasattr(self, "process_graph") or not self.process_graph.has_node(process_name):
                return config_hash, function_hash
            cfg = self.process_graph.nodes[process_name].get("config")
            if getattr(cfg, "process_type", "process") != "chart":
                return config_hash, function_hash
            rcfg = self._get_reporting_cfg()
            entrypoint = rcfg.get("static_entrypoint") or rcfg.get("entrypoint") or ""
            ch_override = self._compute_chart_config_hash(process_name)
            fh_override = self._compute_chart_function_hash(entrypoint) if entrypoint else None
            return ch_override or config_hash, fh_override or function_hash
        except Exception:
            return config_hash, function_hash

    def execute_graph(
        self,
        config: NetworkXGraphConfig,
        context: StepContext,
        run_id: Optional[str] = None,
        resume_from_process: Optional[str] = None,
        stop_after_process: bool | str = False,
    ) -> Dict[str, ExecutionResult]:
        """
        Execute the NetworkX-based graph using Dask's advanced scheduler.
        
        This is the main entry point that replaces the manual scheduling approach
        with Dask's task scheduler for automatic dependency resolution and parallelization.
        """
        
        process_graph = self._build_process_graph(config)
        # Persist the main process graph so hashing can access per-process code_function
        self.process_graph = process_graph
        self._validate_process_dag(process_graph)
        
        if self.state_manager and run_id and not stop_after_process:
            self.state_manager.start_pipeline_execution(run_id, config.__dict__, self.cache_enabled)
        
        self.logger.info(f"Executing {len(process_graph.nodes)} processes with Dask scheduler")
        self.logger.info(f"Process execution order will be determined by Dask: {list(nx.topological_sort(process_graph))}")
        if self.scheduler_mode == 'distributed':
            self.logger.info("Using distributed scheduler (external Dask Client)")
            self._ensure_connected_to_scheduler()
            # Wire distributed client into step_system so @step calls submit to workers
            try:
                from .step_system import set_distributed_client as _set_dc
                _set_dc(self._distributed_client)
            except Exception:
                pass
        else:
            self.logger.info(f"Using threaded scheduler with {self.n_workers} workers")
            # Ensure no distributed client is set in threaded mode
            try:
                from .step_system import set_distributed_client as _set_dc  # type: ignore
                _set_dc(None)
            except Exception:
                pass
        
        execution_results = {}
        
        try:
            is_distributed = self.scheduler_mode == 'distributed'
            if is_distributed:
                self._ensure_connected_to_scheduler()
            process_tasks: Dict[str, Any] = {}

            topo_order = list(nx.topological_sort(process_graph))

            # Limit scheduling for resume/single-process execution modes.
            stop_target: Optional[str] = None
            if isinstance(stop_after_process, str) and stop_after_process.strip():
                stop_target = stop_after_process.strip()
            elif stop_after_process and resume_from_process:
                stop_target = str(resume_from_process)

            targets: set[str] = set(topo_order)
            if stop_target and stop_target in process_graph:
                targets = {stop_target}
            elif resume_from_process and resume_from_process in process_graph:
                # Resume from a given process and continue downstream.
                targets = set(nx.descendants(process_graph, resume_from_process))
                targets.add(resume_from_process)

            required_nodes: set[str] = set()
            for n in targets:
                required_nodes.add(n)
                try:
                    required_nodes.update(nx.ancestors(process_graph, n))
                except Exception:
                    pass

            nodes_order = [n for n in topo_order if n in required_nodes]

            for process_name in nodes_order:
                process_config = process_graph.nodes[process_name]['config']
                dependencies = list(process_graph.predecessors(process_name))
                dep_tasks = [process_tasks[dep] for dep in dependencies if dep in process_tasks]

                cached_task_created = False

                if self.cache_enabled and self.state_manager:
                    # Unified enhanced hashing for cache lookup
                    try:
                        process_input_hash, process_config_hash, composite_fhash = self._compute_process_lookup_hashes(context, process_name)
                        process_config_hash, composite_fhash = self._maybe_apply_chart_hash_overrides(
                            process_name, process_config_hash, composite_fhash
                        )
                    except Exception:
                        process_input_hash = process_config_hash = composite_fhash = None

                    if composite_fhash is None:
                        try:
                            from .step_system import get_process_registry
                            pr = get_process_registry()
                            pdef = pr.get_process(self._get_lookup_name(process_name) or process_name) if pr else None
                            orig_fn = getattr(pdef, 'original_func', None) if pdef else None
                            composite_fhash = self.state_manager._compute_function_hash(orig_fn or getattr(pdef, 'runner', None)) if pdef else None
                        except Exception:
                            composite_fhash = None
                        
                    try:
                        self.logger.info(
                            f"[CACHE] Lookup process={process_name} ih={process_input_hash} ch={process_config_hash} fh={composite_fhash}"
                        )
                        cached_data = self.state_manager.get_cached_process_result_with_metadata(
                            process_name,
                            input_hash=process_input_hash,
                            config_hash=process_config_hash,
                            function_hash=composite_fhash,
                        )
                    except Exception:
                        cached_data = None

                    if not is_distributed and cached_data is None:
                        try:
                            cached_data = self.state_manager.get_cached_process_result_with_metadata(process_name)
                        except Exception:
                            cached_data = None
                    
                    # Extract result and metadata from cached data
                    cached_proc = None
                    cached_run_id = None
                    cached_metadata = {}
                    if cached_data is not None:
                        try:
                            cached_proc, cached_run_id, cached_metadata = cached_data
                        except Exception:
                            # Fallback if metadata extraction fails
                            cached_proc = cached_data if not isinstance(cached_data, tuple) else None
                    
                    if cached_proc is not None:
                        self.logger.info(f"[CACHE] Hit for process={process_name}; scheduling placeholder")
                        if dep_tasks:
                            task = delayed(_return_placeholder_cached_process_execution_result_with_deps)(process_name, dep_tasks)
                        else:
                            task = delayed(_return_placeholder_cached_process_execution_result)(process_name)
                        process_tasks[process_name] = task
                        try:
                            context.step_results[process_name] = cached_proc
                        except Exception:
                            pass
                        cached_task_created = True

                        # Pre-record a 'cached' completion so the UI reflects cache hits immediately
                        # rather than after the compute() phase returns.
                        try:
                            if self.state_manager:
                                from .step_state_manager import ProcessExecutionResult as _ProcessExec  # local import to avoid import cycles
                                enable_logging = self._get_logging_flag(process_name)
                                # Extract cached metadata for frontend display
                                cached_exec_time = cached_metadata.get('execution_time', 0.0) if isinstance(cached_metadata, dict) else 0.0
                                cached_started = cached_metadata.get('started_at') if isinstance(cached_metadata, dict) else None
                                cached_ended = cached_metadata.get('ended_at') if isinstance(cached_metadata, dict) else None
                                self.state_manager.record_process_completion(
                                    run_id or 'default',
                                    _ProcessExec(
                                        process_name=process_name,
                                        success=True,
                                        result=cached_proc,
                                        execution_time=0.0,
                                        timestamp=datetime.now().isoformat(),
                                    ),
                                    input_hash=process_input_hash,
                                    config_hash=process_config_hash,
                                    function_hash=composite_fhash,
                                    was_cached=True,
                                    enable_logging=enable_logging,
                                    cached_run_id=cached_run_id,
                                    cached_started_at=cached_started,
                                    cached_ended_at=cached_ended,
                                    cached_execution_time=cached_exec_time,
                                )
                        except Exception:
                            # Best-effort; if this fails we'll still write completion in the post-process phase
                            pass

                if not cached_task_created:
                    self.logger.info(f"[CACHE] Miss or not loadable for process={process_name}; scheduling execution")
                    ctx_payload = self._serialize_context_for_worker(context)
                    # Provide dependency map for recursive signature hashing on workers
                    try:
                        dependency_map = {n: list(process_graph.predecessors(n)) for n in nodes_order}
                    except Exception:
                        dependency_map = {n: [] for n in nodes_order}
                    proc_payload = {
                        'name': process_config.name,
                        'code_function': getattr(process_config, 'code_function', None),
                        'process_type': getattr(process_config, 'process_type', 'process'),
                        'cache_config': self._get_cache_config_for_worker() if self.cache_enabled and self.state_manager else None,
                        'has_state_manager': bool(self.state_manager and self.cache_enabled),
                        'logging': self._get_logging_flag(process_name),
                        'dependencies': dependencies,
                        'dependency_map': dependency_map,
                    }

                    # Attach chart metadata and precomputed hashes for chart nodes
                    try:
                        if getattr(process_config, 'process_type', 'process') == 'chart':
                            rcfg = self._get_reporting_cfg()
                            entrypoint = rcfg.get('static_entrypoint') or rcfg.get('entrypoint') or ''
                            function_hash_override = self._compute_chart_function_hash(entrypoint) if entrypoint else None
                            config_hash_override = self._compute_chart_config_hash(process_config.name)
                            spec = self._get_chart_spec(process_config.name)
                            chart_spec = {
                                'name': process_config.name,
                                'probe_paths': (spec.get('probe_paths') or {}),
                                'args': list(rcfg.get('args') or []) + list(spec.get('args') or []),
                                'theme': os.environ.get('MLOPS_CHART_THEME'),
                                'entrypoint': entrypoint,
                                'reporting_python': os.environ.get('MLOPS_REPORTING_PYTHON') or None,
                            }
                            proc_payload['hash_overrides'] = {
                                'function_hash': function_hash_override,
                                'config_hash': config_hash_override,
                            }
                            proc_payload['chart_spec'] = chart_spec
                    except Exception:
                        pass
                    if dep_tasks:
                        task = delayed(_worker_execute_process_with_deps)(proc_payload, ctx_payload, dep_tasks, run_id)
                    else:
                        task = delayed(_worker_execute_process_task)(proc_payload, ctx_payload, run_id)
                    process_tasks[process_name] = task

            if process_tasks:
                # Execute according to scheduler mode
                if is_distributed:
                    try:
                        futures = self._distributed_client.compute(list(process_tasks.values()))
                        results_values = self._distributed_client.gather(futures)
                    except Exception:
                        results_values = compute(*process_tasks.values())
                else:
                    results_values = compute(*process_tasks.values(), scheduler='threads', num_workers=self.n_workers)

                proc_results = dict(zip(process_tasks.keys(), results_values))
                execution_results.update(proc_results)
                    
                # Surface worker-side logs in both modes
                try:
                    for _pname, _pres in proc_results.items():
                        try:
                            _r = getattr(_pres, 'result', None)
                            if isinstance(_r, dict) and '__logs__' in _r and _r['__logs__']:
                                _logs = _r['__logs__']
                                try:
                                    self.logger.info(f"[WorkerLogs][{_pname}] BEGIN")
                                    for _line in str(_logs).splitlines():
                                        self.logger.info(f"[{_pname}] {_line}")
                                    self.logger.info(f"[WorkerLogs][{_pname}] END")
                                except Exception:
                                    pass
                        except Exception:
                            continue
                except Exception:
                    pass
                    
                # Post-process results: errors, context hydration, cache recording
                for process_name, result in proc_results.items():
                    # Rehydrate placeholders
                    try:
                        if getattr(result, 'was_cached', False) and not getattr(result, 'result', None):
                            if self.cache_enabled and self.state_manager:
                                try:
                                    ih, ch, fh = self._compute_process_lookup_hashes(context, process_name)
                                    ch, fh = self._maybe_apply_chart_hash_overrides(process_name, ch, fh)
                                    loaded = self.state_manager.get_cached_process_result(process_name, input_hash=ih, config_hash=ch, function_hash=fh)
                                except Exception:
                                    loaded = None
                                if loaded is not None:
                                    result.result = loaded
                    except Exception:
                        pass

                        if result.error is not None:
                            failure_mode = config.execution.get("failure_mode", "stop")
                            if failure_mode == "stop_and_resume":
                                try:
                                    _r = getattr(result, 'result', None)
                                    if isinstance(_r, dict) and '__logs__' in _r and _r['__logs__']:
                                        _logs = _r['__logs__']
                                        try:
                                            self.logger.info(f"[WorkerLogs][{process_name}] BEGIN")
                                            for _line in str(_logs).splitlines():
                                                self.logger.info(f"[{process_name}] {_line}")
                                            self.logger.info(f"[WorkerLogs][{process_name}] END")
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                                try:
                                    self.logger.error(f"Process {process_name} failed. Can resume from this process. Error: {result.error}")
                                except Exception:
                                    self.logger.error(f"Process {process_name} failed. Can resume from this process.")
                                if self.state_manager and run_id and not stop_after_process:
                                    self.state_manager.complete_pipeline_execution(run_id, False)
                                raise RuntimeError(f"Pipeline stopped at process {process_name}.")
                            else:
                                if self.state_manager and run_id and not stop_after_process:
                                    self.state_manager.complete_pipeline_execution(run_id, False)
                                raise RuntimeError(f"Process {process_name} failed: {result.error}")
                        
                    # Update driver context with clean result
                        if result.error is None and getattr(result, 'result', None) is not None:
                            try:
                                clean_result = {k: v for k, v in result.result.items() if not k.startswith('__')} if isinstance(result.result, dict) else result.result
                                context.step_results[process_name] = clean_result
                            except Exception:
                                pass
                        
                    if self.cache_enabled and self.state_manager:
                        try:
                            from .step_state_manager import ProcessExecutionResult as _ProcessExec
                            ih, ch, fh = None, None, None
                            try:
                                ih, ch, fh = self._compute_process_lookup_hashes(context, process_name)
                                ch, fh = self._maybe_apply_chart_hash_overrides(process_name, ch, fh)
                                self.logger.debug(f"[CACHE WRITE] process={process_name} ih={ih} ch={ch} fh={fh}")
                            except Exception as e:
                                self.logger.warning(f"[CACHE WRITE] Failed to compute hashes for {process_name}: {e}")
                            enable_logging = self._get_logging_flag(process_name)
                    
                            # Determine success based on error field
                            is_success = result.error is None
                            
                            self.state_manager.record_process_completion(
                                run_id or 'default',
                                _ProcessExec(
                                    process_name=process_name,
                                    success=is_success,
                                    result=result.result if is_success else None,
                                    execution_time=result.execution_time,
                                    timestamp=datetime.now().isoformat(),
                                ),
                                input_hash=ih,
                                config_hash=ch,
                                function_hash=fh,
                                was_cached=bool(getattr(result, 'was_cached', False)),
                                enable_logging=enable_logging,
                            )
                        except Exception as e:
                            self.logger.warning(f"❌ Failed to record process completion for {process_name}: {e}")

                        # Step-level cache recording - only if process succeeded
                        if is_success:
                            try:
                                sr_map = result.result.get('__step_results__', {}) if isinstance(result.result, dict) else {}
                                if isinstance(sr_map, dict) and sr_map:
                                    from .step_state_manager import StepExecutionResult as _StepExec
                                    for _sname, _sres in sr_map.items():
                                        try:
                                            step_def = self.step_registry.get_step(_sname)
                                            if not step_def:
                                                continue
                                            tmp_ctx = None
                                            try:
                                                from .step_system import StepContext as _Ctx
                                                tmp_ctx = _Ctx(
                                                    project_id=getattr(context, 'project_id', None),
                                                    run_id=run_id or getattr(context, 'run_id', None),
                                                    tracker=None,
                                                    step_results=sr_map,
                                                    global_config=getattr(context, 'global_config', {}) or {},
                                                    data_paths=getattr(context, 'data_paths', {}) or {},
                                                    checkpoint_dir=getattr(context, 'checkpoint_dir', None),
                                                )
                                                try:
                                                    tmp_ctx.current_process = process_name  # type: ignore[attr-defined]
                                                except Exception:
                                                    pass
                                            except Exception:
                                                tmp_ctx = context
                                            input_hash = self._compute_step_input_hash(step_def, tmp_ctx)
                                            try:
                                                function_hash = self.state_manager._compute_function_hash(step_def.original_func)
                                            except Exception:
                                                function_hash = None
                                            try:
                                                config_source = getattr(context, 'global_config', None) or {}
                                                config_hash = self.state_manager._compute_hash(config_source)
                                            except Exception:
                                                config_hash = None
                                            enable_logging = getattr(step_def, 'logging', True) if step_def else True
                                            # Extract execution time from step result metadata
                                            step_exec_time = 0.0
                                            if isinstance(_sres, dict):
                                                step_exec_time = float(_sres.get('__execution_time__', 0.0))
                                            self.state_manager.record_step_completion(
                                                run_id or 'default',
                                                _StepExec(
                                                    step_name=_sname,
                                                    success=True,
                                                    result=_sres,
                                                    execution_time=step_exec_time,
                                                    timestamp=datetime.now().isoformat(),
                                                ),
                                                input_hash=input_hash,
                                                config_hash=config_hash,
                                                function_name=_sname,
                                                function_hash=function_hash,
                                                was_cached=bool(_sres.get('__was_cached__')) if isinstance(_sres, dict) else False,
                                                process_name=process_name,
                                                enable_logging=enable_logging,
                                            )
                                        except Exception:
                                            continue
                            except Exception:
                                pass

                            # Log per-step cached hits summary
                            try:
                                sr_map2 = result.result.get('__step_results__', {}) if isinstance(result.result, dict) else {}
                                if isinstance(sr_map2, dict) and sr_map2:
                                    total_steps = len(sr_map2)
                                    hits = 0
                                    for __v in sr_map2.values():
                                        try:
                                            if isinstance(__v, dict) and __v.get('__was_cached__'):
                                                hits += 1
                                        except Exception:
                                            continue
                                    mode_label = 'Dask Distributed' if is_distributed else 'Dask Threads'
                                    self.logger.info(f"Process {process_name} cached steps: {hits}/{total_steps} [{mode_label}]")
                            except Exception:
                                pass
            
            if self.state_manager and run_id and not stop_after_process:
                self.state_manager.complete_pipeline_execution(run_id, True)
                stats = self.state_manager.get_pipeline_stats(run_id)
                try:
                    if stats and 'cache_hit_rate' in stats:
                        self.logger.info(f"Pipeline completed with Dask scheduler. Cache hit rate: {stats['cache_hit_rate']:.1%} "
                                         f"({stats.get('cache_hit_count', 0)}/{stats.get('completed_steps', 0)} steps)")
                    else:
                        self.logger.info("Pipeline completed with Dask scheduler.")
                except Exception:
                    self.logger.info("Pipeline completed with Dask scheduler.")
        except Exception:
            if self.state_manager and run_id and not stop_after_process:
                self.state_manager.complete_pipeline_execution(run_id, False)
            raise
                    
        return execution_results