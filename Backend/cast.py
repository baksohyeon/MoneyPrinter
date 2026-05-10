"""Reusable character cast definitions for dialogue-mode shorts.

A cast is a small JSON file at ``cast/<name>.json`` declaring the characters
that can speak in a video, each tied to a TikTok TTS voice code. The pipeline
loads a cast by name (per job) and the LLM emits dialogue tagged with the
character ID; the pipeline routes each tagged line to that character's voice.

Casts are optional. When unset / missing / malformed, the pipeline falls back
to the existing single-narrator flow with the job's ``voice`` field.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from utils import PROJECT_ROOT


CAST_DIR = PROJECT_ROOT / "cast"

_NAME_RE = re.compile(r"^[a-z0-9_]+$")
_ID_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


@dataclass
class Character:
    id: str
    voice: str
    description: str = ""


@dataclass
class Cast:
    name: str
    description: str
    characters: List[Character] = field(default_factory=list)

    def find(self, character_id: str) -> Optional[Character]:
        cid = (character_id or "").upper()
        for c in self.characters:
            if c.id == cid:
                return c
        return None


@dataclass
class CastSummary:
    name: str
    description: str
    character_count: int


class CastError(ValueError):
    """Raised on validation failure when loading a cast file."""


def _validate(name: str, payload: dict) -> Cast:
    if not isinstance(payload, dict):
        raise CastError(f"cast '{name}': top-level must be a JSON object")

    declared_name = str(payload.get("name") or name).strip().lower()
    if not _NAME_RE.match(declared_name):
        raise CastError(
            f"cast '{name}': name '{declared_name}' must be lowercase letters/digits/underscore"
        )
    if declared_name != name:
        raise CastError(
            f"cast '{name}': declared name '{declared_name}' does not match filename"
        )

    description = str(payload.get("description") or "").strip()

    raw_chars = payload.get("characters") or []
    if not isinstance(raw_chars, list) or not raw_chars:
        raise CastError(f"cast '{name}': 'characters' must be a non-empty array")

    seen_ids = set()
    characters: List[Character] = []
    for i, ch in enumerate(raw_chars):
        if not isinstance(ch, dict):
            raise CastError(f"cast '{name}': character[{i}] must be an object")
        cid = str(ch.get("id") or "").strip()
        if not _ID_RE.match(cid):
            raise CastError(
                f"cast '{name}': character[{i}] id '{cid}' must be uppercase letters/digits/underscore, starting with a letter"
            )
        if cid in seen_ids:
            raise CastError(f"cast '{name}': duplicate character id '{cid}'")
        seen_ids.add(cid)
        voice = str(ch.get("voice") or "").strip()
        if not voice:
            raise CastError(f"cast '{name}': character '{cid}' missing 'voice'")
        characters.append(
            Character(id=cid, voice=voice, description=str(ch.get("description") or "").strip())
        )

    return Cast(name=declared_name, description=description, characters=characters)


def load_cast(name: str) -> Cast:
    """Load and validate a cast by name. Raises CastError on any failure."""
    safe = (name or "").strip().lower()
    if not _NAME_RE.match(safe):
        raise CastError(f"invalid cast name: {name!r}")
    path = CAST_DIR / f"{safe}.json"
    if not path.exists():
        raise CastError(f"cast '{safe}' not found at {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as exc:
        raise CastError(f"cast '{safe}': invalid JSON ({exc})") from exc
    return _validate(safe, payload)


def list_casts() -> List[CastSummary]:
    """Return summaries for every valid cast/<name>.json. Skips invalid files."""
    summaries: List[CastSummary] = []
    if not CAST_DIR.exists():
        return summaries
    for path in sorted(CAST_DIR.glob("*.json")):
        name = path.stem
        try:
            cast = load_cast(name)
        except CastError:
            continue
        summaries.append(
            CastSummary(
                name=cast.name,
                description=cast.description,
                character_count=len(cast.characters),
            )
        )
    return summaries


def format_cast_header(cast: Cast) -> str:
    """Build the prompt header injected before the user's customPrompt.

    Tells the model what character IDs are available and exactly how each
    output line must be formatted. Tuned to be small-model-tolerant
    (positive imperatives, short example).
    """
    lines = [
        "# CAST (dialogue mode is ACTIVE — read carefully)",
        "Your script is a short dialogue using ONLY the character IDs listed below.",
        "Each line of output starts with [CHARACTER_ID] in square brackets, followed",
        "by ONE sentence of dialogue. Use 4 to 7 lines total. Do not invent new IDs.",
        "",
        "Available characters:",
    ]
    for c in cast.characters:
        suffix = f" — {c.description}" if c.description else ""
        lines.append(f"  [{c.id}]{suffix}")
    lines.extend(
        [
            "",
            "Format example (use the same shape, write your own content):",
            "  [GRANDDAUGHTER] Grandma, I traveled back in time to meet you.",
            "  [GRANDMOTHER] My dear, is that really you?",
            "  [NARRATOR] One man, however, uses time travel differently.",
            "",
            "Output rules:",
            "- One [ID] tag per line. One sentence per line. Period at end of each line.",
            "- No preamble, no commentary, no markdown, no quotation marks wrapping the script.",
            "- The very first line starts with [.",
            "",
            "----- USER PROMPT BELOW -----",
            "",
        ]
    )
    return "\n".join(lines)
