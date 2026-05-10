import os
import subprocess
import uuid

import requests
import srt_equalizer

from typing import List, Optional
from pathlib import Path
from moviepy import (
    AudioFileClip,
    VideoFileClip,
    concatenate_videoclips,
)
from dotenv import load_dotenv
from logstream import log
from utils import ENV_FILE, TEMP_DIR, SUBTITLES_DIR, FONTS_DIR, get_ffmpeg_path

load_dotenv(ENV_FILE)

FRAME_EPSILON = 1 / 120


def save_video(video_url: str, directory: str = str(TEMP_DIR)) -> str:
    """Saves a video from a URL and returns its on-disk path.

    Cache-aware: if the URL is already in the clip cache (Backend/cache.py),
    return that cached path directly — moviepy reads it the same as a fresh
    download. On a cache miss, download to a TEMP_DIR scratch file, then
    promote into the cache and return the cache path.
    """
    from cache import get_clip, store_clip

    cached = get_clip(video_url)
    if cached is not None:
        log(f"[+] Cache hit: {video_url[:80]}...", "info")
        return str(cached)

    destination = Path(directory).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    video_id = uuid.uuid4()
    scratch_path = destination / f"{video_id}.mp4"
    with open(scratch_path, "wb") as f:
        f.write(requests.get(video_url, timeout=60).content)

    try:
        cached_path = store_clip(video_url, str(scratch_path))
        scratch_path.unlink(missing_ok=True)
        return str(cached_path)
    except Exception as exc:
        log(f"[-] Could not promote download to cache: {exc}", "warning")
        return str(scratch_path)


def generate_subtitles(
    audio_path: str,
    sentences: List[str],
    audio_clips: List[AudioFileClip],
    voice: str,
    *,
    provider_override: Optional[str] = None,
) -> str:
    """Resolve a SubtitlesProvider via factory and write its SRT to disk.

    Selection priority (no override):
      1. AssemblyAI if ASSEMBLY_AI_API_KEY is set (preserves prior behavior)
      2. mlx-whisper if Mac fast-path + package available
      3. Local sentence-level timing fallback
    Override via SUBTITLES_PROVIDER env or the ``provider_override`` arg.
    """
    from providers.subtitles import get_subtitles_provider

    provider = get_subtitles_provider(provider_override)
    log(f"[+] Creating subtitles via {provider.name}", "info")

    subtitles = provider.transcribe(
        audio_path,
        sentences=sentences,
        audio_clips=audio_clips,
        voice=voice,
    )

    SUBTITLES_DIR.mkdir(parents=True, exist_ok=True)
    subtitles_path = SUBTITLES_DIR / f"{uuid.uuid4()}.srt"
    with open(subtitles_path, "w", encoding="utf-8") as file:
        file.write(subtitles)

    # Re-flow: cap each line at 10 chars so subtitles read snappy on shorts.
    srt_equalizer.equalize_srt_file(str(subtitles_path), str(subtitles_path), 10)

    log("[+] Subtitles generated.", "success")
    return str(subtitles_path)


def combine_videos(
    video_paths,
    max_duration: int,
    max_clip_duration: int,
    threads: int,
):
    """Concatenate a list of assets into a single 1080x1920 video.

    ``video_paths`` is heterogeneous: each element is either a path string
    (treated as a stock video file) or a KenBurnsAsset (a still that the
    Ken-Burns helper turns into an animated clip on the fly). This keeps the
    pipeline backward-compatible while letting MFLUX-generated images sit
    alongside Pexels footage.
    """
    from effects.ken_burns import KenBurnsAsset, image_to_clip

    video_id = uuid.uuid4()
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    combined_video_path = TEMP_DIR / f"{video_id}.mp4"

    if not video_paths:
        raise ValueError("No source videos were provided for concatenation.")

    max_duration = float(max_duration)
    max_clip_duration = float(max_clip_duration)

    req_dur = max_duration / len(video_paths)

    log("[+] Combining videos...", "info")
    log(f"[+] Each clip will be maximum {req_dur} seconds long.", "info")

    clips = []
    tot_dur = 0
    while tot_dur < (max_duration - FRAME_EPSILON):
        progressed = False
        for asset in video_paths:
            remaining = max_duration - tot_dur
            if remaining <= FRAME_EPSILON:
                break

            if isinstance(asset, KenBurnsAsset):
                max_safe_source_duration = float(asset.duration)
                target_duration = min(
                    req_dur,
                    max_clip_duration,
                    remaining,
                    max_safe_source_duration,
                )
                if target_duration <= 0:
                    continue
                clip = image_to_clip(
                    asset.image_path,
                    target_duration,
                    motion=asset.motion,
                    target_size=(1080, 1920),
                    fps=30,
                )
                clips.append(clip)
                tot_dur += clip.duration
                progressed = True
                continue

            # Stock video path branch.
            clip = VideoFileClip(str(asset))
            clip = clip.without_audio()
            max_safe_source_duration = clip.duration - FRAME_EPSILON
            if max_safe_source_duration <= 0:
                clip.close()
                continue

            target_duration = min(req_dur, max_clip_duration, remaining)
            target_duration = min(target_duration, max_safe_source_duration)

            if target_duration <= 0:
                clip.close()
                continue

            if target_duration < clip.duration:
                clip = clip.subclipped(0, target_duration)
            clip = clip.with_fps(30)

            # Center-crop to 9:16 then resize.
            if round((clip.w / clip.h), 4) < 0.5625:
                clip = clip.cropped(
                    width=clip.w,
                    height=round(clip.w / 0.5625),
                    x_center=clip.w / 2,
                    y_center=clip.h / 2,
                )
            else:
                clip = clip.cropped(
                    width=round(0.5625 * clip.h),
                    height=clip.h,
                    x_center=clip.w / 2,
                    y_center=clip.h / 2,
                )
            clip = clip.resized(new_size=(1080, 1920))

            clips.append(clip)
            tot_dur += clip.duration
            progressed = True

        if not progressed:
            raise RuntimeError("Could not reach target duration from source videos.")

    if not clips:
        raise RuntimeError("No valid clips were produced for concatenation.")

    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip = final_clip.with_fps(30).with_duration(max_duration)

    # Intermediate file gets re-encoded by burn_and_mix(), so prioritize speed.
    # On Apple Silicon, use VideoToolbox; elsewhere, libx264 ultrafast.
    from providers.encoder import get_encoder

    encoder = get_encoder()
    if encoder.name == "videotoolbox":
        write_kwargs = {
            "codec": "h264_videotoolbox",
            "bitrate": "20M",
        }
    else:
        write_kwargs = {
            "codec": "libx264",
            "preset": "ultrafast",
        }

    try:
        final_clip.write_videofile(
            str(combined_video_path),
            threads=threads,
            fps=30,
            audio=False,
            **write_kwargs,
        )
    finally:
        final_clip.close()
        for clip in clips:
            clip.close()

    return str(combined_video_path)


