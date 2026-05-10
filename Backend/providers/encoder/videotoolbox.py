from __future__ import annotations

from typing import List

from providers.encoder.base import Encoder


class VideoToolboxEncoder(Encoder):
    name = "videotoolbox"

    def available(self) -> bool:
        from utils import is_mac_fast_path_available, probe_ffmpeg_encoder

        return is_mac_fast_path_available() and probe_ffmpeg_encoder(
            "h264_videotoolbox"
        )

    def video_codec_args(self, target_bitrate: str, threads: int) -> List[str]:
        return [
            "-c:v",
            "h264_videotoolbox",
            "-b:v",
            target_bitrate or "8M",
            "-tag:v",
            "avc1",
            "-pix_fmt",
            "yuv420p",
        ]
