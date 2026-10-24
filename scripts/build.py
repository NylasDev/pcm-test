#!/usr/bin/env python3
"""Build the standalone site in docs/ from src/.

- data/pcm-alin.json is the single source for the PCM Alin questionnaire: it is
  injected into the <script id="pcm-alin-data"> block of src/index.html
  (kept in sync in place) and of docs/index.html.
- src/index.html is the Claude Artifact source (no <html>/<head> skeleton;
  the Artifact platform adds one). docs/index.html wraps it in a full document
  so it renders in standards mode on GitHub Pages or any static server.

Usage: python3 scripts/build.py
"""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, DOCS, DATA = ROOT / "src", ROOT / "docs", ROOT / "data" / "pcm-alin.json"

SKELETON_HEAD = (
    '<!doctype html><html lang="ro"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
    "<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);"
    "padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px/1.4 system-ui,sans-serif}"
    "img{max-width:100%}[hidden]{display:none!important}</style></head><body>"
)
SKELETON_TAIL = "</body></html>\n"
BLOCK = re.compile(r'(<script type="application/json" id="pcm-alin-data">\n)(.*?)(\n</script>)', re.S)


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert len(data["items"]) == 18 and all(len(i["options"]) == 6 for i in data["items"]), "18 situații × 6 variante"
    payload = json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")

    page = SRC.joinpath("index.html").read_text(encoding="utf-8")
    page, n = BLOCK.subn(lambda m: m.group(1) + payload + m.group(3), page)
    assert n == 1, "missing pcm-alin-data block in src/index.html"
    SRC.joinpath("index.html").write_text(page, encoding="utf-8")

    if DOCS.exists():
        shutil.rmtree(DOCS)
    (DOCS / "fonts").mkdir(parents=True)
    DOCS.joinpath("index.html").write_text(SKELETON_HEAD + page + SKELETON_TAIL, encoding="utf-8")
    for f in ("temple-bg.png", "temple-pdf.png"):
        shutil.copy2(SRC / f, DOCS / f)
    for f in (SRC / "fonts").glob("*.ttf"):
        shutil.copy2(f, DOCS / "fonts" / f.name)
    DOCS.joinpath(".nojekyll").write_text("", encoding="utf-8")
    print(f"built {DOCS.relative_to(ROOT)}/index.html ({DOCS.joinpath('index.html').stat().st_size} bytes)")


if __name__ == "__main__":
    main()
