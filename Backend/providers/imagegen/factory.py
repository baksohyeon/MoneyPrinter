from __future__ import annotations

import os
from typing import Optional

from providers.imagegen.base import ImageGenProvider
from providers.imagegen.mflux import MfluxProvider


_REGISTRY = {
    "mflux": MfluxProvider,
}


def _truthy(value: Optional[str]) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def get_imagegen_provider(
    override: Optional[str] = None,
) -> Optional[ImageGenProvider]:
    """Return an enabled imagegen provider, or None if disabled / unavailable.

    Off by default — image generation is heavy (model download + ~30-50s per
    image). Enable explicitly via:
      - IMAGEGEN_ENABLED=true (env)
      - or pass override="mflux" / job payload
    """
    requested = (override or os.getenv("IMAGEGEN_PROVIDER") or "").strip().lower()
    enabled = bool(requested) or _truthy(os.getenv("IMAGEGEN_ENABLED"))
    if not enabled:
        return None

    name = requested or "mflux"
    cls = _REGISTRY.get(name)
    if not cls:
        return None
    instance = cls()
    if not instance.is_available():
        return None
    return instance
