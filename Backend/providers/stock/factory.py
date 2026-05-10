from __future__ import annotations

import os
from typing import List

from providers.stock.base import StockMatch, StockProvider
from providers.stock.coverr import CoverrProvider
from providers.stock.pexels import PexelsProvider
from providers.stock.pixabay import PixabayProvider

_REGISTRY = {
    "pexels": PexelsProvider,
    "pixabay": PixabayProvider,
    "coverr": CoverrProvider,
}


class _CachedStockProvider(StockProvider):
    """Decorator that consults Backend/cache.py before hitting the network."""

    def __init__(self, inner: StockProvider) -> None:
        self._inner = inner
        self.name = inner.name

    def is_enabled(self) -> bool:
        return self._inner.is_enabled()

    def search(
        self,
        query: str,
        *,
        count: int = 15,
        min_duration: int = 3,
    ) -> List[StockMatch]:
        from cache import get_search, set_search

        cached = get_search(self.name, query, count, min_duration)
        if cached is not None:
            return cached
        matches = self._inner.search(
            query, count=count, min_duration=min_duration
        )
        if matches:
            set_search(self.name, query, count, min_duration, matches)
        return matches


def get_stock_providers() -> List[StockProvider]:
    """Return the enabled stock providers in priority order, wrapped in cache.

    Priority is the order in STOCK_SOURCES (comma-separated). If empty, all
    known providers are tried — providers without an API key disable
    themselves via is_enabled() and are filtered out.
    """
    raw = (os.getenv("STOCK_SOURCES") or "").strip()
    if raw:
        names = [n.strip().lower() for n in raw.split(",") if n.strip()]
    else:
        names = list(_REGISTRY.keys())

    providers: List[StockProvider] = []
    for name in names:
        cls = _REGISTRY.get(name)
        if not cls:
            continue
        instance = cls()
        if instance.is_enabled():
            providers.append(_CachedStockProvider(instance))
    return providers
