from __future__ import annotations

import io
import os
import uuid
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple, Optional

try:
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover
    np = None  # type: ignore

if np is not None:

    class SpillArray(np.ndarray):  # type: ignore[misc]
        """ndarray subclass with list-like truthiness semantics."""

        def __new__(cls, input_array: "np.ndarray", origin_type: Optional[str] = None):
            obj = np.asarray(input_array).view(cls)
            obj._origin_type = origin_type  # type: ignore[attr-defined]
            return obj

        def __array_finalize__(self, obj):
            if obj is None:
                return
            self._origin_type = getattr(obj, "_origin_type", None)

        def __bool__(self) -> bool:  # pragma: no cover - trivial behaviour
            return bool(self.size)

else:  # pragma: no cover - numpy unavailable
    SpillArray = None  # type: ignore

PAYLOAD_REF_KEY = "__mlops_payload_ref__"
PAYLOAD_META_VERSION = 2


def _get_logger() -> logging.Logger:
    return logging.getLogger(__name__)


def _coerce_array(value: Any) -> Optional["np.ndarray"]:
    """Best-effort conversion of supported payloads to a numpy array."""
    if np is None:
        return None
    if isinstance(value, np.ndarray):
        return value
    if hasattr(value, "to_numpy"):
        try:
            arr = value.to_numpy()
            return arr if isinstance(arr, np.ndarray) else None
        except Exception:
            return None
    if isinstance(value, (list, tuple)):
        try:
            arr = np.asarray(value)
            if arr.dtype == object:
                return None
            return arr
        except Exception:
            return None
    return None


def _estimate_bytes(value: Any) -> int:
    if np is not None and isinstance(value, np.ndarray):
        return int(value.nbytes)
    if isinstance(value, (bytes, bytearray)):
        return len(value)
    if isinstance(value, (list, tuple)):
        try:
            if all(isinstance(v, (int, float)) for v in value):
                return len(value) * 8
        except Exception:
            return 0
    return 0


def _should_spill(value: Any, threshold_bytes: int) -> bool:
    arr = _coerce_array(value)
    if arr is None:
        return False
    approx = _estimate_bytes(arr)
    return approx >= threshold_bytes


def _serialize_array(arr: "np.ndarray", origin_type: Optional[str] = None) -> Tuple[bytes, Dict[str, Any]]:
    buf = io.BytesIO()
    np.savez_compressed(buf, data=arr)
    meta = {
        "shape": list(arr.shape),
        "dtype": str(arr.dtype),
        "approx_bytes": int(arr.nbytes),
        "format": "npz",
        "origin_type": origin_type or "ndarray",
    }
    return buf.getvalue(), meta


def _wrap_spilled_array(arr: "np.ndarray", origin_type: Optional[str]) -> Any:
    if origin_type == "list":
        return arr.tolist()
    if origin_type == "tuple":
        return tuple(arr.tolist())
    if np is not None and isinstance(arr, np.ndarray) and SpillArray is not None:
        try:
            wrapped = arr.view(SpillArray)
            wrapped._origin_type = origin_type  # type: ignore[attr-defined]
            return wrapped
        except Exception:
            return arr
    return arr


def _build_payload_filename(run_id: Optional[str], process_name: Optional[str], key_path: Iterable[str]) -> str:
    segments = ["payloads"]
    if run_id:
        segments.append(run_id)
    if process_name:
        segments.append(process_name)
    path_tuple = tuple(key_path)
    if path_tuple:
        path_segment = "-".join(part or "part" for part in path_tuple)
    else:
        path_segment = "data"
    segments.append(path_segment)
    segments.append(str(uuid.uuid4()))
    filename = "/".join(s.strip("/").replace(" ", "_") for s in segments)
    return f"{filename}.npz"


def _store_bytes(state_manager: Any, filename: str, payload: bytes) -> str:
    """Persist bytes via object store when configured, otherwise on the local cache path."""
    if getattr(state_manager, "object_store", None):
        try:
            build_uri = getattr(state_manager, "_build_object_uri", None)
            if callable(build_uri):
                uri = build_uri(filename)
            else:
                uri = state_manager.object_store.build_uri(filename)  # type: ignore[call-arg]
            state_manager.object_store.put_bytes(uri, payload, content_type="application/octet-stream")  # type: ignore[attr-defined]
            return uri
        except Exception as e:
            _get_logger().warning(f"[PayloadSpill] Failed to put bytes to object store ({filename}): {e}")
    cache_dir = getattr(state_manager, "cache_dir", Path("."))
    local_path = Path(cache_dir) / filename
    local_path.parent.mkdir(parents=True, exist_ok=True)
    with open(local_path, "wb") as fout:
        fout.write(payload)
    return str(local_path.resolve())


