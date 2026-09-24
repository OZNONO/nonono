#!/usr/bin/env python3
"""Validate the generated SDVX JSON and print its counts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from update_sdvx_data import LEVELS, validate_songs


def main() -> int:
    default_path = Path(__file__).resolve().parents[1] / "data" / "sdvx_songs.json"
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_path
    with path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document, dict) or not isinstance(document.get("songs"), list):
        raise ValueError("root must be an object containing a songs array")
    app_root = path.resolve().parents[1]
    counts = validate_songs(document["songs"], app_root)
    expected = document.get("counts", {})
    actual_by_level = {str(level): counts[level] for level in LEVELS}
    if expected != {"total": len(document["songs"]), "byLevel": actual_by_level}:
        raise ValueError("stored counts do not match song records")
    script_path = path.with_suffix(".js")
    prefix = "window.SDVX_SONG_DATA="
    script = script_path.read_text(encoding="utf-8")
    if not script.startswith(prefix) or not script.endswith(";\n"):
        raise ValueError("file fallback script has an invalid wrapper")
    fallback_document = json.loads(script[len(prefix):-2])
    if fallback_document != document:
        raise ValueError("file fallback script does not match JSON")
    print(f"valid JSON: {len(document['songs'])} songs; " + ", ".join(
        f"L{level}={counts[level]}" for level in LEVELS
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
