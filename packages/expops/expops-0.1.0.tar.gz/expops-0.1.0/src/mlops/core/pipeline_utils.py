from __future__ import annotations

from typing import Dict, List, Optional, Any
from pathlib import Path


def _load_project_config(project_dir: Path | str, project_id: str) -> Dict[str, Any]:
    import yaml  # Local import to avoid import-time dependency if unused
    project_dir = Path(project_dir).resolve()
    config_path = project_dir / "projects" / project_id / "configs" / "project_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _get_pipeline_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    return (cfg.get("model", {}).get("parameters", {}).get("pipeline", {}) or {})


def _parse_processes_from_pipeline(pipeline_config: Dict[str, Any]) -> List[str]:
    processes: List[str] = []

    # From explicit processes list
    for p in pipeline_config.get("processes", []) or []:
        name = p.get("name")
        if name and name not in processes:
            processes.append(name)

    # From adjacency list (NetworkX-like string or list)
    for src, tgt in _iter_adjlist_edges(pipeline_config.get("process_adjlist")):
        if src and src not in processes:
            processes.append(src)
        if tgt and tgt not in processes:
            processes.append(tgt)

    return processes


def _iter_adjlist_edges(adjlist: Any) -> List[tuple[str, str]]:
    """Parse a NetworkX-style adjacency list into directed edges (src, tgt)."""
    lines: List[str] = []
    if isinstance(adjlist, str):
        lines = adjlist.splitlines()
    elif isinstance(adjlist, list):
        lines = [str(x) for x in adjlist]

    edges: List[tuple[str, str]] = []
    for raw in lines:
        line = str(raw).strip()
        if not line:
            continue
        if "#" in line:
            line = line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            # No outgoing edges on this line
            continue
        src = parts[0]
        for tgt in parts[1:]:
            edges.append((src, tgt))
    return edges


def _build_process_adjacency(pipeline_config: Dict[str, Any]) -> Dict[str, List[str]]:
    processes = _parse_processes_from_pipeline(pipeline_config)
    adj: Dict[str, List[str]] = {p: [] for p in processes}

    # From explicit processes depends_on
    for p in pipeline_config.get("processes", []) or []:
        name = p.get("name")
        deps = p.get("depends_on", []) or []
        for dep in deps:
            adj.setdefault(dep, [])
            if name not in adj[dep]:
                adj[dep].append(name)

    # From adjacency list
    for src, tgt in _iter_adjlist_edges(pipeline_config.get("process_adjlist")):
        adj.setdefault(src, [])
        if tgt not in adj[src]:
            adj[src].append(tgt)

    return adj



def parse_networkx_config_from_project(project_dir: Path | str, project_id: str) -> Dict[str, Any]:
    """Return a lightweight parsed view: {processes: [names], adj: {u:[v,...]}, steps_by_process: {proc:[step_names]}}"""
    cfg = _load_project_config(project_dir, project_id)
    pipeline_cfg = _get_pipeline_config(cfg)

    processes = _parse_processes_from_pipeline(pipeline_cfg)
    adj = _build_process_adjacency(pipeline_cfg)

    # Manual-step mode: do not consider configured or auto-discovered steps
    steps_by_process: Dict[str, List[str]] = {p: [] for p in processes}

    return {
        "processes": processes,
        "adj": adj,
        "steps_by_process": steps_by_process,
        "global_config": cfg.get("model", {}).get("parameters", {}) or {},
    }


def get_process_graph_summary(config_like: Dict[str, Any]) -> Dict[str, Any]:
    processes: List[str] = list(config_like.get("processes", []) or [])
    adj: Dict[str, List[str]] = dict(config_like.get("adj", {}) or {})

    node_set = set(processes)
    for u, vs in adj.items():
        node_set.add(u)
        for v in vs:
            node_set.add(v)

    nodes = list(node_set)
    indeg: Dict[str, int] = {n: 0 for n in nodes}
    for u, vs in adj.items():
        for v in vs:
            indeg[v] = indeg.get(v, 0) + 1

    return {"nodes": nodes, "adj": adj, "indeg": indeg}


def get_process_graph_summary_from_project(project_dir: Path | str, project_id: str) -> Dict[str, Any]:
    config_like = parse_networkx_config_from_project(project_dir, project_id)
    return get_process_graph_summary(config_like)




def setup_environment_and_write_interpreter(
    project_dir: Path | str,
    project_id: str,
    env_file: Path | str,
) -> str:
    # Use a relative import to work whether invoked as `mlops.*` or `src.mlops.*`
    from ..managers.reproducibility_manager import ReproducibilityManager

    project_dir = Path(project_dir).resolve()
    env_file = Path(env_file)

    config_path = project_dir / "projects" / project_id / "configs" / "project_config.yaml"
    rm = ReproducibilityManager(str(config_path), project_path=project_dir / "projects" / project_id)
    cfg = rm.config or {}
    env_cfg = cfg.get("environment", {}) if isinstance(cfg.get("environment", {}), dict) else {}

    if "venv" in env_cfg:
        vcfg = env_cfg.get("venv") or {}
        if not isinstance(vcfg, dict):
            vcfg = {}
        if not vcfg.get("name"):
            vcfg["name"] = project_id
        env_cfg["venv"] = vcfg
        cfg["environment"] = env_cfg
        rm.config = cfg

    rm.setup_environment()
    py = rm.python_interpreter
    Path(env_file).write_text(py)
    return py 