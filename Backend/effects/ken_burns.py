"""Ken-Burns motion for static images: subtle zoom that turns a still into a
clip the rest of the pipeline can splice in alongside Pexels footage.

Two motions for now: ``zoom_in`` (1.0 → 1.15 over the duration) and
``zoom_out`` (1.15 → 1.0). Pan variants can land later if the user asks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from moviepy import CompositeVideoClip, ImageClip


_DEFAULT_TARGET_SIZE: Tuple[int, int] = (1080, 1920)


@dataclass
class KenBurnsAsset:
    """A still that should be animated into a video clip via Ken-Burns."""

    image_path: str
    duration: float = 5.0
    motion: str = "zoom_in"  # zoom_in | zoom_out


def image_to_clip(
    image_path: str,
    duration: float,
    *,
    motion: str = "zoom_in",
    target_size: Tuple[int, int] = _DEFAULT_TARGET_SIZE,
    fps: int = 30,
) -> CompositeVideoClip:
    """Return a 9:16 video clip animated from a still.

    The image is first scaled so that even the most-zoomed frame fully covers
    the target size (no black borders mid-animation), then a time-varying
    resize lambda drives the Ken-Burns motion. Output is centered in the
    target viewport via CompositeVideoClip.
    """
    target_w, target_h = target_size
    base = ImageClip(image_path).with_duration(duration).with_fps(fps)
    iw, ih = base.size

    # Scale so that even the smallest-zoom frame still covers the viewport,
    # plus a small headroom so the largest-zoom frame doesn't run out of
    # source pixels.
    cover_factor = max(target_w / iw, target_h / ih)
    headroom = 1.20  # 20% extra so 1.15× zoom never under-fills
    scale = cover_factor * headroom

    base = base.resized(new_size=(int(round(iw * scale)), int(round(ih * scale))))

    motion = (motion or "zoom_in").lower()
    if motion == "zoom_out":
        zoom_fn = lambda t: 1.15 - 0.15 * (t / max(duration, 1e-6))
    else:
        zoom_fn = lambda t: 1.00 + 0.15 * (t / max(duration, 1e-6))

    animated = base.resized(zoom_fn).with_position("center")

    composite = CompositeVideoClip([animated], size=(target_w, target_h))
    composite = composite.with_duration(duration).with_fps(fps)
    return composite
