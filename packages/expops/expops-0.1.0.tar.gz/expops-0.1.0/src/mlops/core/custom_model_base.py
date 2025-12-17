from __future__ import annotations

from typing import Any, Optional


class MLOpsCustomModelBase:
    """Lightweight base class for user-defined models.

    This class is intentionally minimal: it stores hyperparameters and (when not
    explicitly provided) tries to resolve process-scoped hyperparameters from the
    active `StepContext`.
    """

    def __init__(self, hyperparameters: Optional[dict[str, Any]] = None) -> None:
        """Initialize with hyperparameters.

        If not provided, automatically resolve merged hyperparameters from the
        active step context for the current process (global overrides -> process overrides).
        """
        if hyperparameters and isinstance(hyperparameters, dict):
            self.hyperparameters = hyperparameters
            return
        # Auto-resolve from context without requiring user code to call into the platform
        try:
            from .step_system import get_current_context  # Local import to avoid cycles at module import time
            ctx = get_current_context()
            if ctx and hasattr(ctx, 'get_hyperparameters'):
                proc = getattr(ctx, 'current_process', None)
                resolved = ctx.get_hyperparameters(proc)
                self.hyperparameters = resolved if isinstance(resolved, dict) else {}
            else:
                self.hyperparameters = {}
        except Exception:
            self.hyperparameters = {}
    
    def get_step_registry(self) -> Any:
        """Get the step registry containing all @step decorated functions."""
        from .step_system import get_step_registry
        return get_step_registry()