from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class SubtitlesProvider(ABC):
    """Produces an SRT string from a TTS audio file.

    `sentences` and `audio_clips` are passed through for providers that derive
    timing from the input narration (the local-timing fallback). Network /
    on-device transcribers ignore them.
    """

    name: str = "base"

    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    def transcribe(
        self,
        audio_path: str,
        *,
        sentences: List[str],
        audio_clips: List[Any],
        voice: Optional[str] = None,
    ) -> str: ...
