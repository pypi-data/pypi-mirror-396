from __future__ import annotations

from typing import Any, Dict, List, Optional
from pathlib import Path
import os

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import mimetypes

from mlops.core.workspace import get_projects_root, get_workspace_root

WORKSPACE_ROOT = get_workspace_root()
PROJECTS_DIR = get_projects_root(WORKSPACE_ROOT)


def _app_version() -> str:
    try:
        from importlib.metadata import PackageNotFoundError, version  # type: ignore
        for dist in ("mlops-platform", "mlops_platform"):
            try:
                v = version(dist)
                if v:
                    return str(v)
            except PackageNotFoundError:
                continue
            except Exception:
                continue
    except Exception:
        pass
    return "0.0.0"


app = FastAPI(title="MLOps Platform UI API", version=_app_version())
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _read_projects_index() -> Dict[str, Any]:
    idx_path = PROJECTS_DIR / "projects_index.json"
    if idx_path.exists():
        import json
        try:
            return json.loads(idx_path.read_text()) or {}
        except Exception:
            return {}
    # Fallback: enumerate subdirectories
    out: Dict[str, Any] = {}
    for child in sorted(PROJECTS_DIR.iterdir() if PROJECTS_DIR.exists() else []):
        if not child.is_dir():
            continue
        out[child.name] = {"project_path": f"projects/{child.name}", "description": ""}
    return out


def _parse_graph(project_id: str) -> Dict[str, Any]:
    # Lazy import to avoid runtime import for users not using the UI
    from mlops.core.pipeline_utils import parse_networkx_config_from_project, get_process_graph_summary
    cfg_like = parse_networkx_config_from_project(str(WORKSPACE_ROOT), project_id)
    return get_process_graph_summary(cfg_like)


def _load_kv_cfg_from_project_config(project_id: str) -> Dict[str, Any]:
    """Best-effort load of KV backend config from projects/<id>/configs/project_config.yaml."""
    try:
        import yaml
        cfg_path = PROJECTS_DIR / project_id / "configs" / "project_config.yaml"
        if not cfg_path.exists():
            return {}
        cfg = yaml.safe_load(cfg_path.read_text()) or {}
        kv = ((cfg.get("model", {}) or {}).get("parameters", {}) or {}).get("cache", {}) or {}
        backend = kv.get("backend", {}) or {}
        return backend
    except Exception:
        return {}


def _load_object_store_cfg_from_project_config(project_id: str) -> Dict[str, Any]:
    """Load object_store config from projects/<id>/configs/project_config.yaml."""
    try:
        import yaml
        cfg_path = PROJECTS_DIR / project_id / "configs" / "project_config.yaml"
        if not cfg_path.exists():
            return {}
        cfg = yaml.safe_load(cfg_path.read_text()) or {}
        cache = ((cfg.get("model", {}) or {}).get("parameters", {}) or {}).get("cache", {}) or {}
        store = cache.get("object_store", {}) or {}
        return store
    except Exception:
        return {}


