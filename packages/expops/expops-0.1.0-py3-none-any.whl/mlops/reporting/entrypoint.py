from __future__ import annotations

import argparse
import inspect
import json
import os
import signal
import sys
import threading
from pathlib import Path
from typing import Any, Callable, Optional

from .context import ChartContext
from .kv_utils import create_kv_store
from .registry import CHART_FUNCS


def _write_text(path: Path, content: str) -> None:
    try:
        path.write_text(content, encoding="utf-8")
    except Exception:
        pass


def _append_text(path: Path, content: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(content)
    except Exception:
        pass


def _is_falsey_env(name: str, default: str = "1") -> bool:
    return str(os.environ.get(name, default)).strip().lower() in {"0", "false", "no"}


def _maybe_seed_chart_subprocess() -> None:
    """Best-effort deterministic seeding for chart subprocesses."""
    if _is_falsey_env("MLOPS_TASK_LEVEL_SEEDING", default="1"):
        return
    try:
        base_seed = int(os.environ.get("MLOPS_RANDOM_SEED") or 42)
    except Exception:
        base_seed = 42

    try:
        import random

        random.seed(base_seed)
    except Exception:
        pass

    # Avoid importing heavyweight optional deps just for seeding. If a chart script
    # imports these libraries, they'll be present in sys.modules and we can seed.
    try:
        np = sys.modules.get("numpy")
        if np is None:
            import numpy as np  # type: ignore
        np.random.seed(base_seed)  # type: ignore[attr-defined]
    except Exception:
        pass

    torch = sys.modules.get("torch")
    if torch is not None:
        try:
            torch.manual_seed(base_seed)  # type: ignore[attr-defined]
        except Exception:
            pass
        try:
            if getattr(torch, "cuda", None) and torch.cuda.is_available():  # type: ignore[attr-defined]
                torch.cuda.manual_seed_all(base_seed)  # type: ignore[attr-defined]
        except Exception:
            pass
        try:
            torch.use_deterministic_algorithms(True)  # type: ignore[attr-defined]
        except Exception:
            pass

    tf = sys.modules.get("tensorflow")
    if tf is not None:
        try:
            tf.random.set_seed(base_seed)  # type: ignore[attr-defined]
        except Exception:
            pass


def _import_chart_modules(output_dir: Path) -> None:
    """Import user chart modules (best-effort) so @chart() registrations run."""
    files_csv = os.environ.get("MLOPS_CHART_IMPORT_FILES", "").strip()
    if files_csv:
        for fpath in [p.strip() for p in files_csv.split(",") if p.strip()]:
            try:
                import hashlib
                import importlib.util

                f_abs = str(Path(fpath).resolve())
                mod_name = f"mlops_chart_{hashlib.sha256(f_abs.encode()).hexdigest()[:12]}"
                spec = importlib.util.spec_from_file_location(mod_name, f_abs)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
            except Exception as exc:
                _append_text(output_dir / "import_error.txt", f"Failed to import chart file {fpath}: {exc}\n")

    mods_csv = os.environ.get("MLOPS_CHART_IMPORT_MODULES", "").strip()
    if mods_csv:
        for mname in [m.strip() for m in mods_csv.split(",") if m.strip()]:
            try:
                import importlib

                importlib.import_module(mname)
            except Exception as exc:
                _append_text(output_dir / "import_error.txt", f"Failed to import chart module {mname}: {exc}\n")


def _normalize_probe_mappings(probe_paths_config: Any) -> dict[str, str]:
    out: dict[str, str] = {}
    if isinstance(probe_paths_config, list):
        for item in probe_paths_config:
            if isinstance(item, dict):
                for key, path in item.items():
                    out[str(key)] = str(path)
        return out
    if isinstance(probe_paths_config, dict):
        for key, path in probe_paths_config.items():
            out[str(key)] = str(path)
    return out


def _resolve_chart_fn(chart_name: str) -> Optional[Callable[..., Any]]:
    if chart_name and chart_name in CHART_FUNCS:
        return CHART_FUNCS[chart_name]

    if not chart_name:
        return None

    # Allow chart scripts to call `mlops.reporting.run_chart_entrypoint()` directly
    # without @chart() by searching parent frames for a global callable.
    frame = inspect.currentframe()
    try:
        cur = frame.f_back if frame else None
        for _ in range(12):
            if cur is None:
                break
            mod_name = cur.f_globals.get("__name__")
            if isinstance(mod_name, str) and mod_name.startswith("mlops.reporting"):
                cur = cur.f_back
                continue
            maybe = cur.f_globals.get(chart_name)
            if callable(maybe):
                return maybe
            cur = cur.f_back
    except Exception:
        return None
    finally:
        # Avoid reference cycles through frames.
        del frame

    return None


def _start_autoshutdown_if_enabled(kv: Any, run_id: str) -> None:
    if _is_falsey_env("MLOPS_CHART_AUTO_SHUTDOWN", default="1"):
        return
    if not kv or not hasattr(kv, "get_run_status"):
        return

    def _poll_shutdown() -> None:
        import time

        while True:
            status = None
            try:
                status = kv.get_run_status(run_id)
            except Exception:
                status = None
            if status and str(status).lower() in {"completed", "failed", "cancelled"}:
                try:
                    os.kill(os.getpid(), signal.SIGINT)
                except Exception:
                    os._exit(0)
                return
            time.sleep(2.0)

    t = threading.Thread(target=_poll_shutdown, name="mlops-chart-autoshutdown", daemon=True)
    t.start()


def run_chart_entrypoint(argv: Optional[list[str]] = None, require_function: bool = True) -> int:
    """Standard entrypoint for user chart scripts.

    - Resolves project/run from env/args
    - For static charts: Fetches metrics from multiple probe paths
    - For dynamic charts: Passes probe_paths directly to the user function
    - Invokes a registered or in-module function named by MLOPS_CHART_NAME
      with signature (metrics, ctx) for static or (probe_paths, ctx) for dynamic
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme", default=os.environ.get("MLOPS_CHART_THEME", "light"))
    parser.add_argument("--project-id", default=os.environ.get("MLOPS_PROJECT_ID", ""))
    parser.add_argument("--run-id", default=os.environ.get("MLOPS_RUN_ID", ""))
    parser.add_argument("--oneshot", action="store_true")
    args = parser.parse_args(argv)

    output_dir = Path(os.environ.get("MLOPS_OUTPUT_DIR", "./out"))
    output_dir.mkdir(parents=True, exist_ok=True)

    chart_name = os.environ.get("MLOPS_CHART_NAME", "").strip()
    chart_type = os.environ.get("MLOPS_CHART_TYPE", "static").strip().lower()
    if chart_type not in {"static", "dynamic"}:
        chart_type = "static"

    # Best-effort: import chart modules so @chart() registration runs.
    _import_chart_modules(output_dir)
    _maybe_seed_chart_subprocess()

    if not args.project_id:
        _write_text(output_dir / "error.txt", "Missing --project-id or MLOPS_PROJECT_ID")
        return 1

    run_id = (args.run_id or os.environ.get("MLOPS_RUN_ID", "") or "").strip()
    if not run_id:
        _write_text(output_dir / "error.txt", "Missing --run-id or MLOPS_RUN_ID")
        return 1

    probe_paths_json = os.environ.get("MLOPS_PROBE_PATHS", "").strip()
    if not probe_paths_json:
        _write_text(
            output_dir / "error.txt",
            "Missing MLOPS_PROBE_PATHS. All charts must define probe_paths in config.",
        )
        return 1

    try:
        probe_paths_config = json.loads(probe_paths_json)
    except Exception as e:
        _write_text(output_dir / "error.txt", f"Invalid MLOPS_PROBE_PATHS JSON: {e}")
        return 1

    probe_mappings = _normalize_probe_mappings(probe_paths_config)

    metrics: dict[str, Any] = {}
    kv_store = None
    try:
        kv_store = create_kv_store(args.project_id)
        if kv_store and hasattr(kv_store, "get_probe_metrics_by_path"):
            for user_key, probe_path in probe_mappings.items():
                if chart_type != "static":
                    metrics[user_key] = {}
                    continue
                try:
                    probe_metrics = kv_store.get_probe_metrics_by_path(run_id, probe_path) or {}
                    metrics[user_key] = probe_metrics
                except Exception:
                    metrics[user_key] = {}
    except Exception:
        kv_store = None

    ctx = ChartContext(
        output_dir=output_dir,
        project_id=args.project_id,
        run_id=run_id,
        kv_path="",  # legacy; not used by the current runner
        probe_id=None,  # legacy; probe IDs are not used by path-based charts
        theme=args.theme,
        chart_name=chart_name,
        metrics=metrics,
        probe_ids={},
        chart_type=chart_type,
    )

    fn = _resolve_chart_fn(chart_name)
    if fn is None:
        if require_function:
            _write_text(
                output_dir / "error.txt",
                f"No chart function found for '{chart_name}'. Define def {chart_name}(metrics, ctx): ... or use @chart().",
            )
            return 1
        return 0

    try:
        sig = inspect.signature(fn)
        params = list(sig.parameters.keys())
        num_params = len(params)

        if chart_type == "dynamic":
            first_name = params[0] if num_params >= 1 else None
            payload = probe_mappings
            _start_autoshutdown_if_enabled(kv_store, run_id)
            if num_params >= 2:
                fn(payload, ctx)
            elif num_params == 1:
                if first_name in ("probe_paths", "paths"):
                    fn(payload)
                else:
                    fn(ctx)
            else:
                _write_text(
                    output_dir / "error.txt",
                    f"Dynamic chart function '{chart_name}' must accept at least one parameter (probe_paths or ctx).",
                )
                return 1
        else:
            if num_params >= 2:
                fn(metrics, ctx)
            elif num_params == 1:
                if params[0] == "metrics":
                    fn(metrics)
                else:
                    fn(ctx)
            else:
                _write_text(
                    output_dir / "error.txt",
                    f"Chart function '{chart_name}' must accept at least one parameter (metrics or ctx).",
                )
                return 1
    except Exception as _fe:
        import traceback

        error_msg = f"Chart function failed: {chart_name} -> {_fe}\n{traceback.format_exc()}"
        _write_text(output_dir / "error.txt", error_msg)
        return 1

    return 0


__all__ = ["run_chart_entrypoint"]

if __name__ == "__main__":
    import sys as _sys
    _sys.exit(run_chart_entrypoint())