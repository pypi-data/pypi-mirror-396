#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import time
import yaml
import logging
from pathlib import Path
from typing import Optional, Dict, Any

def _default_workspace_dir() -> Path:
    raw = os.environ.get("MLOPS_WORKSPACE_DIR") or os.environ.get("MLOPS_REPO_ROOT")
    if raw:
        try:
            return Path(raw).expanduser().resolve()
        except Exception:
            return Path(raw)
    return Path.cwd()


# Source-checkout support: make <workspace>/src importable when present; otherwise assume installed package.
_WORKSPACE_ROOT = _default_workspace_dir()
_SRC_DIR = _WORKSPACE_ROOT / "src"
if _SRC_DIR.exists() and str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

class ClusterController:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir.resolve()
        self.logs_dir = self.project_dir / "logs"
        self.artifacts_dir = self.project_dir / "artifacts"
        self.logger = logging.getLogger("CLUSTER_CONTROLLER")
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def _build_kv_env(self, project_id: str) -> Dict[str, str]:
        """Build environment variables for KV backend from project or cluster config."""
        env: Dict[str, str] = {}
        try:
            import yaml as _yaml
            proj_cfg_path = self.project_dir / "projects" / project_id / "configs" / "project_config.yaml"
            proj_cfg = {}
            if proj_cfg_path.exists():
                with open(proj_cfg_path, 'r') as _f:
                    proj_cfg = _yaml.safe_load(_f) or {}
            # Navigate to model.parameters.cache.backend
            try:
                kv_cfg = ((proj_cfg.get('model') or {}).get('parameters') or {}).get('cache', {}) or {}
                backend = (kv_cfg.get('backend') or {}).get('type')
                if backend == 'redis':
                    env['MLOPS_KV_BACKEND'] = 'redis'
                    bcfg = kv_cfg.get('backend') or {}
                    if bcfg.get('host') is not None:
                        env['MLOPS_REDIS_HOST'] = str(bcfg.get('host'))
                    if bcfg.get('port') is not None:
                        env['MLOPS_REDIS_PORT'] = str(bcfg.get('port'))
                    if bcfg.get('db') is not None:
                        env['MLOPS_REDIS_DB'] = str(bcfg.get('db'))
                    if bcfg.get('password') is not None:
                        env['MLOPS_REDIS_PASSWORD'] = str(bcfg.get('password'))
                elif backend == 'gcp':
                    env['MLOPS_KV_BACKEND'] = 'gcp'
                    bcfg = kv_cfg.get('backend') or {}
                    if bcfg.get('gcp_project') is not None:
                        env['GOOGLE_CLOUD_PROJECT'] = str(bcfg.get('gcp_project'))
                    if bcfg.get('emulator_host') is not None:
                        env['FIRESTORE_EMULATOR_HOST'] = str(bcfg.get('emulator_host'))
                    if bcfg.get('credentials_json') is not None:
                        try:
                            cred_path = Path(str(bcfg.get('credentials_json')))
                            # Resolve relative to project dir first; fallback to workspace root.
                            if not cred_path.is_absolute():
                                project_root = (self.project_dir / "projects" / project_id)
                                cand = (project_root / cred_path)
                                cred_path = (cand if cand.exists() else (self.project_dir / cred_path)).resolve()
                            env['GOOGLE_APPLICATION_CREDENTIALS'] = str(cred_path)
                        except Exception:
                            env['GOOGLE_APPLICATION_CREDENTIALS'] = str(bcfg.get('credentials_json'))
            except Exception:
                pass
            # Fallback to cluster kv_store block if present
            if not env:
                cfg_path = self.project_dir / "projects" / project_id / "configs" / "cluster_config.yaml"
                cluster_cfg_local: Dict[str, Any] = {}
                if cfg_path.exists():
                    with open(cfg_path, 'r') as _f:
                        cluster_cfg_local = _yaml.safe_load(_f) or {}
                cluster_kv = cluster_cfg_local.get('kv_store') if isinstance(cluster_cfg_local, dict) else None
                if isinstance(cluster_kv, dict):
                    backend = cluster_kv.get('backend', 'redis')
                    if backend == 'redis':
                        env['MLOPS_KV_BACKEND'] = 'redis'
                        if cluster_kv.get('host') is not None:
                            env['MLOPS_REDIS_HOST'] = str(cluster_kv.get('host'))
                        if cluster_kv.get('port') is not None:
                            env['MLOPS_REDIS_PORT'] = str(cluster_kv.get('port'))
                        if cluster_kv.get('db') is not None:
                            env['MLOPS_REDIS_DB'] = str(cluster_kv.get('db'))
                        if cluster_kv.get('password') is not None:
                            env['MLOPS_REDIS_PASSWORD'] = str(cluster_kv.get('password'))
                    elif backend == 'gcp':
                        env['MLOPS_KV_BACKEND'] = 'gcp'
                        if cluster_kv.get('gcp_project') is not None:
                            env['GOOGLE_CLOUD_PROJECT'] = str(cluster_kv.get('gcp_project'))
                        if cluster_kv.get('emulator_host') is not None:
                            env['FIRESTORE_EMULATOR_HOST'] = str(cluster_kv.get('emulator_host'))
                        if cluster_kv.get('credentials_json') is not None:
                            try:
                                cred_path = Path(str(cluster_kv.get('credentials_json')))
                                if not cred_path.is_absolute():
                                    cred_path = (self.project_dir / cred_path).resolve()
                                env['GOOGLE_APPLICATION_CREDENTIALS'] = str(cred_path)
                            except Exception:
                                env['GOOGLE_APPLICATION_CREDENTIALS'] = str(cluster_kv.get('credentials_json'))
        except Exception:
            env = {}
        return env

    def _load_executor_config(self, project_id: str) -> Dict[str, Any]:
        """Load executor config block from the project's project_config.yaml."""
        try:
            proj_cfg_path = self.project_dir / "projects" / project_id / "configs" / "project_config.yaml"
            if not proj_cfg_path.exists():
                return {}
            with open(proj_cfg_path, 'r') as f:
                proj_cfg = yaml.safe_load(f) or {}
            executor_cfg = ((proj_cfg.get('model') or {}).get('parameters') or {}).get('executor', {}) or {}
            return executor_cfg if isinstance(executor_cfg, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def _extract_comm_compression(executor_cfg: Dict[str, Any]) -> Optional[str]:
        if not isinstance(executor_cfg, dict):
            return None
        dask_cfg = executor_cfg.get('dask') or executor_cfg.get('dask_config') or {}
        if not isinstance(dask_cfg, dict):
            return None
        comm_cfg = dask_cfg.get('comm') or {}
        if isinstance(comm_cfg, dict):
            comp = comm_cfg.get('compression') or comm_cfg.get('codec')
            if comp:
                return str(comp)
        comp = dask_cfg.get('compression')
        return str(comp) if comp else None

    def run_project_with_dask(self, project_id: str,
                               cluster_provider: Optional[str] = None,
                               num_workers: int = 2,
                               provider_options: Optional[Dict[str, Any]] = None) -> None:
        """Run the project locally while provisioning a Dask cluster via a provider (slurm/ansible)."""
        self.logger.info(f"Project directory: {self.project_dir}")
        self.logger.info(f"Logs directory: {self.logs_dir}")
        self.logger.info(f"Artifacts directory: {self.artifacts_dir}")

        # Prepare KV env from config
        kv_env = self._build_kv_env(project_id)
        executor_cfg = self._load_executor_config(project_id)
        comm_compression = self._extract_comm_compression(executor_cfg)

        # Prepare a per-project interpreter using the environment manager
        cache_base = Path.home() / ".cache" / "mlops-platform" / project_id
        env_file = cache_base / "python_interpreter.txt"
        env_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Ensuring project interpreter at {env_file}")
        setup_cmd = [
            sys.executable,
            str(self.project_dir / "src" / "mlops" / "environment" / "setup_env.py"),
            "--project-id", project_id,
            "--project-dir", str(self.project_dir),
            "--env-file", str(env_file),
        ]
        # Log file for this run (unique per run)
        env_log_hint = os.environ.get("MLOPS_RUN_LOG_FILE")
        if env_log_hint:
            proj_log_file = Path(env_log_hint)
            proj_log_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            proj_logs_dir = self.project_dir / "projects" / project_id / "logs"
            proj_logs_dir.mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            proj_log_file = proj_logs_dir / f"{project_id}_{timestamp}.log"
            os.environ["MLOPS_RUN_LOG_FILE"] = str(proj_log_file)
        # Note: pointers are printed in main() before re-exec; avoid duplicate prints here
        with open(proj_log_file, "a", encoding="utf-8") as lf:
            res = subprocess.run(setup_cmd, stdout=lf, stderr=lf, text=True)
        if res.returncode != 0:
            self.logger.error("Project environment setup failed. See project log for details.")
            raise RuntimeError("Failed to set up project environment")

        # Read the project interpreter path produced by setup
        if not env_file.exists():
            raise RuntimeError(f"Missing environment interpreter file at {env_file}")
        project_python = env_file.read_text().strip()
        if not project_python:
            raise RuntimeError("Empty interpreter path read from env file")
        # Make sure required dependencies are present in the project environment
        try:
            # Upgrade pip and core build tools
            with open(proj_log_file, "a", encoding="utf-8") as lf:
                subprocess.run([project_python, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], check=False, stdout=lf, stderr=lf, text=True)
            # Install our package (and extras if needed) into the project env using an absolute path
            repo_path = str(self.project_dir)
            if cluster_provider == 'slurm':
                with open(proj_log_file, "a", encoding="utf-8") as lf:
                    subprocess.run([project_python, "-m", "pip", "install", "-e", f"{repo_path}[slurm]"], check=False, stdout=lf, stderr=lf, text=True)
            else:
                with open(proj_log_file, "a", encoding="utf-8") as lf:
                    subprocess.run([project_python, "-m", "pip", "install", "-e", repo_path], check=False, stdout=lf, stderr=lf, text=True)
            # Ensure pydantic is available for adapters/config schema regardless of editable install success
            try:
                subprocess.run([project_python, "-c", "import pydantic"], check=True, capture_output=True, text=True)
            except Exception:
                with open(proj_log_file, "a", encoding="utf-8") as lf:
                    lf.write("Installing missing dependency: pydantic>=2\n")
                    res = subprocess.run([project_python, "-m", "pip", "install", "pydantic>=2"], check=False, stdout=lf, stderr=lf, text=True)
                    if res.returncode != 0:
                        lf.write("Retrying pydantic install with --user...\n")
                        subprocess.run([project_python, "-m", "pip", "install", "--user", "pydantic>=2"], check=False, stdout=lf, stderr=lf, text=True)
        except Exception:
            pass

        # Verify core distributed dependencies; attempt to install if missing
        def _ensure_importable(py: str, module: str) -> bool:
            try:
                subprocess.run([py, "-c", f"import {module}"], check=True, capture_output=True, text=True)
                return True
            except Exception:
                return False

        core_missing = []
        for mod in ("dask", "distributed"):
            if not _ensure_importable(project_python, mod):
                core_missing.append(mod)
        if core_missing:
            self.logger.info(f"Installing missing core deps into project env: {', '.join(core_missing)}")
            with open(proj_log_file, "a", encoding="utf-8") as lf:
                subprocess.run([project_python, "-m", "pip", "install", *core_missing], check=False, stdout=lf, stderr=lf, text=True)
        # For slurm provider ensure dask-jobqueue is present
        if cluster_provider == 'slurm' and not _ensure_importable(project_python, "dask_jobqueue"):
            self.logger.info("Installing missing SLURM extra: dask-jobqueue>=0.8.0")
            with open(proj_log_file, "a", encoding="utf-8") as lf:
                subprocess.run([project_python, "-m", "pip", "install", "dask-jobqueue>=0.8.0"], check=False, stdout=lf, stderr=lf, text=True)
        # Final gate: give a clear error early if deps are still missing
        if not _ensure_importable(project_python, "dask") or not _ensure_importable(project_python, "distributed"):
            raise RuntimeError("Dask is not available in the project environment. Ensure connectivity or pin it in your project's requirements.txt.")
        if cluster_provider == 'slurm' and not _ensure_importable(project_python, "dask_jobqueue"):
            raise RuntimeError("dask-jobqueue is not available in the project environment. Ensure connectivity or pin it in your project's requirements.txt.")

        # In-process import sanity (rare HPC oddities): ensure this running interpreter can import dask/distributed
        try:
            import dask as _d  # type: ignore
            import distributed as _dist  # type: ignore
            try:
                _dv = getattr(_d, "__version__", "unknown")
            except Exception:
                _dv = "unknown"
            try:
                _disv = getattr(_dist, "__version__", "unknown")
            except Exception:
                _disv = "unknown"
            self.logger.info(f"Dask import OK in-process: dask={_dv}, distributed={_disv}")
        except Exception as _imp_e:
            self.logger.warning(f"In-process import of dask failed: {_imp_e}. Patching sys.path using project env site-packages...")
            try:
                sp = subprocess.run(
                    [project_python, "-c", "import sysconfig; print(sysconfig.get_paths().get('purelib') or '')"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                site_pkgs = (sp.stdout or "").strip()
                if site_pkgs:
                    if site_pkgs not in sys.path:
                        sys.path.insert(0, site_pkgs)
                    try:
                        import dask as _d2  # type: ignore
                        import distributed as _dist2  # type: ignore
                        _dv2 = getattr(_d2, "__version__", "unknown")
                        _disv2 = getattr(_dist2, "__version__", "unknown")
                        self.logger.info(f"Dask import OK after patch: dask={_dv2}, distributed={_disv2}")
                    except Exception as _imp_e2:
                        raise RuntimeError(f"Dask remains unimportable after site-packages patch: {_imp_e2}")
                else:
                    raise RuntimeError("Unable to resolve site-packages path for project interpreter")
            except Exception as _patch_e:
                raise RuntimeError(f"Failed to ensure in-process dask importability: {_patch_e}")

        # Prepare environment for running the pipeline
        env = os.environ.copy()
        if comm_compression:
            env['DASK_DISTRIBUTED__COMM__COMPRESSION'] = comm_compression
            env['MLOPS_DASK_COMPRESSION'] = comm_compression
        else:
            env.setdefault('DASK_DISTRIBUTED__COMM__COMPRESSION', 'zlib')
        env['PYTHONUNBUFFERED'] = '1'
        env['PYTHONPATH'] = f"{self.project_dir / 'src'}:{env.get('PYTHONPATH', '')}".rstrip(':')
        for k, v in kv_env.items():
            env[k] = v

        provider_options = dict(provider_options or {})
        if comm_compression:
            provider_options.setdefault('comm_compression', comm_compression)

        # If a provider is requested, start it here, run pipeline, then stop it
        provider_obj = None
        if cluster_provider:
            self.logger.info(f"Starting provider: {cluster_provider} with {num_workers} workers")
            try:
                from mlops.cluster.providers import SlurmClusterProvider, AnsibleClusterProvider
                if cluster_provider == 'slurm':
                    provider_obj = SlurmClusterProvider()
                elif cluster_provider == 'ansible':
                    provider_obj = AnsibleClusterProvider()
                else:
                    raise ValueError(f"Unknown provider: {cluster_provider}")
                # Ensure workers use the same Python interpreter as the prepared project environment
                provider_options = provider_options or {}
                cluster_kwargs = dict((provider_options.get('cluster_kwargs') or {}))
                cluster_kwargs.setdefault('python', project_python)
                provider_options['cluster_kwargs'] = cluster_kwargs
                _, addr = provider_obj.start(num_workers=num_workers, options=provider_options or {})
                if not addr:
                    raise RuntimeError("Failed to obtain scheduler address from provider")
                env['DASK_SCHEDULER_ADDRESS'] = str(addr)
                self.logger.info(f"Using Dask scheduler at {addr}")
                try:
                    print(f"Dask scheduler: {addr}")
                except Exception:
                    pass
            except Exception as e:
                if provider_obj:
                    try:
                        provider_obj.stop()
                    except Exception:
                        pass
                raise

        # Run the pipeline using the prepared interpreter
        self.logger.info(f"Running pipeline for project '{project_id}'")
        run_cmd = [project_python, "-m", "mlops.main", "run", project_id]
        # Ensure inner processes honor this unique run log
        env['MLOPS_RUN_LOG_FILE'] = str(proj_log_file)
        # Prevent recursion back into the controller when the CLI decides how to run
        env['MLOPS_FORCE_LOCAL'] = '1'
        with open(proj_log_file, "a", encoding="utf-8") as lf:
            result = subprocess.run(run_cmd, env=env, stdout=lf, stderr=lf, text=True)
        rc = result.returncode
        # Try to extract and surface the run ID from the project log
        try:
            run_id_val = None
            with open(proj_log_file, "r", encoding="utf-8") as rf:
                for line in rf:
                    if "with run_id:" in line:
                        # e.g., Executing project 'my-project' with run_id: project-my-project-XXXX
                        idx = line.find("with run_id:")
                        if idx >= 0:
                            run_id_val = line[idx + len("with run_id:"):].strip().strip("'\"")
                    elif "ID: 'project-" in line:
                        # e.g., [NoOpTracker] Started run ... ID: 'project-...'
                        try:
                            start = line.index("ID: '") + 5
                            end = line.index("'", start)
                            run_id_val = line[start:end]
                        except Exception:
                            pass
            if run_id_val:
                print(f"Run ID: {run_id_val}")
        except Exception:
            pass
        # Always attempt to stop provider
        if provider_obj:
            try:
                provider_obj.stop()
            except Exception as e:
                self.logger.warning(f"Provider stop returned error: {e}")
        if rc != 0:
            raise SystemExit(rc)
        self.logger.info("Project completed successfully via Dask scheduler.")


def _setup_logging(logs_dir: Path, project_id: str) -> None:
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / f"cluster_controller_{project_id}.log"
    root = logging.getLogger()
    # Avoid duplicate handlers for repeated invocations
    exists = False
    for h in root.handlers:
        try:
            if isinstance(h, logging.FileHandler) and getattr(h, 'baseFilename', '') == str(log_file):
                exists = True
                break
        except Exception:
            continue
    if not exists:
        root.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        fh = logging.FileHandler(str(log_file), encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh.setFormatter(fmt)
        root.addHandler(fh)
        # Also echo warnings/errors to the console so critical info is visible in terminal
        try:
            has_stream = any(isinstance(h, logging.StreamHandler) for h in root.handlers)
            if not has_stream:
                ch = logging.StreamHandler(sys.stdout)
                ch.setLevel(logging.WARNING)
                ch.setFormatter(fmt)
                root.addHandler(ch)
        except Exception:
            pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cluster Controller")
    parser.add_argument(
        "--project-dir",
        type=str,
        default=str(_WORKSPACE_ROOT),
        help="Base project directory on the cluster (defaults to repo root).",
    )
    parser.add_argument("--project-id", type=str, help="Project ID (e.g., my-project)")
    parser.add_argument("--cluster-config", type=str, default=None, help="Path to cluster_config.yaml (defaults to project's configs folder)")
    parser.add_argument("--log-file", type=str, default=None, help="Per-run project log file path (overrides auto timestamped path)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()
    controller = ClusterController(project_dir)
    if args.project_id:
        _setup_logging(controller.logs_dir, args.project_id)

    # Proactively print pointers so users can find logs even before re-exec (print once only)
    try:
        if not os.environ.get("MLOPS_LOG_POINTERS_PRINTED"):
            proj_logs_dir = project_dir / "projects" / (args.project_id or "unknown") / "logs"
            # Always use a fresh per-run log path unless explicitly overridden by --log-file
            if args.log_file:
                proj_log_file = Path(args.log_file)
            else:
                import time as _time
                ts = _time.strftime("%Y%m%d_%H%M%S")
                proj_log_file = proj_logs_dir / f"{args.project_id}_{ts}.log" if args.project_id else None
            if proj_log_file:
                proj_log_file.parent.mkdir(parents=True, exist_ok=True)
                os.environ["MLOPS_RUN_LOG_FILE"] = str(proj_log_file)
            ctrl_log_file = controller.logs_dir / f"cluster_controller_{args.project_id}.log" if args.project_id else None
            print(f"Project: {args.project_id}", flush=True)
            if proj_log_file:
                print(f"Project log: {proj_log_file}", flush=True)
            if ctrl_log_file:
                print(f"Controller log: {ctrl_log_file}", flush=True)
            os.environ["MLOPS_LOG_POINTERS_PRINTED"] = "1"
    except Exception as _e:
        logging.getLogger("CLUSTER_CONTROLLER").warning(f"Failed to print log pointers: {_e}")

    if not args.project_id:
        logging.getLogger("CLUSTER_CONTROLLER").error("Requires --project-id")
        return
    cache_base = Path.home() / ".cache" / "mlops-platform" / args.project_id
    env_file = cache_base / "python_interpreter.txt"
    env_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        from mlops.core.pipeline_utils import setup_environment_and_write_interpreter
        project_python = setup_environment_and_write_interpreter(project_dir, args.project_id, env_file)
    except Exception as e:
        logging.getLogger("CLUSTER_CONTROLLER").error(f"Failed to set up environment: {e}")
        raise
    if Path(sys.executable).resolve() != Path(project_python).resolve():
        cmd = [project_python, str(Path(__file__).resolve()), "--project-dir", str(project_dir), "--project-id", args.project_id]
        if getattr(args, "cluster_config", None):
            cmd.extend(["--cluster-config", str(args.cluster_config)])
        os.execv(cmd[0], cmd)
    default_cluster_cfg_path = project_dir / "projects" / args.project_id / "configs" / "cluster_config.yaml"
    cluster_cfg = {}
    cfg_path = Path(args.cluster_config).resolve() if getattr(args, "cluster_config", None) else default_cluster_cfg_path
    if cfg_path.exists():
        try:
            with open(cfg_path, 'r') as f:
                cluster_cfg = yaml.safe_load(f) or {}
            logging.getLogger("CLUSTER_CONTROLLER").info(f"Loaded cluster config from: {cfg_path}")
        except Exception as e:
            logging.getLogger("CLUSTER_CONTROLLER").warning(f"Failed to read cluster config at {cfg_path}: {e}")
            cluster_cfg = {}

    # Extract values strictly from cluster_config.yaml
    cluster_provider = cluster_cfg.get('provider')
    cfg_num_workers = cluster_cfg.get('num_workers')
    try:
        num_workers = int(cfg_num_workers) if cfg_num_workers is not None else 2
    except Exception:
        num_workers = 2
    provider_options: Optional[Dict[str, Any]] = None
    cfg_options = cluster_cfg.get('options') if isinstance(cluster_cfg, dict) else None
    if isinstance(cfg_options, dict):
        provider_options = dict(cfg_options)
    controller.run_project_with_dask(
        project_id=args.project_id,
        cluster_provider=cluster_provider,
        num_workers=num_workers,
        provider_options=provider_options,
    )


if __name__ == "__main__":
    main() 