from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

ENV_WORKSPACE_DIR = "MLOPS_WORKSPACE_DIR"
# Legacy alias used across older parts of the codebase.
ENV_REPO_ROOT_LEGACY = "MLOPS_REPO_ROOT"


def get_workspace_root() -> Path:
    """Return the workspace root directory.

    The workspace is where `projects/` lives. Resolution order:
    1) `MLOPS_WORKSPACE_DIR`
    2) legacy `MLOPS_REPO_ROOT`
    3) current working directory
    """
    raw = os.environ.get(ENV_WORKSPACE_DIR) or os.environ.get(ENV_REPO_ROOT_LEGACY)
    if raw:
        try:
            return Path(raw).expanduser().resolve()
        except Exception:
            return Path(raw)
    return Path.cwd()


def get_projects_root(workspace_root: Optional[Path] = None) -> Path:
    root = workspace_root or get_workspace_root()
    return root / "projects"


def resolve_relative_path(
    p: str | Path,
    *,
    project_root: Optional[Path] = None,
    workspace_root: Optional[Path] = None,
) -> Path:
    """Resolve a user-provided path against likely bases.

    - Absolute paths are returned as-is.
    - Relative paths are tried against:
      1) current working directory
      2) `project_root` (if provided)
      3) `workspace_root` / `MLOPS_WORKSPACE_DIR` (if provided/available)

    Returns a Path even if it does not exist (best-effort).
    """
    path = Path(p)
    if path.is_absolute():
        return path

    # 1) As given relative to CWD
    try:
        if path.exists():
            return path
    except Exception:
        pass

    # 2) Relative to project root
    if project_root is not None:
        try:
            cand = (project_root / path)
            if cand.exists():
                return cand
        except Exception:
            pass

    # 3) Relative to workspace root
    wr = workspace_root or get_workspace_root()
    try:
        cand = (wr / path)
        if cand.exists():
            return cand
    except Exception:
        pass

    # Fall back to the most likely base for debugging
    if project_root is not None:
        return project_root / path
    return (wr / path)


def infer_source_root() -> Optional[Path]:
    """Best-effort: detect a source checkout root (repo root) when running from source.

    This is used only for backwards-compatible PYTHONPATH/editable-install fallbacks.
    """
    try:
        # workspace.py lives at <root>/src/mlops/core/workspace.py in source checkouts
        mlops_pkg_dir = Path(__file__).resolve().parents[1]  # .../mlops
        src_dir = mlops_pkg_dir.parent  # .../src (source) or .../site-packages (installed)
        root = src_dir.parent
        if (root / "pyproject.toml").exists() or (root / "setup.py").exists():
            # Heuristic: source checkout root should contain packaging metadata.
            return root
    except Exception:
        pass
    return None


