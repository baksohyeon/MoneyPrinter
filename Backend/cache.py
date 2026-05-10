"""Persistent disk cache for stock search results and downloaded clips.

Two namespaces:
- ``search/<hash>.json`` — search results with a timestamp; honored only while
  fresher than ``STOCK_CACHE_SEARCH_TTL_DAYS`` (default 7).
- ``clips/<hash>.mp4`` — downloaded video bytes keyed by source URL. No TTL —
  Pexels-style URLs are content-addressed enough that a cache hit means the
  bytes are still good. Manually delete the directory to evict.

Cache root resolution:
  1. ``STOCK_CACHE_DIR`` env var if set (absolute or ~ expanded)
  2. ``platformdirs.user_cache_dir("moneyprinter")``
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
from pathlib import Path
from typing import List, Optional

from platformdirs import user_cache_dir

from providers.stock.base import StockMatch


_DEFAULT_SEARCH_TTL_DAYS = 7


def cache_root() -> Path:
    override = os.getenv("STOCK_CACHE_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path(user_cache_dir("moneyprinter")).resolve()


def _search_dir() -> Path:
    p = cache_root() / "search"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _clips_dir() -> Path:
    p = cache_root() / "clips"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _hash(*parts: str) -> str:
    h = hashlib.sha256()
    for part in parts:
        h.update(str(part).encode("utf-8"))
        h.update(b"\x1f")
    return h.hexdigest()[:32]


def _ttl_seconds() -> float:
    raw = os.getenv("STOCK_CACHE_SEARCH_TTL_DAYS", "").strip()
    try:
        days = float(raw) if raw else _DEFAULT_SEARCH_TTL_DAYS
    except ValueError:
        days = _DEFAULT_SEARCH_TTL_DAYS
    return days * 86400.0


def get_search(
    provider: str, query: str, count: int, min_duration: int
) -> Optional[List[StockMatch]]:
    """Return cached matches if entry exists and is within TTL, else None."""
    key = _hash(provider, query, str(count), str(min_duration))
    path = _search_dir() / f"{key}.json"
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            entry = json.load(f)
    except Exception:
        return None

    age = time.time() - float(entry.get("timestamp") or 0)
    if age > _ttl_seconds():
        return None

    raw_matches = entry.get("matches") or []
    return [StockMatch.from_dict(m) for m in raw_matches]


def set_search(
    provider: str,
    query: str,
    count: int,
    min_duration: int,
    matches: List[StockMatch],
) -> None:
    key = _hash(provider, query, str(count), str(min_duration))
    path = _search_dir() / f"{key}.json"
    tmp = path.with_suffix(".json.tmp")
    payload = {
        "timestamp": time.time(),
        "provider": provider,
        "query": query,
        "count": count,
        "min_duration": min_duration,
        "matches": [m.to_dict() for m in matches],
    }
    try:
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        tmp.replace(path)
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def clip_path_for(url: str) -> Path:
    return _clips_dir() / f"{_hash(url)}.mp4"


def get_clip(url: str) -> Optional[Path]:
    p = clip_path_for(url)
    return p if p.exists() and p.stat().st_size > 0 else None


def store_clip(url: str, src_path: str) -> Path:
    """Move/copy ``src_path`` into the clip cache and return the cached path."""
    dest = clip_path_for(url)
    tmp = dest.with_suffix(".mp4.tmp")
    try:
        shutil.copy2(src_path, tmp)
        tmp.replace(dest)
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise
    return dest


def stats() -> dict:
    """Quick introspection helper for debug endpoints / tests."""
    search = list(_search_dir().glob("*.json"))
    clips = list(_clips_dir().glob("*.mp4"))
    return {
        "root": str(cache_root()),
        "search_entries": len(search),
        "clip_entries": len(clips),
        "clips_total_bytes": sum(p.stat().st_size for p in clips),
    }
