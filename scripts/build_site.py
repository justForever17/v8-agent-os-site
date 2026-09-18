"""Build bilingual static pages and a publication directory with an explicit file list."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import struct
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
LOCALES = ("en", "zh")
RELEASE_TAG = "v8-os-v2026.09.17.3"
RELEASE_URL = f"https://github.com/justForever17/v8-agent-os/releases/tag/{RELEASE_TAG}"
STATIC_FILES = ("assets/styles.css", "assets/site.js", "assets/product-icon.png", "assets/orbit.svg", "assets/social-card.png", "assets/fonts/manrope-latin.woff2", "assets/fonts/OFL.txt", "robots.txt", "sitemap.xml", "404.html")


def text(value: str) -> str:
    return html.escape(value, quote=True)


def copy_text(value: str) -> str:
    # Only these presentational tags are supported in our own copy files.
    escaped = text(value)
    for tag in ("<br>", "<span>", "</span>"):
        escaped = escaped.replace(text(tag), tag)
    return escaped


def validate_media(media: dict) -> set[str]:
    expected = {"workspace", "research", "creative", "phone"}
    allowed_screenshots = expected | {"models", "projects", "plugins", "memory-overview", "memory-project", "memory-global", "terminal", "scene-atlas", "scene-camera", "pairing", "recovery"}
    if set(media) != {"screenshots", "video"} or not expected <= set(media["screenshots"]) <= allowed_screenshots:
        raise ValueError("media.json requires workspace/research/creative/phone screenshots; console, memory, scene, terminal, pairing and recovery captures are optional")
    if set(media["video"]) != {"src", "poster", "captionsZh", "captionsEn"}:
        raise ValueError("video requires src, poster, captionsZh and captionsEn")
    files: set[str] = set()
    for group, entries in media.items():
        for key, value in entries.items():
            if not isinstance(value, str):
                raise ValueError(f"{group}.{key} must be a path string or empty string")
            if not value:
                continue
            if any(ord(char) <= 32 for char in value):
                raise ValueError(f"{group}.{key}: media paths must not contain whitespace or control characters")
            allowed = {".webp", ".png", ".jpg", ".jpeg"}
            if group == "video" and key == "src":
                allowed = {".mp4", ".webm"}
            elif key.startswith("captions"):
                allowed = {".vtt"}
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc:
                if group != "video" or parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
                    raise ValueError(f"{group}.{key}: use a permanent public HTTPS media URL without credentials, query or fragment")
                if not re.fullmatch(r"[a-zA-Z0-9.-]+(?::443)?", parsed.netloc) or Path(parsed.path).suffix.lower() not in allowed:
                    raise ValueError(f"{group}.{key}: invalid public media URL or extension")
                continue
            path = ROOT / value
            if "\\" in value or not value.startswith("assets/media/") or any(part in (".", "..") for part in value.split("/")):
                raise ValueError(f"{group}.{key}: use a relative path under assets/media/")
            if not path.resolve().is_relative_to((ROOT / "assets/media").resolve()) or not path.is_file():
                raise ValueError(f"{group}.{key}: file missing or outside assets/media: {value}")
            if key.startswith("captions"):
                if not path.read_text(encoding="utf-8-sig").startswith("WEBVTT"):
                    raise ValueError(f"{key}: subtitle file must start with WEBVTT")
            if path.suffix.lower() not in allowed:
                raise ValueError(f"{group}.{key}: unsupported extension {path.suffix}")
            if path.stat().st_size > 25 * 1024 * 1024:
                raise ValueError(f"{group}.{key}: local file exceeds Pages 25 MiB limit; use an R2 public URL for video")
            files.add(value)
    if not media["video"]["src"] and any(media["video"].values()):
        raise ValueError("Configure video.src together with its poster/captions, or leave all video fields empty")
    return files


def image_dimensions(path: Path) -> tuple[int, int]:
    """Read intrinsic dimensions without an image runtime dependency."""
    with path.open("rb") as stream:
        header = stream.read(32)
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            return struct.unpack(">II", header[16:24])
        if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
            if header[12:16] == b"VP8X":
                return int.from_bytes(header[24:27], "little") + 1, int.from_bytes(header[27:30], "little") + 1
            if header[12:16] == b"VP8L" and header[20] == 0x2F:
                bits = int.from_bytes(header[21:25], "little")
                return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
            if header[12:16] == b"VP8 " and header[23:26] == b"\x9d\x01\x2a":
                width, height = struct.unpack("<HH", header[26:30])
                return width & 0x3FFF, height & 0x3FFF
        if header[:2] == b"\xff\xd8":
            stream.seek(2)
            while stream.read(1) == b"\xff":
                marker = stream.read(1)
                while marker == b"\xff":
                    marker = stream.read(1)
                if not marker or marker[0] in (0xDA, 0xD9):
                    break
                size = int.from_bytes(stream.read(2), "big")
                if size < 2:
                    break
                if marker[0] in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    _, height, width = struct.unpack(">BHH", stream.read(5))
                    return width, height
                stream.seek(size - 2, 1)
    raise ValueError(f"Cannot read image dimensions: {path.name}")


def capture_figure(source: str, alt: str, caption: str, c: dict, base: str, media_root: Path) -> str:
    width, height = image_dimensions(media_root / source)
    url = text(base + source)
    return f'<figure class="media-frame actual-capture"><button type="button" class="capture-open" data-image="{url}" aria-label="{text(c["enlargeImage"] + ": " + alt)}"><img src="{url}" alt="{text(alt)}" loading="lazy" decoding="async" width="{width}" height="{height}"><span class="capture-zoom" aria-hidden="true">{text(c["enlargeImage"])} ↗</span></button><figcaption>{text(caption)}</figcaption></figure>'


def media_url(value: str, base: str) -> str:
    parsed = urlsplit(value)
    return parsed._replace(scheme="https").geturl() if parsed.scheme == "https" else base + value


def render_headers(media: dict) -> str:
    origins = sorted({f"https://{urlsplit(value).netloc.lower()}" for value in media["video"].values() if urlsplit(value).scheme == "https"})
    media_sources = " ".join(["'self'", *origins])
    return ("/*\n"
            "  X-Content-Type-Options: nosniff\n"
            "  Referrer-Policy: strict-origin-when-cross-origin\n"
            "  X-Frame-Options: DENY\n"
            "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n"
            f"  Content-Security-Policy: default-src 'self'; script-src 'self' https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline'; img-src {media_sources} data:; media-src {media_sources}; font-src 'self'; connect-src {media_sources} https://cloudflareinsights.com; frame-ancestors 'none'; base-uri 'self'; form-action 'none'\n"
            "/assets/*\n  Cache-Control: public, max-age=3600\n")


def render_page(locale: str, media: dict, media_root: Path = ROOT) -> str:
    c = json.loads((ROOT / f"content/{locale}.json").read_text(encoding="utf-8"))
    base = "../" if locale == "zh" else "./"
    context = {key: copy_text(value) for key, value in c.items() if isinstance(value, str)}
    context.update({"releaseUrl": RELEASE_URL, "releaseVersion": RELEASE_TAG.removeprefix("v8-os-v")})
    context.update({"base": base, "home": "./", "otherLocale": "../" if locale == "zh" else "./zh/", "otherLang": "en" if locale == "zh" else "zh-CN", "canonical": "https://v8agentos.top/" + ("zh/" if locale == "zh" else ""), "close": "关闭图片" if locale == "zh" else "Close image", "quickstartUrl": "https://github.com/justForever17/v8-agent-os/blob/main/" + ("docs/V8_AGENT_OS_QUICK_START_ZH.md" if locale == "zh" else "README.md#quick-start")})
    for key, file in (("cssVersion", "assets/styles.css"), ("jsVersion", "assets/site.js"), ("orbitVersion", "assets/orbit.svg"), ("socialVersion", "assets/social-card.png")):
        context[key] = hashlib.sha256((ROOT / file).read_bytes()).hexdigest()[:10]
    tabs, panels = [], []
    for index, s in enumerate(c["scenarios"]):
        ident = s["id"]
        tabs.append(f'<a id="tab-{ident}" class="scenario-tab{" is-active" if index == 0 else ""}" href="#scenario-{ident}" data-tab="scenario-{ident}"><span>{text(s["number"])}</span>{text(s["label"])}<span class="tab-arrow" aria-hidden="true">↗</span></a>')
        source = media["screenshots"][ident]
        if source:
            caption = " · ".join(filter(None, (s.get("captureNote"), c["screenshotLabel"])))
            visual = capture_figure(source, s["alt"], caption, c, base, media_root)
        else:
            tags = "".join(f'<span><i aria-hidden="true">{n + 1:02}</i>{text(t)}</span>' for n, t in enumerate(s["tags"]))
            visual = f'''<figure class="media-frame concept-capture concept-{ident}"><div class="concept-toolbar"><span><i></i><i></i><i></i></span><span>V8 / {text(s["artifact"])}</span><span>↗</span></div><div class="concept-content"><div class="concept-prompt"><span class="prompt-mark" aria-hidden="true">✳</span><p>{text(s["prompt"])}</p></div><div class="concept-flow">{tags}</div><div class="concept-artifact"><div class="artifact-art" aria-hidden="true"><i></i><i></i><i></i></div><div><span class="artifact-label">{text(s["artifact"])}</span><p>{text(s["detail"])}</p><div class="artifact-lines" aria-hidden="true"><i></i><i></i><i></i></div></div><span class="artifact-arrow" aria-hidden="true">↗</span></div><p class="concept-result"><span aria-hidden="true">↳</span> {text(s["result"])}</p></div><figcaption>{text(c["concept"])}</figcaption></figure>'''
        panels.append(f'<article id="scenario-{ident}" data-tab-panel class="scenario{" is-active" if index == 0 else ""}" aria-labelledby="tab-{ident}">{visual}<div class="scenario-description"><h3>{text(s["title"])}</h3><p>{text(s["text"])}</p></div></article>')
    context["scenarioTabs"] = "".join(tabs)
    context["scenarioPanels"] = "".join(panels)
    scene_items = [item for item in c["sceneViews"] if media["screenshots"].get(item["id"])]
    scene_tabs, scene_panels = [], []
    for index, item in enumerate(scene_items):
        ident = item["id"]
        active = " is-active" if index == 0 else ""
        scene_tabs.append(f'<a class="scenario-tab{active}" id="tab-{ident}" href="#{ident}" data-tab="{ident}"><span>{index + 1:02}</span>{text(item["label"])}<span class="tab-arrow" aria-hidden="true">↗</span></a>')
        visual = capture_figure(media["screenshots"][ident], item["alt"], c["sceneCaption"], c, base, media_root)
        scene_panels.append(f'<article id="{ident}" data-tab-panel class="scene-panel{active}" aria-labelledby="tab-{ident}">{visual}<div class="scenario-description"><h3>{text(item["title"])}</h3><p>{text(item["text"])}</p></div></article>')
    context["sceneGallery"] = f'''<section id="creative-direction" class="scene-section section-shell" aria-labelledby="scene-title" data-tab-group>
      <div class="section-heading" data-reveal><div><p class="eyebrow">{text(c["sceneLabel"])}</p><h2 id="scene-title">{copy_text(c["sceneTitle"])}</h2></div><p class="section-description">{text(c["sceneText"])}</p></div>
      <div class="scenario-tabs scene-tabs" data-tab-list aria-label="{text(c["sceneTabsLabel"])}">{"".join(scene_tabs)}</div>{"".join(scene_panels)}<p class="fine-print scene-note">{text(c["sceneNote"])}</p>
    </section>''' if scene_items else ""
    controls = [item for item in c["controls"] if media["screenshots"].get(item["id"])]
    control_tabs, control_panels = [], []
    for index, item in enumerate(controls):
        ident = item["id"]
        active = " is-active" if index == 0 else ""
        control_tabs.append(f'<a class="scenario-tab{active}" id="tab-{ident}" href="#control-{ident}" data-tab="control-{ident}"><span>{text(item["number"])}</span>{text(item["label"])}<span class="tab-arrow" aria-hidden="true">↗</span></a>')
        visual = capture_figure(media["screenshots"][ident], item["alt"], c["screenshotLabel"], c, base, media_root)
        control_panels.append(f'<article id="control-{ident}" data-tab-panel class="control-panel{active}" aria-labelledby="tab-{ident}">{visual}<div class="scenario-description"><h3>{text(item["title"])}</h3><p>{text(item["text"])}</p></div></article>')
    context["controlsGallery"] = f'<div class="controls-gallery" data-tab-group><div class="controls-intro"><h3>{text(c["controlsLabel"])}</h3><p>{text(c["controlsText"])}</p></div><div class="scenario-tabs" data-tab-list aria-label="{text(c["controlsTabsLabel"])}">{"".join(control_tabs)}</div>{"".join(control_panels)}<p class="fine-print controls-note">{text(c["controlsNote"])}</p></div>' if controls else ""
    memory_items = [item for item in c["memoryViews"] if media["screenshots"].get(item["id"])]
    memory_tabs, memory_panels = [], []
    for index, item in enumerate(memory_items):
        ident = item["id"]
        active = " is-active" if index == 0 else ""
        memory_tabs.append(f'<a class="scenario-tab{active}" id="tab-{ident}" href="#{ident}" data-tab="{ident}"><span>{index + 1:02}</span>{text(item["label"])}<span class="tab-arrow" aria-hidden="true">↗</span></a>')
        visual = capture_figure(media["screenshots"][ident], item["alt"], c["memoryCaption"], c, base, media_root)
        memory_panels.append(f'<article id="{ident}" data-tab-panel class="memory-panel{active}" aria-labelledby="tab-{ident}">{visual}<div class="memory-description"><h3>{text(item["title"])}</h3><p>{text(item["text"])}</p></div></article>')
    context["memoryGallery"] = f'''<section id="memory" class="memory-section section-shell" aria-labelledby="memory-title" data-tab-group>
      <div class="section-heading" data-reveal><div><p class="eyebrow">{text(c["memoryLabel"])}</p><h2 id="memory-title">{copy_text(c["memoryTitle"])}</h2></div><p class="section-description">{text(c["memoryText"])}</p></div>
      <div class="memory-layout"><div class="memory-index"><div class="memory-tabs" data-tab-list aria-label="{text(c["memoryTabsLabel"])}">{"".join(memory_tabs)}</div><p class="fine-print">{text(c["memoryNote"])}</p></div><div class="memory-panels">{"".join(memory_panels)}</div></div>
    </section>''' if memory_items else ""
    detail_captures = {}
    for ident in ("terminal", "recovery", "pairing"):
        source = media["screenshots"].get(ident)
        if source:
            visual = capture_figure(source, c[f"{ident}Alt"], c[f"{ident}Caption"], c, base, media_root)
            detail_captures[ident] = f'<details class="capture-detail {ident}-evidence"><summary>{text(c[f"{ident}Reveal"])}<span aria-hidden="true">+</span></summary><div id="{ident}-capture">{visual}<p class="fine-print capture-note">{text(c[f"{ident}Note"])}</p></div></details>'
    context["pairingCapture"] = detail_captures.get("pairing", "")
    execution_captures = "".join(detail_captures[ident] for ident in ("terminal", "recovery") if ident in detail_captures)
    if execution_captures:
        points = "".join(f'<li><span>{index + 1:02}</span>{text(item)}</li>' for index, item in enumerate(c["terminalPoints"]))
        context["terminalSection"] = f'''<section id="continuity" class="terminal-section section-shell" aria-labelledby="terminal-title">
          <div class="terminal-copy" data-reveal><p class="eyebrow">{text(c["terminalLabel"])}</p><h2 id="terminal-title">{copy_text(c["terminalTitle"])}</h2><p class="section-description">{text(c["terminalText"])}</p></div>
          <div class="terminal-detail"><ul class="terminal-points">{points}</ul>{execution_captures}</div>
        </section>'''
    else:
        context["terminalSection"] = ""
    v = media["video"]
    if v["src"]:
        poster = f' poster="{text(media_url(v["poster"], base))}"' if v["poster"] else ""
        tracks = "".join(f'<track kind="captions" src="{text(media_url(v[key], base))}" srclang="{lang}" label="{label}"{" default" if lang == locale else ""}>' for key, lang, label in (("captionsZh", "zh", "中文"), ("captionsEn", "en", "English")) if v[key])
        mime = "video/mp4" if Path(urlsplit(v["src"]).path).suffix.lower() == ".mp4" else "video/webm"
        context["filmMedia"] = f'<h2 id="film-title" class="sr-only">{text(c["filmPlay"])}</h2><video controls playsinline preload="none" crossorigin="anonymous"{poster} aria-label="{text(c["filmPlay"])}"><source src="{text(media_url(v["src"], base))}" type="{mime}">{tracks}<a href="{text(media_url(v["src"], base))}">{text(c["filmPlay"])}</a></video><p class="video-error" role="status" hidden>{text(c["filmError"])}</p><p class="caption-error" role="status" hidden>{text(c["captionError"])}</p>'
    else:
        context["filmMedia"] = f'<div class="film-placeholder"><div class="film-orbit" aria-hidden="true"></div><div class="film-topline"><span>{text(c["filmLabel"])}</span><span>{text(c["filmStatus"])}</span></div><div class="film-center"><span class="film-emblem" aria-hidden="true">V8</span><h2 id="film-title">{copy_text(c["filmTitle"])}</h2></div><p class="film-coming"><span class="status-dot"></span>{text(c["filmSoon"])}</p></div>'
    context["principleRows"] = "".join(f'<article class="principle" data-reveal><span class="principle-number">{text(p["number"])}</span><div><h3>{text(p["title"])}</h3><p>{text(p["text"])}</p></div><span class="principle-word" aria-hidden="true">{text(p["word"])}</span></article>' for p in c["principles"])
    phone = media["screenshots"]["phone"]
    if phone:
        context["phoneMedia"] = '<div id="phone-capture" class="phone-capture">' + capture_figure(phone, c["phoneAlt"], c["phoneCaption"], c, base, media_root) + '</div>'
    else:
        context["phoneMedia"] = f'<figure class="phone-device"><div class="phone-status"><span>{text(c["phoneTime"])}</span><i></i><span aria-hidden="true">▰</span></div><div class="phone-body"><div class="phone-app"><img src="{base}assets/product-icon.png" alt="" width="28" height="28"><span>V8 Agent OS</span><span>＋</span></div><span class="phone-project">{text(c["phoneProject"])}</span><p class="phone-user-message">{text(c["phoneMessage"])}</p><div class="phone-response"><span aria-hidden="true">✳</span><p>{text(c["phoneReply"])}</p></div><div class="phone-mini-art" aria-hidden="true"><i></i><img src="{base}assets/product-icon.png" alt="" width="62" height="62"></div><div class="phone-composer" aria-hidden="true"><span>＋</span><i></i><span>↑</span></div></div><figcaption>{text(c["phoneConcept"])}</figcaption></figure>'
    context["ecosystemChips"] = "".join(f'<span><i aria-hidden="true">{symbol}</i>{text(item)}</span>' for symbol, item in zip(("◈", "⌘", "↗", "✳", "◇", "⤴"), c["ecosystemItems"]))
    context["communityTopics"] = "".join(f'<span>{text(item)}</span>' for item in c["communityLinks"])
    context["faqRows"] = "".join(f'<details><summary>{text(f["question"])}<span aria-hidden="true">+</span></summary><p>{text(f["answer"])}</p></details>' for f in c["faqs"])
    template = (ROOT / "templates/index.html").read_text(encoding="utf-8")
    return re.sub(r"\{\{(\w+)\}\}", lambda m: context[m[1]], template)


def build(check: bool = False) -> None:
    media = json.loads((ROOT / "assets/media.json").read_text(encoding="utf-8"))
    media_files = validate_media(media)
    contents = {"index.html": render_page("en", media), "zh/index.html": render_page("zh", media), "_headers": render_headers(media)}
    for relative, rendered in contents.items():
        path = ROOT / relative
        if check:
            if not path.is_file() or path.read_text(encoding="utf-8") != rendered:
                raise ValueError(f"Generated page out of date: {relative}; run python scripts/build_site.py")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf-8", newline="\n")
    for relative in STATIC_FILES:
        if not (ROOT / relative).is_file():
            raise ValueError(f"Missing public asset: {relative}")
    if not check:
        if DIST.is_symlink() or DIST.resolve().parent != ROOT.resolve():
            raise ValueError("Refusing to replace a dist directory outside the site")
        if DIST.exists():
            shutil.rmtree(DIST)
        DIST.mkdir()
        for relative in (*contents, *STATIC_FILES, *sorted(media_files)):
            destination = DIST / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
    print(f"{'Checked' if check else 'Built'} 2 locales; {len(media_files)} configured media files; public files only.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check committed HTML matches the sources without writing files")
    args = parser.parse_args()
    try:
        build(args.check)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f"Site build failed: {exc}\n")
