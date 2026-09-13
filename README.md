# V8 Agent OS — Product portal

**Big ideas. Your move.** The bilingual product portal for [V8 Agent OS](https://github.com/justForever17/v8-agent-os), a personal AI workspace for research, development and creative work.

[Website](https://v8agentos.top/) · [中文](README-ZH.md) · [Community](https://github.com/justForever17/v8-agent-os/discussions) · [Download Preview](https://github.com/justForever17/v8-agent-os/releases/latest)

## Develop

Python 3.12+ builds the site using the standard library. No frontend framework or runtime CDN is required.

```sh
python scripts/build_site.py
python scripts/audit_public_narrative.py
python scripts/test_media.py
python -m http.server 8789 --directory dist
```

Open `http://127.0.0.1:8789/` or `/zh/`.

## Sources

- `content/en.json` and `content/zh.json`: language-specific copy.
- `templates/index.html`: shared semantic page structure.
- `assets/styles.css` and `assets/site.js`: visual design and progressive enhancement.
- `assets/media.json`: scenario screenshot paths, optional console captures (`models`, `projects`, `plugins`), and public R2 video, poster and caption URLs.
- `scripts/build_site.py`: generates the committed `index.html`, `zh/index.html`, and `_headers`; assembles a public-only `dist` directory.

Edit the sources, then rebuild. `python scripts/build_site.py --check` verifies the committed output is current. The committed root pages remain compatible with the existing Cloudflare Pages Git integration. When configuring a build, use `python scripts/build_site.py` and output directory `dist`.

Empty media settings render clearly identified concept illustrations and a coming-soon film section. Screenshots accept local paths under `assets/media/`. Film settings accept local files or permanent public HTTPS URLs without credentials, query parameters or fragments. R2 origins are added to the generated Content Security Policy; configure CORS on your bucket for playback and captions. Large videos belong in R2, not Git.

The current selection includes two real workbench captures and three console captures from a local development build on September 13, 2026. They illustrate material revision, an actual webpage preview, model connections, project folders and plugin configuration. They are not release-package acceptance evidence. Creative and Phone examples remain labeled illustrations pending suitable captures.

The site includes native navigation and FAQ without JavaScript, keyboard-operable scenario tabs, optional screenshot enlargement, reduced-motion support and a page animation pause control. Preview status, model configuration and third-party charges are explained near downloads.

## Browser acceptance

```sh
pip install -r scripts/requirements-test.txt
python -m playwright install chromium
python scripts/test_browser.py
```

Tests cover desktop/mobile layouts, both languages, tabs, navigation, FAQ, no-JavaScript use, reduced motion, decoded video and captions using isolated transport fixtures, media failure states and the screenshot dialog. Actual user-provided R2 links still require live playback verification.

CI checks the generated output and uploads only `dist`. Private preparation documents and acceptance captures are stored outside this repository and are not part of the public site.

## Credits

The product icon comes from the desktop app's `apps/v8-agent-os-shell/assets/icon.png`. The orbit illustration is original portal artwork. After changing the icon or social artwork, run `python scripts/render_social.py` (Playwright required), then rebuild the site. Manrope is self-hosted under the SIL Open Font License; see `assets/fonts/OFL.txt`. Product source and release assets are maintained in the main V8 Agent OS repository.
