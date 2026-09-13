"""Counterexamples for the public-media contract. No R2 account or network needed."""
import copy
import json
import unittest

from build_site import ROOT, render_headers, render_page, validate_media


class MediaContract(unittest.TestCase):
    def setUp(self):
        self.media = {"screenshots": dict.fromkeys(("workspace", "research", "creative", "phone"), ""), "video": dict.fromkeys(("src", "poster", "captionsZh", "captionsEn"), "")}

    def test_unconfigured_is_an_honest_non_player(self):
        validate_media(self.media)
        for locale in ("zh", "en"):
            page = render_page(locale, self.media)
            self.assertNotIn("<video", page)
            self.assertIn("film-placeholder", page)
            self.assertNotIn('src=""', page)

    def test_remote_url_case_captions_and_origin(self):
        self.media["video"] = {"src": "HTTPS://media.example.com/films/LAUNCH.MP4", "poster": "https://images.example.com/poster.webp", "captionsZh": "https://media.example.com/zh.vtt", "captionsEn": "https://media.example.com/en.vtt"}
        self.assertEqual(validate_media(self.media), set())
        page = render_page("zh", self.media)
        self.assertIn('src="https://media.example.com/films/LAUNCH.MP4" type="video/mp4"', page)
        self.assertIn('crossorigin="anonymous"', page)
        self.assertIn('srclang="zh" label="中文" default', page)
        self.assertNotIn('../https:', page)
        headers = render_headers(self.media)
        self.assertIn("media-src 'self' https://images.example.com https://media.example.com;", headers)
        self.assertNotIn("media-src *", headers)
        self.assertIn("script-src 'self';", headers)

    def test_private_and_ephemeral_urls_are_not_publishable(self):
        for value in ("http://media.example.com/a.mp4", "https://user:pass@media.example.com/a.mp4", "https://media.example.com/a.mp4?X-Amz-Signature=example", "https://media.example.com/a.mp4#token", "//media.example.com/a.mp4", "file:///C:/secret.mp4", "assets/media/../../private.mp4", "https://media.example.com/a.html", "https://media.example.com\n.evil/a.mp4"):
            with self.subTest(url=value):
                m = copy.deepcopy(self.media)
                m["video"]["src"] = value
                with self.assertRaises(ValueError):
                    validate_media(m)

    def test_missing_local_file_is_not_silently_published(self):
        self.media["screenshots"]["workspace"] = "assets/media/missing-workspace.webp"
        with self.assertRaises(ValueError):
            validate_media(self.media)

    def test_poster_without_video_is_a_configuration_error(self):
        self.media["video"]["poster"] = "https://media.example.com/poster.webp"
        with self.assertRaises(ValueError):
            validate_media(self.media)

    def test_language_content_schema_stays_aligned(self):
        en = json.loads((ROOT / "content/en.json").read_text(encoding="utf-8"))
        zh = json.loads((ROOT / "content/zh.json").read_text(encoding="utf-8"))
        self.assertEqual(en.keys(), zh.keys())
        self.assertEqual([s["id"] for s in en["scenarios"]], [s["id"] for s in zh["scenarios"]])
        self.assertEqual(len(en["faqs"]), len(zh["faqs"]))


if __name__ == "__main__":
    unittest.main()
