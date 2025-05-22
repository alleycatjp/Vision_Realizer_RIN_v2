# !/usr/bin/env python3
"""Module documentation follows."""
"""
Remove long header comments from .py files
and save them under docs/headers/.

A-C method:
  • keep 4-line summary in the code
  • move full header to docs/headers/<same path>.md
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # Vision_Realizer_RIN_v2
DOCS = ROOT / "docs" / "headers"
SUMMARY = [
    "# (long header moved to docs/headers/)",
    "#",
    '"""Module documentation follows."""\n'
]

def shorten(py: Path):
    lines = py.read_text(encoding="utf-8").splitlines(keepends=True)
    cut = next((i for i,l in enumerate(lines)
                if l.strip().startswith('"""') or not l.strip()), 0)
    header, body = lines[:cut], lines[cut:]

    # save full header
    md = DOCS / py.relative_to(ROOT)
    md = md.with_suffix(".md")
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text("".join(header), encoding="utf-8")

    # write summary + body
    first = header[0].strip("#").strip() if header else py.name
    py.write_text(f"# {first}\n" + "\n".join(SUMMARY) + "".join(body),
                  encoding="utf-8")

def main():
    DOCS.mkdir(parents=True, exist_ok=True)
    for py in ROOT.rglob("*.py"):
        if ".venv" in py.parts:
            continue
        shorten(py)
    print("✅ 全 .py の長ヘッダを docs/headers へ退避しました")

if __name__ == "__main__":
    main()
