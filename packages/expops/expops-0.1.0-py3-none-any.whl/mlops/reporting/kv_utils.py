from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional, Tuple

from mlops.core.workspace import get_projects_root, get_workspace_root


def _load_backend_cfg_from_project_config(project_id: str) -> dict[str, Any]:
    root = get_workspace_root()
    cfg_path = get_projects_root(root) / project_id / "configs" / "project_config.yaml"
    if not cfg_path.exists():
        return {}
    try:
        import yaml  # type: ignore
    except Exception:
        return {}
    try:
        cfg = yaml.safe_load(cfg_path.read_text()) or {}
        cache_cfg = (((cfg.get("model") or {}).get("parameters") or {}).get("cache") or {})
        backend_cfg = (cache_cfg.get("backend") or {}) if isinstance(cache_cfg, dict) else {}
        return backend_cfg if isinstance(backend_cfg, dict) else {}
    except Exception:
        return {}


def _as_int(val: Any) -> Optional[int]:
    if val is None or val == "":
        return None
    try:
        return int(val)
    except Exception:
        return None


def create_kv_store(project_id: str) -> Optional[Any]:
    """Create a KV store instance for chart subprocesses.

    Priority:
    - `MLOPS_KV_BACKEND` (if set)
    - project config `projects/<id>/configs/project_config.yaml` (cache.backend)
    - environment-driven heuristics
    """
    backend_cfg = _load_backend_cfg_from_project_config(project_id)
    backend_type = str(os.environ.get("MLOPS_KV_BACKEND") or backend_cfg.get("type") or "").strip().lower()

    if backend_type == "redis":
        try:
            from mlops.storage.adapters.redis_store import RedisStore  # type: ignore
            host = backend_cfg.get("host") or os.environ.get("MLOPS_REDIS_HOST")
            port = _as_int(backend_cfg.get("port") or os.environ.get("MLOPS_REDIS_PORT"))
            db = _as_int(backend_cfg.get("db") or os.environ.get("MLOPS_REDIS_DB"))
            password = backend_cfg.get("password") or os.environ.get("MLOPS_REDIS_PASSWORD")
            return RedisStore(project_id=project_id, host=host, port=port, db=db, password=password)
        except Exception:
            return None

    if backend_type == "gcp":
        try:
            from mlops.storage.adapters.gcp_kv_store import GCPStore  # type: ignore

            gcp_project = (
                backend_cfg.get("gcp_project")
                or os.environ.get("GOOGLE_CLOUD_PROJECT")
                or os.environ.get("MLOPS_GCP_PROJECT")
            )
            emulator_host = backend_cfg.get("emulator_host") or os.environ.get("FIRESTORE_EMULATOR_HOST")

            # If config provides credentials path relative to the project folder, export it.
            creds_rel = backend_cfg.get("credentials_json")
            try:
                if creds_rel and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                    root = get_workspace_root()
                    cred_path = get_projects_root(root) / project_id / str(creds_rel)
                    if cred_path.exists():
                        os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", str(cred_path.resolve()))
            except Exception:
                pass

            return GCPStore(project_id=project_id, gcp_project=gcp_project, emulator_host=emulator_host)
        except Exception:
            return None

    # Env-driven Redis (only if any Redis env is present)
    try:
        if any(os.environ.get(k) for k in ("MLOPS_REDIS_HOST", "MLOPS_REDIS_PORT", "MLOPS_REDIS_DB", "MLOPS_REDIS_PASSWORD")):
            from mlops.storage.adapters.redis_store import RedisStore  # type: ignore
            return RedisStore(project_id=project_id)
    except Exception:
        pass

    # Env-driven GCP/Firestore
    try:
        gcp_project = os.environ.get("MLOPS_GCP_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
        emulator_host = os.environ.get("FIRESTORE_EMULATOR_HOST")
        creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if gcp_project or creds_json or emulator_host:
            from mlops.storage.adapters.gcp_kv_store import GCPStore  # type: ignore
            return GCPStore(project_id=project_id, gcp_project=gcp_project, emulator_host=emulator_host)
    except Exception:
        pass

    return None


def resolve_kv_path_from_env_or_firestore(project_id: str, run_id: str, probe_path: str) -> Tuple[str, Optional[str]]:
    """Deprecated: kept for older chart scripts (probe IDs removed)."""
    try:
        from mlops.storage.path_utils import encode_probe_path  # type: ignore
    except Exception:
        encode_probe_path = lambda s: s  # type: ignore
    if run_id and probe_path:
        enc = encode_probe_path(probe_path)
        return f"metric/{run_id}/probes_by_path/{enc}", None
    if run_id:
        return f"runs/{run_id}", None
    return "", None


__all__ = [
    "create_kv_store",
    "resolve_kv_path_from_env_or_firestore",
]


