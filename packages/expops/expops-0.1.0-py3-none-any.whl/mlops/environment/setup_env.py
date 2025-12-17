#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Setup project environment and write interpreter path")
    p.add_argument("--project-id", required=True)
    p.add_argument("--project-dir", required=True, help="Path to repository root")
    p.add_argument("--env-file", required=True, help="Path to write the interpreter path")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(args.project_dir).resolve()
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from mlops.core.pipeline_utils import setup_environment_and_write_interpreter

    py = setup_environment_and_write_interpreter(repo_root, args.project_id, args.env_file)
    print(f"[env] Environment setup completed. Interpreter: {py}")


if __name__ == "__main__":
    main()