from __future__ import annotations

import os
from typing import Optional

from providers.subtitles.assemblyai import AssemblyAIProvider
from providers.subtitles.base import SubtitlesProvider
from providers.subtitles.local_timing import LocalTimingProvider
from providers.subtitles.mlx_whisper import MlxWhisperProvider


_REGISTRY = {
    "assemblyai": AssemblyAIProvider,
    "mlx_whisper": MlxWhisperProvider,
    "local": LocalTimingProvider,
    "local_timing": LocalTimingProvider,
}


def get_subtitles_provider(override: Optional[str] = None) -> SubtitlesProvider:
    """Pick a subtitles provider by override → env → auto-priority.

    Auto-priority (no explicit override):
      1. AssemblyAI if its key is present (preserves existing user setups)
      2. mlx-whisper if Mac fast-path is available
      3. Local sentence-level timing (always available)
    """
    requested = (override or os.getenv("SUBTITLES_PROVIDER") or "").strip().lower()

    if requested:
        cls = _REGISTRY.get(requested)
        if cls:
            instance = cls()
            if instance.is_available():
                return instance

    aai = AssemblyAIProvider()
    if aai.is_available():
        return aai

    mlx = MlxWhisperProvider()
    if mlx.is_available():
        return mlx

    return LocalTimingProvider()
