#!/usr/bin/env python3
"""Update SDVX chart data and a local, compressed jacket cache.

The first run downloads one sort script and one jacket per uncached chart. Later
runs reuse chart metadata and existing WebP files, so the normal weekly request
count returns to robots.txt plus one request for each of the four level pages.
"""

from __future__ import annotations

import argparse
import html
import io
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from PIL import Image, ImageOps

LEVELS = (17, 18, 19, 20)
BASE_URL = "https://sdvx.in"
PAGE_URLS = {level: f"{BASE_URL}/sort/sort_{level}.htm" for level in LEVELS}
ROBOTS_URL = f"{BASE_URL}/robots.txt"
USER_AGENT = "nonono-sdvx-data-updater/2.0 (+https://github.com/oznono/nonono)"
MAX_WORKERS = 6
JACKET_SIZE = (256, 256)
JACKET_QUALITY = 78

SONG_PATTERN = re.compile(
    r'<script\s+src=["\']/(?P<generation>\d{2})/js/'
    r'(?P<code>\d{5})sort\.js["\']\s*></script>\s*'
    r'<script>\s*SORT(?P=code)(?P<sourceDifficulty>[A-Z])\(\);\s*</script>\s*'
    r'<!--(?P<title>.*?)-->',
    re.IGNORECASE | re.DOTALL,
)
VALID_CHART_TYPE = re.compile(r"^[A-Z][A-Z0-9]{2,7}$")


def decode_body(body: bytes, declared_charset: str | None = None) -> str:
    for charset in (declared_charset, "utf-8-sig", "utf-8", "cp932", "shift_jis"):
        if not charset:
            continue
        try:
            return body.decode(charset)
        except (LookupError, UnicodeDecodeError):
            continue
    raise ValueError("response could not be decoded as UTF-8 or Japanese text")


def request_bytes(url: str, timeout: int = 30) -> tuple[bytes, str | None]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read(), response.headers.get_content_charset()


def fetch_text(url: str, timeout: int = 30) -> str:
    body, charset = request_bytes(url, timeout)
    return decode_body(body, charset)


def normalize_url(value: str, source_url: str) -> str:
    candidate = html.unescape(value).strip()
    if not candidate or candidate == "#" or candidate.lower().startswith("javascript:"):
        return ""
    absolute = urllib.parse.urljoin(source_url, candidate)
    parsed = urllib.parse.urlparse(absolute)
    return absolute if parsed.scheme in {"http", "https"} and parsed.netloc else ""


def internal_difficulty_before(page: str, song_start: int, level: int) -> float | int:
    """Use an explicit rating only within its SDVX version block."""
    block_start = page.rfind("<script>SDVXLG", 0, song_start)
    prefix = page[max(block_start, 0):song_start]
    ratings = re.findall(rf"<!--({level}(?:\.\d+)?)-->", prefix)
    if not ratings:
        return level
    value = float(ratings[-1])
    return int(value) if value.is_integer() else value


def parse_level_page(page: str, level: int, source_url: str) -> list[dict[str, object]]:
    songs: list[dict[str, object]] = []
    for match in SONG_PATTERN.finditer(page):
        title = html.unescape(match.group("title")).strip()
        if not title:
            continue
        generation = match.group("generation")
        code = match.group("code")
        source_difficulty = match.group("sourceDifficulty").upper()
        suffix = source_difficulty.lower()
        songs.append(
            {
                "title": title,
                "level": level,
                "difficulty": internal_difficulty_before(page, match.start(), level),
                "chartType": "",
                "url": normalize_url(f"/{generation}/{code}{suffix}.htm", source_url),
                "jacketPath": "",
                "sourceJacketUrl": normalize_url(
                    f"/{generation}/jacket/{code}{suffix}.png", source_url
                ),
                "source": {
                    "generation": generation,
                    "code": code,
                    "difficultyKey": source_difficulty,
                },
            }
        )
    return songs


def parse_chart_type(script: str, code: str, difficulty_key: str) -> str:
    pattern = re.compile(
        rf'function\s+TBR{re.escape(code)}{re.escape(difficulty_key)}\(\)'
        rf'\{{document\.title=.*?\[(?P<chart>[A-Z][A-Z0-9]{{2,7}})\]"?;\}}'
    )
    match = pattern.search(script)
    return match.group("chart") if match else ""


def deduplicate(songs: list[dict[str, object]]) -> tuple[list[dict[str, object]], int]:
    unique: list[dict[str, object]] = []
    seen: set[str] = set()
    for song in songs:
        key = str(song["url"]) or json.dumps(
            [song["title"], song["level"], song["source"]], ensure_ascii=False, sort_keys=True
        )
        if key not in seen:
            seen.add(key)
            unique.append(song)
    return unique, len(songs) - len(unique)


