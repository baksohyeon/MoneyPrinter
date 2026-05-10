from __future__ import annotations

import os
from typing import Any, List, Optional

from providers.subtitles.base import SubtitlesProvider


_LANGUAGE_MAPPING = {
    "br": "pt",
    "id": "en",  # AssemblyAI doesn't have Indonesian
    "jp": "ja",
    "kr": "ko",
}


class AssemblyAIProvider(SubtitlesProvider):
    """Cloud STT via AssemblyAI. Requires ASSEMBLY_AI_API_KEY."""

    name = "assemblyai"

    def is_available(self) -> bool:
        if not (os.getenv("ASSEMBLY_AI_API_KEY") or "").strip():
            return False
        try:
            import assemblyai  # noqa: F401
            return True
        except ImportError:
            return False

    def transcribe(
        self,
        audio_path: str,
        *,
        sentences: List[str],
        audio_clips: List[Any],
        voice: Optional[str] = None,
    ) -> str:
        import assemblyai as aai

        lang_code = _LANGUAGE_MAPPING.get(voice or "", voice or "en")
        aai.settings.api_key = os.getenv("ASSEMBLY_AI_API_KEY", "")
        # API requires the plural `speech_models` list with current model names.
        speech_model = os.getenv("ASSEMBLY_AI_SPEECH_MODEL", "universal-2")
        config = aai.TranscriptionConfig(
            language_code=lang_code,
            speech_models=[speech_model],
        )
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(audio_path)
        return transcript.export_subtitles_srt()
