from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional


class ChartContext:
    """Runtime context passed to chart functions.

    The platform supports two chart styles:
    - **static**: chart function receives resolved `metrics` (dict)
    - **dynamic**: chart function receives `probe_paths` and may subscribe to updates
    """

    def __init__(
        self,
        output_dir: Path,
        project_id: str,
        run_id: str,
        kv_path: str,
        probe_id: Optional[str],
        theme: str,
        chart_name: str,
        metrics: Optional[dict[str, Any]] = None,
        probe_ids: Optional[dict[str, str]] = None,
        chart_type: str = "static",
    ):
        self.output_dir = output_dir
        self.project_id = project_id
        self.run_id = run_id
        self.kv_path = kv_path
        self.probe_id = probe_id
        self.theme = theme
        self.chart_name = chart_name
        self.metrics = metrics or {}
        self.probe_ids = probe_ids or {}
        self.chart_type = chart_type

    def _firestore_client(self) -> Optional[Any]:
        try:
            from google.cloud import firestore  # type: ignore
        except Exception:
            return None
        try:
            return firestore.Client()
        except Exception:
            return None

    def load_payload(self) -> Optional[dict[str, Any]]:
        """Deprecated helper: load a document at `self.kv_path` from Firestore (if available)."""
        client = self._firestore_client()
        if client is None:
            return None
        try:
            root = client.collection("mlops_projects").document(self.project_id)
            rel_path = (self.kv_path or "").strip("/")
            parts = rel_path.split("/") if rel_path else []
            if not parts or len(parts) % 2 != 0:
                return None
            ref = root
            for i in range(0, len(parts), 2):
                ref = ref.collection(parts[i]).document(parts[i + 1])
            snap = ref.get()
            return snap.to_dict() if getattr(snap, "exists", False) else None
        except Exception:
            return None

    def get_firestore_client(self) -> Optional[Any]:
        """Deprecated: prefer `_firestore_client()` or KV APIs."""
        return self._firestore_client()
    
    # Deprecated: id-based refs no longer used
    def get_probe_ref(self, probe_id: str) -> Optional[Any]:
        return None
    
    def get_probe_metrics_ref(self, probe_id: str) -> Optional[Any]:
        # Deprecated
        return None

    def get_probe_metrics_ref_by_path(self, probe_path: str) -> Optional[Any]:
        """Resolve a probe_path to its metrics document reference.

        This allows dynamic charts to subscribe directly using the configured
        probe path without dealing with probe IDs.

        Args:
            probe_path: The logical probe path as specified in chart config.

        Returns:
            Firestore document reference for the metrics document, or None if
            it cannot be resolved or Firestore is unavailable.
        """
        client = self._firestore_client()
        if client is None:
            return None
        try:
            from mlops.storage.path_utils import encode_probe_path  # type: ignore
        except Exception:
            return None
        try:
            enc = encode_probe_path(probe_path)
            return (
                client.collection("mlops_projects")
                .document(self.project_id)
                .collection("metric")
                .document(self.run_id)
                .collection("probes_by_path")
                .document(enc)
            )
        except Exception:
            return None

    def savefig(self, filename: "os.PathLike[str] | str", fig: Optional[Any] = None, **savefig_kwargs: Any) -> Path:
        """Save a matplotlib figure under this context's output directory.

        - Ensures parent directories exist
        - If `filename` is relative, it is resolved under `self.output_dir`
        - If `fig` is provided, calls `fig.savefig(...)`; otherwise uses pyplot.savefig on current figure

        Returns the resolved output path.
        """
        out_path = Path(filename)
        if not out_path.is_absolute():
            out_path = self.output_dir / out_path
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Best-effort; downstream save will raise if it truly cannot write
            pass
        if fig is not None:
            fig.savefig(out_path, **savefig_kwargs)
        else:
            # Import locally to avoid hard dependency at module import time
            try:
                import matplotlib.pyplot as _plt  # type: ignore
                _plt.savefig(out_path, **savefig_kwargs)
            except Exception:
                # Re-raise for caller context
                raise
        return out_path

    def get_run_status(self) -> Optional[str]:
        """Return lowercased run status (best-effort)."""
        try:
            from .kv_utils import create_kv_store
            kv = create_kv_store(self.project_id)
            if kv and hasattr(kv, "get_run_status"):
                status = kv.get_run_status(self.run_id)
                if status:
                    return str(status).lower()
        except Exception:
            pass
        client = self._firestore_client()
        if client is None:
            return None
        try:
            snap = (
                client.collection("mlops_projects")
                .document(self.project_id)
                .collection("runs")
                .document(self.run_id)
                .get()
            )
            if not getattr(snap, "exists", False):
                return None
            data = snap.to_dict() or {}
            status = data.get("status")
            return str(status).lower() if status else None
        except Exception:
            return None

    def is_run_finished(self) -> bool:
        """Return True if the run status indicates completion/failure/cancellation.

        This is a convenience predicate for chart scripts to decide when to
        unsubscribe their listeners and exit.
        """
        status = self.get_run_status()
        return status in {"completed", "failed", "cancelled"}


__all__ = [
    "ChartContext",
]


