"""Browser acceptance: real navigation/layout, no-JS, reduced motion and media failure paths.

Video bytes are generated in the browser; only the remote transport is a fixture.
This proves player/CORS behavior, not the availability of a user's actual R2 objects.
"""
from __future__ import annotations

import argparse
import base64
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import tempfile
import time
from threading import Event, Thread

from playwright.sync_api import sync_playwright, expect
from build_site import ROOT, render_headers, render_page


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        path = Path(self.directory) / "_headers"
        if path.is_file():
            for line in path.read_text().splitlines():
                if line.strip().startswith("Content-Security-Policy:"):
                    self.send_header("Content-Security-Policy", line.strip().split(":", 1)[1].strip())
        super().end_headers()


def start_server(directory: Path, handler=Handler):
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(handler, directory=str(directory)))
    Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}"


def wait_truth(page, expression, timeout=10):
    # Playwright wait_for_function's in-page eval conflicts with the production CSP.
    # Poll a directly evaluated function without weakening that policy.
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if page.evaluate(expression):
            return
        page.wait_for_timeout(50)
    state = page.evaluate("() => ({ready:document.readyState,enhanced:document.documentElement.classList.contains('has-js'),tracks:[...document.querySelectorAll('track')].map(t=>({state:t.readyState,mode:t.track.mode,src:t.src})),videoError:document.querySelector('video')?.error?.code})")
    raise AssertionError(f"Timed out waiting for observable browser state: {expression}; last state={state}")


