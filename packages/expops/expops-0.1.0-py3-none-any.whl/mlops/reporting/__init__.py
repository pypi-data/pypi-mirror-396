from __future__ import annotations

from typing import Any

from .context import ChartContext
from .registry import chart


def run_chart_entrypoint(*args: Any, **kwargs: Any) -> int:
    from .entrypoint import run_chart_entrypoint as _impl

    return _impl(*args, **kwargs)

__all__ = ["chart", "ChartContext", "run_chart_entrypoint"]