def check_robots(fetcher=fetch_text) -> None:
    robots_text = fetcher(ROBOTS_URL)
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(ROBOTS_URL)
    parser.parse(robots_text.splitlines())
    targets = list(PAGE_URLS.values()) + [f"{BASE_URL}/01/jacket/example.png"]
    denied = [url for url in targets if not parser.can_fetch(USER_AGENT, url)]
    if denied:
        raise PermissionError(f"robots.txt disallows required paths: {', '.join(denied)}")
    print("robots.txt permits level pages and jacket paths")


def read_existing(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        existing = json.load(handle)
    if not isinstance(existing, dict) or not isinstance(existing.get("songs"), list):
        raise ValueError(f"existing data has an invalid shape: {path}")
    return existing


def collect_pages(fetcher=fetch_text, check_policy: bool = True) -> list[dict[str, object]]:
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


def enrich_chart_types(
    songs: list[dict[str, object]], existing_by_url: dict[str, dict[str, object]], fetcher=fetch_text
) -> None:
    pending: dict[str, list[dict[str, object]]] = defaultdict(list)
    for song in songs:
        cached = existing_by_url.get(str(song["url"]), {})
        cached_type = cached.get("chartType")
        if isinstance(cached_type, str) and VALID_CHART_TYPE.fullmatch(cached_type):
            song["chartType"] = cached_type
            continue
        source = song["source"]
        sort_url = f"{BASE_URL}/{source['generation']}/js/{source['code']}sort.js"
        pending[sort_url].append(song)

    if not pending:
        print("chart types: all reused from existing data")
        return

    print(f"chart types: fetching {len(pending)} uncached song script(s)")
    failures = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetcher, url): (url, grouped) for url, grouped in pending.items()}
        for future in as_completed(futures):
            url, grouped = futures[future]
            try:
                script = future.result()
                for song in grouped:
                    source = song["source"]
                    song["chartType"] = parse_chart_type(
                        script, str(source["code"]), str(source["difficultyKey"])
                    )
                    if not song["chartType"]:
                        failures += 1
            except Exception as error:
                failures += len(grouped)
                print(f"warning: chart type unavailable from {url}: {error}", file=sys.stderr)
    if failures:
        print(f"warning: {failures} chart type(s) remain unavailable", file=sys.stderr)


def jacket_filename(song: dict[str, object]) -> str:
    source = song["source"]
    return f"{source['generation']}_{source['code']}_{str(source['difficultyKey']).lower()}.webp"


def optimize_jacket(image_bytes: bytes, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(io.BytesIO(image_bytes)) as source:
        source.load()
        image = ImageOps.exif_transpose(source).convert("RGB")
        image = ImageOps.fit(image, JACKET_SIZE, method=Image.Resampling.LANCZOS)
        descriptor, temporary_name = tempfile.mkstemp(
            dir=target.parent, prefix=f".{target.name}.", suffix=".tmp"
        )
        os.close(descriptor)
        try:
            image.save(temporary_name, "WEBP", quality=JACKET_QUALITY, method=6)
            os.replace(temporary_name, target)
        except Exception:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise


def cache_jackets(
    songs: list[dict[str, object]],
    existing_by_url: dict[str, dict[str, object]],
    jacket_dir: Path,
    fetcher=request_bytes,
) -> None:
    pending: list[tuple[dict[str, object], Path]] = []
    for song in songs:
        filename = jacket_filename(song)
        target = jacket_dir / filename
        local_path = PurePosixPath("assets", "jackets", filename).as_posix()
        cached = existing_by_url.get(str(song["url"]), {})
        if (
            target.is_file()
            and cached.get("sourceJacketUrl") == song["sourceJacketUrl"]
            and cached.get("jacketPath") == local_path
        ):
            song["jacketPath"] = local_path
        elif target.is_file() and not cached:
            song["jacketPath"] = local_path
        else:
            pending.append((song, target))

    print(f"jackets: {len(songs) - len(pending)} cached, {len(pending)} to download")
    if not pending:
        return

    failures = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetcher, str(song["sourceJacketUrl"])): (song, target)
            for song, target in pending
            if song["sourceJacketUrl"]
        }
        for future in as_completed(futures):
            song, target = futures[future]
            local_path = PurePosixPath("assets", "jackets", target.name).as_posix()
            try:
                body, _ = future.result()
                optimize_jacket(body, target)
                song["jacketPath"] = local_path
            except Exception as error:
                failures += 1
                cached_path = existing_by_url.get(str(song["url"]), {}).get("jacketPath", "")
                cached_target = jacket_dir.parents[1] / str(cached_path) if cached_path else None
                if cached_target and cached_target.is_file():
                    song["jacketPath"] = str(cached_path)
                print(f"warning: jacket unavailable for {song['title']}: {error}", file=sys.stderr)
    if failures:
        print(f"warning: {failures} jacket(s) use an existing image or fallback", file=sys.stderr)


