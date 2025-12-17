from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar, overload

ChartFn = Callable[..., Any]
CHART_FUNCS: dict[str, ChartFn] = {}

_F = TypeVar("_F", bound=ChartFn)


@overload
def chart(fn: _F) -> _F: ...


@overload
def chart(name: str | None = None) -> Callable[[_F], _F]: ...


def chart(name: str | None | _F = None):
    """Register a chart function by name.

    The registration key is either:
    - the function name, or
    - the explicit `name=...`

    The runner (`mlops.reporting.entrypoint`) dispatches based on `MLOPS_CHART_NAME`.
    """

    def _decorator(fn: _F) -> _F:
        key = (name if isinstance(name, str) else getattr(fn, "__name__", "")).strip()
        if key:
            CHART_FUNCS[key] = fn
        return fn

    # Allow `@chart` without parentheses.
    if callable(name) and not isinstance(name, str):
        fn2 = name
        name = None
        return _decorator(fn2)  # type: ignore[arg-type]

    return _decorator


__all__ = [
    "chart",
    "CHART_FUNCS",
]


