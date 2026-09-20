from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from update_sdvx_data import deduplicate, normalize_url, parse_level_page, validate_songs


class ParserTests(unittest.TestCase):
    def test_parses_script_declarations_and_preserves_distinct_charts(self):
        page = """
        <script src="/03/js/03245sort.js"></script><script>SORT03245M();</script><!--NEO GRAVITY-->
        <script src="/03/js/03245sort.js"></script><script>SORT03245E();</script><!--NEO GRAVITY-->
        """
        songs = parse_level_page(page, 18, "https://sdvx.in/sort/sort_18.htm")
        self.assertEqual(2, len(songs))
        self.assertEqual("https://sdvx.in/03/03245m.htm", songs[0]["url"])
        self.assertEqual("E", songs[1]["difficulty"])

    def test_missing_and_placeholder_links_stay_empty(self):
        for value in ("", "#", "javascript:void(0)"):
            self.assertEqual("", normalize_url(value, "https://sdvx.in/sort/sort_17.htm"))

    def test_only_exact_duplicates_are_removed(self):
        first = {"title": "Song", "level": 17, "difficulty": "M", "url": ""}
        second = {"title": "Song", "level": 17, "difficulty": "E", "url": ""}
        unique, removed = deduplicate([first, first.copy(), second])
        self.assertEqual(2, len(unique))
        self.assertEqual(1, removed)

    def test_validation_accepts_empty_urls(self):
        songs = [
            {"title": f"Song {level}", "level": level, "difficulty": "M", "url": ""}
            for level in (17, 18, 19, 20)
        ]
        self.assertEqual(1, validate_songs(songs)[17])


if __name__ == "__main__":
    unittest.main()