def validate_songs(songs: list[dict[str, object]], app_root: Path | None = None) -> Counter:
    if not isinstance(songs, list) or not songs:
        raise ValueError("songs must be a non-empty list")
    counts: Counter = Counter()
    seen: set[str] = set()
    for index, song in enumerate(songs):
        title = song.get("title")
        level = song.get("level")
        difficulty = song.get("difficulty")
        chart_type = song.get("chartType")
        url = song.get("url")
        jacket_path = song.get("jacketPath")
        source_jacket_url = song.get("sourceJacketUrl")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"song {index} has no title")
        if level not in LEVELS:
            raise ValueError(f"song {index} has invalid level: {level!r}")
        if not isinstance(difficulty, (int, float)) or not level <= difficulty < level + 1:
            raise ValueError(f"song {index} has invalid detailed difficulty: {difficulty!r}")
        if not isinstance(chart_type, str) or (chart_type and not VALID_CHART_TYPE.fullmatch(chart_type)):
            raise ValueError(f"song {index} has invalid chart type: {chart_type!r}")
        for field, value in (("url", url), ("sourceJacketUrl", source_jacket_url)):
            if not isinstance(value, str):
                raise ValueError(f"song {index} has a non-string {field}")
            if value and urllib.parse.urlparse(value).scheme not in {"http", "https"}:
                raise ValueError(f"song {index} has an unsafe {field}: {value!r}")
        if not isinstance(jacket_path, str):
            raise ValueError(f"song {index} has a non-string jacketPath")
        if jacket_path:
            pure_path = PurePosixPath(jacket_path)
            if pure_path.is_absolute() or ".." in pure_path.parts or pure_path.parts[:2] != ("assets", "jackets"):
                raise ValueError(f"song {index} has an unsafe jacketPath: {jacket_path!r}")
            if app_root and not (app_root / Path(*pure_path.parts)).is_file():
                raise ValueError(f"song {index} references a missing jacket: {jacket_path}")
        key = str(url) or json.dumps([title, level, song.get("source")], sort_keys=True)
        if key in seen:
            raise ValueError(f"duplicate chart record: {key}")
        seen.add(key)
        counts[level] += 1
    missing_levels = set(LEVELS) - set(counts)
    if missing_levels:
        raise ValueError(f"missing levels: {sorted(missing_levels)}")
    return counts


def make_document(songs: list[dict[str, object]], app_root: Path) -> dict[str, object]:
    counts = validate_songs(songs, app_root)
    return {
        "schemaVersion": 3,
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": [PAGE_URLS[level] for level in LEVELS],
        "counts": {
            "total": len(songs),
            "byLevel": {str(level): counts[level] for level in LEVELS},
        },
        "songs": songs,
    }


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def json_content(document: dict[str, object]) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def script_content(document: dict[str, object]) -> str:
    payload = json.dumps(document, ensure_ascii=False, separators=(",", ":"))
    return f"window.SDVX_SONG_DATA={payload};\n"


def write_documents(json_path: Path, document: dict[str, object]) -> None:
    script_path = json_path.with_suffix(".js")
    # JSON is canonical and replaced last. A supporting-file failure therefore
    # cannot overwrite the last valid JSON.
    atomic_write_text(script_path, script_content(document))
    atomic_write_text(json_path, json_content(document))


def comparable_songs(songs: list[dict[str, object]]) -> list[dict[str, object]]:
    return songs


def main() -> int:
    app_root = Path(__file__).resolve().parents[1]
    default_output = app_root / "data" / "sdvx_songs.json"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--skip-robots", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    try:
        existing = read_existing(args.output)
        existing_by_url = {
            str(song.get("url")): song
            for song in (existing or {}).get("songs", [])
            if isinstance(song, dict) and song.get("url")
        }
        songs = collect_pages(check_policy=not args.skip_robots)
        enrich_chart_types(songs, existing_by_url)
        cache_jackets(songs, existing_by_url, app_root / "assets" / "jackets")
        validate_songs(songs, app_root)

        if existing is not None and comparable_songs(existing.get("songs", [])) == comparable_songs(songs):
            expected_script = script_content(existing)
            script_path = args.output.with_suffix(".js")
            if not script_path.exists() or script_path.read_text(encoding="utf-8") != expected_script:
                atomic_write_text(script_path, expected_script)
                print(f"restored file fallback: {script_path}")
            counts = validate_songs(songs, app_root)
            print(f"no data changes: {len(songs)} total; " + ", ".join(
                f"L{level}={counts[level]}" for level in LEVELS
            ))
            return 0

        document = make_document(songs, app_root)
        write_documents(args.output, document)
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
