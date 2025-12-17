from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any


def _read_requirement_lines(path: Path) -> list[str]:
    lines: list[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            lines.append(line)
    return lines


def load_requirements(config: dict[str, Any]) -> list[str]:
    """Load pip-style requirements from a config dict.

    Supported keys:
    - `requirements`: list[str] or newline-separated str
    - `requirements_file`: path to a requirements.txt file
    """
    if "requirements" in config:
        reqs = config.get("requirements")
        if isinstance(reqs, str):
            out: list[str] = []
            for raw in reqs.splitlines():
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                out.append(line)
            return out
        if isinstance(reqs, list):
            out: list[str] = []
            for item in reqs:
                s = str(item).strip()
                if s and not s.startswith("#"):
                    out.append(s)
            return out

    req_file = config.get("requirements_file")
    if req_file:
        path = Path(str(req_file))
        if not path.exists():
            raise FileNotFoundError(f"Requirements file not found: {path}")
        return _read_requirement_lines(path)

    return []


_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+")


def requirement_to_package_name(requirement: str) -> str:
    """Best-effort extract a package name for `pip show` from a requirement spec."""
    s = str(requirement).strip()
    if not s:
        return ""

    # Handle "name @ url"
    if "@" in s and not s.startswith("@"):
        s = s.split("@", 1)[0].strip()

    # Strip environment markers (PEP 508)
    if ";" in s:
        s = s.split(";", 1)[0].strip()

    # Strip extras
    if "[" in s:
        s = s.split("[", 1)[0].strip()

    # Strip version specifiers (common cases)
    for op in ("===", "==", ">=", "<=", "!=", "~=", ">", "<", "="):
        if op in s:
            s = s.split(op, 1)[0].strip()
            break

    m = _NAME_RE.match(s)
    return m.group(0) if m else s


def verify_pip_requirements(python_exec: str, requirements: list[str]) -> tuple[bool, list[str]]:
    """Return (ok, missing_packages) using `pip show`."""
    missing: list[str] = []
    for req in requirements or []:
        name = requirement_to_package_name(req)
        if not name:
            continue
        try:
            subprocess.check_output(
                [python_exec, "-m", "pip", "show", name],
                text=True,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            missing.append(name)
        except FileNotFoundError:
            missing.append(name)
    return (len(missing) == 0), missing


