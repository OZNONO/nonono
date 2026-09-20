#!/usr/bin/env python3
"""Fetch SDVX level pages and atomically update the frontend JSON data."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

LEVELS = (17, 18, 19, 20)
BASE_URL = "https://sdvx.in"
PAGE_URLS = {level: f"{BASE_URL}/sort/sort_{level}.htm" for level in LEVELS}
ROBOTS_URL = f"{BASE_URL}/robots.txt"
USER_AGENT = "nonono-sdvx-data-updater/1.0 (+https://github.com/oznono/nonono)"

# The live pages document.write each song from a per-song script. The title is
# retained in the adjacent comment, so one level-page request contains all data.
SONG_PATTERN = re.compile(
    r'<script\s+src=["\']/(?P<generation>\d{2})/js/'
    r'(?P<code>\d{5})sort\.js["\']\s*></script>\s*'
    r'<script>\s*SORT(?P=code)(?P<difficulty>[A-Z])\(\);\s*</script>\s*'
    r'<!--(?P<title>.*?)-->',
    re.IGNORECASE | re.DOTALL,
)


def decode_body(body: bytes, declared_charset: str | None = None) -> str:
    """Decode a response without silently replacing Japanese song titles."""
    candidates = [declared_charset, "utf-8", "cp932", "shift_jis"]
    for charset in candidates:
        if not charset:
            continue
        try:
            return body.decode(charset)
        except (LookupError, UnicodeDecodeError):
            continue
    raise ValueError("response could not be decoded as UTF-8 or Japanese text")


def fetch_text(url: str, timeout: int = 30) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset()
        return decode_body(response.read(), charset)


def normalize_url(value: str, source_url: str) -> str:
    """Return a safe absolute URL, preserving missing/placeholder links as ''."""
    candidate = html.unescape(value).strip()
    if not candidate or candidate == "#" or candidate.lower().startswith("javascript:"):
        return ""
    absolute = urllib.parse.urljoin(source_url, candidate)
    parsed = urllib.parse.urlparse(absolute)
    return absolute if parsed.scheme in {"http", "https"} and parsed.netloc else ""


def parse_level_page(page: str, level: int, source_url: str) -> list[dict[str, object]]:
    songs: list[dict[str, object]] = []
    for match in SONG_PATTERN.finditer(page):
        title = html.unescape(match.group("title")).strip()
        if not title:
            continue
        generation = match.group("generation")
        code = match.group("code")
        difficulty = match.group("difficulty").upper()
        derived_path = f"/{generation}/{code}{difficulty.lower()}.htm"
        songs.append(
            {
                "title": title,
                "level": level,
                "difficulty": difficulty,
                "url": normalize_url(derived_path, source_url),
            }
        )
    return songs


def deduplicate(songs: list[dict[str, object]]) -> tuple[list[dict[str, object]], int]:
    unique: list[dict[str, object]] = []
    seen: set[tuple[object, ...]] = set()
    for song in songs:
        key = (song["title"], song["level"], song["difficulty"], song["url"])
        if key not in seen:
            seen.add(key)
            unique.append(song)
    return unique, len(songs) - len(unique)


def check_robots(fetcher=fetch_text) -> None:
    robots_text = fetcher(ROBOTS_URL)
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(ROBOTS_URL)
    parser.parse(robots_text.splitlines())
    denied = [url for url in PAGE_URLS.values() if not parser.can_fetch(USER_AGENT, url)]
    if denied:
        raise PermissionError(f"robots.txt disallows: {', '.join(denied)}")
    print("robots.txt permits the four level pages")


def collect(fetcher=fetch_text, check_policy: bool = True) -> list[dict[str, object]]:
    if check_policy:
        check_robots(fetcher)

    collected: list[dict[str, object]] = []
    for level, url in PAGE_URLS.items():
        page = fetcher(url)
        songs = parse_level_page(page, level, url)
        if not songs:
            raise ValueError(f"level {level}: no songs parsed; refusing to replace existing data")
        print(f"level {level}: {len(songs)} songs")
        collected.extend(songs)

    unique, removed = deduplicate(collected)
    if removed:
        print(f"removed {removed} exact duplicate record(s)")
    return unique


def validate_songs(songs: list[dict[str, object]]) -> Counter:
    if not isinstance(songs, list) or not songs:
        raise ValueError("songs must be a non-empty list")
    counts: Counter = Counter()
    seen: set[tuple[object, ...]] = set()
    for index, song in enumerate(songs):
        if not isinstance(song, dict):
            raise ValueError(f"song {index} is not an object")
        title = song.get("title")
        level = song.get("level")
        difficulty = song.get("difficulty")
        url = song.get("url")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"song {index} has no title")
        if level not in LEVELS:
            raise ValueError(f"song {index} has invalid level: {level!r}")
        if not isinstance(difficulty, str) or not difficulty:
            raise ValueError(f"song {index} has no difficulty")
        if not isinstance(url, str):
            raise ValueError(f"song {index} has a non-string URL")
        if url and urllib.parse.urlparse(url).scheme not in {"http", "https"}:
            raise ValueError(f"song {index} has an unsafe URL: {url!r}")
        key = (title, level, difficulty, url)
        if key in seen:
            raise ValueError(f"duplicate song record: {key!r}")
        seen.add(key)
        counts[level] += 1
    missing_levels = set(LEVELS) - set(counts)
    if missing_levels:
        raise ValueError(f"missing levels: {sorted(missing_levels)}")
    return counts


def make_document(songs: list[dict[str, object]]) -> dict[str, object]:
    counts = validate_songs(songs)
    return {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": [PAGE_URLS[level] for level in LEVELS],
        "counts": {
            "total": len(songs),
            "byLevel": {str(level): counts[level] for level in LEVELS},
        },
        "songs": songs,
    }


def read_existing(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        existing = json.load(handle)
    if not isinstance(existing, dict) or not isinstance(existing.get("songs"), list):
        raise ValueError(f"existing data has an invalid shape: {path}")
    validate_songs(existing["songs"])
    return existing


def atomic_write_json(path: Path, document: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(document, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    default_output = Path(__file__).resolve().parents[1] / "data" / "sdvx_songs.json"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--skip-robots", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    try:
        songs = collect(check_policy=not args.skip_robots)
        existing = read_existing(args.output)
        if existing is not None and existing["songs"] == songs:
            counts = validate_songs(songs)
            print(f"no data changes: {len(songs)} total; " + ", ".join(
                f"L{level}={counts[level]}" for level in LEVELS
            ))
            return 0
        document = make_document(songs)
        atomic_write_json(args.output, document)
        counts = document["counts"]["byLevel"]
        print(f"updated {args.output}: {document['counts']['total']} total; " + ", ".join(
            f"L{level}={counts[str(level)]}" for level in LEVELS
        ))
        return 0
    except (OSError, ValueError, PermissionError, urllib.error.URLError) as error:
        print(f"update failed; existing JSON was not replaced: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
