"""Storage backend implementations.

Adapters may have optional third-party dependencies (e.g. `redis`, `google-cloud-*`)
and are intended to be imported/constructed only when that backend is selected.
"""

from __future__ import annotations


