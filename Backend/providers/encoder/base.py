from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SubtitleStyle:
    font_name: str = "Bold"
    font_size: int = 22
    primary_color: str = "&H0000FFFF&"
    outline_color: str = "&H00000000&"
    outline: int = 4
    alignment: int = 2
    margin_v: int = 80


_ALIGNMENT_MAP = {
    ("left", "bottom"): 1,
    ("center", "bottom"): 2,
    ("right", "bottom"): 3,
    ("left", "center"): 4,
    ("center", "center"): 5,
    ("right", "center"): 6,
    ("left", "top"): 7,
    ("center", "top"): 8,
    ("right", "top"): 9,
}


def hex_to_ass_color(hex_color: str) -> str:
    """Convert '#RRGGBB' (web) to '&H00BBGGRR&' (libass alpha+BGR, alpha=00)."""
    s = (hex_color or "").strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        return "&H0000FFFF&"
    try:
        int(s, 16)
    except ValueError:
        return "&H0000FFFF&"
    r, g, b = s[0:2], s[2:4], s[4:6]
    return f"&H00{b}{g}{r}&".upper()


def parse_subtitle_position(position: Optional[str]) -> int:
    """Map MoneyPrinter's 'horiz,vert' string to libass Alignment numpad (1-9)."""
    if not position:
        return 2
    parts = [p.strip().lower() for p in position.split(",")]
    if len(parts) != 2:
        return 2
    horiz, vert = parts[0], parts[1]
    return _ALIGNMENT_MAP.get((horiz, vert), 2)


def _safe_filter_path(path: str) -> str:
    """Reject paths containing chars that break ffmpeg's filter parser.

    The subtitles/fontsdir filter arguments are split on ':' and ','. Paths used
    by MoneyPrinter (UUID-named files in TEMP_DIR / SUBTITLES_DIR / FONTS_DIR)
    never contain these on macOS/Linux, so we fail loud rather than silently
    producing a broken filter graph.
    """
    if any(c in path for c in (":", ",", "'", "[", "]")):
        raise ValueError(
            f"Path contains characters that need escaping in ffmpeg filters: {path!r}"
        )
    return path


def build_subtitles_filter(
    srt_path: str, fonts_dir: str, style: SubtitleStyle
) -> str:
    style_parts = [
        f"Fontname={style.font_name}",
        f"Fontsize={style.font_size}",
        f"PrimaryColour={style.primary_color}",
        f"OutlineColour={style.outline_color}",
        "BorderStyle=1",
        f"Outline={style.outline}",
        "Shadow=0",
        f"Alignment={style.alignment}",
        f"MarginV={style.margin_v}",
    ]
    style_str = ",".join(style_parts)
    return (
        f"subtitles={_safe_filter_path(srt_path)}"
        f":fontsdir={_safe_filter_path(fonts_dir)}"
        f":force_style='{style_str}'"
    )


class Encoder(ABC):
    """Builds ffmpeg codec arguments for the chosen video/audio encoder."""

    name: str = "base"

    @abstractmethod
    def available(self) -> bool: ...

    @abstractmethod
    def video_codec_args(self, target_bitrate: str, threads: int) -> List[str]: ...

    def audio_codec_args(self, bitrate: str = "192k") -> List[str]:
        return ["-c:a", "aac", "-b:a", bitrate]
