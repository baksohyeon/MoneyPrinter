import time
from pathlib import Path

import cache
from providers.stock.base import StockMatch


def test_cache_root_uses_override(tmp_path, monkeypatch):
    monkeypatch.setenv("STOCK_CACHE_DIR", str(tmp_path))
    assert cache.cache_root() == tmp_path.resolve()


def test_search_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("STOCK_CACHE_DIR", str(tmp_path))
    matches = [
        StockMatch("https://example.com/a.mp4", 6.0, 1920, 1080, "pexels"),
        StockMatch("https://example.com/b.mp4", 4.0, 1280, 720, "pexels"),
    ]
    cache.set_search("pexels", "ocean", 15, 3, matches)

    got = cache.get_search("pexels", "ocean", 15, 3)
    assert got == matches


def test_search_returns_none_when_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("STOCK_CACHE_DIR", str(tmp_path))
    assert cache.get_search("pexels", "nope", 15, 3) is None


def test_search_expires_after_ttl(tmp_path, monkeypatch):
    monkeypatch.setenv("STOCK_CACHE_DIR", str(tmp_path))
    monkeypatch.setenv("STOCK_CACHE_SEARCH_TTL_DAYS", "0")  # everything stale
    cache.set_search(
        "pexels",
        "x",
        15,
        3,
        [StockMatch("https://example.com/a.mp4", 6.0, 1920, 1080, "pexels")],
    )
    assert cache.get_search("pexels", "x", 15, 3) is None


def test_search_keys_are_distinct(tmp_path, monkeypatch):
    monkeypatch.setenv("STOCK_CACHE_DIR", str(tmp_path))
    a = [StockMatch("https://a", 5.0, 1, 1, "pexels")]
    b = [StockMatch("https://b", 5.0, 1, 1, "pexels")]
    cache.set_search("pexels", "term", 15, 3, a)
    cache.set_search("pixabay", "term", 15, 3, b)
    assert cache.get_search("pexels", "term", 15, 3) == a
    assert cache.get_search("pixabay", "term", 15, 3) == b


def test_clip_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("STOCK_CACHE_DIR", str(tmp_path))
    src = tmp_path / "scratch.mp4"
    src.write_bytes(b"fake mp4 bytes")
    url = "https://example.com/clip.mp4"

    assert cache.get_clip(url) is None
    stored = cache.store_clip(url, str(src))
    assert stored.exists()
    assert stored.read_bytes() == b"fake mp4 bytes"

    again = cache.get_clip(url)
    assert again is not None
    assert again == stored


def test_clip_ignores_zero_byte_files(tmp_path, monkeypatch):
    monkeypatch.setenv("STOCK_CACHE_DIR", str(tmp_path))
    p = cache.clip_path_for("https://x")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"")
    assert cache.get_clip("https://x") is None


def test_stats_reports_counts(tmp_path, monkeypatch):
    monkeypatch.setenv("STOCK_CACHE_DIR", str(tmp_path))
    cache.set_search(
        "pexels", "q", 15, 3, [StockMatch("https://a", 5.0, 1, 1, "pexels")]
    )
    src = tmp_path / "s.mp4"
    src.write_bytes(b"x" * 1000)
    cache.store_clip("https://a", str(src))

    stats = cache.stats()
    assert stats["search_entries"] == 1
    assert stats["clip_entries"] == 1
    assert stats["clips_total_bytes"] == 1000
