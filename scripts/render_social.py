"""Regenerate the social preview after an icon/art change (uses the test Playwright dependency)."""
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
svg = (ROOT / "assets/social-card.svg").read_text(encoding="utf-8")
icon = base64.b64encode((ROOT / "assets/product-icon.png").read_bytes()).decode("ascii")
svg = svg.replace('href="product-icon.png"', f'href="data:image/png;base64,{icon}"')
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
    page.set_content('<style>body{margin:0}svg{display:block}</style>' + svg, wait_until="load")
    page.screenshot(path=str(ROOT / "assets/social-card.png"))
    browser.close()
print("Rendered social preview with the product icon.")
