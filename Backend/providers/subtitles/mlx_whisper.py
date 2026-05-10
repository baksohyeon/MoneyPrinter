from __future__ import annotations

import os
from typing import Any, List, Optional

from providers.subtitles.base import SubtitlesProvider


_VOICE_TO_LANG = {
    "br": "pt",
    "id": "en",
    "jp": "ja",
    "kr": "ko",
    "en": "en",
}

_DEFAULT_MODEL = "mlx-community/whisper-tiny"


def _seconds_to_srt(t: float) -> str:
    ms_total = int(round(t * 1000))
    hours, rem = divmod(ms_total, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    seconds, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"


class MlxWhisperProvider(SubtitlesProvider):
    """Local Whisper inference via Apple's MLX. Mac M-series only."""

    name = "mlx_whisper"

    def is_available(self) -> bool:
        from utils import is_mac_fast_path_available

        if not is_mac_fast_path_available():
            return False
        try:
            import mlx_whisper  # noqa: F401
            return True
        except ImportError:
            return False

    def _resolve_model(self) -> str:
        raw = (os.getenv("MLX_WHISPER_MODEL") or "").strip()
        if not raw:
            return _DEFAULT_MODEL
        # Accept either a full HF repo or a short alias like "tiny" / "base".
        if "/" in raw:
            return raw
        return f"mlx-community/whisper-{raw}"

    def transcribe(
        self,
        audio_path: str,
        *,
        sentences: List[str],
        audio_clips: List[Any],
        voice: Optional[str] = None,
    ) -> str:
        import mlx_whisper

        language = _VOICE_TO_LANG.get((voice or "").strip().lower())
        kwargs = {"path_or_hf_repo": self._resolve_model()}
        if language:
            kwargs["language"] = language

        result = mlx_whisper.transcribe(audio_path, **kwargs)

        segments = result.get("segments") or []
        if not segments:
            # Fallback: emit the full text as one entry over the audio length.
            text = (result.get("text") or "").strip()
            if not text:
                return ""
            audio_dur = sum(
                float(getattr(c, "duration", 0) or 0) for c in audio_clips
            )
            return (
                f"1\n{_seconds_to_srt(0)} --> "
                f"{_seconds_to_srt(max(audio_dur, 1.0))}\n{text}\n"
            )

        entries: List[str] = []
        for i, seg in enumerate(segments, start=1):
            start = float(seg.get("start") or 0)
            end = float(seg.get("end") or start)
            text = (seg.get("text") or "").strip()
            if not text:
                continue
            entries.append(
                f"{i}\n{_seconds_to_srt(start)} --> {_seconds_to_srt(end)}\n{text}\n"
            )
        return "\n".join(entries)
