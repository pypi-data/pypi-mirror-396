#!/usr/bin/env python3
"""
MLOps Platform CLI

Main entry point for the MLOps platform with project-based workflows.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

import yaml

from .managers.project_manager import ProjectManager
from .core.pipeline_utils import setup_environment_and_write_interpreter
from .core.workspace import get_workspace_root, infer_source_root


ENV_ENV_READY = "MLOPS_ENV_READY"
ENV_FORCE_LOCAL = "MLOPS_FORCE_LOCAL"
ENV_LOG_POINTERS_PRINTED = "MLOPS_LOG_POINTERS_PRINTED"
ENV_RUN_LOG_FILE = "MLOPS_RUN_LOG_FILE"
ENV_WORKSPACE_DIR = "MLOPS_WORKSPACE_DIR"


def _env_truthy(name: str) -> bool:
    try:
        return str(os.environ.get(name, "")).strip().lower() in {"1", "true", "yes"}
    except Exception:
        return False


def _is_timestamped_log_path(project_id: str, path_obj: Path) -> bool:
    try:
        pattern = rf"^{re.escape(project_id)}_\d{{8}}_\d{{6}}\.log$"
        return bool(re.match(pattern, path_obj.name))
    except Exception:
        return False


def _select_run_log_file(project_path: Path, project_id: str) -> Path:
    logs_dir = project_path / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    run_log_env = os.environ.get(ENV_RUN_LOG_FILE)
    if run_log_env:
        try:
            candidate = Path(run_log_env)
            if _is_timestamped_log_path(project_id, candidate):
                candidate.parent.mkdir(parents=True, exist_ok=True)
                return candidate
        except Exception:
            pass

    ts = time.strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"{project_id}_{ts}.log"
    os.environ[ENV_RUN_LOG_FILE] = str(log_file)
    return log_file


def _print_log_pointers_once(project_id: str, log_path: Path) -> None:
    try:
        if not os.environ.get(ENV_LOG_POINTERS_PRINTED):
            print(f"Project: {project_id}", flush=True)
            print(f"Project log: {log_path}", flush=True)
            os.environ[ENV_LOG_POINTERS_PRINTED] = "1"
    except Exception:
        pass


def _append_to_log_file(log_file: Path, text: str) -> None:
    try:
        with open(log_file, "a", encoding="utf-8") as lf:
            lf.write(text)
    except Exception:
        pass


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


def _configure_file_logging_and_redirect(log_file: Path) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(str(log_file), encoding="utf-8")],
        force=True,
    )
    root_logger = logging.getLogger()
    sys.stdout = _StreamToLogger(root_logger, logging.INFO)
    sys.stderr = _StreamToLogger(root_logger, logging.ERROR)


def _get_cluster_provider(cluster_config_path: Path) -> str | None:
    try:
        if not cluster_config_path.exists():
            return None
        with open(cluster_config_path) as f:
            cluster_cfg = yaml.safe_load(f) or {}
        provider = cluster_cfg.get("provider")
        if isinstance(provider, str) and provider.strip():
            return provider.strip()
    except Exception:
        pass
    return None


def _maybe_delegate_to_cluster_controller(project_id: str, project_path: Path, local_flag: bool, workspace_root: Path) -> None:
    if local_flag or _env_truthy(ENV_FORCE_LOCAL):
        return
    cluster_config_path = project_path / "configs" / "cluster_config.yaml"
    if not _get_cluster_provider(cluster_config_path):
        return

    controller_path = Path(__file__).resolve().parent / "cluster" / "controller.py"
    # Pass workspace root explicitly so the controller does not rely on a source checkout layout.
    cmd = [sys.executable, str(controller_path), "--project-dir", str(workspace_root), "--project-id", project_id]
    result = subprocess.run(cmd)
    raise SystemExit(result.returncode)


def _maybe_prepare_and_reexec_under_project_interpreter(
    workspace_root: Path, project_id: str, log_file: Path, local_flag: bool
) -> None:
    if os.environ.get(ENV_ENV_READY):
        return

    try:
        cache_base = Path.home() / ".cache" / "mlops-platform" / project_id
        env_file = cache_base / "python_interpreter.txt"
        env_file.parent.mkdir(parents=True, exist_ok=True)

        # Ensure all subprocesses/child interpreters can find the projects/ workspace.
        os.environ.setdefault(ENV_WORKSPACE_DIR, str(workspace_root))

        project_python = setup_environment_and_write_interpreter(workspace_root, project_id, env_file)

        # Backwards compatible: if we're running from a source checkout, ensure the
        # project interpreter can import our code even without a self-install.
        source_root = infer_source_root()
        if source_root and (source_root / "src").exists():
            os.environ["PYTHONPATH"] = f"{source_root / 'src'}:{os.environ.get('PYTHONPATH', '')}".rstrip(":")

        _append_to_log_file(
            log_file,
            f"\n=== Preparing project interpreter at {project_python} ({datetime.now()}) ===\n"
            + f"workspace_root={workspace_root}\n",
        )

        def _current_dist_version() -> str | None:
            """Return the installed distribution version of mlops-platform (if available)."""
            try:
                from importlib.metadata import PackageNotFoundError, version  # type: ignore
            except Exception:
                return None
            for dist in ("mlops-platform", "mlops_platform"):
                try:
                    v = version(dist)
                    if v:
                        return str(v)
                except PackageNotFoundError:
                    continue
                except Exception:
                    continue
            return None

        dist_version = _current_dist_version()

        with open(log_file, "a", encoding="utf-8") as lf:
            # Upgrade pip tooling
            subprocess.run(
                [project_python, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"],
                stdout=lf,
                stderr=lf,
                text=True,
                check=False,
            )
            # Ensure the platform package is importable in the project interpreter.
            #
            # - Installed package workflow: install the SAME version into the project env from PyPI.
            # - Dev workflow (source checkout): fall back to editable install.
            installed_ok = False
            if dist_version:
                lf.write(f"Installing mlops-platform=={dist_version} into project env...\n")
                result = subprocess.run(
                    [project_python, "-m", "pip", "install", f"mlops-platform=={dist_version}"],
                    stdout=lf,
                    stderr=lf,
                    text=True,
                    check=False,
                )
                lf.write(f"mlops-platform install exit code: {result.returncode}\n")
                installed_ok = (result.returncode == 0)
            elif source_root and (source_root / "setup.py").exists():
                lf.write("Installing mlops-platform from local source checkout (editable)...\n")
                result = subprocess.run(
                    [project_python, "-m", "pip", "install", "-e", str(source_root)],
                    stdout=lf,
                    stderr=lf,
                    text=True,
                    check=False,
                )
                lf.write(f"platform editable install exit code: {result.returncode}\n")
                installed_ok = (result.returncode == 0)
            else:
                lf.write("WARNING: could not determine current mlops-platform version; skipping self-install.\n")
            # Ensure pydantic is available in the project env even if editable install failed
            need_pyd = subprocess.run([project_python, "-c", "import pydantic"], capture_output=True, text=True)
            if need_pyd.returncode != 0:
                lf.write("Installing pydantic>=2 in project env...\n")
                subprocess.run(
                    [project_python, "-m", "pip", "install", "pydantic>=2"],
                    stdout=lf,
                    stderr=lf,
                    text=True,
                    check=False,
                )

            # If the project interpreter still can't import mlops, do not re-exec.
            # This keeps the CLI functional even when self-install is not available yet.
            import_check = subprocess.run([project_python, "-c", "import mlops"], stdout=lf, stderr=lf, text=True)
            if import_check.returncode != 0:
                lf.write(
                    "WARNING: project interpreter cannot import 'mlops'; "
                    + ("self-install succeeded but import failed.\n" if installed_ok else "self-install was not successful.\n")
                    + "Skipping re-exec under project interpreter.\n"
                )
                return

        cmd = [project_python, "-m", "mlops.main", "run", project_id]
        if local_flag:
            cmd.append("--local")
        os.environ[ENV_ENV_READY] = "1"
        os.execv(cmd[0], cmd)
    except Exception as e:
        _append_to_log_file(log_file, f"Environment setup failed: {e}\n")


def create_project_command(args: argparse.Namespace) -> None:
    project_manager = ProjectManager()
    
    try:
        project_info = project_manager.create_project(
            project_id=args.project_id,
            base_config_path=args.config,
            description=args.description or ""
        )

        print("\nProject Details:")
        print(f"   ID: {project_info['project_id']}")
        print(f"   Path: {project_info['project_path']}")
        print(f"   Created: {project_info['created_at']}")
        
        if args.config:
            print(f"   Config: {project_info.get('active_config', 'No config copied')}")
        
        print("\nNext steps:")
        print(f"   1. Run your project: python -m mlops.main run {args.project_id}")
        print(f"   2. Update config: python -m mlops.main config {args.project_id} --set key=value")
        print(f"   3. List projects: python -m mlops.main list")
        
    except ValueError as e:
        raise SystemExit(f"Error: {e}")


def delete_project_command(args: argparse.Namespace) -> None:
    project_manager = ProjectManager()
    
    success = project_manager.delete_project(args.project_id, confirm=args.force)
    if not success:
        raise SystemExit(1)


def list_projects_command(args: argparse.Namespace) -> None:
    project_manager = ProjectManager()
    projects = project_manager.list_projects()
    
    if not projects:
        print("No projects found. Create your first project with:")
        print("   python -m mlops.main create my-project")
        return
    
    print(f"Found {len(projects)} project(s):\n")
    
    for project in projects:
        print(f"- {project['project_id']}")
        print(f"   Description: {project.get('description', 'No description')}")
        print(f"   Created: {project.get('created_at', 'Unknown')}")
        print(f"   Path: {project.get('project_path', 'Unknown')}")
        
        runs = project.get('runs', [])
        if runs:
            print(f"   Runs: {len(runs)} completed")
        print()


def run_project_command(args: argparse.Namespace) -> None:
    project_manager = ProjectManager()
    
    if not project_manager.project_exists(args.project_id):
        raise SystemExit(
            f"Error: Project '{args.project_id}' does not exist\n"
            f"Create it first with: python -m mlops.main create {args.project_id}"
        )
    
    project_path = project_manager.get_project_path(args.project_id)
    workspace_root = get_workspace_root()
    _maybe_delegate_to_cluster_controller(args.project_id, project_path, bool(args.local), workspace_root)

    config_path = project_manager.get_project_config_path(args.project_id)
    
    if not config_path.exists():
        raise SystemExit(
            f"Error: No configuration found for project '{args.project_id}'\n"
            f"Expected config at: {config_path}\n"
            f"You can set a config with: python -m mlops.main config {args.project_id} --file path/to/config.yaml"
        )
    
    log_file = _select_run_log_file(project_path, args.project_id)
    _print_log_pointers_once(args.project_id, log_file)

    _maybe_prepare_and_reexec_under_project_interpreter(workspace_root, args.project_id, log_file, bool(args.local))
    _configure_file_logging_and_redirect(log_file)

    print(f"Running project '{args.project_id}'...")
    print(f"Project path: {project_path}")
    print(f"Config: {config_path}")

    try:
        # Initialize MLPlatform and run pipeline (lazy import after ensuring deps)
        from .platform import MLPlatform
        platform = MLPlatform()
        results = platform.run_pipeline_for_project(args.project_id, str(config_path))
        
        print("\nPipeline completed successfully.")
        if isinstance(results, dict):
            print(f"Run ID: {results.get('run_id', 'N/A')}")
        else:
            print(f"Results: {results}")
        
    except Exception as e:
        raise SystemExit(f"Error running pipeline: {e}")


def _parse_config_value(raw: str) -> object:
    """Parse a simple scalar value from CLI input (best-effort)."""
    s = str(raw)
    low = s.lower()
    if low in {"true", "false"}:
        return low == "true"
    if s.isdigit():
        return int(s)
    try:
        if "." in s and s.replace(".", "", 1).isdigit():
            return float(s)
    except Exception:
        pass
    return s


def config_project_command(args: argparse.Namespace) -> None:
    project_manager = ProjectManager()
    
    if not project_manager.project_exists(args.project_id):
        raise SystemExit(f"Error: Project '{args.project_id}' does not exist")
    
    # Handle setting config file
    if args.file:
        config_file_path = Path(args.file)
        if not config_file_path.exists():
            raise SystemExit(f"Error: Config file '{args.file}' does not exist")
        
        project_path = project_manager.get_project_path(args.project_id)
        dest_config = project_path / "configs" / "project_config.yaml"
        
        shutil.copy2(config_file_path, dest_config)
        
        # Update project info
        project_info = project_manager.get_project_info(args.project_id)
        project_info["active_config"] = str(dest_config)
        
        project_info_file = project_path / "project_info.json"
        with open(project_info_file, 'w') as f:
            json.dump(project_info, f, indent=2)
        
        print(f"Configuration updated for project '{args.project_id}'")
        print(f"Config file: {dest_config}")
        return
    
    if args.set:
        config_updates = {}
        for setting in args.set:
            try:
                key, value = setting.split('=', 1)
                value_obj = _parse_config_value(value)
                
                # Handle nested keys (e.g., model.parameters.n_estimators=100)
                keys = key.split('.')
                current = config_updates
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = value_obj
                
            except ValueError:
                raise SystemExit(f"Error: Invalid setting format '{setting}'. Use key=value")
        
        project_manager.update_project_config(args.project_id, config_updates)
        print(f"Configuration updated for project '{args.project_id}'")
        return
    
    # Show current config
    config_path = project_manager.get_project_config_path(args.project_id)
    if config_path.exists():
        print(f"Current configuration for project '{args.project_id}':")
        print(f"File: {config_path}")
        print("\n" + "="*50)
        with open(config_path, 'r') as f:
            print(f.read())
    else:
        print(f"No configuration file found for project '{args.project_id}'")
        print(f"Create one with: python -m mlops.main config {args.project_id} --file path/to/config.yaml")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MLOps Platform with Project-based Workflows",
        prog="python -m mlops.main"
    )
    parser.add_argument(
        "--workspace",
        "-w",
        help="Workspace root directory (contains projects/). Defaults to MLOPS_WORKSPACE_DIR or current directory.",
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create project command
    create_parser = subparsers.add_parser('create', help='Create a new project')
    create_parser.add_argument('project_id', help='Project identifier (e.g., my-project)')
    create_parser.add_argument('--config', '-c', help='Base configuration file to copy')
    create_parser.add_argument('--description', '-d', help='Project description')
    create_parser.set_defaults(func=create_project_command)
    
    # Delete project command
    delete_parser = subparsers.add_parser('delete', help='Delete a project')
    delete_parser.add_argument('project_id', help='Project to delete')
    delete_parser.add_argument('--force', '-f', action='store_true', help='Skip confirmation prompt')
    delete_parser.set_defaults(func=delete_project_command)
    
    # List projects command
    list_parser = subparsers.add_parser('list', help='List all projects')
    list_parser.set_defaults(func=list_projects_command)
    
    # Run project command
    run_parser = subparsers.add_parser('run', help='Run a project pipeline')
    run_parser.add_argument('project_id', help='Project to run')
    run_parser.add_argument('--local', '-l', action='store_true', help='Force local run even if a cluster_config.yaml exists')
    run_parser.set_defaults(func=run_project_command)
    
    # Config project command
    config_parser = subparsers.add_parser('config', help='Manage project configuration')
    config_parser.add_argument('project_id', help='Project to configure')
    config_parser.add_argument('--file', '-f', help='Set configuration from file')
    config_parser.add_argument('--set', '-s', action='append', help='Set configuration value (key=value)')
    config_parser.set_defaults(func=config_project_command)
    
    # Parse and execute
    args = parser.parse_args()

    # Apply workspace override early so all downstream components resolve paths consistently.
    try:
        if getattr(args, "workspace", None):
            os.environ[ENV_WORKSPACE_DIR] = str(Path(args.workspace).expanduser().resolve())
    except Exception:
        pass
    # Ensure relative paths in configs (e.g., "projects/<id>/...") resolve against the workspace.
    try:
        os.chdir(get_workspace_root())
    except Exception:
        pass
    
    if not args.command:
        parser.print_help()
        raise SystemExit(1)
    
    args.func(args)


if __name__ == '__main__':
    main() 