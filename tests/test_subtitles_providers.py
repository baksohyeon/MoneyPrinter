from types import SimpleNamespace
from unittest.mock import patch

import pytest

from providers.subtitles.assemblyai import AssemblyAIProvider
from providers.subtitles.factory import get_subtitles_provider
from providers.subtitles.local_timing import LocalTimingProvider, _to_srt_time
from providers.subtitles.mlx_whisper import MlxWhisperProvider


def _clip(duration: float):
    return SimpleNamespace(duration=duration)


def test_to_srt_time_format():
    assert _to_srt_time(0) == "00:00:00,000"
    assert _to_srt_time(1.5) == "00:00:01,500"
    assert _to_srt_time(61.0) == "00:01:01,000"
    assert _to_srt_time(3661.123) == "01:01:01,123"


def test_local_timing_always_available():
    assert LocalTimingProvider().is_available() is True


def test_local_timing_emits_sentence_per_clip():
    sentences = ["Hello world", "Fast path is alive"]
    clips = [_clip(1.5), _clip(2.0)]

    srt = LocalTimingProvider().transcribe(
        "audio.mp3", sentences=sentences, audio_clips=clips, voice="en"
    )

    assert "Hello world" in srt
    assert "Fast path is alive" in srt
    assert "00:00:00,000 --> 00:00:01,500" in srt
    assert "00:00:01,500 --> 00:00:03,500" in srt


def test_assemblyai_disabled_without_key(monkeypatch):
    monkeypatch.delenv("ASSEMBLY_AI_API_KEY", raising=False)
    assert AssemblyAIProvider().is_available() is False


def test_assemblyai_enabled_with_key(monkeypatch):
    monkeypatch.setenv("ASSEMBLY_AI_API_KEY", "fake-key")
    assert AssemblyAIProvider().is_available() is True


def test_mlx_whisper_disabled_off_apple_silicon(monkeypatch):
    monkeypatch.setattr(
        "providers.subtitles.mlx_whisper.__name__",
        "providers.subtitles.mlx_whisper",
    )
    with patch("utils.is_mac_fast_path_available", return_value=False):
        assert MlxWhisperProvider().is_available() is False


def test_mlx_whisper_resolve_model_short_alias(monkeypatch):
    monkeypatch.setenv("MLX_WHISPER_MODEL", "base")
    p = MlxWhisperProvider()
    assert p._resolve_model() == "mlx-community/whisper-base"


def test_mlx_whisper_resolve_model_full_repo(monkeypatch):
    monkeypatch.setenv("MLX_WHISPER_MODEL", "openai/whisper-large-v3")
    p = MlxWhisperProvider()
    assert p._resolve_model() == "openai/whisper-large-v3"


def test_mlx_whisper_resolve_model_default(monkeypatch):
    monkeypatch.delenv("MLX_WHISPER_MODEL", raising=False)
    p = MlxWhisperProvider()
    assert p._resolve_model() == "mlx-community/whisper-tiny"


def test_factory_assemblyai_wins_when_key_present(monkeypatch):
    monkeypatch.setenv("ASSEMBLY_AI_API_KEY", "fake")
    monkeypatch.delenv("SUBTITLES_PROVIDER", raising=False)
    monkeypatch.setattr(MlxWhisperProvider, "is_available", lambda self: True)
    monkeypatch.setattr(AssemblyAIProvider, "is_available", lambda self: True)
    provider = get_subtitles_provider()
    assert provider.name == "assemblyai"


def test_factory_falls_back_to_mlx_whisper(monkeypatch):
    monkeypatch.delenv("ASSEMBLY_AI_API_KEY", raising=False)
    monkeypatch.delenv("SUBTITLES_PROVIDER", raising=False)
    monkeypatch.setattr(AssemblyAIProvider, "is_available", lambda self: False)
    monkeypatch.setattr(MlxWhisperProvider, "is_available", lambda self: True)
    provider = get_subtitles_provider()
    assert provider.name == "mlx_whisper"


def test_factory_falls_back_to_local(monkeypatch):
    monkeypatch.delenv("ASSEMBLY_AI_API_KEY", raising=False)
    monkeypatch.delenv("SUBTITLES_PROVIDER", raising=False)
    monkeypatch.setattr(AssemblyAIProvider, "is_available", lambda self: False)
    monkeypatch.setattr(MlxWhisperProvider, "is_available", lambda self: False)
    provider = get_subtitles_provider()
    assert provider.name == "local_timing"


def test_factory_explicit_override_local(monkeypatch):
    monkeypatch.setenv("ASSEMBLY_AI_API_KEY", "fake")
    monkeypatch.setenv("SUBTITLES_PROVIDER", "local")
    provider = get_subtitles_provider()
    assert provider.name == "local_timing"


def test_factory_override_falls_through_when_unavailable(monkeypatch):
    """If SUBTITLES_PROVIDER asks for mlx_whisper but it's unavailable,
    the factory continues to the auto-priority chain (not silently picks
    something different from what was requested)."""
    monkeypatch.setenv("SUBTITLES_PROVIDER", "mlx_whisper")
    monkeypatch.setenv("ASSEMBLY_AI_API_KEY", "fake")
    monkeypatch.setattr(MlxWhisperProvider, "is_available", lambda self: False)
    monkeypatch.setattr(AssemblyAIProvider, "is_available", lambda self: True)
    provider = get_subtitles_provider()
    assert provider.name == "assemblyai"
