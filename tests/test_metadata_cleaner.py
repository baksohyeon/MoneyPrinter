"""Locks in the patterns observed from llama3.1:8b output that the cleaner
must strip — preambles, numbered alternatives, markdown emphasis, trailing
parentheticals. Feel free to add more cases as they show up in the wild."""

import pytest

from gpt import _clean_metadata_line


def test_returns_empty_for_empty_input():
    assert _clean_metadata_line("") == ""
    assert _clean_metadata_line("   \n  \n ") == ""


def test_plain_string_passes_through():
    assert _clean_metadata_line("Just a plain title here") == "Just a plain title here"


def test_strips_double_asterisk_wrap():
    assert _clean_metadata_line("**Wrapped Title**") == "Wrapped Title"


def test_strips_quote_wrap():
    assert _clean_metadata_line('"Quoted Title"') == "Quoted Title"


def test_extracts_from_numbered_alternative_list():
    raw = """Here are a few options:

1. **"Dino Briefing: The Prehistoric Warning"** (6 words)
2. "Telling T-Rexes About Their Demise" (9 words)
"""
    assert _clean_metadata_line(raw) == "Dino Briefing: The Prehistoric Warning"


def test_extracts_from_bolded_quoted_line_after_preamble():
    raw = """Here is a brief and engaging description for your YouTube Shorts video:

**"The Unconventional Time Traveler | Warning Dinosaurs of Doom!"**

"Body line that should not be picked."
"""
    assert (
        _clean_metadata_line(raw)
        == "The Unconventional Time Traveler | Warning Dinosaurs of Doom!"
    )


def test_handles_sure_heres_preamble():
    raw = "Sure, here's a title:\n\n**The One About Dinosaurs**"
    assert _clean_metadata_line(raw) == "The One About Dinosaurs"


def test_drops_trailing_parenthetical():
    raw = '**"Snappy Title"** (8 words, keyword rich)'
    assert _clean_metadata_line(raw) == "Snappy Title"


def test_falls_back_to_raw_when_only_preambles():
    """If every line is a preamble, return the raw input rather than empty
    string. Better to ship the messy version than silently emit nothing."""
    raw = "Here are a few options:\nHere is the title:"
    out = _clean_metadata_line(raw)
    assert out  # non-empty


def test_strips_bullet_marker():
    raw = "* My Title"
    assert _clean_metadata_line(raw) == "My Title"
