from __future__ import annotations

import base64


def encode_probe_path(probe_path: str) -> str:
    """Encode a logical probe_path into a Firestore/Redis-safe identifier.

    Uses URL-safe base64 without padding and a small prefix to avoid pure-numeric IDs.
    """
    raw = str(probe_path).encode("utf-8")
    enc = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    return f"p_{enc}"


def decode_probe_path(encoded_id: str) -> str:
    """Decode an encoded probe_path identifier back to the logical path.

    Raises ValueError if the identifier cannot be decoded.
    """
    payload = str(encoded_id)
    if payload.startswith("p_"):
        payload = payload[2:]
    # Restore base64 padding
    pad = "=" * (-len(payload) % 4)
    try:
        raw = base64.urlsafe_b64decode(payload + pad)
        return raw.decode("utf-8")
    except Exception as e:
        raise ValueError(f"Invalid encoded probe path id: {encoded_id}") from e


__all__ = [
    "encode_probe_path",
    "decode_probe_path",
]


