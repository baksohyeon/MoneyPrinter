from pathlib import Path

import pytest
from PIL import Image

from effects.ken_burns import KenBurnsAsset, image_to_clip


def _make_jpg(path: Path, w: int = 800, h: int = 600) -> Path:
    """Make a JPG with a horizontal gradient — zoom motion shifts pixel
    values, so frames differ across t even though the source is static."""
    img = Image.new("RGB", (w, h))
    px = img.load()
    for x in range(w):
        for y in range(h):
            px[x, y] = (x % 256, y % 256, (x + y) % 256)
    img.save(path, "JPEG")
    return path


def test_image_to_clip_produces_target_size(tmp_path):
    img = _make_jpg(tmp_path / "src.jpg", 1280, 720)
    clip = image_to_clip(str(img), duration=2.0, motion="zoom_in")
    try:
        assert clip.size == (1080, 1920)
        assert pytest.approx(clip.duration, rel=0.01) == 2.0
        assert clip.fps == 30
    finally:
        clip.close()


def test_image_to_clip_handles_portrait_source(tmp_path):
    img = _make_jpg(tmp_path / "portrait.jpg", 720, 1280)
    clip = image_to_clip(str(img), duration=1.5, motion="zoom_out")
    try:
        assert clip.size == (1080, 1920)
        assert pytest.approx(clip.duration, rel=0.01) == 1.5
    finally:
        clip.close()


def test_image_to_clip_zoom_out_animates(tmp_path):
    """Sample a frame at t=0 vs t=duration and confirm pixel content differs.
    A static (broken zoom) image would produce identical frames.
    """
    img = _make_jpg(tmp_path / "src.jpg", 1280, 720)
    clip = image_to_clip(str(img), duration=2.0, motion="zoom_out")
    try:
        f0 = clip.get_frame(0.0)
        f1 = clip.get_frame(1.9)
        # Frames are numpy arrays. Different zoom levels mean different pixel values.
        assert f0.shape == f1.shape
        # Cheap check: the two frames are not literally identical.
        assert not (f0 == f1).all(), "zoom motion produced identical frames"
    finally:
        clip.close()


def test_ken_burns_asset_defaults():
    a = KenBurnsAsset(image_path="/tmp/x.png")
    assert a.duration == 5.0
    assert a.motion == "zoom_in"
