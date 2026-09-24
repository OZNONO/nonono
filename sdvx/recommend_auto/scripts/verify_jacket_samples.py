#!/usr/bin/env python3
"""Verify three local jacket files per level against live source definitions."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image

from update_sdvx_data import BASE_URL, LEVELS, fetch_text, normalize_url


def verify_song(song: dict[str, object], app_root: Path) -> None:
    source = song["source"]
    generation = str(source["generation"])
    code = str(source["code"])
    key = str(source["difficultyKey"])
    data_url = f"{BASE_URL}/{generation}/js/{code}data.js"
    script = fetch_text(data_url)
    jacket_pattern = re.compile(
        rf'var\s+JK{code}{key}\s*=\s*"<img\s+src=(?P<path>[^\s>]+)'
    )
    match = jacket_pattern.search(script)
    if not match:
        raise ValueError(f"jacket variable missing: {data_url}")
    actual_url = normalize_url(match.group("path").strip('"\''), data_url)
    if actual_url != song["sourceJacketUrl"]:
        raise ValueError(f"source mismatch for {song['title']}: {actual_url}")

    local_path = app_root / Path(*Path(str(song["jacketPath"])).parts)
    with Image.open(local_path) as image:
        if image.format != "WEBP" or image.size != (256, 256):
            raise ValueError(f"invalid local jacket: {local_path} ({image.format}, {image.size})")
    print(f"L{song['level']} {song['title']} -> {song['chartType']} {song['difficulty']} -> {local_path.name}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    app_root = Path(__file__).resolve().parents[1]
    document = json.loads((app_root / "data" / "sdvx_songs.json").read_text(encoding="utf-8"))
    for level in LEVELS:
        songs = [song for song in document["songs"] if song["level"] == level]
        for index in sorted({0, len(songs) // 2, len(songs) - 1}):
            verify_song(songs[index], app_root)
    print("verified 3 live-to-local jacket mappings for each level")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
