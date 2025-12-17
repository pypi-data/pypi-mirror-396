from __future__ import annotations

from typing import Any, Dict, List, Optional

from datetime import datetime
import json
import logging
import os
from pathlib import Path
import time

from .graph_types import ExecutionResult
from .payload_spill import spill_large_payloads
from .workspace import get_projects_root, get_workspace_root, infer_source_root, resolve_relative_path

logger = logging.getLogger(__name__)


def _apply_hash_overrides(proc_payload: Dict[str, Any], config_hash: Optional[str], function_hash: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """Apply optional hash overrides supplied by the driver (used for chart nodes)."""
    overrides = proc_payload.get("hash_overrides") if isinstance(proc_payload, dict) else None
    if isinstance(overrides, dict):
        config_hash = overrides.get("config_hash") or config_hash
        function_hash = overrides.get("function_hash") or function_hash
    return config_hash, function_hash


def _strip_internal_keys(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: v for k, v in value.items() if not str(k).startswith("__")}
    return value


def _record_chart_artifacts(
    state_manager: Any,
    project_id: str,
    run_id: str,
    chart_name: str,
    out_dir: Path,
    chart_type: str = "static",
) -> None:
    """Best-effort: upload PNG artifacts and record them in the KV store for UI listing."""
    try:
        obj_store = getattr(state_manager, "object_store", None)
        kv = getattr(state_manager, "kv_store", None)
    except Exception:
        return

    try:
        pngs = list(out_dir.rglob("*.png"))
    except Exception:
        pngs = []

    abs_charts_root = None
    try:
        if obj_store and hasattr(obj_store, "_bucket") and getattr(obj_store, "_bucket") is not None:
            bname = getattr(getattr(obj_store, "_bucket"), "name", None)
            if bname:
                abs_charts_root = f"gs://{bname}/projects/{project_id}/charts/{run_id}"
    except Exception:
        abs_charts_root = None

    artifacts: list[dict] = []
    for p in pngs:
        try:
            local_path = str(p.resolve())
        except Exception:
            local_path = str(p)

        obj_path = None
        if obj_store:
            try:
                base = f"projects/{project_id}/charts/{run_id}/{chart_name}"
                if abs_charts_root:
                    base = f"{abs_charts_root}/{chart_name}"
                remote = obj_store.build_uri(base, p.name)
                with open(p, "rb") as f:
                    obj_store.put_bytes(remote, f.read(), content_type="image/png")
                obj_path = remote
            except Exception as upload_err:
                logger.warning(f"[Charts] Upload failed for {p.name}: {upload_err}")
                obj_path = None

        if not obj_path:
            obj_path = local_path

        try:
            artifacts.append(
                {
                    "title": p.name,
                    "object_path": obj_path,
                    "cache_path": local_path,
                    "mime_type": "image/png",
                    "size_bytes": p.stat().st_size,
                    "created_at": time.time(),
                    "chart_type": chart_type,
                }
            )
        except Exception:
            continue

    try:
        if kv and hasattr(kv, "record_run_chart_artifacts"):
            kv.record_run_chart_artifacts(str(run_id), str(chart_name), artifacts)
    except Exception as kv_err:
        logger.warning(f"[Charts] Failed to record artifacts in KV: {kv_err}")


def _build_step_context_from_payload(context_payload: Dict[str, Any]) -> Any:
    from .step_system import StepContext as _Ctx
    try:
        payload = context_payload if isinstance(context_payload, dict) else {}

        checkpoint_dir_value = payload.get("checkpoint_dir")

        step_results_in = payload.get("step_results") or {}
        step_results: Dict[str, Any] = {}
        if isinstance(step_results_in, dict):
            for key, val in step_results_in.items():
                if isinstance(val, dict):
                    data = val.get("data")
                    if isinstance(data, dict):
                        step_results[key] = dict(data)
                    else:
                        step_results[key] = _strip_internal_keys(val)
                else:
                    step_results[key] = val

        data_paths: Dict[str, Path] = {}
        data_paths_in = payload.get("data_paths") or {}
        if isinstance(data_paths_in, dict):
            for k, v in data_paths_in.items():
                try:
                    data_paths[str(k)] = Path(v)
                except Exception:
                    continue

        checkpoint_dir = Path(checkpoint_dir_value) if checkpoint_dir_value else None

        return _Ctx(
            project_id=payload.get("project_id"),
            run_id=payload.get("run_id"),
            tracker=None,
            step_results=step_results,
            global_config=payload.get("global_config") or {},
            data_paths=data_paths,
            checkpoint_dir=checkpoint_dir,
        )
    except Exception:
        # Fall back to a minimal context if anything in the payload is malformed.
        try:
            pid = context_payload.get("project_id") if isinstance(context_payload, dict) else "default"
        except Exception:
            pid = "default"
        return _Ctx(project_id=pid)

def _derive_task_seed(base_seed: int, parts: List[str]) -> int:
    import hashlib as _hashlib
    payload = f"{base_seed}|" + "|".join(parts)
    digest = _hashlib.sha256(payload.encode()).digest()
    val = int.from_bytes(digest[:4], "big") & 0x7FFFFFFF
    return val or (base_seed & 0x7FFFFFFF) or 1


def _seed_all(seed: int) -> None:
    import random as _random
    try:
        _random.seed(seed)
    except Exception:
        pass
    try:
        import numpy as _np  # type: ignore
        _np.random.seed(seed)
    except Exception:
        pass
    # Best-effort deep learning libs
    try:
        import torch as _torch  # type: ignore
        try:
            _torch.manual_seed(seed)
        except Exception:
            pass
        try:
            if _torch.cuda.is_available():
                _torch.cuda.manual_seed_all(seed)
        except Exception:
            pass
        try:
            _torch.use_deterministic_algorithms(True)  # type: ignore[attr-defined]
        except Exception:
            pass
    except Exception:
        pass
    try:
        import tensorflow as _tf  # type: ignore
        try:
            _tf.random.set_seed(seed)
        except Exception:
            pass
    except Exception:
        pass


def _seed_rng_for_task(run_id: Optional[str], process_name: Optional[str], step_name: Optional[str], iteration: Optional[int]) -> None:
    # Gate with task-level seeding toggle; default enabled.
    try:
        enabled = str(os.environ.get("MLOPS_TASK_LEVEL_SEEDING", "1")).lower() not in ("0", "false", "no")
    except Exception:
        enabled = True
    if not enabled:
        return

    try:
        base = int(os.environ.get("MLOPS_RANDOM_SEED", "42") or 42)
    except Exception:
        base = 42

    parts: List[str] = []
    if process_name:
        parts.append(str(process_name))
    if step_name:
        parts.append(str(step_name))
    if iteration is not None:
        try:
            parts.append(str(int(iteration)))
        except Exception:
            parts.append(str(iteration))

    seed_val = _derive_task_seed(base, parts)
    _seed_all(seed_val)
    logger.debug(f"[Seed] base={base} parts={parts} -> seed={seed_val}")


def _maybe_import_custom_model_from_global_config(global_params: Dict[str, Any]) -> None:
    if not isinstance(global_params, dict):
        return

    script_path = global_params.get("custom_script_path")
    if not script_path:
        try:
            script_path = (global_params.get("model", {}) or {}).get("parameters", {}).get("custom_script_path")
        except Exception:
            script_path = None
    if not script_path:
        return

    import importlib
    import importlib.util
    import sys as _sys

    script_path_str = str(script_path)
    try:
        spec = importlib.util.spec_from_file_location("custom_model", script_path_str)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            _sys.modules["custom_model"] = mod
            spec.loader.exec_module(mod)  # type: ignore[attr-defined]
            return
    except Exception:
        pass

    # Fall back to importing by module name.
    try:
        stem = Path(script_path_str).stem
        importlib.import_module(stem)
        return
    except Exception:
        pass

    # Fall back to a previously-loaded module.
    try:
        importlib.import_module("custom_model")
    except Exception:
        return


def _prepare_runner_kwargs(sig: Any, ctx: Any, process_name: Optional[str], dependencies: List[str]) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}
    params = getattr(sig, "parameters", {}) or {}

    if "data" in params:
        data_payload: Dict[str, Any] = {}
        for dep_name in dependencies or []:
            dep_result = ctx.get_step_result(dep_name) if (ctx and hasattr(ctx, "get_step_result")) else None
            data_payload[dep_name] = dep_result if dep_result else {}
        kwargs["data"] = data_payload

    if "hyperparameters" in params:
        try:
            kwargs["hyperparameters"] = ctx.get_hyperparameters(process_name) if ctx else {}
        except Exception:
            kwargs["hyperparameters"] = {}
    return kwargs