def run(output: Path | None = None):
    # Both pages use the production template and assets. Keep the layout fixture
    # independent of later user-supplied R2 links; media has a separate matrix below.
    temporary = tempfile.TemporaryDirectory(prefix="v8-site-layout-")
    fixture = Path(temporary.name)
    shutil.copytree(ROOT / "dist", fixture, dirs_exist_ok=True)
    empty_media = {"screenshots": dict.fromkeys(("workspace", "research", "creative", "phone"), ""), "video": dict.fromkeys(("src", "poster", "captionsZh", "captionsEn"), "")}
    for locale, relative in (("en", "index.html"), ("zh", "zh/index.html")):
        (fixture / relative).write_text(render_page(locale, empty_media), encoding="utf-8")
    (fixture / "_headers").write_text(render_headers(empty_media), encoding="utf-8")
    server, base = start_server(fixture)
    checks = 0
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            errors = []
            for locale, path in (("en", "/"), ("zh", "/zh/")):
                for width, height in ((1440, 1000), (390, 844), (320, 740), (768, 1024)):
                    page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.goto(base + path, wait_until="networkidle")
                    wait_truth(page, "() => document.fonts.status === 'loaded'")
                    expect(page.locator("h1")).to_be_visible()
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), f"Horizontal overflow: {locale} {width}"
                    expect(page.locator("video")).to_have_count(0)
                    expect(page.locator(".film-placeholder")).to_have_count(1)
                    if width == 1440:
                        page.mouse.move(200, 280)
                        wait_truth(page, "() => document.querySelector('.orbit-stage').style.transform.includes('rotateY(-')")
                        page.mouse.move(1250, 320)
                        wait_truth(page, "() => !document.querySelector('.orbit-stage').style.transform.includes('rotateY(-')")
                    for id in ("workspace", "creative", "research"):
                        page.locator(f"#tab-{id}").click()
                        expect(page.locator(f"#scenario-{id}")).to_be_visible()
                        expect(page.locator(".scenario:visible")).to_have_count(1)
                    if width == 1440:
                        surface = page.locator("#scenario-research .media-frame")
                        surface.scroll_into_view_if_needed()
                        rect = surface.bounding_box()
                        page.mouse.move(rect["x"] + rect["width"] * .75, rect["y"] + rect["height"] * .4)
                        wait_truth(page, "() => document.querySelector('#scenario-research .media-frame').style.transform.includes('rotateY(')")
                        wait_truth(page, "() => getComputedStyle(document.querySelector('#scenario-research .pointer-glow')).opacity === '1'")
                        page.mouse.move(10, 10)
                        wait_truth(page, "() => document.querySelector('#scenario-research .media-frame').style.transform === ''")
                    page.locator("#tab-research").focus()
                    page.keyboard.press("ArrowRight")
                    expect(page.locator("#tab-workspace")).to_be_focused()
                    expect(page.locator("#scenario-workspace")).to_be_visible()
                    page.keyboard.press("End")
                    expect(page.locator("#tab-creative")).to_be_focused()
                    page.reload(wait_until="networkidle")
                    expect(page.locator("#scenario-creative")).to_be_visible()
                    summary = page.locator("summary").first
                    summary.click()
                    expect(page.locator("details").first).to_have_attribute("open", "")
                    summary.click()
                    expect(page.locator("details").first).not_to_have_attribute("open", "")
                    if width < 761:
                        page.evaluate("scrollTo({top:0,behavior:'instant'})")
                        page.locator(".menu-button").click()
                        expect(page.locator(".navigation")).to_be_visible()
                        page.keyboard.press("Escape")
                        expect(page.locator(".menu-button")).to_be_focused()
                        expect(page.locator(".navigation")).not_to_be_visible()
                    page.locator(".motion-toggle").click()
                    assert page.evaluate("document.documentElement.classList.contains('motion-paused')")
                    expect(page.locator(".pointer-active")).to_have_count(0)
                    page.reload(wait_until="networkidle")
                    assert page.evaluate("document.documentElement.classList.contains('motion-paused')")
                    if output and width in (1440, 390):
                        output.mkdir(parents=True, exist_ok=True)
                        page.evaluate("scrollTo({top:0,behavior:'instant'})")
                        page.screenshot(path=str(output / f"{locale}-{width}-full.png"), full_page=True)
                        page.screenshot(path=str(output / f"{locale}-{width}-hero.png"))
                    page.close()
                    checks += 1
                nojs = browser.new_page(java_script_enabled=False, viewport={"width": 390, "height": 844})
                nojs.goto(base + path)
                expect(nojs.locator(".scenario:visible")).to_have_count(3)
                expect(nojs.locator(".navigation")).to_be_visible()
                nojs.locator("summary").first.click()
                expect(nojs.locator("details").first).to_have_attribute("open", "")
                assert nojs.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
                nojs.close()
                reduced = browser.new_page(reduced_motion="reduce")
                reduced.goto(base + path, wait_until="networkidle")
                assert reduced.locator(".orbit-art").evaluate("e => getComputedStyle(e).animationName") == "none"
                expect(reduced.locator(".motion-toggle")).to_be_disabled()
                expect(reduced.locator(".is-reveal-pending")).to_have_count(0)
                reduced.close()
                checks += 2
            touch = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
            touch.goto(base + "/zh/", wait_until="networkidle")
            touch.locator(".menu-button").tap()
            expect(touch.locator(".navigation")).to_be_visible()
            touch.locator(".navigation a").first.tap()
            touch.locator("#tab-creative").tap()
            expect(touch.locator("#scenario-creative")).to_be_visible()
            expect(touch.locator(".pointer-active")).to_have_count(0)
            touch.close()
            assert not errors, errors
            print(f"Passed {checks} bilingual viewport/no-JS/reduced-motion scenarios, mouse tilt/glow/reset and touch navigation.")
            media_acceptance(browser, output)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        temporary.cleanup()


