from __future__ import annotations

import importlib.util
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from mlops.core import StepStateManager, get_context_factory, get_step_registry, set_current_context
from mlops.core.custom_model_base import MLOpsCustomModelBase
from mlops.core.dask_networkx_executor import DaskNetworkXExecutor
from mlops.core.networkx_parser import parse_networkx_pipeline_from_config

from ..base import ModelAdapter
from ..config_schema import AdapterConfig


def _as_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    try:
        if hasattr(value, "model_dump"):
            return value.model_dump()  # type: ignore[attr-defined]
    except Exception:
        pass
    try:
        return dict(value)  # type: ignore[arg-type]
    except Exception:
        return {}


def _to_int(value: Any) -> Optional[int]:
    try:
        if value is None:
            return None
        return int(value)
    except Exception:
        return None


def _to_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


class CustomModelAdapter(ModelAdapter):
    """Adapter for user-provided Python model scripts.

    Responsibilities:
    - Load the custom script and register `@step` functions
    - Build a StepStateManager (KV + optional object store)
    - Execute the configured NetworkX pipeline via DaskNetworkXExecutor
    """

    def __init__(
        self,
        config: AdapterConfig,
        python_interpreter: Optional[str] = None,
        environment_name: Optional[str] = None,
        conda_env_name: Optional[str] = None,
        project_path: Optional[Path] = None,
    ) -> None:
        super().__init__(config, python_interpreter=python_interpreter, environment_name=environment_name, conda_env_name=conda_env_name)
        self.project_path = project_path
        self.step_registry = get_step_registry()
        self.step_state_manager: StepStateManager | None = None
        self.networkx_executor: DaskNetworkXExecutor | None = None
        self.tracker: Any = None
        self.logger = logging.getLogger(__name__)

    def set_tracker(self, tracker: Any) -> None:
        self.tracker = tracker

    def _repo_root(self) -> Path:
        """Best-effort workspace root resolution (where projects/ lives)."""
        try:
            from mlops.core.workspace import get_workspace_root
            return get_workspace_root()
        except Exception:
            return Path.cwd()

    def _resolve_custom_script_path(self, custom_script_path: str) -> Path:
        p = Path(custom_script_path)
        if p.is_absolute() and p.exists():
            return p
        if p.exists():
            return p
        # Try relative to project path (for configs that use "models/foo.py")
        try:
            if self.project_path and (self.project_path / p).exists():
                return self.project_path / p
        except Exception:
            pass
        # Try relative to repo root (for configs that use "projects/<id>/models/foo.py")
        try:
            repo_root = self._repo_root()
            cand = repo_root / p
            if cand.exists():
                return cand
        except Exception:
            pass
        return p
        
    def initialize(self) -> None:
        """Initialize the adapter: import model module, configure caching, and set up the executor."""
        self.logger = logging.getLogger(__name__)

        custom_script_path = getattr(self.config.parameters, "custom_script_path", None)
        if not custom_script_path:
            raise ValueError("custom_script_path must be specified in configuration")
        custom_target = getattr(self.config.parameters, "custom_target", None)

        script_path = self._resolve_custom_script_path(str(custom_script_path))
        if not script_path.exists():
            raise FileNotFoundError(f"Custom script not found: {custom_script_path}")

        spec = importlib.util.spec_from_file_location("custom_model", str(script_path.resolve()))
        if spec is None or spec.loader is None:
            raise ImportError(f"Failed to create import spec for: {script_path}")
        custom_module = importlib.util.module_from_spec(spec)
        sys.modules["custom_model"] = custom_module
        spec.loader.exec_module(custom_module)  # type: ignore[attr-defined]

        if custom_target:
            if not hasattr(custom_module, custom_target):
                raise AttributeError(f"Target '{custom_target}' not found in {custom_script_path}")
            self.model_class = getattr(custom_module, custom_target)
            try:
                if not issubclass(self.model_class, MLOpsCustomModelBase):
                    self.logger.info(f"Target '{custom_target}' does not inherit MLOpsCustomModelBase; proceeding anyway.")
            except TypeError:
                pass

        self.logger.info(f"Imported model module from: {custom_script_path}")

        # Steps are registered via decorators during import.
        self.step_registry = get_step_registry()
        try:
            step_names = list(getattr(self.step_registry, "_steps", {}).keys())
            if not step_names:
                self.logger.warning("No steps found in registry. Ensure your model uses @step decorators.")
            else:
                self.logger.info(f"Found {len(step_names)} registered step(s)")
        except Exception:
            pass

        cache_config = getattr(self.config.parameters, "cache", {}) or {}
        cache_config = _as_dict(cache_config)
        cache_ttl_hours = cache_config.get("ttl_hours", 24) if isinstance(cache_config, dict) else 24

        step_cache_dir = (self.project_path / "cache" / "steps") if self.project_path else Path("step_cache")

        project_id_for_ns = self.project_path.name if self.project_path else "default"
        backend_cfg = _as_dict(cache_config.get("backend", {}))

        # Key-value store backend selection (config -> env -> in-memory).
        from mlops.storage.adapters.memory_store import InMemoryStore

        def _try_init_redis_from(cfg: dict) -> Optional[object]:
            try:
                from mlops.storage.adapters.redis_store import RedisStore
                return RedisStore(
                    project_id=project_id_for_ns,
                    host=cfg.get("host"),
                    port=cfg.get("port"),
                    db=cfg.get("db"),
                    password=cfg.get("password"),
                )
            except Exception as e:
                self.logger.warning(f"Redis backend unavailable: {e}")
                return None

        def _try_init_gcp_from(cfg: dict) -> Optional[object]:
            try:
                from mlops.storage.adapters.gcp_kv_store import GCPStore
                return GCPStore(
                    project_id=project_id_for_ns,
                    gcp_project=cfg.get("gcp_project") or os.getenv("GOOGLE_CLOUD_PROJECT"),
                    topic_name=cfg.get("topic_name"),
                    emulator_host=cfg.get("emulator_host") or os.getenv("FIRESTORE_EMULATOR_HOST"),
                )
            except Exception as e:
                self.logger.warning(f"GCP backend unavailable: {e}")
                return None

        backend_type = str(backend_cfg.get("type") or os.getenv("MLOPS_KV_BACKEND") or "redis").lower()
        kv_store = None
        if backend_type == "redis":
            cfg = dict(backend_cfg) if isinstance(backend_cfg, dict) else {}
            kv_store = _try_init_redis_from(
                {
                    "host": os.getenv("MLOPS_REDIS_HOST") or cfg.get("host"),
                    "port": os.getenv("MLOPS_REDIS_PORT") or cfg.get("port"),
                    "db": os.getenv("MLOPS_REDIS_DB") or cfg.get("db"),
                    "password": os.getenv("MLOPS_REDIS_PASSWORD") or cfg.get("password"),
                }
            )
            if kv_store:
                self.logger.info("Initialized Redis backend for key-value store")
        elif backend_type == "gcp":
            kv_store = _try_init_gcp_from(backend_cfg)
            if kv_store:
                self.logger.info("Initialized GCP Firestore/PubSub backend for key-value store")

        if kv_store is None:
            kv_store = _try_init_redis_from(
                {
                    "host": os.getenv("MLOPS_REDIS_HOST"),
                    "port": os.getenv("MLOPS_REDIS_PORT"),
                    "db": os.getenv("MLOPS_REDIS_DB"),
                    "password": os.getenv("MLOPS_REDIS_PASSWORD"),
                }
            )
        if kv_store is None:
            kv_store = _try_init_gcp_from(
                {
                    "gcp_project": os.getenv("GOOGLE_CLOUD_PROJECT"),
                    "emulator_host": os.getenv("FIRESTORE_EMULATOR_HOST"),
                }
            )
        if kv_store is None:
            kv_store = InMemoryStore(project_id_for_ns)
            self.logger.info("Using in-memory key-value store (non-persistent)")

        # Optional object store for cache artifacts.
        obj_store = None
        obj_prefix = None
        try:
            store_cfg = _as_dict(cache_config.get("object_store"))
            store_type = str(store_cfg.get("type", "")).lower()
            if store_type == "gcs":
                bucket = store_cfg.get("bucket") or os.getenv("MLOPS_GCS_BUCKET")
                prefix = store_cfg.get("prefix") or os.getenv("MLOPS_GCS_PREFIX")
                if bucket:
                    from mlops.storage.adapters.gcs_object_store import GCSObjectStore
                    # Prefix is applied by the object store, so StepStateManager should not add another prefix.
                    obj_store = GCSObjectStore(bucket=bucket, prefix=prefix)
                    obj_prefix = None
                    self.logger.info(f"Initialized GCS object store for cache artifacts (bucket={bucket}, prefix={prefix})")
        except Exception as e:
            self.logger.warning(f"Object store init failed; falling back to local cache files: {e}")

        self.step_state_manager = StepStateManager(
            cache_dir=step_cache_dir,
            kv_store=kv_store,
            logger=self.logger,
            cache_ttl_hours=cache_ttl_hours,
            object_store=obj_store,
            object_prefix=obj_prefix,
        )

        executor_config = _as_dict(getattr(self.config.parameters, "executor", {}) or {})
        env_workers = os.environ.get("MLOPS_N_WORKERS")
        try:
            n_workers = int(env_workers) if env_workers else int(executor_config.get("n_workers", 2))
        except Exception:
            n_workers = 2

        dask_tuning_cfg = _as_dict(executor_config.get("dask") or {})
        if isinstance(dask_tuning_cfg, dict) and not dask_tuning_cfg and executor_config.get("dask_config"):
            dask_tuning_cfg = _as_dict(executor_config.get("dask_config"))

        min_workers_override = _to_int(executor_config.get("min_workers")) if isinstance(executor_config, dict) else None
        wait_for_workers_override = _to_float(executor_config.get("wait_for_workers_sec")) if isinstance(executor_config, dict) else None
        if isinstance(dask_tuning_cfg, dict):
            if min_workers_override is None:
                min_workers_override = _to_int(dask_tuning_cfg.get("min_workers"))
            if wait_for_workers_override is None:
                wait_for_workers_override = _to_float(dask_tuning_cfg.get("wait_for_workers_sec"))

        dask_overrides: Dict[str, Any] = {}
        compression_setting = None
        if isinstance(dask_tuning_cfg, dict):
            comm_cfg = _as_dict(dask_tuning_cfg.get("comm") or {})
            if isinstance(comm_cfg, dict):
                compression_setting = comm_cfg.get("compression") or comm_cfg.get("codec")
            if compression_setting:
                dask_overrides["distributed.comm.compression"] = str(compression_setting)
            memory_cfg = _as_dict(dask_tuning_cfg.get("memory") or {})
            if isinstance(memory_cfg, dict):
                mem_map = {
                    "worker_target_fraction": "distributed.worker.memory.target",
                    "worker_spill_fraction": "distributed.worker.memory.spill",
                    "worker_pause_fraction": "distributed.worker.memory.pause",
                }
                for src_key, dst_key in mem_map.items():
                    val = memory_cfg.get(src_key)
                    if val is not None:
                        try:
                            dask_overrides[dst_key] = float(val)
                        except Exception:
                            dask_overrides[dst_key] = val
            overrides_block = dask_tuning_cfg.get("overrides")
            if isinstance(overrides_block, dict):
                for key, value in overrides_block.items():
                    if isinstance(key, str):
                        dask_overrides[key] = value

        if compression_setting:
            try:
                os.environ.setdefault("MLOPS_DASK_COMPRESSION", str(compression_setting))
            except Exception:
                pass

        scheduler_address = executor_config.get("scheduler_address") or os.environ.get("DASK_SCHEDULER_ADDRESS")
        scheduler_mode = "distributed" if scheduler_address else "threads"

        extra_files_to_upload: list[str] = []
        try:
            extra_files_to_upload = [str(script_path)]
        except Exception:
            extra_files_to_upload = []
        # Upload reporting entrypoint for worker-side chart imports (best-effort).
        try:
            rep_cfg_text = os.environ.get("MLOPS_REPORTING_CONFIG") or ""
            if rep_cfg_text:
                rep_cfg = json.loads(rep_cfg_text) or {}
                ep = rep_cfg.get("static_entrypoint") or rep_cfg.get("entrypoint")
                if isinstance(ep, str) and ep.strip():
                    p = Path(ep)
                    if not p.is_absolute():
                        p = self._repo_root() / p
                    if p.exists():
                        extra_files_to_upload.append(str(p))
        except Exception:
            pass

        self.networkx_executor = DaskNetworkXExecutor(
            step_registry=self.step_registry,
            state_manager=self.step_state_manager,
            logger=self.logger,
            n_workers=n_workers,
            scheduler_mode=scheduler_mode,
            scheduler_address=scheduler_address,
            client=None,
            extra_files_to_upload=extra_files_to_upload,
            min_workers=min_workers_override,
            wait_for_workers_sec=wait_for_workers_override,
            dask_config_overrides=dask_overrides,
        )
        mode_label = "distributed" if scheduler_mode == "distributed" else "threads"
        self.logger.info(f"Initialized Dask NetworkX executor with {n_workers} workers ({mode_label} scheduler)")
        
        self.logger.info("Enhanced caching with function hashing: ENABLED")

        # Make state manager available for manual step-level caching in decorators
        try:
            from mlops.core.step_system import set_state_manager as _set_sm
            _set_sm(self.step_state_manager)
        except Exception:
            pass
        
        

    def _execute_step_graph(self, run_id: str, data_paths: Dict[str, Path], tracker: Any = None, **kwargs) -> Dict[str, Any]:
        """Execute the configured pipeline once."""
        if not self.networkx_executor or not self.step_state_manager:
            raise RuntimeError("NetworkX execution not properly initialized")
            
        pipeline_config = self.config.parameters.pipeline
        if not pipeline_config:
            raise ValueError("NetworkX executor requires pipeline configuration with 'processes' and 'steps' sections")
            
        pipeline_dict = pipeline_config.model_dump() if hasattr(pipeline_config, 'model_dump') else pipeline_config
        
        if "processes" not in pipeline_dict:
            raise ValueError(
                "NetworkX executor requires 'processes' section in pipeline configuration. "
                "Legacy 'main_flow' syntax is no longer supported. "
                "Please use the NetworkX format with processes and steps."
            )
        
        networkx_config = parse_networkx_pipeline_from_config(pipeline_dict)
        
        project_id = self.project_path.name if self.project_path else "default"
        
        context_factory = get_context_factory()
        global_cfg = _as_dict(self.config.parameters)
        overrides = kwargs.get("global_config_overrides")
        if isinstance(overrides, dict) and overrides:
            global_cfg = {**global_cfg, **overrides}

        context = context_factory.create_context(
            project_id=project_id,
            run_id=run_id,
            tracker=tracker,
            global_config=global_cfg,
            data_paths=data_paths,
            checkpoint_dir=self.project_path / "artifacts" / "checkpoints" if self.project_path else Path("artifacts/checkpoints")
        )
        
        set_current_context(context)
        
        try:
            resume_from_process = kwargs.get("resume_from_process")
            config_hash = self.step_state_manager._compute_config_hash(pipeline_dict)
            
            if resume_from_process and self.step_state_manager.can_resume_from_step(run_id, resume_from_process, config_hash):
                self.logger.info(f"Resuming execution from process: {resume_from_process}")
                context.step_results = self.step_state_manager.get_step_results(run_id)
            else:
                self.step_state_manager.start_pipeline_execution(run_id, pipeline_dict)
                
            single_process = kwargs.get("single_process", False)
            execution_results = self.networkx_executor.execute_graph(
                networkx_config,
                context,
                run_id=run_id,
                resume_from_process=resume_from_process,
                stop_after_process=single_process,
            )
            
            results = {}
            
            for process_name, process_result in execution_results.items():
                if process_result.error is None:  # success check for simplified result
                    if process_result.result:
                        result_dict = process_result.result
                        results[f"{process_name}_result"] = result_dict
                        
                        if process_name == "model_training" and result_dict:
                            training_summary = {}
                            if 'model' in result_dict:
                                model = result_dict['model']
                                if hasattr(model, 'get_training_metrics'):
                                    training_summary['model_metrics'] = model.get_training_metrics()
                                training_summary['model_type'] = type(model).__name__
                            results[f"{process_name}_summary"] = training_summary
                        
                        elif process_name == "evaluate_model" and result_dict:
                            evaluation_summary = {}
                            if 'evaluation_metrics' in result_dict:
                                evaluation_summary['final_metrics'] = result_dict['evaluation_metrics']
                            if 'predictions' in result_dict:
                                evaluation_summary['prediction_count'] = len(result_dict['predictions'])
                            results[f"{process_name}_summary"] = evaluation_summary
                
                else:
                    results[f"{process_name}_error"] = process_result.error
                    self.logger.error(f"Process {process_name} failed: {process_result.error}")
            
            return results
            
        finally:
            set_current_context(None)

    def run(self, data_paths: Dict[str, Path] | None = None, **kwargs) -> Dict[str, Any]:
        """Run the pipeline once according to the configured processes/steps."""
        run_id = kwargs.pop("run_id", f"run_{int(time.time())}")
        tracker = kwargs.pop("tracker", self.tracker)
        normalized_paths: Dict[str, Path] = data_paths or {}
        return self._execute_step_graph(run_id=run_id, data_paths=normalized_paths, tracker=tracker, **kwargs)

    def save_model(self, model_path: str, **kwargs) -> None:
        """Save model artifacts (handled automatically by step system)."""
        self.logger.info(f"Model artifacts will be saved automatically by the step system to: {model_path}")

    def load_model(self, model_path: str, **kwargs) -> Any:
        """Load model artifacts (handled automatically by step system)."""
        self.logger.info(f"Model artifacts will be loaded automatically by the step system from: {model_path}")
        return None

        

    @classmethod
    def validate_config(cls, config: AdapterConfig) -> bool:
        """Validate the adapter configuration."""
        try:
            if not config.parameters.custom_script_path:
                return False
            if not config.parameters.pipeline:
                return False
            pipeline_dict = config.parameters.pipeline.model_dump() if hasattr(config.parameters.pipeline, 'model_dump') else config.parameters.pipeline
            if "processes" not in pipeline_dict:
                return False
            return True
        except Exception:
            return False

    def save(self, path: Path) -> None:
        """Save adapter state."""
        pass

    def load(self, path: Path) -> None:
        """Load adapter state."""
        pass

Adapter = CustomModelAdapter 