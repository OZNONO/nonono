from __future__ import annotations

import io
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path

from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from update_sdvx_data import (
    cache_jackets,
    deduplicate,
    normalize_url,
    optimize_jacket,
    parse_chart_type,
    parse_level_page,
    parse_wiki_level_page,
    merge_wiki_difficulties,
    script_content,
    validate_songs,
)


def song_record(level: int, suffix: str = "m") -> dict[str, object]:
    return {
        "title": f"Song {level}",
        "level": level,
        "difficulty": level,
        "difficultySource": "wiki",
        "chartType": "MXM",
        "url": f"https://sdvx.in/01/0100{level % 10}{suffix}.htm",
        "jacketPath": "",
        "sourceJacketUrl": "",
        "source": {"generation": "01", "code": f"0100{level % 10}", "difficultyKey": suffix.upper()},
    }


class ParserTests(unittest.TestCase):
    def test_parses_detailed_rating_only_inside_its_version_block(self):
        page = """
        <script>SDVXLG07S();</script><!--18.3-->
        <script src="/07/js/07001sort.js"></script><script>SORT07001M();</script><!--New Song-->
        <script>SDVXLG06_3S();</script>
        <script src="/06/js/06001sort.js"></script><script>SORT06001M();</script><!--Old Song-->
        """
        songs = parse_level_page(page, 18, "https://sdvx.in/sort/sort_18.htm")
        self.assertEqual(18.3, songs[0]["difficulty"])
        self.assertEqual(18, songs[1]["difficulty"])
        self.assertEqual("https://sdvx.in/07/jacket/07001m.png", songs[0]["sourceJacketUrl"])

    def test_parses_wiki_rating_and_chart_column(self):
        page = """
        <table><tr><td>dif</td><td>ind</td><td>NOV</td><td>ADV</td><td>EXH</td><td>MXM</td></tr>
        <tr><td></td><td></td><td>06001</td><td>Song 18</td><td>180</td>
        <td>06</td><td>12</td><td>15</td><td><b>18.4</b></td><td>-</td><td>2200</td><td></td></tr></table>
        """
        self.assertEqual(
            [{"title": "Song 18", "difficulty": 18.4, "chartType": "MXM", "reference": "06001"}],
            parse_wiki_level_page(page, 18.4),
        )

    def test_wiki_merge_keeps_only_confirmed_deleted_chart_as_fallback(self):
        matched = song_record(18)
        deleted = []
        for title, generation, code in (
            ("Realize", "06", "06360"),
            ("Redo", "06", "06354"),
            ("ふ・れ・ん・ど・し・た・い (WEREHEREMIX)", "05", "05220"),
        ):
            song = song_record(17)
            song["title"] = title
            song["source"] = {"generation": generation, "code": code, "difficultyKey": "M"}
            deleted.append(song)
        wiki = [{"title": "Song 18", "difficulty": 18.0, "chartType": "MXM", "reference": "06001"}]
        merge_wiki_difficulties([matched, *deleted], wiki)
        self.assertEqual((18.0, "wiki"), (matched["difficulty"], matched["difficultySource"]))
        self.assertTrue(all((song["difficulty"], song["difficultySource"]) == (17, "fallback") for song in deleted))

    def test_parses_exact_chart_type_instead_of_source_letter(self):
        script = 'function TBR03075M(){document.title="Everlasting Message [GRV]";}'
        self.assertEqual("GRV", parse_chart_type(script, "03075", "M"))

    def test_missing_and_placeholder_links_stay_empty(self):
        for value in ("", "#", "javascript:void(0)"):
            self.assertEqual("", normalize_url(value, "https://sdvx.in/sort/sort_17.htm"))

    def test_distinct_chart_urls_are_preserved(self):
        first = song_record(17, "m")
        second = song_record(17, "e")
        unique, removed = deduplicate([first, first.copy(), second])
        self.assertEqual(2, len(unique))
        self.assertEqual(1, removed)

    def test_validation_accepts_missing_optional_link_and_jacket(self):
        songs = [song_record(level) for level in (17, 18, 19, 20)]
        songs[0]["url"] = ""
        self.assertEqual(1, validate_songs(songs)[17])

    def test_jacket_is_resized_and_encoded_as_webp(self):
        source = Image.new("RGB", (608, 608), "magenta")
        buffer = io.BytesIO()
        source.save(buffer, "PNG")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "jacket.webp"
            optimize_jacket(buffer.getvalue(), target)
            with Image.open(target) as result:
                self.assertEqual("WEBP", result.format)
                self.assertEqual((256, 256), result.size)

    def test_cached_jacket_is_not_downloaded_again(self):
        song = song_record(18)
        song["sourceJacketUrl"] = "https://sdvx.in/01/jacket/01008m.png"
        filename = "01_01008_m.webp"
        with tempfile.TemporaryDirectory() as directory:
            jacket_dir = Path(directory) / "assets" / "jackets"
            jacket_dir.mkdir(parents=True)
            (jacket_dir / filename).write_bytes(b"cached")
            existing = {
                str(song["url"]): {
                    "sourceJacketUrl": song["sourceJacketUrl"],
                    "jacketPath": f"assets/jackets/{filename}",
                }
            }
            cache_jackets([song], existing, jacket_dir, fetcher=lambda _: self.fail("downloaded"))
            self.assertEqual(f"assets/jackets/{filename}", song["jacketPath"])

    def test_jacket_failure_keeps_song_with_fallback(self):
        song = song_record(19)
        song["sourceJacketUrl"] = "https://sdvx.in/missing.png"

        def fail_download(_):
            raise urllib.error.URLError("missing")

        with tempfile.TemporaryDirectory() as directory:
            cache_jackets([song], {}, Path(directory) / "assets" / "jackets", fetcher=fail_download)
        self.assertEqual("", song["jacketPath"])

    def test_file_fallback_contains_same_document(self):
        document = {"schemaVersion": 3, "songs": [{"title": "곡"}]}
        script = script_content(document)
        self.assertTrue(script.startswith("window.SDVX_SONG_DATA="))
        self.assertIn('"title":"곡"', script)


if __name__ == "__main__":
    unittest.main()
