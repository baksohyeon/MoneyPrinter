from __future__ import annotations

from typing import List

from providers.encoder.base import Encoder


class Libx264Encoder(Encoder):
    name = "libx264"

    def available(self) -> bool:
        from utils import probe_ffmpeg_encoder

        return probe_ffmpeg_encoder("libx264")

    def video_codec_args(self, target_bitrate: str, threads: int) -> List[str]:
        return [
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "23",
            "-pix_fmt",
            "yuv420p",
            "-threads",
            str(max(1, int(threads or 2))),
        ]
