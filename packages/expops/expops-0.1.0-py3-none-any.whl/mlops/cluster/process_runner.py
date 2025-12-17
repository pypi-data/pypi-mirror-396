#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
import yaml

def _workspace_root() -> Path:
    raw = os.environ.get("MLOPS_WORKSPACE_DIR") or os.environ.get("MLOPS_REPO_ROOT")
    if raw:
        try:
            return Path(raw).expanduser().resolve()
        except Exception:
            return Path(raw)
    return Path.cwd()


# Source-checkout support: when running on a shared filesystem, ensure <workspace>/src is importable.
WORKSPACE_ROOT = _workspace_root()
SRC_DIR = WORKSPACE_ROOT / "src"
if SRC_DIR.exists() and str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mlops.adapters.custom.custom_adapter import CustomModelAdapter
from mlops.adapters.config_schema import AdapterConfig


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run a single process of a project pipeline")
    p.add_argument("--project-id", required=True, help="Project ID, e.g., my-project")
    p.add_argument("--process", required=True, help="Process name to execute (e.g., data_preparation)")
    p.add_argument("--run-id", required=True, help="Shared run_id across processes")
    p.add_argument("--config", help="Path to project_config.yaml (optional)")
    return p.parse_args()


def load_project_config(project_id: str, config_path_arg: str | None) -> tuple[dict, Path]:
    project_path = WORKSPACE_ROOT / "projects" / project_id
    if config_path_arg:
        config_path = Path(config_path_arg)
    else:
        config_path = project_path / "configs" / "project_config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config, project_path


def main() -> None:
    args = parse_args()
    platform_config, project_path = load_project_config(args.project_id, args.config)

    executor_cfg = platform_config.get("model", {}).get("parameters", {}).get("executor", {}) or {}
    try:
        slurm_cpus = int(os.environ.get("SLURM_CPUS_PER_TASK") or os.environ.get("SLURM_CPUS_ON_NODE") or 0)
    except Exception:
        slurm_cpus = 0
    if slurm_cpus and (not isinstance(executor_cfg, dict) or not executor_cfg.get("n_workers")):
        if not isinstance(executor_cfg, dict):
            executor_cfg = {}
        suggested = max(1, slurm_cpus - 1) if slurm_cpus > 2 else slurm_cpus
        platform_config.setdefault("model", {}).setdefault("parameters", {}).setdefault("executor", {})["n_workers"] = suggested

    adapter_config = AdapterConfig(**platform_config["model"])

    adapter = CustomModelAdapter(
        config=adapter_config,
        python_interpreter=sys.executable,
        project_path=project_path,
    )
    adapter.initialize()

    training_data = platform_config.get("data", {}).get("sources", {}).get("training", {}).get("path")
    training_data_path = None
    if training_data:
        p = Path(training_data)
        if p.is_absolute():
            training_data_path = p
        else:
            cand = (project_path / p)
            training_data_path = cand if cand.exists() else (WORKSPACE_ROOT / p)

    adapter.run(
        data_paths={"training": training_data_path} if training_data_path else {},
        run_id=args.run_id,
        resume_from_process=args.process,
        single_process=True,
    )


if __name__ == "__main__":
    main() 