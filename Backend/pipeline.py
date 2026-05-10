import os
import shutil
import subprocess

from apiclient.errors import HttpError
from moviepy import AudioFileClip, concatenate_audioclips
from uuid import uuid4

from cast import CastError, load_cast
from dialogue import parse_script
from effects.ken_burns import KenBurnsAsset
from gpt import generate_metadata, generate_script, get_search_terms
from logstream import log
from parallel import parallel_map
from providers.imagegen import get_imagegen_provider
from providers.stock import get_stock_providers
from tiktokvoice import tts
from utils import (
    ASSETS_DIR,
    BASE_DIR,
    PROJECT_ROOT,
    TEMP_DIR,
    choose_random_song,
)
from video import burn_and_mix, combine_videos, generate_subtitles, save_video
from youtube import upload_video


class PipelineCancelled(Exception):
    pass


def run_generation_pipeline(
    data: dict,
    is_cancelled,
    on_log,
    amount_of_stock_videos: int = 10,
) -> str:
    def emit(message: str, level: str = "info") -> None:
        log(message, level)
        if on_log:
            on_log(message, level)

    def guard_cancelled() -> None:
        if is_cancelled and is_cancelled():
            raise PipelineCancelled("Video generation was cancelled.")

    paragraph_number = int(data.get("paragraphNumber", 1))
    ai_model = data.get("aiModel")
    n_threads = data.get("threads")
    subtitles_position = data.get("subtitlesPosition")
    text_color = data.get("color")
    use_music = data.get("useMusic", False)
    automate_youtube_upload = data.get("automateYoutubeUpload", False)

    # Per-job provider overrides (frontend sends these in the payload).
    # Empty string / None = use env / auto-priority.
    provider_overrides = data.get("providers") or {}
    imagegen_override = (provider_overrides.get("imagegen") or "").strip() or None
    encoder_override = (provider_overrides.get("encoder") or "").strip() or None
    subtitles_override = (provider_overrides.get("subtitles") or "").strip() or None

    # Optional cast for dialogue-mode shorts. Empty / missing / invalid →
    # fall back to single-narrator mode (existing behavior).
    cast = None
    cast_name = (data.get("cast") or "").strip()
    if cast_name:
        try:
            cast = load_cast(cast_name)
            emit(
                f"[+] Cast loaded: {cast.name} ({len(cast.characters)} characters)",
                "info",
            )
        except CastError as exc:
            emit(
                f"[!] Cast '{cast_name}' could not be loaded ({exc}). "
                "Falling back to single-narrator mode.",
                "warning",
            )

    emit("[Video to be generated]", "info")
    emit("   Subject: " + data["videoSubject"], "info")
    emit("   AI Model: " + str(ai_model), "info")
    emit("   Custom Prompt: " + data["customPrompt"], "info")

    guard_cancelled()

    voice = data.get("voice", "")
    voice_prefix = voice[:2]

    if not voice:
        emit('[!] No voice was selected. Defaulting to "en_us_001"', "warning")
        voice = "en_us_001"
        voice_prefix = voice[:2]

    script = generate_script(
        data["videoSubject"],
        paragraph_number,
        ai_model,
        voice,
        data["customPrompt"],
        cast=cast,
    )

    if not script:
        raise RuntimeError(
            "Could not generate a script. Try a different model or prompt."
        )

    search_terms = get_search_terms(
        data["videoSubject"], amount_of_stock_videos, script, ai_model
    )

    it = 15
    # Niche topics have few long clips; 3s helps. Override: PEXELS_MIN_VIDEO_DURATION_SECONDS
    min_dur = int(os.getenv("PEXELS_MIN_VIDEO_DURATION_SECONDS", "3"))

    providers = get_stock_providers()
    if not providers:
        raise RuntimeError(
            "No stock-video providers enabled. Set PEXELS_API_KEY (and optionally "
            "PIXABAY_API_KEY / COVERR_API_KEY) in .env."
        )
    emit(
        f"[+] Stock providers enabled: {', '.join(p.name for p in providers)}",
        "info",
    )

    guard_cancelled()
    search_workers = int(os.getenv("PARALLEL_SEARCH_WORKERS", "8"))

    # Flatten (provider, term) so all queries fan out across one thread pool.
    queries = [
        (provider, term) for term in search_terms for provider in providers
    ]

    def _query_one(pair):
        provider, term = pair
        return provider.search(term, count=it, min_duration=min_dur)

    raw_results = parallel_map(
        _query_one,
        queries,
        max_workers=max(search_workers, len(providers)),
        on_error=lambda pair, exc: emit(
            f"[-] {pair[0].name} search failed for '{pair[1]}': {exc}",
            "warning",
        ),
        is_cancelled=is_cancelled,
    )

    # Group matches by term (preserve provider order from STOCK_SOURCES).
    matches_by_term: dict[str, list] = {term: [] for term in search_terms}
    for (_provider, term), matches in zip(queries, raw_results):
        if matches:
            matches_by_term[term].extend(matches)

    video_urls: list[str] = []
    used_terms: list[str] = []
    unmatched_terms: list[str] = []
    for term in search_terms:
        picked = False
        for match in matches_by_term.get(term, []):
            if match.url not in video_urls:
                video_urls.append(match.url)
                used_terms.append(term)
                picked = True
                break
        if not picked:
            unmatched_terms.append(term)

    # Optional: ask the imagegen provider to fill stock gaps with AI B-roll.
    imagegen_assets: list[KenBurnsAsset] = []
    imagegen = get_imagegen_provider(imagegen_override)
    if imagegen and unmatched_terms:
        emit(
            f"[+] {imagegen.name}: generating {len(unmatched_terms)} B-roll image(s) for unmatched terms",
            "info",
        )
        for term in unmatched_terms:
            guard_cancelled()
            try:
                img_path = str(TEMP_DIR / f"{uuid4()}_imagegen.png")
                imagegen.generate(term, img_path)
                imagegen_assets.append(
                    KenBurnsAsset(
                        image_path=img_path,
                        duration=5.0,
                        motion="zoom_in",
                    )
                )
                emit(f"   imagegen ok: '{term}' → {img_path}", "info")
            except Exception as exc:
                emit(f"[-] imagegen failed for '{term}': {exc}", "warning")
    elif unmatched_terms:
        emit(
            f"[!] {len(unmatched_terms)} term(s) had no stock match; "
            f"set IMAGEGEN_ENABLED=true to fill with AI images.",
            "warning",
        )

    if not video_urls and not imagegen_assets:
        raise RuntimeError("No videos found to download and imagegen disabled.")

    guard_cancelled()
    emit(f"[+] Downloading {len(video_urls)} videos...", "info")

    download_workers = int(os.getenv("PARALLEL_DOWNLOAD_WORKERS", "8"))
    download_results = parallel_map(
        save_video,
        video_urls,
        max_workers=download_workers,
        on_error=lambda url, exc: emit(
            f"[-] Could not download video: {url} ({exc})", "error"
        ),
        is_cancelled=is_cancelled,
    )
    video_paths = [path for path in download_results if path]
    # Mix Ken-Burns assets in with the downloaded paths — combine_videos
    # accepts both string paths and KenBurnsAsset instances.
    video_paths = video_paths + imagegen_assets

    # Auto-prepend assets/intro.{png,jpg,jpeg,webp} if present. Used to drop
    # a meme PNG / infographic at the start of the video. Motion = "fit"
    # so the entire image is visible (no crop) and load-bearing text on
    # the edges survives.
    intro_image = next(
        (
            ASSETS_DIR / f"intro.{ext}"
            for ext in ("png", "jpg", "jpeg", "webp")
            if (ASSETS_DIR / f"intro.{ext}").exists()
        ),
        None,
    )
    if intro_image is not None:
        try:
            intro_duration = float(os.getenv("INTRO_DURATION", "3.0"))
        except ValueError:
            intro_duration = 3.0
        intro_asset = KenBurnsAsset(
            image_path=str(intro_image),
            duration=intro_duration,
            motion="fit",
        )
        video_paths = [intro_asset] + video_paths
        emit(
            f"[+] Using intro asset {intro_image.name} ({intro_duration:.1f}s, motion=fit)",
            "info",
        )

    emit("[+] Videos downloaded!", "success")
    emit("[+] Script generated!", "success")

    guard_cancelled()

    # Parse the script into dialogue lines. With a cast, lines tagged
    # [CHARACTER_ID] are routed to that character's voice; without (or on
    # untagged output) every line gets the job's default voice.
    dialogue_lines = parse_script(script, cast, default_voice=voice)
    if not dialogue_lines:
        raise RuntimeError("Script produced zero usable lines.")

    if cast is not None:
        line_summary = ", ".join(
            f"[{l.character_id}]" if l.character_id else "[narrator]"
            for l in dialogue_lines
        )
        emit(f"[+] Dialogue: {len(dialogue_lines)} line(s) — {line_summary}", "info")

    tts_paths = [str(TEMP_DIR / f"{uuid4()}.mp3") for _ in dialogue_lines]
    tts_workers = int(os.getenv("PARALLEL_TTS_WORKERS", "4"))

    def _synthesize(idx_line):
        idx, line = idx_line
        tts(line.text, line.voice or voice, filename=tts_paths[idx])
        return tts_paths[idx]

    parallel_map(
        _synthesize,
        list(enumerate(dialogue_lines)),
        max_workers=tts_workers,
        on_error=lambda pair, exc: emit(
            f"[-] TTS failed for line #{pair[0]} ([{pair[1].character_id or 'narrator'}]): {exc}",
            "error",
        ),
        is_cancelled=is_cancelled,
    )

    # Keep dialogue lines and audio clips aligned — drop where synth failed.
    aligned_lines = []
    paths: list[AudioFileClip] = []
    for line, p in zip(dialogue_lines, tts_paths):
        if os.path.exists(p):
            aligned_lines.append(line)
            paths.append(AudioFileClip(p))
    if not paths:
        raise RuntimeError("All TTS calls failed; cannot continue.")
    # Subtitles still want plain sentence text — strip away character tags.
    sentences = [l.text for l in aligned_lines]

    final_audio = concatenate_audioclips(paths)
    tts_path = str(TEMP_DIR / f"{uuid4()}.mp3")
    try:
        final_audio.write_audiofile(tts_path)
    finally:
        final_audio.close()
        for audio_clip in paths:
            audio_clip.close()

    try:
        subtitles_path = generate_subtitles(
            audio_path=tts_path,
            sentences=sentences,
            audio_clips=paths,
            voice=voice_prefix,
            provider_override=subtitles_override,
        )
    except Exception as err:
        emit(f"[-] Error generating subtitles: {err}", "error")
        subtitles_path = None

    if not subtitles_path:
        raise RuntimeError(
            "Could not generate subtitles. Check AssemblyAI key or local subtitle settings."
        )

    temp_audio = AudioFileClip(tts_path)
    try:
        combined_video_path = combine_videos(
            video_paths, temp_audio.duration, 5, n_threads or 2
        )
    finally:
        temp_audio.close()

    final_video_path = "output.mp4"
    final_output_path = str(PROJECT_ROOT / final_video_path)

    song_path = None
    if use_music:
        song_path = choose_random_song()
        if not song_path:
            emit(
                "[-] Could not find songs in Songs/. Continuing without background music.",
                "warning",
            )

    guard_cancelled()

    try:
        burn_and_mix(
            combined_video_path,
            tts_path,
            subtitles_path,
            output_path=final_output_path,
            music_path=song_path,
            threads=n_threads or 2,
            subtitles_position=subtitles_position or "center,bottom",
            text_color=text_color or "#FFFF00",
            encoder_override=encoder_override,
        )
    except Exception as err:
        raise RuntimeError(
            f"Could not render final video. ({err})"
        ) from err

    title, description, keywords = generate_metadata(
        data["videoSubject"], script, ai_model
    )

    emit("[-] Metadata for YouTube upload:", "info")
    emit("   Title:", "info")
    emit(f"   {title}", "info")
    emit("   Description:", "info")
    emit(f"   {description}", "info")
    emit("   Keywords:", "info")
    emit(f"  {', '.join(keywords)}", "info")

    if automate_youtube_upload:
        client_secrets_file = str((BASE_DIR / "client_secret.json").resolve())
        skip_yt_upload = False
        if not os.path.exists(client_secrets_file):
            skip_yt_upload = True
            emit(
                "[-] Client secrets file missing. YouTube upload will be skipped.",
                "warning",
            )
            emit(
                "[-] Please download the client_secret.json from Google Cloud Platform and store this inside the /Backend directory.",
                "error",
            )

        if not skip_yt_upload:
            video_category_id = "28"
            privacy_status = "private"
            video_metadata = {
                "video_path": final_output_path,
                "title": title,
                "description": description,
                "category": video_category_id,
                "keywords": ",".join(keywords),
                "privacyStatus": privacy_status,
            }

            try:
                video_response = upload_video(
                    video_path=video_metadata["video_path"],
                    title=video_metadata["title"],
                    description=video_metadata["description"],
                    category=video_metadata["category"],
                    keywords=video_metadata["keywords"],
                    privacy_status=video_metadata["privacyStatus"],
                )
                emit(f"Uploaded video ID: {video_response.get('id')}", "success")
            except HttpError as err:
                emit(
                    f"An HTTP error {err.resp.status} occurred:\n{err.content}", "error"
                )

    emit(f"[+] Video generated: {final_video_path}!", "success")

    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/f", "/im", "ffmpeg.exe"],
            check=False,
            capture_output=True,
            text=True,
        )
    elif shutil.which("pkill"):
        subprocess.run(
            ["pkill", "-f", "ffmpeg"],
            check=False,
            capture_output=True,
            text=True,
        )

    return final_video_path
