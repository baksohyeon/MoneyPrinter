"""Backward-compat shim. New code should use ``providers.stock`` directly."""

from typing import List

from providers.stock.pexels import PexelsProvider


def search_for_stock_videos(query: str, api_key: str, it: int, min_dur: int) -> List[str]:
    """Legacy URL-list interface, now backed by PexelsProvider."""
    provider = PexelsProvider(api_key=api_key)
    matches = provider.search(query, count=it, min_duration=min_dur)
    return [m.url for m in matches]
