from __future__ import annotations

import os
from typing import List, Optional

import requests

from logstream import log
from providers.stock.base import StockMatch, StockProvider


class PixabayProvider(StockProvider):
    name = "pixabay"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key if api_key is not None else os.getenv("PIXABAY_API_KEY", "")

    def is_enabled(self) -> bool:
        return bool(self._api_key)

    def search(
        self,
        query: str,
        *,
        count: int = 15,
        min_duration: int = 3,
    ) -> List[StockMatch]:
        if not self.is_enabled():
            return []

        try:
            response = requests.get(
                "https://pixabay.com/api/videos/",
                params={
                    "key": self._api_key,
                    "q": query,
                    "per_page": min(max(count, 3), 200),
                    "safesearch": "true",
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            log(f"[-] Pixabay search failed for '{query}': {exc}", "warning")
            return []

        matches: List[StockMatch] = []
        for hit in data.get("hits") or []:
            duration = float(hit.get("duration") or 0)
            videos = hit.get("videos") or {}
            best_url = ""
            best_w = 0
            best_h = 0
            best_res = 0
            for size_key in ("large", "medium", "small", "tiny"):
                v = videos.get(size_key) or {}
                url = v.get("url") or ""
                if not url:
                    continue
                w = int(v.get("width") or 0)
                h = int(v.get("height") or 0)
                res = w * h
                if res > best_res:
                    best_res = res
                    best_url = url
                    best_w = w
                    best_h = h
            if best_url:
                matches.append(
                    StockMatch(
                        url=best_url,
                        duration=duration,
                        width=best_w,
                        height=best_h,
                        source=self.name,
                    )
                )

        kept = self._filter_and_sort(matches, min_duration)
        log(f'\t=> "{query}" pixabay: {len(kept)} match(es)', "info")
        return kept
