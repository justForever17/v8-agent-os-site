from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGETS = (ROOT / "index.html", ROOT / "zh" / "index.html")
FORBIDDEN = {
    "openclaw": re.compile(r"openclaw|clawhub", re.IGNORECASE),
    "bridge_claim": re.compile(r"v8[- ]bridge|ecosystem_hijack|hijack|assimil", re.IGNORECASE),
    "overclaim_en": re.compile(r"global security system|rogue plugins|takes over real business", re.IGNORECASE),
    "overclaim_zh": re.compile(r"接管全景|全局治安|碾压|防毒防爆"),
    "explicit_at_only": re.compile(r"(only|必须|只能).{0,24}(@plugin|@插件).{0,24}(grant|授权)", re.IGNORECASE),
    "obsolete_docs": re.compile(r"docs/ENGINE_(?:QUICK_START|DEVELOPER_GUIDE|API_REFERENCE|CONFIG_GUIDE)\.md"),
}


def main() -> int:
    violations: list[str] = []
    for path in TARGETS:
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT).as_posix()
        for name, pattern in FORBIDDEN.items():
            match = pattern.search(text)
            if match:
                violations.append(f"{relative}:{name}:{match.group(0)}")
        card_count = text.count('class="bento-card')
        placeholder_count = text.count('class="feature-placeholder')
        if card_count != 12:
            violations.append(f"{relative}:card_count:{card_count}")
        if placeholder_count != 4:
            violations.append(f"{relative}:placeholder_count:{placeholder_count}")
    if violations:
        print("Public narrative audit failed:")
        for item in violations:
            print(f"- {item}")
        return 1
    print("Public narrative audit: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
