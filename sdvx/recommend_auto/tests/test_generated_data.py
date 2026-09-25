from __future__ import annotations

import json
import unittest
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = APP_ROOT / "data" / "sdvx_songs.json"


class GeneratedDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        cls.songs = cls.document["songs"]
        cls.by_source = {
            (
                song["source"]["generation"],
                song["source"]["code"],
                song["source"]["difficultyKey"],
            ): song
            for song in cls.songs
        }

    def test_all_charts_have_verified_or_confirmed_fallback_difficulty(self):
        self.assertEqual(1906, len(self.songs))
        self.assertEqual(1903, sum(song["difficultySource"] == "wiki" for song in self.songs))
        fallback = {key for key, song in self.by_source.items() if song["difficultySource"] == "fallback"}
        self.assertEqual(
            {("06", "06360", "M"), ("06", "06354", "M"), ("05", "05220", "M")},
            fallback,
        )

    def test_same_title_charts_and_chart_type_override_are_exact(self):
        self.assertEqual(18.4, self.by_source[("06", "06104", "M")]["difficulty"])
        self.assertEqual(18.0, self.by_source[("06", "06641", "M")]["difficulty"])
        self.assertEqual("VVD", self.by_source[("01", "01103", "M")]["chartType"])
        self.assertEqual(17.0, self.by_source[("01", "01103", "M")]["difficulty"])

    def test_urls_are_unique_and_local_jackets_exist(self):
        urls = [song["url"] for song in self.songs]
        self.assertEqual(len(urls), len(set(urls)))
        for song in self.songs:
            if song["jacketPath"]:
                self.assertTrue((APP_ROOT / song["jacketPath"]).is_file(), song["jacketPath"])

    def test_existing_ui_contract_is_preserved(self):
        html = (APP_ROOT / "index.html").read_text(encoding="utf-8")
        script = (APP_ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn('<option value="3" selected>3</option>', html)
        self.assertIn("Dyscontrolled galaxy!!", script)
        self.assertIn("new URL(song.jacketPath, document.baseURI)", script)
        self.assertIn("context.drawImage(image", script)
        self.assertIn('row.querySelector(".song-meta")', script)
        self.assertIn('title.textContent = song.title', script)
        self.assertIn('`[${song.title}](${song.url}) [ ${chartLabel} ]`', script)
        self.assertNotIn("곡을 중복 없이 추천했습니다.", script)


if __name__ == "__main__":
    unittest.main()
