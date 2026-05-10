from __future__ import annotations

import os
from typing import List, Optional

import requests

from logstream import log
from providers.stock.base import StockMatch, StockProvider


class CoverrProvider(StockProvider):
    name = "coverr"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key if api_key is not None else os.getenv("COVERR_API_KEY", "")

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
                "https://api.coverr.co/videos",
                params={
                    "query": query,
                    "page_size": min(max(count, 3), 50),
                    "urls": "true",
                },
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            log(f"[-] Coverr search failed for '{query}': {exc}", "warning")
            return []

        matches: List[StockMatch] = []
        for hit in data.get("hits") or []:
            duration = float(hit.get("duration") or 0)
            urls = hit.get("urls") or {}
            url = urls.get("mp4_download") or urls.get("mp4") or ""
            if not url:
                continue
            matches.append(
                StockMatch(
                    url=url,
                    duration=duration,
                    width=int(hit.get("max_width") or 0),
                    height=int(hit.get("max_height") or 0),
                    source=self.name,
                )
            )

        kept = self._filter_and_sort(matches, min_duration)
        log(f'\t=> "{query}" coverr: {len(kept)} match(es)', "info")
        return kept