def _compute_process_lookup_hashes_worker(
    state_manager: Any,
    ctx: Any,
    process_name: str,
    dependencies: List[str],
    dependency_map: Optional[Dict[str, List[str]]] = None,
    lookup_name: Optional[str] = None,
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Compute (ih, ch, fh) on the worker using the same helper as the driver."""
    try:
        from .process_hashing import compute_process_hashes
    except Exception:
        compute_process_hashes = None  # type: ignore[assignment]

    dep_map: Dict[str, List[str]] = {}
    try:
        for k, v in (dependency_map or {}).items():
            dep_map[str(k)] = sorted(set(v or []))
    except Exception:
        dep_map = {}
    dep_map.setdefault(process_name, sorted(set(dependencies or [])))

    if compute_process_hashes:
        ih, ch, fh = compute_process_hashes(state_manager, ctx, process_name, dep_map, lookup_name=lookup_name)
    else:
        ih = ch = fh = None

    logger.debug(f"[HashTrace] side=worker process={process_name} ih={ih} ch={ch} fh={fh}")
    return (ih, ch, fh)


def _execute_process_on_worker(ctx: Any, proc_payload: Dict[str, Any], run_id: Optional[str]) -> ExecutionResult:
    process_name = proc_payload.get('name')
    start_time = time.time()
    # Deterministic task-level seeding (process scope)
    _seed_rng_for_task(run_id, process_name, None, 0)

    from .step_system import get_process_registry as _get_pr, set_current_context as _set_ctx, set_current_process_context as _set_proc
    import io as _io
    import contextlib as _ctxlib
    import logging as _logging
    _log_stream = _io.StringIO()
    _stdout_stream = _io.StringIO()
    _stderr_stream = _io.StringIO()
    _root_logger = _logging.getLogger()
    _prev_root_level = getattr(_root_logger, "level", _logging.INFO)
    _handler = _logging.StreamHandler(_log_stream)
    try:
        _handler.setLevel(_logging.DEBUG)
        _root_logger.addHandler(_handler)
        _root_logger.setLevel(_logging.DEBUG)
    except Exception:
        pass

    def _cleanup_capture() -> None:
        try:
            _root_logger.removeHandler(_handler)
        except Exception:
            pass
        try:
            _root_logger.setLevel(_prev_root_level)
        except Exception:
            pass

    state_manager = None
    cache_config = proc_payload.get('cache_config', {}) if isinstance(proc_payload, dict) else {}
    if cache_config:
        try:
            logger.info(
                f"[Worker] Attempting state manager creation from proc_payload cache_config: "
                f"kv_type={cache_config.get('kv_store_type')}, "
                f"obj_type={cache_config.get('object_store_type')}, "
                f"bucket={cache_config.get('object_store_config', {}).get('bucket')}"
            )
            state_manager = _create_worker_state_manager(cache_config)
            if state_manager:
                logger.info(
                    f"[Worker] State manager created from cache_config -> "
                    f"has_object_store={hasattr(state_manager, 'object_store') and state_manager.object_store is not None}"
                )
        except Exception as e:
            logger.warning(f"[Worker] Failed to create state manager from cache_config: {e}")
            state_manager = None
    if not state_manager:
        try:
            from .step_system import get_current_state_manager
            state_manager = get_current_state_manager()
        except Exception:
            state_manager = None
    if not state_manager:
        try:
            from .step_system import _get_step_system
            ss = _get_step_system()
            if ss and hasattr(ss, 'state_manager'):
                state_manager = ss.state_manager
        except Exception:
            state_manager = None
    # Final fallback: initialize worker state manager from context if still missing
    if not state_manager:
        try:
            _gc_ctx = getattr(ctx, 'global_config', {}) if ctx else {}
            _pid_ctx = getattr(ctx, 'project_id', None)
            _maybe_init_worker_state_manager(_gc_ctx, _pid_ctx)
            from .step_system import get_state_manager as _get_sm_fallback
            state_manager = _get_sm_fallback()
            logger.debug("[Worker] State manager lazily initialized in _execute_process_on_worker")
        except Exception:
            state_manager = None

    # Resolve process definition early to compute canonical hashes using code_function mapping
    pr = _get_pr()
    lookup_name = proc_payload.get('code_function') or process_name
    pdef = pr.get_process(lookup_name) if pr else None
    runner = getattr(pdef, 'runner', None) if pdef else None
    if not callable(runner):
        _maybe_import_custom_model_from_global_config(getattr(ctx, 'global_config', {}) or {})
        pr = _get_pr()
        pdef = pr.get_process(lookup_name) if pr else None
        runner = getattr(pdef, 'runner', None) if pdef else None
    # Record process started exactly at timing start using unified hashing
    try:
        if state_manager and run_id and process_name:
            deps = proc_payload.get('dependencies', []) or []
            dep_map = proc_payload.get('dependency_map') or {}
            ih, ch, fh = _compute_process_lookup_hashes_worker(state_manager, ctx, process_name, deps, dep_map, lookup_name=lookup_name)
            ch, fh = _apply_hash_overrides(proc_payload, ch, fh)
            state_manager.record_process_started(
                run_id,
                process_name,
                input_hash=ih,
                config_hash=ch,
                function_hash=fh,
                started_at=start_time,
            )
    except Exception:
        pass

    # Special handling for chart processes
    if str(proc_payload.get('process_type', 'process')) == 'chart':
        try:
            result = _run_chart_process_on_worker(ctx, proc_payload, run_id)
            exec_time = time.time() - start_time
            if isinstance(result, dict):
                # Record completion for chart processes so UI/KV reflect status immediately
                try:
                    from .step_state_manager import ProcessExecutionResult as _ProcessExec
                    if state_manager:
                        ih, ch, fh = _compute_process_lookup_hashes_worker(
                            state_manager,
                            ctx,
                            process_name,
                            proc_payload.get('dependencies', []) or [],
                            proc_payload.get('dependency_map') or {},
                            lookup_name=lookup_name,
                        )
                        ch, fh = _apply_hash_overrides(proc_payload, ch, fh)
                        enable_logging = proc_payload.get('logging', True) if isinstance(proc_payload, dict) else True
                        state_manager.record_process_completion(
                            run_id or 'default',
                            _ProcessExec(
                                process_name=process_name,
                                success=True,
                                result=result,
                                execution_time=exec_time,
                                timestamp=datetime.now().isoformat(),
                            ),
                            input_hash=ih,
                            config_hash=ch,
                            function_hash=fh,
                            was_cached=False,
                            enable_logging=enable_logging,
                        )
                except Exception:
                    pass
                _cleanup_capture()
                return ExecutionResult(name=process_name, result=result, execution_time=exec_time, was_cached=False, error=None)
            else:
                _cleanup_capture()
                return ExecutionResult(name=process_name, result={'__logs__': 'Invalid chart result'}, execution_time=exec_time, was_cached=False, error=None)
        except Exception as e:
            exec_time = time.time() - start_time
            _cleanup_capture()
            return ExecutionResult(name=process_name, result={'__error_context__': str(e)}, execution_time=exec_time, was_cached=False, error=str(e))

    # runner already resolved above
    if not callable(runner):
        exec_time = time.time() - start_time
        _cleanup_capture()
        return ExecutionResult(name=process_name, result=None, execution_time=exec_time, was_cached=False, error=f"No runner defined for process '{process_name}'.")

    _set_ctx(ctx)
    try:
        try:
            _set_proc(process_name)
        except Exception:
            pass
        import inspect
        try:
            original_func = getattr(pdef, 'original_func', None) if pdef else None
            sig = inspect.signature(original_func) if original_func else inspect.signature(runner)
        except Exception:
            sig = inspect.signature(runner)
        dependencies = proc_payload.get('dependencies', [])
        kwargs = _prepare_runner_kwargs(sig, ctx, process_name, dependencies)
        with _ctxlib.redirect_stdout(_stdout_stream), _ctxlib.redirect_stderr(_stderr_stream):
            ret = runner(**kwargs) if kwargs else runner()
    except Exception as runner_error:
        exec_time = time.time() - start_time
        error_result = {
            '__logs__': (_log_stream.getvalue() or '') + (_stdout_stream.getvalue() or '') + (_stderr_stream.getvalue() or '')
        }
        return ExecutionResult(name=process_name, result=error_result, execution_time=exec_time, was_cached=False, error=str(runner_error))
    finally:
        try:
            _set_proc(None)
        except Exception:
            pass
        _set_ctx(None)
        _cleanup_capture()

    if not isinstance(ret, dict):
        exec_time = time.time() - start_time
        try:
            _captured = {
                '__logs__': (_log_stream.getvalue() or '') + (_stdout_stream.getvalue() or '') + (_stderr_stream.getvalue() or '')
            }
        except Exception:
            _captured = None
        return ExecutionResult(name=process_name, result=_captured, execution_time=exec_time, was_cached=False, error=f"Process '{process_name}' must return a dictionary, got {type(ret).__name__}.")

    if state_manager and isinstance(ret, dict):
        try:
            ret = spill_large_payloads(ret, state_manager, run_id, process_name)
        except Exception as spill_err:
            logger.error("[PayloadSpill] Failed to spill payload for process %s: %s", process_name, spill_err)
            raise

    exec_time = time.time() - start_time
    ret["__logs__"] = (_log_stream.getvalue() or "") + (_stdout_stream.getvalue() or "") + (_stderr_stream.getvalue() or "")

    try:
        from .step_state_manager import ProcessExecutionResult as _ProcessExec
        if state_manager and ret:
            ih, ch, fh = _compute_process_lookup_hashes_worker(state_manager, ctx, process_name, proc_payload.get('dependencies', []) or [], proc_payload.get('dependency_map') or {}, lookup_name=lookup_name)
            enable_logging = proc_payload.get('logging', True) if isinstance(proc_payload, dict) else True
            state_manager.record_process_completion(
                run_id or 'default',
                _ProcessExec(
                    process_name=process_name,
                    success=True,
                    result=ret,
                    execution_time=exec_time,
                    timestamp=datetime.now().isoformat(),
                ),
                input_hash=ih,
                config_hash=ch,
                function_hash=fh,
                was_cached=False,
                enable_logging=enable_logging,
            )
    except Exception:
        pass

    # If lightweight mode, return only minimal data (logs) to the driver to avoid large deserialization
    _lightweight = isinstance(proc_payload, dict) and bool(proc_payload.get('lightweight_result'))
    if _lightweight:
        try:
            logs_only = None
            if isinstance(ret, dict) and '__logs__' in ret:
                logs_only = {'__logs__': ret.get('__logs__')}
            return ExecutionResult(name=process_name, result=logs_only, execution_time=exec_time, was_cached=False, error=None)
        except Exception:
            return ExecutionResult(name=process_name, result=None, execution_time=exec_time, was_cached=False, error=None)

    return ExecutionResult(name=process_name, result=ret, execution_time=exec_time, was_cached=False, error=None)


def _run_chart_process_on_worker(ctx: Any, proc_payload: Dict[str, Any], run_id: Optional[str]) -> Dict[str, Any]:
    name = proc_payload.get('name')
    if not name:
        logger.error("[Charts] No chart name in proc_payload")
        return {'output_dir': '', 'artifact_count': 0}

    chart_spec = proc_payload.get('chart_spec') or {}
    entrypoint = chart_spec.get('entrypoint') or ''
    reporting_python = chart_spec.get('reporting_python') or os.environ.get('MLOPS_REPORTING_PYTHON') or None
    project_id = getattr(ctx, 'project_id', None) or os.environ.get('MLOPS_PROJECT_ID') or 'default'
    rid = run_id or getattr(ctx, 'run_id', None) or os.environ.get('MLOPS_RUN_ID') or 'default'

    logger.info(f"[Charts] Starting chart '{name}' for run {rid}, project {project_id}")

    # Safeguard: mark process as running when the chart actually begins execution
    try:
        from .step_system import get_state_manager as _get_sm
        sm = _get_sm()
    except Exception:
        sm = None
    try:
        if sm and rid and name:
            already_running = False
            try:
                prev = sm.kv_store.list_run_steps(rid) if hasattr(sm, 'kv_store') else {}
                rec = (prev or {}).get(f"{name}.__process__") or {}
                status = str(rec.get('status') or '').lower()
                already_running = status in ('running','completed','cached','failed')
            except Exception:
                already_running = False
            if not already_running:
                deps = proc_payload.get('dependencies', []) or []
                dep_map = proc_payload.get('dependency_map') or {}
                ih, ch, fh = _compute_process_lookup_hashes_worker(sm, ctx, name, deps, dep_map)
                ch, fh = _apply_hash_overrides(proc_payload, ch, fh)
                sm.record_process_started(
                    rid,
                    name,
                    input_hash=ih,
                    config_hash=ch,
                    function_hash=fh,
                    started_at=time.time(),
                )
                logger.debug(f"[Charts] Marked '{name}' running for run {rid}")
    except Exception:
        pass

    # Build output dir under project artifacts (workspace-root based)
    workspace_root = get_workspace_root()
    projects_root = get_projects_root(workspace_root)
    out_dir = projects_root / project_id / 'artifacts' / 'charts' / rid / name / time.strftime('%Y%m%d_%H%M%S')
    out_dir.mkdir(parents=True, exist_ok=True)

    # Prepare environment
    env = os.environ.copy()
    env['MLOPS_PROJECT_ID'] = str(project_id)
    env['MLOPS_RUN_ID'] = str(rid)
    env['MLOPS_OUTPUT_DIR'] = str(out_dir)
    env['MLOPS_CHART_NAME'] = str(name)
    env['MLOPS_CHART_TYPE'] = 'static'

    # Include probe_paths (chart-level overrides merged with global spec at driver)
    try:
        if chart_spec.get('probe_paths'):
            env['MLOPS_PROBE_PATHS'] = json.dumps(chart_spec['probe_paths'])
    except Exception:
        pass

    # Ensure PYTHONPATH contains src dir only for source checkouts (installed packages don't need it)
    try:
        src_root = infer_source_root()
        if src_root and (src_root / "src").exists():
            env['PYTHONPATH'] = f"{src_root / 'src'}:{env.get('PYTHONPATH', '')}".rstrip(":")
    except Exception:
        pass

    # Always use framework entrypoint as a module, and import user script if provided
    # This ensures chart functions are properly discovered and executed
    if entrypoint:
        project_root = projects_root / project_id
        ep = resolve_relative_path(entrypoint, project_root=project_root, workspace_root=workspace_root)
        # Set import path for user's chart script
        env['MLOPS_CHART_IMPORT_FILES'] = str(ep)
        logger.info(f"[Charts] Will import user script: {ep}")

    # Build command - always use framework entrypoint as module
    py = reporting_python or os.environ.get('MLOPS_RUNTIME_PYTHON') or os.environ.get('MLOPS_REPORTING_PYTHON') or 'python'
    
    # Check if Python interpreter exists and is executable
    py_path = Path(py) if not py.startswith('python') else None
    if py_path and not py_path.exists():
        logger.error(f"[Charts] Python interpreter not found: {py}")
        logger.warning(f"[Charts] Falling back to system python3")
        py = 'python3'
    
    # Always run as module to ensure proper initialization
    cmd = [py, '-u', '-m', 'mlops.reporting.entrypoint', '--oneshot'] + list(chart_spec.get('args') or [])

    # Run chart
    import subprocess as _subprocess
    stdout_log = out_dir / 'stdout.log'
    stderr_log = out_dir / 'stderr.log'
    
    logger.info(f"[Charts] Executing chart '{name}': {' '.join(cmd)}")
    logger.info(f"[Charts] Output directory: {out_dir}")
    logger.info(f"[Charts] Python interpreter: {py}")
    logger.info(f"[Charts] Entrypoint: {entrypoint}")
    logger.info(f"[Charts] MLOPS_CHART_NAME env: {env.get('MLOPS_CHART_NAME')}")
    logger.info(f"[Charts] MLOPS_OUTPUT_DIR env: {env.get('MLOPS_OUTPUT_DIR')}")
    
    with open(stdout_log, 'w', buffering=1) as out_f, open(stderr_log, 'w', buffering=1) as err_f:
        # Write diagnostic info
        err_f.write(f"=== Chart Execution Diagnostics ===\n")
        err_f.write(f"Chart: {name}\n")
        err_f.write(f"Python: {py}\n")
        err_f.write(f"Command: {' '.join(cmd)}\n")
        err_f.write(f"CWD: {workspace_root}\n")
        err_f.write(f"Output dir: {out_dir}\n")
        err_f.write(f"===================================\n\n")
        err_f.flush()
        
        result = _subprocess.run(cmd, env=env, check=False, stdout=out_f, stderr=err_f, cwd=str(workspace_root))
    
    logger.info(f"[Charts] Chart '{name}' execution completed with return code: {result.returncode}")
    
    # Check if any PNGs were created
    png_count = len(list(out_dir.rglob('*.png')))
    logger.info(f"[Charts] Found {png_count} PNG file(s) in {out_dir}")
    
    # Upload/record artifacts (best-effort).
    try:
        from .step_system import get_state_manager as _get_sm
        sm = _get_sm()
    except Exception:
        sm = None

    if sm is not None:
        try:
            _record_chart_artifacts(sm, str(project_id), str(rid), str(name), out_dir, chart_type="static")
        except Exception as upload_exc:
            logger.warning(f"[Charts] Artifact recording failed: {upload_exc}")
    else:
        logger.warning("[Charts] No state manager available - artifacts not recorded")

    final_count = len(list(out_dir.rglob('*.png')))
    logger.info(f"[Charts] Chart '{name}' complete. Output dir: {out_dir}, PNG count: {final_count}")
    
    return {
        'output_dir': str(out_dir),
        'artifact_count': final_count,
    }


def _return_placeholder_cached_process_execution_result(process_name: str) -> ExecutionResult:
    return ExecutionResult(name=process_name, result=None, execution_time=0.0, was_cached=True, error=None)

def _return_placeholder_cached_process_execution_result_with_deps(process_name: str, dep_results: List[ExecutionResult]) -> ExecutionResult:
    for dep in dep_results or []:
        if dep and dep.error is not None:
            return ExecutionResult(name=process_name, result=None, execution_time=0.0, was_cached=False, error=f"Dependency {dep.name} failed: {dep.error}")
    return ExecutionResult(name=process_name, result=None, execution_time=0.0, was_cached=True, error=None)


def _worker_execute_step_task(step_name: str, process_name: Optional[str], context_arg: Any,
                              iteration: int = 0, run_id: Optional[str] = None) -> ExecutionResult:
    from .step_system import get_step_registry, set_current_context
    registry = get_step_registry()
    step_def = registry.get_step(step_name)
    if not step_def:
        try:
            if isinstance(context_arg, dict):
                global_params = context_arg.get('global_config') or {}
            else:
                global_params = getattr(context_arg, 'global_config', {}) or {}
            _maybe_import_custom_model_from_global_config(global_params)
            step_def = registry.get_step(step_name)
        except Exception:
            step_def = registry.get_step(step_name)
    if not step_def:
        raise ValueError(f"Step '{step_name}' not found in registry (worker). Ensure the model module defines and registers it.")

    try:
        from dask.distributed import get_worker  # type: ignore
        _worker = get_worker()
        _worker_addr = getattr(_worker, "address", "unknown")
    except Exception:
        _worker_addr = None
    try:
        import socket as _socket
        _host = _socket.gethostname()
    except Exception:
        _host = "unknown"
    logger.info(
        f"[Distributed] Executing step '{step_name}' (process {process_name}, iter {iteration}) "
        f"on worker={_worker_addr or 'n/a'} host={_host}"
    )

    start_time = time.time()

    from .step_system import StepContext as _Ctx
    if isinstance(context_arg, _Ctx):
        ctx = context_arg
    else:
        if isinstance(context_arg, dict):
            ctx = _build_step_context_from_payload(context_arg)
        else:
            try:
                ctx = _Ctx(project_id=getattr(context_arg, 'project_id', 'default'))
            except Exception:
                ctx = _Ctx(project_id='default')

    try:
        _gc = getattr(ctx, 'global_config', {}) if ctx else {}
        _pid = getattr(ctx, 'project_id', None)
        _maybe_init_worker_state_manager(_gc, _pid)
    except Exception as e:
        logger.warning(f"[Distributed] Worker state manager init failed for step {step_name}: {e}")

    set_current_context(ctx)
    # Deterministic task-level seeding (step scope)
    _seed_rng_for_task(run_id, process_name, step_name, iteration)
    try:
        from .step_system import get_current_state_manager as _get_sm
        _sm = _get_sm()
    except Exception:
        _sm = None
    try:
        _proc_name = process_name or getattr(ctx, 'current_process', None)
        if _sm and run_id and _proc_name and step_name:
            _sm.record_step_started(run_id, _proc_name, step_name)
    except Exception:
        pass
    try:
        # Execute step without auto-parameter resolution; context is available via current context
        # The step wrapper will inject context automatically if declared in the signature.
        result = step_def.func()
    finally:
        set_current_context(None)

    if not isinstance(result, dict):
        raise ValueError(f"Step '{step_name}' must return a dictionary, got {type(result).__name__}.")
    try:
        def _json_safe(v: Any) -> Any:
            import json as _json
            from collections.abc import Mapping, Sequence
            primitives = (str, int, float, bool, type(None))
            if isinstance(v, primitives):
                return v
            if isinstance(v, Mapping):
                return {str(k): _json_safe(val) for k, val in v.items()}
            if isinstance(v, Sequence) and not isinstance(v, (str, bytes, bytearray)):
                return [_json_safe(x) for x in v]
            try:
                _json.dumps(v)
                return v
            except Exception:
                return str(v)
        result = {k: _json_safe(v) for k, v in result.items()}
    except Exception:
        pass
    exec_time = time.time() - start_time
    if isinstance(result, dict):
        result['__execution_time__'] = exec_time
    ctx.step_results[step_name] = result
    return ExecutionResult(name=step_name, result=result, execution_time=exec_time, was_cached=False, error=None)


def _worker_execute_step_with_deps(step_name: str, process_name: Optional[str], context_payload: dict,
                                   dep_results: List[ExecutionResult], iteration: int = 0,
                                   run_id: Optional[str] = None) -> ExecutionResult:
    from .step_system import StepContext as _Ctx
    ctx = _build_step_context_from_payload(context_payload) if isinstance(context_payload, dict) else _Ctx(project_id='default')
    try:
        setattr(ctx, 'current_process', process_name)
    except Exception:
        pass
    for dep in dep_results:
        if dep.error is None and dep.result:
            ctx.step_results[dep.name] = dep.result
        else:
            raise RuntimeError(f"Dependency step {dep.name} failed: {dep.error}")
    return _worker_execute_step_task(step_name, process_name, ctx, iteration, run_id)


def _create_worker_state_manager(cache_config: Dict[str, Any]):
    from .step_state_manager import StepStateManager
    from pathlib import Path
    import os
    import logging
    
    kv_store = None
    kv_store_type = cache_config.get('kv_store_type', '')
    if 'GCP' in kv_store_type or 'Firestore' in kv_store_type:
        try:
            from ..storage.adapters.gcp_kv_store import GCPStore
            kv_config = cache_config.get('kv_store_config', {})
            kv_store = GCPStore(
                project_id=kv_config.get('project_id'),
                gcp_project=kv_config.get('gcp_project'),
                topic_name=kv_config.get('topic_name'),
                emulator_host=kv_config.get('emulator_host'),
            )
        except Exception:
            kv_store = None
    object_store = None
    obj_store_type = cache_config.get('object_store_type', '')
    if 'GCS' in obj_store_type:
        try:
            from ..storage.adapters.gcs_object_store import GCSObjectStore
            obj_config = cache_config.get('object_store_config', {})
            object_store = GCSObjectStore(
                bucket=obj_config.get('bucket'),
                prefix=obj_config.get('prefix')
            )
        except Exception:
            object_store = None
    if kv_store:
        cache_dir = Path(os.getenv('MLOPS_STEP_CACHE_DIR') or '/tmp/mlops-step-cache')
        return StepStateManager(
            cache_dir=cache_dir,
            kv_store=kv_store,
            logger=logging.getLogger(__name__),
            object_store=object_store
        )
    return None


def _worker_execute_process_task(proc_payload: Dict[str, Any], context_payload: Dict[str, Any],
                                run_id: Optional[str] = None) -> ExecutionResult:
    process_name = proc_payload.get('name')
    start_time = time.time()

    from .step_system import StepContext as _Ctx
    try:
        if isinstance(context_payload, _Ctx):
            ctx = context_payload
        else:
            ctx = _build_step_context_from_payload(context_payload) if isinstance(context_payload, dict) else _Ctx(project_id='default')
    except Exception:
        ctx = _Ctx(project_id='default')

    try:
        try:
            _gc2 = context_payload.get('global_config') if isinstance(context_payload, dict) else {}
            _pid2 = context_payload.get('project_id') if isinstance(context_payload, dict) else None
            _maybe_init_worker_state_manager(_gc2, _pid2)
        except Exception:
            pass

        # Deterministic task-level seeding (process scope)
        _seed_rng_for_task(run_id, process_name, None, 0)

        # Process start is now recorded inside _execute_process_on_worker at the exact timing start

        return _execute_process_on_worker(ctx, proc_payload, run_id)
    except Exception as e:
        exec_time = time.time() - start_time
        error_result = {'__error_context__': str(e)}
        return ExecutionResult(name=process_name, result=error_result, execution_time=exec_time, was_cached=False, error=str(e))


def _worker_execute_process_with_deps(proc_payload: Dict[str, Any], context_payload: Dict[str, Any],
                                     dep_results: List[ExecutionResult], run_id: Optional[str] = None) -> ExecutionResult:
    from .step_system import StepContext as _Ctx
    ctx = _build_step_context_from_payload(context_payload) if isinstance(context_payload, dict) else _Ctx(project_id='default')
    try:
        setattr(ctx, 'current_process', proc_payload.get('name'))
    except Exception:
        pass
    # Ensure a worker state manager exists (with object store when available) and custom model is imported
    try:
        from .step_system import get_state_manager as _get_sm, set_state_manager as _set_sm
        sm_existing = _get_sm()
        # Prefer cache_config-provisioned state manager when missing or when object_store is absent
        try:
            cfg = proc_payload.get('cache_config') if isinstance(proc_payload, dict) else None
        except Exception:
            cfg = None
        needs_obj_store = False
        if sm_existing is None:
            needs_obj_store = True
        else:
            try:
                needs_obj_store = getattr(sm_existing, 'object_store', None) is None
            except Exception:
                needs_obj_store = True
        if cfg and needs_obj_store:
            try:
                sm_new = _create_worker_state_manager(cfg)
                if sm_new is not None:
                    _set_sm(sm_new)
            except Exception:
                pass
        # Import custom model on the worker so process/step registries are populated for hashing
        try:
            _maybe_import_custom_model_from_global_config(getattr(ctx, 'global_config', {}) or {})
        except Exception:
            pass
    except Exception:
        pass
    for dep in dep_results:
        if dep.error is not None:
            return ExecutionResult(name=proc_payload.get('name'), result=None, execution_time=0.0, was_cached=False, error=f"Dependency {dep.name} failed: {dep.error}")
        if not getattr(dep, 'was_cached', False) and not dep.result:
            return ExecutionResult(name=proc_payload.get('name'), result=None, execution_time=0.0, was_cached=False, error=f"Dependency {dep.name} failed: {dep.error}")
        try:
            if dep.result is not None:
                ctx.step_results[dep.name] = _strip_internal_keys(dep.result)
            else:
                # Hydrate cached dependency placeholder on worker using state manager
                try:
                    from .step_system import get_state_manager as _get_sm
                    sm = _get_sm()
                except Exception:
                    sm = None
                if sm is not None:
                    try:
                        # Compute hashes for the dependency using the same worker helper
                        deps_for_dep = []
                        try:
                            dep_map = proc_payload.get('dependency_map') or {}
                            deps_for_dep = (dep_map or {}).get(dep.name, [])
                        except Exception:
                            deps_for_dep = []
                        ih, ch, fh = _compute_process_lookup_hashes_worker(sm, ctx, dep.name, deps_for_dep, proc_payload.get('dependency_map') or {})
                    except Exception:
                        ih = ch = fh = None
                    loaded = None
                    # Try hash-based lookup first
                    try:
                        if hasattr(sm, 'get_cached_process_result_with_metadata'):
                            data = sm.get_cached_process_result_with_metadata(dep.name, input_hash=ih, config_hash=ch, function_hash=fh)
                            if data is not None:
                                loaded, _, _ = data
                    except Exception:
                        loaded = None
                    # Fallback: if context_payload carried a cache_path alias
                    if loaded is None:
                        try:
                            cache_hint = None
                            try:
                                s = (context_payload.get('step_results') or {}).get(dep.name, {}) if isinstance(context_payload, dict) else {}
                                cache_hint = s.get('cache_path') if isinstance(s, dict) else None
                            except Exception:
                                cache_hint = None
                            if cache_hint and hasattr(sm, 'load_process_result_from_path'):
                                loaded = sm.load_process_result_from_path(cache_hint)
                        except Exception:
                            loaded = None
                    if isinstance(loaded, dict):
                        try:
                            ctx.step_results[dep.name] = _strip_internal_keys(loaded)
                        except Exception:
                            ctx.step_results[dep.name] = loaded
            inner = {}
            try:
                inner = dep.result.get('__step_results__', {}) if isinstance(dep.result, dict) else {}
            except Exception:
                inner = {}
            if isinstance(inner, dict):
                ctx.step_results.update(inner)
        except Exception:
            continue
    return _worker_execute_process_task(proc_payload, ctx, run_id)


def _maybe_init_worker_state_manager(global_config: Any, project_id: Optional[str]) -> None:
    try:
        from .step_system import get_state_manager as _get_sm, set_state_manager as _set_sm
        sm_existing = _get_sm()
        if sm_existing is not None:
            return
        import os as _os
        import logging as _logging
        logger = _logging.getLogger(__name__)
        gcp_creds = _os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        gcp_project = _os.getenv('GOOGLE_CLOUD_PROJECT')
        logger.info(
            f"[Worker] Initializing state manager with GOOGLE_APPLICATION_CREDENTIALS={'SET' if gcp_creds else 'UNSET'}, "
            f"GOOGLE_CLOUD_PROJECT={gcp_project or 'UNSET'}"
        )
        # Prefer top-level cache; fallback to nested model.parameters.cache for backward compatibility
        cache_cfg = (global_config.get('cache') or {}) if isinstance(global_config, dict) else {}
        if not cache_cfg and isinstance(global_config, dict):
            try:
                cache_cfg = (global_config.get('model') or {}).get('parameters', {}).get('cache') or {}
            except Exception:
                cache_cfg = {}
        backend_cfg = cache_cfg.get('backend') if isinstance(cache_cfg, dict) else {}
        # Derive missing GCP env from backend config and project layout
        try:
            from pathlib import Path as _Path
            creds_rel = (backend_cfg or {}).get('credentials_json')
            if creds_rel and not _os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                repo_root = get_workspace_root()
                pid_effective = project_id or _os.getenv('MLOPS_PROJECT_ID') or 'default'
                cred_path = (get_projects_root(repo_root) / str(pid_effective) / str(creds_rel)).resolve()
                if cred_path.exists():
                    _os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', str(cred_path))
            if (backend_cfg or {}).get('gcp_project') and not _os.getenv('GOOGLE_CLOUD_PROJECT'):
                _os.environ.setdefault('GOOGLE_CLOUD_PROJECT', str(backend_cfg.get('gcp_project')))
        except Exception:
            pass
        from mlops.storage.adapters.memory_store import InMemoryStore
        kv_store = None
        pid_effective = project_id or _os.getenv('MLOPS_PROJECT_ID') or 'default'
        backend_type = (backend_cfg.get('type') if isinstance(backend_cfg, dict) else None) or _os.getenv('MLOPS_KV_BACKEND') or 'redis'
        logger.info(
            f"[Worker] KV backend selection -> MLOPS_KV_BACKEND={_os.getenv('MLOPS_KV_BACKEND') or 'unset'}, "
            f"resolved={backend_type}, project_ns={pid_effective}"
        )
        if backend_type == 'redis':
            logger.info(
                f"[Worker] Redis env -> host={_os.getenv('MLOPS_REDIS_HOST')}, "
                f"port={_os.getenv('MLOPS_REDIS_PORT')}, db={_os.getenv('MLOPS_REDIS_DB')}"
            )
        else:
            logger.info(f"[Worker] GCP env -> FIRESTORE_EMULATOR_HOST={_os.getenv('FIRESTORE_EMULATOR_HOST') or 'unset'}")
        if backend_type == 'redis':
            try:
                from mlops.storage.adapters.redis_store import RedisStore
                cfg = dict(backend_cfg) if isinstance(backend_cfg, dict) else {}
                kv_store = RedisStore(
                    project_id=pid_effective,
                    host=cfg.get('host') or _os.getenv('MLOPS_REDIS_HOST'),
                    port=cfg.get('port') or _os.getenv('MLOPS_REDIS_PORT'),
                    db=cfg.get('db') or _os.getenv('MLOPS_REDIS_DB'),
                    password=cfg.get('password') or _os.getenv('MLOPS_REDIS_PASSWORD'),
                )
            except Exception:
                kv_store = None
        if kv_store is None:
            try:
                from mlops.storage.adapters.gcp_kv_store import GCPStore
                cfg = dict(backend_cfg) if isinstance(backend_cfg, dict) else {}
                kv_store = GCPStore(
                    project_id=pid_effective,
                    gcp_project=cfg.get('gcp_project') or _os.getenv('GOOGLE_CLOUD_PROJECT'),
                    topic_name=cfg.get('topic_name'),
                    emulator_host=cfg.get('emulator_host') or _os.getenv('FIRESTORE_EMULATOR_HOST'),
                )
            except Exception:
                kv_store = None
        if kv_store is None:
            kv_store = InMemoryStore(project_id or 'default')
        obj_store = None
        obj_prefix = None
        try:
            store_cfg = cache_cfg.get('object_store') if isinstance(cache_cfg, dict) else None
            if not store_cfg and isinstance(global_config, dict):
                try:
                    store_cfg = ((global_config.get('model') or {}).get('parameters', {}).get('cache') or {}).get('object_store')
                except Exception as e:
                    logger.warning(f"[Worker] Failed to extract object_store config from model.parameters.cache: {e}")
                    store_cfg = None
            
            logger.info(f"[Worker] Object store config extraction -> store_cfg={'present' if store_cfg else 'None'}, type={store_cfg.get('type') if isinstance(store_cfg, dict) else 'N/A'}")
            
            if isinstance(store_cfg, dict) and store_cfg.get('type') == 'gcs':
                from mlops.storage.adapters.gcs_object_store import GCSObjectStore
                bucket = store_cfg.get('bucket') or _os.getenv('MLOPS_GCS_BUCKET')
                prefix = store_cfg.get('prefix') or _os.getenv('MLOPS_GCS_PREFIX')
                logger.info(f"[Worker] GCS config -> bucket={bucket or 'None'}, prefix={prefix or 'None'}")
                if bucket:
                    try:
                        obj_store = GCSObjectStore(bucket=bucket, prefix=prefix)
                        obj_prefix = None
                        logger.info(f"[Worker] Successfully initialized GCS object store (bucket={bucket})")
                    except Exception as gcs_e:
                        logger.error(f"[Worker] Failed to initialize GCS object store: {gcs_e}")
                        obj_store = None
                        obj_prefix = None
                else:
                    logger.warning("[Worker] GCS object_store configured but 'bucket' is missing")
            elif store_cfg:
                logger.info(f"[Worker] Object store type '{store_cfg.get('type')}' not supported or not 'gcs'")
        except Exception as e:
            logger.error(f"[Worker] Unexpected error during object store initialization: {e}")
            obj_store = None
            obj_prefix = None
        from pathlib import Path as _Path
        cache_dir = _Path(_os.getenv('MLOPS_STEP_CACHE_DIR') or '/tmp/mlops-step-cache')
        from .step_state_manager import StepStateManager as _SSM
        try:
            ttl_val = int(((cache_cfg or {}).get('ttl_hours') if isinstance(cache_cfg, dict) else 24) or 24)
        except Exception:
            ttl_val = 24
        sm_new = _SSM(cache_dir=cache_dir, kv_store=kv_store, logger=logging.getLogger(__name__), cache_ttl_hours=ttl_val, object_store=obj_store, object_prefix=obj_prefix)
        logger.info(
            f"[Worker] StateManager created -> kv_store={type(kv_store).__name__ if kv_store else 'None'}, "
            f"object_store={type(obj_store).__name__ if obj_store else 'None'}"
        )
        _set_sm(sm_new)
    except Exception:
        return


