from __future__ import annotations

from typing import Any, Optional


def compute_process_hashes(
    state_manager: Any,
    context: Any,
    process_name: str,
    dependency_map: dict[str, list[str]],
    lookup_name: Optional[str] = None,
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Compute (input_hash, config_hash, function_hash) deterministically for a process.

    Determinism requirements:
    - Predecessors are traversed using a sorted order
    - Upstream signatures are dictionaries with stable key order (sorted by name)
    - Config hashing uses a filtered, ordered payload
    - Function hash is augmented with nested step AST and referenced step function hashes
    """
    try:
        from .step_system import get_process_registry, get_step_registry
    except Exception:
        get_process_registry = None  # type: ignore[assignment]
        get_step_registry = None  # type: ignore[assignment]

    # Build a stable mapping of configured process names -> code function names (registry keys)
    _lookup_map: dict[str, str] = {}
    try:
        global_cfg = getattr(context, "global_config", {}) or {}
        pipeline_cfg = (global_cfg.get("pipeline", {}) or {}) if isinstance(global_cfg, dict) else {}
        for p in (pipeline_cfg.get("processes", []) or []):
            if not isinstance(p, dict):
                continue
            name = p.get("name")
            code_fn = p.get("code_function")
            if name and code_fn:
                _lookup_map[str(name)] = str(code_fn)
    except Exception:
        _lookup_map = {}

    def _filtered_global_settings(gc: Any) -> dict[str, Any]:
        try:
            if not isinstance(gc, dict):
                return {}
            return {k: v for k, v in gc.items() if k not in ("pipeline", "project_config_file_hash")}
        except Exception:
            return {}

    # 1) Build upstream_signatures recursively (ih/ch/fh) using dependency_map
    def _sorted_preds(name: str) -> list[str]:
        try:
            preds = list(dependency_map.get(name, []) or [])
            preds = sorted(set(preds))
            return preds
        except Exception:
            return []

    def _sig_for(up_proc: str) -> dict[str, Optional[str]]:
        ih_u, ch_u, fh_u = _compute_for(up_proc)
        return {"ih": ih_u, "ch": ch_u, "fh": fh_u}

    memo: dict[str, tuple[Optional[str], Optional[str], Optional[str]]] = {}

    def _compute_for(name: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
        cached = memo.get(name)
        if cached is not None:
            return cached

        # Recursively compute signature for an upstream process
        try:
            upstream_signatures: dict[str, dict[str, Optional[str]]] = {}
            for p in _sorted_preds(name):
                try:
                    upstream_signatures[p] = _sig_for(p)
                except Exception:
                    continue
            input_surface = {
                "global_config_keys": sorted(list((getattr(context, "global_config", {}) or {}).keys())),
                "project_id": getattr(context, "project_id", None),
                "upstream_signatures": {k: upstream_signatures[k] for k in sorted(upstream_signatures.keys())},
            }
            ih = state_manager._compute_hash(input_surface) if state_manager else None
        except Exception:
            ih = None

        try:
            global_config = getattr(context, "global_config", {}) or {}
            # Build process-scoped config hash: (global_without_pipeline, current process hyperparameters, process name)
            process_hparams: dict[str, Any] = {}
            try:
                pipeline_cfg = global_config.get("pipeline", {}) if isinstance(global_config, dict) else {}
                for proc_cfg in (pipeline_cfg.get("processes", []) or []):
                    if isinstance(proc_cfg, dict) and proc_cfg.get("name") == name:
                        maybe = proc_cfg.get("hyperparameters", {}) or {}
                        process_hparams = dict(maybe) if isinstance(maybe, dict) else {}
                        break
            except Exception:
                process_hparams = {}
            # Exclude the pipeline graph and synthetic full-config hash to avoid global invalidations
            enhanced_config = {
                "global_config": _filtered_global_settings(global_config),
                "process_hyperparameters": process_hparams,
                "process_name": name,
            }
            ch = state_manager._compute_hash(enhanced_config) if state_manager else None
        except Exception:
            try:
                # Last resort fallback: minimal global-only hash without pipeline
                minimal = _filtered_global_settings(getattr(context, "global_config", {}) or {})
                ch = state_manager._compute_hash(minimal) if state_manager else None
            except Exception:
                ch = None

        try:
            pr = get_process_registry() if callable(get_process_registry) else None
            _node_lookup = _lookup_map.get(name)
            if not _node_lookup and name == process_name:
                _node_lookup = lookup_name
            pdef = pr.get_process(_node_lookup or name) if pr else None
            orig_fn = getattr(pdef, "original_func", None) if pdef else None
            fh = state_manager._compute_function_hash(orig_fn or getattr(pdef, "runner", None)) if (state_manager and pdef) else None

            try:
                sr = get_step_registry() if callable(get_step_registry) else None
                used_step_names = set()
                try:
                    import inspect as _inspect, ast as _ast
                    src = _inspect.getsource(orig_fn or getattr(pdef, "runner", None)) if pdef else ""
                    tree = _ast.parse(src) if src else None

                    class _CallVisitor(_ast.NodeVisitor):
                        def __init__(self):
                            self.names = set()
                        def visit_Call(self, node):
                            try:
                                if isinstance(node.func, _ast.Name):
                                    self.names.add(node.func.id)
                                elif isinstance(node.func, _ast.Attribute):
                                    self.names.add(node.func.attr)
                            except Exception:
                                pass
                            self.generic_visit(node)

                    class _NestedStepVisitor(_ast.NodeVisitor):
                        def __init__(self):
                            self.func_nodes = {}
                        def visit_FunctionDef(self, node):
                            try:
                                has_step = False
                                for deco in (node.decorator_list or []):
                                    if isinstance(deco, _ast.Name) and deco.id == "step":
                                        has_step = True
                                    elif isinstance(deco, _ast.Call) and isinstance(deco.func, _ast.Name) and deco.func.id == "step":
                                        has_step = True
                                if has_step and isinstance(node.name, str):
                                    self.func_nodes[node.name] = node
                            except Exception:
                                pass
                            self.generic_visit(node)

                    nv = None
                    if tree is not None:
                        cv = _CallVisitor()
                        cv.visit(tree)
                        used_step_names = set(cv.names or set())
                        nv = _NestedStepVisitor()
                        nv.visit(tree)
                except Exception:
                    used_step_names = set()
                    nv = None

                step_hashes: dict[str, str] = {}
                # 1) Nested steps (AST)
                try:
                    import ast as _ast
                    if nv and getattr(nv, "func_nodes", None):
                        for _nm in sorted(nv.func_nodes.keys()):
                            try:
                                _node = nv.func_nodes[_nm]
                                normalized = _ast.dump(_node, annotate_fields=True, include_attributes=False)
                                s_hash = state_manager._compute_hash({"ast": normalized}) if state_manager else None
                                if s_hash:
                                    step_hashes[_nm] = s_hash
                            except Exception:
                                continue
                except Exception:
                    pass
                for _nm in sorted(list(used_step_names)):
                    if _nm in step_hashes:
                        continue
                    try:
                        sdef = sr.get_step(_nm) if sr else None
                        if sdef is not None:
                            s_orig = getattr(sdef, "original_func", None) or getattr(sdef, "func", None)
                            s_hash = state_manager._compute_function_hash(s_orig) if (state_manager and s_orig) else None
                            if s_hash:
                                step_hashes[_nm] = s_hash
                    except Exception:
                        continue
                if step_hashes and fh:
                    # Stable combination by sorting keys
                    ordered = {k: step_hashes[k] for k in sorted(step_hashes.keys())}
                    fh = state_manager._compute_hash({"proc": fh, "steps": ordered})
            except Exception:
                pass
        except Exception:
            fh = None

        out = (ih, ch, fh)
        memo[name] = out
        return out

    return _compute_for(process_name)


