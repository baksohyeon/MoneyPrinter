import pytest

from providers.encoder.base import (
    SubtitleStyle,
    build_subtitles_filter,
    hex_to_ass_color,
    parse_subtitle_position,
)
from providers.encoder.factory import get_encoder
from providers.encoder.libx264 import Libx264Encoder
from providers.encoder.videotoolbox import VideoToolboxEncoder


@pytest.mark.parametrize(
    "web,ass",
    [
        ("#FFFF00", "&H0000FFFF&"),
        ("#FF0000", "&H000000FF&"),
        ("#00FF00", "&H0000FF00&"),
        ("#0000FF", "&H00FF0000&"),
        ("FF0000", "&H000000FF&"),
        ("#FFF", "&H00FFFFFF&"),
    ],
)
def test_hex_to_ass_color_known_values(web, ass):
    assert hex_to_ass_color(web) == ass


def test_hex_to_ass_color_invalid_falls_back_to_yellow():
    assert hex_to_ass_color("not-a-color") == "&H0000FFFF&"
    assert hex_to_ass_color("") == "&H0000FFFF&"
    assert hex_to_ass_color(None) == "&H0000FFFF&"


@pytest.mark.parametrize(
    "pos,expected",
    [
        ("center,bottom", 2),
        ("left,bottom", 1),
        ("right,bottom", 3),
        ("center,center", 5),
        ("left,top", 7),
        ("right,top", 9),
        (None, 2),
        ("", 2),
        ("garbage", 2),
        ("foo,bar", 2),
    ],
)
def test_parse_subtitle_position(pos, expected):
    assert parse_subtitle_position(pos) == expected


def test_build_subtitles_filter_emits_libass_argument():
    f = build_subtitles_filter("/tmp/foo.srt", "/tmp/fonts", SubtitleStyle())
    assert f.startswith("subtitles=/tmp/foo.srt")
    assert ":fontsdir=/tmp/fonts" in f
    assert "Fontname=Bold" in f
    assert "PrimaryColour=&H0000FFFF&" in f
    assert "Alignment=2" in f


def test_build_subtitles_filter_rejects_unsafe_paths():
    with pytest.raises(ValueError):
        build_subtitles_filter("/tmp/with:colon.srt", "/tmp/fonts", SubtitleStyle())
    with pytest.raises(ValueError):
        build_subtitles_filter("/tmp/foo.srt", "/tmp/with,comma", SubtitleStyle())


def test_libx264_encoder_args_contract():
    enc = Libx264Encoder()
    args = enc.video_codec_args("8M", 4)
    assert "libx264" in args
    assert "-pix_fmt" in args and "yuv420p" in args
    assert "-threads" in args and "4" in args


def test_videotoolbox_encoder_args_contract():
    enc = VideoToolboxEncoder()
    args = enc.video_codec_args("8M", 4)
    assert "h264_videotoolbox" in args
    assert "-b:v" in args and "8M" in args
    assert "-tag:v" in args and "avc1" in args


def test_factory_libx264_override_returns_libx264(monkeypatch):
    monkeypatch.delenv("ENCODER_PROVIDER", raising=False)
    enc = get_encoder("libx264")
    assert enc.name == "libx264"


def test_factory_videotoolbox_override_falls_back_when_unavailable(monkeypatch):
    monkeypatch.delenv("ENCODER_PROVIDER", raising=False)
    monkeypatch.setattr(VideoToolboxEncoder, "available", lambda self: False)
    enc = get_encoder("videotoolbox")
    assert enc.name == "libx264"


def test_factory_auto_picks_videotoolbox_when_available(monkeypatch):
    monkeypatch.delenv("ENCODER_PROVIDER", raising=False)
    monkeypatch.setattr(VideoToolboxEncoder, "available", lambda self: True)
    enc = get_encoder()
    assert enc.name == "videotoolbox"


def test_factory_auto_falls_back_to_libx264(monkeypatch):
    monkeypatch.delenv("ENCODER_PROVIDER", raising=False)
    monkeypatch.setattr(VideoToolboxEncoder, "available", lambda self: False)
    enc = get_encoder()
    assert enc.name == "libx264"


def test_factory_env_override_works(monkeypatch):
    monkeypatch.setenv("ENCODER_PROVIDER", "libx264")
    enc = get_encoder()
    assert enc.name == "libx264"
