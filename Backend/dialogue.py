"""Parse Ollama-emitted scripts into a list of (character, voice, text) lines.

Cast mode: the model is asked to emit each line tagged like
    [CHAD] An asteroid will strike the northeast of the Yucatán Peninsula.
A regex pulls out the tag, looks up the character in the cast, and routes
the line to that character's voice.

Single-narrator mode: the script is plain prose. Sentences are split on
``". "`` (the same separator the pipeline used pre-cast) and every line gets
the job's default voice.

The unified entry point ``parse_script()`` handles both. If a cast is
provided but the model emitted zero tagged lines, it falls back to
single-narrator mode automatically — cast is a soft augmentation, never a
hard requirement.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from cast import Cast


_TAG_LINE = re.compile(r"^\s*\[([A-Z][A-Z0-9_]*)\]\s*(.+?)\s*$")


@dataclass
class DialogueLine:
    character_id: str        # uppercase ID, or "" in single-narrator mode
    text: str                # cleaned line, no [TAG] prefix
    voice: str               # TikTok TTS voice code routed for this line


def parse_tagged_dialogue(
    script: str, cast: Cast, fallback_voice: str
) -> List[DialogueLine]:
    """Return DialogueLine per ``[ID] sentence`` line in the script.

    Lines that don't match the [ID] format are dropped. Lines with an ID not
    in the cast still get included but routed to ``fallback_voice``.
    """
    if not script:
        return []
    lines: List[DialogueLine] = []
    for raw in script.splitlines():
        m = _TAG_LINE.match(raw)
        if not m:
            continue
        cid, text = m.group(1), m.group(2).strip()
        if not text:
            continue
        char = cast.find(cid)
        voice = char.voice if char else (fallback_voice or "")
        lines.append(DialogueLine(character_id=cid, text=text, voice=voice))
    return lines


def parse_untagged_script(script: str, default_voice: str) -> List[DialogueLine]:
    """Wrap the legacy ``". "`` sentence-split into DialogueLine list."""
    if not script:
        return []
    parts = [s.strip() for s in script.split(". ") if s.strip()]
    return [
        DialogueLine(character_id="", text=p, voice=default_voice or "")
        for p in parts
    ]


def parse_script(
    script: str,
    cast: Optional[Cast],
    default_voice: str,
) -> List[DialogueLine]:
    """Single entry: try cast-mode parsing if a cast was given, fall back to
    legacy sentence split if cast yielded nothing usable.
    """
    if cast is not None:
        tagged = parse_tagged_dialogue(script, cast, fallback_voice=default_voice)
        if tagged:
            return tagged
    return parse_untagged_script(script, default_voice)
