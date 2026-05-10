from cast import Cast, Character
from dialogue import (
    DialogueLine,
    parse_script,
    parse_tagged_dialogue,
    parse_untagged_script,
)


def _trio() -> Cast:
    return Cast(
        name="trio",
        description="",
        characters=[
            Character(id="ALICE", voice="v_alice"),
            Character(id="BOB", voice="v_bob"),
        ],
    )


def test_parse_tagged_basic():
    script = (
        "[ALICE] Hello there.\n"
        "[BOB] General Kenobi.\n"
    )
    out = parse_tagged_dialogue(script, _trio(), fallback_voice="v_default")
    assert out == [
        DialogueLine(character_id="ALICE", text="Hello there.", voice="v_alice"),
        DialogueLine(character_id="BOB", text="General Kenobi.", voice="v_bob"),
    ]


def test_parse_tagged_drops_untagged_lines():
    """Lines without [ID] are not eligible for tagged-dialogue mode."""
    script = (
        "Random preamble.\n"
        "[ALICE] First.\n"
        "Floating untagged text in the middle.\n"
        "[BOB] Last.\n"
    )
    out = parse_tagged_dialogue(script, _trio(), fallback_voice="v_default")
    assert [(l.character_id, l.text) for l in out] == [
        ("ALICE", "First."),
        ("BOB", "Last."),
    ]


def test_parse_tagged_unknown_id_uses_fallback():
    script = "[ALIEN] What is this place?\n"
    out = parse_tagged_dialogue(script, _trio(), fallback_voice="v_fallback")
    assert len(out) == 1
    assert out[0].character_id == "ALIEN"
    assert out[0].voice == "v_fallback"


def test_parse_tagged_handles_blank_lines_and_whitespace():
    script = "  \n[ALICE]   Hi.   \n\n[BOB]\tHey.\n"
    out = parse_tagged_dialogue(script, _trio(), fallback_voice="x")
    assert [(l.character_id, l.text) for l in out] == [
        ("ALICE", "Hi."),
        ("BOB", "Hey."),
    ]


def test_parse_untagged_splits_on_period_space():
    script = "First sentence. Second sentence. Third sentence."
    out = parse_untagged_script(script, default_voice="v")
    assert [l.text for l in out] == [
        "First sentence",
        "Second sentence",
        "Third sentence.",
    ]
    assert all(l.character_id == "" for l in out)
    assert all(l.voice == "v" for l in out)


def test_parse_untagged_empty_string():
    assert parse_untagged_script("", "v") == []


def test_parse_script_prefers_cast_when_tags_present():
    script = "[ALICE] One.\n[BOB] Two.\n"
    out = parse_script(script, _trio(), default_voice="v_def")
    assert [l.voice for l in out] == ["v_alice", "v_bob"]


def test_parse_script_falls_back_when_no_tags():
    """Cast given but model produced plain prose: should auto-fallback."""
    script = "First. Second. Third."
    out = parse_script(script, _trio(), default_voice="v_def")
    assert all(l.character_id == "" for l in out)
    assert all(l.voice == "v_def" for l in out)
    assert len(out) == 3


def test_parse_script_no_cast_uses_untagged():
    script = "First. Second."
    out = parse_script(script, None, default_voice="v_x")
    assert [l.text for l in out] == ["First", "Second."]
    assert all(l.voice == "v_x" for l in out)
