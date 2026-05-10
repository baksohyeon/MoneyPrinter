import os
import shutil
import subprocess

from apiclient.errors import HttpError
from moviepy import AudioFileClip, concatenate_audioclips
from uuid import uuid4

from gpt import generate_metadata, generate_script, get_search_terms
from logstream import log
from parallel import parallel_map
from providers.stock import get_stock_providers
from tiktokvoice import tts
from utils import (
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
    for term in search_terms:
        for match in matches_by_term.get(term, []):
            if match.url not in video_urls:
                video_urls.append(match.url)
                break

    if not video_urls:
        raise RuntimeError("No videos found to download.")

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

    emit("[+] Videos downloaded!", "success")
    emit("[+] Script generated!", "success")

    guard_cancelled()

    sentences = script.split(". ")
    sentences = list(filter(lambda x: x != "", sentences))

    tts_paths = [str(TEMP_DIR / f"{uuid4()}.mp3") for _ in sentences]
    tts_workers = int(os.getenv("PARALLEL_TTS_WORKERS", "4"))

    def _synthesize(idx_sentence):
        idx, sentence = idx_sentence
        tts(sentence, voice, filename=tts_paths[idx])
        return tts_paths[idx]

    parallel_map(
        _synthesize,
        list(enumerate(sentences)),
        max_workers=tts_workers,
        on_error=lambda pair, exc: emit(
            f"[-] TTS failed for sentence #{pair[0]}: {exc}", "error"
        ),
        is_cancelled=is_cancelled,
    )

    # Keep sentences and audio clips aligned — drop entries where synth failed.
    aligned_sentences: list[str] = []
    paths: list[AudioFileClip] = []
    for sentence, p in zip(sentences, tts_paths):
        if os.path.exists(p):
            aligned_sentences.append(sentence)
            paths.append(AudioFileClip(p))
    sentences = aligned_sentences
    if not paths:
        raise RuntimeError("All TTS calls failed; cannot continue.")

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
