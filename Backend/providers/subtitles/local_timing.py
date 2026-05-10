from __future__ import annotations

from typing import Any, List, Optional

from providers.subtitles.base import SubtitlesProvider


def _to_srt_time(total_seconds: float) -> str:
    ms_total = int(round(total_seconds * 1000))
    hours, rem = divmod(ms_total, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    seconds, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"


class LocalTimingProvider(SubtitlesProvider):
    """Sentence-level timing derived from per-sentence audio clip durations.

    Always available — no external service or model. Produces lower-resolution
    timing than transcription-based providers (one SRT entry per sentence).
    """

    name = "local_timing"

    def is_available(self) -> bool:
        return True

    def transcribe(
        self,
        audio_path: str,
        *,
        sentences: List[str],
        audio_clips: List[Any],
        voice: Optional[str] = None,
    ) -> str:
        start_time = 0.0
        entries: List[str] = []
        for i, (sentence, audio_clip) in enumerate(
            zip(sentences, audio_clips), start=1
        ):
            duration = float(audio_clip.duration)
            end_time = start_time + duration
            entries.append(
                f"{i}\n{_to_srt_time(start_time)} --> {_to_srt_time(end_time)}\n{sentence}\n"
            )
            start_time += duration
        return "\n".join(entries)
