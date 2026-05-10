from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class StockMatch:
    """A single video match returned by a stock provider."""

    url: str
    duration: float
    width: int
    height: int
    source: str

    @property
    def resolution(self) -> int:
        return int(self.width) * int(self.height)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "StockMatch":
        return cls(
            url=d["url"],
            duration=float(d.get("duration") or 0),
            width=int(d.get("width") or 0),
            height=int(d.get("height") or 0),
            source=str(d.get("source") or "unknown"),
        )


class StockProvider(ABC):
    """A stock-video search source. Each provider is gated on its API key."""

    name: str = "base"

    @abstractmethod
    def is_enabled(self) -> bool: ...

    @abstractmethod
    def search(
        self,
        query: str,
        *,
        count: int = 15,
        min_duration: int = 3,
    ) -> List[StockMatch]: ...

    def _filter_and_sort(
        self, matches: List[StockMatch], min_duration: int
    ) -> List[StockMatch]:
        kept = [m for m in matches if m.duration >= min_duration]
        kept.sort(key=lambda m: m.resolution, reverse=True)
        return kept