def spill_large_payloads(result: Dict[str, Any],
                         state_manager: Any,
                         run_id: Optional[str],
                         process_name: Optional[str],
                         threshold_bytes: int = 5_000_000) -> Dict[str, Any]:
    """
    Replace large numeric payloads inside a result dict with lightweight references.
    """
    if not isinstance(result, dict) or state_manager is None or np is None:
        return result

    def _process(key: str, value: Any, path: Tuple[str, ...]) -> Any:
        if isinstance(value, dict):
            return {k: _process(k, v, path + (k,)) for k, v in value.items()}
        if isinstance(value, list):
            if _should_spill(value, threshold_bytes):
                return _spill_value(value, path)
            try:
                return [_process(str(idx), item, path + (str(idx),)) for idx, item in enumerate(value)]
            except Exception:
                pass
        if isinstance(value, tuple):
            if _should_spill(value, threshold_bytes):
                return _spill_value(list(value), path)
            return tuple(_process(str(idx), item, path + (str(idx),)) for idx, item in enumerate(value))
        if _should_spill(value, threshold_bytes):
            return _spill_value(value, path)
        return value

    def _spill_value(payload_value: Any, key_path: Tuple[str, ...]) -> Dict[str, Any]:
        arr = _coerce_array(payload_value)
        if arr is None:
            return payload_value  # type: ignore[return-value]
        if isinstance(payload_value, list):
            origin_type = "list"
        elif isinstance(payload_value, tuple):
            origin_type = "tuple"
        elif np is not None and isinstance(payload_value, np.ndarray):
            origin_type = "ndarray"
        else:
            origin_type = type(payload_value).__name__
        data_bytes, meta = _serialize_array(arr, origin_type=origin_type)
        path_tuple = key_path or ("payload",)
        filename = _build_payload_filename(run_id, process_name, path_tuple)
        uri = _store_bytes(state_manager, filename, data_bytes)
        ref = {
            PAYLOAD_REF_KEY: True,
            "uri": uri,
            "meta": meta,
            "version": PAYLOAD_META_VERSION,
            "key_path": "/".join(path_tuple),
            "process": process_name,
            "run_id": run_id,
        }
        try:
            _get_logger().info(f"[PayloadSpill] Spilled payload for {process_name}:{ref['key_path']} -> {uri} ({meta['approx_bytes']} bytes)")
        except Exception:
            pass
        return ref

    new_result = {}
    for k, v in result.items():
        key = str(k)
        new_result[key] = _process(key, v, (key,))
    return new_result


def hydrate_payload_refs(data: Any, state_manager: Any) -> Any:
    """Replace payload reference dicts with their hydrated numpy arrays."""
    if state_manager is None or np is None:
        return data
    if isinstance(data, dict):
        if data.get(PAYLOAD_REF_KEY):
            return _load_payload(data, state_manager)
        return {k: hydrate_payload_refs(v, state_manager) for k, v in data.items()}
    if isinstance(data, list):
        return [hydrate_payload_refs(v, state_manager) for v in data]
    if isinstance(data, tuple):
        return tuple(hydrate_payload_refs(v, state_manager) for v in data)
    return data


def _load_payload(ref: Dict[str, Any], state_manager: Any) -> Any:
    uri = ref.get("uri")
    if not uri:
        return ref
    try:
        payload_bytes = None
        if str(uri).startswith("gs://") and getattr(state_manager, "object_store", None):
            payload_bytes = state_manager.object_store.get_bytes(uri)  # type: ignore[attr-defined]
        else:
            path = Path(uri)
            if not path.is_absolute() and getattr(state_manager, "cache_dir", None):
                path = Path(state_manager.cache_dir) / path
            with open(path, "rb") as fin:
                payload_bytes = fin.read()
        if payload_bytes is None:
            raise RuntimeError("No payload bytes resolved")
        with np.load(io.BytesIO(payload_bytes), allow_pickle=False) as npz:
            arr = npz["data"]
        meta = ref.get("meta") if isinstance(ref.get("meta"), dict) else {}
        origin_type = meta.get("origin_type") if isinstance(meta, dict) else None
        return _wrap_spilled_array(arr, origin_type)
    except Exception as e:
        _get_logger().warning(f"[PayloadSpill] Failed to hydrate payload {uri}: {e}")
        return ref


if __name__ == "__main__":  # pragma: no cover - developer self-test hook
    logging.basicConfig(level=logging.INFO)
    if np is None:
        print("NumPy is not available; skipping payload spill self-test.")
    else:
        class _TempStateManager:
            def __init__(self) -> None:
                self.cache_dir = Path(os.environ.get("PAYLOAD_SPILL_TMP", "/tmp/payload_spill_test"))
                self.object_store = None

        sm = _TempStateManager()
        sample = {"X_test": np.random.rand(2000, 200)}  # ~3.2 MB -> forces spill
        spilled = spill_large_payloads(sample, sm, run_id="selftest", process_name="demo", threshold_bytes=1_000_000)
        print(spilled)