def burn_and_mix(
    combined_video_path: str,
    audio_path: str,
    subtitles_path: str,
    *,
    output_path: str,
    music_path: Optional[str] = None,
    music_volume: float = 0.1,
    threads: int = 2,
    subtitles_position: str = "center,bottom",
    text_color: str = "#FFFF00",
    target_bitrate: Optional[str] = None,
    encoder_override: Optional[str] = None,
) -> str:
    """Single-pass ffmpeg composition: burn subtitles via libass, mix TTS (and
    optional looped background music), encode with the selected encoder.

    Replaces the old MoviePy SubtitlesClip + CompositeVideoClip path, eliminating
    per-frame ImageMagick TextClip calls and collapsing 2-3 encodes into 1.
    """
    from providers.encoder import get_encoder
    from providers.encoder.base import (
        SubtitleStyle,
        build_subtitles_filter,
        hex_to_ass_color,
        parse_subtitle_position,
    )

    encoder = get_encoder(encoder_override)
    ffmpeg_bin = get_ffmpeg_path()

    style = SubtitleStyle(
        font_name="Bold",
        font_size=22,
        primary_color=hex_to_ass_color(text_color),
        outline_color="&H00000000&",
        outline=4,
        alignment=parse_subtitle_position(subtitles_position),
    )
    fonts_dir = str(FONTS_DIR.resolve())
    sub_filter = build_subtitles_filter(subtitles_path, fonts_dir, style)

    target_bitrate = target_bitrate or os.getenv("TARGET_BITRATE", "8M")

    cmd: List[str] = [
        ffmpeg_bin,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(combined_video_path),
        "-i",
        str(audio_path),
    ]

    if music_path:
        cmd += ["-stream_loop", "-1", "-i", str(music_path)]
        filter_complex = (
            f"[0:v]{sub_filter}[v];"
            f"[1:a][2:a]amix=inputs=2:weights='1 {music_volume}':duration=first[a]"
        )
        cmd += [
            "-filter_complex",
            filter_complex,
            "-map",
            "[v]",
            "-map",
            "[a]",
        ]
    else:
        filter_complex = f"[0:v]{sub_filter}[v]"
        cmd += [
            "-filter_complex",
            filter_complex,
            "-map",
            "[v]",
            "-map",
            "1:a:0",
        ]

    cmd += encoder.video_codec_args(target_bitrate, threads)
    cmd += encoder.audio_codec_args("192k")
    cmd += ["-shortest", str(output_path)]

    log(
        f"[+] Encoding via {encoder.name} (bitrate={target_bitrate}, music={'on' if music_path else 'off'})",
        "info",
    )
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log(
            f"[-] ffmpeg failed (exit {result.returncode}): {result.stderr[:1500]}",
            "error",
        )
        raise RuntimeError(
            f"burn_and_mix: ffmpeg exited {result.returncode}. "
            f"Last stderr: {result.stderr[-500:]}"
        )

    return str(output_path)


def generate_video(
    combined_video_path: str,
    tts_path: str,
    subtitles_path: str,
    threads: int,
    subtitles_position: str,
    text_color: str,
) -> str:
    """Backward-compat wrapper: burn subtitles + add TTS audio to TEMP_DIR/output.mp4.

    Music is no longer applied here — the pipeline now calls burn_and_mix()
    directly when use_music is set, in a single ffmpeg pass.
    """
    output_path = TEMP_DIR / "output.mp4"
    burn_and_mix(
        combined_video_path,
        tts_path,
        subtitles_path,
        output_path=str(output_path),
        threads=threads or 2,
        subtitles_position=subtitles_position or "center,bottom",
        text_color=text_color or "#FFFF00",
    )
    return "output.mp4"
