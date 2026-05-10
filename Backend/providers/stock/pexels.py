from __future__ import annotations

import os
from typing import List, Optional

import requests

from logstream import log
from providers.stock.base import StockMatch, StockProvider


class PexelsProvider(StockProvider):
    name = "pexels"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key if api_key is not None else os.getenv("PEXELS_API_KEY", "")

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
                "https://api.pexels.com/videos/search",
                params={"query": query, "per_page": count},
                headers={"Authorization": self._api_key},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            log(f"[-] Pexels search failed for '{query}': {exc}", "warning")
            return []

        matches: List[StockMatch] = []
        for video in data.get("videos") or []:
            duration = float(video.get("duration") or 0)
            best_url = ""
            best_w = 0
            best_h = 0
            best_res = 0
            for f in video.get("video_files") or []:
                link = f.get("link") or ""
                if "/video-files" not in link:
                    continue
                w = int(f.get("width") or 0)
                h = int(f.get("height") or 0)
                res = w * h
                if res > best_res:
                    best_res = res
                    best_url = link
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
        log(f'\t=> "{query}" pexels: {len(kept)} match(es)', "info")
        return kept
