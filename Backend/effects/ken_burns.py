"""Ken-Burns motion for static images: subtle zoom that turns a still into a
clip the rest of the pipeline can splice in alongside Pexels footage.

Three motions:
- ``zoom_in``  (1.0 → 1.15 over duration; over-scale so frame always fills)
- ``zoom_out`` (1.15 → 1.0)
- ``fit``      (no zoom; entire image visible, padded to viewport — used
                for intro memes / wide infographics where cropping would
                remove load-bearing text)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from moviepy import CompositeVideoClip, ImageClip


_DEFAULT_TARGET_SIZE: Tuple[int, int] = (1080, 1920)
_FIT_BG = (255, 255, 255)


@dataclass
class KenBurnsAsset:
    """A still that should be animated into a video clip via Ken-Burns."""

    image_path: str
    duration: float = 5.0
    motion: str = "zoom_in"  # zoom_in | zoom_out | fit


def _fit_clip(
    image_path: str,
    duration: float,
    target_size: Tuple[int, int],
    fps: int,
) -> CompositeVideoClip:
    target_w, target_h = target_size
    base = ImageClip(image_path).with_duration(duration).with_fps(fps)
    iw, ih = base.size

    fit_factor = min(target_w / iw, target_h / ih)
    new_w = int(round(iw * fit_factor))
    new_h = int(round(ih * fit_factor))

    base = base.resized(new_size=(new_w, new_h)).with_position("center")
    composite = CompositeVideoClip(
        [base], size=(target_w, target_h), bg_color=_FIT_BG
    )
    return composite.with_duration(duration).with_fps(fps)


def image_to_clip(
    image_path: str,
    duration: float,
    *,
    motion: str = "zoom_in",
    target_size: Tuple[int, int] = _DEFAULT_TARGET_SIZE,
    fps: int = 30,
) -> CompositeVideoClip:
    """Return a 9:16 video clip animated from a still."""
    motion = (motion or "zoom_in").lower()

    if motion == "fit":
        return _fit_clip(image_path, duration, target_size, fps)

    target_w, target_h = target_size
    base = ImageClip(image_path).with_duration(duration).with_fps(fps)
    iw, ih = base.size

    # Over-scale so even the smallest-zoom frame covers the viewport, plus
    # a small headroom so the largest-zoom frame doesn't run out of source.
    cover_factor = max(target_w / iw, target_h / ih)
    headroom = 1.20
    scale = cover_factor * headroom

    base = base.resized(new_size=(int(round(iw * scale)), int(round(ih * scale))))

    if motion == "zoom_out":
        zoom_fn = lambda t: 1.15 - 0.15 * (t / max(duration, 1e-6))
    else:
        zoom_fn = lambda t: 1.00 + 0.15 * (t / max(duration, 1e-6))

    animated = base.resized(zoom_fn).with_position("center")

    composite = CompositeVideoClip([animated], size=(target_w, target_h))
    composite = composite.with_duration(duration).with_fps(fps)
    return composite