def _kv_for_project(project_id: str):
    # Prefer explicit config from project_config.yaml; fall back to env
    backend_cfg = _load_kv_cfg_from_project_config(project_id)

    # If Redis configured in project config
    if isinstance(backend_cfg, dict) and str(backend_cfg.get("type", "")).lower() == "redis":
        try:
            from mlops.storage.adapters.redis_store import RedisStore  # type: ignore
            host = backend_cfg.get("host") or os.getenv("MLOPS_REDIS_HOST")
            port = backend_cfg.get("port") or os.getenv("MLOPS_REDIS_PORT")
            db = backend_cfg.get("db") or os.getenv("MLOPS_REDIS_DB")
            password = backend_cfg.get("password") or os.getenv("MLOPS_REDIS_PASSWORD")
            return RedisStore(project_id=project_id, host=host, port=port, db=db, password=password)
        except Exception:
            pass

    # If GCP configured in project config
    if isinstance(backend_cfg, dict) and str(backend_cfg.get("type", "")).lower() == "gcp":
        try:
            from mlops.storage.adapters.gcp_kv_store import GCPStore  # type: ignore
            gcp_project = backend_cfg.get("gcp_project") or os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("MLOPS_GCP_PROJECT")
            # If credentials_json provided relative to project, set GOOGLE_APPLICATION_CREDENTIALS
            creds_rel = backend_cfg.get("credentials_json")
            if creds_rel and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                cred_path = PROJECTS_DIR / project_id / creds_rel
                if cred_path.exists():
                    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", str(cred_path.resolve()))
            if gcp_project and not os.getenv("GOOGLE_CLOUD_PROJECT"):
                os.environ.setdefault("GOOGLE_CLOUD_PROJECT", str(gcp_project))
            emulator = backend_cfg.get("emulator_host") or os.getenv("FIRESTORE_EMULATOR_HOST")
            return GCPStore(project_id=project_id, gcp_project=gcp_project, emulator_host=emulator)
        except Exception:
            pass

    # Env-driven Redis
    try:
        from mlops.storage.adapters.redis_store import RedisStore  # type: ignore
        host = os.getenv("MLOPS_REDIS_HOST")
        port = os.getenv("MLOPS_REDIS_PORT")
        db = os.getenv("MLOPS_REDIS_DB")
        password = os.getenv("MLOPS_REDIS_PASSWORD")
        if host or password or db or port:
            try:
                return RedisStore(project_id=project_id, host=host, port=port, db=db, password=password)
            except Exception:
                pass
    except Exception:
        pass
    # Env-driven GCP
    try:
        from mlops.storage.adapters.gcp_kv_store import GCPStore 
        gcp_project = os.getenv("MLOPS_GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
        emulator = os.getenv("FIRESTORE_EMULATOR_HOST")
        if gcp_project or emulator:
            try:
                return GCPStore(project_id=project_id, gcp_project=gcp_project, emulator_host=emulator)
            except Exception:
                pass
    except Exception:
        pass
    # As a last resort, use in-memory singleton per process for dev
    try:
        from mlops.storage.adapters.memory_store import InMemoryStore  # type: ignore
        return InMemoryStore(project_id)
    except Exception:
        return None


def _list_runs_fs(project_id: str) -> List[str]:
    # Fallback: list charts folders which are created per run
    charts_dir = PROJECTS_DIR / project_id / "artifacts" / "charts"
    runs: List[str] = []
    if charts_dir.exists():
        for child in sorted(charts_dir.iterdir()):
            if child.is_dir():
                runs.append(child.name)
    # Also scan logs for the latest timestamped files as run hints (no ID inside logs guaranteed)
    # We will not parse logs; keep simple.
    return runs


@app.get("/api/projects")
def list_projects() -> Dict[str, Any]:
    idx = _read_projects_index()
    return {"projects": sorted(idx.keys())}


def _object_store_for_project(project_id: str):
    cfg = _load_object_store_cfg_from_project_config(project_id)
    if not isinstance(cfg, dict):
        return None
    typ = str(cfg.get("type", "")).lower()
    if typ == "gcs":
        try:
            # Set up credentials if provided in the KV backend config (same credentials used for both)
            backend_cfg = _load_kv_cfg_from_project_config(project_id)
            if isinstance(backend_cfg, dict):
                creds_rel = backend_cfg.get("credentials_json")
                if creds_rel and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                    cred_path = PROJECTS_DIR / project_id / creds_rel
                    if cred_path.exists():
                        os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", str(cred_path.resolve()))
            
            from mlops.storage.adapters.gcs_object_store import GCSObjectStore  # type: ignore
            bucket = cfg.get("bucket")
            prefix = cfg.get("prefix")
            if not bucket:
                return None
            return GCSObjectStore(bucket=bucket, prefix=prefix)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to initialize GCS object store: {e}")
            return None
    return None


@app.get("/api/projects/{project_id}/runs")
def list_runs(project_id: str) -> Dict[str, Any]:
    # Prefer KV backend for past runs if available; fallback to filesystem charts dir
    runs: List[str] = []
    kv = _kv_for_project(project_id)
    try:
        if kv and hasattr(kv, "list_runs"):
            runs = kv.list_runs(limit=100) or []
    except Exception:
        runs = []
    return {"runs": runs}


@app.get("/api/projects/{project_id}/graph")
def get_graph(project_id: str) -> Dict[str, Any]:
    try:
        graph = _parse_graph(project_id)
        return graph
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse graph: {e}")


@app.get("/api/projects/{project_id}/runs/{run_id}/status")
def get_run_status(project_id: str, run_id: str) -> Dict[str, Any]:
    kv = _kv_for_project(project_id)
    status = None
    steps: Dict[str, Any] = {}
    try:
        if kv and hasattr(kv, "get_run_status"):
            status = kv.get_run_status(run_id)
        if kv and hasattr(kv, "list_run_steps"):
            steps = kv.list_run_steps(run_id) or {}
    except Exception:
        pass
    process_status: Dict[str, str] = {}
    process_info: Dict[str, Dict[str, Any]] = {}

    def _parse_ts(val: Any) -> Optional[float]:
        if not val:
            return None
        try:
            if isinstance(val, (int, float)):
                return float(val)
            s = str(val)
            try:
                return datetime.fromisoformat(s).timestamp()
            except Exception:
                return float(s)
        except Exception:
            return None

    for key, rec in steps.items():
        proc = str(rec.get("process_name") or (key.split(".")[0] if isinstance(key, str) and "." in key else ""))
        st = str(rec.get("status") or "").lower()
        if not proc:
            continue
        prev = process_status.get(proc)
        rank = {"completed": 4, "failed": 4, "cached": 4, "running": 3, "": 0}
        if prev == "running" and st in ("", "pending"):
            st_effective = "running"
        else:
            st_effective = st
        if prev is None or rank.get(st_effective, 0) > rank.get(prev, 0):
            process_status[proc] = st_effective

        info = process_info.setdefault(proc, {"status": "pending", "started_at": None, "ended_at": None, "duration_sec": None})
        step_name = str(rec.get("step_name") or (key.split(".", 1)[1] if isinstance(key, str) and "." in key else ""))
        
        # Extract cached_run_id from step record (first encountered for this process)
        cached_run_id = rec.get("cached_run_id")
        if cached_run_id and "cached_run_id" not in info:
            info["cached_run_id"] = cached_run_id
        
        # Extract cached timing information for cached steps
        cached_started_at = rec.get("cached_started_at")
        cached_ended_at = rec.get("cached_ended_at")
        cached_execution_time = rec.get("cached_execution_time")
        
        # For cached steps, store the original timing information
        if st == "cached" and cached_started_at is not None and "cached_started_at" not in info:
            info["cached_started_at"] = _parse_ts(cached_started_at)
        if st == "cached" and cached_ended_at is not None and "cached_ended_at" not in info:
            info["cached_ended_at"] = _parse_ts(cached_ended_at)
        if st == "cached" and cached_execution_time is not None and "cached_execution_time" not in info:
            try:
                info["cached_execution_time"] = float(cached_execution_time)
            except Exception:
                pass
        
        # Only use started_at/ended_at from the process summary record (__process__)
        # to avoid step records overwriting process end time.
        is_process_summary = (step_name == "__process__")
        ts_start = _parse_ts(rec.get("started_at")) if is_process_summary else None
        ts_end = _parse_ts(rec.get("ended_at")) if is_process_summary else None
        # Update timestamps only when coming from the process summary
        if is_process_summary and ts_start is not None:
            cur = info.get("started_at")
            info["started_at"] = min(cur, ts_start) if isinstance(cur, (int, float)) else ts_start
        if is_process_summary and ts_end is not None and st in ("completed", "cached", "failed"):
            cur = info.get("ended_at")
            info["ended_at"] = max(cur, ts_end) if isinstance(cur, (int, float)) else ts_end
        
        # Handle execution time
        exec_time = rec.get("execution_time")
        try:
            exec_time = float(exec_time) if exec_time is not None else None
        except Exception:
            exec_time = None
        
        if step_name == "__process__":
            if st:
                info["status"] = st
            # For terminal states, prefer execution_time when it's positive; avoid
            # writing 0.0 which can mask a valid (ended-started) duration.
            if st in ("completed", "cached", "failed"):
                if isinstance(exec_time, (int, float)) and exec_time > 0:
                    info["duration_sec"] = exec_time
            # Ensure start/end timestamps from the __process__ summary are reflected
            if isinstance(ts_start, (int, float)):
                cur = info.get("started_at")
                info["started_at"] = min(cur, ts_start) if isinstance(cur, (int, float)) else ts_start
            if isinstance(ts_end, (int, float)):
                cur = info.get("ended_at")
                info["ended_at"] = max(cur, ts_end) if isinstance(cur, (int, float)) else ts_end
        else:
            # Do not modify duration based on individual steps; process duration comes
            # from the __process__ record or (ended_at - started_at) fallback.
            
            if st == "failed":
                info["status"] = "failed"
            elif st in ("completed", "cached") and info["status"] not in ("failed", "completed", "cached"):
                if isinstance(info.get("started_at"), (int, float)):
                    info["status"] = "running"
            elif st == "running":
                info["status"] = "running"

    for proc, info in process_info.items():
        # Ensure consistency: use process_status as the source of truth for status
        if proc in process_status:
            info["status"] = process_status[proc]
        
        # Clear ended_at for running processes to avoid showing same start/end time.
        # Keep ended_at for pending (unknown) so UI can display '-' based on None.
        current_status = str(info.get("status") or "").lower()
        if current_status == "running":
            info["ended_at"] = None
        
        # Prefer (ended-started) when execution_time is missing or non-positive
        if isinstance(info.get("started_at"), (int, float)) and isinstance(info.get("ended_at"), (int, float)):
            _diff = max(0.0, float(info["ended_at"]) - float(info["started_at"]))
            cur_dur = info.get("duration_sec")
            try:
                cur_dur_val = float(cur_dur) if cur_dur is not None else None
            except Exception:
                cur_dur_val = None
            if cur_dur_val is None or cur_dur_val <= 0.0:
                info["duration_sec"] = _diff
        
        # Calculate live duration if running and we have a start time, or if duration is
        # non-positive due to an initial 0.0 execution_time write.
        if current_status == "running" and isinstance(info.get("started_at"), (int, float)):
            try:
                now_ts = datetime.now().timestamp()
                live = max(0.0, float(now_ts) - float(info["started_at"]))
                cur_dur = info.get("duration_sec")
                try:
                    cur_dur_val = float(cur_dur) if cur_dur is not None else None
                except Exception:
                    cur_dur_val = None
                if cur_dur_val is None or cur_dur_val <= 0.0 or live > cur_dur_val:
                    info["duration_sec"] = live
            except Exception:
                pass
        if not info.get("status"):
            info["status"] = "pending"

    return {"status": status or "unknown", "steps": steps, "process_status": process_status, "process_info": process_info}


@app.get("/api/projects/{project_id}/chart-config")
def get_chart_config(project_id: str) -> Dict[str, Any]:
    """Get chart configuration from project_config.yaml including probe_paths.
    
    Returns chart definitions needed by frontend to render dynamic charts.
    Response:
    {
      "charts": [
        {
          "name": "chart_name",
          "type": "dynamic"|"static",
          "probe_paths": { "key": "path", ... }
        }, ...
      ],
      "entrypoint": "path/to/charts.js"  # User's chart file
    }
    """
    try:
        import yaml
        cfg_path = PROJECTS_DIR / project_id / "configs" / "project_config.yaml"
        if not cfg_path.exists():
            return {"charts": [], "entrypoint": None}
        
        cfg = yaml.safe_load(cfg_path.read_text()) or {}
        reporting = cfg.get("reporting", {}) or {}
        
        charts_list = reporting.get("charts", []) or []
        # New config keys: prefer explicit dynamic_entrypoint for web UI JS, then derive from static_entrypoint, then legacy entrypoint
        dyn_entry_cfg = str(reporting.get("dynamic_entrypoint", "") or "").strip()
        static_entry_cfg = str(reporting.get("static_entrypoint", "") or "").strip()
        legacy_entry_cfg = str(reporting.get("entrypoint", "") or "").strip()
        
        # Resolve JS entrypoint for frontend dynamic charts
        js_entrypoint = None
        # 1) Explicit dynamic_entrypoint (expected to be a .js path under projects/<id>/charts)
        if dyn_entry_cfg:
            cand = Path(dyn_entry_cfg)
            if cand.exists() or (WORKSPACE_ROOT / cand).exists():
                js_entrypoint = dyn_entry_cfg
        # 2) Derive from static_entrypoint (.py -> .js)
        if not js_entrypoint and static_entry_cfg:
            py_path = Path(static_entry_cfg)
            js_path = py_path.with_suffix('.js')
            if js_path.exists() or (WORKSPACE_ROOT / js_path).exists():
                js_entrypoint = str(js_path)
        # 3) Legacy: derive from entrypoint (.py -> .js)
        if not js_entrypoint and legacy_entry_cfg:
            py_path = Path(legacy_entry_cfg)
            js_path = py_path.with_suffix('.js')
            if js_path.exists() or (WORKSPACE_ROOT / js_path).exists():
                js_entrypoint = str(js_path)
        
        result_charts = []
        for chart_def in charts_list:
            if isinstance(chart_def, dict):
                result_charts.append({
                    "name": chart_def.get("name", ""),
                    "type": chart_def.get("type", "static"),
                    "probe_paths": chart_def.get("probe_paths", {})
                })
        
        return {
            "charts": result_charts,
            "entrypoint": js_entrypoint
        }
    except Exception as e:
        return {"charts": [], "entrypoint": None, "error": str(e)}


@app.get("/api/projects/{project_id}/runs/{run_id}/charts")
def list_charts(project_id: str, run_id: str) -> Dict[str, Any]:
    """List charts for a run from KV store, including static/dynamic and cache paths.

    Response shape:
    {
      "charts": {
        "<chart_name>": {
          "type": "static"|"dynamic",
          "items": [ {"title","object_path","cache_path","mime_type","size_bytes","created_at"} ]
        }, ...
      }
    }
    """
    kv = _kv_for_project(project_id)
    charts: Dict[str, Any] = {}
    try:
        if kv and hasattr(kv, "list_run_charts"):
            charts = kv.list_run_charts(run_id) or {}
    except Exception:
        charts = {}
    if not charts:
        try:
            backend_cfg = _load_kv_cfg_from_project_config(project_id)
            if isinstance(backend_cfg, dict) and str(backend_cfg.get("type", "")).lower() == "gcp":
                try:
                    from google.cloud import firestore  # type: ignore
                    client = firestore.Client()
                    ref = client.collection('mlops_projects').document(project_id) \
                        .collection('runs').document(run_id) \
                        .collection('charts_index').document('index')
                    snap = ref.get()
                    if getattr(snap, 'exists', False):
                        data = snap.to_dict() or {}
                        raw = data.get('charts', {})
                        if isinstance(raw, dict):
                            norm: Dict[str, Any] = {}
                            for name, val in raw.items():
                                if isinstance(val, dict):
                                    ctype = val.get('type')
                                    items = val.get('items') or []
                                    if not ctype and isinstance(items, list) and items and isinstance(items[0], dict):
                                        ctype = items[0].get('chart_type')
                                    norm[name] = { 'type': (str(ctype).lower() if isinstance(ctype, str) else 'static'), 'items': items }
                                elif isinstance(val, list):
                                    norm[name] = { 'type': 'static', 'items': val }
                            charts = norm
                except Exception:
                    pass
        except Exception:
            pass
    return {"charts": charts}


@app.get("/api/projects/{project_id}/runs/{run_id}/metrics/{probe_path:path}")
def get_probe_metrics(project_id: str, run_id: str, probe_path: str) -> Dict[str, Any]:
    """Get current metrics for a specific probe path.
    
    This endpoint enables frontend dynamic charts to poll for metrics updates.
    """
    kv = _kv_for_project(project_id)
    if not kv or not hasattr(kv, "get_probe_metrics_by_path"):
        raise HTTPException(status_code=503, detail="KV store not available")
    
    try:
        metrics = kv.get_probe_metrics_by_path(run_id, probe_path)
        return {"metrics": metrics or {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {e}")


@app.get("/api/projects/{project_id}/runs/{run_id}/charts/fetch")
def fetch_chart(project_id: str, run_id: str, uri: str = "", cache_path: str = "") -> Response:
    """Fetch a single chart image.

    Prefer cache_path (local filesystem) when provided and exists. Otherwise, if
    uri is a gs:// path and object store is configured, fetch from object store.
    If uri is a local path, try to read it directly.
    """
    if cache_path and isinstance(cache_path, str):
        try:
            p = Path(cache_path)
            if p.exists() and p.is_file():
                data = p.read_bytes()
                mime, _ = mimetypes.guess_type(p.name)
                return Response(content=data, media_type=mime or "image/png")
        except Exception:
            pass
    
    # If no uri provided, fail
    if not uri or not isinstance(uri, str):
        raise HTTPException(status_code=400, detail="Invalid chart reference")
    
    # If uri is a gs:// path, use object store
    if uri.startswith("gs://"):
        store = _object_store_for_project(project_id)
        if not store or not hasattr(store, "get_bytes"):
            raise HTTPException(status_code=404, detail="Object store not configured")
        try:
            data = store.get_bytes(uri)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Object not found: {e}")
        mime, _ = mimetypes.guess_type(uri)
        return Response(content=data, media_type=mime or "image/png")
    
    # Otherwise, treat uri as a local file path (fallback when no object store)
    try:
        p = Path(uri)
        if p.exists() and p.is_file():
            data = p.read_bytes()
            mime, _ = mimetypes.guess_type(p.name)
            return Response(content=data, media_type=mime or "image/png")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Local file not found: {e}")
    
    raise HTTPException(status_code=404, detail="Chart not found")

PROJECTS_STATIC_DIR = PROJECTS_DIR
if PROJECTS_STATIC_DIR.exists():
    # Mount /projects BEFORE mounting / so that requests to /projects/... resolve here
    app.mount("/projects", StaticFiles(directory=str(PROJECTS_STATIC_DIR)), name="projects-static")

# Serve static frontend (dev fallback; packaged UI is handled separately)
PKG_UI_DIR = Path(__file__).resolve().parent / "ui"
if PKG_UI_DIR.exists():
    app.mount("/", StaticFiles(directory=str(PKG_UI_DIR), html=True), name="static")
else:
    STATIC_DIR = WORKSPACE_ROOT / "web-ui"
    if STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


def create_app() -> FastAPI:
    return app


if __name__ == "__main__":
    import uvicorn 
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("mlops.web.server:app", host=host, port=port, reload=False)


