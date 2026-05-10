import json

import pytest

import cast as cast_module
from cast import (
    Cast,
    CastError,
    Character,
    format_cast_header,
    list_casts,
    load_cast,
)


def _write(tmp_path, name: str, payload: dict):
    p = tmp_path / f"{name}.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def test_load_cast_happy_path(monkeypatch, tmp_path):
    monkeypatch.setattr(cast_module, "CAST_DIR", tmp_path)
    _write(
        tmp_path,
        "trio",
        {
            "name": "trio",
            "description": "test cast",
            "characters": [
                {"id": "A", "voice": "v1", "description": "alpha"},
                {"id": "B", "voice": "v2"},
            ],
        },
    )
    cast = load_cast("trio")
    assert cast.name == "trio"
    assert len(cast.characters) == 2
    assert cast.characters[0] == Character(id="A", voice="v1", description="alpha")
    assert cast.find("a") == cast.characters[0]
    assert cast.find("missing") is None


def test_load_cast_filename_must_match_declared_name(monkeypatch, tmp_path):
    monkeypatch.setattr(cast_module, "CAST_DIR", tmp_path)
    _write(
        tmp_path,
        "alpha",
        {"name": "beta", "characters": [{"id": "X", "voice": "v"}]},
    )
    with pytest.raises(CastError, match="declared name 'beta' does not match"):
        load_cast("alpha")


def test_load_cast_rejects_invalid_name():
    with pytest.raises(CastError):
        load_cast("Bad-Name!")


def test_load_cast_missing_file(monkeypatch, tmp_path):
    monkeypatch.setattr(cast_module, "CAST_DIR", tmp_path)
    with pytest.raises(CastError, match="not found"):
        load_cast("nope")


def test_load_cast_invalid_json(monkeypatch, tmp_path):
    monkeypatch.setattr(cast_module, "CAST_DIR", tmp_path)
    (tmp_path / "broken.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(CastError, match="invalid JSON"):
        load_cast("broken")


def test_load_cast_requires_characters(monkeypatch, tmp_path):
    monkeypatch.setattr(cast_module, "CAST_DIR", tmp_path)
    _write(tmp_path, "empty", {"characters": []})
    with pytest.raises(CastError, match="non-empty array"):
        load_cast("empty")


def test_load_cast_rejects_lowercase_id(monkeypatch, tmp_path):
    monkeypatch.setattr(cast_module, "CAST_DIR", tmp_path)
    _write(tmp_path, "lower", {"characters": [{"id": "lower", "voice": "v"}]})
    with pytest.raises(CastError, match="must be uppercase"):
        load_cast("lower")


def test_load_cast_rejects_duplicate_ids(monkeypatch, tmp_path):
    monkeypatch.setattr(cast_module, "CAST_DIR", tmp_path)
    _write(
        tmp_path,
        "dup",
        {
            "characters": [
                {"id": "X", "voice": "v1"},
                {"id": "X", "voice": "v2"},
            ]
        },
    )
    with pytest.raises(CastError, match="duplicate character id"):
        load_cast("dup")


def test_load_cast_rejects_missing_voice(monkeypatch, tmp_path):
    monkeypatch.setattr(cast_module, "CAST_DIR", tmp_path)
    _write(tmp_path, "novoice", {"characters": [{"id": "A", "voice": ""}]})
    with pytest.raises(CastError, match="missing 'voice'"):
        load_cast("novoice")


def test_list_casts_skips_invalid(monkeypatch, tmp_path):
    monkeypatch.setattr(cast_module, "CAST_DIR", tmp_path)
    _write(tmp_path, "good", {"characters": [{"id": "A", "voice": "v"}]})
    (tmp_path / "broken.json").write_text("{", encoding="utf-8")
    summaries = list_casts()
    assert len(summaries) == 1
    assert summaries[0].name == "good"
    assert summaries[0].character_count == 1


def test_list_casts_empty_when_dir_missing(monkeypatch, tmp_path):
    missing = tmp_path / "nonexistent"
    monkeypatch.setattr(cast_module, "CAST_DIR", missing)
    assert list_casts() == []


def test_format_cast_header_lists_all_ids():
    cast = Cast(
        name="trio",
        description="",
        characters=[
            Character(id="A", voice="v1", description="first"),
            Character(id="B", voice="v2"),
        ],
    )
    header = format_cast_header(cast)
    assert "[A]" in header
    assert "[B]" in header
    assert "first" in header
    assert "USER PROMPT BELOW" in header


def test_real_wojak_chad_cast_loads():
    """Smoke that the cast we ship in repo is valid."""
    cast = load_cast("wojak_chad")
    assert cast.name == "wojak_chad"
    assert len(cast.characters) == 5
    ids = {c.id for c in cast.characters}
    assert ids == {"GRANDDAUGHTER", "GRANDMOTHER", "NARRATOR", "CHAD", "DINOSAUR"}
