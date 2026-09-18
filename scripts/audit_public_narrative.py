"""Check public navigation, generated files and publication boundaries, not a fixed layout."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from build_site import ROOT, STATIC_FILES, RELEASE_URL, build, validate_media


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.images = []
        self.headings = 0
        self.html_lang = ""
        self.videos = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "html":
            self.html_lang = a.get("lang", "")
        if tag == "h1":
            self.headings += 1
        if tag == "video":
            self.videos.append(a)
        if tag == "img":
            self.images.append(a)
        for key in ("href", "src", "poster"):
            if key in a:
                self.links.append(a[key])
        if tag == "a" and a.get("target") == "_blank":
            assert "noopener" in a.get("rel", ""), "External tab missing noopener"


def audit():
    build(check=True)
    media = json.loads((ROOT / "assets/media.json").read_text(encoding="utf-8"))
    for relative, language in (("index.html", "en"), ("zh/index.html", "zh-CN")):
        source = (ROOT / relative).read_text(encoding="utf-8")
        page = Page()
        page.feed(source)
        assert page.html_lang == language and page.headings == 1, f"{relative}: language or heading structure"
        assert len(page.ids) == len(set(page.ids)), f"{relative}: duplicate IDs"
        assert not re.search(r"\{\{\w+\}\}", source), f"{relative}: unrendered template"
        for image in page.images:
            assert "alt" in image, f"{relative}: image needs alt text"
        for url in page.links:
            assert url, f"{relative}: empty resource URL"
            parts = urlsplit(url)
            if parts.scheme or parts.netloc:
                assert parts.scheme == "https", f"{relative}: public links must be HTTPS"
                continue
            if not parts.path and parts.fragment:
                assert unquote(parts.fragment) in page.ids, f"{relative}: broken anchor {url}"
                continue
            target = (ROOT / relative).parent / unquote(parts.path)
            if parts.path.endswith("/"):
                target /= "index.html"
            assert target.is_file(), f"{relative}: missing local target {url}"
        assert "https://github.com/justForever17/v8-agent-os/discussions" in page.links
        assert RELEASE_URL in page.links
        assert "https://github.com/justForever17/v8-agent-os/releases/latest" not in page.links, "Preview downloads must target the verified release, not GitHub's stable-only latest redirect"
        if not media["video"]["src"]:
            assert not page.videos and "film-placeholder" in source, "Empty video must not present a broken player"
        else:
            assert len(page.videos) == 1
            v = page.videos[0]
            assert v.get("preload") == "none" and "autoplay" not in v and "controls" in v
            assert v.get("crossorigin") == "anonymous", "Remote captions require anonymous CORS"
        assert ".codex-tmp" not in source and "portal-private" not in source, "Private material linked from public HTML"
    if (ROOT / "dist").is_dir():
        expected = {"index.html", "zh/index.html", "_headers", *STATIC_FILES, *validate_media(media)}
        actual = {p.relative_to(ROOT / "dist").as_posix() for p in (ROOT / "dist").rglob("*") if p.is_file()}
        assert actual == expected, f"Publication file list differs: extra={actual - expected}; missing={expected - actual}"
    print("Public site audit passed: navigation, media states, bilingual output and publication file list.")


if __name__ == "__main__":
    try:
        audit()
    except (AssertionError, ValueError, OSError) as exc:
        print(f"Public site audit failed: {exc}", file=sys.stderr)
        sys.exit(1)
