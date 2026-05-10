from typing import List
from unittest.mock import MagicMock, patch

import pytest

from providers.stock.base import StockMatch, StockProvider
from providers.stock.coverr import CoverrProvider
from providers.stock.factory import _CachedStockProvider, get_stock_providers
from providers.stock.pexels import PexelsProvider
from providers.stock.pixabay import PixabayProvider


def test_stock_match_round_trip_dict():
    m = StockMatch("https://x", 5.0, 1080, 1920, "pexels")
    assert StockMatch.from_dict(m.to_dict()) == m


def test_pexels_disabled_without_api_key():
    assert PexelsProvider(api_key="").is_enabled() is False
    assert PexelsProvider(api_key="real-key").is_enabled() is True


def test_pixabay_disabled_without_api_key():
    assert PixabayProvider(api_key="").is_enabled() is False
    assert PixabayProvider(api_key="real-key").is_enabled() is True


def test_coverr_disabled_without_api_key():
    assert CoverrProvider(api_key="").is_enabled() is False
    assert CoverrProvider(api_key="real-key").is_enabled() is True


def test_pexels_returns_empty_when_disabled():
    assert PexelsProvider(api_key="").search("x") == []


def _fake_pexels_response():
    return {
        "videos": [
            {
                "duration": 6,
                "video_files": [
                    {
                        "link": "https://www.pexels.com/video-files/abc/720p.mp4",
                        "width": 1280,
                        "height": 720,
                    },
                    {
                        "link": "https://www.pexels.com/video-files/abc/1080p.mp4",
                        "width": 1920,
                        "height": 1080,
                    },
                ],
            },
            {  # below min_duration
                "duration": 2,
                "video_files": [
                    {
                        "link": "https://www.pexels.com/video-files/short/720p.mp4",
                        "width": 1280,
                        "height": 720,
                    }
                ],
            },
        ]
    }


def test_pexels_picks_highest_resolution_and_filters_short_clips():
    p = PexelsProvider(api_key="key")
    with patch("providers.stock.pexels.requests.get") as get:
        get.return_value.json.return_value = _fake_pexels_response()
        get.return_value.raise_for_status.return_value = None
        matches = p.search("ocean", count=15, min_duration=3)
    assert len(matches) == 1
    m = matches[0]
    assert m.url.endswith("1080p.mp4")
    assert m.width == 1920 and m.height == 1080
    assert m.source == "pexels"


def test_pixabay_picks_largest_size_variant():
    p = PixabayProvider(api_key="key")
    payload = {
        "hits": [
            {
                "duration": 5,
                "videos": {
                    "tiny": {"url": "https://t/u.mp4", "width": 320, "height": 180},
                    "large": {"url": "https://l/u.mp4", "width": 1920, "height": 1080},
                    "medium": {"url": "https://m/u.mp4", "width": 1280, "height": 720},
                },
            }
        ]
    }
    with patch("providers.stock.pixabay.requests.get") as get:
        get.return_value.json.return_value = payload
        get.return_value.raise_for_status.return_value = None
        matches = p.search("forest")
    assert len(matches) == 1
    assert matches[0].url == "https://l/u.mp4"
    assert matches[0].source == "pixabay"


def test_coverr_uses_mp4_url_field():
    p = CoverrProvider(api_key="key")
    payload = {
        "hits": [
            {
                "duration": 4,
                "max_width": 1920,
                "max_height": 1080,
                "urls": {"mp4": "https://c/u.mp4", "mp4_preview": "https://c/p.mp4"},
            },
            {  # missing url, should be skipped
                "duration": 7,
                "urls": {},
            },
        ]
    }
    with patch("providers.stock.coverr.requests.get") as get:
        get.return_value.json.return_value = payload
        get.return_value.raise_for_status.return_value = None
        matches = p.search("city")
    assert len(matches) == 1
    assert matches[0].url == "https://c/u.mp4"


def test_factory_returns_only_enabled(monkeypatch):
    monkeypatch.setenv("STOCK_SOURCES", "pexels,pixabay,coverr")
    monkeypatch.setenv("PEXELS_API_KEY", "p")
    monkeypatch.setenv("PIXABAY_API_KEY", "")
    monkeypatch.setenv("COVERR_API_KEY", "c")
    providers = get_stock_providers()
    names = [p.name for p in providers]
    assert names == ["pexels", "coverr"]


def test_factory_respects_priority_order(monkeypatch):
    monkeypatch.setenv("STOCK_SOURCES", "pixabay,pexels")
    monkeypatch.setenv("PEXELS_API_KEY", "p")
    monkeypatch.setenv("PIXABAY_API_KEY", "x")
    providers = get_stock_providers()
    assert [p.name for p in providers] == ["pixabay", "pexels"]


def test_factory_returns_empty_when_no_keys(monkeypatch):
    monkeypatch.delenv("PEXELS_API_KEY", raising=False)
    monkeypatch.delenv("PIXABAY_API_KEY", raising=False)
    monkeypatch.delenv("COVERR_API_KEY", raising=False)
    monkeypatch.delenv("STOCK_SOURCES", raising=False)
    assert get_stock_providers() == []


class _StubProvider(StockProvider):
    name = "stub"
    call_count = 0

    def __init__(self) -> None:
        self.call_count = 0

    def is_enabled(self) -> bool:
        return True

    def search(
        self, query: str, *, count: int = 15, min_duration: int = 3
    ) -> List[StockMatch]:
        self.call_count += 1
        return [StockMatch("https://stub/x.mp4", 5.0, 1080, 1920, self.name)]


def test_cached_provider_short_circuits_inner(tmp_path, monkeypatch):
    monkeypatch.setenv("STOCK_CACHE_DIR", str(tmp_path))
    inner = _StubProvider()
    cached = _CachedStockProvider(inner)

    first = cached.search("water", count=5, min_duration=3)
    second = cached.search("water", count=5, min_duration=3)

    assert first == second
    assert inner.call_count == 1, "second call should hit the disk cache"
