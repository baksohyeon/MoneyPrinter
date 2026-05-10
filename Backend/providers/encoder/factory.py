from __future__ import annotations

import os
from typing import Optional

from providers.encoder.base import Encoder
from providers.encoder.libx264 import Libx264Encoder
from providers.encoder.videotoolbox import VideoToolboxEncoder


def get_encoder(override: Optional[str] = None) -> Encoder:
    """Resolve an encoder by job override → env var → mac auto-detect → libx264.

    A requested provider that turns out to be unavailable falls back to libx264
    rather than raising — keeps single-machine behavior predictable.
    """
    requested = (override or os.getenv("ENCODER_PROVIDER", "")).strip().lower()
    libx264 = Libx264Encoder()
    videotoolbox = VideoToolboxEncoder()

    if requested == "videotoolbox":
        return videotoolbox if videotoolbox.available() else libx264
    if requested == "libx264":
        return libx264

    if videotoolbox.available():
        return videotoolbox
    return libx264