def media_acceptance(browser, output):
    # Produce a real tiny video in an isolated browser, with no third-party fixture download.
    maker = browser.new_page()
    maker.goto("about:blank")
    encoded = maker.evaluate("""async () => {
      const canvas = document.createElement('canvas'); canvas.width=320; canvas.height=180;
      const ctx=canvas.getContext('2d'); const stream=canvas.captureStream(12);
      const recorder=new MediaRecorder(stream,{mimeType:'video/webm;codecs=vp8'});
      const chunks=[]; recorder.ondataavailable=e=>chunks.push(e.data);
      const done=new Promise(resolve=>recorder.onstop=resolve); recorder.start();
      for(let i=0;i<12;i++){ctx.fillStyle=i%2?'#ffb17c':'#20150f';ctx.fillRect(0,0,320,180);await new Promise(r=>setTimeout(r,90));}
      recorder.stop(); await done; stream.getTracks().forEach(t=>t.stop());
      const bytes=new Uint8Array(await new Blob(chunks).arrayBuffer());
      return btoa(String.fromCharCode(...bytes));
    }""")
    movie = base64.b64decode(encoded)
    png = maker.screenshot()
    maker.close()
    with tempfile.TemporaryDirectory(prefix="v8-site-media-") as temp:
        fixture = Path(temp)
        shutil.copytree(ROOT / "dist", fixture, dirs_exist_ok=True)
        (fixture / "assets/media").mkdir(parents=True, exist_ok=True)
        (fixture / "assets/media/workspace.png").write_bytes(png)
        media = {"screenshots": {"research": "", "workspace": "assets/media/workspace.png", "creative": "", "phone": ""}, "video": {"src": "https://media.example.test/launch.webm", "poster": "", "captionsZh": "https://media.example.test/zh.vtt", "captionsEn": ""}}
        (fixture / "zh/index.html").write_text(render_page("zh", media), encoding="utf-8")
        (fixture / "_headers").write_text(render_headers(media), encoding="utf-8")
        script_gate = Event()
        script_gate.set()
        class MediaHandler(Handler):
            def do_GET(self):
                if "/assets/site.js" in self.path:
                    script_gate.wait(timeout=15)
                super().do_GET()
        server, base = start_server(fixture, MediaHandler)
        try:
            for failure in (None, "video", "captions", "captions-early", "cors"):
                page = browser.new_page()
                requests = []
                def route_media(route):
                    requests.append(route.request.url)
                    is_video = route.request.url.endswith(".webm")
                    failed = (is_video and failure == "video") or (not is_video and failure in ("captions", "captions-early"))
                    headers = {"Accept-Ranges": "bytes"}
                    if failure != "cors":
                        headers["Access-Control-Allow-Origin"] = base
                    else:
                        # Playwright adds ACAO when omitted from fulfill; an explicit
                        # wrong origin exercises the browser's actual CORS rejection.
                        headers["Access-Control-Allow-Origin"] = "https://not-allowed.example.test"
                    route.fulfill(status=404 if failed else 200, headers=headers, content_type="video/webm" if is_video else "text/vtt", body=b"" if failed else movie if is_video else "WEBVTT\n\n00:00:00.000 --> 00:00:03.000\nBrowser caption fixture\n")
                page.route("https://media.example.test/**", route_media)
                if failure == "captions-early":
                    script_gate.clear()
                    try:
                        page.goto(base + "/zh/", wait_until="commit")
                        wait_truth(page, "() => document.querySelector('track')?.readyState === 3 && !document.documentElement.classList.contains('has-js')")
                    finally:
                        script_gate.set()
                    wait_truth(page, "() => document.documentElement.classList.contains('has-js')")
                    expect(page.locator(".caption-error")).to_be_visible()
                else:
                    page.goto(base + "/zh/", wait_until="networkidle")
                assert not any(url.endswith(".webm") for url in requests), "preload=none must not fetch video on page load"
                page.locator("video").scroll_into_view_if_needed()
                page.locator("video").evaluate("v=>{v.muted=true;v.play().catch(()=>{});}")
                if failure in ("video", "cors"):
                    expect(page.locator(".video-error")).to_be_visible()
                else:
                    wait_truth(page, "() => { const v=document.querySelector('video'); return v.currentTime > 0 && v.videoWidth > 0 && v.readyState >= 2 && !v.error; }")
                    if failure in ("captions", "captions-early"):
                        expect(page.locator(".caption-error")).to_be_visible()
                        expect(page.locator(".video-error")).not_to_be_visible()
                    else:
                        wait_truth(page, "() => Array.from(document.querySelector('video').textTracks[0].cues || []).some(c => c.text === 'Browser caption fixture')")
                        expect(page.locator(".video-error")).not_to_be_visible()
                        page.locator("#tab-workspace").click()
                        page.locator(".capture-open").click()
                        expect(page.locator("dialog")).to_be_visible()
                        page.keyboard.press("Escape")
                        expect(page.locator("dialog")).not_to_be_visible()
                        expect(page.locator(".capture-open")).to_be_focused()
                page.close()
            print("Passed decoded remote-video fixture, real caption text, video/caption 404 including pre-script caption failure, CORS rejection and screenshot dialog (not live R2 or range seeking).")
        finally:
            script_gate.set()
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screenshots", type=Path)
    args = parser.parse_args()
    run(args.screenshots)
