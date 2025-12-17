from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from datetime import datetime
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import time
import uuid

import yaml

from .adapters.plugin_manager import AdapterPluginManager
from .adapters.config_schema import AdapterConfig
from .managers.reproducibility_manager import ReproducibilityManager
from .managers.project_manager import ProjectManager
from .tracking.plugin_manager import TrackerPluginManager
from .tracking.base import ExperimentTracker, NoOpExperimentTracker
from .core.workspace import get_projects_root, get_workspace_root, infer_source_root


class MLPlatform:
    """Main platform class that orchestrates the ML pipeline."""
    
    def __init__(self) -> None:
        self.adapter_manager = AdapterPluginManager()
        # Adapter discovery already tries both `mlops.*` and `src.mlops.*` layouts.
        self.adapter_manager.discover_adapters("mlops.adapters")
        
        self.tracker_plugin_manager = TrackerPluginManager()
        self.tracker_plugin_manager.discover_trackers("mlops.tracking.plugins")
        # Ensure a fallback tracker is always available even if plugin discovery fails.
        self.tracker_plugin_manager._trackers.setdefault("noop", NoOpExperimentTracker)

        # Track output directories of dynamic charts so we can upload artifacts later.
        self._dynamic_chart_outputs: list[tuple[str, Path]] = []

    def _initialize_tracker(self, platform_config: Dict[str, Any]) -> ExperimentTracker:
        """Initialize experiment tracker from configuration."""
        logger = logging.getLogger(__name__)
        tracking_config = platform_config.get("reproducibility", {}).get("experiment_tracking", {})
        tracker_name = tracking_config.get("backend", "noop")
        tracker_params = tracking_config.get("parameters", {})

        tracker: ExperimentTracker | None = None
        try:
            tracker = self.tracker_plugin_manager.create_tracker(tracker_name, config=tracker_params)
        except Exception as e:
            logger.warning(f"Failed to initialize tracker '{tracker_name}': {e}. Falling back to NoOpExperimentTracker.")
            tracker = None
        if tracker is None:
            logger.warning(f"Tracker '{tracker_name}' not available. Falling back to NoOpExperimentTracker.")
            tracker = NoOpExperimentTracker(config=tracker_params)
        return tracker

    def _repo_root(self) -> Path:
        # Legacy name; this is now the workspace root (where projects/ lives).
        try:
            return get_workspace_root()
        except Exception:
            return Path.cwd()

    def _set_env_var(self, key: str, value: str) -> None:
        """Best-effort environment variable setter (never raises)."""
        try:
            os.environ[key] = value
        except Exception:
            pass

    def _get_reporting_python_exec(self) -> str:
        try:
            return getattr(self, "_reporting_python", None) or os.environ.get("MLOPS_REPORTING_PYTHON") or sys.executable
        except Exception:
            return sys.executable

    def _in_distributed_mode(self) -> bool:
        return bool(os.environ.get("DASK_SCHEDULER_ADDRESS") or os.environ.get("MLOPS_CLUSTER_MODE"))

    def _get_project_id_from_adapter(self, adapter: Any) -> str:
        try:
            ssm = getattr(adapter, 'step_state_manager', None)
            kv = getattr(ssm, 'kv_store', None) if ssm else None
            return (getattr(kv, 'project_id', None) if kv else None) or os.environ.get("MLOPS_PROJECT_ID") or ""
        except Exception:
            return os.environ.get("MLOPS_PROJECT_ID") or ""

    def _get_project_dir_hint(self, project_id: str):
        try:
            pm = ProjectManager()
            return pm.get_project_path(project_id)
        except Exception:
            return None

    def _resolve_entrypoint_path(self, entrypoint: str, project_dir_hint: Path | None = None) -> Path | None:
        try:
            ep = Path(entrypoint)
            if ep.is_absolute() and ep.exists():
                return ep
            if ep.exists():
                return ep
            if project_dir_hint:
                cand = (Path(project_dir_hint) / entrypoint)
                if cand.exists():
                    return cand
            ws = self._repo_root()
            cand = (ws / entrypoint)
            return cand if cand.exists() else None
        except Exception:
            return None

    def _default_reporting_entrypoint_path(self) -> Path | None:
        """Return the built-in reporting entrypoint file path (inside the installed package)."""
        try:
            import mlops.reporting.entrypoint as _entry
            p = Path(getattr(_entry, "__file__", "") or "")
            return p if p.exists() else None
        except Exception:
            return None

    def _maybe_apply_cache_env(self, env: dict, platform_config: Dict[str, Any], project_dir_hint) -> None:
        cache_cfg = ((platform_config.get("model") or {}).get("parameters") or {}).get("cache") or {}
        if not isinstance(cache_cfg, dict):
            return
        backend_cfg = cache_cfg.get("backend") or {}
        if not isinstance(backend_cfg, dict):
            return

        gcp_project = backend_cfg.get("gcp_project")
        if gcp_project:
            env["MLOPS_GCP_PROJECT"] = str(gcp_project)
        emulator_host = backend_cfg.get("emulator_host")
        if emulator_host:
            env["FIRESTORE_EMULATOR_HOST"] = str(emulator_host)
        creds_path = backend_cfg.get("credentials_json")
        if creds_path:
            try:
                creds_path_val = str(creds_path)
                if not Path(creds_path_val).is_absolute() and project_dir_hint:
                    creds_path_val = str(Path(project_dir_hint) / creds_path_val)
                env["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path_val
            except Exception:
                pass

    def _ensure_repo_src_on_pythonpath(self, env: dict) -> None:
        src_root = infer_source_root()
        if not src_root:
            return
        repo_src = str(src_root / "src")
        prev_pp = str(env.get("PYTHONPATH", "") or "")
        if repo_src in prev_pp.split(":"):
            return
        env["PYTHONPATH"] = f"{repo_src}:{prev_pp}".rstrip(":")

    def _compute_config_hash(self, config_content: Dict[str, Any]) -> str:
        """Compute a stable hash of the configuration content (excluding run_id)."""
        logger = logging.getLogger(__name__)
        try:
            config_copy = dict(config_content)
            config_copy.pop("run_id", None)
            
            config_str = json.dumps(config_copy, sort_keys=True, default=str, separators=(",", ":"))
            
            return hashlib.sha256(config_str.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to compute config hash: {e}. Falling back to random UUID-based hash.")
            return str(uuid.uuid4()).replace("-", "")[:16]

    def _generate_run_id(self, platform_config: Dict[str, Any], project_id: str | None = None) -> str:
        """Generate or extract run ID from configuration."""
        run_id_from_config = platform_config.get("run_id") 
        if run_id_from_config and run_id_from_config not in ["${RUN_ID:-auto-generated}", "auto-generated"]:
            return str(run_id_from_config)
        
        # Always add a unique suffix so every execution has a distinct run_id
        unique_suffix = datetime.utcnow().strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:8]
        if project_id:
            return f"project-{project_id}-{unique_suffix}"
        return f"config-{unique_suffix}"

    def _prepare_run_metadata(self, platform_config: Dict[str, Any], run_id: str) -> Dict[str, Any]:
        """Prepare run metadata for tracking."""
        run_name = platform_config.get("metadata", {}).get("name", "ml-pipeline-run")
        run_tags = platform_config.get("metadata", {}).get("tags", {})
        if isinstance(run_tags, list):
            run_tags = {tag: "true" for tag in run_tags}
        
        return {
            "run_name": f"{run_name}-{run_id[:8]}",
            "run_id": run_id,
            "tags": run_tags
        }

    def _execute_pipeline(self, adapter, platform_config: Dict[str, Any], run_id: str, tracker: ExperimentTracker) -> Dict[str, Any]:
        """Execute the ML pipeline using the specified adapter."""
        logger = logging.getLogger(__name__)
        print(f"[MLPlatform] Starting pipeline execution for run_id: {run_id}")
        
        try:
            self._preregister_chart_probe_paths(adapter, platform_config, run_id)
        except Exception as e:
            logger.warning(f"Failed to pre-register chart probe paths: {e}")
        
        dynamic_chart_processes = []
        try:
            reporting_cfg = (platform_config or {}).get("reporting") or {}
            if isinstance(reporting_cfg, dict) and reporting_cfg.get("enabled"):
                dynamic_chart_processes = self._start_dynamic_charts(adapter, platform_config, run_id)
        except Exception as _dynamic_e:
            logger.warning(f"Failed to start dynamic charts: {_dynamic_e}")
        
        data_sources = platform_config.get("data", {}).get("sources", {})
        training_params = platform_config.get("training", {}).get("parameters", {})

        training_path_cfg = data_sources.get("training") or {}
        validation_path_cfg = data_sources.get("validation") or {}

        training_data_path = Path(training_path_cfg["path"]) if isinstance(training_path_cfg, dict) and training_path_cfg.get("path") else None
        validation_data_path = Path(validation_path_cfg["path"]) if isinstance(validation_path_cfg, dict) and validation_path_cfg.get("path") else None

        adapter_kwargs = dict(training_params) if isinstance(training_params, dict) else {}
        adapter_kwargs["data_paths"] = {}
        if training_data_path:
            adapter_kwargs["data_paths"]["training"] = training_data_path
        if validation_data_path:
            adapter_kwargs["data_paths"]["validation"] = validation_data_path

        # Provide selected top-level sections to adapters/workers for cache hashing hooks.
        full_cfg_hash = self._compute_config_hash(platform_config)
        self._set_env_var("MLOPS_PROJECT_CONFIG_HASH", str(full_cfg_hash))
        adapter_kwargs["global_config_overrides"] = {
            "reproducibility": (platform_config.get("reproducibility", {}) or {}),
            "data": (platform_config.get("data", {}) or {}),
            "project_config_file_hash": full_cfg_hash,
        }

        # Give adapters a chance to attach the tracker instance if they support it.
        try:
            if hasattr(adapter, "set_tracker"):
                adapter.set_tracker(tracker)
        except Exception:
            pass

        # Pass run_id + tracker down so adapters can keep storage/tracking consistent.
        pipeline_results = adapter.run(
            data_paths=adapter_kwargs.get("data_paths"),
            run_id=run_id,
            tracker=tracker,
            **{k: v for k, v in adapter_kwargs.items() if k != "data_paths"}
        )
        print(f"[MLPlatform] Pipeline completed")

        try:
            reporting_cfg = (platform_config or {}).get("reporting") or {}
            if isinstance(reporting_cfg, dict) and reporting_cfg.get("enabled"):
                is_distributed = self._in_distributed_mode()
                if dynamic_chart_processes:
                    if is_distributed:
                        logger.info(f"Dynamic chart jobs submitted to cluster: {', '.join(dynamic_chart_processes)}")
                    else:
                        pids = ", ".join([str(p.pid) for p in dynamic_chart_processes if getattr(p, "pid", None)])
                        logger.info(f"Dynamic chart(s) running in background (PIDs: {pids})")
                
                # Best-effort: upload artifacts produced by dynamic charts (async)
                try:
                    self._upload_dynamic_chart_artifacts_async(adapter, run_id)
                except Exception as _dyn_up_e:
                    logger.warning(f"Dynamic chart artifact upload failed: {_dyn_up_e}")
        except Exception as _report_e:
            logger.warning(f"Reporting failed: {_report_e}")

        return {
            "run_id": run_id,
            "pipeline_results": pipeline_results
        }

    def _preregister_chart_probe_paths(self, adapter: Any, platform_config: Dict[str, Any], run_id: str) -> None:
        """No-op retained for backwards compatibility."""
        logging.getLogger(__name__).debug("Probe path pre-registration is a no-op (path-based metrics).")

    def _get_reporting_cfg(self, platform_config: Dict[str, Any]) -> Dict[str, Any]:
        cfg = (platform_config or {}).get("reporting") or {}
        return cfg if isinstance(cfg, dict) else {}

    def _get_reporting_entrypoint(self, reporting_cfg: Dict[str, Any]) -> str:
        return str(reporting_cfg.get("static_entrypoint") or reporting_cfg.get("entrypoint") or "").strip()

    def _get_dynamic_chart_specs(self, reporting_cfg: Dict[str, Any]) -> list[dict]:
        charts = reporting_cfg.get("charts") or []
        if not isinstance(charts, list):
            return []
        out: list[dict] = []
        for c in charts:
            if isinstance(c, dict) and str(c.get("type", "")).lower() == "dynamic":
                out.append(c)
        return out

    def _resolve_reporting_entry_to_run(self, configured_entry: Path) -> tuple[Path, str | None]:
        """Resolve the actual script/module to run for reporting.

        If config points to a user script, run the framework entrypoint and import the user file.
        """
        default_entry = self._default_reporting_entrypoint_path()
        if default_entry is None:
            return configured_entry, None
        try:
            if configured_entry.resolve() != default_entry.resolve():
                return default_entry, str(configured_entry)
        except Exception:
            pass
        return default_entry, None

    def _start_dynamic_charts(self, adapter: Any, platform_config: Dict[str, Any], run_id: str) -> list:
        """Start dynamic charts as background processes (local) or cluster jobs (distributed).
        
        Returns list of subprocess.Popen objects (local) or job IDs (distributed) for tracking.
        """
        logger = logging.getLogger(__name__)
        
        # Detect if we're in cluster/distributed mode
        is_distributed = self._in_distributed_mode()
        
        if is_distributed:
            logger.info("Detected distributed mode - will submit dynamic charts as cluster jobs")
            return self._start_dynamic_charts_distributed(adapter, platform_config, run_id)
        else:
            logger.info("Local mode - will run dynamic charts as background processes")
            return self._start_dynamic_charts_local(adapter, platform_config, run_id)
    
    def _start_dynamic_charts_local(self, adapter: Any, platform_config: Dict[str, Any], run_id: str) -> list:
        """Start dynamic charts as local background processes.
        
        Returns list of subprocess.Popen objects for the started dynamic chart processes.
        """
        logger = logging.getLogger(__name__)
        
        project_id = self._get_project_id_from_adapter(adapter)
        
        reporting_cfg = self._get_reporting_cfg(platform_config)
        entrypoint = self._get_reporting_entrypoint(reporting_cfg)
        if not entrypoint:
            return []
        
        args = list(reporting_cfg.get("args") or [])
        
        dynamic_charts = self._get_dynamic_chart_specs(reporting_cfg)
        if not dynamic_charts:
            return []
        
        reporting_python = self._get_reporting_python_exec()
        
        project_dir_hint = self._get_project_dir_hint(project_id)
        entry = self._resolve_entrypoint_path(entrypoint, project_dir_hint=project_dir_hint)
        if not entry:
            logger.warning(f"Reporting entrypoint not found: {entrypoint}")
            return []

        # Output under the project artifacts directory
        try:
            if project_dir_hint:
                output_base = Path(project_dir_hint) / "artifacts" / "charts" / run_id
            else:
                output_base = get_projects_root(self._repo_root()) / project_id / "artifacts" / "charts" / run_id
        except Exception:
            output_base = Path.cwd() / "projects" / project_id / "artifacts" / "charts" / run_id

        default_entry = self._default_reporting_entrypoint_path()
        
        dynamic_processes = []
        
        for spec in dynamic_charts:
            name = str(spec.get("name") or "dynamic_chart").strip()
            chart_out = output_base / name / time.strftime("%Y%m%d_%H%M%S")
            
            try:
                chart_out.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
            # Track for later upload
            try:
                self._dynamic_chart_outputs.append((name, chart_out))
            except Exception:
                pass
            
            env = os.environ.copy()
            if project_id:
                env["MLOPS_PROJECT_ID"] = project_id
            env["MLOPS_OUTPUT_DIR"] = str(chart_out)
            env["MLOPS_CHART_NAME"] = name
            env["MLOPS_RUN_ID"] = run_id
            env["MLOPS_CHART_TYPE"] = "dynamic"
            
            self._maybe_apply_cache_env(env, platform_config, project_dir_hint)
            
            if "probe_paths" in spec:
                try:
                    env["MLOPS_PROBE_PATHS"] = json.dumps(spec.get("probe_paths"))
                except Exception:
                    pass

            entry_to_run, import_file = self._resolve_reporting_entry_to_run(entry)
            try:
                if import_file:
                    env["MLOPS_CHART_IMPORT_FILES"] = import_file
            except Exception:
                pass
            
            try:
                self._ensure_repo_src_on_pythonpath(env)
            except Exception as _path_e:
                logger.warning(f"Failed to set PYTHONPATH for dynamic chart '{name}': {_path_e}")
            
            spec_args = list(spec.get("args") or [])
            run_as_module = bool(default_entry and entry_to_run and entry_to_run.resolve() == default_entry.resolve())
            if run_as_module:
                cmd = [reporting_python, "-u", "-m", "mlops.reporting.entrypoint"] + args + spec_args
            else:
                cmd = [reporting_python, "-u", str(entry_to_run)] + args + spec_args
            
            try:
                logger.info(f"Starting dynamic chart '{name}' in background -> {chart_out}")
                stdout_log = chart_out / "stdout.log"
                stderr_log = chart_out / "stderr.log"

                stdout_file = open(stdout_log, "a", buffering=1)
                stderr_file = open(stderr_log, "a", buffering=1)
                try:
                    proc = subprocess.Popen(cmd, env=env, stdout=stdout_file, stderr=stderr_file, cwd=str(self._repo_root()))
                finally:
                    # Close in parent; child keeps its own fds.
                    try:
                        stdout_file.close()
                    except Exception:
                        pass
                    try:
                        stderr_file.close()
                    except Exception:
                        pass
                dynamic_processes.append(proc)
                logger.info(f"Dynamic chart '{name}' started with PID {proc.pid}, logs: stdout={stdout_log}, stderr={stderr_log}")
            except Exception as _e:
                logger.warning(f"Failed to start dynamic chart '{name}': {_e}")
        
        if dynamic_processes:
            logger.info(f"Started {len(dynamic_processes)} dynamic chart(s) in background")
        
        return dynamic_processes
    
    def _start_dynamic_charts_distributed(self, adapter: Any, platform_config: Dict[str, Any], run_id: str) -> list:
        """Start dynamic charts via the configured cluster provider.

        Returns list of provider-specific job identifiers (strings)."""
        provider = self._get_cluster_provider_name(adapter)
        if provider == "slurm":
            return self._start_dynamic_charts_distributed_slurm(adapter, platform_config, run_id)
        elif provider == "ansible":
            # Run on head node as a fallback; return labels as job ids
            procs = self._start_dynamic_charts_local(adapter, platform_config, run_id)
            return [f"pid-{getattr(p, 'pid', 'unknown')}" for p in (procs or [])]
        else:
            logging.getLogger(__name__).warning(f"Unknown cluster provider '{provider}'. Falling back to local dynamic charts.")
            procs = self._start_dynamic_charts_local(adapter, platform_config, run_id)
            return [f"pid-{getattr(p, 'pid', 'unknown')}" for p in (procs or [])]

    def _get_cluster_provider_name(self, adapter: Any) -> str:
        """Determine the cluster provider from env or project cluster_config.yaml."""
        try:
            prov = os.environ.get("MLOPS_CLUSTER_PROVIDER")
            if isinstance(prov, str) and prov.strip():
                return prov.strip().lower()
        except Exception:
            pass
        # Try project cluster_config.yaml
        project_id = self._get_project_id_from_adapter(adapter)
        project_dir_hint = self._get_project_dir_hint(project_id)
        if project_dir_hint:
            cfg_path = Path(project_dir_hint) / "configs" / "cluster_config.yaml"
        else:
            cfg_path = get_projects_root(self._repo_root()) / project_id / "configs" / "cluster_config.yaml"
        try:
            if cfg_path.exists():
                with open(cfg_path) as f:
                    data = yaml.safe_load(f) or {}
                provider = data.get("provider")
                if isinstance(provider, str) and provider.strip():
                    return provider.strip().lower()
        except Exception:
            pass
        return "slurm"

    def _start_dynamic_charts_distributed_slurm(self, adapter: Any, platform_config: Dict[str, Any], run_id: str) -> list:
        """Start dynamic charts by submitting SLURM sbatch jobs."""
        logger = logging.getLogger(__name__)

        project_id = self._get_project_id_from_adapter(adapter)

        reporting_cfg = self._get_reporting_cfg(platform_config)
        entrypoint = self._get_reporting_entrypoint(reporting_cfg)
        if not entrypoint:
            return []

        args = list(reporting_cfg.get("args") or [])
        dynamic_charts = self._get_dynamic_chart_specs(reporting_cfg)
        if not dynamic_charts:
            return []

        reporting_python = self._get_reporting_python_exec()
        project_dir_hint = self._get_project_dir_hint(project_id)
        entry = self._resolve_entrypoint_path(entrypoint, project_dir_hint=project_dir_hint)
        if not entry:
            logger.warning(f"Reporting entrypoint not found: {entrypoint}")
            return []

        # Output under the project artifacts directory
        try:
            if project_dir_hint:
                output_base = Path(project_dir_hint) / "artifacts" / "charts" / run_id
            else:
                output_base = get_projects_root(self._repo_root()) / project_id / "artifacts" / "charts" / run_id
        except Exception:
            output_base = Path.cwd() / "projects" / project_id / "artifacts" / "charts" / run_id

        default_entry = self._default_reporting_entrypoint_path()
        entry_to_run, import_file = self._resolve_reporting_entry_to_run(entry)
        run_as_module = bool(default_entry and entry_to_run and entry_to_run.resolve() == default_entry.resolve())

        job_ids: list[str] = []
        for spec in dynamic_charts:
            name = str(spec.get("name") or "dynamic_chart").strip()
            chart_out = output_base / name / time.strftime("%Y%m%d_%H%M%S")
            try:
                chart_out.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
            try:
                self._dynamic_chart_outputs.append((name, chart_out))
            except Exception:
                pass

            env_vars = []
            if project_id:
                env_vars.append(f"MLOPS_PROJECT_ID={project_id}")
            try:
                env_vars.append(f"MLOPS_WORKSPACE_DIR={self._repo_root()}")
                env_vars.append(f"MLOPS_REPO_ROOT={self._repo_root()}")  # legacy alias
            except Exception:
                pass
            env_vars.append(f"MLOPS_OUTPUT_DIR={chart_out}")
            env_vars.append(f"MLOPS_CHART_NAME={name}")
            env_vars.append(f"MLOPS_RUN_ID={run_id}")
            env_vars.append(f"MLOPS_CHART_TYPE=dynamic")

            # Add import file if using user script
            if import_file:
                env_vars.append(f"MLOPS_CHART_IMPORT_FILES={import_file}")

            tmp_env = {}
            self._maybe_apply_cache_env(tmp_env, platform_config, project_dir_hint)
            for k, v in tmp_env.items():
                env_vars.append(f"{k}={v}")

            if "probe_paths" in spec:
                try:
                    probe_paths_json = json.dumps(spec.get("probe_paths")).replace('"', '\\"')
                    env_vars.append(f'MLOPS_PROBE_PATHS="{probe_paths_json}"')
                except Exception:
                    pass

            try:
                src_root = infer_source_root()
                if src_root and (src_root / "src").exists():
                    repo_src = str(src_root / "src")
                    env_vars.append(f"PYTHONPATH={repo_src}:$PYTHONPATH")
            except Exception:
                pass

            chart_cmd_args = args + list(spec.get("args") or [])
            
            if run_as_module:
                chart_cmd = f"{reporting_python} -u -m mlops.reporting.entrypoint {' '.join(chart_cmd_args)}"
            else:
                chart_cmd = f"{reporting_python} -u {entry_to_run} {' '.join(chart_cmd_args)}"

            sbatch_script = f"""#!/bin/bash
#SBATCH --job-name={name}
#SBATCH --output={chart_out}/slurm-%j.out
#SBATCH --error={chart_out}/slurm-%j.err
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

# Export environment variables
{chr(10).join(f'export {var}' for var in env_vars)}

# Run the chart
{chart_cmd}
"""

            script_path = chart_out / f"submit_{name}.sh"
            try:
                script_path.write_text(sbatch_script)
                script_path.chmod(0o755)
            except Exception as e:
                logger.warning(f"Failed to write sbatch script for '{name}': {e}")
                continue

            try:
                logger.info(f"Submitting dynamic chart '{name}' to cluster -> {chart_out}")
                result = subprocess.run(["sbatch", str(script_path)], capture_output=True, text=True, check=True)
                output = result.stdout.strip()
                if "Submitted batch job" in output:
                    job_id = output.split()[-1]
                    job_ids.append(job_id)
                    logger.info(f"Dynamic chart '{name}' submitted as job {job_id}")
                else:
                    logger.warning(f"Unexpected sbatch output for '{name}': {output}")
            except Exception as e:
                logger.warning(f"Failed to submit dynamic chart '{name}': {e}")

        if job_ids:
            logger.info(f"Submitted {len(job_ids)} dynamic chart(s) to cluster: {', '.join(job_ids)}")
        return job_ids
    
    def _upload_dynamic_chart_artifacts_async(self, adapter: Any, run_id: str) -> None:
        """Upload PNG artifacts from dynamic chart output directories asynchronously.
        
        This runs in a background thread to avoid blocking the main execution flow.
        """
        import threading
        logger = logging.getLogger(__name__)
        
        def _upload_worker():
            try:
                self._upload_dynamic_chart_artifacts(adapter, run_id)
            except Exception as e:
                logger.warning(f"Async dynamic chart upload failed: {e}")
        
        # Start upload in background thread
        upload_thread = threading.Thread(target=_upload_worker, daemon=True)
        upload_thread.start()
        logger.info("Dynamic chart artifact upload started in background")

    def _upload_dynamic_chart_artifacts(self, adapter: Any, run_id: str) -> None:
        """Upload PNG artifacts from dynamic chart output directories and record them in KV.
        
        Best-effort: skips silently if directories are missing or object store is unavailable.
        """
        logger = logging.getLogger(__name__)
        try:
            tracked: list = getattr(self, "_dynamic_chart_outputs", []) or []
        except Exception:
            tracked = []
        if not tracked:
            return
        uploaded_any = False
        for item in tracked:
            try:
                name, chart_out = item
            except Exception:
                continue
            try:
                # Ensure path is a Path
                chart_out = Path(chart_out)
            except Exception:
                continue
            if not chart_out.exists():
                # Skip missing dirs (e.g., remote-only paths)
                continue
            try:
                self._upload_single_chart_artifacts(adapter, run_id, name, chart_out, chart_type="dynamic")
                uploaded_any = True
            except Exception as _e:
                logger.warning(f"Dynamic chart upload failed for '{name}': {_e}")
        if uploaded_any:
            logger.info("Uploaded dynamic chart artifacts and recorded in KV store")

    def _upload_single_chart_artifacts(self, adapter: Any, run_id: str, name: str, chart_out: Path, chart_type: str | None = None) -> None:
        """Upload PNG artifacts for a single chart and record them in KV.

        chart_type: optional "static" or "dynamic" for UI differentiation.
        """
        logger = logging.getLogger(__name__)
        ssm = getattr(adapter, 'step_state_manager', None)
        obj_store = getattr(ssm, 'object_store', None) if ssm else None
        kv = getattr(ssm, 'kv_store', None) if ssm else None
        try:
            project_ns = os.environ.get('MLOPS_PROJECT_ID', '')
        except Exception:
            project_ns = ''
        # If bucket known, build absolute gs:// directory prefix for improved UX
        abs_charts_root = None
        try:
            if obj_store and hasattr(obj_store, '_bucket') and getattr(obj_store, '_bucket') is not None:
                bname = getattr(getattr(obj_store, '_bucket'), 'name', None)
                if bname:
                    abs_charts_root = f"gs://{bname}/projects/{project_ns}/charts/{run_id}"
        except Exception:
            abs_charts_root = None
        import time as _time
        artifacts: list[dict] = []
        # Capture PNGs recursively to support nested structures under chart output
        for p in chart_out.rglob("*.png"):
            obj_path = None
            # Always capture local cache path so UI can fetch from server if object store is unavailable
            try:
                local_path = str(p.resolve())
            except Exception:
                local_path = str(p)
            if obj_store:
                try:
                    base = f"projects/{project_ns}/charts/{run_id}/{name}"
                    if abs_charts_root:
                        base = f"{abs_charts_root}/{name}"
                    remote = obj_store.build_uri(base, p.name)
                    with open(p, 'rb') as f:
                        obj_store.put_bytes(remote, f.read(), content_type="image/png")
                    obj_path = remote
                except Exception as _ue:
                    logger.warning(f"Upload failed for chart '{name}' file {p.name}: {_ue}")
            if not obj_path:
                # Fallback to local cache path if no remote object path
                obj_path = local_path
            try:
                artifacts.append({
                    "title": p.name,
                    "object_path": obj_path,
                    "cache_path": local_path,
                    "mime_type": "image/png",
                    "size_bytes": p.stat().st_size,
                    "created_at": _time.time(),
                    "chart_type": (chart_type or "static"),
                })
            except Exception:
                pass
        # Record artifacts in KV store for UI listing
        try:
            if kv and hasattr(kv, 'record_run_chart_artifacts'):
                kv.record_run_chart_artifacts(run_id, name, artifacts)
        except Exception:
            pass
    

    # -------------------- Cloud bootstrap helpers --------------------

    def _configure_logging(self, config: Dict[str, Any], project_path: Path) -> None:
        """Configure Python logging system based on the config.

        Honors MLOPS_RUN_LOG_FILE env var to force a unique per-run log file.
        """
        # Prefer explicit per-run log path if it is timestamped; otherwise, create a timestamped file.
        env_log = os.environ.get("MLOPS_RUN_LOG_FILE")
        chosen_log_file: str
        if env_log:
            try:
                name = Path(env_log).name
                pattern = rf"^{re.escape(project_path.name)}_\d{{8}}_\d{{6}}\.log$"
                if re.match(pattern, name):
                    chosen_log_file = env_log
                else:
                    raise ValueError("Non-timestamped log path provided; overriding with timestamped path")
            except Exception:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                chosen_log_file = str(project_path / "logs" / f"{project_path.name}_{ts}.log")
                self._set_env_var("MLOPS_RUN_LOG_FILE", chosen_log_file)
        else:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            chosen_log_file = str(project_path / "logs" / f"{project_path.name}_{ts}.log")
            self._set_env_var("MLOPS_RUN_LOG_FILE", chosen_log_file)
        log_path = Path(chosen_log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        handlers = [logging.FileHandler(str(log_path), encoding="utf-8")]
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=handlers,
            force=True
        )

        # Redirect stdout/stderr prints to the logging system so nothing goes to the terminal
        class _StreamToLogger:
            def __init__(self, logger: logging.Logger, level: int):
                self.logger = logger
                self.level = level
                self._buffer = ""

            def write(self, message: str) -> None:
                if not message:
                    return
                self._buffer += message
                while "\n" in self._buffer:
                    line, self._buffer = self._buffer.split("\n", 1)
                    if line.strip():
                        self.logger.log(self.level, line)

            def flush(self) -> None:
                if self._buffer.strip():
                    self.logger.log(self.level, self._buffer.strip())
                    self._buffer = ""

        root_logger = logging.getLogger()
        sys.stdout = _StreamToLogger(root_logger, logging.INFO)
        sys.stderr = _StreamToLogger(root_logger, logging.ERROR)

    def run_pipeline_for_project(self, project_id: str, config_path: str) -> Dict[str, Any]:
        """
        Run the ML pipeline for a specific project.
        
        Args:
            project_id: The project identifier
            config_path: Path to the project's configuration file
            
        Returns:
            Pipeline execution results
        """
        project_manager = ProjectManager()
        
        if not project_manager.project_exists(project_id):
            raise ValueError(f"Project '{project_id}' does not exist")
        
        project_path = project_manager.get_project_path(project_id)
        
        with open(config_path) as f:
            platform_config = yaml.safe_load(f)
        
        self._update_config_for_project(platform_config, project_path, project_id)

        # Export project id so reporting and upload paths use the correct namespace.
        self._set_env_var("MLOPS_PROJECT_ID", str(project_id))
        
        self._configure_logging(platform_config, project_path)
        logger = logging.getLogger(__name__)
        
        tracker = self._initialize_tracker(platform_config)
        repro_manager = ReproducibilityManager(config_path, tracker_instance=tracker, project_path=project_path)
        
        repro_manager.ensure_reproducibility_setup()
        # Ensure both runtime and reporting environments are initialized so their interpreters are available
        try:
            repro_manager.setup_environment()
        except Exception as _env_e:
            logger.warning(f"Environment setup skipped or failed: {_env_e}")

        # Export the project runtime and reporting interpreters so auto-installs go into the venvs
        try:
            if getattr(repro_manager, 'python_interpreter', None):
                self._set_env_var("MLOPS_RUNTIME_PYTHON", str(repro_manager.python_interpreter))
        except Exception:
            pass
        try:
            if getattr(repro_manager, 'reporting_python_interpreter', None):
                self._set_env_var("MLOPS_REPORTING_PYTHON", str(repro_manager.reporting_python_interpreter))
                self._reporting_python = str(repro_manager.reporting_python_interpreter)
        except Exception:
            pass

        # Export reporting config for workers (charts metadata and entrypoints)
        try:
            rep_cfg = (platform_config or {}).get('reporting', {}) or {}
            self._set_env_var("MLOPS_REPORTING_CONFIG", json.dumps(rep_cfg))
        except Exception:
            pass

        model_section = platform_config.get("model", {})
        try:
            repro_manager.apply_cloud_env_from_config(model_section)
            repro_manager.ensure_cloud_dependencies(model_section)
        except Exception as _cloud_e:
            logger.warning(f"Cloud bootstrap skipped or failed: {_cloud_e}")


        run_id = self._generate_run_id(platform_config, project_id)
        run_metadata = self._prepare_run_metadata(platform_config, run_id)
        
        # Keep this exact substring ("with run_id:") stable; cluster controller parses it.
        print(f"Executing project '{project_id}' with run_id: {run_id}")

        run_started = False
        final_status = "FINISHED"
        
        try:
            tracker.start_run(**run_metadata)
            run_started = True
            model_config = AdapterConfig(**platform_config["model"])
            adapter = self.adapter_manager.create_adapter(
                platform_config["model"]["framework"],
                model_config,
                python_interpreter=repro_manager.python_interpreter,
                environment_name=repro_manager.environment_name,
                project_path=project_manager.get_project_path(project_id)
            )
            
            if adapter is None:
                raise ValueError(f"Could not create adapter for framework: {platform_config['model']['framework']}")
            
            adapter.initialize()
            try:
                if hasattr(adapter, "set_tracker"):
                    adapter.set_tracker(tracker)
            except Exception:
                pass

            pipeline_results = self._execute_pipeline(adapter, platform_config, run_id, tracker)
            
            saved_artifact_paths = repro_manager.save_run_artifacts_locally(run_id, adapter)
            pipeline_results["artifact_paths"] = saved_artifact_paths

            config_hash = self._compute_config_hash(platform_config)
            project_manager.add_run_to_project(project_id, run_id, config_hash)
            
            print(f"Project '{project_id}' pipeline execution completed successfully!")
            return pipeline_results
            
        except Exception as e:
            final_status = "FAILED"
            print(f"Pipeline execution failed: {e}")
            raise
        finally:
            if run_started:
                try:
                    if hasattr(tracker, "run_active"):
                        if getattr(tracker, "run_active"):
                            tracker.end_run(status=final_status)
                    else:
                        tracker.end_run(status=final_status)
                except Exception:
                    pass

    def _update_config_for_project(self, config: Dict[str, Any], project_path: Path, project_id: str) -> None:
        """Update configuration paths to be project-specific."""
        repro = config.get("reproducibility")
        if isinstance(repro, dict):
            artifacts_config = repro.get("artifacts")
            if isinstance(artifacts_config, dict):
                model_cfg = artifacts_config.get("model")
                if isinstance(model_cfg, dict):
                    model_cfg["path"] = str(project_path / "artifacts" / "models")
                data_cfg = artifacts_config.get("data")
                if isinstance(data_cfg, dict):
                    data_cfg["path"] = str(project_path / "artifacts" / "data")

            tracking_config = repro.get("experiment_tracking")
            if isinstance(tracking_config, dict):
                params = tracking_config.get("parameters")
                if isinstance(params, dict):
                    tracking_uri = params.get("tracking_uri")
                    if isinstance(tracking_uri, str) and "sqlite" in tracking_uri:
                        params["tracking_uri"] = f"sqlite:///{project_path}/artifacts/experiments.db"

    